#!/usr/bin/env bash
# SKB2-2 (R-MS6; placeholder id) -- THE ARM-ENTRY COUNTER WRITTEN WITH THE
# LEVER OFF: every routed site's use writes its counter statement whether or
# not the host asked for it, so shipped artifacts move.
# Detector (memfnfinder): run_arm_reach.sh's lever-off identity and
# "no counter named" checks.
SAB_ID="SKB2-2-reach-counter-lever-off"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="mf_use writes the arm-entry counter on every routed site, the lever off included"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->reach_k >= 0)
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
SAB_AFTER='    if (r->reach_k >= 0 || r->fd_row)   /* SABOTAGE SKB2-2 */
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
