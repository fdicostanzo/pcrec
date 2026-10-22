# S1369 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the element takes a match end past ctx->len.
# Witness: every no-variable cell's `blen` arm wants BADSPAN.
# Reach (K35): token blen; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1369-span-end-past-len"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element takes a match end past ctx->len'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1369.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (c[0][0] < 0 || c[0][1] < c[0][0] || (size_t)c[0][1] > ctx->len\n"'
SAB_AFTER='"        if (c[0][0] < 0 || c[0][1] < c[0][0]   /* SABOTAGE S1369 */\n"'
