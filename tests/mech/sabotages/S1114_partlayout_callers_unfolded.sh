#!/usr/bin/env bash
# S1114 ([ENTRY-TABLE] E1, lane e1; compound_entries.md §3.2 `callers` [r3
# CE-8]) -- CALLERS ARE COUNTED WITHOUT FOLDING THE OWNER'S ALWAYS_INLINE
# FUNCTIONS. The VM hybrid's prefilter at the `inline` rung is called from
# `_search_run`, which A1 inlines into `_search` and `_search_in`: two
# callers. Planted, it has one, P3 holds every request on it, and nothing a
# control asks moves. Seen by the precedence fixtures (P4/P5/P7... read P3)
# and by the evaluator, whose expected callers come from the -fno-inline call
# graph with the owners' attributes folded.
SAB_ID="S1114-partlayout-callers-unfolded"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='callers(part) skips folding owned always_inline callers, so the inline-rung hybrid'"'"'s prefilter reads one caller and P3 holds every control on it'
SAB_DOC_FIGURE="MEASURED by lane e1fix 2026-10-18 (one mech row, solo, Linux dev box, at c572e9570): partlayout:26fail/22pass, DETECTED, against a clean 0fail/48pass. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1114."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" --features all --vm-entry-shape=4 --part-residual=shared --emit-facts --pattern "(a)b" | tr "\t" " "'
SAB_REACH_EXPECT='byte prefilter prefilter 4 R2 yes P8 residual-shared shared 0
byte search_run owned'
SAB_BEFORE='            if (!(set & pl->owned_inline & PCREC_ENTRY_BIT(f)) ||'
SAB_AFTER='            if (1 || !(set & pl->owned_inline & PCREC_ENTRY_BIT(f)) ||   /* SABOTAGE S1114 */'
