#!/usr/bin/env bash
# S473 ([K82] (B), lane k82hbuild) -- `-fno-req-handoff` IS IGNORED.
#
# Detector: run_prechecks.sh §5.12j. NOT the registry suite: `--list-axes`
# walks the same row, so its deny column empties with the plant -- a control
# sharing its source (k82fix's S462 lesson).
SAB_ID="S473-deny-ignored"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the handoff row'\''s deny bit is dropped from its table row, so -fno-req-handoff is accepted and changes nothing'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S473.'
SAB_REACH='"$PCREC" --features all -p rx -fno-req-handoff -o "$REACH_TMP/o.c" --pattern '\''(?i)cat'\'' && grep -q '\''^#define RX_REQ_HANDOFF "none"'\'' "$REACH_TMP/o.c" && echo REACH-DENY'
SAB_REACH_EXPECT='REACH-DENY'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|fno-req-handoff|2'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { { "handoff",            PCREC_NO_REQ_HANDOFF, req_handoff_applies }, REQ_USE_HANDOFF,'
SAB_AFTER='    { { "handoff",            0 /* SABOTAGE S473 */, req_handoff_applies }, REQ_USE_HANDOFF,'
