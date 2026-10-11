/* split_rx.c — [OPT-ATTEMPT-SPLIT] exact twin: rx_search composed from the
 * unanchored artifact (prefix su, the arms without `^`) and the anchored one
 * (prefix sa, the `^` arm). See mk_split.py for the exactness argument. */
#include <stddef.h>
int su_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int sa_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2])
{
    ptrdiff_t cu[1][2];
    int ru = su_search(s, n, from, cu);
    if (ru < 0) return ru;
    if (from == 0 && !(ru == 1 && cu[0][0] == 0)) {
        int ra = sa_search(s, n, 0, caps);
        if (ra != 0) return ra;
    }
    if (ru == 1 && caps) { caps[0][0] = cu[0][0]; caps[0][1] = cu[0][1]; }
    return ru;
}
