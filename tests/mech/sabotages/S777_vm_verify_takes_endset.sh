#!/usr/bin/env bash
# S777 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- LR-S3: a clamped tie reaches the VM's verify-at, its window end max(D) = n instead of the priority end.
# Detector: the window twin: the lazy tie `(\s+?){2}$`'s window end differs; run_rev_end.sh's hybrid tie witness loses its relocate arm.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the clamped ties now finish by `prio-const`; the hybrid tie that still
# reaches the VM route's FINISH for ENDSET is the state-dependent
# `(?:(\s+)|x(\s*?))$` (run_rev_end.sh's relocate witness).
SAB_ID='S777-vm-verify-takes-endset'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revtwin revend'
SAB_DESC='LR-S3: a clamped tie reaches the VM'\''s verify-at, its window end max(D) = n instead of the priority end'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S777.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?:(\\s+)|x(\\s*?))$" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && "$PCREC" --emit-facts --features all --pattern "(?:(\\s+)|x(\\s*?))$" | grep -qF "prio=state-dependent" && echo REACH-HYB-TIE'
SAB_REACH_EXPECT='REACH-HYB-TIE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },
      .u.finish = { CAND_FIN_VERIFY } },'
SAB_AFTER='                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT, CAND_HAND_ENDSET } },   /* SABOTAGE S777 */
      .u.finish = { CAND_FIN_VERIFY } },'
