#!/usr/bin/env bash
# S803 ([MEMFN] R-15, lane r15b) -- THE ROW'S DENY IS UNWIRED.
#
# WHAT IT BREAKS. `--memfn=no-precheck-assign-byte` (options.def, the kit's
# first scalar deny) is the row's OFF arm (D144 item 4, D147): denied, the
# generic row renders the site. The walk denies a row by its `opt` (the arm
# struct's options.def name, read by arm_table's accessor). The plant leaves
# the row's `opt` NULL, so the deny is accepted and does nothing: the OFF arm
# is gone.
#
# WHERE IT IS SEEN. No artifact moves on this tree (no pcrec site before L1;
# the cli's deny-is-inert cases stay green, as they must). C5's
# pre-landmark-byte-deny fixture (the site with the deny in its opts) renders
# through `precheck` instead of `generic` (check 1) and its pin moves
# (check 2). Arm memfnarms. (rows_check.py's check C, the row's control, sees
# it too, but no mech arm runs test-memfn-rows.)
SAB_ID="S803-r15-landmark-deny-unwired"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnarms"
SAB_DESC="the kit's precheck_assign_byte row carries no opt, so --memfn=no-precheck-assign-byte is accepted and denies nothing (the row's OFF arm is gone)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r15b: see docs/dev/lanes/r15b_report.md §5 (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && mkdir -p out && ./fx out && cat out/pre-landmark-byte.use'
SAB_REACH_EXPECT='size_t handoff_position = ({ const void *rx_mf1_q = subject_length > search_from ? memchr(subject + search_from, 46, subject_length - search_from) : NULL;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "precheck-assign-byte",'
SAB_AFTER='    NULL,       /* SABOTAGE S803: the deny unwired */'
