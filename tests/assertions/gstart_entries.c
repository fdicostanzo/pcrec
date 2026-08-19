/* tests/assertions/gstart_entries.c — [M6.2] WAVE D: the two ENTRIES of one
 * artifact, driven side by side (assertions_design.md §9.3 as corrected by
 * R30 E8, and §10 wave D's replacement obligation).
 *
 * WHAT THE TWO ENTRIES ARE. `docs/spec/match_api.md` exports both:
 *
 *     <prefix>_search(s, n, startpos, caps)   SEARCH from `startpos` onward
 *     <prefix>_match_caps(&ctx, caps)         MATCH HERE, at `ctx.pos` only
 *
 * and `\G` is the first construct whose answer depends on which one was
 * called with what. Under `search` it means "the offset the SEARCH was asked
 * to begin at"; under the match-here entry it means `ctx->pos`, which is
 * where that entry is asked to match — trivially true at entry.
 *
 * WHY BOTH HALVES ARE ASSERTED AND THE SCOPE MATTERS. R30 E8 withdrew this
 * wave's originally-owed differential ("the two entries can disagree because
 * the ctx has no startpos") on the grounds that its premise was factually
 * wrong: `startpos` IS threaded, it is `ctx->pos`. What replaces it is
 * narrower and real:
 *
 *   FULLY-`\G` patterns:   the two entries AGREE exactly. Every branch is
 *                          pinned to `startpos`, so `search`'s later attempts
 *                          all fail and it can only report what a match-here
 *                          at the same offset reports.
 *   PARTIAL-`\G` patterns: the two entries legitimately DISAGREE at
 *                          `startpos > 0`. `search` may find the `\G`-free
 *                          branch at a LATER offset; the match-here entry is
 *                          asked about one position and answers about that
 *                          one. `\Gfoo|bar` on "xfoo bar" at 2 is the cell:
 *                          `search` reports (5,8) and match-here reports no
 *                          match.
 *
 * An unscoped "the entries agree" assertion would be RED ON CORRECT
 * BEHAVIOUR, which is why this driver reports both answers and the runner
 * decides per class rather than asserting one rule over all patterns.
 *
 * The prefix is fixed at `ge` (the runner compiles every case with `-p ge`),
 * because a driver cannot be generic over a C identifier prefix. The HEADER
 * name is not the prefix: `pcrec -o <dir>/gen.c` writes `<dir>/gen.h`
 * whatever `-p` says, so the include is `gen.h` and only the symbols carry
 * the prefix — the same split tests/fuzz/fuzz_driver.c already lives with.
 *
 * Usage: ge_entries <subject-file> <startpos>
 * Prints one line:  "search <r> [<s> <e>] | here <r> [<s> <e>]"
 * where <r> is the raw return (1/0 for search, the consumed length or a
 * negative code for match-here), so a give-up is never read as a no-match. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

int main(int argc, char **argv)
{
    unsigned char buf[1 << 16];
    size_t n, sp;
    FILE *f;
    ptrdiff_t caps[GE_NCAPS][2];
    rx_ctx ctx;
    ptrdiff_t here;
    int found;

    if (argc < 3) { fprintf(stderr, "usage: %s <subject-file> <startpos>\n", argv[0]); return 2; }
    f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    n = fread(buf, 1, sizeof buf, f);
    fclose(f);
    sp = (size_t)strtoul(argv[2], NULL, 10);

    found = ge_search(buf, n, sp, caps);
    if (found == 1) printf("search 1 %td %td", caps[0][0], caps[0][1]);
    else            printf("search %d", found);

    /* The match-here entry, asked about EXACTLY the position `search` was
     * asked to start from. Its `caps` is a separate array: A-8's
     * untouched-wins rule means a negative return leaves it alone, so
     * sharing one array with the call above would let a stale span from the
     * search be read as this entry's answer. */
    {
        ptrdiff_t hcaps[GE_NCAPS][2];
        ctx.subject = buf; ctx.len = n; ctx.pos = sp;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;
        here = ge_match_caps(&ctx, hcaps);
        if (here >= 0) printf(" | here %td %td %td\n", here, hcaps[0][0], hcaps[0][1]);
        else           printf(" | here %td\n", here);
    }
    return 0;
}
