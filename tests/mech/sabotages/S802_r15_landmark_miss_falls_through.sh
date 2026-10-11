#!/usr/bin/env bash
# S802 ([MEMFN] R-15, lane r15b) -- THE KEPT LANDMARK'S MISS FALLS THROUGH.
#
# WHAT IT BREAKS. On a miss precheck_assign_byte stores `n` (the site's
# `miss`, MISS_N) and then runs pcrec's `on_miss` on `result >= n`. The plant
# stores `lo` instead, so where lo < n a window without the byte keeps lo and
# falls through to the code after the site: the ASSIGN contract (a miss runs
# on_miss) is broken. On [REQ-HANDOFF-L1]'s customer that is slower, not
# wrong (no landmark, no match: the scan finds none), S617's class, so pcrec's
# corpus cannot see it, by construction.
#
# WHERE IT IS SEEN. The kit's checks only: C5's pin of pre-landmark-byte moves
# and check 14's no-landmark subjects must take the on_miss path (memfnarms);
# G2's gate family alone (g2gate) runs the landmark sites against G2's own
# reference, where a miss must run on_miss.
SAB_ID="S802-r15-landmark-miss-falls-through"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnarms g2gate"
SAB_DESC="the kit's precheck_assign_byte row stores lo instead of n on a miss, so a window without the byte keeps lo and falls through instead of running on_miss"
SAB_DOC_FIGURE="HAND-MEASURED by lane r15b: see docs/dev/lanes/r15b_report.md §5 (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && mkdir -p out && ./fx out && cat out/pre-landmark-byte.use'
SAB_REACH_EXPECT='size_t handoff_position = ({ const void *rx_mf1_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        art->prefix, handle, art->prefix, handle, h->s, h->n,'
SAB_AFTER='        art->prefix, handle, art->prefix, handle, h->s, h->lo,  /* SABOTAGE S802 */'
