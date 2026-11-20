#!/usr/bin/env bash
# S3378 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-T1 (span_arms §5.7, guard bound): the lookbehind's guard grown by its
# body's own `lg` keeps its first 32 positions instead of its last.
# Detector: the harness on tests/litscan/spanarms.rxt (both engines), libpcre2-8's answers.
SAB_ID="S3378-growing-lg-keeps-first"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/spanarms.rxt"
SAB_DESC='a growing lookbehind guard keeps its FIRST 32 positions, so W-T1'\''s run is shifted two places and the pre-check deletes the match'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3378."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''[ac]{17}[bc]{17}(?<=(?<=ca{16})b{17}).'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}6161616161616161616161616161616161626262626262626262626262626262/fdfdffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff\t'\'' && echo REACH-WT1'
SAB_REACH_EXPECT="REACH-WT1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            g = rn_pre(br->lg, g);'
SAB_AFTER='            g = rn_app(br->lg, g);   /* SABOTAGE S3378 */'
