#!/usr/bin/env bash
# S630 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-prefilter's sets cell no longer restarts the size term, so the re-emitted VM artifact would pick K for an artifact that no longer exists.
# S-F11's cell on row 9. Detector at B2: fit_tables_selfcheck's bound check first (a restarting row adds a ladder run to the bound), then the oracle's post-row restart check on (\p{Xwd}) -e utf8 (fbt (a), (d)); from B3 the trace's trial records.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S630-t1-drop-prefilter-no-restart'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-prefilter's sets cell no longer restarts the size term, so the re-emitted VM artifact would pick K for an artifact that no longer exists"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S630. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                FIT_CARRY_SIZECAP, false, true },'
SAB_AFTER='                FIT_CARRY_SIZECAP, false, false },   /* SABOTAGE S630 */'
