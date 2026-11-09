#!/usr/bin/env bash
# S3001 -- review 2026-11-08 r5 X-1 (lane u2rev), A LEVEL'S HEADER IS A FACT, NEVER TEXT IN ITS BLOCK.
#
# Plant: memfn/src/ofsskip.c's level block writes the level's `#include` line inside its bracket
# again (the pre-u2rev shape: the header parsed inside the host's target region, which breaks a
# consumer's later intrinsic use at gcc). The fact is still noted, so every compile still builds.
# Detector (arm g2simd): memfn/tests/run_g2_simd.py's per-target check that the kit's text holds
# no `#include`, and its consumer TU over the x86-64-v3 file.
SAB_ID="S3001-level-block-writes-include"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2simd"
SAB_DESC='the offset-skip level block writes its #include inside the target region again'
SAB_DOC_FIGURE='MEASURED by lane u2rev by hand (u2rev_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3001.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    art->includes |= kit_level(r->decl->level)->includes;'
SAB_AFTER='    art->includes |= kit_level(r->decl->level)->includes; o->puts(o->u, mf_include_c(kit_level(r->decl->level)->includes));   /* SABOTAGE S3001 */'
