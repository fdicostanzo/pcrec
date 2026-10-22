# S1351 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the element's slot < ctx->ncap test on a map entry is removed.
# Witness: every referencing cell's mis arm (a map whose entries are all ncaps, the element over it without the check) must return MISMATCH.
# Reach (K35): token mis; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1351-element-ncap-check"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element reads a map slot at or past ctx->ncap'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1351.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (sl < 0 || (size_t)sl >= nc) return -3;\n"'
SAB_AFTER='"        if (sl < 0) return -3;   /* SABOTAGE S1351 */\n"'
