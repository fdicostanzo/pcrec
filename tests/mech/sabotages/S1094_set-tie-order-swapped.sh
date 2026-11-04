#!/usr/bin/env bash
# S1094 (lane b3a, [MEMFN] R17-b' B3a) -- S980 / PR-7: the set port breaks a mass tie toward the member EARLIER in pattern order; caught by the -e utf8 ba tie witness
# span_pick unit 1b (lane sp1bfix) RE-ANCHORED: tie_over became T_PRES_MEMBER's key,
# kit_tie_member_key (window.c). The plant's intent is the MEMBER ORDER, not the byte: the
# order field is complemented (an UNKNOWN order 0 goes highest), the byte still breaks an
# equal order upward, so an equal-mass tie goes to the member EARLIER in pattern order.
SAB_ID="S1094-set-tie-order-swapped"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="candoracle"
SAB_DESC="S980 / PR-7: the set port breaks a mass tie toward the member EARLIER in pattern order; caught by the -e utf8 ba tie witness"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return (int32_t)(o << 8 | (unsigned)byte);'
SAB_AFTER='    return (int32_t)((0xFFFFu - o) << 8 | (unsigned)byte);   /* SABOTAGE S1094 */'
SAB_DOC_FIGURE="HAND-MEASURED by lane sp1bfix after the span_pick 1b re-anchor: the sabotaged tree under tests/codegen/run_cand_oracle.sh, candoracle:8fail/163pass DETECTED (the solo mech run is left to the gate shard)."
