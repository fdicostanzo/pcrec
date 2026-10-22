# S1500 -- [M4-SUBST] (lane substb2; docs/design/replace_design.md §R4,
# docs/spec/subst_api.md §10¶7).
#
# Plant: replace-all's batch size ignores RX_FOREACH_PAIRS / ncap, so <rx>_next_n
# writes more pairs than its stack array holds.
# Witness: the `ncaps30` cell (30 pairs a match, 64 matches a batch into 256
# pairs) is a stack overrun ASan reports in run_subst_tests.sh's sanitizer pass;
# `ncaps300` (301 pairs a match) wants MISMATCH and gets the overrun.
# Reach (K35): token pairs (cell ncaps300); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1500-replace-all-batch-past-pairs"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all'\''s batch size ignores RX_FOREACH_PAIRS / ncap, so next_n overruns its stack array'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1500.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    k = nc <= RX_FOREACH_PAIRS ? RX_FOREACH_PAIRS / nc : 0;\n"'
SAB_AFTER='"    k = RX_FOREACH_PAIRS;   /* SABOTAGE S1500 */\n"'
