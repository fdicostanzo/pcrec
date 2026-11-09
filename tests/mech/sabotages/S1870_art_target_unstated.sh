# S1870 ([XARCH-DEV] U3, lane u3tgt) -- the art is never told its CPU target: pcrec_memfn_art skips mf_art_target, so the kit refuses the art's first site define ("the art states no target") and every compile that reaches a memfn site fails with an internal error. (Corrected by lane u3crit, review 2026-11-08-r5-xarch X-5a: the row first said every art renders the portable text, which was the staging switch's position 0; since the joint merge the refusal is the kit's only answer.) A WRONG target, rather than none, is S1885.
# Successor of S1864 (RETIRED 2026-11-08 by lane u3tgt: it planted the derivation of MF_P_PORTABLE_ONLY off the target set, pcrec_memfn_policy, which U3 deleted; this row plants the statement that replaced it).
# Detector (arm cli): collateral -- tests/cli/run_cli_tests.sh's compiles that reach a memfn site fail outright, the vrun cases first.
SAB_ID="S1870-art-target-unstated"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="cli"
SAB_DESC="the art is never told its CPU target (mf_art_target skipped), so the kit refuses its first define and every compile reaching a memfn site fails"
SAB_DOC_FIGURE="cli: every run_cli_tests.sh case that compiles through a memfn site reads red (the vrun cases first). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1870."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (mf_art_target(job->mf, pcrec_memfn_target(cx)))'
SAB_AFTER='        if (0 && mf_art_target(job->mf, pcrec_memfn_target(cx)))   /* SABOTAGE S1870 */'
