#!/usr/bin/env bash
# S3280 -- lane formsfixb (review r35 F14, R-45 r45_reply.md rev 6 §3 "The forms"): A LOOP STARTS ONE
# OFFSET PAST THE HEAD. wf_loop_len (memfn/src/window.c) compares the entry's offset with `<=` instead of
# `<`, so the entry AT the head is a lone test and every loop starts at h + 1: the answers are unchanged
# and the identity check (both sides carry the same wf_loop_len) cannot see it, so the cards would time
# a head under the next one's name. The detector is G2's WINDOW family's head passes (memfn/tests/
# run_g2_win.sh, the lever span-head=N at every finite grid head): the generator's EXACT loop pin
# (G2's own reading of the forms: each loop's start and end) is red on every site whose stretch
# crosses the head.
SAB_ID="S3280-span-loop-head-late"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_loop_len reads the head as <=: loops start one past it, G2's window family's exact loop pin must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the head passes' span loop pin: lane formsfixb 2026-11-17. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3280."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (w->off[i] < w->head) return 0;'
SAB_AFTER='    if (w->off[i] <= w->head) return 0;   /* SABOTAGE S3280 */'
