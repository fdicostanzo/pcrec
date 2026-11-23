#!/usr/bin/env bash
# S3480 (lane l3r66, 2026-11-21; span_arms L3, docs/design/span_arms.md §14.4 L3's REV 3.5 addendum,
# review r66 EMIT-2) -- `ReqWalkParams.fwd_reentry` loses its `-fprefilter` disjunct, so a forced VM with
# a forced hybrid prefilter reads as "no forward re-entry" and BACK displaces the consumed run the
# prefilter's `handoff` row keeps: `(?<=qz)x?a: --engine=vm -fprefilter` lists `717a` at -2 for BASE's
# `613a` at 1 (9.0M -> 14.2M instructions on English text). NO ANSWER MOVES (both runs are sound).
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the `--engine=vm -fprefilter` cells.
SAB_ID="S3480-fwd-reentry-ignores-fprefilter"
SAB_FILE="src/facts/facts.c"
SAB_SUITES="facts"
SAB_DESC='fwd_reentry ignores -fprefilter, so a forced VM with a forced hybrid prefilter loses the forward re-entry on its consumed run to a BACK run at K < 0'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r66_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3480."
SAB_REACH='"$PCREC" --features all --engine=vm -fprefilter --emit-facts --pattern '\''(?<=qz)x?a:'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}613a\t'\'' && echo REACH-PF'
SAB_REACH_EXPECT="REACH-PF"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                        pcrec_opt_has(cx->opt, PCREC_FORCE_PREFILTER)),'
SAB_AFTER='                        false),   /* SABOTAGE S3480 */'
