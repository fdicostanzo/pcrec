# S1454 — the post-resolution pass never asks whether a lookbehind's length
# re-enters itself, so `(?<=(?R))x` compiles again (K127). Lane langfix2.
SAB_ID="S1454-lookbehind-recursion-unchecked"
SAB_FILE="src/opt/postresolve.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/inlookaround_self.rxt"
SAB_DESC="pcrec_postresolve passes recurses=false for every deferred lookbehind"
SAB_DOC_FIGURE="PREDICTED: the perr blocks of tests/recursion/inlookaround_self.rxt whose branch widths are otherwise fixed now compile and fail; the ACCEPTED controls stay green. Canonical figure owed from run_sabotage_matrix.sh S1454."
SAB_COUNT=1
SAB_BEFORE="                                    pcrec_callgraph_lookbehind_recurses(cx, p.at[i]));"
SAB_AFTER="                                    false);   /* SABOTAGE S1454 */"
