#!/usr/bin/env bash
# S643 ([DEC-FALLBACK] B2, lane decfbB2) -- T3's projection reads the size rung's row for a [SEL-1] rung, so a SEL1 collapse would stamp size cap retry.
# S-T3c. Detector at B2: the gate oracle on W_SEL1 (fbt (a)/(d)); from B5 fbt (c).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S643-t3-projection-wrong-reason'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T3's projection reads the size rung's row for a [SEL-1] rung, so a SEL1 collapse would stamp size cap retry"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S643. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    const FitCrCell want = cr == CR_SEL1 ? FIT_CR_TO_SEL1'
SAB_AFTER='    const FitCrCell want = cr == CR_SEL1 ? FIT_CR_TO_SIZECAP   /* SABOTAGE S643 */'
