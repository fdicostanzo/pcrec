/* tests/atomic_groups/atomic_entries.c — [M6.4.2]: all THREE entries of one
 * cut-bearing artifact, driven side by side (atomic_groups_design.md §4.4
 * RULE H4, and §12 slice 4's evidence obligation).
 *
 * WHY THIS EXISTS AND WHY NO `.rxt` BLOCK CAN REPLACE IT. A `.rxt` case drives
 * `<prefix>_search` and compares ONE span. H4's claim is about the OTHER TWO
 * entries, and it is a claim that they need NO CHANGE for this module — which
 * is exactly the kind of claim that is true until it is not, and that nothing
 * in the corpus can see either way.
 *
 * WHAT H4 RESTS ON, and why it is worth driving rather than reading. Two
 * structural reasons plus one that is this module's own:
 *
 *   1. `<prefix>_match_anchored` starts at `ctx->pos` and never moves it, so
 *      "anchored at the requested position" is a property of the CALL rather
 *      than a filter applied to a search's answer afterwards.
 *   2. It returns `pos - ctx->pos`, computed from POSITIONS and never from
 *      `caps` — so a construct that moves the reported start (`\K`) or the
 *      reported end cannot corrupt the return.
 *   3. THE PART THAT IS THIS MODULE'S: both match-here entries pass `ctx->len`
 *      as the MRL ceiling, never a prefilter window. §4's whole hazard is that
 *      the prefilter's span END is not a bound on a CUT match's end, and that
 *      hazard therefore cannot reach these two entries at all. An entry that
 *      started passing a window would be a silent match loss on exactly the
 *      R3a family, and this driver is what would print it.
 *
 * THE ORACLE FOR A MATCH-HERE ENTRY IS `\G`, which is the trick wave D
 * invented and this file reuses: `tests/fuzz/pcre2_oracle` has no anchored
 * mode, but PCRE2 already has a spelling for "match here and nowhere else" —
 * `\G` is true iff `pos == startpos`, so libpcre2's answer for `\G(?:PAT)` at
 * `sp` IS the match-here answer for `PAT` at `sp`. The wrap is `\G(?:PAT)` and
 * not `\GPAT` because a top-level alternation would otherwise bind only its
 * first branch to the `\G`.
 *
 * SO WHAT IS PRINTED, per cell, one line:
 *
 *     search      the reported span, against libpcre2 — the same answer the
 *                 corpus checks, printed here so the three entries can be
 *                 compared against a common reference rather than only
 *                 against each other.
 *     match       the CONSUMED length at `ctx->pos`, which is what a D38
 *                 callout would advance by.
 *     caps        the same length AND the reported span, from the entry that
 *                 delivers offsets.
 *
 * Usage: t <subject-file> <startpos>
 *        t                        (reads "<path> <startpos>" lines on stdin)
 *
 * Built against ONE pattern's gen.h at a time by run_atomic_diff.sh, which is
 * what supplies the AG_* prefix macros below.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

#ifndef AG_NCAPS
#define AG_NCAPS   RX_NCAPS
#endif
#define ag_search      rx_search
#define ag_match       rx_match
#define ag_match_caps  rx_match_caps

static int one_cell(const char *path, size_t sp)
{
    unsigned char buf[1 << 16];
    size_t n;
    FILE *f;
    ptrdiff_t caps[AG_NCAPS][2];
    int found;

    f = fopen(path, "rb");
    if (!f) { perror(path); return 2; }
    n = fread(buf, 1, sizeof buf, f);
    fclose(f);

    found = ag_search(buf, n, sp, caps);
    if (found == 1) printf("search 1 %td %td", caps[0][0], caps[0][1]);
    else            printf("search %d", found);

    /* THE `rx_matchfn`-TYPED ENTRY delivers no captures at all, so its return
     * is the ONLY thing a caller can act on. Driven on its own so an entry
     * that derived it from `caps` would print a plausible number that is wrong
     * in the one direction nothing else measures. */
    {
        rx_ctx ctx;
        ptrdiff_t here;
        ctx.subject = buf; ctx.len = n; ctx.pos = sp;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;
        here = ag_match(&ctx);
        printf(" | match %td", here);
    }

    /* THE CAPS-DELIVERING SIBLING, with its OWN array: A-8's untouched-wins
     * rule means a negative return leaves `caps` alone, so reusing the
     * search's array would let a stale span be read as this entry's answer. */
    {
        rx_ctx ctx;
        ptrdiff_t hcaps[AG_NCAPS][2];
        ptrdiff_t here;
        ctx.subject = buf; ctx.len = n; ctx.pos = sp;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;
        here = ag_match_caps(&ctx, hcaps);
        if (here >= 0) printf(" | caps %td %td %td\n", here, hcaps[0][0], hcaps[0][1]);
        else           printf(" | caps %td\n", here);
    }
    return 0;
}

int main(int argc, char **argv)
{
    char line[8192];

    if (argc >= 3)
        return one_cell(argv[1], (size_t)strtoul(argv[2], NULL, 10));
    if (argc != 1) {
        fprintf(stderr, "usage: %s [<subject-file> <startpos>]"
                        "   (no args: read '<path> <startpos>' lines from stdin)\n",
                argv[0]);
        return 2;
    }
    while (fgets(line, sizeof line, stdin)) {
        char *sp = strrchr(line, ' ');
        if (!sp) { fprintf(stderr, "atomic_entries: malformed input line\n"); return 2; }
        *sp++ = '\0';
        /* A cell that cannot be read is a HARD failure, never a skipped line:
         * a batch driver that silently produced fewer lines than it was given
         * would shift every subsequent answer against the caller's own list,
         * and the caller compares positionally. */
        if (one_cell(line, (size_t)strtoul(sp, NULL, 10)) != 0) return 2;
    }
    return 0;
}
