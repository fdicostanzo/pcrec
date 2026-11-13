#!/usr/bin/env bash
# S3076 ([REQ-PAST-LAST], lane rpfix, review r2-reqpast CHK-2) -- THE ATTEMPT
# LOOP RE-ASKS FROM attempt_position + 1. The least hit the re-ask wants is at
# or after the attempt just begun; asking one byte later loses a hit that
# starts exactly there, so a match beginning at it is answered NOMATCH
# (`b*xx(?=q)` over "xxxq" from 0: 1-3 becomes no match). A WRONG ANSWER.
# Detector: tests/litscan/handoff_vm.rxt.
SAB_ID='S3076-reask-from-next-position'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff_vm.rxt'
SAB_DESC='the VM attempt loop'\''s re-ask of the pre-check starts at attempt_position + 1'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rpfix_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3076.'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''b*xx(?=q)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "unbounded"'\'' "$REACH_TMP/o.c" && grep -q '\''^ *if (landmark_position < attempt_position) {$'\'' "$REACH_TMP/o.c" && echo REACH-REASK-LO'
SAB_REACH_EXPECT='REACH-REASK-LO'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        .s = "subject", .n = "subject_length", .lo = posvar, .indent = indent,
        .on_miss = REQ_ON_MISS, .result = "landmark_position",'
SAB_AFTER='        .s = "subject", .n = "subject_length", .lo = posvar[0] == '\''a'\'' ? "attempt_position + 1" : posvar, .indent = indent,   /* SABOTAGE S3076 */
        .on_miss = REQ_ON_MISS, .result = "landmark_position",'
