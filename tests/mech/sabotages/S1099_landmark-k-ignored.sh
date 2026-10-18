#!/usr/bin/env bash
# S1099 (lane b3a, [MEMFN] R17-b' B3a) -- the fifth port ignores K where K x h reaches the whole rate; caught by the .{0,100}e declined witness
SAB_ID="S1099-landmark-k-ignored"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="the fifth port ignores K where K x h reaches the whole rate; caught by the .{0,100}e declined witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        else if (k * h >= 1000000u) out->landmark = 0;'
SAB_AFTER='        else if (0) out->landmark = 0;   /* SABOTAGE S1099 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane b3afix: see docs/dev/lanes/b3a_report.md §9 (the solo mech run of this row, candoracle:1fail/139pass DETECTED at ebfb5a88a)."
