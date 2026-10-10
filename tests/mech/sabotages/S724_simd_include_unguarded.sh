#!/usr/bin/env bash
# S724 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the #include outside the level guard ([r9 C-7]): off-target preprocessing now pulls in the header, so C18 leg (a) is red.
SAB_ID='S724-simd-include-unguarded'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='simdfloor'
SAB_DESC='a level'\''s intrinsics #include escapes its guard (the guard is closed around it)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S724. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kit_out(o, "#include <%s>\n", lv->header);'
SAB_AFTER='        kit_out(o, "#endif\n#include <%s>\n#if %s\n", lv->header, lv->guard);   /* SABOTAGE S724 */'
