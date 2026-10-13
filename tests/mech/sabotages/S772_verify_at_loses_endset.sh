#!/usr/bin/env bash
# S772 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `search-from` takes ENDSET ahead of `verify-at` on CAND_ROUTE_DFA: a tie relocates where the anchored machine exists.
# Detector: run_rev_end.sh: `\s+$`/`\s*?$` read the relocate arm where the anchored one is expected.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# detectors: run_rev_end.sh's F0 tie witness (`\s+$` under
# -fno-rev-end-onewalk) and the F2 state-dependent `(?:\s+|x\s*?)$`, both of
# which expect the anchored arm. Reach: the latter's mark_prio.
SAB_ID='S772-verify-at-loses-endset'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='`search-from` takes ENDSET ahead of `verify-at` on CAND_ROUTE_DFA: a tie relocates where the anchored machine exists'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S772.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "(?:\\s+|x\\s*?)$" | grep -F "prio=state-dependent" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT, CAND_HAND_ENDSET },
                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },'
SAB_AFTER='      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT },   /* SABOTAGE S772 */
                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },'
