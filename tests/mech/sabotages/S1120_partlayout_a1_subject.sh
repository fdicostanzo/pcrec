#!/usr/bin/env bash
# S1120 ([ENTRY-TABLE] E1, lane e1fix; compound_entries.md §3.1 A1, §3.6
# "A1 disjointness", review r1 Q4) -- AN OWNED FUNCTION IN A CONTROL CLASS.
# `subject_class` is the one source of a record's class; planted, it names
# A1's `_search_run` a prefilter subject, so a control would lay out the VM
# entry chain's body its rung owns. The render refuses (a subject record
# whose head carries no mark: `_search_run`'s head is the VM emitter's, never
# marked), so every T3 compile of a VM artifact fails: seen by the evaluator,
# the fixtures, disjoint and neutral.
SAB_ID="S1120-partlayout-a1-subject"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='subject_class names A1'"'"'s _search_run a prefilter subject, so a control lays out a function the VM entry rung owns'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:36fail/12pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1120."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" --features all --vm-entry-shape=4 --part-residual=shared --emit-facts --pattern "(a)b" | tr "\t" " "'
SAB_REACH_EXPECT='byte search_run owned 4 R3 - P1 owned owner 0'
SAB_BEFORE='static int subject_class(PcrecEntry e)
{
'
SAB_AFTER='static int subject_class(PcrecEntry e)
{
    if (e == PCREC_ENTRY_SEARCH_RUN) return PCREC_PART_PREFILTER;   /* SABOTAGE S1120 */
'
