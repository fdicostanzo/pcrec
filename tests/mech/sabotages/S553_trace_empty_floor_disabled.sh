#!/usr/bin/env bash
# S553 ([START-TABLE] C0, lane stc0 row D; docs/dev/lanes/stc0_report.md §2) -- the records floor no longer fires when NO arm carried any record: an empty trace on both sides passes (the empty-vs-empty shape).
# Detector (arm emitsweep): scripts/tests/trace_diff.py.test.
SAB_ID='S553-trace-empty-floor-disabled'
SAB_FILE='scripts/trace_diff.py'
SAB_SUITES='emitsweep'
SAB_DESC='the records floor no longer fires when NO arm carried any record: an empty trace on both sides passes (the empty-vs-empty shape)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc0_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S553.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if not floors and not arms:'
SAB_AFTER='        if False:   # SABOTAGE S553'
