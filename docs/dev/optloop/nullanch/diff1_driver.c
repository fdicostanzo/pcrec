/* docs/dev/optloop/nullanch/diff1_driver.c -- [NULLABLE-ANCH] BUILD's answer
 * differential (lane nullanch1): the REFERENCE compiler's default artifact
 * (prefix `da`, main before the row: prefilter declined) against the WORKING
 * compiler's default artifact (prefix `db`, the row: hybrid admitted) over
 * EVERY subject up to a length bound over a small alphabet AND every start
 * offset 0..len (`^`/`$`/`\z` are offset-sensitive; STEP 0's driver ran
 * offset 0 only). Compares the rc and, on a match, every capture span. A
 * `da` give-up (rc < 0) where `db` answers is counted separately (the K65
 * answer improvement), as is the converse (which would be a regression).
 * Build: -DNCAPS=n -DALPHA='"ab"' -DMAXLEN=n. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
int da_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int db_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
int main(void)
{
    const char *al = ALPHA; int na = (int)strlen(al);
    unsigned char s[64];
    long calls = 0, subjects = 0, same = 0, gu_a = 0, gu_b = 0, bad = 0, matches = 0;
    for (int len = 0; len <= MAXLEN; len++) {
        long cnt = 1; for (int i = 0; i < len; i++) cnt *= na;
        for (long k = 0; k < cnt; k++) {
            long t = k;
            for (int i = 0; i < len; i++) { s[i] = (unsigned char)al[t % na]; t /= na; }
            subjects++;
            for (int sp = 0; sp <= len; sp++) {
                ptrdiff_t ca[NCAPS][2], cb[NCAPS][2];
                memset(ca, 0xAA, sizeof ca); memset(cb, 0xAA, sizeof cb);
                int ra = da_search(s, (size_t)len, (size_t)sp, ca);
                int rb = db_search(s, (size_t)len, (size_t)sp, cb);
                calls++;
                if (ra < 0 && rb >= 0) { gu_a++; continue; }
                if (rb < 0 && ra >= 0) { gu_b++; continue; }
                if (ra != rb) { bad++; if (bad < 5) printf("DIFF rc %d vs %d len %d sp %d\n", ra, rb, len, sp); continue; }
                if (ra == 1) { matches++;
                    if (memcmp(ca, cb, sizeof ca)) { bad++; if (bad < 5) printf("DIFF caps len %d sp %d\n", len, sp); continue; } }
                same++;
            }
        }
    }
    printf("%ld subjects x every start = %ld calls: %ld identical (%ld matches), %ld ref-give-up/new-answers, %ld new-give-up/ref-answers, %ld DIFFERENT\n",
           subjects, calls, same, matches, gu_a, gu_b, bad);
    return bad != 0 || gu_b != 0;
}
