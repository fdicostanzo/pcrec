#include <ctype.h>
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
    if (sb->abort_over && sb->len + sb->cmt_dropped + need > sb->abort_over && sb->cx)
        ctx_fail(sb->cx, 0, "size-term ladder trial over its scratch bound");
    if (sb->len + need + 1 <= sb->cap) return;
    size_t cap = sb->cap ? sb->cap : 256;
    while (cap < sb->len + need + 1) cap *= 2;
    /* [M4.7b/K7] realloc into a TEMPORARY: on failure the old buffer is still
     * live and still owned by `sb`, so the error path's pcrec_sb_free reclaims it.
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

/* [EMIT-VERB] (D112) THE COMMENT GATE, at the three primitives every other
 * append in this file is built on (`pcrec_sb_text`, `pcrec_sb_field`, `pcrec_sb_row`,
 * `pcrec_sb_join`, the three `sb_stamp*`) — so a helper added later inherits the
 * gate instead of having to remember it. Inside a muted region an append is
 * a no-op: `len` does not advance, so the size term's `abort_over` and the
 * caps see exactly the bytes the artifact will carry.
 *
 * NOT A FILTER OVER FINISHED TEXT. The class is decided at the emission site
 * and the text is never written, so nothing downstream has to recognise a
 * comment or repair a line — the failure mode a post-hoc strip would have. */
static inline bool sb_muted(const StrBuf *sb) { return sb->cmt_mute_depth != 0; }

void pcrec_sb_comments(StrBuf *sb, bool on) { sb->cmt_drop = !on; }

size_t pcrec_sb_len_uncut(const StrBuf *sb) { return sb->len + sb->cmt_dropped; }

void pcrec_sb_cmt_open(StrBuf *sb, PcrecCmtClass klass)
{
    sb->cmt_depth++;
    if (klass == PCREC_CMT_NONESSENTIAL && sb->cmt_drop && !sb->cmt_mute_depth)
        sb->cmt_mute_depth = sb->cmt_depth;
}

void pcrec_sb_cmt_close(StrBuf *sb)
{
    /* An unbalanced close would leave the buffer muted for the rest of the
     * compile — silent, total, and exactly the shape that is hard to
     * attribute. It cannot happen from this tree's call sites (every open has
     * its close in the same function), so the guard is a floor, not a
     * mechanism: refuse to underflow. */
    if (sb->cmt_depth == 0) return;
    if (sb->cmt_mute_depth == sb->cmt_depth) sb->cmt_mute_depth = 0;
    sb->cmt_depth--;
}

void pcrec_sb_putc(StrBuf *sb, char c)
{
    if (sb_muted(sb)) { sb->cmt_dropped += 1; return; }
    sb_grow(sb, 1);
    sb->p[sb->len++] = c;
    sb->p[sb->len] = 0;
}

void pcrec_sb_puts(StrBuf *sb, const char *s)
{
    if (sb_muted(sb)) { sb->cmt_dropped += strlen(s); return; }
    size_t n = strlen(s);
    sb_grow(sb, n);
    memcpy(sb->p + sb->len, s, n);
    sb->len += n;
    sb->p[sb->len] = 0;
}

/* `sb_printf`'s body, reached through a `va_list` so an ADAPTER that already
 * holds one can append formatted text — `pcrec_sb_fragfv`'s own reason, one
 * destination over. Measure, grow, format: the two `vsnprintf` calls read the
 * SAME arguments through their own `va_copy`, because a `va_list` is consumed
 * by the traversal that measures it. File-static on purpose: no caller outside
 * this file needs it, and the text layer's public surface is the smaller for
 * it. */
static void sb_vprintf(StrBuf *sb, const char *fmt, va_list ap)
      __attribute__((format(printf, 2, 0)));

static void sb_vprintf(StrBuf *sb, const char *fmt, va_list ap)
{
    if (sb_muted(sb)) {
        /* MEASURED, not skipped: the discarded byte count is what keeps the
         * two length-based decisions off this axis (see StrBuf.cmt_dropped).
         * One `vsnprintf` into nothing, on a path that then writes nothing. */
        va_list apm;
        va_copy(apm, ap);
        int nm = vsnprintf(NULL, 0, fmt, apm);
        va_end(apm);
        if (nm > 0) sb->cmt_dropped += (size_t)nm;
        return;
    }
    va_list ap2;
    va_copy(ap2, ap);
    int n = vsnprintf(NULL, 0, fmt, ap2);
    va_end(ap2);
    if (n < 0) abort();
    sb_grow(sb, (size_t)n);
    va_list ap3;
    va_copy(ap3, ap);
    vsnprintf(sb->p + sb->len, (size_t)n + 1, fmt, ap3);
    va_end(ap3);
    sb->len += (size_t)n;
}

void sb_printf(StrBuf *sb, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    sb_vprintf(sb, fmt, ap);
    va_end(ap);
}

char *pcrec_sb_take(StrBuf *sb)
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

