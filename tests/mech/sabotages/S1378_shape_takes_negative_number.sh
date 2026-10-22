# S1378 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: rx_shape_match takes a needed row with a negative number.
# Witness: the driver's `shape` line wants row 0 refused; reach token `negnum`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1378-shape-takes-negative-number"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='rx_shape_match takes a needed row with a negative number'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1378.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            if (e->number < 0 || (e->number != 0\n"'
SAB_AFTER='"            if ((e->number != 0   /* SABOTAGE S1378 */\n"'
