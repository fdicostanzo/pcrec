#!/usr/bin/env bash
# S1160 ([DD-11.5] P2a SP-11, lane ctxbuild; A1) -- A1's PLANT: `sides_of` sets
# `left_abs` from `bot_ok` in BOTH directions. Under R1's row gate only an
# absent-PREV-reading row reads `left_abs`, and every such row routes the
# pattern to ENG_ATTEMPT, which builds no reverse machine, so no witness can
# reach the plant (ctx_span.md §4.2.3); a reverse machine that ever met such a
# row is refused by the closure's routing assertion. DECLARED UNREACHED.
SAB_ID="S1160-reverse-left-abs-from-bot"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="harness"
SAB_DESC='the reverse machine reads its left side as absent wherever bot_ok holds'
SAB_DOC_FIGURE='DECLARED UNREACHED by lane ctxbuild 2026-10-19: no artifact carries a reverse machine beside an absent-prev-reading row. Read the verdict from a run: bash tests/mech/run_sabotage_matrix.sh S1160.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?m)^a|b" >/dev/null 2>&1 && grep -c "_reverse_next_state\[" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='UNREACHED'
SAB_EXPECT_REASON='a (?m)^ routes to ENG_ATTEMPT, which builds no reverse machine, so the reverse left_abs is read by no row; the REACH reads NOW REACHED if a reverse machine is ever built beside an absent-prev row'
SAB_COUNT='1'
SAB_BEFORE='    sd.left_abs  = m->reverse ? false : bot_ok;'
SAB_AFTER='    sd.left_abs  = bot_ok;   /* SABOTAGE S1160 */'
