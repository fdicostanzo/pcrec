/* definitions_oracle_driver.c — [DD-11.3]'s A==B leg: ONE binary holding
 * BOTH artifacts for one cell (`pa` = the row's own construct, Pattern A;
 * `pb` = the table's resolved definition, Pattern B), possdiff_driver.c's
 * own "two prefixes, one TU" shape (tests/possessify/CLAUDE.md) — the fixed
 * ABI types are emitted under a prefix-independent include guard exactly so
 * two differently-prefixed headers can share a TU.
 *
 * Prints one line per subject (index, then pa's verdict, then pb's),
 * fields tab-separated so definitions_oracle_check.c can parse them without
 * re-deriving the subject text (definitions_oracle_subjects.h is the one
 * shared source, PC-4's own drift-proofing). Verdict shape mirrors
 * pc4_driver.c's own three-valued read of `rx_search`'s return (a give-up
 * is NOT a match and must not be read as one, K21's class):
 *
 *     m <start> <end> <cap0s> <cap0e> <cap1s> <cap1e> ...
 *     n
 *     g steps|frames
 *
 * `ncaps` varies between pa/pb (e.g. `(a)` has one group, `(?:a)` has
 * none), so each side's capture columns are its OWN `<prefix>_info.ncaps`
 * count — never assumed equal, and definitions_oracle_check.c compares
 * only the WHOLE-MATCH span across sides plus each side's own captures
 * against libpcre2's answer for the SAME pattern (Pattern A only owns
 * captures worth comparing 1:1; a body-varying Pattern B can legitimately
 * have a different capture shape and still be BEHAVIOURALLY identical on
 * span, e.g. `(?:a)` vs `(a)`). */

#include <stdio.h>
#include <stdlib.h>

#include "pa.h"
#include "pb.h"
#include "definitions_oracle_subjects.h"

static void run_one(const char *tag, ptrdiff_t (*caps)[2], int ncaps,
                     int (*search)(const unsigned char *, size_t, size_t,
                                   ptrdiff_t (*)[2]),
                     const unsigned char *s, size_t len)
{
    int found = search(s, len, 0, caps);
    if (found == 1) {
        printf("%s m %td %td", tag, caps[0][0], caps[0][1]);
        for (int c = 0; c < ncaps; c++)
            printf(" %td %td", caps[c][0], caps[c][1]);
        printf("\n");
    } else if (found == 0) {
        printf("%s n\n", tag);
    } else {
        printf("%s g %s\n", tag, found == PCREC_ERR_STEPS ? "steps" : "frames");
    }
}

int main(void)
{
    if (pa_info.ncaps < 1 || pb_info.ncaps < 1) {
        fprintf(stderr, "definitions_oracle_driver: ncaps pa=%d pb=%d "
                "(expected >= 1)\n", pa_info.ncaps, pb_info.ncaps);
        return 2;
    }
    ptrdiff_t (*caps_a)[2] = calloc((size_t)pa_info.ncaps, sizeof *caps_a);
    ptrdiff_t (*caps_b)[2] = calloc((size_t)pb_info.ncaps, sizeof *caps_b);
    if (!caps_a || !caps_b) {
        fprintf(stderr, "definitions_oracle_driver: out of memory\n");
        return 2;
    }

    unsigned char one;
    for (int i = 0; i < (int)DEFN_NSUBJ; i++) {
        size_t len;
        const unsigned char *s = defn_subject(i, &one, &len);
        printf("%d\t", i);
        run_one("a", caps_a, pa_info.ncaps, pa_search, s, len);
        printf("%d\t", i);
        run_one("b", caps_b, pb_info.ncaps, pb_search, s, len);
    }
    free(caps_a);
    free(caps_b);
    return 0;
}
