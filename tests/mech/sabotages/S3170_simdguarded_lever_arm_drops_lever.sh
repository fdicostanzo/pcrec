#!/usr/bin/env bash
# S3170 (lane mfind fix 1, 2026-11-14; [MEMFN] RQ-3) -- THE LEVER WITNESS NO
# LONGER SPELLS ITS LEVER.
#
# simd_guarded_check.py's LEVER_ARMS reach the rows only the test-only lever
# `mfind` renders (mfind-w16, mfind-w32). With the lever flag dropped from
# the arm, `foo.*bar` renders no mfind site, so the two declared rows are read
# by no artifact: the check's "rows no artifact read (a bound nothing
# reaches)" gate goes red, and so does the simd-form-lever floor.
SAB_ID='S3170-simdguarded-lever-arm-drops-lever'
SAB_FILE="tests/memfn/simd_guarded_check.py"
SAB_SUITES='simdguarded'
SAB_DESC="the lever witness arm no longer carries --harness=mfind, so the lever-only simd_bounds rows are read by no artifact"
SAB_DOC_FIGURE='DESIGNED by lane mfind fix 1 2026-11-14; LOUD expected (simd_bounds.tsv rows no artifact read: mfind-w16, mfind-w32). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3170.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="LEVER_ARMS = [('lever:mfind@' + t, ['--harness=mfind', '-fmemfn-simd=' + t])"
SAB_AFTER="LEVER_ARMS = [('lever:mfind@' + t, ['-fmemfn-simd=' + t])   # SABOTAGE S3170"
