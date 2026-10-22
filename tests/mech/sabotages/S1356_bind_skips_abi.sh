# S1356 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the check no longer compares the subst record's abi with the header's.
# Witness: every cell's babi arm (the check against a record copy with abi + 1) must be MISMATCH.
# Reach (K35): token abi; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1356-bind-skips-abi"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the check no longer compares the record'\''s abi with the header'\''s'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1356.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (t->abi != PCREC_RX_ABI_H || (t->support && *t->support != t->support_id)\n"'
SAB_AFTER='"    if ((t->support && *t->support != t->support_id)   /* SABOTAGE S1356 */\n"'
