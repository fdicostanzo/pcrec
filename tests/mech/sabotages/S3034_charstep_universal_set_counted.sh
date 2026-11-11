#!/usr/bin/env bash
# S3034 ([UCP] U3, review 2026-11-10 r4 ucpu3 ADMIT-3/checks-1, lane ucpu3fix)
# -- THE UNIVERSAL NON-ASCII SET COUNTS AGAINST PCREC_MAX_CHAR_STEP_SETS. The
# unanchored loop's all-non-ASCII set splits no character; counted, it takes
# one of the 8 sets and a caller gets 7. The reject knee row "8 sets (the
# last admitted)" goes red; the subject tip's reject table had no knee row.
SAB_ID="S3034-charstep-universal-set-counted"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="reject"
SAB_DESC="the all-non-ASCII set is counted as a character-stepped set, so a caller gets 7 of the 8"
SAB_DOC_FIGURE='reject arm: the char-step "8 sets (the last admitted)" row red (measured at landing, lane ucpu3fix).'
SAB_REACH='"$PCREC" -e utf8 --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(*UCP)\\b\\w+\\b" >/dev/null 2>&1 && grep -c "define RX_DFA_SCAN \"char-step\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    if (nonascii_all(iv, n)) return ISL_SET_ALL;'
SAB_AFTER='    if (0 && nonascii_all(iv, n)) return ISL_SET_ALL;   /* SABOTAGE S3034 */'
