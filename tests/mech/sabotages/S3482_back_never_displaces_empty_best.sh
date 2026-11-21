#!/usr/bin/env bash
# S3482 (lane l3r66, 2026-11-21; review r66 CHECK-4's plant V1-M2, span_arms §14.4 L3's REV 3.5 addendum)
# -- BACK's `displaces` loses its empty-best disjunct, so where no consumed run and no bounded byte
# landmark exists (`(?<=foo)`) BACK's run is not chosen on a forward route: `(?<=foo)` lists no run for
# `666f6f` at -3 (the x8 win lost). NO ANSWER MOVES. The narrowing direction of the rule.
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the default-route `(?<=foo)` cell.
SAB_ID="S3482-back-never-displaces-empty-best"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='TOP'\''s BACK row never displaces an empty consumed run on a forward route, so (?<=foo) loses its lookbehind run'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r66_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3482."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=foo)'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}666f6f\t'\'' && echo REACH-EMPTY-BEST'
SAB_REACH_EXPECT="REACH-EMPTY-BEST"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        || (best->n == 0 && !rb_set_bounded_landmark(set))'
SAB_AFTER='        || false   /* SABOTAGE S3482 */'
