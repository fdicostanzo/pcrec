#!/usr/bin/env bash
# SKB2-3 (R-MS6; placeholder id) -- THE COUNTER NEVER COUNTS: its statement is
# written but adds nothing, so every arm reads 0 on a subject that enters it.
# Detector (memfnfinder): run_arm_reach.sh's ">= 1 on a fixture that enters".
SAB_ID="SKB2-3-reach-counter-never-counts"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the arm-entry counter's statement adds 0: an entered arm reads 0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
SAB_AFTER='        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d] += 0; }\n",   /* SABOTAGE SKB2-3 */'
