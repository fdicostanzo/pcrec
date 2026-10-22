# S1501 -- [M4-SUBST] (lane substb2; docs/design/replace_design.md §R4,
# docs/spec/subst_api.md §4¶14).
#
# Plant: the element's room test is removed, so it writes pieces past o->cap.
# Witness: every cell's `room` arm (two matches into a piece array one short) wants NOSPACE with n and prev untouched.
# Reach (K35): token room; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1501-element-room-test-removed"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element'\''s room test is removed, so it writes pieces past o->cap'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1501.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (o->n > o->cap || (P && k > (o->cap - o->n) / P)) {\n"'
SAB_AFTER='"    if (0) {   /* SABOTAGE S1501 */\n"'
