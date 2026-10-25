# S1376 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: a 129-byte group name is taken.
# Witness: the refusal table's 129-byte `${L..}` and `$L..` rows.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1376-name-length-off-by-one"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='a 129-byte group name is taken'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1376.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (name && !var && nlen > PCREC_MAX_GROUP_NAME) {'
SAB_AFTER='        if (name && !var && nlen > PCREC_MAX_GROUP_NAME + 1) {   /* SABOTAGE S1376 */'
