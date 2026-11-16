#!/usr/bin/env bash
# S3251 ([MEMFN] R-45 plan B, review 2026-11-16 r27 CHECK-2; lane span4kfix) --
# NONE REPLY CARRIES PLAN_TEST.
#
# WHAT IT BREAKS AND WHO CATCHES IT: a NONE ask answers a plan_test list (the
# caller's) though NONE's frame part is zero: purity's "NONE's reply carries a
# plan_test list" (arm_fixtures --purity, run by run_finder.sh) is red. S3086's
# frame-part compare sets the list pointers aside, so it cannot see this one.
SAB_ID="S3251-none-reply-carries-plan-test"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='a NONE reply carries the caller'"'"'s plan_test list: the purity fixture asserting plan_test NULL on NONE is red'
SAB_DOC_FIGURE='Validated by plant 2026-11-16 (lane span4kfix, docs/dev/lanes/span4kfix_report.md). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3251.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        reply_of(d, out, rows);
        rc = 0;'
SAB_AFTER='        reply_of(d, out, rows);
        rc = 0;
        if (out->nplan && rows->plan_test) { memset(rows->plan_test, 1, out->nplan); out->plan_test = rows->plan_test; }   /* SABOTAGE S3251 */'
