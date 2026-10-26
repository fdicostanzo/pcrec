#!/usr/bin/env bash
# S1656 ([INLINE-C] stage 1b, lane ic1b; design S-IC20) -- the marked set is made unconditional (every kind marks every group), so backreference-free and callout-free patterns move
#
# Witness and reach: the backref identity gate (a backreference-free pattern's bytes on all three axes, --no-captures included) goes red.
SAB_ID="S1656-marked-set-unconditional"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="brefidentity"
SAB_DESC='the marked set is made unconditional (every kind marks every group), so backreference-free and callout-free patterns move'
SAB_REACH='"$PCREC" -p rx  -o "$REACH_TMP/o.c" --pattern '\''(a)(b)c'\'' && grep -qF '\''rx_'\'' "$REACH_TMP/o.c" && echo REACH-MARKED-SET-POP'
SAB_REACH_EXPECT='REACH-MARKED-SET-POP'
SAB_COUNT=1
SAB_BEFORE='    case KREADS_NONE:
        return;'
SAB_AFTER='    case KREADS_NONE: /* [SABOTAGE S1656] */
        for (int g = 1; g < nmark; g++) mark[g] = true;
        return;'
