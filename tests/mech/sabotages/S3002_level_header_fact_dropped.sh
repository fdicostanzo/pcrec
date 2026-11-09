#!/usr/bin/env bash
# S3002 -- review 2026-11-08 r5 X-1 (lane u2rev), A RENDERED LEVEL NOTES ITS HEADER ON mf_includes.
#
# Plant: memfn/src/ofsskip.c's level block no longer ORs the level's MF_INC_* bit into the art's
# includes, so the host never writes the vector header and the helper's intrinsics are undeclared.
# Detector (matrix column g2simd): memfn/tests/run_g2_simd.py's header-fact check reads the levels the kit
# text renders (its helpers) and requires each level's header among the file-scope includes ahead of the
# region; the failed fact skips the target's compiles (run_g2_simd.py's one rule), so no compiler error reaches the log.
SAB_ID="S3002-level-header-fact-dropped"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2simd"
SAB_DESC='a rendered SIMD level stops stating its header on mf_includes'
SAB_DOC_FIGURE='MEASURED by lane simdskip by hand on a scratch copy of the joint tree (g2simd:2fail/1570pass, 49 compiles skipped because the facts of the target failed, no compiler error in the log; the one rule of run_g2_simd.py, which replaced the s3002fix header-only early return; simdskip_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3002.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    art->includes |= kit_level(r->decl->level)->includes;'
SAB_AFTER='    (void)0;   /* SABOTAGE S3002 */'
