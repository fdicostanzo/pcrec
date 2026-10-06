#!/usr/bin/env bash
# S494 ([START-SET] stage 2; startset.md §4.3, r3's S484) --
# `pcrec_artifact_has_dfa_scan` RETURNS TRUE ON A VM-HAT ARTIFACT, the K64
# shape: K65/K66's no-DFA pre-checks key on it and would elide their linear
# no-match proofs. The plant puts the VM hat's verdict into a function that
# has no VM-hat knowledge; `pcrec_emit_vm_start_seek`'s assertion then
# refuses every mover's compile. Detectors (arm vmhat): the fixtures (every
# VM-hat block fails to compile) and [vm-movers].
SAB_ID='S494-has-dfa-scan-on-vmhat'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='pcrec_artifact_has_dfa_scan reads true on a VM-hat artifact (the K64 shape; the K65/K66 pre-checks would elide their no-match proofs)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S494.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(ab)\1'\'' && grep -q '\''RX_VM_START_SCAN "first-class"'\'' "$REACH_TMP/o.c" && echo REACH-VMHAT'
SAB_REACH_EXPECT='REACH-VMHAT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return cx->job->fit.chosen == ENGM_DFA || cx->job->fit.prefilter;'
SAB_AFTER='    return cx->job->fit.chosen == ENGM_DFA || cx->job->fit.prefilter ||   /* SABOTAGE S494 */
           (cx->job->fit.chosen == ENGM_VM && strcmp(pcrec_vm_start_scan_name(cx), "none") != 0);'
