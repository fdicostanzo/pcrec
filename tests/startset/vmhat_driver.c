/* tests/startset/vmhat_driver.c -- [START-SET] stage 2: the VM hat's
 * EVERY-STARTPOS DIFFERENTIAL and its START-BYTE ORACLE, in one pass
 * (docs/design/startset.md §6.2; driven by vmhat_diff.py).
 *
 * Two artifacts of ONE pattern under ONE set of options share this TU: `pa`,
 * built `-fno-start-set` (the DENY arm, today's emitter), and `pb`, the
 * default build (the hat). Every subject line on stdin (`\xHH` decoded) is
 * copied into an EXACTLY-sized heap buffer -- so an over-read is a fault
 * under ASan -- and both are asked at EVERY startpos 0..n:
 *
 *   - SAME: the same return and, on a match, the same capture vector;
 *   - ALLOW: the deny arm GAVE UP (a code in [PCREC_ERR_FLOOR, -2]) and the
 *     hat answered (match or no-match) -- the one direction
 *     docs/spec/match_api.md §3.1 allows: a skipped attempt spends nothing;
 *   - DEFECT: anything else, printed.
 *
 * And, where argv[1] is the start set as 64 hex digits (`start_set`'s own
 * rendering, bit b of byte b>>3), the first byte of every non-empty match
 * the DENY arm reports must be in it: the expectation comes from MATCHES of
 * a build that never reads the fact, not from the walk. argv[1] "-" skips it
 * (a `\K` pattern, whose reported start is not its attempt start).
 *
 * Exit 0 iff no defect and no start-byte violation; the counts on stdout. */
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pa.h"
#include "pb.h"

static int hexval(int c)
{
    return c >= '0' && c <= '9' ? c - '0' : c >= 'a' && c <= 'f' ? c - 'a' + 10
         : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1;
}

static void show(FILE *o, const unsigned char *s, size_t n)
{
    for (size_t i = 0; i < n; i++)
        if (s[i] >= 0x21 && s[i] < 0x7f && s[i] != '\\') fputc(s[i], o);
        else fprintf(o, "\\x%02x", s[i]);
}

int main(int argc, char **argv)
{
    unsigned char set[32] = { 0 };
    int chk = argc > 1 && strcmp(argv[1], "-") != 0 && strlen(argv[1]) == 64;
    for (int i = 0; chk && i < 32; i++)
        set[i] = (unsigned char)(hexval(argv[1][2 * i]) << 4 | hexval(argv[1][2 * i + 1]));
    static char line[65536];
    static unsigned char dec[65536];
    long cells = 0, same = 0, allow = 0, defect = 0, matches = 0, sbv = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        for (char *p = line; *p && *p != '\n';) {
            if (p[0] == '\\' && p[1] == 'x' && hexval(p[2]) >= 0 && hexval(p[3]) >= 0) {
                dec[n++] = (unsigned char)(hexval(p[2]) << 4 | hexval(p[3]));
                p += 4;
            } else {
                dec[n++] = (unsigned char)*p++;
            }
        }
        unsigned char *s = malloc(n ? n : 1);
        if (!s) return 2;
        memcpy(s, dec, n);
        for (size_t f = 0; f <= n; f++) {
            ptrdiff_t ca[PA_NCAPS][2], cb[PB_NCAPS][2];
            memset(ca, 0xff, sizeof ca);
            memset(cb, 0xff, sizeof cb);
            int ra = pa_search(s, n, f, ca);
            int rb = pb_search(s, n, f, cb);
            cells++;
            if (ra == rb && (ra != 1 || (sizeof ca == sizeof cb && !memcmp(ca, cb, sizeof ca)))) {
                same++;
            } else if (ra <= -2 && ra >= PCREC_ERR_FLOOR && rb >= 0) {
                allow++;
            } else {
                if (++defect <= 5) {
                    fprintf(stderr, "DIVERGENCE subject=");
                    show(stderr, s, n);
                    fprintf(stderr, " startpos=%zu deny=%d hat=%d", f, ra, rb);
                    if (ra == 1) fprintf(stderr, " deny(%td,%td)", ca[0][0], ca[0][1]);
                    if (rb == 1) fprintf(stderr, " hat(%td,%td)", cb[0][0], cb[0][1]);
                    fputc('\n', stderr);
                }
            }
            if (ra == 1 && ca[0][1] > ca[0][0]) {
                unsigned b = s[ca[0][0]];
                matches++;
                if (chk && !(set[b >> 3] >> (b & 7) & 1) && ++sbv <= 5) {
                    fprintf(stderr, "START-BYTE byte=0x%02x not in S, subject=", b);
                    show(stderr, s, n);
                    fprintf(stderr, " startpos=%zu match=(%td,%td)\n", f, ca[0][0], ca[0][1]);
                }
            }
        }
        free(s);
    }
    printf("cells %ld same %ld allow %ld defect %ld matches %ld startbyte_viol %ld\n",
           cells, same, allow, defect, matches, sbv);
    return defect || sbv ? 1 : 0;
}
