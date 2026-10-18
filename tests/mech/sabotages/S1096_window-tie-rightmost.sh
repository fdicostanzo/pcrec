#!/usr/bin/env bash
# S1096 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness
SAB_ID="S1096-window-tie-rightmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if (w == lo_s || wm < wl) { wl = wm; at = w; }'
SAB_AFTER='                if (w == lo_s || wm <= wl) { wl = wm; at = w; }   /* SABOTAGE S1096 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:1fail/139pass DETECTED at ebfb5a88a)."
