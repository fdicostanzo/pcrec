#!/usr/bin/env bash
# S3077 ([REQ-PAST-LAST], lane rpfix, review r2-reqpast CHK-5) -- A DFA-SCAN
# ARTIFACT TAKES THE ATTEMPT-LOOP ROWS. The shared conjunct
# `pcrec_artifact_has_dfa_scan` keeps a VM hybrid (`([^@ ]+)@x`: its
# prefilter is a DFA scan with a re-entry of its own) off the attempt-loop
# handoff; the plant drops it, so the hybrid stamps "unbounded". NO ANSWER
# MOVES; the hybrid decline pin of tests/memfn/run_handoff_reach.sh is the
# detector (arm memfnreach).
SAB_ID='S3077-unbounded-hybrid-admitted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the attempt-loop handoff rows are admitted on an artifact whose prefilter is a DFA scan (a VM hybrid)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rpfix_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3077.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: ([^@ ]+)@x (hybrid, unbounded K): declined (RX_REQ_HANDOFF none)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_artifact_has_dfa_scan(cx) || !(cand_path_members(cx) & CAND_MVM))'
SAB_AFTER='    if (!(cand_path_members(cx) & CAND_MVM))   /* SABOTAGE S3077 */'
