#!/usr/bin/env bash
# SK-B3A-4 (PLACEHOLDER id; lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness
SAB_ID="SK-B3A-4-window-tie-rightmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if (w == lo_s || wm < wl) { wl = wm; at = w; }'
SAB_AFTER='                if (w == lo_s || wm <= wl) { wl = wm; at = w; }   /* SABOTAGE SK-B3A-4 */'
