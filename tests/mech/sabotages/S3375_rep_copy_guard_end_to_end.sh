#!/usr/bin/env bash
# S3375 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-RG (span_arms §5.7, REP through CAT): a copy's `rg` is laid end to end
# with the next copy instead of met with its first positions.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3375-rep-copy-guard-end-to-end"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a repeat copy'\''s lookahead guard is laid end to end with the next copy, so `(?:abc(?=ab)){2}` claims `abcababc` and deletes `abcabc`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3375."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?:abc(?=ab)){2}'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}616263616263\t'\'' && echo REACH-WRG'
SAB_REACH_EXPECT="REACH-WRG"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int i = 0; i < c; i++) o = rr_cat(w, b, o);'
SAB_AFTER='    for (int i = 0; i < c; i++) { RbRuns bb = b; if (i && b.all && b.rg.n) { bb.head = bb.tail = bb.best = rn_app(b.head, b.rg); bb.rg = rn_none(); } o = rr_cat(w, bb, o); }   /* SABOTAGE S3375 */'
