#!/usr/bin/env bash
# S1666 ([INLINE-C] stage 1b guide, lane ic1bguide) -- the lookaround refusal drops its fix wording
#
# Witness and reach: run_callouts_tests.sh arm 5 (the per-culprit once-refusal rows).
SAB_ID="S1666-callout-refusal-no-fix"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the lookaround refusal drops its fix wording'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?*a+)(?C"x,once")a+c'\'' 2>&1 | grep -qF '\''or wrap it: (?>(?*...))'\'' && echo REACH-GUIDE-FIX-NAMED'
SAB_REACH_EXPECT='REACH-GUIDE-FIX-NAMED'
SAB_COUNT=1
SAB_BEFORE='"use %s (atomic), or wrap it: (?>%s...))",'
SAB_AFTER='"use %s (atomic), or wrap it: (?>%s...)", /* [SABOTAGE S1666] */'
