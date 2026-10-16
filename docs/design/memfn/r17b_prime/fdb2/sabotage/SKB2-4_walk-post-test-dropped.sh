#!/usr/bin/env bash
# SKB2-4 (KW-3; placeholder id) -- THE KIT'S POST-TEST DROPPED: an unbounded
# walk whose empty range runs the miss (`empty` MISS) no longer writes
# `if (lo >= n) on_miss` after the walk, so the consumer falls into its loop
# at n instead of leaving (pcrec wrote that test itself before B2).
# Detector (memfnfinder): finder_check K's byte1vm signature (D1w's WALK with
# its post-test); emit_sweep sees it as movers on every byte-class and VM-hat
# artifact.
SAB_ID="SKB2-4-walk-post-test-dropped"
SAB_FILE="memfn/src/pffind.c"
SAB_SUITES="memfnfinder"
SAB_DESC="pf_walk no longer writes the post-test an empty-MISS site needs (KW-3)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->site.empty == MF_EMPTY_MISS)
        kit_out(o, "%sif (%s >= %s) %s\n", ind, h->lo, h->n, h->on_miss);
    return 0;'
SAB_AFTER='    if (0 && r->site.empty == MF_EMPTY_MISS)   /* SABOTAGE SKB2-4 */
        kit_out(o, "%sif (%s >= %s) %s\n", ind, h->lo, h->n, h->on_miss);
    return 0;'
