#!/usr/bin/env bash
# S1655 ([INLINE-C] stage 1b, lane ic1b; design S-IC19) -- the search loop of a callout artifact re-runs a failed attempt at the same start once, so a class 1-2 site fires twice per attempt
#
# Witness and reach: gen_diff.py's firing-class bound: a once-per-start or once-per-match site fires at most once per attempt start in one call.
SAB_ID="S1655-callout-attempt-rerun"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="callouts"
SAB_DESC='the search loop of a callout artifact re-runs a failed attempt at the same start once, so a class 1-2 site fires twice per attempt'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"pass")b'\'' && grep -qF '\''if (result < -1) return (int)result;'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-SEARCH-LOOP'
SAB_REACH_EXPECT='REACH-CALLOUT-SEARCH-LOOP'
SAB_COUNT=1
SAB_BEFORE='        v->cx->ncallouts > 0 ? "        if (result < -1) return (int)result;\n" : "",'
SAB_AFTER='        v->cx->ncallouts > 0 ? "        if (result < -1) return (int)result;\n        { static __thread int rr; if (result == -1 && (rr ^= 1)) continue; } /* [SABOTAGE S1655] */\n" : "",'
