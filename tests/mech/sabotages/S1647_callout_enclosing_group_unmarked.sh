#!/usr/bin/env bash
# S1647 ([INLINE-C] stage 1b, lane ic1b; design S-IC2) -- a callout site's marked set leaves group 1 out, so a group enclosing the site is not published at close
#
# Witness and reach: checks.c's enclosing-group check, (a(?C"see1")b)+ on abab: the second fire must see group 1 = [0,2), the first iteration's closed value.
SAB_ID="S1647-callout-enclosing-group-unmarked"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="callouts"
SAB_DESC='a callout site'\''s marked set leaves group 1 out, so a group enclosing the site is not published at close'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''(a(?C"see1")b)+'\'' && grep -qF '\''rx_callout_see1.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-ENCLOSING'
SAB_REACH_EXPECT='REACH-CALLOUT-ENCLOSING'
SAB_COUNT=1
SAB_BEFORE='        for (int g = 1; g < nmark; g++) mark[g] = true;'
SAB_AFTER='        for (int g = 2 /* [SABOTAGE S1647] */; g < nmark; g++) mark[g] = true;'
