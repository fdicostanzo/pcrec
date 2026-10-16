#!/usr/bin/env bash
# S1080 (R-MS6; lane fdb2, [MEMFN] R17-b' B2) -- THE ARM-ENTRY COUNTER WRITTEN WITH THE
# LEVER OFF: every routed site's use writes its counter statement whether or
# not the host asked for it, so shipped artifacts move.
# Detector (memfnfinder): run_arm_reach.sh's lever-off identity and
# "no counter named" checks.
SAB_ID="S1080-reach-counter-lever-off"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="mf_use writes the arm-entry counter on every routed site, the lever off included"
SAB_DOC_FIGURE="HAND-MEASURED by lane fdb2: see docs/dev/lanes/fdb2_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->reach_k >= 0)
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
SAB_AFTER='    if (r->reach_k >= 0 || r->fd_row)   /* SABOTAGE S1080 */
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
