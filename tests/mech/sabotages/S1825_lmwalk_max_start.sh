#!/usr/bin/env bash
# S1825 ([LANDWALK] stage 1, lane p1build) -- THE WALK TAKES THE LARGEST
# START instead of the smallest.
#
# WHAT IT BREAKS. The backward walk keeps the first accepting position it
# meets (the one nearest the landmark), so the verify runs from a start
# above the leftmost one and a later match is reported.
#
# WHERE IT IS SEEN. The answer net: `a+b` on "aab" is (0,3), the plant (1,3).
SAB_ID='S1825-lmwalk-max-start'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='the landmark walk verifies from the largest start the backward walk accepts at'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1825.'
SAB_HARNESS_TARGET='tests/landwalk/landwalk.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "a+b" | grep -F "#define RX_DFA_SCAN \"landmark-walk\""'
SAB_REACH_EXPECT='#define RX_DFA_SCAN "landmark-walk"'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    "rewind_position", "match_start_position",
    "            ", "                ", true, false,
    "    /* ---- LANDMARK TABLES: from one past a landmark, where can a\n"'
SAB_AFTER='    "rewind_position", "*(match_start_position == (size_t)-1 ? &match_start_position : &lmwalk_start)",   /* SABOTAGE S1825 */
    "            ", "                ", true, false,
    "    /* ---- LANDMARK TABLES: from one past a landmark, where can a\n"'
