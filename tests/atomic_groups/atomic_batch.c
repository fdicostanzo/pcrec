/* tests/atomic_groups/atomic_batch.c — one artifact, MANY cells, ONE process.
 *
 * WHY THIS EXISTS RATHER THAN A REUSE OF tests/fuzz/fuzz_driver.c. That driver
 * answers ONE (subject, startpos) per invocation, which is right for the fuzzer
 * (it is handed one input at a time) and is what every differential in this
 * tree has used since. `run_atomic_diff.sh` sweeps every startpos in [0, n]
 * over ~140 subjects for ~50 patterns in FOUR arms, which is ~120,000 cells —
 * and at one process per cell the sweep is SUBPROCESS-BOUND by two orders of
 * magnitude. MEASURED before this file existed: 44 cells per minute, i.e.
 * about eleven hours for one run, which is not a test anyone runs.
 *
 * Batched, the same sweep is one process per (pattern, arm) — about 200 — plus
 * ONE python process for the whole oracle side. The measurement is identical;
 * only the process count changes.
 *
 * IT IS NOT A REPLACEMENT FOR fuzz_driver.c AND MUST NOT BECOME ONE. That file
 * is the fuzzer's own template and is deliberately compiled once and linked
 * against every pattern's `gen.o` (see its header); this one is compiled per
 * pattern with that pattern's `gen.c`, which is what lets it be this small.
 * `tests/atomic_groups/atomic_entries.c` is the sibling that drives all THREE
 * entries; this one drives only `<prefix>_search`, because that is what §1-§3
 * compare and reading three entries per cell would triple the work for three
 * numbers only §4 asks about.
 *
 * PROTOCOL. Reads `<subject-file>\t<startpos>` lines on stdin, writes ONE line
 * per input line to stdout in tests/fuzz/pcre2_oracle's own format, so the
 * caller compares strings and never parses:
 *
 *     match <s0> <e0>
 *     nomatch
 *
 * A LINE THAT CANNOT BE READ IS A HARD FAILURE, never a skipped line: a batch
 * driver that silently produced fewer lines than it was given would shift every
 * subsequent answer against the caller's list, and the caller compares
 * positionally. That is the defect this whole shape is most exposed to, so it
 * is the one thing checked on every line.
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
        int found;

        if (!tab) {
            fprintf(stderr, "atomic_batch: malformed input line\n");
            return 2;
        }
        *tab++ = '\0';
        sp = (size_t)strtoul(tab, NULL, 10);

        f = fopen(line, "rb");
        if (!f) { perror(line); return 2; }
        n = fread(buf, 1, sizeof buf, f);
        fclose(f);

        found = rx_search(buf, n, sp, caps);
        if (found == 1) printf("match %td %td\n", caps[0][0], caps[0][1]);
        else            printf("nomatch\n");
    }
    return 0;
}
