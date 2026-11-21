#!/usr/bin/env bash
# S3280 -- lane formsfixb (review r35 F14, R-45 r45_reply.md rev 6 §3 "The forms"): A LOOP STARTS ONE
# OFFSET PAST THE HEAD. the H form's renderer (memfn/src/window.c, wf_span_h; wf_loop_len before U2) compares the entry's offset with `<=` instead of
# `<`, so the entry AT the head is a lone test and every loop starts at h + 1: the answers are unchanged
# and the identity check (both sides carry the same wf_loop_len) cannot see it, so the cards would time
# a head under the next one's name. The detector is G2's WINDOW family's head passes (memfn/tests/
# run_g2_win.sh, the lever span-head=N at every finite grid head): the generator's EXACT loop pin
# (G2's own reading of the forms: each loop's start and end) is red on every site whose stretch
# crosses the head.
# Re-aimed by lane bsu1 (R-47 U1, block_span.md §10.2): w->head retired; wf_loop_len takes the head as a parameter.
# Re-aimed by lane bsu2 (R-47 U2, review r72 SLOT-1): the use renders from the stored k, so the head is read in
# wf_span_h (the H rows' render column) alone and wf_loop_len no longer takes it; same intent (loops start at h + 1).
SAB_ID="S3280-span-loop-head-late"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_span_h reads the head as <= (wf_loop_len before U2): loops start one past it, G2's window family's exact loop pin must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the head passes' span loop pin: lane formsfixb 2026-11-17. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3280."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    while (a < end && w->off[a] < st->h) a++;'
SAB_AFTER='    while (a < end && w->off[a] <= st->h) a++;   /* SABOTAGE S3280 */'
