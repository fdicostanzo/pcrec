#!/usr/bin/env bash
# S635 ([DEC-FALLBACK] B2, lane decfbB2) -- sel1-collapse's sets cell writes CR_SIZECAP instead of CR_SEL1, so the collapse it asks for reports the size rung's reason.
# S-F14. Detector at B2: fit_tables_selfcheck's one-writer-per-reason check refuses every trace compile, and the oracle's post-row cr check (fbt (a), (d)).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S635-t1-sel1-collapse-writes-sizecap'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="sel1-collapse's sets cell writes CR_SIZECAP instead of CR_SEL1, so the collapse it asks for reports the size rung's reason"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S635. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_SET, FIT_CR_TO_SEL1, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },'
SAB_AFTER='      .sets = { FIT_DD_SET, FIT_CR_TO_SIZECAP, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },   /* SABOTAGE S635 */'
