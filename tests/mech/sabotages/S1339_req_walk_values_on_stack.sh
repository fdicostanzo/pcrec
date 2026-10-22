# S1339 ([DD-10], lane dd10) -- rb_walk's child results go back on the C stack instead of the depth-indexed
# slots: 2.6 KB per frame, two frames per nesting level (1.38 MB at depth 250, measured). Same answers; only
# the compile-stack arm sees it. Detector: tests/thread/run_compile_stack.sh.
SAB_ID="S1339-req-walk-values-on-stack"
SAB_FILE="src/facts/req.c"
SAB_SUITES="compilestack"
SAB_DESC='rb_walk keeps its two child RbVal results in its own C frame instead of RbWalk.slot'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1339.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    RbVal *t = rb_slots(w);'
SAB_AFTER='    RbVal tl[2], *t = tl;   /* SABOTAGE S1339 */'
