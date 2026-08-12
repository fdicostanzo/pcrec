/* pc4_driver.c — the pcrec side of PC-4 (MOD-0.3e): runs ONE generated
 * matcher over the ENTIRE shared subject set and prints one verdict line
 * per subject:
 *
 *     match <start> <end>
 *     nomatch
 *
 * Subjects are embedded from pc4_subjects.h — the same header pc4_check.c
 * (the libpcre2 side) embeds — so a subject-set drift between the two
 * sides is a compile error, not a silent partial comparison. One process
 * per PATTERN rather than per (pattern, subject): 271 subjects in-process
 * is what makes a ~70k-cell sweep affordable inside make test.
 *
 * Linked against a matcher generated with prefix `rx` (like the fuzzer's
 * driver template, one object reused across every pattern). */

#include <stdio.h>

#include "gen.h"
#include "pc4_subjects.h"

int main(void)
{
    unsigned char one;
    for (int i = 0; i < (int)PC4_NSUBJ; i++) {
        size_t len;
        const unsigned char *s = pc4_subject(i, &one, &len);
        rx_span m;
        if (rx_search(s, len, 0, &m))
            printf("match %zu %zu\n", m.start, m.end);
        else
            printf("nomatch\n");
    }
    return 0;
}
