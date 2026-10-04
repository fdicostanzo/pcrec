#!/usr/bin/env bash
# S462 ([K82], lane k82fix) -- `-fno-req-set-lead` IS IGNORED.
#
# Every optimization carries its own deny (D144 item 4), and bit 45 is the
# set-leads row's: denied, the run pre-check is the abi-59 program. This
# plant drops the row's deny bit, so the flag is accepted and does nothing.
# Detector: run_prechecks.sh §5.11's `-fno-req-set-lead` row (lead "-" reads
# "61") and §5.8/§5.9's deny rows; the registry's axes check reads the
# `--list-axes` deny column and goes red too.
SAB_ID="S462-set-lead-deny-ignored"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks registry"
SAB_DESC="the set-leads row's deny bit is dropped from its table row, so -fno-req-set-lead is accepted and changes nothing"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S462."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:user|USER)[ \\t]*=" && grep -q "^#define RX_REQ_RUN \"55534552@0/dfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 61," "$REACH_TMP/o.c" && echo REACH-SET-LEADS'
SAB_REACH_EXPECT="REACH-SET-LEADS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { { "set-leads",   PCREC_NO_REQ_SET_LEAD,  req_set_leads_applies   }, REQ_ADMIT_SET_LEADS,'
SAB_AFTER='    { { "set-leads",   0 /* SABOTAGE S462 */,  req_set_leads_applies   }, REQ_ADMIT_SET_LEADS,'
