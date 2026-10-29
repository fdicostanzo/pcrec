# S1355 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: replace-all drops the tail after the last match.
# Witness: the `tail` cell (`a` -> `b` on "xa y"): replace-all gives xb y.
# Reach (K35): token S1355 (cell tail); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1355-tail-dropped"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all drops the tail after the last match'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1355.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        pcrec_subst_append_(&tail, 1, out, cap, &w, &fits);\n"'
SAB_AFTER='"        (void)tail;   /* SABOTAGE S1355 */\n"'
