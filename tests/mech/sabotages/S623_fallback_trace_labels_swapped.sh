#!/usr/bin/env bash
# S623 ([DEC-FALLBACK] B1, lane decfbB1) -- the fallback trace's ARRIVAL
# LABEL SET swaps `overflow` and `size` (src/core/compile.c's
# fit_trace_labels), so every [SEL-1] arrival is recorded as a size-cap one
# and vice versa: T1's `on` masks would be held to the wrong label from B2.
# Trace build only; the default build is untouched.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a), the
# hand-written `row@labels` sequences.
SAB_ID='S623-fallback-trace-labels-swapped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the fallback trace's label set swaps overflow and size: a [SEL-1] arrival reads as a size-cap one (trace build only)"
SAB_DOC_FIGURE='At B1 the same plant reads red on every (a) sequence that arrives with either label and in row_reach.py (declared zeros reached, reached cells dropped) and cross_record.py (docs/dev/lanes/decfbB1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S623.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                 (cx->dfa_overflowed  ? 2u : 0u) |
                                 (cx->size_cap_refused ? 1u : 0u)];'
SAB_AFTER='                                 (cx->dfa_overflowed  ? 1u : 0u) |   /* SABOTAGE S623 */
                                 (cx->size_cap_refused ? 2u : 0u)];'
