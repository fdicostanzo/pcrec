#!/usr/bin/env bash
# S1080 (R-MS6; lane fdb2, [MEMFN] R17-b' B2) -- THE ARM-ENTRY COUNTER ARMED WITHOUT
# THE LEVER: pcrec asks the kit for the counter (mf_reach) on every harness
# compile, whether or not the arm-reach option was given, so the harness
# build's lever-off artifact carries counters the shipped compiler's does not.
# The realistic fault: the host-side gate on the option dropped.
# Detector (memfnfinder): run_arm_reach.sh's lever-off identity (harness vs
# shipped) and its no-counter-shape check.
SAB_ID="S1080-reach-counter-lever-off"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="memfnfinder"
SAB_DESC="pcrec arms the arm-entry counter on every harness compile, the lever off included"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1080) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 6fail/886pass (docs/dev/lanes/fdb2land_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (cx->emit_in && cx->emit_in->harness && cx->emit_in->harness->arm_reach &&'
SAB_AFTER='        if (cx->emit_in && cx->emit_in->harness &&   /* SABOTAGE S1080 */'
