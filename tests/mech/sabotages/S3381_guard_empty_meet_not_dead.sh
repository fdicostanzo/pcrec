#!/usr/bin/env bash
# S3381 (lane l1feat, 2026-11-19; span_arms L1, docs/design/span_arms.md §5.7 and
# §14.4 L1) -- W-D2 (span_arms §5.7): the guard-vs-guard branch drops positions without
# setting DEAD (SIM-2's corner).
# Detector: tests/codegen/run_facts_checks.sh [facts-look], the listing cells.
# REACH re-aimed (lane l3tri, 2026-11-20): since span_arms L3 (BACK) W-D2's value is
# `6263` (the lookbehind's `bc` at K -1), no longer `none`; the probe reads only the
# `dead` annotation, which is the site's output (any run is sound for a never-match).
SAB_ID="S3381-guard-empty-meet-not-dead"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC='the guard-against-guard EMPTY-MEET branch drops positions without setting NEVER, so `(?<=ab)(?<=cb)c` is not listed `dead`'
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/l1feat_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3381."
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=ab)(?<=cb)c'\'' | grep -qP '\''^byte\treq_whole_run\t([^\t]*\t){5}dead\t'\'' && echo REACH-WD2'
SAB_REACH_EXPECT="REACH-WD2"
# RE-AIMED 2026-11-20 (lane l3r65, review r65 A): by default W-D2 lists BASE's `none` again (BACK does not
# displace the consumed `c` at K 0 where a forward scan may re-enter); `6263` under `--engine=vm`.
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'            *empty = true;\n            if (guard) { n = k; break; }'
SAB_AFTER=$'            if (!guard) *empty = true;   /* SABOTAGE S3381 */\n            if (guard) { n = k; break; }'
