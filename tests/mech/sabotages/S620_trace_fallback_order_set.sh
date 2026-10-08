#!/usr/bin/env bash
# S620 ([DEC-FALLBACK] S-I2, dec_fallback.md §4.4; drafted at B0 by decfbB0c,
# numbered at B1, lane decfbB1) -- trace_diff's per-slot ORDERED mode is
# downgraded to a set compare, so the `fallback` slot's record order (an
# arrival's sequence IS the attempt order, the property B2-B5 gate on) reads
# clean when two records swap.
# Detector (arm emitsweep): scripts/tests/trace_diff.py.test, whose
# order-overrides-unordered / order-x-ordered-* cases plant the swap.
SAB_ID='S620-trace-fallback-order-set'
SAB_FILE='scripts/trace_diff.py'
SAB_SUITES='emitsweep'
SAB_DESC="trace_diff's --order SLOT=ordered is compared as a SET: a swap of two fallback records inside one compile reads clean"
SAB_DOC_FIGURE='B0 drafted the plant (order ignored: 4 of 30 self-tests red, docs/dev/lanes/decfbB0c_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S620.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if order[slot] == "set":'
SAB_AFTER='            if order[slot] in ORDER_MODES:   # SABOTAGE S620: every named slot compared as a set'
