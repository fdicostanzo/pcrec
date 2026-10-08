#!/usr/bin/env bash
# S647 ([DEC-FALLBACK] B3, lane decfbB3) -- T1 row 2 (size-term-trial) is no longer asked on the other label (S-F2): a size-term trial that fails for an ordinary reason refuses the compile instead of ruling its K out
# Live from B3 (the walk is the dispatch, the sets routine the writer).
# Detector: tests/codegen/run_fallback_table.sh (a) seq-trial: the 6-deep tower under --engine=vm refuses where it compiles (also run_size_term.sh's R1 cell).
SAB_ID='S647-t1_trial_on_drops_other'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T1 row 2 (size-term-trial) is no longer asked on the other label (S-F2): a size-term trial that fails for an ordinary reason refuses the compile instead of ruling its K out"
SAB_DOC_FIGURE='Re-run: bash tests/mech/run_sabotage_matrix.sh S647. docs/dev/lanes/decfbB3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .on = FIT_L_OVERFLOW | FIT_L_SIZE | FIT_L_OTHER, .fof = FIT_FOF_OUT,'
SAB_AFTER='      .on = FIT_L_OVERFLOW | FIT_L_SIZE, .fof = FIT_FOF_OUT,   /* SABOTAGE S647 */'
