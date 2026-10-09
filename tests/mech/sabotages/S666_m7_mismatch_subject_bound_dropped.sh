#!/usr/bin/env bash
# S666 ([MEMFN] M7, lane m7) -- THE KIT'S SUBJECT-END TEST IS DROPPED.
#
# WHAT IT BREAKS. The encoding seam's span compare (N7) is the kit's MISMATCH
# loop since M7 (memfn/src/mismatch.c, mm_render). Its exact and
# expression-fold shapes test `at + i >= n ||` before reading `s[at + i]`;
# the plant drops that test, so the loop reads the subject PAST its read
# limit and compares whatever lies there against the reference: a contract
# breach (MF_OP_MISMATCH reads `s` only in [lo, n)) whose answer effect
# depends on the bytes after the subject.
#
# WHERE IT IS SEEN. The kit's own arm: the `mm-exact`/`mm-ucp-expr`/
# `mm-nonident` pins move, and run_arm_pins.sh check 11 runs the loops on
# subjects whose buffer holds stale bytes past n against the contract's byte
# loop. pcrec's answer suites see it only where the bytes past a subject
# happen to equal the reference (a C string's NUL rarely does): hand-measure
# it rather than rely on it. Arm memfnarms.
SAB_ID="S666-m7-mismatch-subject-bound-dropped"
SAB_FILE="memfn/src/mismatch.c"
SAB_SUITES="memfnarms"
SAB_DESC="the kit's MISMATCH loop (exact and expression-fold shapes) drops its subject-end test, so the span compare reads past n"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m7_report.md section 6): memfnarms 6 failed / 280 passed (three generic mm-* pins and two n7_target freezes move; check 11 fails to BUILD, the planted text leaving n unused under -Werror). The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(a+)\1"'
SAB_REACH_EXPECT='    for (i = 0; i < reflen; i++) {
        if (at + i >= n || s[at + i] != ref[i])'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kb_printf(b, "%s    if (%s + %s >= %s || %s != %s)\n", ind, LO, R, N, x, y);'
SAB_AFTER='        kb_printf(b, "%s    if (%s != %s)\n", ind, x, y);  /* SABOTAGE S666 */'
