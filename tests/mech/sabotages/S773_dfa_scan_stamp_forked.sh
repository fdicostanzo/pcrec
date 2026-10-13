#!/usr/bin/env bash
# S773 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- `<PREFIX>_DFA_SCAN` is a second predicate (the pin and the route), not LOCATE's selection.
# Detector: run_rev_end.sh (the denied build still stamps `rev-end`) and run_dfa_stamps.sh (the stamp against the text).
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# reach reads any form row (`\s+$`: tagged).
SAB_ID='S773-dfa-scan-stamp-forked'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend dfastamps'
SAB_DESC='`<PREFIX>_DFA_SCAN` is a second predicate (the pin and the route), not LOCATE'\''s selection'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S773.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s+$" | grep -F "form=tagged" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return cand_locate_of(cx)->u.locate.scan[cand_route_of(cx)];'
SAB_AFTER='    if (pcrec_fact_end_pin(cx) != PCREC_EPIN_NONE && cand_route_of(cx) == CAND_ROUTE_DFA)
        return "rev-end";   /* SABOTAGE S773: the stamp forked from the selection */
    return cand_locate_of(cx)->u.locate.scan[cand_route_of(cx)];'
