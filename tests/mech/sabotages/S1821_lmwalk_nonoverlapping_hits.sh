#!/usr/bin/env bash
# S1821 ([LANDWALK] stage 1, lane p1build; r5 SOUND-2, T3) -- THE HIT STREAM
# SKIPS TO THE LAST VERIFY'S REACH (a non-overlapping stream) instead of
# taking every occurrence of the landmark.
#
# WHAT IT BREAKS. After a failed verify the next hit is searched from the
# farthest byte the verify read, so a landmark inside that span is never
# walked from and the reach guard (which relocates on it) never fires.
#
# WHERE IT IS SEEN. The answer net's family R: `[a-z]+@...x` on "a@b@cdex" is
# (2,8); the verify from 0 reads past the second `@`, and the plant resumes
# after it (NOMATCH, simulated on the emitted artifact at authoring). T3's
# cells do not see it under a single-byte landmark (every hit overlaps none).
SAB_ID='S1821-lmwalk-nonoverlapping-hits'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='the landmark walk resumes its hit search at the last verify reach instead of the next byte'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1821.'
SAB_HARNESS_TARGET='tests/landwalk/landwalk.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "[a-z]+@(?:[a-z]+@)*[a-z]+ " | grep -F "size_t lmwalk_reach = search_from;"'
SAB_REACH_EXPECT='size_t lmwalk_reach = search_from;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='               "            lmwalk_reach = scan_position;\n"
               "        }\n"
               "        landmark_position++;\n"'
SAB_AFTER='               "            lmwalk_reach = scan_position;\n"
               "        }\n"
               "        landmark_position = lmwalk_reach > landmark_position ? lmwalk_reach : landmark_position + 1;   /* SABOTAGE S1821 */\n"'
