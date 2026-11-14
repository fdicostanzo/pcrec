#!/usr/bin/env bash
# S3131 (lane r1on, 2026-11-14; [RUN-POS-SET] stage 2a rule (1), the walk arm
# `alt`, src/facts/walk_arms.def) -- ROW 1 IGNORES THE `alt` ARM.
#
# `rr_alt_rows` passes row 1 over under `--harness=restore=alt`, so the
# answer-identity sweep (tests/axes/run_axes.sh's internal arm) compares the
# default against the form before rule (1). This plant drops the row's arm:
# the lever restores nothing and the sweep compares the default with itself.
# Detector: run_facts_checks.sh [facts-ahead]'s `alt` twins.
SAB_ID="S3131-alt-arm-not-restored"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="rr_alt row 1 carries no restored arm, so --harness=restore=alt still applies rule (1) and the answer-identity arm compares the default with itself"
SAB_DOC_FIGURE="DESIGNED by lane r1on 2026-11-14; MEASURED by the lane's mechrows cloud run (docs/dev/lanes/r1on_report.md OWED). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3131."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=alt -fno-altcls-merge -fno-altcls-factor -p rx --emit-main -o /dev/stdout --pattern "xy(?:ab|ac)zw" | grep -qE "RX_REQ_RUN \"61627a77(@[0-9]+)?/fffeffff\"" && echo REACH-ALT-ARM-RESTORES'
SAB_REACH_EXPECT="REACH-ALT-ARM-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { rr_alt_union, PCREC_WALK_ARM(ALT) },'
SAB_AFTER='    { rr_alt_union, 0 },   /* SABOTAGE S3131 */'
