#!/usr/bin/env bash
# S922 ([MEMFN] R17-b' B2, lane fdb2; r17b_prime.md §8.3 [rev3 D6], §1.6) --
# A FINDER ROW ROUTED BEFORE ITS STEP: R7 (the layer's LINER form, routed at
# B4) carries `routed` 1 at B2.
#
# WHAT IT BREAKS. Routing is one bit per row (§1.6); a site renders the
# table's pick iff its deciding rows are routed. R7 routed early makes every
# set site whose shape's saving key holds render R7's pick, V1, which has no
# arm before B4: the define is refused there, and wherever R7 holds the
# routed-record count rises past its population.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh): the table
# check A (R7 routed and locked at B2, where the design routes D1, D1c, D1w
# only) and the fixture fd-R7 (a set10 site under the R7 set, now refused).
SAB_ID="S922-fd-row-routed-early"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC="finder row R7 carries routed 1 at B2 (it routes at B4): set sites whose saving key holds are decided by an early-routed row"
SAB_DOC_FIGURE="MEASURED 2026-10-16 by lane fdb2fix, solo (run_sabotage_matrix.sh S922): DETECTED, memfnfinder 8fail/852pass (docs/dev/lanes/fdb2_report.md §10.3). The memfnfinder arm's counts changed with run_finder.sh's summed totals after this run; re-read from a run."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      FF_V1, FF_UNSTATED, { 0, 0, 0, 0 }, 0, NULL, FB_DERIVED, "B4",'
SAB_AFTER='      FF_V1, FF_UNSTATED, { 0, 0, 0, 0 }, 1, NULL, FB_DERIVED, "B4",   /* SABOTAGE S922 */'
