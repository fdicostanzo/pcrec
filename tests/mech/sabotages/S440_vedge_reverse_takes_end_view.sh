# S440 ([OPT-VEDGE], lane vedge) -- THE REVERSE MACHINE TAKES END-VIEW MEMBERS.
#
# The view-tolerant scan edge admits a chain member that carries an END (\z)
# view only on a machine whose walk ENDS at the subject's end, where the loop
# evaluates the view at `pos == n` and stops (src/opt/scanedge.c, precondition
# (3)'s relaxation; `end_is_exit`). The reverse walk STARTS at `n` and steps
# FROM the view-selected state there, and the edge path runs before the view
# select, so an END-viewed head on the reverse machine scans from `n` without
# ever taking its view. The plant passes `end_is_exit = true` for the reverse
# machine. Witness: `[a-z]{2,4}(?:\z|[a-z])`, whose reverse start state is a
# scan-shaped END-viewed member -- "ab" answers nomatch against [0,2]
# (measured on a scratch build of this plant at 41aec745: 23 of
# tests/assertions/view_edge.rxt's cells red, every one on that pattern). No
# corpus artifact outside that file moves under the plant (a whole-corpus
# artifact diff found 0), so the row is scoped to tests/assertions.
SAB_ID="S440-vedge-reverse-takes-end-view"
SAB_FILE="src/core/compile.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/assertions"
SAB_DESC="compile.c passes end_is_exit=true to pcrec_scanedge_dfa for the REVERSE machine, so its END-viewed start state becomes a scan-edge head that scans from n without taking its view: [a-z]{2,4}(?:\\z|[a-z]) on \"ab\" answers nomatch against [0,2]"
SAB_DOC_FIGURE="MEASURED 2026-10-03 (lane vedge, scratch build of this plant at 41aec745): tests/assertions/view_edge.rxt 23 fail / 2680 pass; the harness arm's own figure over tests/assertions is OWED to a matrix run."
# [MECH-REACH] the witness still compiles to a two-machine DFA artifact whose
# reverse walk exists to be broken.
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "[a-z]{2,4}(?:\\z|[a-z])" | grep -c -e "#define RX_ENGINE \"dfa\"" -e "RX_DFA_START \"reverse-pass\""'
SAB_REACH_EXPECT="2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                pcrec_scanedge_dfa(&cx, &cx.job->rdfa,
                                   pcrec_dfa_scan_state_written(&cx, &cx.job->rdfa), false);'
SAB_AFTER='                pcrec_scanedge_dfa(&cx, &cx.job->rdfa,
                                   pcrec_dfa_scan_state_written(&cx, &cx.job->rdfa), true);   /* SABOTAGE S440 */'
