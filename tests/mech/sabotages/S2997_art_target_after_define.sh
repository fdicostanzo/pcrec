#!/usr/bin/env bash
# S2997 -- [XARCH-DEV] unit U2 (request R-37; lane u2), mf_art_target's ORDER RULE (memfn.h: stated
# before the art's first define; the U3 interface sheet, item 1).
#
# Plant: memfn/src/compose.c's mf_art_target forgets the art's defines, so an art whose first site
# was rendered for no target can be given one after it (its earlier text then disagrees with its
# later text and its stamps).
# Detector (arm g2simd): memfn/tests/g2/g2_simd_gen.c's control art (site 0 defined with no target
# stated, then the target stated) must be refused; the generator fails, and the family is red.
SAB_ID="S2997-art-target-after-define"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2simd"
SAB_DESC='mf_art_target accepts a first statement after the art has defined a site'
SAB_DOC_FIGURE='MEASURED by lane u2 by hand (u2_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2997.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!art->target && art->nsites)'
SAB_AFTER='    if (!art->target && art->nsites && 0)   /* SABOTAGE S2997 */'
