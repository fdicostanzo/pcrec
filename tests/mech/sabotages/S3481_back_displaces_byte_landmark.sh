#!/usr/bin/env bash
# S3481 (lane l3r66, 2026-11-21; span_arms L3, docs/design/span_arms.md §14.4 L3's REV 3.5 addendum,
# review r66 EMIT-3) -- BACK's `displaces` forgets the byte landmark: an EMPTY consumed `best` is taken as
# "nothing to keep" even where a necessary byte sits at a bounded K, so `(?<=qz)(?:a.|.a)` lists `717a`
# at -2 for BASE's no run (byte landmark `a` at K 1) and its forward re-entry on `a` is lost to the K < 0
# decline (9.0M -> 40.0M instructions on qz-dense text). NO ANSWER MOVES (both landmarks are sound).
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the default-route `(?<=qz)(?:a.|.a)` cells.
SAB_ID="S3481-back-displaces-byte-landmark"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='TOP'\''s BACK row displaces an empty consumed run whose set holds a byte at a bounded K, so the forward re-entry on that byte landmark is lost to the K < 0 decline'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r66_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3481."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=qz)(?:a.|.a)'\'' | grep -qP '\''^byte\treq_landmark_maxoff\t([^\t]*\t){4}1\t'\'' && echo REACH-BYTE-LANDMARK'
SAB_REACH_EXPECT="REACH-BYTE-LANDMARK"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        || (best->n == 0 && !rb_set_bounded_landmark(set))'
SAB_AFTER='        || (best->n == 0)   /* SABOTAGE S3481 */'
