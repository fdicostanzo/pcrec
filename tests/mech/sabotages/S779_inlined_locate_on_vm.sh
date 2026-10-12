#!/usr/bin/env bash
# S779 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- the inlined body asks LOCATE on CAND_ROUTE_VM, so a hybrid never selects the walk.
# Detector: run_rev_end.sh: the hybrid witnesses read `unanchored`.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the hybrid's inlined walk is now F1 on `(\d+)$`; reach reads its form.
SAB_ID='S779-inlined-locate-on-vm'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='the inlined body asks LOCATE on CAND_ROUTE_VM, so a hybrid never selects the walk'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S779.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "(\\d+)$" | grep -F "form=one-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_artifact_has_dfa_scan(cx) ? cand_route_of(cx) : CAND_ROUTE_VM;'
SAB_AFTER='    return pcrec_artifact_has_dfa_scan(cx) && cx->job->fit.chosen == ENGM_DFA
           ? cand_route_of(cx) : CAND_ROUTE_VM;   /* SABOTAGE S779 */'
