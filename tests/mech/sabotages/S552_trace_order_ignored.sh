#!/usr/bin/env bash
# S552 ([START-TABLE] C0, lane stc0 row C; docs/dev/lanes/stc0_report.md §2) -- the ordered per-pattern compare becomes a multiset compare: a swap or reorder of records inside one pattern reads clean.
# Detector (arm emitsweep): scripts/tests/trace_diff.py.test.
SAB_ID='S552-trace-order-ignored'
SAB_FILE='scripts/trace_diff.py'
SAB_SUITES='emitsweep'
SAB_DESC='the ordered per-pattern compare becomes a multiset compare: a swap or reorder of records inside one pattern reads clean'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc0_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S552.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if sa != sb:
            pos ='
SAB_AFTER='        if sorted(sa) != sorted(sb):   # SABOTAGE S552
            pos ='
