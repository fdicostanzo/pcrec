#!/usr/bin/env bash
# S640 ([DEC-FALLBACK] B2, lane decfbB2) -- T2's forced-off and var rows swapped, so -fno-prefilter a${v}b would list no-engine-vm instead of no-fno-prefilter.
# S-T2g. Detector at B2: the listing oracle on --emit-ir -fno-prefilter a${v}b (fbt (d) or-l-varff); from B4 the check_ir_value row.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S640-t2-forced-off-var-swapped'
SAB_FILE='src/opt/select_engine.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T2's forced-off and var rows swapped, so -fno-prefilter a\${v}b would list no-engine-vm instead of no-fno-prefilter"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S640. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "forced-off",         pfa_forced_off,         PFV_OFF,     "no-fno-prefilter",
      ESEL_PASS },
    { "var",                pfa_var,                PFV_OFF,     "no-engine-vm",
      ESEL_PASS },'
SAB_AFTER='    { "var",                pfa_var,                PFV_OFF,     "no-engine-vm",
      ESEL_PASS },
    { "forced-off",         pfa_forced_off,         PFV_OFF,     "no-fno-prefilter",
      ESEL_PASS },   /* SABOTAGE S640 */'
