#!/usr/bin/env bash
# S766 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- a tie takes end n-1 without the anchored run.
# Detector: the answer net's greedy ties: `\s*$` on " \n" is (0,2), `\s+$` on "a \n".
SAB_ID='S766-revend-tie-takes-n1'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='a tie takes end n-1 without the anchored run'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S766.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\s+$" && grep -q "revend_len = rx_match(&revend_ctx)" "$REACH_TMP/o.c" && echo REACH-T2'
SAB_REACH_EXPECT='REACH-T2'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                   "        revend_end = revend_start + (size_t)revend_len;\n"'
SAB_AFTER='                   "        revend_end = subject_length - 1; (void)revend_len;   /* SABOTAGE S766 */\n"'
