#!/usr/bin/env bash
# S493 ([START-SET] stage 2; startset.md §6.3) -- V's NO-PREFILTER conjunct
# removed: a VM HYBRID takes the VM hat too. Its prefilter is a DFA scan, so
# `pcrec_emit_vm_start_seek`'s §4.3 assertion refuses the compile; the stamp
# would otherwise read "first-class" on a hybrid. Detectors (arm vmhat):
# [vm-wit]'s hybrid witness `(a|b)c\d+` (expects "none"; the compile now
# fails) and [vm-route].
SAB_ID='S493-vmhat-prefn-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='V'\''s no-prefilter conjunct is gone: a VM hybrid also takes the VM hat'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S493.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(a|b)c\d+'\'' && grep -q '\''RX_VM_PREFILTER "hybrid"'\'' "$REACH_TMP/o.c" && echo REACH-HYBRID'
SAB_REACH_EXPECT='REACH-HYBRID'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->job->fit.chosen != ENGM_VM || cx->job->fit.prefilter) return false;'
SAB_AFTER='    if (cx->job->fit.chosen != ENGM_VM) return false;   /* SABOTAGE S493 */'
