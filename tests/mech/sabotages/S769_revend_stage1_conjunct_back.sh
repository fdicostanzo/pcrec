#!/usr/bin/env bash
# S769 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §4.3 (stage 2, D156 addendum 1 Q2); docs/dev/lanes/revbuild_report.md) -- stage 1's conjunct restored: a VM hybrid's inlined body keeps the composite.
# Detector: run_rev_end.sh: the hybrid witnesses `(\s+){2}$`, `(\d+)$` read `unanchored`.
SAB_ID='S769-revend-stage1-conjunct-back'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='stage 1'\''s conjunct restored: a VM hybrid'\''s inlined body keeps the composite'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S769.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\d+)$" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && grep -q "revend_seed" "$REACH_TMP/o.c" && echo REACH-HYB-WALK'
SAB_REACH_EXPECT='REACH-HYB-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_fact_end_pin(s->cx) != PCREC_EPIN_NONE;               /* R1 */'
SAB_AFTER='    return pcrec_fact_end_pin(s->cx) != PCREC_EPIN_NONE &&
           cand_finish_of(s->cx) != CAND_ROUTE_VM;   /* SABOTAGE S769: stage 1 again */'
