#!/usr/bin/env bash
# S1112 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.4 P2, §2.1 H1) --
# THE NOT-COPYABLE ROW IS DROPPED. P2 holds a body gcc can never copy (the
# DFA attempt route's label table) ahead of every control row; planted, a
# `compound:inline` request writes always_inline on split's F part and the
# artifact no longer compiles ("can never be copied"). Seen by the evaluator
# (the controlled artifact refuses to build) and the held fixtures.
SAB_ID="S1112-partlayout-p2-dropped"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='row P2 never holds, so an inline control writes always_inline on a label-table body (split'"'"'s F part, the attempt-route prefilter) and the artifact does not compile'
SAB_DOC_FIGURE="MEASURED by lane e1 2026-10-18 (one mech row, solo, Linux dev box, at b57d43101^): partlayout:6fail/40pass, DETECTED, against a clean 0fail/46pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1112."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline"'
SAB_BEFORE='{ (void)pl; return !p->copyable; }'
SAB_AFTER='{ (void)pl; (void)p; return false; }   /* SABOTAGE S1112 */'
