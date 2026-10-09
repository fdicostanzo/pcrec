#!/usr/bin/env bash
# S625 ([DEC-FALLBACK] B1, lane decfbB1) -- the `admit` record names T2's two
# default-scope nullable rows the wrong way round (`var-nullable`, the F1
# holder, against `nullable-exact`), so B4's T2 walk would be held to a
# mapping that swaps them.
# Trace build only; the default build is untouched.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# adm-nulex and adm-varnul records.
SAB_ID='S625-admit-trace-var-rows-swapped'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the admit record swaps T2 rows var-nullable and nullable-exact (trace build only)"
SAB_DOC_FIGURE='Read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S625.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# [DEC-FALLBACK] B4 (lane decfbB4, 2026-10-08) RE-AIMED, INTENT RE-VERIFIED.
# The `admit` record now prints the WALK's row name (`fit->pf_admit->name`):
# the record's own derivation is gone, so its row-swap plant has no text.
# The claim, "the trace's admit record names the wrong T2 row", moves to
# the row's NAME cell: row 3 is named as row 4. fbt (a)'s adm-varnul
# (`^${v}$`, hand-written `var-nullable`) is the detector.
SAB_BEFORE='    { "var-nullable",       pfa_var_nullable,       PFV_OFF,     "no-nullable-exact",'
SAB_AFTER='    { "nullable-exact",     pfa_var_nullable,       PFV_OFF,     "no-nullable-exact",   /* SABOTAGE S625 */'
