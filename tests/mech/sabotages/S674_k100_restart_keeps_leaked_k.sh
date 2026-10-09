# S674 — [K100] A RESTARTING ROW NO LONGER RESTORES THE CALLER'S K
# (tests/codegen/run_size_term.sh §10).
#
# A row whose `sets.restart` cell is set (`prefilter-collapse`,
# `drop-prefilter`) restarts the size term: the artifact the ladder chose K
# for no longer exists. Its routine in `compile_driver` puts back
# `defo.unroll_k`, which the ladder's trials and FINAL attempt overwrote
# (K100). This plant drops that write, so the restarted default attempt runs
# at the leaked K, its term reads `option` and the ladder never runs again:
# K100 as filed. At the shipped limits no corpus pattern reaches it
# (population 0); §10's lowsize reference compiler does, and B1's witness
# `(?:aa|a){8,12}+ab` refuses again.
SAB_ID="S674-k100-restart-keeps-leaked-k"
SAB_FILE="src/core/compile.c"
SAB_SUITES="sizeterm"
SAB_DESC="a restarting fallback row resets the size term's phase and record but not defo.unroll_k, so the restarted default attempt runs at the K the ladder wrote, reads 'option' and never re-runs the ladder -- K100 undone; the lowsize witness refuses again"
SAB_DOC_FIGURE="tests/codegen/run_size_term.sh §10 goes 38/0 -> 34/1 (the witness REFUSED; its four follow-on checks do not run), exactly what the pre-fix tree read (9b1f78df, 34/1). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S674."
SAB_COUNT=1
SAB_BEFORE='                defo.unroll_k = user_unroll_k;'
SAB_AFTER='                (void)user_unroll_k;   /* SABOTAGE S674: the restart keeps the leaked K */'
