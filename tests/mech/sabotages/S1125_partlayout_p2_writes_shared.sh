#!/usr/bin/env bash
# S1125 ([ENTRY-TABLE] E1, lane e1fix; review r1 F1; compound_entries.md
# §3.8 F3) -- P2 WRITES AN ATTRIBUTE. P2 must leave a body gcc cannot copy
# exactly as the default artifact has it; planted, it writes the shared
# layout, so every control on any class strips IPA from every attempt-route
# prefilter. Seen by tests/partlayout's p2 check (byte identity to the
# default under controls on other classes) and the evaluator's P2 head
# check.
SAB_ID="S1125-partlayout-p2-writes-shared"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='row P2 writes the shared layout instead of nothing, so a control on any class rewrites every attempt-route prefilter'"'"'s head'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:3fail/45pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1125."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" --features all --part-layout=find:inline --emit-facts --pattern "^(a)b" | tr "\t" " "'
SAB_REACH_EXPECT='P2 not-copyable as-emitted'
SAB_BEFORE='      0,                 true,  pr_not_copyable },'
SAB_AFTER='      PCREC_PART_SHARED, true,  pr_not_copyable },   /* SABOTAGE S1125 */'
