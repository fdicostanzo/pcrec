#!/usr/bin/env bash
# S1930 (lane sartie, 2026-11-10; span_arms R1's tie rule, docs/design/span_arms.md
# §3.7; Frank's ruling 2026-11-10) -- THE RARITY ROW IGNORES THE `tie` ARM.
#
# The run choice (src/facts/req.c `rn_choice_rows`) passes its rarity row over
# under `--harness=restore=tie`, so the predecessor's choice (the first run at
# equal information) is what runs. This plant drops the row's arm: under the
# lever `abcd.efgh` keeps the rarer run `abcd`, the arm restores nothing.
# Detector: tests/codegen/run_facts_checks.sh [facts-tie].
SAB_ID="S1930-tie-arm-not-restored"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the run choice's rarity row carries no restored arm, so the harness lever's predecessor choice at an equal-information tie is never produced"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sartie_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1930."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=tie -p rx --emit-main -o /dev/stdout --pattern "abcd.efgh" | grep -q "RX_REQ_RUN \"65666768@" && echo REACH-TIE-ARM-RESTORES'
SAB_REACH_EXPECT="REACH-TIE-ARM-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { rn_rarer,     PCREC_WALK_ARM(TIE) },'
SAB_AFTER='    { rn_rarer,     0 },   /* SABOTAGE S1930 */'
