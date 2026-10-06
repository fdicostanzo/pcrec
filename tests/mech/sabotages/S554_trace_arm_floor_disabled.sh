#!/usr/bin/env bash
# S554 ([START-TABLE] C0, lane stc0 row E; docs/dev/lanes/stc0_report.md §2) -- the per-arm records floor never fires: a trace arm below its floor passes when both sides agree.
# Detector (arm emitsweep): scripts/tests/trace_diff.py.test.
SAB_ID='S554-trace-arm-floor-disabled'
SAB_FILE='scripts/trace_diff.py'
SAB_SUITES='emitsweep'
SAB_DESC='the per-arm records floor never fires: a trace arm below its floor passes when both sides agree'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc0_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S554.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                if got[side] < fl:'
SAB_AFTER='                if False:   # SABOTAGE S554'
