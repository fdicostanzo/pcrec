#!/usr/bin/env bash
# S3258 ([MEMFN] R-45 raise, review 2026-11-16 r28 R28-1; lane raisefix) --
# RUN PART TERMS PAST MAX_TERM.
#
# WHAT IT BREAKS AND WHO CATCHES IT: run_part_terms no longer declines a derived run
# part of more than MF_MAX_TERM terms, so it writes past mf_pred.term[MF_MAX_TERM] (an
# out-of-bounds index 33 under UBSan at 40 unspelled positions; the translated
# vocabulary's own "nterm > MF_MAX_TERM" catch comes only AFTER the write). The
# purity harness's long-run fixture (arm_fixtures --purity, pur_long_run_fixtures: a
# part of MF_MAX_TERM + 8 unspelled positions must be refused NAMING the term count)
# is red; run_finder.sh runs it. S3254 is the stretch rule's sibling row.
SAB_ID="S3258-run-part-terms-past-max-term"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='run_part_terms writes a derived run part of more than MF_MAX_TERM terms (the term rule of the declining row contract removed): the 40-unspelled-position long-run fixture is not refused by the term rule and is red'
SAB_DOC_FIGURE='Validated by plant 2026-11-16 (lane raisefix, docs/dev/lanes/raisefix_report.md): fx --purity 1 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3258.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (nterms > MF_MAX_TERM) {'
SAB_AFTER='    if (0 && nterms > MF_MAX_TERM) {   /* SABOTAGE S3258 */'
