#!/usr/bin/env bash
# S724 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09; RE-AIMED for the target seam, lane u3floor, 2026-11-08) -- a level's #include rendered under a conditional of the kit's own. Before U2 the plant closed the level guard around the include (C18 leg (a), off-target preprocessing); U2 retired the guard field and every CPU #if, so the plant is now a CPU-free `#if 1` around the include: the scaffolding lint (simdfloor) admits no preprocessor line in the kit's text but an admitted level's #include, and must read it red.
SAB_ID='S724-simd-include-unguarded'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='simdfloor'
SAB_DESC='a level'\''s intrinsics #include is rendered under a conditional of the kit'\''s own (#if 1), which the scaffolding lint must refuse'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S724. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kit_out(o, "#include <%s>\n", lv->header);'
SAB_AFTER='        kit_out(o, "#if 1\n#include <%s>\n#endif\n", lv->header);   /* SABOTAGE S724 */'
