#!/usr/bin/env bash
# S3380 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-D1 (span_arms §5.7): the consumed-position EMPTY-MEET branch does not set
# DEAD.
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the listing cells.
SAB_ID="S3380-consumed-empty-meet-not-dead"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='the consumed-position EMPTY-MEET branch does not set NEVER, so `foo(?=bar)baz` is not listed `dead`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3380."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''foo(?=bar)baz'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}666f6f62617a\tdead\t'\'' && echo REACH-WD1'
SAB_REACH_EXPECT="REACH-WD1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'            *empty = true;\n            if (guard) { n = k; break; }'
SAB_AFTER='            if (guard) { *empty = true; n = k; break; }   /* SABOTAGE S3380 */'
