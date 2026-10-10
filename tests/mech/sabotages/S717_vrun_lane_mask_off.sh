#!/usr/bin/env bash
# S717 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the lane mask off by one: the first not-yet-tested candidate of the overlapped final block is masked away. G2's SIMD family.
SAB_ID='S717-vrun-lane-mask-off'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun final block'\''s lane mask drops one more lane than the loops covered'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S717. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o->puts(o->u, " & (~0u << (i - f));\n"'
SAB_AFTER='    o->puts(o->u, " & (~0u << (i - f + 1));\n"   /* SABOTAGE S717 */'
