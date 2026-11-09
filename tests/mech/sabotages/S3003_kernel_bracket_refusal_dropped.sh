#!/usr/bin/env bash
# S3003 -- review 2026-11-08 r5 SEAM-5 kernel half (lane u2rev), THE FIND-ANY KERNEL REFUSES A
# SINK WITHOUT BRACKETS where its target admits a level (never a silent decline, never a call
# through a NULL bracket).
#
# Plant: memfn/src/vany.c's bracket refusal never fires.
# Detector (matrix column memfntargets): tests/memfn/targets_check.c's bracket row (the base SIMD target, a sink without
# simd_open/simd_close: -1, a text, nothing written); under the plant the kernel calls the NULL
# bracket and the checker dies short of its row floor.
SAB_ID="S3003-kernel-bracket-refusal-dropped"
SAB_FILE="memfn/src/vany.c"
SAB_SUITES="memfntargets"
SAB_DESC='the find-any kernel stops refusing a sink without simd_open/simd_close at a level'
SAB_DOC_FIGURE='MEASURED by lane u2rev by hand (u2rev_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3003.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (levels && (!o->simd_open || !o->simd_close))'
SAB_AFTER='    if (0 && levels && (!o->simd_open || !o->simd_close))   /* SABOTAGE S3003 */'
