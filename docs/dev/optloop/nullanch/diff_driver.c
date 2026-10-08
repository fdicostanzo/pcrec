/* docs/dev/optloop/nullanch/diff_driver.c -- [NULLABLE-ANCH] STEP 0's
 * answer differential: the DEFAULT artifact (prefix `da`, prefilter
 * declined) against its `-fprefilter` hand twin (prefix `db`, hybrid
 * admitted -- the stand-in for the corrected predicate) over EVERY subject
 * up to a length bound over a small alphabet. Compares the rc and, on a
 * match, every capture span. A `da` give-up (rc < 0, the step budget) where
 * `db` answers is counted separately (an answer IMPROVEMENT, K65's shape),
 * never a disagreement. Build: -DNCAPS=n -DALPHA='"ab"' -DMAXLEN=n. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
int da_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int db_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int main(void)
{
    const char *al = ALPHA; int na = (int)strlen(al);
    unsigned char s[64];
    long total = 0, same = 0, giveup_da = 0, bad = 0, matches = 0;
    for (int len = 0; len <= MAXLEN; len++) {
        long cnt = 1; for (int i = 0; i < len; i++) cnt *= na;
        for (long k = 0; k < cnt; k++) {
            long t = k;
            for (int i = 0; i < len; i++) { s[i] = (unsigned char)al[t % na]; t /= na; }
            ptrdiff_t ca[NCAPS][2], cb[NCAPS][2];
            memset(ca, 0xAA, sizeof ca); memset(cb, 0xAA, sizeof cb);
            int ra = da_search(s, (size_t)len, 0, ca);
            int rb = db_search(s, (size_t)len, 0, cb);
            total++;
            if (ra < 0 && rb >= 0) { giveup_da++; continue; }
            if (ra != rb) { bad++; if (bad < 5) printf("DIFF rc %d vs %d on len %d\n", ra, rb, len); continue; }
            if (ra == 1) { matches++;
                if (memcmp(ca, cb, sizeof ca)) { bad++; if (bad < 5) printf("DIFF caps on len %d\n", len); continue; } }
            same++;
        }
    }
    printf("%ld subjects: %ld identical (%ld matches), %ld da-give-up/db-answers, %ld DIFFERENT\n",
           total, same, matches, giveup_da, bad);
    return bad != 0;
}
