#!/usr/bin/env bash
# S740 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- the match-here entry's FINISH ask drops its hand (asks with 0). A hand is MANDATORY on a FINISH ask (locate_finish.md §2.2): no take cell matches 0.
# Detector: tests/codegen/run_cand_oracle.sh: the trace build aborts `finish-no-hand FINISH` at the first FINISH ask, on every DFA witness (MEASURED by plant at landing: 29 checks fail). In the default build the walk selects no row and every DFA compile crashes.
SAB_ID='S740-finish-hand-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle codegen'
SAB_DESC='the match-here FINISH ask passes hand 0: the hand-mandatory check aborts (trace build), the walk selects no row (default build)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S740.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "#define RX_DFA_MATCH \"unwrapped\"" "$REACH_TMP/o.c" && echo REACH-FINISH'
SAB_REACH_EXPECT='REACH-FINISH'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2): the match-here hand is dfa_match_hand(cx); the plant still passes hand 0. Intent
# unchanged.
SAB_BEFORE='                  .hand = dfa_match_hand(cx) };'
SAB_AFTER='                  .hand = 0 };   /* SABOTAGE S740: the hand dropped */'
