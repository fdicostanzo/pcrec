#!/usr/bin/env bash
# S2998 -- [XARCH-DEV] unit U2 (request R-37; lane u2), mf_art_target takes ROWS of the kit's table
# only (the U3 interface sheet, item 1; K0's mf_target_c_of identity rule).
#
# Plant: memfn/src/compose.c's mf_art_target forgets the row test, so a caller's copy of a row (the
# same facts at another address, which mf_target_c_of does not know) and NULL are taken.
# Detector (arm g2simd): memfn/tests/g2/g2_simd_gen.c's refusal cases (a copy, NULL) are accepted
# and the generator fails. A NULL taken also faults later in the same art.
SAB_ID="S2998-art-target-accepts-copy"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2simd"
SAB_DESC='mf_art_target takes a pointer that is not a row of the kit table (a copy, or NULL)'
SAB_DOC_FIGURE='Not yet run by hand; exact re-run: bash tests/mech/run_sabotage_matrix.sh S2998.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!t || !mf_target_c_of(t))
        return kit_fail(art, "mf_art_target: the target is not a row of the kit'"'"'s table");'
SAB_AFTER='    if (0)   /* SABOTAGE S2998 */
        return kit_fail(art, "mf_art_target: the target is not a row of the kit'"'"'s table");'
