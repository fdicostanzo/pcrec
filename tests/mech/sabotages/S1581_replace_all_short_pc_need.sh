# S1581 -- [M4-SUBST] lane substr1fix (review 2026-10-24-r1-subst-code IFACE-4;
# docs/spec/subst_api.md §10¶7-¶8).
#
# Plant: replace-all with a piece array below one match's pieces reports no need.
# Witness: run_subst_tests.py's `pshort` arm (every cell: replace-all with
# o->cap = npieces - 1 must answer NOSPACE with o->need = npieces, *len untouched).
# Reach (K35): token pshort; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1581-replace-all-short-pc-need"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all with a piece array below one match'\''s pieces reports no need'
SAB_DOC_FIGURE='Owed: lane substr1fix queued this row (docs/dev/lanes/substland_report.md, substr1fix STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1581.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (o->cap < P) { o->need = P; return PCREC_SUBST_NOSPACE; }   /* not one match'\''s pieces */\n"'
SAB_AFTER='"    if (o->cap < P) { o->need = 0; return PCREC_SUBST_NOSPACE; }   /* SABOTAGE S1581 */\n"'
