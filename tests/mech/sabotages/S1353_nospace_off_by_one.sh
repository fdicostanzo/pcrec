# S1353 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: replace-all's fit test is len < room, so an output exactly cap long is NOSPACE.
# Witness: every out cell's exact arm (replace-all at cap == the length) must return the count.
# Reach (K35): token exact; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1353-nospace-off-by-one"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all'\''s fit test is len < room, so an output exactly cap long is NOSPACE'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1353.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (*fits && out && pc[i].len <= cap - *w) {\n"'
SAB_AFTER='"        if (*fits && out && pc[i].len < cap - *w) {   /* SABOTAGE S1353 */\n"'
