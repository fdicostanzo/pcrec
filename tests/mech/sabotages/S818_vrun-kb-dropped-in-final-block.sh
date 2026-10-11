#!/usr/bin/env bash
# S818 ([MEMFN] R-16, lane r16b, 2026-10-11) -- the final block's mask drops KB (the whole block keeps it). G2's SIMD family (the final-block mask's loads, and its answers: the verify still trims KB).
SAB_ID='S818-vrun-kb-dropped-in-final-block'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the overlapped final block filters on KA alone while the verify still treats KB as proven'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S818. docs/dev/lanes/r16b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kit_out(o, "(unsigned)%s(", v->mmask);'
SAB_AFTER='    if (!strcmp(base, "f")) k2 = -1; kit_out(o, "(unsigned)%s(", v->mmask);   /* SABOTAGE S818 */'
