#!/usr/bin/env bash
# S3279 -- lane forms (R-45 plan A, r45_reply.md rev 6 §3 "The head lever and its identity check"):
# THE HEAD LEVER IS IGNORED. the span form table, wfS (memfn/src/window.c; formerly wf_span_head), drops the lever `span-head=N`, so every
# compile takes the shipped head 64: the cards would time H(64) under every grid head's name. The
# detector is G2's WINDOW family's head passes (memfn/tests/run_g2_win.sh, every finite grid head):
# the generator's exact loop pin (a loop G2 expects at the head is missing) and each pass's
# per-family loop floors (LOOP_FLOORS_<h>, every family at every head: review r35 F13) red.
# Re-aimed by lane bsu1 (R-47 U1, block_span.md §10.2): wf_span_head retired into THE SPAN FORM TABLE (wfS); the plant is now T-lever's predicate never holding.
SAB_ID="S3279-span-head-lever-ignored"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="the span form table's T-lever never holds: every head pass renders the default, G2's window family's loop floors must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the head passes' exact loop pin and loop floors (lane formsfixb 2026-11-17; first by hand, lane forms). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3279."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return x->d->art->levers & KIT_LEVER_SPAN_HEAD;'
SAB_AFTER='    (void)x; return 0;   /* SABOTAGE S3279 */'
