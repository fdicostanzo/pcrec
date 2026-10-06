#!/usr/bin/env bash
# S492 ([START-SET] stage 2; startset.md §6.3) -- V's UNANCHORED conjunct
# removed: an anchored or \G-start VM artifact takes the hat. Probably
# answer-invisible (an attempt the seek moves still fails its own anchor, and
# `attempt_max` ends the loop), so the detector is structural (checks-F4):
# [vm-anchor] (every mover's RX_VM_START is "unanchored") and [vm-movers]
# (anchored blocks join the movers, off the manifest), arm vmhat.
SAB_ID='S492-vmhat-anchor-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='V'\''s unanchored conjunct is gone: anchored and \G-start VM artifacts take the VM hat'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S492.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''^(ab)\1'\'' && grep -q '\''RX_VM_START "anchored"'\'' "$REACH_TMP/o.c" && echo REACH-ANCHORED-VM'
SAB_REACH_EXPECT='REACH-ANCHORED-VM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_fact_start_anchor(cx) != PCREC_SANCH_NONE) return false;
    if (ss->nullable) return false;'
SAB_AFTER='    /* SABOTAGE S492: the unanchored conjunct removed */
    if (ss->nullable) return false;'
