#!/usr/bin/env bash
# S3252 ([MEMFN] R-45 plan B, review 2026-11-16 r27 CHECK-3; lane span4kfix) --
# REPLY LISTS IN KIT STORAGE.
#
# WHAT IT BREAKS AND WHO CATCHES IT: reply_of copies the plan lists into the caller's
# rows but points the reply at a kit-owned static copy: the reply's lists are not the
# caller's rows (and two held replies alias). The purity harness's ask wrapper
# ("the reply's plan list is not the caller's rows") and d27_frame's
# lists_are_caller_rows are red; run_finder.sh runs the first.
SAB_ID="S3252-reply-lists-in-kit-storage"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='reply_of points the reply'"'"'s plan lists at kit-owned static storage instead of the caller'"'"'s rows: purity'"'"'s owner check (reply lists == the rows passed) is red'
SAB_DOC_FIGURE='Validated by plant 2026-11-16 (lane span4kfix, docs/dev/lanes/span4kfix_report.md). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3252.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    out->plan = rows->plan;
    out->plan_term = rows->plan_term;'
SAB_AFTER='    static int32_t sab_plan[MF_WPLAN_MAX]; static uint16_t sab_term[MF_WPLAN_MAX];   /* SABOTAGE S3252 */
    memcpy(sab_plan, rows->plan, d->np * sizeof *sab_plan); memcpy(sab_term, rows->plan_term, d->np * sizeof *sab_term);
    out->plan = sab_plan;
    out->plan_term = sab_term;'
