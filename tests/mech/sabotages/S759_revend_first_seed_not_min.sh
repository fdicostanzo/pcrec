#!/usr/bin/env bash
# S759 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the first accepting seed is kept instead of the smallest start over the seeds.
# Detector: the answer net: `\s*$|x\z`, `[^\n]*\n?$` and the tie families, where seed n-1 reaches further left.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the two-seed walk (F0/F3/F4) keeps it; its detector is now the F3 witness
# `(?:\n\n|a){0,4}$` on "\n\n\n" (seed n reaches 1, seed n-1 reaches 0) in
# tests/endmark/b3_rows.rxt, run by the endmark arm. Reach: that pattern takes
# form two-seed.
SAB_ID='S759-revend-first-seed-not-min'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='endmark'
SAB_DESC='the first accepting seed is kept instead of the smallest start over the seeds'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S759.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "(?:\\n\\n|a){0,4}$" | grep -F "form=two-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='               "        if (match_start_position < revend_start) {\n"'
SAB_AFTER='               "        if (revend_start == (size_t)-1) {   /* SABOTAGE S759 */\n"'
