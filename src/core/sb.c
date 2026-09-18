#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

static void sb_grow(StrBuf *sb, size_t need)
{
    /* [ART-SIZE] The size term's early abort. Checked here because this is the
     * ONE place a buffer's length grows, so no append path can miss it. See
     * StrBuf's own comment in internal.h for why it is a cost guard and not a
     * cap decision — the cap is always decided by the exact post-emission
     * scan in compile.c, on an attempt that ran to completion. */
    if (sb->abort_over && sb->len + need > sb->abort_over && sb->cx)
        ctx_fail(sb->cx, 0, "size-term ladder trial over its scratch bound");
    if (sb->len + need + 1 <= sb->cap) return;
    size_t cap = sb->cap ? sb->cap : 256;
    while (cap < sb->len + need + 1) cap *= 2;
    /* [M4.7b/K7] realloc into a TEMPORARY: on failure the old buffer is still
     * live and still owned by `sb`, so the error path's sb_free reclaims it.
     * Assigning the NULL straight into sb->p would leak it and lose the only
     * pointer to it. */
    char *np = realloc(sb->p, cap);
    if (!np) {
        if (sb->cx) ctx_nomem(sb->cx);
        abort();   /* a detached buffer (syntax_dump.c) has no error channel */
    }
    sb->p = np;
    sb->cap = cap;
}

void sb_putc(StrBuf *sb, char c)
{
    sb_grow(sb, 1);
    sb->p[sb->len++] = c;
    sb->p[sb->len] = 0;
}

void sb_puts(StrBuf *sb, const char *s)
{
    size_t n = strlen(s);
    sb_grow(sb, n);
    memcpy(sb->p + sb->len, s, n);
    sb->len += n;
    sb->p[sb->len] = 0;
}

void sb_printf(StrBuf *sb, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    va_list ap2;
    va_copy(ap2, ap);
    int n = vsnprintf(NULL, 0, fmt, ap);
    va_end(ap);
    if (n < 0) abort();
    sb_grow(sb, (size_t)n);
    vsnprintf(sb->p + sb->len, (size_t)n + 1, fmt, ap2);
    va_end(ap2);
    sb->len += (size_t)n;
}

char *sb_take(StrBuf *sb)
{
    char *p = sb->p ? sb->p : strdup("");
    if (!p) {
        if (sb->cx) ctx_nomem(sb->cx);
        abort();
    }
    sb->p = NULL;
    sb->len = sb->cap = 0;
    return p;
}

void sb_free(StrBuf *sb)
{
    free(sb->p);
    sb->p = NULL;
    sb->len = sb->cap = 0;
}

/* ---- THE TEXT LAYER ([REVW.1] wave 1) -----------------------------------
 *
 * The contract, the two vocabularies and why they must not be swapped are
 * stated once, at the declarations in core/internal.h. What follows is the
 * implementation and nothing else.
 *
 * D108: DATA IN, TEXT OUT. Nothing below reads a `Ctx`, a walk or a machine,
 * so the future IR-consuming back-end calls the same functions unchanged. */

/* The tail both vocabularies share, and the reason this file has them at all:
 * before wave 1 it was written twice (syntax_dump.c's `put_text` and
 * rxt_source.c's `put_escaped`), with only one of the two dumps calling its
 * own copy. A byte no line-oriented frame can carry goes out by NUMBER;
 * printable bytes and UTF-8 continuation bytes are themselves, because the
 * escape protects the FRAMING and never transcodes the content. */
static void sb_frame_byte(StrBuf *sb, unsigned char c)
{
    if (c < 0x20 || c == 0x7f) sb_printf(sb, "\\x%02x", c);
    else                       sb_putc(sb, (char)c);
}

void sb_textn(StrBuf *sb, const char *s, size_t n)
{
    if (!s) return;
    for (size_t i = 0; i < n; i++) sb_frame_byte(sb, (unsigned char)s[i]);
}

void sb_text(StrBuf *sb, const char *s)
{
    if (!s) return;
    sb_textn(sb, s, strlen(s));
}

void sb_field(StrBuf *sb, const char *s)
{
    if (!s) return;
    for (const unsigned char *q = (const unsigned char *)s; *q; q++) {
        switch (*q) {
        case '\\': sb_puts(sb, "\\\\"); break;
        case '\t': sb_puts(sb, "\\t");  break;
        case '\n': sb_puts(sb, "\\n");  break;
        case '\r': sb_puts(sb, "\\r");  break;
        default:
            sb_frame_byte(sb, *q);
            break;
        }
    }
}

void sb_join(StrBuf *sb, const char *sep, const char *const *names, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        if (i) sb_puts(sb, sep);
        if (names[i]) sb_puts(sb, names[i]);
    }
}

void sb_row(StrBuf *sb, const char *const *cells, size_t ncell)
{
    for (size_t i = 0; i < ncell; i++) {
        if (i) sb_putc(sb, '\t');
        sb_text(sb, cells[i]);
    }
    sb_putc(sb, '\n');
}

/* ---- THE FRAGMENT ([REVW.2] wave 2 stage 3) -----------------------------
 *
 * The contract is stated once, at the declaration in core/internal.h. This is
 * `sb_printf`'s body with the destination changed: measure, allocate exactly,
 * format. The two `vsnprintf` calls read the SAME argument list through a
 * `va_copy`, because a `va_list` is consumed by the first traversal.
 *
 * `n + 1` is the allocation, not `n`: `vsnprintf` writes its NUL within the
 * size it is given, so a buffer of exactly `n` would hold `n - 1` bytes of
 * text and truncate — which is precisely the failure this primitive exists to
 * make impossible, and the one an off-by-one here would reintroduce silently.
 *
 * `n < 0` aborts, matching `sb_printf`: a negative `vsnprintf` return is an
 * encoding error in a format string this tree wrote itself, not a condition a
 * pattern can provoke, so there is no diagnosis to route. */
const char *sb_fragf(Arena *a, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    va_list ap2;
    va_copy(ap2, ap);
    int n = vsnprintf(NULL, 0, fmt, ap);
    va_end(ap);
    if (n < 0) abort();
    char *out = arena_alloc(a, (size_t)n + 1);
    vsnprintf(out, (size_t)n + 1, fmt, ap2);
    va_end(ap2);
    return out;
}
