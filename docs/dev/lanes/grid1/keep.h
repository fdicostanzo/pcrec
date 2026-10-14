/* vecspike: the preserved site state (V3/V4). One per find-all pass over one
 * subject: zero it before the pass's first call; every call passes the same
 * (s, n) and s[0..n) is unchanged between calls. rx_search_keep re-binds
 * (resets) when (s, n) differ from the bound pair. */
#ifndef VS_KEEP_H
#define VS_KEEP_H
#include <stddef.h>
struct rx_keep {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long m;
};
int rx_search_keep(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2], struct rx_keep *st);
#endif
