#!/usr/bin/env bash
# S3277 -- lane forms (R-45 plan A, r45_reply.md rev 6 §3 "the forms"): A LOOP SPANS TWO BYTE SETS.
# wf_loop_len (memfn/src/window.c) stops comparing the entries' byte sets, so a stretch of consecutive
# WIDE core positions with DIFFERENT sets becomes one loop testing every byte against the FIRST
# entry's set: a candidate the window rejects passes (or one it accepts fails). The detector is G2's
# WINDOW family (memfn/tests/run_g2_win.sh) at every finite grid head: its repeated-class family's
# MIXED stretches (a second WIDE class from h + 1 or h + 2, counted and floored per head: review r35
# F16, lane formsfixb), read by the generator (a loop over two sets is red at the text) and broken
# by the driver's class swaps at the boundary.
SAB_ID="S3277-span-loop-mixed-sets"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_loop_len ignores set equality: one loop tests mixed byte sets against the first, G2's window family's head passes must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the mixed stretches at every finite grid head (lane formsfixb 2026-11-17; first by hand, lane forms). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3277."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (j > i && (w->off[j] != w->off[j - 1] + 1 || w->table[j] != w->table[i] ||
                      memcmp(w->set[j], w->set[i], 32)))'
SAB_AFTER='        if (j > i && (w->off[j] != w->off[j - 1] + 1 || w->table[j] != w->table[i]))   /* SABOTAGE S3277 */'
