#!/usr/bin/env bash
# S3002 -- review 2026-11-08 r5 X-1 (lane u2rev), A RENDERED LEVEL NOTES ITS HEADER ON mf_includes.
#
# Plant: memfn/src/ofsskip.c's level block no longer ORs the level's MF_INC_* bit into the art's
# includes, so the host never writes the vector header and the helper's intrinsics are undeclared.
# Detector (arm g2simd): memfn/tests/run_g2_simd.py writes every mf_includes line ahead of the
# region and compiles each target's file; the x86-64 and x86-64-v3 files fail to build.
SAB_ID="S3002-level-header-fact-dropped"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2simd"
SAB_DESC='a rendered SIMD level stops stating its header on mf_includes'
SAB_DOC_FIGURE='MEASURED by lane u2rev by hand (u2rev_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3002.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    art->includes |= kit_level(r->decl->level)->includes;'
SAB_AFTER='    (void)0;   /* SABOTAGE S3002 */'
