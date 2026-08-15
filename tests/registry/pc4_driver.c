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
 * driver template, one object reused across every pattern). This file
 * therefore does NOT read the compile-time RX_NCAPS macro for the caps
 * array size (that macro is baked in from the THROWAWAY template pattern
 * this driver.o is compiled against, not from whatever pattern's gen.o it
 * ends up linked with) — see tests/fuzz/fuzz_driver.c's header comment for
 * the full story: RX_NCAPS is per-pattern since [M4.5], and today's PC-4
 * pattern space happens to have zero capturing constructs, so this bug was
 * dormant here rather than firing, but a caps array sized off the wrong
 * pattern's macro is exactly as wrong the day a capturing construct is
 * added to the sweep. `rx_info.ncaps`, read at RUNTIME off the actual
 * linked artifact, is correct regardless of which pattern's gen.o this
 * driver.o ends up next to. */

#include <stdio.h>
#include <stdlib.h>

#include "gen.h"
#include "pc4_subjects.h"

int main(void)
{
    if (rx_info.ncaps < 1) {
        fprintf(stderr, "pc4_driver: rx_info.ncaps=%d (expected >= 1)\n", rx_info.ncaps);
        return 2;
    }
    ptrdiff_t (*caps)[2] = calloc((size_t)rx_info.ncaps, sizeof *caps);
    if (!caps) {
        fprintf(stderr, "pc4_driver: out of memory (ncaps=%d)\n", rx_info.ncaps);
        return 2;
    }

    unsigned char one;
    for (int i = 0; i < (int)PC4_NSUBJ; i++) {
        size_t len;
        const unsigned char *s = pc4_subject(i, &one, &len);
        if (rx_search(s, len, 0, caps))
            printf("match %td %td\n", caps[0][0], caps[0][1]);
        else
            printf("nomatch\n");
    }
    free(caps);
    return 0;
}
