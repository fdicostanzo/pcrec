#!/usr/bin/env bash
# S728 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- C11's FORMS movers half (an ON artifact differs from the default while FORMS reads none), and RQ-3's bound (guarded bytes > 0 under a none stamp).
SAB_ID='S728-memfn-forms-left-none'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='memfnstamps simdguarded'
SAB_DESC='a FUNC that carries a SIMD row records no MEMFN_FORMS token, so the stamp reads none on a mover'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S728. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (nr) fn_note_form(art, rung, nr);'
SAB_AFTER='    if (0) fn_note_form(art, rung, nr);   /* SABOTAGE S728 */'
