#!/usr/bin/env bash
# S633 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-prefilter's sets cell stops carrying the refused attempt's size-cap figures, so VM_PREFILTER_WHY would lose its numbers.
# S-F10. Detector at B2: the oracle's post-row carry check on (\p{Xwd}) -e utf8 (fbt (a), (d)); from B3 fbt (c)'s VM_PREFILTER_WHY shape.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S633-t1-drop-prefilter-no-carry'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-prefilter's sets cell stops carrying the refused attempt's size-cap figures, so VM_PREFILTER_WHY would lose its numbers"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S633. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                FIT_CARRY_SIZECAP, false, true },'
SAB_AFTER='                0, false, true },   /* SABOTAGE S633 */'
