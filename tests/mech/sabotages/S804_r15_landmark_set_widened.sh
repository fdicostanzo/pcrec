#!/usr/bin/env bash
# S804 ([MEMFN] R-15, lane r15b) -- A MULTI-MEMBER SET IS TAKEN AS ONE BYTE.
#
# WHAT IT BREAKS. The pre-check's renderer writes a byte part as one
# `memchr` of its byte, right only for a ONE-member set (`single_byte`); the
# row precheck_assign_byte keeps that byte's position. The plant widens the
# test to any non-empty set, so a two-member ret_pred renders `memchr` of its
# LOWEST member: a site whose landmark is the other member misses it.
#
# WHERE IT IS SEEN. pcrec never states a multi-member pre-check byte (the gate
# is req_byte, one member, by construction), so pcrec's corpus is blind to it.
# The kit's checks: C5's pre-landmark-two-members fixture renders through
# `precheck` instead of `generic` (check 1, memfnarms), and G2's gate family
# alone (g2gate) runs the landmark space's 2/3/255/256-member near-misses
# against G2's own reference.
SAB_ID="S804-r15-landmark-set-widened"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnarms g2gate"
SAB_DESC="the pre-check's single_byte test admits any non-empty set, so a multi-member ret_pred (or gate byte) renders memchr of its lowest member"
SAB_DOC_FIGURE="HAND-MEASURED by lane r15b: see docs/dev/lanes/r15b_report.md §5 (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && mkdir -p out && ./fx out && cat out/pre-landmark-byte.use'
SAB_REACH_EXPECT='size_t handoff_position = ({ const void *rx_mf1_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return n == 1;'
SAB_AFTER='    return n >= 1;  /* SABOTAGE S804 */'
