#!/usr/bin/env bash
# S817 ([MEMFN] R-16, lane r16b, 2026-10-11) -- the w32 helper's w16 rung keeps KB (KA alone only where w16 is standalone). G2's kb-dropped-rung population and the cli (?i)cat case.
SAB_ID='S817-vrun-kb-on-w16-rung'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='cli g2simd'
SAB_DESC='the w16 helper reads KB unless vrun-w32 is denied: the w16 rung under a w32 helper filters on two positions'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S817. docs/dev/lanes/r16b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (v->npos < 2) return -1;'
SAB_AFTER='    if (v->npos < 2 && kit_opt_denied(x->site->opts, "vrun-w32")) return -1;   /* SABOTAGE S817 */'
