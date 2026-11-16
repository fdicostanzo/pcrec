#!/usr/bin/env bash
# S3250 ([MEMFN] R-45 plan B, review 2026-11-16 r27 SEAM-1/CHECK-4; lane span4kfix) --
# FRAMED ASK WRITES ROWS THEN REFUSES.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the framed ask writes its plan lists into the
# caller's rows and only then refuses a missing plan_test list (plan B's shipped order):
# a refused ask has written the caller's rows. The detector is the purity harness's
# refusal fixture (arm_fixtures --purity, pur_refusal_rows: "a framed ask with no
# plan_test list answered ... or wrote the caller's rows"), run by run_finder.sh.
SAB_ID="S3250-framed-ask-writes-rows-then-refuses"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='a framed ask writes the caller'"'"'s plan rows before it refuses a missing plan_test list: the purity refusal fixture (rows held to a sentinel across a refused ask) is red'
SAB_DOC_FIGURE='Validated by plant 2026-11-16 (lane span4kfix, docs/dev/lanes/span4kfix_report.md). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3250.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (ok && !art->err[0] && rows_hold(d, rows, 1)) {'
SAB_AFTER='        if (ok && rows_hold(d, rows, 0)) reply_of(d, out, rows);   /* SABOTAGE S3250 */
        if (ok && !art->err[0] && rows_hold(d, rows, 1)) {'
