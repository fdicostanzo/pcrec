#!/usr/bin/env bash
# S1079 (SN-1's shape; lane fdb2, [MEMFN] R17-b' B2) -- D1's ROUTED BIT
# LEFT 0 after B2: one-byte sites render their pre-table form, which is the
# same text (zero movers), so byte identity cannot see it (§1.6 [rev3 B5]).
# Detectors (memfnfinder): A (D1 routed 1 at B2) and K (byte1t decided by D1;
# the routed record), and the routed census's D1 floors.
SAB_ID="S1079-fd-d1-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="finder row D1 keeps routed 0 after its routing step: its sites render their pre-table form under no routed decision"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1079) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 7fail/894pass (docs/dev/lanes/fdb2land_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      FF_LIBC, FF_UNSTATED, { 0, 0, 0, 0 }, 1, "fd-d1", FB_UNMEASURED_DEFAULT, "B2",'
SAB_AFTER='      FF_LIBC, FF_UNSTATED, { 0, 0, 0, 0 }, 0, "fd-d1", FB_UNMEASURED_DEFAULT, "B2",   /* SABOTAGE S1079 */'
