/* tests/harness/outcome_word.h — THE ONE PRINTER of a negative
 * `<prefix>_search` return, shared by driver.c (both of its paths) and
 * HARNESS_BATCH's generated dispatch.c (tests/harness/dispatch_gen.sh).
 *
 * [axtri, 2026-10-07] It used to be hand-kept copies, and dispatch.c's fell
 * behind TWICE: [VAR]'s `unset-var` and [UTF-VALID]'s `utf <offset>` never
 * reached it, so under HARNESS_BATCH every `-futf-check` refusal printed
 * `giveup -9` and make test-axes' -futf-check arm failed all 990 of its
 * ill-formed cells (docs/dev/lanes/axtri_report.md). One table, included
 * by both, is the fix; a new code gets its word HERE and both drivers have
 * it.
 *
 * The words: every typed give-up code (`steps`/`frames`/`work`/`recurse`),
 * `internal` (PCREC_ERR_INTERNAL — below the floor, the artifact caught its
 * own inconsistency; run.sh's `gu` refuses to let a block expect it),
 * `unset-var` (PCREC_ERR_UNSET_VAR, a caller refusal a block MAY expect),
 * and `utf <offset>` (PCREC_ERR_UTF, -futf-check refused an ill-formed
 * subject — the offset is `<prefix>_valid_upto` at the SAME startpos, what
 * tests/axes/utfcheck_arm.py compares; no `gu` word, reached only under
 * RXTFLAGS). Any other negative code prints `giveup <n>` rather than a
 * guess — PCREC_ERR_STARTPOS (-7) still does (varmvp_report.md's flagged
 * gap). The caller exits 3 after this, whatever was printed.
 *
 * Include AFTER an artifact header: the PCREC_ERR_* codes are the
 * artifact's own #defines. `valid_upto` is that artifact's
 * `<prefix>_valid_upto`, called only for PCREC_ERR_UTF. */
#ifndef RXT_OUTCOME_WORD_H
#define RXT_OUTCOME_WORD_H

#include <stdio.h>

static void rxt_print_negative(int code,
                               size_t (*valid_upto)(const unsigned char *, size_t, size_t),
                               const unsigned char *buf, size_t len, size_t pos)
{
    const char *word = code == PCREC_ERR_STEPS     ? "steps"
                     : code == PCREC_ERR_FRAMES    ? "frames"
                     : code == PCREC_ERR_WORK      ? "work"
                     : code == PCREC_ERR_RECURSE   ? "recurse"
                     : code == PCREC_ERR_INTERNAL  ? "internal"
                     : code == PCREC_ERR_UNSET_VAR ? "unset-var"
                     : NULL;
    if (code == PCREC_ERR_UTF)
        printf("utf %zu\n", valid_upto(buf, len, pos));
    else if (word) printf("%s\n", word);
    else printf("giveup %d\n", code);
}

#endif
