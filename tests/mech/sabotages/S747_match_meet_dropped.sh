#!/usr/bin/env bash
# S747 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- the meet `caller ⊓ body` dropped (LR-G8): the match-here entry asks FINISH for `AT` even on an `empty` body, so `verify-at` is selected wherever the anchored machine was built and the empty engine's `_match` stops being the search-filter wrapper.
# Detector: tests/codegen/run_anchored_match.sh: `\B\b` stamps `unwrapped` where the empty engine's documented form is `search-filter`. MEASURED by plant at landing: 4 checks fail.
SAB_ID='S747-match-meet-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='anchoredmatch'
SAB_DESC='the match-here meet dropped: FINISH is asked AT on an empty body and DFA_MATCH reads unwrapped on empty artifacts'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S747.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\B\\b" && grep -qF "#define RX_DFA_SCAN \"empty\"" "$REACH_TMP/o.c" && echo REACH-EMPTY'
SAB_REACH_EXPECT='REACH-EMPTY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2): the meet is dfa_match_hand's one line; the plant still asks AT on an empty body. Intent
# unchanged.
SAB_BEFORE='    return dfa_engine_is_empty(cx) ? CAND_HAND_NOMATCH : CAND_HAND_AT;'
SAB_AFTER='    return CAND_HAND_AT;   /* SABOTAGE S747: the meet dropped */'
