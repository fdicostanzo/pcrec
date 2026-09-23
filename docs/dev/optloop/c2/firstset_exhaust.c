/* [OPT-FIRSTSET] §4.5 — THE EXHAUSTIVE COMPARATOR (lane fsreconcile, 2026-09-22).
 *
 * Every string of length 0..L over a given alphabet, through the find-all
 * loop of all THREE artifacts in ONE process -- the shipped one, the
 * narrowed twin, and the twin plus §4.4's re-seed -- so a disagreement is a
 * difference between the three `<p>_search` bodies and nothing else.  The
 * three are linked together by emitting them at three DIFFERENT `-p`
 * prefixes (`rx`/`tw`/`rs`) and hand-editing the latter two, which is what
 * makes an in-process comparison possible at all.
 *
 * It classifies each disagreement, because the direction is the finding:
 * `fewer_matches` is a LOST match, `more_matches` a SPURIOUS one, and
 * `same_count_different_span` a match reported in the wrong place.
 * `firstset_design.md` §4.2 predicts the SECOND; this lane measures only the
 * FIRST.
 *
 * ANSWERS ONLY -- no clock.
 * Build/run: see `firstset_witness.sh`. */
/* (original header follows)
   exhaustive base/twin/reseed find-all agreement over every
   string of length 0..L on a given alphabet.  Links all three artifacts in
   ONE process (distinct emitted prefixes rx/tw/rs), so a disagreement is a
   difference between the three rx_search bodies and nothing else.
   Answers only; no clock.  argv[1]=alphabet, argv[2]=max length. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "json.h"
#include "tw.h"
#include "rs.h"

#define MAXSPAN 64
typedef int (*search_fn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);

static int findall(search_fn f, const unsigned char *b, size_t n,
                   size_t out[MAXSPAN][2])
{
    ptrdiff_t caps[1][2];
    size_t pos = 0; int k = 0;
    for (;;) {
        int r = f(b, n, pos, caps);
        if (r <= 0) break;                 /* 0 = nomatch, <0 = give-up */
        if (k >= MAXSPAN) break;
        out[k][0] = (size_t)caps[0][0];
        out[k][1] = (size_t)caps[0][1];
        k++;
        pos = (out[k-1][1] > out[k-1][0]) ? out[k-1][1] : out[k-1][0] + 1;
        if (pos > n) break;
    }
    return k;
}

static void show(const char *tag, const unsigned char *b, size_t n,
                 size_t sp[MAXSPAN][2], int k)
{
    printf("  %-7s ", tag);
    for (int i = 0; i < k; i++) printf("(%zu,%zu) ", sp[i][0], sp[i][1]);
    printf(" n=%d\n", k);
    (void)b; (void)n;
}

int main(int argc, char **argv)
{
    const char *alpha = argv[1];
    int L = atoi(argv[2]);
    size_t A = strlen(alpha);
    unsigned char buf[32];
    long total = 0, bad_tw = 0, bad_rs = 0, shown = 0;
    long tw_fewer = 0, tw_more = 0, tw_span = 0;
    size_t s0[MAXSPAN][2], s1[MAXSPAN][2], s2[MAXSPAN][2];

    for (int len = 0; len <= L; len++) {
        long combos = 1;
        for (int i = 0; i < len; i++) combos *= (long)A;
        for (long c = 0; c < combos; c++) {
            long v = c;
            for (int i = 0; i < len; i++) { buf[i] = (unsigned char)alpha[v % (long)A]; v /= (long)A; }
            buf[len] = 0;
            total++;
            int k0 = findall(rx_search, buf, (size_t)len, s0);
            int k1 = findall(tw_search, buf, (size_t)len, s1);
            int k2 = findall(rs_search, buf, (size_t)len, s2);
            int d1 = (k0 != k1) || memcmp(s0, s1, sizeof(size_t) * 2 * (size_t)k0);
            int d2 = (k0 != k2) || memcmp(s0, s2, sizeof(size_t) * 2 * (size_t)k0);
            if (d1) { bad_tw++;
                if (k1 < k0) tw_fewer++; else if (k1 > k0) tw_more++; else tw_span++; }
            if (d2) bad_rs++;
            if ((d1 || d2) && shown < 12) {
                shown++;
                printf("DISAGREE [%s]  (twin=%d reseed=%d)\n", (char *)buf, d1, d2);
                show("base", buf, (size_t)len, s0, k0);
                if (d1) show("twin", buf, (size_t)len, s1, k1);
                if (d2) show("reseed", buf, (size_t)len, s2, k2);
            }
        }
    }
    printf("twin disagreements by kind: fewer_matches=%ld more_matches=%ld same_count_different_span=%ld\n",
           tw_fewer, tw_more, tw_span);
    printf("alphabet='%s' maxlen=%d subjects=%ld  twin_disagree=%ld  reseed_disagree=%ld\n",
           alpha, L, total, bad_tw, bad_rs);
    return (bad_tw || bad_rs) ? 1 : 0;
}
