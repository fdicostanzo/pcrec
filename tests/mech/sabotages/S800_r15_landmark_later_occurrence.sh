#!/usr/bin/env bash
# S800 ([MEMFN] R-15, lane r15b) -- THE KEPT LANDMARK IS A LATER OCCURRENCE.
#
# WHAT IT BREAKS. The row precheck_assign_byte (memfn/src/precheck.c,
# `landmark`) keeps the LEFTMOST position of the pre-check's one byte in
# [lo, n) for the handoff (memfn.h ALL_PRESENT/ASSIGN: ret_pred's position is
# found by the FIND contract, the first). The plant searches from lo + 1, so a
# landmark AT lo is skipped and the next one, or a miss, is returned. On
# [REQ-HANDOFF-L1]'s customer a later landmark moves the handoff past matches
# that begin within K bytes before the skipped one (an earlier one would be
# equivalent there: rlhtwin §2.2), so it is NOT an equivalent mutant.
#
# WHERE IT IS SEEN. No pcrec site of the row's shape exists before L1, so no
# artifact moves. The kit's checks see it: C5's pin of the pre-landmark-byte
# fixture moves (check 2), and check 14 runs that fixture's text on every
# short subject over { '.', 'a' } from every lo against a loop written from
# the contract: every subject with '.' at lo answers wrong. Arm memfnarms
# (tests/memfn/run_arm_pins.sh).
SAB_ID="S800-r15-landmark-later-occurrence"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnarms"
SAB_DESC="the kit's precheck_assign_byte row searches its kept landmark from lo + 1, so a landmark at lo is skipped and a later occurrence (or a miss) is kept for the handoff"
SAB_DOC_FIGURE="HAND-MEASURED by lane r15b: see docs/dev/lanes/r15b_report.md §5 (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && mkdir -p out && ./fx out && cat out/pre-landmark-byte.use'
SAB_REACH_EXPECT='size_t handoff_position = ({ const void *rx_mf1_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='%s > %s ? memchr(%s + %s, %d, %s - %s) : NULL;'
SAB_AFTER='%s > %s ? memchr(%s + %s + 1, %d, %s - %s - 1) : NULL;  /* SABOTAGE S800 */'
