# S1355 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the glue drops the tail after the last match.
# Witness: the `tail` cell (`a` -> `b` on "xa y"): xb y expected.
# Reach (K35): token S1355 (cell tail); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1355-tail-dropped"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the glue drops the tail after the last match'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1355.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    rx_subst_put(&cur, out, cap, ctx.subject + cur.prev, ctx.len - cur.prev);\n"'
SAB_AFTER='"    (void)0;   /* SABOTAGE S1355 */\n"'
