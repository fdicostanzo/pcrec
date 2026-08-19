/* pc4_driver.c — the pcrec side of PC-4 (MOD-0.3e): runs ONE generated
 * matcher over the ENTIRE shared subject set and prints one verdict line
 * per subject:
 *
 *     match <start> <end>
 *     nomatch
 *     giveup steps | giveup frames
 *
 * The third line is [K21-class fix, 2026-08-15]: `rx_search`'s return is
 * THREE-valued, not boolean (1 match, 0 no-match, a negative
 * PCREC_ERR_STEPS/PCREC_ERR_FRAMES give-up sentinel ([ABI-NS]/D60:
 * unprefixed since [ABI-NS]) on a VM artifact's budget
 * exhaustion — a DFA artifact never returns one). The ORIGINAL version of
 * this loop tested the result with `if (rx_search(...))`, which is
 * C-truthy on a negative return too, so a give-up took the match branch
 * and printed `caps`, which the give-up path never writes — uninitialized
 * stack reported as a confident match. Same bug shape, same fix pattern,
 * as three other readers of this API: tests/fuzz/fuzz_driver.c (fixed,
 * fuzzfix arc), tests/harness/driver.c (fixed alongside this file,
 * 2026-08-15), and src/gen/emit_dfa.c's `pcrec_emit_main`
 * (docs/dev/known_issues.md K21, the CLI's `--emit-main`). NOTE the
 * `89ccd89` "sibling" fix in THIS file predates this one and fixed a
 * DIFFERENT bug (the `caps[RX_NCAPS][2]` stack-array sizing hazard below)
 * — it did not touch this truthiness check, so this file was genuinely
 * still open until now; see known_issues.md's K21 "Class closure" note.
 * `pc4_check.c` (the libpcre2 side) treats a `giveup` line as a
 * NON-COMPARABLE outcome, symmetric to its own `mlimits` bucket for
 * libpcre2's own give-up — never entered into the match/nomatch agreement
 * check as a fabricated verdict, counted separately, and asserted zero
 * (PC-4's pattern space is DFA-only today, so this is dormant: nothing in
 * run_pc4.sh selects `--engine=vm` or a tiny budget).
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
        int found = rx_search(s, len, 0, caps);
        if (found == 1)
            printf("match %td %td\n", caps[0][0], caps[0][1]);
        else if (found == 0)
            printf("nomatch\n");
        else
            printf("giveup %s\n", found == PCREC_ERR_STEPS ? "steps" : "frames");
    }
    free(caps);
    return 0;
}
