# S393 ([CLS-TREE] S4, lane s4build) -- THE KIT'S FORM IGNORES `--tune`.
#
# ANSWER-NEUTRAL: every form is exhaustively equivalent (tests/clskit/), so an
# emitter that asked the class table at `balanced` whatever the dial said
# answers every cell right at every position. The plant hands
# `pcrec_clskit_select` position 0. tests/codegen/run_tune_dial.sh §3d reads
# the matcher's FORM off the emitted text per position and goes red at -2/-1
# (want K, gets P3) and +2 (want P2, gets P3).
SAB_ID="S393-wcls-tune-unwired"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="tunedial"
SAB_DESC="vm_wcls hands pcrec_clskit_select position 0 whatever --tune says, so the class table's size and speed rows never fire (answer-identical)"
SAB_DOC_FIGURE="MEASURED solo 2026-09-30 at the s4build tip: tunedial:3fail/19pass DETECTED -- §3d at -2, -1 and +2."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    ClsSelectIn in = { v->cx->opt->tune, 0, NULL };'
SAB_AFTER='    ClsSelectIn in = { 0, 0, NULL };'
