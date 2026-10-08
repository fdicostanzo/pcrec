#!/usr/bin/env bash
# S628 ([DEC-FALLBACK] B2, lane decfbB2) -- sel1-drop's sets cell keeps dfa_disabled instead of setting it: on a first overflow under -fno-prefilter-collapse the retry would rebuild the machine that overflowed.
# S-F13. Detector at B2: the oracle's post-row state check on the first-overflow sel1-drop witness (fbt (a) seq-sel1d, (d) or-sel1d0); from B3 the compile loops to the attempt cap.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S628-t1-sel1-drop-keeps-dd'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="sel1-drop's sets cell keeps dfa_disabled instead of setting it: on a first overflow under -fno-prefilter-collapse the retry would rebuild the machine that overflowed"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S628. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_SET, FIT_CR_TO_NONE, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },'
SAB_AFTER='      .sets = { FIT_DD_KEEP, FIT_CR_TO_NONE, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },   /* SABOTAGE S628 */'
