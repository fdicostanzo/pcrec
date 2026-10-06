#!/usr/bin/env bash
# S528 ([MEMFN] R4c, lane r4cchecks) -- A KIT CALL FROM A FUNCTION NO ROW NAMES.
#
# C17's dynamic half is keyed on mf_define/mf_emit calls (the rev-3 key,
# `mf_emit_site(`, named nothing). A call to mf_define from
# pcrec_memfn_stamps_render, which no `delegated` row names (no row at all is
# delegated), is an unlisted site: rule 2 goes red. The call is behind
# `if (0)` so the tree builds and no compile moves. Detector: C17 (arm
# memfnmanifest). SAB_REACH: the half is declared UNREACHED on the clean tree
# and its synthetic-caller selftest passes.
SAB_ID="S528-c17-kit-call-unlisted"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnmanifest"
SAB_DESC='an if (0) call to mf_define is planted in pcrec_memfn_stamps_render, a function no delegated row names: an unlisted site for C17 rule 2'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S528.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_site_manifest.sh" "$TREE"'
SAB_REACH_EXPECT='UNREACHED: rule 2 (dynamic half)
PASS: selftest: the shim logs a synthetic caller'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    mf_art *art = mf_art_begin(&ma, cx->opt->prefix, MF_P_PORTABLE_ONLY, 0);'
SAB_AFTER='    mf_art *art = mf_art_begin(&ma, cx->opt->prefix, MF_P_PORTABLE_ONLY, 0);
    if (0) (void)mf_define(art, NULL, NULL, NULL, NULL); /* SABOTAGE S528 */'
