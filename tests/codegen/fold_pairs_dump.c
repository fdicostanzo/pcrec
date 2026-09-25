/* tests/codegen/fold_pairs_dump.c — SOURCE A for run_cls_fold_agreement.sh's
 * two-independent-sources check, tests/backrefs/fold_agreement_check.c's own
 * shape one mechanism over ([FORM-CHAR], docs/design/compare_stack.md
 * §duplications).
 *
 * WHAT IT DERIVES AND WHY THE POPULATION IS NEVER HAND-TYPED. The VM class
 * emitter's fold shape (src/gen/emit_vm.c's `vm_cls_shape`/`vm_cls_test`) has
 * its own, SEPARATE recognizer for "is this two-member class a fold pair" —
 * `count == 2 && (lo ^ hi) == 0x20 && lo >= 'A' && lo <= 'Z'` — spelled with
 * no reference to `pcrec_ascii_fold` (src/core/fold.c), the ONE table this
 * project has otherwise made the ground truth for the ASCII fold relation
 * (tests/backrefs/fold_agreement_check.c's own header). Nothing ties the two
 * together, so a future edit to either — the table gaining or losing a pair,
 * the recognizer's letters conjunct being narrowed or widened — could drift
 * from the other with no check noticing.
 *
 * This program reads `pcrec_ascii_fold` DIRECTLY (linked from libpcrec.a,
 * never copied) and prints the population run_cls_fold_agreement.sh needs to
 * drive real compiles from — never a list someone typed by hand:
 *
 *   F <lo> <hi>   — a genuine ASCII fold pair per fold.c (lo < hi, lo's
 *                   partner is hi and hi's is lo). Exactly the 26 letter
 *                   pairs today; the shell script floors rather than pins
 *                   the count, so a future change to the table is measured,
 *                   not assumed.
 *   N <lo> <hi>   — a NEAR-MISS: hi == lo | 0x20 (the same bit relationship
 *                   every real fold pair has) but fold.c says NEITHER byte
 *                   folds. These are the punctuation bytes that sit either
 *                   side of the letter block (0x40 '@', 0x5B-0x5F
 *                   '[' '\' ']' '^' '_') and are exactly the population
 *                   S228's sabotage (the recognizer's letters conjunct
 *                   dropped) needs a WITNESS from — a class the compiler
 *                   must NOT give the fold shape.
 *
 * THE RANGE 0x40..0x5F IS THE WHOLE CANDIDATE SET, not an arbitrary
 * shrinking: `hi = lo | 0x20` requires bit 5 of `lo` clear, and 0x40..0x5F is
 * exactly the printable-ASCII half of the four such 32-byte bands (the other
 * three are non-printable or non-ASCII) — every byte capable of pairing with
 * another under this exact mask lands in one of these two lines, with none
 * omitted. */
#include <stdio.h>

#include "core/internal.h"

int main(void)
{
    int nf = 0, nn = 0;

    for (unsigned lo = 0x40; lo <= 0x5f; lo++) {
        unsigned hi = lo | 0x20u;
        if (pcrec_ascii_fold[lo] == hi && pcrec_ascii_fold[hi] == lo) {
            printf("F %u %u\n", lo, hi);
            nf++;
        } else if (pcrec_ascii_fold[lo] == lo && pcrec_ascii_fold[hi] == hi) {
            printf("N %u %u\n", lo, hi);
            nn++;
        } else {
            /* Neither a clean fold pair nor a clean non-fold pair — e.g. one
             * side folds to something OTHER than the other side. fold.c's
             * own measured shape (backrefs_design.md §4.1: every folding
             * byte has exactly one partner, and it is always the 0x20
             * neighbour for a letter) makes this unreachable today; printed
             * rather than silently dropped, so a future table change that
             * broke the relation would show up as a THIRD line kind instead
             * of a quietly shrunken F/N population. */
            printf("X %u %u\n", lo, hi);
        }
    }
    fprintf(stderr, "fold_pairs_dump: %d fold pair(s), %d near-miss pair(s)\n",
            nf, nn);
    return 0;
}
