#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

static void sb_grow(StrBuf *sb, size_t need)
{
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
