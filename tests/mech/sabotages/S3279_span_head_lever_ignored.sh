#!/usr/bin/env bash
# S3279 -- lane forms (R-45 plan A, r45_reply.md rev 6 §3 "The head lever and its identity check"):
# THE HEAD LEVER IS IGNORED. wf_span_head (memfn/src/window.c) drops the lever `span-head=N`, so every
# compile takes the shipped head 64: the cards would time H(64) under every grid head's name. The
# detector is G2's WINDOW family's head passes (memfn/tests/run_g2_win.sh): each pass's per-family
# loop floors (LOOP_FLOORS_0/8/24) red, the looped-site counts falling to 0.
SAB_ID="S3279-span-head-lever-ignored"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_span_head ignores the span-head lever: every head pass renders the default, G2's window family's loop floors must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the head passes' loop floors: lane forms 2026-11-17, by hand. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3279."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (art && (art->levers & KIT_LEVER_SPAN_HEAD)) return (int32_t)art->span_head;'
SAB_AFTER='    (void)art;   /* SABOTAGE S3279 */'
