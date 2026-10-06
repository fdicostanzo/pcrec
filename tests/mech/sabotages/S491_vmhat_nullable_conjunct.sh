#!/usr/bin/env bash
# S491 ([START-SET] stage 2; startset.md §6.3, r3's S482) -- V's NON-NULLABLE
# conjunct removed: a pattern that can match EMPTY takes the hat, and the seek
# skips the empty match at a position whose byte is in no set.
#
# Detectors (arm vmhat): the fixture `a*b?` under `--engine=vm` (vmhat.rxt
# VMN: `ms 0 "" 0 0` and its kin -> no match), [vm-movers] (new movers off
# the manifest) and the differential.
SAB_ID='S491-vmhat-nullable-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='V'\''s non-nullable conjunct is gone: a nullable pattern takes the VM hat and loses its empty matches'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S491.'
SAB_REACH='"$PCREC" --features all --engine=vm --emit-facts --pattern '\''a*b?'\'' | grep -q '\''start_set	pattern	E2	derived	[a-z]*	nullable'\'' && echo REACH-NULLABLE-VM'
SAB_REACH_EXPECT='REACH-NULLABLE-VM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (ss->nullable) return false;
    for (int b = 0; b < 256; b++) n += ss->bits[b >> 3] >> (b & 7) & 1;'
SAB_AFTER='    /* SABOTAGE S491: the non-nullable conjunct removed */
    for (int b = 0; b < 256; b++) n += ss->bits[b >> 3] >> (b & 7) & 1;'
