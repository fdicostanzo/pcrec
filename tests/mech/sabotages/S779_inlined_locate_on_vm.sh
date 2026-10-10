#!/usr/bin/env bash
# S779 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- the inlined body asks LOCATE on CAND_ROUTE_VM, so a hybrid never selects the walk.
# Detector: run_rev_end.sh: the hybrid witnesses read `unanchored`.
SAB_ID='S779-inlined-locate-on-vm'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='the inlined body asks LOCATE on CAND_ROUTE_VM, so a hybrid never selects the walk'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S779.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\d+)$" && grep -q "revend_seed" "$REACH_TMP/o.c" && echo REACH-HYB-WALK'
SAB_REACH_EXPECT='REACH-HYB-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_artifact_has_dfa_scan(cx) ? cand_route_of(cx) : CAND_ROUTE_VM;'
SAB_AFTER='    return pcrec_artifact_has_dfa_scan(cx) && cx->job->fit.chosen == ENGM_DFA
           ? cand_route_of(cx) : CAND_ROUTE_VM;   /* SABOTAGE S779 */'
