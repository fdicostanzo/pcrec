# S1356 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: bind no longer compares the records' abi with the header's.
# Witness: every cell's babi arm (an rx record copy with abi + 1) must be MISMATCH.
# Reach (K35): token abi (every cell); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1356-bind-skips-abi"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='bind no longer compares the records'\'' abi with the header'\''s'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1356.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (rx->abi != PCREC_RX_ABI_H || sub->abi != PCREC_RX_ABI_H || rx->ncaps < 1\n"'
SAB_AFTER='"    if (rx->ncaps < 1   /* SABOTAGE S1356 */\n"'
