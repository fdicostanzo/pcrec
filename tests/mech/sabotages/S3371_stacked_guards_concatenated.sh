#!/usr/bin/env bash
# S3371 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-S1 (span_arms §5.7, CAT-EDGE stacking): stacked leftovers are
# concatenated (`acc` ++ `cc`), not met at equal offsets.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3371-stacked-guards-concatenated"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='two stacked lookbehind guards are CONCATENATED instead of met at equal offsets, so `[ac][ac]cc(?<=acc)(?<=cc)d` claims `ccccd` and deletes `caccd`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3371."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''[ac][ac]cc(?<=acc)(?<=cc)d'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}6161636364/fdffffffff\t'\'' && echo REACH-WS1'
SAB_REACH_EXPECT="REACH-WS1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.lg = l.all && lleft.n ? rn_guard_meet_last(w, l.lg, lleft, &empty) : l.lg;'
SAB_AFTER='    o.lg = l.all && lleft.n ? rn_app(l.lg, lleft) : l.lg;   /* SABOTAGE S3371 */'
