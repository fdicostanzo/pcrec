#!/usr/bin/env bash
# S2995 -- [XARCH-DEV] unit U2 (request R-37; lane u2), THE KIT'S TEXT HOLDS NO CPU `#if`
# (target_seam_units.md §2's U2 row; the host's region supplies the ISA).
#
# Plant: memfn/src/ofsskip.c's level block writes a preprocessor conditional into the level again (an
# empty `#if` / `#endif` pair on a plant-only macro, the pre-U2 shape), which compiles everywhere.
# Detector (arm g2simd): memfn/tests/run_g2_simd.py's section 0 counts the conditionals in the kit's
# text between G2's markers in every target's file: one is red.
SAB_ID="S2995-ofsskip-level-block-if"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="g2simd"
SAB_DESC='the offset-skip level block writes an #if again: the kit text is no longer conditional-free'
SAB_DOC_FIGURE='MEASURED by lane u2 by hand (u2_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2995.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o->simd_open(o->u, (int)r->decl->level);'
SAB_AFTER='    o->simd_open(o->u, (int)r->decl->level); o->puts(o->u, "#if defined(MF_U2_PLANT)\n#endif\n");   /* SABOTAGE S2995 */'
