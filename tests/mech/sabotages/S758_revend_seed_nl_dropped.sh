#!/usr/bin/env bash
# S758 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the walk's n-1 seed dropped: a `$`/`\Z` match ending before a final newline is lost.
# Detector: the answer net: `\d+$` on "abc123\n" and `a*$` on "aa\n" answer NOMATCH or the empty end match.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the n-1 seed is now F1 `one-seed`'s last-byte choice; the plant drops it
# there, and its own detectors (`\d+$` on "abc123\n", `a*$` on "aa\n") are
# F1 artifacts. Reach: `\d+$` takes form one-seed (--emit-facts end_mark).
SAB_ID='S758-revend-seed-nl-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='the walk'\''s n-1 seed dropped: a `$`/`\Z` match ending before a final newline is lost'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S758.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\d+$" | grep -F "form=one-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='               "    if (subject_length > 0 && subject[subject_length - 1] == %s) {\n"'
SAB_AFTER='               "    if (0 && subject[subject_length - 1] == %s) {   /* SABOTAGE S758 */\n"'
