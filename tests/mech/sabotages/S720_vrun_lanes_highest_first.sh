#!/usr/bin/env bash
# S720 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- lane order: the leftmost-candidate contract broken inside one block (multi-hit blocks). G2's SIMD family.
SAB_ID='S720-vrun-lanes-highest-first'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun block'\''s lanes are tried highest first, so a later candidate is returned before an earlier one'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S720. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                  "            size_t cand = i + (size_t)__builtin_ctz(m);\n"'
SAB_AFTER='                  "            size_t cand = i + (size_t)(31 - __builtin_clz(m));\n"   /* SABOTAGE S720 */'
