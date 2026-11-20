#!/usr/bin/env bash
# S3370 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-A1 (span_arms §5.7, ALT): the alternation keeps a guard only ONE branch
# carries instead of the guards both imply.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3370-alt-keeps-one-branch-guard"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='ALT keeps a guard only one branch carries, so `xy[ac]b(?:(?<=ab)b|c)` narrows `[ac]` to `a` and deletes `xycbc`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3370."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''xy[ac]b(?:(?<=ab)b|c)'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}7879616262/fffffdfffe\t'\'' && echo REACH-WA1'
SAB_REACH_EXPECT="REACH-WA1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    o.lg = rn_common_tail(w, l.lg, r.lg);'
SAB_AFTER='    o.lg = l.lg.n ? l.lg : r.lg;   /* SABOTAGE S3370 */'
