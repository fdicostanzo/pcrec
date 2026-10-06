#!/usr/bin/env bash
# S501 ([START-SET], D148; docs/design/startset.md §6.3) -- THE WALK READS A
# LOOKAROUND AS CONSUMING: `A_LOOK` returns its BODY's first bytes,
# non-nullable, where a zero-width node must be erased (§3.2). The set is
# then the lookaround body's bytes instead of what follows it (rev 2's
# `look-eats` plant, 118 violations; it also covered `A_CTX`, which this row
# leaves alone).
#
# Detector at stage 1: tests/startset C-SS* ([ss-ctrl]) and the `(?<=a)z|w`
# witness of [ss-flag]. Stage 2/3 add answer identity on both hats.
SAB_ID="S501-walk-look-consumes"
SAB_FILE="src/facts/startset.c"
SAB_SUITES="startset vmhat dfahat"
SAB_DESC="the start-set walk reads A_LOOK as consuming its body's first bytes (non-nullable) instead of erasing it, so a lookaround's body replaces the bytes that follow it in the start set"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/ssbuild01_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S501."
# RE-AIMED 2026-10-06 (lane ssbuild3): the probe no longer pins the listing's
# `used` column -- stage 2's every-artifact RX_VM_START_SCAN stamp asks the
# fact on every compile, so `used` reads `yes` since abi 62 and the `no` this
# probe matched made the row read UNREACHED. Intent unchanged: the witness's
# start set has two members.
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''(?<=ab)z|w'\'' | grep -q '\''^byte	start_set	pattern	E2	derived	[a-z]*	2:'\'' && echo REACH-LOOKAROUND-SET'
SAB_REACH_EXPECT="REACH-LOOKAROUND-SET"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_KRESET:
        case A_LOOK:
            return acc;'
SAB_AFTER='        case A_KRESET:
            return acc;
        case A_LOOK: {   /* SABOTAGE S501: the lookaround read as consuming */
            StartSet b = ss_walk(cx, a->l, ss_empty());
            b.nullable = false;
            return ss_cat(b, &acc);
        }'
