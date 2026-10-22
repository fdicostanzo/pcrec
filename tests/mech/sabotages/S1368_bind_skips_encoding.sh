# S1368 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: bind takes a template of another encoding.
# Witness: cells `encbind`/`encbind2` want bind MISMATCH; reach token `encbind`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1368-bind-skips-encoding"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='bind takes a template of another encoding'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1368.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        || (sub->encoding >= 0 && sub->encoding != rx->encoding)\n"'
SAB_AFTER='"        || 0   /* SABOTAGE S1368 */\n"'
