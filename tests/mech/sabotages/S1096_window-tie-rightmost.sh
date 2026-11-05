#!/usr/bin/env bash
# S1096 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness
# span_pick unit 1b (lane sp1bfix) RE-ANCHORED: the window's tie is now T_WINDOW's TIE_LEFTMOST
# read through kit_tie_takes; the same plant (a tie goes to the rightmost window, `wm <= wl`)
# replaces the whole tie condition.
# span_pick unit 1d (lane sp1d) RE-ANCHORED: the run window asks the one before-relation
# kit_pick_takes; the same plant (`<=`: a tie goes to the rightmost window) replaces that call.
SAB_ID="S1096-window-tie-rightmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if (kit_pick_takes(&bw, wm, T_WINDOW, w)) bw = (kit_pick){ w, w, wm };'
SAB_AFTER='                if (bw.pos < 0 || wm <= bw.v) bw = (kit_pick){ w, w, wm };   /* SABOTAGE S1096 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane sp1bfix after the span_pick 1b re-anchor: the sabotaged tree under tests/codegen/run_cand_oracle.sh, candoracle:5fail/173pass DETECTED (the solo mech run is left to the gate shard)."
