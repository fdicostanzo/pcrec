# S1368 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the check and the by-name helper (both sites, COUNT 2) take a template of another encoding.
# Witness: cells `encbind`/`encbind2` want the check MISMATCH.
# Reach (K35): token encbind; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1368-bind-skips-encoding"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the check and the by-name helper take a template of another encoding'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1368.'
SAB_EXPECT=DETECTED
SAB_COUNT=2
SAB_BEFORE='"        || rx->ncaps < 1 || (t->encoding >= 0 && t->encoding != rx->encoding)\n"'
SAB_AFTER='"        || rx->ncaps < 1   /* SABOTAGE S1368 */\n"'
