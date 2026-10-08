#!/usr/bin/env bash
# S644 ([DEC-FALLBACK] B2, lane decfbB2) -- T4's cap-rescue and size-model rows swapped, so a cap rescue that also moved K would stamp size-model.
# S-T4a. Detector at B2: the stwhy oracle on lowsize (?:a\K){0,10}ab (fbt (d) or-w-cr); from B5 run_size_term.sh §6 and fbt (b).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S644-t4-rescue-model-swapped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T4's cap-rescue and size-model rows swapped, so a cap rescue that also moved K would stamp size-model"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S644. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { NULL,                  stw_rescue,  true  },
    { "size-model",          stw_moved,   false },'
SAB_AFTER='    { "size-model",          stw_moved,   false },
    { NULL,                  stw_rescue,  true  },   /* SABOTAGE S644 */'
