#!/usr/bin/env bash
# S1910 (lane sae1fix, 2026-11-09; review 2026-11-09-r3-sae1 CHECK-3) -- THE
# M>=1 HALF OF T2 ROW 1 LOSES ITS `all`.
#
# A repeat of a width-0 body at `rmin >= 1` (`ab(?:\B){3}cd`) is the ruled
# half of row 1: the run joins across it. This plant drops the `all` mark
# there, so the run stays the old `6364` (a sound loss, answers unchanged).
# Detector: tests/codegen/run_facts_checks.sh [facts-arm], the m>=1 cells.
SAB_ID="S1910-rep-unit-min1-not-all"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="a repeat of a width-0 body at rmin>=1 no longer marks its value all, so the run is not joined across it"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae1fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1910."
SAB_REACH='"$PCREC" --features all -p rx --emit-main -o /dev/stdout --pattern "ab(?:\\B){3}cd" | grep -qF "RX_REQ_RUN \"61626364@1\"" && echo REACH-M1-JOINS'
SAB_REACH_EXPECT="REACH-M1-JOINS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    v->runs.all = true;'
SAB_AFTER='    v->runs.all = rmin == 0;   /* SABOTAGE S1910 */'
