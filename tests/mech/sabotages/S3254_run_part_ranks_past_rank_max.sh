#!/usr/bin/env bash
# S3254 ([MEMFN] R-45 raise, review 2026-11-16 r27 READ-1; lane span4kfix) --
# RUN PART RANKS PAST RANK_MAX.
#
# WHAT IT BREAKS AND WHO CATCHES IT: run_part_terms no longer declines a scan stretch
# over MF_RANK_MAX positions, so run_rank writes past mf_pred.rank_pos[MF_RANK_MAX] (a
# silent in-struct overwrite at 33 positions; a heap overflow at 100). The purity
# harness's long-run fixture (arm_fixtures --purity, pur_long_run_fixtures: a 33-position
# run part must be refused NAMING the stretch) is red; run_finder.sh runs it.
SAB_ID="S3254-run-part-ranks-past-rank-max"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='run_part_terms ranks a scan stretch of over MF_RANK_MAX positions (the declining row contract removed): the 33-position long-run fixture is not refused by the stretch rule and is red'
SAB_DOC_FIGURE='Validated by plant 2026-11-16 (lane span4kfix, docs/dev/lanes/span4kfix_report.md): fx --purity 1 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3254.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (b - a > MF_RANK_MAX) {'
SAB_AFTER='    if (0 && b - a > MF_RANK_MAX) {   /* SABOTAGE S3254 */'
