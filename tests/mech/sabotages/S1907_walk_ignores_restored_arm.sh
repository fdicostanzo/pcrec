#!/usr/bin/env bash
# S1907 (lane sae1, 2026-11-09; span_arms E1, the walk-parameter table,
# docs/design/span_arms.md §3.7) -- THE WALK IGNORES ITS RESTORED ARMS.
#
# The harness lever's restored arms reach the walk through its parameter
# record (`ReqWalkParams.restored`). This plant drops them at the walk entry,
# so `make test-axes`' internal arm `--harness=restore=empty` silently compiles
# the new form and compares it with itself, while the listing still names the
# arm. Detector: tests/codegen/run_facts_checks.sh [facts-arm] (the run under
# the lever is the new one).
SAB_ID="S1907-walk-ignores-restored-arm"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the necessary-run walk drops the restored arms its parameter record carries, so the harness lever's old form is never produced while the listing still names the arm"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1907."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=empty --emit-facts --pattern "abcd(?:\\b)*efgh" | grep -qP "^byte\treq_whole_run\t.*\t65666768\tharness:empty\t" && echo REACH-ARM-RESTORES'
SAB_REACH_EXPECT="REACH-ARM-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    w->restored = p->restored;'
SAB_AFTER='    w->restored = 0;   /* SABOTAGE S1907 */'
