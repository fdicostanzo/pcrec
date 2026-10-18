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
# [MEMFN] R17-b' B3b (lane b3b, 2026-10-18) RE-AIMED: bit 45 is RETIRED, the
# set-leads row is the memfn kit's PRES row P4 and its deny the kit's
# `--memfn=no-pres-set-lead`; `-fno-req-set-lead`/PCREC_NO_REQ_SET_LEAD stay
# that deny's ALIAS, rewritten in the compile driver (Q-R17P-19; the kit
# manager's Q-19: never a silent no-op). The plant drops the REWRITE, so the
# flag is accepted, read by no row, and changes the emitted program nothing
# (intent unchanged: the flag is accepted and does nothing). Detector
# unchanged: run_prechecks.sh's `-fno-req-set-lead` rows.
SAB_ID="S462-set-lead-deny-ignored"
SAB_FILE="src/core/compile.c"
SAB_SUITES="prechecks"
SAB_DESC="the compile driver no longer rewrites PCREC_NO_REQ_SET_LEAD (bit 45, retired) to the kit deny no-pres-set-lead, so -fno-req-set-lead is accepted and changes nothing"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S462."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:user|USER)[ \\t]*=" && grep -q "^#define RX_REQ_RUN \"55534552@0/dfdfdfdf\"" "$REACH_TMP/o.c" && grep -q "!memchr(subject + search_from, 61," "$REACH_TMP/o.c" && echo REACH-SET-LEADS'
SAB_REACH_EXPECT="REACH-SET-LEADS"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (defo.flags & PCREC_NO_REQ_SET_LEAD) {'
SAB_AFTER='    if (0 /* SABOTAGE S462 */ && (defo.flags & PCREC_NO_REQ_SET_LEAD)) {'
