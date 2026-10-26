#!/usr/bin/env bash
# S1656 ([INLINE-C] stage 1b, lane ic1b; design S-IC20) -- the marked set is made unconditional (every kind marks every group), so backreference-free and callout-free patterns move
#
# Witness and reach: the backref identity gate (a backreference-free pattern's bytes on all three axes, --no-captures included) goes red.
SAB_ID="S1656-marked-set-unconditional"
SAB_FILE="src/opt/atomic.c"
SAB_SUITES="brefidentity"
SAB_DESC='the marked set is made unconditional (every kind marks every group), so backreference-free and callout-free patterns move'
# RE-AIMED at lane ic1bfix (review r2 CHK-5): the old reach grepped `rx_`,
# true of every artifact. This one shows the population the plant moves: on
# the clean tree `--no-captures` DROPS both unmarked groups of `(a)(b)c` (no
# SLOT_GROUP in the artifact) while the capture build RETAINS them, so a
# marked set made unconditional changes this artifact.
SAB_REACH='"$PCREC" -p rx --no-captures --engine=vm -o "$REACH_TMP/d.c" --pattern '\''(a)(b)c'\'' && ! grep -qF SLOT_GROUP "$REACH_TMP/d.c" && echo REACH-GROUPS-DROPPED; "$PCREC" -p rx --engine=vm -o "$REACH_TMP/k.c" --pattern '\''(a)(b)c'\'' && grep -qF SLOT_GROUP "$REACH_TMP/k.c" && echo REACH-GROUPS-RETAINED'
SAB_REACH_EXPECT='REACH-GROUPS-DROPPED
REACH-GROUPS-RETAINED'
SAB_COUNT=1
SAB_BEFORE='    case KREADS_NONE:
        return;'
SAB_AFTER='    case KREADS_NONE: /* [SABOTAGE S1656] */
        for (int g = 1; g < nmark; g++) mark[g] = true;
        return;'
