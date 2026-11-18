#!/usr/bin/env bash
# S3279 -- lane forms (R-45 plan A, r45_reply.md rev 6 §3 "The head lever and its identity check"):
# THE HEAD LEVER IS IGNORED. wf_span_head (memfn/src/window.c) drops the lever `span-head=N`, so every
# compile takes the shipped head 64: the cards would time H(64) under every grid head's name. The
# detector is G2's WINDOW family's head passes (memfn/tests/run_g2_win.sh, every finite grid head):
# the generator's exact loop pin (a loop G2 expects at the head is missing) and each pass's
# per-family loop floors (LOOP_FLOORS_<h>, every family at every head: review r35 F13) red.
SAB_ID="S3279-span-head-lever-ignored"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_span_head ignores the span-head lever: every head pass renders the default, G2's window family's loop floors must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the head passes' exact loop pin and loop floors (lane formsfixb 2026-11-17; first by hand, lane forms). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3279."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (art && (art->levers & KIT_LEVER_SPAN_HEAD)) return (int32_t)art->span_head;'
SAB_AFTER='    (void)art;   /* SABOTAGE S3279 */'
