#!/usr/bin/env bash
# S528 ([MEMFN] R4c, lane r4cchecks) -- A KIT CALL FROM A FUNCTION NO ROW NAMES.
#
# C17's dynamic half is keyed on mf_define/mf_emit calls (the rev-3 key,
# `mf_emit_site(`, named nothing). A call to mf_define from
# pcrec_memfn_stamps_render, which no `delegated` row names, is an unlisted
# site: rule 2's static half goes red. The call is behind `if (0)` so the
# tree builds and no compile moves. Detector: C17 (arm memfnmanifest).
# SAB_REACH: the clean tree's rule 2 is LIVE and passes, its synthetic-caller
# selftest included.
# RE-AIMED 2026-10-06 ([MEMFN] R4c, lane r4cfix): rule 2 went live at R4c
# REPLACE (PRE/OFS/SETREST delegated) and the stamp pass now takes the
# attempt's art (`pcrec_memfn_art`), so the anchor and the reach line move.
# Intent unchanged: a kit call from a function no delegated row names.
SAB_ID="S528-c17-kit-call-unlisted"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="memfnmanifest"
SAB_DESC='an if (0) call to mf_define is planted in pcrec_memfn_stamps_render, a function no delegated row names: an unlisted site for C17 rule 2'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S528.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_site_manifest.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: selftest: the shim logs a synthetic caller
PASS: rule 2 (dynamic half): every function that reached the kit'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    mf_art *art = pcrec_memfn_art(cx);'
SAB_AFTER='    mf_art *art = pcrec_memfn_art(cx);
    if (0) (void)mf_define(art, NULL, NULL, NULL, NULL); /* SABOTAGE S528 */'
