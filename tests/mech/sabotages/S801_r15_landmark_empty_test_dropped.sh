#!/usr/bin/env bash
# S801 ([MEMFN] R-15, lane r15b) -- THE KEPT LANDMARK'S EMPTY TEST IS DROPPED.
#
# WHAT IT BREAKS. precheck_assign_byte's `memchr` sits behind `n > lo`, as the
# gate's does: an empty window cannot hold the byte, and `memchr` (declared
# nonnull) is never handed the NULL subject with length 0 that the match API
# allows (match_api §3.1). The plant makes the test always true, so the empty
# window calls `memchr(NULL + 0, b, 0)`: answer-invisible on a non-NULL
# subject, undefined behaviour on the legal NULL one.
#
# WHERE IT IS SEEN. No artifact moves (no pcrec site before L1). C5's pin of
# pre-landmark-byte moves (check 2), and check 14 runs the fixture's text on a
# NULL subject at n = 0 under -fsanitize=undefined, whose nonnull-attribute
# check faults the call. Arm memfnarms.
SAB_ID="S801-r15-landmark-empty-test-dropped"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnarms"
SAB_DESC="the kit's precheck_assign_byte row drops its empty test (n > lo), so an empty window hands memchr the legal NULL subject at length 0 (undefined behaviour)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r15b: see docs/dev/lanes/r15b_report.md §5 (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && mkdir -p out && ./fx out && cat out/pre-landmark-byte.use'
SAB_REACH_EXPECT='size_t handoff_position = ({ const void *rx_mf1_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='= %s > %s ? memchr('
SAB_AFTER='= (%s > %s || 1) ? memchr(  /* SABOTAGE S801 */'
