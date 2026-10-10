#!/usr/bin/env bash
# S716 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the final block's guard off by one (R-1's PLANT 1): a hit at n - T - 1 that only the overlapped final block covers is missed. Seen by G2's SIMD family (answers, every level live).
SAB_ID='S716-vrun-final-guard-short'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun helpers'\'' overlapped final block is skipped when exactly one candidate is left (its guard one short)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S716. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                  "            if (i + %u >= n) return n;\n"'
SAB_AFTER='                  "            if (i + %u + 1 >= n) return n;\n"   /* SABOTAGE S716 */'
