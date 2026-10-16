#!/usr/bin/env bash
# S1081 (R-MS6; lane fdb2, [MEMFN] R17-b' B2) -- THE COUNTER NEVER COUNTS: its statement is
# written but adds nothing, so every arm reads 0 on a subject that enters it.
# Detector (memfnfinder): run_arm_reach.sh's ">= 1 on a fixture that enters".
SAB_ID="S1081-reach-counter-never-counts"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the arm-entry counter's statement adds 0: an entered arm reads 0"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb2: see docs/dev/lanes/fdb2_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
SAB_AFTER='        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d] += 0; }\n",   /* SABOTAGE S1081 */'
