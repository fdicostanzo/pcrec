#!/usr/bin/env bash
# S3382 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-D3, W-D4, W-D6, W-D7's plant (span_arms §5.7): DEAD as ONE walk-level
# flag; any empty meet kills the root. (Two edits: the meet records the
# flag in a spare bit of the walk's lookahead depth, the exit reads it.)
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the listing cells.
SAB_ID="S3382-dead-as-one-walk-flag"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='NEVER is one walk-level flag: any empty meet anywhere lists the root dead, so the live `x(?:foo(?=bar)baz)?y`, `(?:foo(?=bar)baz|q)`, `(?:foo(?=bar)baz){0}x` and W-T1 are listed `dead`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3382."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''x(?:foo(?=bar)baz)?y'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){4}none\t\t'\'' && echo REACH-WD3'
SAB_REACH_EXPECT="REACH-WD3"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'            *empty = true;\n            if (guard) { n = k; break; }'
SAB_AFTER=$'            *empty = true; ((RbWalk *)w)->ahead |= 0x40000000;   /* SABOTAGE S3382 */\n            if (guard) { n = k; break; }'
SAB_FILE2="src/facts/req.c"
SAB_BEFORE2='    *never = v->runs.never;'
SAB_AFTER2='    *never = v->runs.never || (w->ahead & 0x40000000);   /* SABOTAGE S3382 */'
SAB_COUNT2=1
