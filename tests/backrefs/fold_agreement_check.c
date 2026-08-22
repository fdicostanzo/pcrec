/* tests/backrefs/fold_agreement_check.c — THE 256-BYTE AGREEMENT CHECK
 * (backrefs_design.md §4.1, R32 E8), swept over all 65,536 ORDERED PAIRS.
 *
 * WHAT IT TIES, AND WHY THE TWO SIDES ARE INDEPENDENT. pcrec's caseless fold
 * exists TWICE and cannot be made to exist once:
 *
 *   - at PARSE time, as the class widener `cls_casefold` applies (D23: an
 *     option compiles away, so `-i '[a]'` becomes the class {a, A} and the
 *     emitted matcher has no flag, no branch and no `tolower()`);
 *   - at MATCH time, inside the encoding residual `$_bref_match_caseless`,
 *     because a caseless backreference's operand is SUBJECT TEXT nobody has
 *     seen at compile time and there is no bitmap to widen.
 *
 * The first draft's answer was "reuse the same table as `\b`", which R32 E8
 * refuted: `cls_casefold` is `static`, takes a 32-byte BITMAP and widens it in
 * place — it is not a byte-to-byte map, and nothing in `src/gen/enc/` can call
 * it. So the residual would carry a SECOND SPELLING of A-Z <-> a-z with
 * nothing checking that the two agree, which is this project's named failure
 * shape pointed the other way: not a control sharing a source with its
 * subject, but two sources with no control at all.
 *
 * THIS IS THE MECHANISM THAT DISCHARGES IT. `pcrec_ascii_fold`
 * (src/core/fold.c) is the ONE OBJECT, and `cls_casefold` derives its widening
 * from it — so the table IS the parse-time fold by construction. The other
 * side is read out of an artifact PCREC ACTUALLY EMITTED: this file is
 * compiled against a generated `gen.c` and calls the shipped
 * `rx_bref_match_caseless` directly. Neither side can be edited into agreement
 * with the other without moving the thing it stands for.
 *
 * THE SWEEP IS ORDERED PAIRS, not the 52-byte set, because equality under a
 * fold is a RELATION and the two sides could agree on which bytes fold while
 * disagreeing about what they fold TO. Sabotage row S114 moves exactly one
 * byte ('z' stops folding) — the smallest divergence this check must still
 * see, and one a caseless corpus that happened to use no 'z' would not.
 *
 * MEASURED, and asserted here rather than assumed: exactly 52 bytes have a
 * partner, each has exactly one, and no byte >= 0x80 folds at all — libpcre2
 * 10.46's 8-bit non-UTF answer, and pcrec's own class fold re-measured against
 * it at zero disagreements. */
#include <stdio.h>

#include "core/internal.h"
#include "gen.h"

int main(void)
{
    int bad = 0, folding_pairs = 0, partnered = 0, nonascii = 0;
    int i, j;

    for (i = 0; i < 256; i++) {
        int partners = 0;
        for (j = 0; j < 256; j++) {
            unsigned char buf[2];
            ptrdiff_t r;
            int resid_eq, table_eq;

            /* The "capture" is buf[0..1) and the cursor is at 1, so the entry
             * compares byte i against byte j and returns 1 iff they are equal
             * under THIS ARTIFACT's fold. */
            buf[0] = (unsigned char)i;
            buf[1] = (unsigned char)j;
            r = rx_bref_match_caseless(buf, 2, 0, 1, 1);
            resid_eq = (r == 1);
            table_eq = (i == j) || (pcrec_ascii_fold[i] == (unsigned char)j);

            if (resid_eq != table_eq) {
                if (++bad <= 10)
                    printf("DISAGREE 0x%02x vs 0x%02x: residual says %s, "
                           "pcrec_ascii_fold says %s\n", i, j,
                           resid_eq ? "equal" : "different",
                           table_eq ? "equal" : "different");
                continue;
            }
            if (i != j && resid_eq) {
                folding_pairs++;
                partners++;
                if (i >= 0x80 || j >= 0x80) nonascii++;
            }
        }
        if (partners > 1) {
            printf("DEFECT 0x%02x has %d partners; every folding byte has "
                   "exactly one\n", i, partners);
            bad++;
        }
        if (partners == 1) partnered++;
    }

    /* The MEASURED shape of the fold, asserted so that a check agreeing over
     * an EMPTY folding relation cannot read as a pass. */
    if (partnered != 52) {
        printf("DEFECT %d bytes fold, expected exactly 52 (the ASCII "
               "letters)\n", partnered);
        bad++;
    }
    if (folding_pairs != 52) {
        printf("DEFECT %d folding ORDERED pairs, expected exactly 52\n",
               folding_pairs);
        bad++;
    }
    if (nonascii != 0) {
        printf("DEFECT %d folding pairs involve a byte >= 0x80; in the C "
               "locale those have no case (D23)\n", nonascii);
        bad++;
    }

    if (bad) {
        printf("fold-agreement: %d disagreement(s) over 65536 ordered pairs\n",
               bad);
        return 1;
    }
    printf("fold-agreement: 65536 ordered byte pairs, the SHIPPED "
           "$_bref_match_caseless and pcrec_ascii_fold induce the SAME "
           "partition; %d bytes fold, each with exactly one partner, none "
           ">= 0x80\n", partnered);
    return 0;
}
