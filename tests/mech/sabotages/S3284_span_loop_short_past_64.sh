#!/usr/bin/env bash
# S3284 -- lane formsfixb (review r35 F12): A LOOP FROM OFFSET 64 ON STOPS ONE SHORT. wf_loop
# (memfn/src/window.c) ends a loop that starts at offset 64 or later one position early, so its last
# entry is never tested: the defect lives ONLY in the regime where the shipped default H(64) loops,
# which no G2 check reached before review r35 F12 raised G2's reach (G2W_REACH 256, stretches to
# 64 + 4, long rows of 500 and 1024). The detector is G2's WINDOW family (memfn/tests/run_g2_win.sh):
# the default pass's and head 64's answers (the long rows' and the deterministic breaks') and the
# exact loop pin at heads 32 and 64.
SAB_ID="S3284-span-loop-short-past-64"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_loop's end one short from offset 64 on: the shipped default's own loops skip their last entry, G2's window family must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win), the default pass and head 64: lane formsfixb 2026-11-17. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3284."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int32_t lo = rc->w->off[i], end = lo + (int32_t)len;'
SAB_AFTER='    int32_t lo = rc->w->off[i], end = lo + (int32_t)len - (lo >= 64);   /* SABOTAGE S3284 */'
