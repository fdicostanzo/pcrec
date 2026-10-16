#!/usr/bin/env bash
# S1082 (KW-3; lane fdb2, [MEMFN] R17-b' B2) -- THE KIT'S POST-TEST DROPPED: an unbounded
# walk whose empty range runs the miss (`empty` MISS) no longer writes
# `if (lo >= n) on_miss` after the walk, so the consumer falls into its loop
# at n instead of leaving (pcrec wrote that test itself before B2).
# Detector (memfnfinder): finder_check K's byte1vm signature (D1w's WALK with
# its post-test); emit_sweep sees it as movers on every byte-class and VM-hat
# artifact.
SAB_ID="S1082-walk-post-test-dropped"
SAB_FILE="memfn/src/pffind.c"
SAB_SUITES="memfnfinder"
SAB_DESC="pf_walk no longer writes the post-test an empty-MISS site needs (KW-3)"
SAB_DOC_FIGURE="MEASURED 2026-10-16 by lane fdb2fix, solo (run_sabotage_matrix.sh S1082): DETECTED, memfnfinder 2fail/883pass (docs/dev/lanes/fdb2_report.md §10.3). The memfnfinder arm's counts changed with run_finder.sh's summed totals after this run; re-read from a run."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->site.empty == MF_EMPTY_MISS)
        kit_out(o, "%sif (%s >= %s) %s\n", ind, h->lo, h->n, h->on_miss);
    return 0;'
SAB_AFTER='    if (0 && r->site.empty == MF_EMPTY_MISS)   /* SABOTAGE S1082 */
        kit_out(o, "%sif (%s >= %s) %s\n", ind, h->lo, h->n, h->on_miss);
    return 0;'
