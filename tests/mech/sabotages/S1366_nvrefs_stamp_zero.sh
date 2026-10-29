# S1366 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: <S>_NVREFS is the bare count, 0 for a template with no ${!name}.
# Witness: the `hs.h` header check wants `HS_NVREFS 1` (subst_api.md §5¶2).
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1366-nvrefs-stamp-zero"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='<S>_NVREFS is the bare count, 0 for a template with no ${!name}'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1366.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_stampf(sb, up, "NVREFS", "%d", at_least_one(t->nvrefs));'
SAB_AFTER='    pcrec_sb_stampf(sb, up, "NVREFS", "%d", t->nvrefs);   /* SABOTAGE S1366 */'
