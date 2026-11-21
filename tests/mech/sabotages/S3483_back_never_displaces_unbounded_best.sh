#!/usr/bin/env bash
# S3483 (lane l3r66, 2026-11-21; review r66 CHECK-4's plant V2-M5, span_arms §14.4 L3's REV 3.5 addendum)
# -- BACK's `displaces` loses its unbounded-best disjunct, so a consumed run at no static bound (which no
# forward re-entry keeps) is never displaced: `(?<=xyz)a+xyz` lists BASE's unbounded run for BACK's
# `78797a61` at -3 (the 0.33-0.82 win lost). NO ANSWER MOVES. The narrowing direction of the rule.
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the default-route `(?<=xyz)a+xyz` cells.
SAB_ID="S3483-back-never-displaces-unbounded-best"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='TOP'\''s BACK row never displaces a consumed run at no static bound, so (?<=xyz)a+xyz loses its lookbehind run'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r66_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3483."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=xyz)a+xyz'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}78797a61\t'\'' && echo REACH-UNBOUNDED-BEST'
SAB_REACH_EXPECT="REACH-UNBOUNDED-BEST"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        || (lo < hi && best->off >= PCREC_W_UNBOUNDED);'
SAB_AFTER='        || false;   /* SABOTAGE S3483 */'
