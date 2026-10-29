#!/usr/bin/env bash
# S1079 (SN-1's shape; lane fdb2, [MEMFN] R17-b' B2) -- D1's ROUTED BIT
# LEFT 0 after B2: one-byte sites render their pre-table form, which is the
# same text (zero movers), so byte identity cannot see it (§1.6 [rev3 B5]).
# Detectors (memfnfinder): A (D1 routed 1 at B2) and K (byte1t decided by D1;
# the routed record), and the routed census's D1 floors.
# RE-ANCHORED at B4' (lane b4p, LOCKDOWN): the `routed` bit is deleted, so the
# plant is now `fd_row_decides` HOLDING D1 back (intent unchanged: D1 does not
# decide, its sites render the pre-table form); detector K.
# RE-ANCHORED at D172 S3 (lane s3): fd_row_decides, which held back only the
# R-26.6 preview's row, retired with RPT and the preview; the plant is now
# fd_route itself declining a D1 decision (intent unchanged).
SAB_ID="S1079-fd-d1-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="finder row D1 is held back from deciding (fd_route declines its decision): its sites render their pre-table form under no decided row"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1079) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 7fail/894pass (docs/dev/lanes/fdb2land_report.md). RE-ANCHORED at B4' (lane b4p): read the current figure from a run."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (d.terminal >= FD_NROWS) return NULL;'
SAB_AFTER='    if (d.terminal >= FD_NROWS || !strcmp(fd_rows[d.terminal].id, "D1")) return NULL;   /* SABOTAGE S1079 */'
