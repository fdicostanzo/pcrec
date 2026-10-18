#!/usr/bin/env bash
# S1127 ([ENTRY-TABLE] E1, lane e1fix; review r1 F8) -- THE HEAD-MARK
# TABLE'S SUBJECT ROW HOLDS FOR EVERY HEAD. Row M3 must mark only a head
# whose entry is a subject; planted, an exported search head (a DFA
# artifact's `<prefix>_search`, a compound part's own search) writes a mark
# with no subject record and the render refuses. Seen by the evaluator,
# fixtures, disjoint and neutral (controlled compiles refuse).
SAB_ID="S1127-partlayout-head-mark-any"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='head-mark row M3 holds for every head, so a non-subject search head writes a mark no record renders'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:4fail/44pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1127."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-residual=shared -o "$REACH_TMP/x.c" --pattern "^\s+|\s+$" && grep -h "RX_PART_LAYOUT\|^int rx_search(" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "residual=shared"
int rx_search('
SAB_BEFORE='{ (void)cx; return subject_class(e) >= 0; }'
SAB_AFTER='{ (void)cx; (void)e; return true; }   /* SABOTAGE S1127 */'
