#!/usr/bin/env bash
# S638 ([DEC-FALLBACK] B2, lane decfbB2) -- drop-prefilter's retries cell reads 2, so the table's attempt bound no longer equals COMPILE_MAX_ATTEMPTS' hand formula.
# S-I1 (§1.8). Detector: fit_tables_selfcheck's bound check, which refuses every trace-build compile (fbt (a)/(d)).
# B2 builds the tables BESIDE the old derivations and switches no reader, so
# until the reader switches the trace build's both-derivations oracle (abort
# on a difference, both orders) or fit_tables_selfcheck is the detector;
# the default build is unchanged by the plant.
SAB_ID='S638-t1-attempt-bound-drift'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="drop-prefilter's retries cell reads 2, so the table's attempt bound no longer equals COMPILE_MAX_ATTEMPTS' hand formula"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S638. docs/dev/lanes/decfbB2_report.md carries the B2 run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                 "\"size cap retry, hybrid %llu > %llu\"" },
      .ukw = NULL, .retries = 1, .repeat = FIT_REP_ONCE,'
SAB_AFTER='                 "\"size cap retry, hybrid %llu > %llu\"" },
      .ukw = NULL, .retries = 2, .repeat = FIT_REP_ONCE,   /* SABOTAGE S638 */'
