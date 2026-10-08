#!/usr/bin/env bash
# S624 ([DEC-FALLBACK] B1, lane decfbB1) -- the size-cap ladder's fallback
# record (`fb-size`) stops printing, so T1 rows 6-9 vanish from the trace and
# an ordered compare of `fallback` records cannot see them move.
# Trace build only; the default build is untouched.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)
# (every size-cap sequence reads short); also emit_sweep --variant --trace's
# FALLBACK_TRACE_SITES reach check and row_reach.py, which are lane gates.
SAB_ID='S624-fallback-trace-size-record-dropped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the fallback trace's size-cap record never prints: T1 rows 6-9 disappear from every sequence (trace build only)"
SAB_DOC_FIGURE='At B1 the plant gave 9 (a) failures (docs/dev/lanes/decfbB1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S624.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            FIT_TRACE(&cx, rung->name, restart_term, "fb-size");'
SAB_AFTER='            /* SABOTAGE S624: the size-cap record dropped */'
