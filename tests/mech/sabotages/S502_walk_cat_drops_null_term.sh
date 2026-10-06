#!/usr/bin/env bash
# S502 ([START-SET], D148; docs/design/startset.md §6.3) -- THE WALK'S A_CAT
# DROPS `null(l) ? F(r)`: a nullable left factor no longer lets the right
# factor's first bytes in, so the start set is too SMALL (review r4
# sound-F2's own example; rev 2's `cat-null` plant, 367 violations).
#
# Detector at stage 1: tests/startset C-SS* ([ss-ctrl]) -- a forward DFA
# whose emitted start bytes include the right factor's lands outside the
# fact. Stage 2/3 add answer identity (the design's witness `(?<=a)z` under
# `--engine=vm` on `az`). The corpus arm is not named: no hat reads the fact
# at stage 1, so the plant moves no answer.
SAB_ID="S502-walk-cat-drops-null-term"
SAB_FILE="src/facts/startset.c"
SAB_SUITES="startset vmhat dfahat"
SAB_DESC="the start-set walk's A_CAT drops the null(l) ? F(r) term, so a nullable left factor hides the right factor's first bytes (the set is too small)"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/ssbuild01_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S502."
# RE-AIMED 2026-10-06 (lane ssbuild3): the probe no longer pins the listing's
# `used` column -- stage 2's every-artifact RX_VM_START_SCAN stamp asks the
# fact on every compile, so `used` reads `yes` since abi 62 and the `no` this
# probe matched made the row read UNREACHED. Intent unchanged: the witness's
# start set has two members.
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''a?bc'\'' | grep -q '\''^byte	start_set	pattern	E2	derived	[a-z]*	2:'\'' && echo REACH-NULLABLE-LEFT'
SAB_REACH_EXPECT="REACH-NULLABLE-LEFT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (l.nullable)
        for (int i = 0; i < 32; i++) l.bits[i] |= r->bits[i];'
SAB_AFTER='    if (0 && l.nullable)   /* SABOTAGE S502 */
        for (int i = 0; i < 32; i++) l.bits[i] |= r->bits[i];'
