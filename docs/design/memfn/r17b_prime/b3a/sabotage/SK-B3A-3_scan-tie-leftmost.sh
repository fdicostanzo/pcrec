#!/usr/bin/env bash
# SK-B3A-3 (PLACEHOLDER id; lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness
SAB_ID="SK-B3A-3-scan-tie-leftmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the run-scan port drops its tie rule (a tie goes to the leftmost position); caught by the -e utf8 abcd tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (scan < 0 || c < sm) { scan = (int)i; sm = c; }'
SAB_AFTER='            if (scan < 0 || c <= sm) { scan = (int)i; sm = c; }   /* SABOTAGE SK-B3A-3 */'
