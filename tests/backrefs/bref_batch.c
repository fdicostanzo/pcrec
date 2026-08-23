/* tests/backrefs/bref_batch.c — one artifact, MANY cells, ONE process, and it
 * reports the GROUP SPANS as well as the match span.
 *
 * WHY THE GROUPS. For this module the group spans are the SHARPER detector,
 * and that is measured rather than assumed: R32 E1's own counterexample,
 * `(a|b\1)+` on "ab", is libpcre2 (0,1) with group 1 = (0,1) where the
 * refuted write-on-traverse model answers (0,2) with group 1 = (1,2) — the
 * two differ in BOTH, but the whole re-entry family contains subjects where
 * the outer span agrees and the group does not. A differential that compared
 * only `caps[0]` would report agreement on exactly the population
 * publish-at-close exists for.
 *
 * WHY IT IS BATCHED (tests/atomic_groups/atomic_batch.c's header, measured
 * there): one process per cell makes a sweep of this size subprocess-bound by
 * two orders of magnitude. Batched, it is one process per (pattern, arm).
 *
 * PROTOCOL. Reads `<subject-file>\t<startpos>` on stdin and writes ONE line
 * per input line:
 *
 *     match <s0> <e0> [<s1> <e1> ...]        one pair per group in RX_NCAPS
 *     nomatch
 *     giveup <code>                          a budget return, never a match
 *
 * A LINE THAT CANNOT BE READ IS A HARD FAILURE, never a skipped line: the
 * caller compares POSITIONALLY, so a driver that silently produced fewer
 * lines than it was given would shift every subsequent answer. That is the
 * defect this shape is most exposed to, so it is checked on every line.
 *
 * A GIVE-UP IS REPORTED, NOT COLLAPSED INTO `nomatch`. `<prefix>_search`'s
 * return is three-valued and a backreference is exactly the construct that
 * can exhaust the work budget — `(a*)\1` over a long subject compares O(n)
 * bytes per step. Printing a distinct token means the sweep FAILS on such a
 * cell instead of silently scoring it as agreement with a `nomatch` oracle.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

int main(void)
{
    char line[8192];
    unsigned char buf[1 << 16];

    while (fgets(line, sizeof line, stdin)) {
        char *tab = strchr(line, '\t');
        size_t n, sp;
        FILE *f;
        ptrdiff_t caps[RX_NCAPS][2];
        int found, g;

        if (!tab) {
            fprintf(stderr, "bref_batch: malformed input line\n");
            return 2;
        }
        *tab++ = '\0';
        sp = (size_t)strtoul(tab, NULL, 10);

        f = fopen(line, "rb");
        if (!f) { perror(line); return 2; }
        n = fread(buf, 1, sizeof buf, f);
        fclose(f);

        for (g = 0; g < RX_NCAPS; g++) caps[g][0] = caps[g][1] = PCREC_UNSET;
        found = rx_search(buf, n, sp, caps);
        if (found == 1) {
            printf("match %td %td", caps[0][0], caps[0][1]);
            for (g = 1; g < RX_NCAPS; g++)
                printf(" %td %td", caps[g][0], caps[g][1]);
            printf("\n");
        } else if (found == 0) {
            printf("nomatch\n");
        } else {
            printf("giveup %d\n", found);
        }
    }
    return 0;
}
