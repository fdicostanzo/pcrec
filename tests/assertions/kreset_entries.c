/* tests/assertions/kreset_entries.c — [M6.2] WAVE E: all THREE entries of one
 * `\K` artifact, driven side by side (assertions_design.md §6.3 rule 3, R30
 * E8, and §10 wave E's first landing condition).
 *
 * WHY THIS EXISTS AND WHY NO `.rxt` BLOCK CAN REPLACE IT. A `.rxt` case drives
 * `<prefix>_search` and compares ONE span. R30 E8's hazard is not in that
 * span — it is in the other two entries, and specifically in two quantities a
 * span comparison cannot see:
 *
 *   1. THE FILTER. `docs/spec/match_api.md`'s match-here entry answers about
 *      exactly `ctx->pos`. In the DFA artifact that is `rx_search` plus
 *      `caps[0][0] != ctx->pos`, and §6.3 quotes it: under `\K` the filter
 *      compares against the POST-`\K` start and REJECTS a genuine anchored
 *      match. `a\Kb` at `ctx->pos == 0` returns -1 there where PCRE2 matches.
 *   2. THE RETURN VALUE. §6.3's second half: the DFA entry returns
 *      `caps[0][1] - caps[0][0]`, which under `\K` is the POST-`\K` length.
 *      A D38 callout uses that return as its ADVANCE, so a `\K` pattern used
 *      as a callout would advance by the wrong amount — silently. On `ab\K`
 *      the two numbers are 0 and 2, which is the difference between an
 *      advancing loop and an infinite one.
 *
 * THE VM'S ENTRIES ARE NOT THAT SHAPE, and E8's other correction is exactly
 * that the two engines' match-here entries do not share one. A `\K` pattern
 * is VM-forced (src/opt/select_engine.c), so its match-here entry calls
 * `<prefix>_match_impl` directly: the anchoring is structural rather than a
 * filter applied afterwards, and the return is `pos - ctx->pos`, computed
 * from positions and never from `caps`. This driver is what turns that from
 * a claim in a comment into three printed numbers.
 *
 * SO WHAT IS ASSERTED, per case, by the runner:
 *
 *     search      the reported span, against libpcre2 — the same answer the
 *                 `.rxt` corpus checks, printed here so the entries can be
 *                 compared against a common reference rather than only
 *                 against each other.
 *     match       the CONSUMED length at `ctx->pos`. Must be >= 0 wherever
 *                 libpcre2 matches AT that offset, and must be the number of
 *                 bytes consumed FROM `ctx->pos` — not the reported span's
 *                 width. This is the entry the D38 advance reads.
 *     match_caps  the same length AND the reported span, which is where the
 *                 `\K` write shows up. On `a\Kb` at 0 this prints length 2
 *                 with span (1,2): the two disagree by design, and a build
 *                 that made them agree has broken one of them.
 *
 * `match` and `match_caps` are driven SEPARATELY rather than one being
 * assumed to agree with the other, because they are two emitted functions
 * (`rx_matchfn`-typed and caps-delivering) and the whole subject of this file
 * is entries that were assumed to share a shape and did not.
 *
 * The prefix is fixed at `ke` (the runner compiles every case with `-p ke`),
 * for gstart_entries.c's reason: a driver cannot be generic over a C
 * identifier prefix. The HEADER name is not the prefix — `pcrec -o
 * <dir>/gen.c` writes `<dir>/gen.h` whatever `-p` says.
 *
 * Usage: ke_entries <subject-file> <startpos>     one cell, from argv
 *        ke_entries                                 many cells, from stdin
 *
 * THE BATCH FORM IS NOT A CONVENIENCE. This driver is called once per CELL,
 * and the sweep that uses it is (patterns x engines x subjects x every
 * startpos) — 23,548 cells on the shipped list. At one process per cell the
 * whole cost is fork/exec: measured 9m18s wall against 2m22s user, i.e. the
 * script spent three quarters of its time NOT running any of the code under
 * test. Reading `<subject-path> <startpos>` lines from stdin and printing one
 * result line each collapses that to one process per ARTIFACT, at no cost to
 * what is compared: each line still gets its own `<prefix>_work`, its own
 * `caps` arrays and its own `rx_ctx`, so no state crosses between cells.
 * The single-cell argv form is kept because §3's named advance cell drives
 * exactly one and reads better that way.
 *
 * MEASURED before and after, and the second number is the one that matters:
 * 9m18s -> 5m10s wall, with §2's own figures BYTE-IDENTICAL across the change
 * (23,548 cells, 2,462 of them with the consumed length differing from the
 * reported width, 0 wrong). A speedup that moved a count would have meant the
 * batching changed what was compared.
 *
 * Prints one line per cell:
 *   "search <r> [<s> <e>] | match <r> | caps <r> [<s> <e>]"
 * where every <r> is the RAW return, so a give-up code is never read as a
 * no-match (K21's class). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gen.h"

/* ONE CELL, and every buffer it touches is local to this call. The subject is
 * re-read per cell rather than cached: a cache keyed on the path would be a
 * second mechanism to get wrong, and the read is not what this driver's cost
 * was ever in. */
static int one_cell(const char *path, size_t sp)
{
    unsigned char buf[1 << 16];
    size_t n;
    FILE *f;
    ptrdiff_t caps[KE_NCAPS][2];
    int found;

    f = fopen(path, "rb");
    if (!f) { perror(path); return 2; }
    n = fread(buf, 1, sizeof buf, f);
    fclose(f);

    found = ke_search(buf, n, sp, caps);
    if (found == 1) printf("search 1 %td %td", caps[0][0], caps[0][1]);
    else            printf("search %d", found);

    /* THE `rx_matchfn`-TYPED ENTRY. It delivers no captures at all, so its
     * return is the ONLY thing a caller — a D38 callout among them — can act
     * on. That is exactly why it is driven on its own line here: on a `\K`
     * pattern this number and the reported span are different quantities, and
     * an entry that derived one from the other would print a plausible pair
     * that is wrong in the direction nothing else measures. */
    {
        rx_ctx ctx;
        ptrdiff_t here;
        ctx.subject = buf; ctx.len = n; ctx.pos = sp;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;
        here = ke_match(&ctx);
        printf(" | match %td", here);
    }

    /* THE CAPS-DELIVERING SIBLING, with its OWN array: A-8's untouched-wins
     * rule means a negative return leaves `caps` alone, so reusing the search's
     * array would let a stale span be read as this entry's answer. */
    {
        rx_ctx ctx;
        ptrdiff_t hcaps[KE_NCAPS][2];
        ptrdiff_t here;
        ctx.subject = buf; ctx.len = n; ctx.pos = sp;
        ctx.ncap = 0; ctx.caps = NULL; ctx.user = NULL;
        here = ke_match_caps(&ctx, hcaps);
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
        if (!sp) { fprintf(stderr, "ke_entries: malformed input line\n"); return 2; }
        *sp++ = '\0';
        /* A cell that cannot be read is a HARD failure, never a skipped line:
         * a batch driver that silently produced fewer lines than it was given
         * would shift every subsequent answer against the caller's own list,
         * and the caller compares positionally. */
        if (one_cell(line, (size_t)strtoul(sp, NULL, 10)) != 0) return 2;
    }
    return 0;
}
