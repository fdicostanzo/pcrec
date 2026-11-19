#!/usr/bin/env bash
# S3374 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-F4 (span_arms §5.7, T2 row 1): a min-0 repeat of a width-0 body keeps
# the body's guards instead of being the plain unit.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3374-min0-width0-rep-keeps-guard"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a min-0 repeat of a lookahead keeps the lookahead'\''s guard, so `x(?=ab)?a[bc]` narrows `[bc]` to `b` and deletes `xac`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3374."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''x(?=ab)?a[bc]'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}786162/fffffe\t'\'' && echo REACH-WF4'
SAB_REACH_EXPECT="REACH-WF4"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (m == 0) rb_init(v);'
SAB_AFTER='    if (m == 0) { rb_init(v); v->runs.lg = b->runs.lg; v->runs.rg = b->runs.rg; }   /* SABOTAGE S3374 */'
