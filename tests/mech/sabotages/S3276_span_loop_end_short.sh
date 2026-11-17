#!/usr/bin/env bash
# S3276 -- lane forms (R-45 plan A, docs/design/memfn/r45_reply.md rev 6 §3): THE SPAN LOOP STOPS ONE
# POSITION SHORT. wf_loop (memfn/src/window.c) ends its loop at the stretch's last offset instead of one
# past it, so the last position of every looped stretch is never tested: a candidate whose last
# position is a non-member passes. Default-width artifacts never loop (head 64), so the detector is
# G2's WINDOW family (memfn/tests/run_g2_win.sh): at every finite grid head (the lever span-head=N)
# the generator's EXACT loop pin (each loop's end) and the driver's DETERMINISTIC BREAKS at each
# stated stretch's last entries (review r35 F17, lane formsfixb: no longer a random break's luck),
# and the long rows' breaks in the default pass.
SAB_ID="S3276-span-loop-end-short"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="wf_loop's end one short: a looped stretch's last position is never tested, G2's window family's head passes must red"
SAB_DOC_FIGURE="G2's WINDOW family (memfn/tests/run_g2_win.sh, arm g2win): the exact loop pin and the deterministic breaks at every finite grid head (lane formsfixb 2026-11-17; first by hand, lane forms). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3276."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int32_t lo = rc->w->off[i], end = lo + (int32_t)len;'
SAB_AFTER='    int32_t lo = rc->w->off[i], end = lo + (int32_t)len - 1;   /* SABOTAGE S3276 */'
