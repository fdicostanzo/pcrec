# S1364 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the glue's batch buffer holds kmax pairs, not kmax * ncaps.
# Witness: the `ncaps30`/`ncaps300` cells (next_n writes ncaps pairs per entry): a stack overrun,
# which run_subst_tests.sh section 4 (the cells under ASan, lane substfix) sees on any box.
# Reach (K35): token nogroupceiling (cell ncaps300); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1364-batch-buffer-one-pair"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the glue'\''s batch buffer holds kmax pairs, not kmax * ncaps'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1364.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    ptrdiff_t buf[kmax * nc][2];                 /* at least one match at any ncaps */\n"'
SAB_AFTER='"    ptrdiff_t buf[kmax][2];   /* SABOTAGE S1364 */\n"'
