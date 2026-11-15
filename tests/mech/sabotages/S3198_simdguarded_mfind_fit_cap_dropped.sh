#!/usr/bin/env bash
# S3198 (lane mcfixd, 2026-11-15; r5 CHECKS-5 of docs/dev/reviews/2026-11-15-r5-memfn-mfindcomb.md)
# -- THE FUSED ONE-MEMBER FINDER'S FIT CAP IS DROPPED.
#
# mfind_applies answers `ofs_fn_fits(x, d)`: a site whose verify chain would
# render more guarded bytes than the row's declared bound DECLINES the row and
# keeps the SWAR body alone (review 2026-11-15 r2 F1). Made unconditional, the
# long-chain lever witnesses (mfind-long-tbl, mfind-long-run) render the w16/w32
# helpers again and stamp 4,089 / 2,335 guarded bytes at x86-64, past the
# declared mfind-w16 bound plus target-text: simd_guarded_check's "plain stamp
# exceeds the sum of its rows' bounds" and the lever-capped floor (0 < 4) fire.
# G2's one-member space never reaches the cap (every G2 site fits), so only
# this suite can see it.
SAB_ID='S3198-simdguarded-mfind-fit-cap-dropped'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='simdguarded'
SAB_DESC="mfind_applies no longer asks the fit test, so the long verify chains render SIMD helpers past the row's declared bound"
SAB_DOC_FIGURE='DESIGNED by lane mcfixd 2026-11-15; LOUD expected (plain stamp over the rows bound sum; lever-capped floor). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3198.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return ofs_fn_fits(x, d);'
SAB_AFTER='    (void)x; (void)d; return 1;   /* SABOTAGE S3198 */'
