#!/usr/bin/env bash
# S1919 (lane sar1, 2026-11-09; span_arms R1, witness W-R6, docs/design/span_arms.md §3.6) -- THE WIDTH OF THE UNROLLED COPIES.
#
# T2 row 2 (src/facts/req.c `rr_rep_exact`) gives an exact repeat its exact
# width, `rr_rep_w`, whatever count was unrolled. This plant keeps the width
# of the unrolled copies: `a.` is not `all`, so 2 copies are unrolled and
# `(a.){10}` is 4 bytes wide where it is 20. The run `xyz` is then placed
# at most 4 bytes into the attempt (K 4, 5 for the `.?` twin), the handoff
# skips the attempt at 0 and no later start matches. Detector: the harness
# on tests/litscan/spanarms.rxt (VM and DFA witnesses).
SAB_ID="S1919-rep-width-from-copies"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_DESC="the necessary-run walk takes an exact repeat's width from the copies it unrolled instead of the repeat's count, so every run after it is placed too near the attempt start and the handoff skips the attempt that matches"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1919."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a.){10}xyz" && grep -qE "^#define RX_REQ_HANDOFF \"20\"$" "$REACH_TMP/o.c" && echo REACH-WR6-K20'
SAB_REACH_EXPECT="REACH-WR6-K20"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.maxw = rr_rep_w(m, b.maxw);'
SAB_AFTER='    /* SABOTAGE S1919: the width of the unrolled copies */'
