#!/usr/bin/env bash
# S725 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm admitted where the narrowest is: it meets the base target. Re-aimed at unit U2 (lane u2): levels carry `needs`, not a guard; the widest level needs the narrowest's feature, so the base target admits it (the table check cannot see it: the base target does supply that feature) and its helpers sit in the base region. Detectors: G2's base-target file holds w32 helpers (g2simd) and the find-any kernel at the base target renders w32 (memfntargets' admission literals).
SAB_ID='S725-w32-under-w16-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='g2simd memfntargets'
SAB_DESC='the widest level needs only the narrowest feature, so the base target admits it and meets its intrinsics'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S725. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"avx2", "imm'
SAB_AFTER='"sse2", /* SABOTAGE S725 */ "imm'
