# S1346 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the element's start < previous-end span check is removed, so an overlapping span's gap wraps.
# Witness: the `overlap` cell (`x|(?<=(?1))y|(\Kx)` on "xy", `[$0]`): BADSPAN expected; the wrapped gap is a SIZE_MAX-long piece.
# Reach (K35): token S1346 (cell overlap); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1346-badspan-prev-check"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element'\''s start < previous-end span check is removed, so an overlapping span'\''s gap wraps'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1346.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            || ((flags & RX_SUBST_GAPS) && (size_t)c[0][0] < prev)) {\n"'
SAB_AFTER='"            || 0) {   /* SABOTAGE S1346 */\n"'
