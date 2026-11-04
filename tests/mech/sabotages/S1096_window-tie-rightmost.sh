#!/usr/bin/env bash
# S1096 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness
# span_pick unit 1b (lane sp1bfix) RE-ANCHORED: the window's tie is now T_WINDOW's TIE_LEFTMOST
# read through kit_tie_takes; the same plant (a tie goes to the rightmost window, `wm <= wl`)
# replaces the whole tie condition.
SAB_ID="S1096-window-tie-rightmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if (w == lo_s || wm < wl || (wm == wl && kit_tie_takes(T_WINDOW, w, at))) {'
SAB_AFTER='                if (w == lo_s || wm <= wl) {   /* SABOTAGE S1096 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane sp1bfix after the span_pick 1b re-anchor: the sabotaged tree under tests/codegen/run_cand_oracle.sh, candoracle:5fail/173pass DETECTED (the solo mech run is left to the gate shard)."
