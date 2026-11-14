#!/usr/bin/env bash
# S3124 ([MEMFN] span_pick 3.0b, D27 finding F4; lane d27fix) -- A RUN COMPARE'S POSITIONS ANSWER TABLE.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the reply's plan_test answers TABLE for an offered position E-find
# tests inside a run compare (one compare of the stretch's bytes, which reads no table), as before the
# ruling that the reply follows the text. No byte moves. The detectors are the D27 frame suite
# (tests/memfn/d27_frame/): obs_plan_test_table_text_runcmp (TABLE where the text reads no offer), and
# on its traced runs the kit's agreement, whose define-side reading kept the ruling.
SAB_ID="S3124-run-compare-answers-table"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnd27frame"
SAB_DESC='plan_test answers TABLE for an offered position inside a run compare, whose text reads no table (D27 finding F4)'
SAB_DOC_FIGURE='Validated by plant (lane d27fix, docs/dev/lanes/d27fix_report.md), by hand on a copy of the tree: D27_QUICK=1 tests/memfn/d27_frame/run.sh red. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3124.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return w->table[k] && w->grp[k] < 0 ? MF_WTEST_TABLE : MF_WTEST_OWN;'
SAB_AFTER='    return w->table[k] ? MF_WTEST_TABLE : MF_WTEST_OWN;   /* SABOTAGE S3124 */'