void pcrec_sb_free(StrBuf *sb)
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
    else                       pcrec_sb_putc(sb, (char)c);
}

void pcrec_sb_textn(StrBuf *sb, const char *s, size_t n)
{
    if (!s) return;
    for (size_t i = 0; i < n; i++) sb_frame_byte(sb, (unsigned char)s[i]);
}

void pcrec_sb_text(StrBuf *sb, const char *s)
{
    if (!s) return;
    pcrec_sb_textn(sb, s, strlen(s));
}

void pcrec_sb_field(StrBuf *sb, const char *s)
{
    if (!s) return;
    for (const unsigned char *q = (const unsigned char *)s; *q; q++) {
        switch (*q) {
        case '\\': pcrec_sb_puts(sb, "\\\\"); break;
        case '\t': pcrec_sb_puts(sb, "\\t");  break;
        case '\n': pcrec_sb_puts(sb, "\\n");  break;
        case '\r': pcrec_sb_puts(sb, "\\r");  break;
        default:
            sb_frame_byte(sb, *q);
            break;
        }
    }
}

void pcrec_sb_join(StrBuf *sb, const char *sep, const char *const *names, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        if (i) pcrec_sb_puts(sb, sep);
        if (names[i]) pcrec_sb_puts(sb, names[i]);
    }
}

void pcrec_sb_row(StrBuf *sb, const char *const *cells, size_t ncell)
{
    for (size_t i = 0; i < ncell; i++) {
        if (i) pcrec_sb_putc(sb, '\t');
        pcrec_sb_text(sb, cells[i]);
    }
    pcrec_sb_putc(sb, '\n');
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
const char *pcrec_sb_fragfv(Arena *a, const char *fmt, va_list ap)
{
    va_list ap2;
    va_copy(ap2, ap);
    int n = vsnprintf(NULL, 0, fmt, ap2);
    va_end(ap2);
    if (n < 0) abort();
    char *out = arena_alloc(a, (size_t)n + 1);
    va_list ap3;
    va_copy(ap3, ap);
    vsnprintf(out, (size_t)n + 1, fmt, ap3);
    va_end(ap3);
    return out;
}

const char *pcrec_sb_fragf(Arena *a, const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    const char *out = pcrec_sb_fragfv(a, fmt, ap);
    va_end(ap);
    return out;
}

/* ---- THE STAMP ([REVW.2] wave 2, EP2 step 10 / lens 1 X8) ---------------
 *
 * The contract is stated once, at the declarations in core/internal.h. This
 * is the one implementation the three entry points share.
 *
 * `%-*s` AT WIDTH 0 IS THE UNPADDED CASE: a printf field width of zero states
 * no minimum, so `pcrec_sb_stampf` is `pcrec_sb_stampwf` with the padding asked for and
 * not supplied, rather than a second spelling of the line. The separator
 * space is emitted HERE and not inside the width, which is what makes a
 * padded name and an over-long one produce the same one-space minimum the
 * hand-written formats produced. */
static void sb_stampv(StrBuf *c, const char *upper, const char *name,
                      int namew, const char *valfmt, va_list ap)
      __attribute__((format(printf, 5, 0)));

static void sb_stampv(StrBuf *c, const char *upper, const char *name,
                      int namew, const char *valfmt, va_list ap)
{
    sb_printf(c, "#define %s_%-*s ", upper, namew, name);
    sb_vprintf(c, valfmt, ap);
    pcrec_sb_putc(c, '\n');
}

void pcrec_sb_stampf(StrBuf *c, const char *upper, const char *name,
               const char *valfmt, ...)
{
    va_list ap;
    va_start(ap, valfmt);
    sb_stampv(c, upper, name, 0, valfmt, ap);
    va_end(ap);
}

void pcrec_sb_stampwf(StrBuf *c, const char *upper, const char *name, int namew,
                const char *valfmt, ...)
{
    va_list ap;
    va_start(ap, valfmt);
    sb_stampv(c, upper, name, namew, valfmt, ap);
    va_end(ap);
}

void pcrec_sb_stamp_str(StrBuf *c, const char *upper, const char *name,
                  const char *value)
{
    pcrec_sb_stampf(c, upper, name, "\"%s\"", value);
}

/* ---- THE UPPERCASED NAME ([REVW.2] wave 2; lens 10 item 2; D108) --------
 *
 * The contract is stated once, at the declaration in core/internal.h.
 *
 * `toupper` AND NOT AN ASCII TABLE, deliberately: this is `prefix_upper`'s
 * own body moved, byte for byte, and swapping in a locale-independent
 * uppercase would be a behaviour change smuggled inside a refactor. If this
 * tree ever wants ASCII-only folding here, that is its own change with its
 * own byte-identity argument. */
const char *pcrec_sb_upper(Arena *a, const char *s)
{
    size_t n = strlen(s);
    char *out = arena_alloc(a, n + 1);
    for (size_t i = 0; i < n; i++)
        out[i] = (char)toupper((unsigned char)s[i]);
    out[n] = 0;
    return out;
}
