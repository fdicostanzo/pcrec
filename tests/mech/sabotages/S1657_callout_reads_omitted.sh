#!/usr/bin/env bash
# S1657 ([INLINE-C] stage 1b, lane ic1b; design S-IC25) -- a callout site's reads (every group) are omitted from the marked set, so --no-captures drops the groups its view shows
#
# Witness and reach: checks.c A5, (a)b(?C"g1set") and (a)b(?C"see") under --no-captures: the site must still see group 1 = [0,1).
SAB_ID="S1657-callout-reads-omitted"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="callouts"
SAB_DESC='a callout site'\''s reads (every group) are omitted from the marked set, so --no-captures drops the groups its view shows'
SAB_REACH='"$PCREC" -p rx --features all --no-captures -o "$REACH_TMP/o.c" --pattern '\''(a)b(?C"g1set")'\'' && grep -qF '\''rx_callout_g1set.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-NOCAPS'
SAB_REACH_EXPECT='REACH-CALLOUT-NOCAPS'
SAB_COUNT=1
SAB_BEFORE='    case KREADS_ALL:
        for (int g = 1; g < nmark; g++) mark[g] = true;
        return;'
SAB_AFTER='    case KREADS_ALL: /* [SABOTAGE S1657] */
        return;'
