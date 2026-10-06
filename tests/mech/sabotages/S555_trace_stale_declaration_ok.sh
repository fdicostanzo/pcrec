#!/usr/bin/env bash
# S555 ([START-TABLE] C0, lane stc0 row F; docs/dev/lanes/stc0_report.md §2) -- a declared multiplicity that filters nothing on the working side is accepted: a stale declaration hides nothing but passes.
# Detector (arm emitsweep): scripts/tests/trace_diff.py.test.
SAB_ID='S555-trace-stale-declaration-ok'
SAB_FILE='scripts/trace_diff.py'
SAB_SUITES='emitsweep'
SAB_DESC='a declared multiplicity that filters nothing on the working side is accepted: a stale declaration hides nothing but passes'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc0_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S555.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if declared and filtered[1] == 0:'
SAB_AFTER='    if False:   # SABOTAGE S555'
