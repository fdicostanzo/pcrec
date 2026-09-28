/* pcrec_bdrive.c -- the bequiv.py alphabet and order, driven through
 * pcrec-generated matchers.  For each subject, prints bequiv.py's marked
 * string ("|" before every position where the anchored zero-width match
 * succeeds, and at the end), one artifact per stream, so `shasum` of a
 * stream equals bequiv.py's sha1(prim marks) iff every answer agrees with
 * libpcre2.  Build with -DENC_UTF8 to use character boundaries only.
 * Artifacts: A0..A5 are linked in by the Makefile-free build line in
 * run_bdrive.sh.  Usage: pcrec_bdrive IDX MAXLEN */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "A0.h"
#include "A1.h"
#include "A2.h"
#include "A3.h"
#include "A4.h"
#include "A5.h"
static ptrdiff_t (*const fns[6])(const rx_ctx *) = { A0_match, A1_match, A2_match, A3_match, A4_match, A5_match };
static const char *ALPHA[] = { "a", "_", "5", " ", "-", "\xc3\xa9", "\xd9\xa3", "\xcc\x81",
    "\xe6\x97\xa5", "\xe2\x80\xbf", "\xf0\xa0\x80\x80", "\xc2\xa0", "\xe2\x82\xac", "\xf0\x9f\x98\x80" };
#define NA 14
int main(int argc, char **argv) {
    int idx = atoi(argv[1]), maxlen = atoi(argv[2]);
    unsigned char s[64]; char outb[256];
    for (int L = 0; L <= maxlen; L++) {
        int t[8] = {0};
        for (;;) {
            size_t n = 0, bnd[8]; int nb = 0;
            for (int i = 0; i < L; i++) { bnd[nb++] = n; size_t k = strlen(ALPHA[t[i]]); memcpy(s + n, ALPHA[t[i]], k); n += k; }
            size_t o = 0;
            for (size_t p = 0; p <= n; p++) {
#ifdef ENC_UTF8
                int isb = (p == n); for (int i = 0; i < nb; i++) if (bnd[i] == p) isb = 1;
#else
                int isb = 1;
#endif
                if (isb) {
                    rx_ctx c; memset(&c, 0, sizeof c); c.subject = s; c.len = n; c.pos = p;
                    ptrdiff_t r = fns[idx](&c);
                    if (r < -1) { fprintf(stderr, "ERR %td at pos %zu\n", r, p); return 2; }
                    if (r >= 0) outb[o++] = '|';
                }
                if (p < n) outb[o++] = s[p];
            }
            fwrite(outb, 1, o, stdout);
            int i = L - 1;
            while (i >= 0 && ++t[i] == NA) t[i--] = 0;
            if (i < 0) break;
        }
    }
    return 0;
}
