#!/usr/bin/env bash
# S727 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the one deny carrier ignored ([r9 F-2]): the cli cases for --memfn=no-vrun-w16/-w32 and G2's deny classes.
SAB_ID='S727-memfn-deny-ignored'
SAB_FILE='memfn/src/options.c'
SAB_SUITES='cli g2simd'
SAB_DESC='the walk never finds a --memfn=no-<row> deny, so a SIMD row'\''s own deny does nothing'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S727. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return 1;'
SAB_AFTER='            return 0;   /* SABOTAGE S727 */'
