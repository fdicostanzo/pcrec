#!/usr/bin/env bash
# S3372 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-N1 (span_arms §5.7, ITEM): a lookbehind nested in a lookahead has its
# guard flattened into the lookahead's head at offset 0.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3372-nested-lg-flattened-into-head"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a lookahead body'\''s own lookbehind guard is flattened into its head at offset 0, so `ab[xy][xy](?=(?<=xx)y)[xy]` narrows the wrong positions and deletes `abxxy`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3372."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''ab[xy][xy](?=(?<=xx)y)[xy]'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}6162787879\t'\'' && echo REACH-WN1'
SAB_REACH_EXPECT="REACH-WN1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'        u->rg = g;\n        u->lg = br->lg;'
SAB_AFTER=$'        u->rg = br->lg.n ? rn_app(br->lg, g) : g;   /* SABOTAGE S3372 */\n        u->lg = rn_none();'
