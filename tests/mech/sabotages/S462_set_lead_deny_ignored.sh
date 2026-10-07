#!/usr/bin/env bash
# S462 ([K82], lane k82fix) -- `-fno-req-set-lead` IS IGNORED.
#
# Every optimization carries its own deny (D144 item 4), and bit 45 is the
# set-leads row's: denied, the run pre-check is the abi-59 program. This
# plant drops the row's deny bit, so the flag is accepted and does nothing.
# Detector: run_prechecks.sh §5.11's `-fno-req-set-lead` row (lead "-" reads
# "61") and §5.8/§5.9's deny rows. The registry's axes check does NOT see it
# (measured: registry 0 fail): `--list-axes` walks the same row, so its deny
# column empties with the plant -- a control sharing its source.
# [START-TABLE] C4 (lane stc4, 2026-10-07) RE-AIMED: `req_admits[]` is deleted
# into `cand_rows[]`'s PRESENCE slot, so the plant drops the same deny bit from
# the same row there (intent unchanged: the flag is accepted and does nothing).
# It is now the same edit as S596's; the two rows differ in their detector
# (this one the pre-check suite's deny cells, S596 the trace build's oracle).
SAB_ID="S462-set-lead-deny-ignored"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="the set-leads row's deny bit is dropped from its table row, so -fno-req-set-lead is accepted and changes nothing"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S462."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:user|USER)[ \\t]*=" && grep -q "^#define RX_REQ_RUN \"55534552@0/dfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 61," "$REACH_TMP/o.c" && echo REACH-SET-LEADS'
SAB_REACH_EXPECT="REACH-SET-LEADS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "set-leads", PCREC_NO_REQ_SET_LEAD, req_set_leads_applies },'
SAB_AFTER='    { .c = { "set-leads", 0 /* SABOTAGE S462 */, req_set_leads_applies },'
