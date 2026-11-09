#!/usr/bin/env bash
# S2999 -- [XARCH-DEV] unit U2 (request R-37; lane u2), A SIMD ROW SERVES ONLY TARGETS ADMITTING ITS
# LEVEL (memfn/src/vrun.c's contracts; fields.def's NO_<level> classes).
#
# Plant: the w32 row's target field also serves the targets that do not admit its level, so the base
# target (which admits w16 only) and the portable one render a w32 rung: 32-byte intrinsics inside a
# region that does not supply them.
# Detector (arm g2simd): memfn/tests/run_g2_simd.py's section 0 (the base target's file holds w32
# helpers; its tokens no longer follow the 32-byte target's by rule), and that file does not compile.
SAB_ID="S2999-vrun-w32-serves-base-target"
SAB_FILE="memfn/src/vrun.c"
SAB_SUITES="g2simd"
SAB_DESC='the w32 vrun row serves a target that does not admit its level'
SAB_DOC_FIGURE='MEASURED by lane u2 by hand (u2_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2999.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=',  /* a target admitting w32 */'
SAB_AFTER=' | CM_NO_LEVEL(1),  /* SABOTAGE S2999: serves NO_w32 too */'
