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
# FIGURE RE-MEASURED at span_pick 1e's review fix (lane sp1efix): see SAB_DOC_FIGURE.
# RE-ANCHORED at the r1 s30a review fixes (lane s30arev): fd_find's returns are named (FD_NO_ROW); intent
# unchanged.
SAB_ID="S1079-fd-d1-unrouted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="finder row D1 is held back from deciding for the composer (fd_find declines its decision when no stop is stated): its sites render their pre-table form under no decided row"
SAB_DOC_FIGURE="MEASURED 2026-11-05 BY HAND at lane/memfn-sp1efix 695a83447 (the plant applied to a git archive of that commit, built with make, tests/memfn/run_finder.sh with LIB its build/libpcrec.a): DETECTED, memfnfinder 6fail/3155pass (byte1t and hat1 decided by no row, '2 of 4 routed sites', the two lever-on artifacts holding no counter increment, the lever case floor). The sp1e review's own runs read 3fail/3160pass for the same plant at 9de5b5638, so the by-hand figure is not the matrix's: the figure of record is the mech run's (gate job 437 of lane sp1efix). Earlier figures: fdb2land 7fail/894pass at B2; sp1e 6fail/3155pass at 7d5d6711c. Re-measured 2026-11-09 BY HAND after the s30arev re-aim, planted by hand on a git archive of lane/memfn-s30a c8d54df7c (lane s30arev, review r1 s30a fixes), built with nice make -j2; 15 patterns x 4 arms compiled by the planted and the clean pcrec and classed: SAME 60; memfnfinder 6fail/3308pass."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (d.terminal >= FD_NROWS) return FD_NO_ROW;'
SAB_AFTER='    if (d.terminal >= FD_NROWS || (!st && !strcmp(fd_rows[d.terminal].id, "D1"))) return FD_NO_ROW;   /* SABOTAGE S1079 */'
