#!/usr/bin/env bash
# S3277 -- lane forms (R-45 plan A, r45_reply.md rev 6 §3 "the forms"): A LOOP SPANS TWO BYTE SETS.
# wf_loop_len (memfn/src/window.c) stops comparing the entries' byte sets, so a stretch of consecutive
# WIDE core positions with DIFFERENT sets becomes one loop testing every byte against the FIRST
# entry's set: a candidate the window rejects passes (or one it accepts fails). The detector is G2's
# WINDOW family's head passes (memfn/tests/run_g2_win.sh, the lever span-head=N at 0, 8, 24), whose
# mass/report/random families state mixed-set stretches.
SAB_ID="S3277-span-loop-mixed-sets"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_loop_len ignores set equality: one loop tests mixed byte sets against the first, G2's window family's head passes must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), its head passes: lane forms 2026-11-17, by hand. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3277."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (j > i && (w->off[j] != w->off[j - 1] + 1 || w->table[j] != w->table[i] ||
                      memcmp(w->set[j], w->set[i], 32)))'
SAB_AFTER='        if (j > i && (w->off[j] != w->off[j - 1] + 1 || w->table[j] != w->table[i]))   /* SABOTAGE S3277 */'
