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
SAB_DOC_FIGURE="HAND-VALIDATED by lane e1 (2026-10-18, a git-archive copy of the e1 tree with the plant applied by tests/mech/lib/replace.py, rebuilt, and tests/partlayout/run_partlayout_tests.sh run against it): partlayout:21fail/20pass against a clean 0fail/41pass. The solo mech run is OWED (docs/dev/lanes/e1_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline"'
SAB_BEFORE='            if (!(set & pl->owned_inline & PCREC_ENTRY_BIT(f)) ||'
SAB_AFTER='            if (1 || !(set & pl->owned_inline & PCREC_ENTRY_BIT(f)) ||   /* SABOTAGE S1114 */'
