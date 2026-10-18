#!/usr/bin/env bash
# S1118 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.4.2) -- THE /held
# MARKER IS DROPPED. A request a constraint row (P1-P3) holds is a selection
# outcome, reported in `<PREFIX>_PART_LAYOUT` as `CLASS=V/held`; planted, the
# stamp says the request was honoured. Seen by the hand-written held stamps
# (fixtures `held-compound`, `constraint-*`) and the evaluator's expected
# stamp.
SAB_ID="S1118-partlayout-held-dropped"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='the stamp drops /held, so a request a constraint row held reads as honoured'
SAB_DOC_FIGURE="OWED: the solo mech run (docs/dev/lanes/e1_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline"'
SAB_BEFORE='                        !any ? "/none" : held ? "/held" : "");'
SAB_AFTER='                        !any ? "/none" : held ? "" : "");   /* SABOTAGE S1118 */'
