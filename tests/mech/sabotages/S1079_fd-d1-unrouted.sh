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
# RE-ANCHORED at span_pick 1e (lane sp1e): fd_route merged into fd_find, the
# one T-FIND walk; the plant declines a D1 decision for the composer's ask
# (`st` NULL) alone, so the window family's stops are untouched (intent
# unchanged).
SAB_ID="S1079-fd-d1-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="finder row D1 is held back from deciding for the composer (fd_find declines its decision when no stop is stated): its sites render their pre-table form under no decided row"
SAB_DOC_FIGURE="MEASURED 2026-10-17 by lane fdb2land, solo (run_sabotage_matrix.sh S1079) at B2 merged onto the new kit base, after run_finder.sh's summed-count fix: DETECTED, memfnfinder 7fail/894pass (docs/dev/lanes/fdb2land_report.md). RE-ANCHORED at B4' (lane b4p): read the current figure from a run. RE-ANCHORED at span_pick 1e (lane sp1e) into fd_find: MEASURED 2026-11-05 BY HAND (the plant applied to a git archive of lane/memfn-sp1e 7d5d6711c, built, tests/memfn/run_finder.sh against its build/libpcrec.a): DETECTED, memfnfinder 6fail/3155pass (byte1t and hat1 decided by no row; the routed census and the lever cases under their floors); the mech run's own figure is gate job 427's (docs/dev/lanes/sp1e_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (d.terminal >= FD_NROWS) return 0;'
SAB_AFTER='    if (d.terminal >= FD_NROWS || (!st && !strcmp(fd_rows[d.terminal].id, "D1"))) return 0;   /* SABOTAGE S1079 */'
