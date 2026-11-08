# S1870 ([XARCH-DEV] U3, lane u3tgt) -- the art is never told its CPU target: pcrec_memfn_art skips mf_art_target, so every art renders the portable target's text and a SIMD target's artifact carries its guard and region around no SIMD level.
# Successor of S1864 (RETIRED 2026-11-08 by this lane: it planted the derivation of MF_P_PORTABLE_ONLY off the target set, pcrec_memfn_policy, which U3 deleted; the set's one member IS the art's target now, so the derivation it broke no longer exists; this row plants the statement that replaced it).
# Detector (arm cli): tests/cli/run_cli_tests.sh's vrun case at the 16-byte target (the w16 helper is not rendered).
SAB_ID="S1870-art-target-unstated"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="cli"
SAB_DESC="the art is never told its CPU target (mf_art_target skipped), so a SIMD target's artifact renders no SIMD level"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh vrun-w16 case reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1870."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (mf_art_target(job->mf, pcrec_memfn_target(cx)))'
SAB_AFTER='        if (0 && mf_art_target(job->mf, pcrec_memfn_target(cx)))   /* SABOTAGE S1870 */'
