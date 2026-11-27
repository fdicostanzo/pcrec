# S3603 -- [ARENA-SCOPES] F1, ruling R-1 (lane arenabuild2, 2026-11-25): the
# binding test of W7's DFA-memo exclusion. compile_driver's nomem arrival
# (`fb-nomem`) returns without freeing the attempt's DFA memo arena.
#
# W7 excludes the memo arena from its hand-kept window on the premise that
# compile_driver frees it on EVERY arrival, refusals included. alloc_check now
# asserts that premise in every child (a memo arena still holding a block when
# the compile returns exits 6, a FAIL naming the memo), so the plant must turn
# W1's malloc sweep red there, not only as an anonymous stranded block.
SAB_ID="S3603-dfa-memo-not-freed-on-nomem"
SAB_FILE="src/core/compile.c"
SAB_SUITES="resource"
SAB_DESC="compile_driver's fb-nomem arrival returns without pcrec_dfa_memo_free: the memo arena strands on every nomem refusal after the DFA was built; alloc_check's memo-premise assertion (R-1) names it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3603."
SAB_REACH_POP="tests/core/alloc_check.c|if \\(mm_n\\) _exit\\(6\\);|1"
SAB_COUNT=1
SAB_BEFORE='                FIT_TRACE(&cx, rung->name, 0, "fb-nomem");
                job_cleanup(&cx);
                pcrec_dfa_memo_free(&dmemo);'
SAB_AFTER='                FIT_TRACE(&cx, rung->name, 0, "fb-nomem");
                job_cleanup(&cx);   /* SABOTAGE S3603: the memo is not freed */'
