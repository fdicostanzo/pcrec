#!/usr/bin/env bash
# S729 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the ladder as a walk-on ([r9 C-2]): a denied rung still renders. The cli case for each deny removing exactly its level; G2's deny-w16 class.
SAB_ID='S729-vrun-rung-not-reasked'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='cli g2simd'
SAB_DESC='a PREFIX row'\''s named rung is rendered without being re-asked, so --memfn=no-vrun-w16 leaves the w16 helper under w32'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S729. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (i < NFN && kit_ask(&fn_table, i, &in, MF_PH_DEFINE, art->denies, x, &tc))'
SAB_AFTER='        if (i < NFN && (kit_ask(&fn_table, i, &in, MF_PH_DEFINE, art->denies, x, &tc), 1))   /* SABOTAGE S729 */'
