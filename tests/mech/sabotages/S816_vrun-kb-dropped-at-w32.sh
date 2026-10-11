#!/usr/bin/env bash
# S816 ([MEMFN] R-16, lane r16b, 2026-10-11) -- KB dropped at w32 too. G2's SIMD family (the per-level filter rule) and the cli (?i)cat case.
SAB_ID='S816-vrun-kb-dropped-at-w32'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='cli g2simd'
SAB_DESC='the w32 level reads one filter position: KB is read at no level'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S816. docs/dev/lanes/r16b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                     "_mm256_cmpeq_epi8", "_mm256_movemask_epi8", 2 },'
SAB_AFTER='                     "_mm256_cmpeq_epi8", "_mm256_movemask_epi8", 1 },   /* SABOTAGE S816 */'
