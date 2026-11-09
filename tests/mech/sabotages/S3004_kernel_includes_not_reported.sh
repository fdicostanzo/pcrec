#!/usr/bin/env bash
# S3004 -- review 2026-11-08 r5 X-1 (lane u2rev), THE FIND-ANY KERNEL REPORTS ITS HEADERS.
#
# Plant: memfn/src/vany.c's `*includes` stays 0 at every target, so a caller writes no vector
# header ahead of the region.
# Detector (matrix column memfntargets): tests/memfn/targets_check.c's admission rows (includes equal to
# the admitted levels' bits) at both SIMD targets.
SAB_ID="S3004-kernel-includes-not-reported"
SAB_FILE="memfn/src/vany.c"
SAB_SUITES="memfntargets"
SAB_DESC='the find-any kernel stops reporting the admitted levels headers in includes'
SAB_DOC_FIGURE='MEASURED by lane u2rev by hand (u2rev_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3004.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (levels & 1u << lv) *includes |= kit_level(lv)->includes;'
SAB_AFTER='        if (0 && (levels & 1u << lv)) *includes |= kit_level(lv)->includes;   /* SABOTAGE S3004 */'
