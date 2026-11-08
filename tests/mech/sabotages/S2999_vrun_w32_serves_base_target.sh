#!/usr/bin/env bash
# S2999 -- [XARCH-DEV] unit U2 (request R-37; lane u2), A SIMD ROW SERVES ONLY TARGETS ADMITTING ITS
# LEVEL (memfn/src/vrun.c's contracts; fields.def's NO_<level> classes).
#
# Plant: the w32 row's target field serves every stated target, so the base target (which admits w16
# only) renders a w32 rung: AVX2 intrinsics inside an SSE2 region.
# Detector (arm g2simd): memfn/tests/run_g2_simd.py's section 0 (the x86-64 file holds w32 helpers;
# every site's x86-64 token is no longer its x86-64-v3 token less w32), and the x86-64 file's builds
# do not compile.
SAB_ID="S2999-vrun-w32-serves-base-target"
SAB_FILE="memfn/src/vrun.c"
SAB_SUITES="g2simd"
SAB_DESC='the w32 vrun row serves a target that does not admit its level'
SAB_DOC_FIGURE='MEASURED by lane u2 by hand (u2_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2999.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [FLD_target]          = MF_ANY & ~CM_NO_LEVEL(LV_X86_W32),  /* a target admitting its level */'
SAB_AFTER='    [FLD_target]          = MF_ANY & ~CM_NO_LEVEL(LV_X86_W16),  /* SABOTAGE S2999 */'
