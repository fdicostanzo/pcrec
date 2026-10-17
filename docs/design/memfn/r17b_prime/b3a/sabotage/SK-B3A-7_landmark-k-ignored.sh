#!/usr/bin/env bash
# SK-B3A-7 (PLACEHOLDER id; lane b3a, [MEMFN] R17-b' B3a) -- the fifth port ignores K where K x h reaches the whole rate; caught by the .{0,100}e declined witness
SAB_ID="SK-B3A-7-landmark-k-ignored"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="the fifth port ignores K where K x h reaches the whole rate; caught by the .{0,100}e declined witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        else if (k * h >= 1000000u) out->landmark = 0;'
SAB_AFTER='        else if (0) out->landmark = 0;   /* SABOTAGE SK-B3A-7 */'
