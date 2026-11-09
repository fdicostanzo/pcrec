#!/usr/bin/env bash
# S724 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09; RE-AIMED for the target seam, lane u3floor, 2026-11-08) -- a level's #include rendered under a conditional of the kit's own. Before U2 the plant closed the level guard around the include (C18 leg (a), off-target preprocessing); U2 retired the guard field and every CPU #if, so the plant was a CPU-free `#if 1` around the include; RE-ANCHORED by lane u2rev (review r5 X-1: the kit writes no #include, a level's header is an mf_includes fact), the plant is now an empty `#if 1`/`#endif` pair in the level block: the scaffolding lint (simdfloor) admits no preprocessor line in the kit's text but an admitted level's #include, and must read it red.
SAB_ID='S724-simd-include-unguarded'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='simdfloor'
SAB_DESC='a level block renders a conditional of the kit'\''s own (#if 1 / #endif), which the scaffolding lint must refuse'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S724. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    art->includes |= kit_level(r->decl->level)->includes;'
SAB_AFTER='    art->includes |= kit_level(r->decl->level)->includes; kit_out(o, "#if 1\n#endif\n");   /* SABOTAGE S724 */'
