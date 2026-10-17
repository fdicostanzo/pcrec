#!/usr/bin/env bash
# S1084 (R-MS6; lane fdb2fix, [MEMFN] R17-b' B2) -- THE KIT WRITES THE ARM-ENTRY
# COUNTER UNASKED: mf_use writes the counter statement on every routed site
# whether or not the host called mf_reach (an unset stem renders as text), so
# the shipped compiler's artifacts move. Both builds link the kit, so they
# agree byte for byte: harness-vs-shipped identity cannot see this one.
# Detector (memfnfinder): run_arm_reach.sh's lever-off no-counter-shape check
# (`extern unsigned long`), the row the review found blind before it.
SAB_ID="S1084-reach-counter-kit-unasked"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC="mf_use writes the arm-entry counter on every routed site, the lever off included"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1084) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 11fail/881pass (docs/dev/lanes/fdb2land_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->reach_k >= 0)
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
SAB_AFTER='    if (r->reach_k >= 0 || r->fd_row)   /* SABOTAGE S1084 */
        kit_out(body, "%s{ extern unsigned long %s[]; %s[%d]++; }\n",'
