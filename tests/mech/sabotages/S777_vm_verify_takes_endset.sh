#!/usr/bin/env bash
# S777 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- LR-S3: a clamped tie reaches the VM's verify-at, its window end max(D) = n instead of the priority end.
# Detector: the window twin: the lazy tie `(\s+?){2}$`'s window end differs; run_rev_end.sh's hybrid tie witness loses its relocate arm.
SAB_ID='S777-vm-verify-takes-endset'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revtwin revend'
SAB_DESC='LR-S3: a clamped tie reaches the VM'\''s verify-at, its window end max(D) = n instead of the priority end'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S777.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\s+?){2}$" && grep -q "search_from = revend_start;" "$REACH_TMP/o.c" && echo REACH-HYB-TIE'
SAB_REACH_EXPECT='REACH-HYB-TIE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },
      .u.finish = { CAND_FIN_VERIFY } },'
SAB_AFTER='                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT, CAND_HAND_ENDSET } },   /* SABOTAGE S777 */
      .u.finish = { CAND_FIN_VERIFY } },'
