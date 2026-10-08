#!/usr/bin/env bash
# S649 ([DEC-FALLBACK] B3, lane decfbB3) -- the sets routine re-latches dfa_was_engine on EVERY overflow, not only the first (S-F8): the collapsed prefilter's overflow overwrites the DFA's role, so overflowed-dfa reads overflowed-prefilter
# Live from B3 (the walk is the dispatch, the sets routine the writer).
# Detector: tests/codegen/run_fallback_table.sh (a) fstate seq-sel1cd 2 latch=1/0 and (b) att-ovfdfa on ^(?:(?:a|b)*a(?:a|b){20})?$.
SAB_ID='S649-sets_latch_every_overflow'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the sets routine re-latches dfa_was_engine on EVERY overflow, not only the first (S-F8): the collapsed prefilter's overflow overwrites the DFA's role, so overflowed-dfa reads overflowed-prefilter"
SAB_DOC_FIGURE='Re-run: bash tests/mech/run_sabotage_matrix.sh S649. docs/dev/lanes/decfbB3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (w->latch && !dfa_disabled) {'
SAB_AFTER='            if (w->latch) {   /* SABOTAGE S649 */'
