#!/usr/bin/env bash
# S629 ([DEC-FALLBACK] B2, lane decfbB2) -- sel1-collapse's sets cell does not latch dfa_was_engine on the first overflow, so an overflowed DFA engine is attributed overflowed-prefilter.
# S-F8's cell (the latch column). Detector at B2: the oracle's post-row latch check on W_OVF/W_SEL1 (fbt (a), (d)); from B3 fbt (b) overflowed-dfa -> overflowed-prefilter.
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S629-t1-sel1-collapse-no-latch'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="sel1-collapse's sets cell does not latch dfa_was_engine on the first overflow, so an overflowed DFA engine is attributed overflowed-prefilter"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S629. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_SET, FIT_CR_TO_SEL1, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, true, false },'
SAB_AFTER='      .sets = { FIT_DD_SET, FIT_CR_TO_SEL1, FIT_SDR_KEEP, 0, FIT_CARRY_OVW, false, false },   /* SABOTAGE S629 */'
