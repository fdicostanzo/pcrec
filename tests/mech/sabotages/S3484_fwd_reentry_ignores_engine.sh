#!/usr/bin/env bash
# S3484 (lane l3r66, 2026-11-21; review r66 CHECK-4's plant V3-Fa, span_arms §14.4 L3's REV 3.5 addendum)
# -- `ReqWalkParams.fwd_reentry` loses its engine clause, so `--engine=vm` (no hybrid prefilter, no
# forward re-entry) reads as a forward route and keeps the consumed run: `(?<=foo)bar --engine=vm` lists
# `626172` at 0 for BACK's `666f6f626172` at -3. NO ANSWER MOVES. The narrowing direction of the rule.
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the `--engine=vm` cells.
SAB_ID="S3484-fwd-reentry-ignores-engine"
SAB_FILE="src/facts/facts.c"
SAB_SUITES="facts"
SAB_DESC='fwd_reentry ignores the engine, so the forced VM (no forward re-entry) never takes BACK'\''s run over a bounded consumed run'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r66_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3484."
SAB_REACH='"$PCREC" --features all --engine=vm --emit-facts --pattern '\''(?<=foo)bar'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}666f6f626172\t'\'' && echo REACH-VM'
SAB_REACH_EXPECT="REACH-VM"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                       (cx->opt->engine != PCREC_ENGINE_VM ||'
SAB_AFTER='                       (true ||   /* SABOTAGE S3484 */'
