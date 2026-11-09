#!/usr/bin/env bash
# S725 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm admitted where the narrowest is: it meets the base target. Re-aimed at unit U2 (lane u2): levels carry `needs`, not a guard; the widest level needs the narrowest's feature, so the base target admits it (the table check cannot see it: the base target does supply that feature) and its helpers sit in the base region. Detectors: G2's base-target file holds w32 helpers (g2simd) and the find-any kernel at the base target renders w32 (memfntargets' admission literals).
SAB_ID='S725-w32-under-w16-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='g2simd memfntargets'
SAB_DESC='the widest level needs only the narrowest feature, so the base target admits it and meets its intrinsics'
SAB_DOC_FIGURE='MEASURED by lane simdskip by hand on a scratch copy of the joint tree (g2simd:2fail/1611pass, memfntargets:2fail/0pass, 17 and 29 compiles skipped because the facts of their targets failed, no compiler error in either log; simdskip_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S725.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"avx2", MF_INC_LEVEL_W32'
SAB_AFTER='"sse2", /* SABOTAGE S725 */ MF_INC_LEVEL_W32'
