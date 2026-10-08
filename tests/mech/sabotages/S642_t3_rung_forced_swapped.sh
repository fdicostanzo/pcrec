#!/usr/bin/env bash
# S642 ([DEC-FALLBACK] B2, lane decfbB2) -- T3's rung and forced rows swapped, so a [SEL-1] rung collapse would stamp the forced language reason.
# S-T3a. Detector at B2: the gate oracle on (1{0,30}?[^]abc][^abc]){28,30}0+|a (fbt (a) gate-sel1, (d) or-g-sel1); from B5 fbt (c).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S642-t3-rung-forced-swapped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T3's rung and forced rows swapped, so a [SEL-1] rung collapse would stamp the forced language reason"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S642. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "rung",     pflw_rung,   true,  PFLW_PASS     },
    { "forced",   pflw_worth,  true,  PFLW_FORCED   },'
SAB_AFTER='    { "forced",   pflw_worth,  true,  PFLW_FORCED   },
    { "rung",     pflw_rung,   true,  PFLW_PASS     },   /* SABOTAGE S642 */'
