#!/usr/bin/env bash
# S1118 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.4.2) -- THE /held
# MARKER IS DROPPED. A request a constraint row (P1-P3) holds is a selection
# outcome, reported in `<PREFIX>_PART_LAYOUT` as `CLASS=V/held`; planted, the
# stamp says the request was honoured. Seen by the hand-written held stamps
# (fixtures `constraint-*`) and the evaluator's expected
# stamp.
SAB_ID="S1118-partlayout-held-dropped"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='the stamp drops /held, so a request a constraint row held reads as honoured'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:9fail/39pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1118."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "^(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline/held"'
SAB_BEFORE='                        !any ? "/none" : held ? "/held" : "");'
SAB_AFTER='                        !any ? "/none" : held ? "" : "");   /* SABOTAGE S1118 */'
