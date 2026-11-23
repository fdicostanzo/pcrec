#!/usr/bin/env bash
# S3383 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-L4 (span_arms §5.7, the reach leak): at reach 0 an `rg` is kept at TOP.
# Sound, so no answer moves: the listing is the detector.
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the listing cells.
SAB_ID="S3383-top-keeps-rg-at-reach0"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='TOP keeps a trailing lookahead'\''s guard at reach 0, so `bar(?=baz)` lists `barbaz` (sound for every reader; L2'\''s value, not L1'\''s)'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3383."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''bar(?=baz)'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}626172\t'\'' && echo REACH-WL4'
SAB_REACH_EXPECT="REACH-WL4"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    *run = rb_top(w, &v->runs, &v->set, cons_lo, cons_hi);'
SAB_AFTER='    if (v->runs.all && v->runs.rg.n) { *run = rn_app(v->runs.best, v->runs.rg); *cons_lo = 0; *cons_hi = run->n; } else *run = rb_top(w, &v->runs, &v->set, cons_lo, cons_hi);   /* SABOTAGE S3383 */'
# RE-ANCHORED 2026-11-21 (lane l3r66, review r66 EMIT-3): `rb_top` takes the root's set. Intent unchanged.
# RE-ANCHORED 2026-11-20 (lane l3feat2, span_arms L3 feature): TOP returns the consumed extent beside the run (D-5);
# the plant states the kept `rg` as consumed. Intent unchanged.
