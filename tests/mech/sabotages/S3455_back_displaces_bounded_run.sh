# S3455 (lane l3r65, 2026-11-20; span_arms L3, docs/design/span_arms.md §14.4 L3's REV 3.3 addendum,
# review r65 A) -- TOP's BACK row's `displaces` column is passed over, so on a compile that may re-enter
# a forward scan a BACK run displaces a consumed run at a bounded K: `(?<=qz)x?a:` lists `qz` at -2
# (an EMPTY consumed extent) where the pick rule keeps `a:` at 1, and the forward scan's re-entry,
# declined at K < 0, is lost (the x10 shape). NO ANSWER MOVES (both runs are sound).
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the default-route cells.
SAB_ID="S3455-back-displaces-bounded-run"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='TOP'\''s BACK row displaces a consumed run at a bounded K (its displaces column passed over), so the forward re-entry is lost to the K < 0 decline'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l3r65_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3455."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=qz)x?a:'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}613a\t'\'' && echo REACH-A'
SAB_REACH_EXPECT="REACH-A"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (rb_top_rows[i].displaces(w, &root->best, set, clo, chi) && rn_cmp(w, &best, &cand) < 0) {'
SAB_AFTER='        if (rn_cmp(w, &best, &cand) < 0) {   /* SABOTAGE S3455 */'
# RE-ANCHORED 2026-11-21 (lane l3r66, review r66 EMIT-3): `displaces` takes the root's set. Intent unchanged.
