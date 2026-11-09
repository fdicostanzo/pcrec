#!/usr/bin/env bash
# S1908 (lane sae1, 2026-11-09; span_arms E1, the `harness:` token,
# docs/spec/facts_listing.md §4.1.3¶4a) -- A DERIVED FACT DOES NOT INHERIT
# THE RESTORED ARM.
#
# A fact derived from a walk fact the restored arm can change (`req_run`,
# `req_byte`) names the arm because `pf_ask` ORs each asked fact's arms into
# the asking derivation's (src/facts/facts.c). This plant drops the OR, so the
# derived rows list their rate token as if no arm were restored. Detector:
# tests/codegen/run_facts_checks.sh [facts-arm].
SAB_ID="S1908-arm-token-not-inherited"
SAB_FILE="src/facts/facts.c"
SAB_SUITES="facts"
SAB_DESC="a fact derived from a walk fact under a restored arm does not inherit the arm, so its listing row hides that its value was derived under the harness lever"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1908."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=empty --emit-facts --pattern "abcd(?:\\b)*efgh" | grep -qP "^byte\treq_run\t.*\tharness:empty\t" && echo REACH-ARM-INHERITED'
SAB_REACH_EXPECT="REACH-ARM-INHERITED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    cx->job->pf.arms_seen |= cx->job->pf.why[f].arms;'
SAB_AFTER='    (void)0;   /* SABOTAGE S1908 */'
