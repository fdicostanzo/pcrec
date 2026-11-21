#!/usr/bin/env bash
# S467 ([K82] (B), lane k82hbuild) -- AN UNBOUNDED RUN IS HANDED OFF.
#
# Answer-equivalent by construction (lo is search_from whenever K is
# saturated). Detector: run_prechecks.sh §5.12a's unbounded rows and §5.12c's
# bounded check over its population.
SAB_ID="S467-unbounded-handed-off"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC='the handoff row'\''s BOUNDED conjunct is dropped, so an unbounded run is handed off at the saturated K (2^40): the subtraction never fires and every answer is unchanged, so only the structural check can see it'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S467.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''a.*?(?i:select)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "none"'\'' "$REACH_TMP/o.c" && echo REACH-UNBOUNDED-NONE'
SAB_REACH_EXPECT='REACH-UNBOUNDED-NONE'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|^a\.\*\?\(\?i\)select%|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!pcrec_bound_bounded(k)) return false;'
SAB_AFTER='    if (!pcrec_bound_stated(k)) return false; /* SABOTAGE S467 */'
# RE-ANCHORED 2026-11-20 (lane l3build, span_arms L3 RM-2, D-7): K is a `PfBound` (state +
# signed value); the conjunct is the bounded predicate, and the plant keeps only "stated",
# so an unbounded landmark is handed off (the DFA route then stamps REQ_HANDOFF "unbounded"
# and takes the no-move branch; [5.12c] reads it as before). Intent unchanged.
