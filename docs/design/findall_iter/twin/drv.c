/* docs/design/findall_iter/twin/drv.c — lane iterdes, [FINDALL-NEXT] HAND TWIN driver.
 *
 * Answers only (NO timing). Built against one twin artifact (mktwin.py) with
 * -DPFX=<prefix>. Reads subjects, one per stdin line, in the .rxt
 * subject-escape vocabulary (\t \n \r \\ \xNN), and prints for each:
 *
 *   L=<spans>  match_api.md §3.1.3's loop over <p>_search + <p>_next_pos
 *   I=<spans>  the iterator, <p>_next with a caps buffer
 *   Z=<spans>  the iterator, <p>_next with caps == NULL (span read back by
 *              a parallel caps run is not possible, so Z prints the COUNT)
 *   B=<rc>     a bound iterator called with another n (must be PCREC_ERR_ITER)
 *   N=<spans>  <p>_next_n with K = 3 (crossing batch boundaries)
 *
 * and the iterator's final rc. The runner (run_twin.sh) compares I against L
 * (non-retry twins) or against libpcre2's global loop (retry twins), and I
 * against N always.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
#define F(x) CAT(PFX, x)
#include HDR
#include "iter_abi.h"

int F(_next)(rx_iter *it, const unsigned char *s, size_t n, ptrdiff_t (*caps)[2]);
size_t F(_next_n)(rx_iter *it, const unsigned char *s, size_t n, ptrdiff_t (*out)[2], size_t k);

static size_t unesc(const char *in, size_t len, unsigned char *out)
{
    size_t o = 0;
    for (size_t i = 0; i < len; i++) {
        if (in[i] == '\\' && i + 1 < len) {
            char c = in[i + 1];
            if (c == 't') { out[o++] = '\t'; i++; continue; }
            if (c == 'n') { out[o++] = '\n'; i++; continue; }
            if (c == 'r') { out[o++] = '\r'; i++; continue; }
            if (c == '\\') { out[o++] = '\\'; i++; continue; }
            if (c == 'x' && i + 3 < len) {
                char h[3] = { in[i + 2], in[i + 3], 0 };
                out[o++] = (unsigned char)strtoul(h, NULL, 16);
                i += 3;
                continue;
            }
        }
        out[o++] = (unsigned char)in[i];
    }
    return o;
}

#define NCAPS CAT(PFXU, _NCAPS)

int main(void)
{
    static char line[1 << 20];
    static unsigned char s[1 << 19];
    static ptrdiff_t caps[NCAPS][2], out[3][2];
    while (fgets(line, sizeof line, stdin)) {
        size_t len = strlen(line);
        if (len && line[len - 1] == '\n') line[--len] = 0;
        size_t n = unesc(line, len, s);
        int k = 0;

        printf("L=");
        size_t p = 0;
        for (k = 0; p <= n; k++) {
            int r = F(_search)(s, n, p, caps);
            if (r != 1) { if (r < 0) printf(" GU%d", r); break; }
            printf("%s(%td,%td)", k ? " " : "", caps[0][0], caps[0][1]);
            p = caps[0][1] > caps[0][0] ? F(_next_pos)(s, n, (size_t)caps[0][1] - 1)
                                       : F(_next_pos)(s, n, (size_t)caps[0][0]);
        }

        rx_iter it = RX_ITER_INIT;
        printf("\tI=");
        for (k = 0; F(_next)(&it, s, n, caps); k++)
            printf("%s(%td,%td)", k ? " " : "", caps[0][0], caps[0][1]);
        printf("\trc=%d", it.rc);
        /* a call after the end must stay at the end (sticky) */
        if (F(_next)(&it, s, n, caps)) printf(" STICKY-FAIL");

        rx_iter iz = RX_ITER_INIT;
        for (k = 0; F(_next)(&iz, s, n, NULL); k++) ;
        printf("\tZ=%d", k);

        rx_iter in = RX_ITER_INIT;
        /* a different (s, n) on a bound iterator is refused, not rebound */
        rx_iter ib = RX_ITER_INIT;
        (void)F(_next)(&ib, s, n, caps);
        (void)F(_next)(&ib, s, n + 1, caps);
        printf("\tB=%d", ib.rc);

        printf("\tN=");
        size_t got, tot = 0;
        while ((got = F(_next_n)(&in, s, n, out, 3)) > 0) {
            for (size_t i = 0; i < got; i++, tot++)
                printf("%s(%td,%td)", tot ? " " : "", out[i][0], out[i][1]);
            if (got < 3) break;
        }
        printf("\n");
    }
    return 0;
}
