#!/usr/bin/env bash
# S759 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the first accepting seed is kept instead of the smallest start over the seeds.
# Detector: the answer net: `\s*$|x\z`, `[^\n]*\n?$` and the tie families, where seed n-1 reaches further left.
SAB_ID='S759-revend-first-seed-not-min'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='the first accepting seed is kept instead of the smallest start over the seeds'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S759.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\s+$" && grep -q "for (int revend_seed = 0;" "$REACH_TMP/o.c" && echo REACH-WALK'
SAB_REACH_EXPECT='REACH-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='               "        if (match_start_position < revend_start) {\n"'
SAB_AFTER='               "        if (revend_start == (size_t)-1) {   /* SABOTAGE S759 */\n"'
