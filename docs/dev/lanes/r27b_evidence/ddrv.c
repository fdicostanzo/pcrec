/* docs/dev/lanes/r27b_evidence/ddrv.c — job 581: the no-clock DIFFERENTIAL driver.
 *
 *   ddrv CASEFILE TILE
 *
 * CASEFILE (written by diff_581.py): repeated  u32 n, n subject bytes, then (n + 1) pairs of
 * int32 (start, end) -- python `re`'s search(subject, lo) for lo = 0..n, (-1, -1) for none.
 * For every case and every lo the arm's rx_search(subject, n, lo) must return the same span.
 *
 * Over-reads must show as WRONG ANSWERS (or, built with -DEXACT under ASan, as a fault):
 *   default   the subject sits in the middle of a buffer with 64 sentinel bytes on EACH side;
 *             the sentinel is TILE (a text that satisfies the cell's terms) rotated by a phase,
 *             and every phase 0..len(TILE)-1 is run, so a term read one byte past the end (or
 *             before the start) sees a byte that would complete a match.
 *   -DEXACT   the subject is a malloc block of EXACTLY n bytes (n == 0: 1); no neighbours.
 * Prints "ddrv: cases C checks K mismatches M" and the first mismatches; exit 1 if M > 0.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include HDR

#define PAD 64

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: ddrv CASEFILE TILE\n"); return 64; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    const char *tile = argv[2];
    size_t tl = strlen(tile), cases = 0, checks = 0, bad = 0;
#ifdef EXACT
    size_t phases = 1;
#else
    size_t phases = tl;
#endif
    uint32_t n;
    while (fread(&n, 4, 1, f) == 1) {
        unsigned char *subj = malloc(n ? n : 1);
        int32_t *exp = malloc((size_t)(n + 1) * 8);
        if (fread(subj, 1, n, f) != n || fread(exp, 8, (size_t)n + 1, f) != (size_t)n + 1) {
            fprintf(stderr, "ddrv: torn case file\n"); return 2;
        }
        cases++;
        for (size_t ph = 0; ph < phases; ph++) {
#ifdef EXACT
            unsigned char *buf = malloc(n ? n : 1), *s = buf;
            memcpy(buf, subj, n);
#else
            unsigned char *buf = malloc((size_t)n + 2 * PAD), *s = buf + PAD;
            for (size_t i = 0; i < PAD; i++) buf[i] = (unsigned char)tile[(i + ph) % tl];
            for (size_t i = 0; i < PAD; i++) buf[PAD + n + i] = (unsigned char)tile[(i + ph) % tl];
            memcpy(s, subj, n);
#endif
            for (size_t lo = 0; lo <= n; lo++) {
                ptrdiff_t caps[RX_NCAPS][2];
                int r = rx_search(s, n, lo, caps);
                int32_t gs = r == 1 ? (int32_t)caps[0][0] : -1, ge = r == 1 ? (int32_t)caps[0][1] : -1;
                checks++;
                if (gs != exp[2 * lo] || ge != exp[2 * lo + 1]) {
                    if (bad++ < 5) {
                        fprintf(stderr, "MISMATCH n=%u lo=%zu phase=%zu got (%d,%d) python (%d,%d) subject=", n, lo, ph,
                                gs, ge, exp[2 * lo], exp[2 * lo + 1]);
                        for (uint32_t i = 0; i < n; i++) fprintf(stderr, "%02x", subj[i]);
                        fprintf(stderr, "\n");
                    }
                }
            }
            free(buf);
        }
        free(subj); free(exp);
    }
    printf("ddrv: cases %zu checks %zu mismatches %zu\n", cases, checks, bad);
    return bad ? 1 : 0;
}
