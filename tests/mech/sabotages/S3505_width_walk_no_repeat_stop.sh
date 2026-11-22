#!/usr/bin/env bash
# S3505 (K159, lane k159fix; docs/dev/known_issues.md K159) -- the width walk's repeated-frontier stop removed: an unbounded pattern walks to the `j > nfa->n` backstop again (n closures of an n-state frontier).
# Detector: run_facts_checks.sh [facts-width-cpu] (nested + 14 deep under a 5 CPU-second watchdog bound; the unfixed walk spends about 20 s on the dev box). Same answers: no answer-level check can see it.
SAB_ID='S3505-width-walk-no-repeat-stop'
SAB_FILE='src/facts/kset.c'
SAB_SUITES='facts'
SAB_DESC='pcrec_width_walk never compares the frontier with its checkpoint, so nested + 14 deep compiles in about 20 CPU seconds instead of 0.07 (K159 restored; width answers unchanged)'
SAB_DOC_FIGURE='validated by plant at lane k159fix ([facts-width-cpu] FAILS, watchdog rc 123); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3505.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (w.ncur == nck) {'
SAB_AFTER='        if (0 && w.ncur == nck) {   /* SABOTAGE S3505 */'
