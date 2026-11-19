#!/usr/bin/env bash
# S3282 -- lane formsfixb (review r35 F14, the sibling of S3279): THE HEAD LEVER IS READ AS A SMALLER
# HEAD. wf_span_head (memfn/src/window.c) honours the lever `span-head=N` but takes every N as 0 (L),
# so each head pass renders more loops, not fewer: the loop-count floors (lower bounds) all hold and
# the answers are unchanged. The detector is G2's WINDOW family's head passes (memfn/tests/
# run_g2_win.sh): the generator's reading that no loop starts below the pass's head, and its exact
# loop pin, are red at every head past 0.
SAB_ID="S3282-span-head-lever-read-as-zero"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_span_head reads every span-head=N as 0: loops below the head, G2's window family's head check must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the head passes' loop reading: lane formsfixb 2026-11-17. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3282."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (art && (art->levers & KIT_LEVER_SPAN_HEAD)) return (int32_t)art->span_head;'
SAB_AFTER='    if (art && (art->levers & KIT_LEVER_SPAN_HEAD)) return 0;   /* SABOTAGE S3282 */'
