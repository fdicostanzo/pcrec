#!/usr/bin/env bash
# S785 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 5; docs/dev/lanes/slbuild_report.md) -- the tolerant-utf8 first-character guard dropped.
# Detector: tests/utf8/landing_illformed.rxt (libpcre2 10.46's MATCH_INVALID_UTF answers at every startpos); run_start_landing.sh §1's guard witness.
SAB_ID='S785-landing-guard-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='startlanding harness'
SAB_DESC='a wide landing artifact no longer steps past an ill-formed sequence at the landing, so `.` on C3 61 reports [0,2) where the match is [1,2)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S785.'
SAB_REACH='"$PCREC" -e utf8 -p rx -o "$REACH_TMP/o.c" --pattern "." && grep -q "do landing_position++;" "$REACH_TMP/o.c" && echo REACH-GUARD'
SAB_REACH_EXPECT='REACH-GUARD'
SAB_HARNESS_TARGET='tests/utf8/landing_illformed.rxt'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (pcrec_dfa_landing_guard(cx)) {
            /* §2.5.2'\''s SKIP'
SAB_AFTER='        if (0 && pcrec_dfa_landing_guard(cx)) {   /* SABOTAGE S785 */
            /* §2.5.2'\''s SKIP'
