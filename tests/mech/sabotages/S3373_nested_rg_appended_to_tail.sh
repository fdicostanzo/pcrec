#!/usr/bin/env bash
# S3373 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-N2 (span_arms §5.7, ITEM): a lookahead nested in a lookbehind has its
# guard appended to the lookbehind's tail.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3373-nested-rg-appended-to-tail"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a lookbehind body'\''s tail is taken with its inner lookahead'\''s guard appended, so `[ac][ac](?<=ac(?=cc))cc` claims `cccc` and deletes `accc`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3373."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''[ac][ac](?<=ac(?=cc))cc'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}61636363\t'\'' && echo REACH-WN2'
SAB_REACH_EXPECT="REACH-WN2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'        u->lg = g;\n        u->rg = br->rg;'
SAB_AFTER=$'        u->lg = br->rg.n ? rn_app(g, br->rg) : g;   /* SABOTAGE S3373 */\n        u->rg = rn_none();'
