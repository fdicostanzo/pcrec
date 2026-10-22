# S1351 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the element's ctx->ncap == binding ncaps check is removed.
# Witness: every cell's mis arm (the element at k = 0 with ncap + 1) must return MISMATCH.
# Reach (K35): token S1351 (every bound cell); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1351-element-ncap-check"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element'\''s ctx->ncap == binding ncaps check is removed'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1351.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                       "        || nc != (size_t)b->ncaps || (flags & ~RX_SUBST_GAPS)", p);'
SAB_AFTER='                       "        || (flags & ~RX_SUBST_GAPS)", p);   /* SABOTAGE S1351 */'
