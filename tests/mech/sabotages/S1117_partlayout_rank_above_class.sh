#!/usr/bin/env bash
# S1117 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.4, §3.6
# "precedence") -- THE THRESHOLD BEATS A CLASS VALUE. A class value (P4-P6) is
# absolute and comes before the rank threshold (P7); planted, P7 is moved
# above them, so `--part-layout=prefilter:shared --part-inline-rank=R2`
# inlines the prefilter it was told to keep shared. Seen by the hand fixture
# `class-beats-rank` (P4 expected) and the evaluator's same row.
SAB_ID="S1117-partlayout-rank-above-class"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='row P7 (the rank threshold) is walked before the class-value rows P4-P6, so a part whose class value is shared or auto is inlined by a threshold that should not reach it'
SAB_DOC_FIGURE="MEASURED by lane e1 2026-10-18 (one mech row, solo, Linux dev box, at b57d43101^): partlayout:6fail/40pass, DETECTED, against a clean 0fail/46pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1117."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" --features all --part-layout=prefilter:shared --part-inline-rank=R2 --emit-facts --pattern "(a)b" | tr "\t" " "'
SAB_REACH_EXPECT='P4 class-shared shared'
SAB_BEFORE='    { "P4",  "class-shared",    "the part'"'"'s class value is shared",
      PCREC_PART_SHARED, false, pr_cls_shared },
    { "P5",  "class-inline",    "the part'"'"'s class value is inline",
      PCREC_PART_INLINE, false, pr_cls_inline },
    { "P6",  "class-auto",      "the part'"'"'s class value is auto",
      PCREC_PART_AUTO,   false, pr_cls_auto },
    { "P7",  "rank-hot",        "the threshold is a rank; the part'"'"'s rank is at or above it",
      PCREC_PART_INLINE, false, pr_rank_hot },
'
SAB_AFTER='    { "P7",  "rank-hot",        "the threshold is a rank; the part'"'"'s rank is at or above it",
      PCREC_PART_INLINE, false, pr_rank_hot },   /* SABOTAGE S1117: P7 ahead of P4-P6 */
    { "P4",  "class-shared",    "the part'"'"'s class value is shared",
      PCREC_PART_SHARED, false, pr_cls_shared },
    { "P5",  "class-inline",    "the part'"'"'s class value is inline",
      PCREC_PART_INLINE, false, pr_cls_inline },
    { "P6",  "class-auto",      "the part'"'"'s class value is auto",
      PCREC_PART_AUTO,   false, pr_cls_auto },
'
