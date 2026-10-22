# S1347 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the element's end < start span check is removed, so a backward span is rendered.
# Witness: the `backward2` cell (`x(?=(?1))|(b\K)` on "xb", `[x]`, no group read): BADSPAN expected.
# Reach (K35): token S1347 (cells backward, backward2); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1347-badspan-backward-check"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element'\''s end < start span check is removed, so a backward span is rendered'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1347.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (c[0][0] < 0 || c[0][1] < c[0][0] || (size_t)c[0][1] > ctx->len\n"'
SAB_AFTER='"        if (c[0][0] < 0 || (size_t)c[0][1] > ctx->len   /* SABOTAGE S1347 */\n"'
