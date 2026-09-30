/* tests/utfcheck/driver.c -- the pcrec side of [UTF-VALID]'s differential.
 *
 * Linked against ONE artifact compiled with `-p rx`. Reads rows on stdin,
 *
 *     subject_hex  startpos  qpos  mode
 *
 * and prints one line per row:
 *
 *     S <search> <ov0> <ov1> <valid_upto(startpos)> <valid_upto(qpos)>
 *     A <match> <match_caps> <c0> <c1> <valid_upto(startpos)> <valid_upto(qpos)>
 *
 * EVERY ENTRY THAT TAKES A SUBJECT IS DRIVEN, and the pairs that must agree
 * are compared HERE: `_search` against `_search_in(..., NULL)`; `_match`
 * against `_match_in(..., NULL)` and against `_match_caps`'s return;
 * `_match_caps` against `_match_caps_in(..., NULL)`. A disagreement prints
 * `DISAGREE ...` instead of a result line, which the checker reads as a
 * failure — the check sits at one site per BODY, so a body that lost it
 * shows up as two entries answering differently on the same call.
 * `caps` is pre-filled with a sentinel and must come back UNTOUCHED on
 * every NEGATIVE return (match_api.md §3.1's rule, -9 included). A `0`
 * (no match) is not asserted here: a DFA artifact with dead groups writes
 * them unset at entry ([DD-14 wave G], src/gen/emit_dfa.c), which predates
 * this suite and is recorded in docs/dev/lanes/uvbuild_report.md. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"

static size_t unhex(const char *h, unsigned char *o)
{
    size_t n = 0;
    if (!strcmp(h, "-")) return 0;
    while (h[0] && h[1]) {
        unsigned v;
        if (sscanf(h, "%2x", &v) != 1) break;
        o[n++] = (unsigned char)v;
        h += 2;
    }
    return n;
}

#define SENT ((ptrdiff_t)-77)

static int untouched(ptrdiff_t (*c)[2])
{
    for (int i = 0; i < RX_NCAPS; i++)
        if (c[i][0] != SENT || c[i][1] != SENT) return 0;
    return 1;
}

static void fill(ptrdiff_t (*c)[2])
{
    for (int i = 0; i < RX_NCAPS; i++) c[i][0] = c[i][1] = SENT;
}

int main(void)
{
    char hex[16384], mode[8];
    size_t sp, qp;
    static unsigned char s[8192];
    while (scanf("%16383s %zu %zu %7s", hex, &sp, &qp, mode) == 4) {
        size_t n = unhex(hex, s);
        const unsigned char *subj = n ? s : NULL;
        size_t v1 = rx_valid_upto(subj, n, sp), v2 = rx_valid_upto(subj, n, qp);
        if (mode[0] == 'S') {
            ptrdiff_t a[RX_NCAPS][2], b[RX_NCAPS][2];
            fill(a); fill(b);
            int r = rx_search(subj, n, sp, a);
            int ri = rx_search_in(subj, n, sp, b, NULL);
            if (r != ri) { printf("DISAGREE search %d search_in %d\n", r, ri); continue; }
            if (r < 0 && !untouched(a)) { printf("DISAGREE caps touched on %d\n", r); continue; }
            if (r == 1) printf("S 1 %td %td %zu %zu\n", a[0][0], a[0][1], v1, v2);
            else        printf("S %d - - %zu %zu\n", r, v1, v2);
        } else {
            rx_ctx c;
            ptrdiff_t a[RX_NCAPS][2], b[RX_NCAPS][2];
            memset(&c, 0, sizeof c);
            c.subject = subj; c.len = n; c.pos = sp;
            fill(a); fill(b);
            ptrdiff_t m = rx_match(&c), mi = rx_match_in(&c, NULL);
            ptrdiff_t mc = rx_match_caps(&c, a), mci = rx_match_caps_in(&c, b, NULL);
            if (m != mi || mc != mci || m != mc) {
                printf("DISAGREE match %td match_in %td caps %td caps_in %td\n", m, mi, mc, mci);
                continue;
            }
            if (mc < 0 && !untouched(a)) { printf("DISAGREE caps touched on %td\n", mc); continue; }
            if (mc >= 0) printf("A %td %td %td %td %zu %zu\n", m, mc, a[0][0], a[0][1], v1, v2);
            else         printf("A %td %td - - %zu %zu\n", m, mc, v1, v2);
        }
        fflush(stdout);
    }
    return 0;
}
