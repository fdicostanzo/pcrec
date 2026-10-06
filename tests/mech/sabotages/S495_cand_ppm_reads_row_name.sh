#!/usr/bin/env bash
# S495 ([START-SET] stage 0, K84; docs/design/startset.md §6.3) --
# `pcrec_dfa_cand_ppm` CLASSIFIES THE SELECTED PREFILTER ROW BY ITS NAME again,
# the K84 shape the stage-0 fix removed: the byte-class rows are recognised by
# `strcmp` on two names rather than by `DfaPf.scan`, so a new SET-scanning row
# with any other name would be priced at 1,000,000 ppm.
#
# Detector at stage 0: tests/codegen/run_cand_rows.sh's
# [cand-no-name-strcmp], the structural check this row exists to prove. It is
# ANSWER-INVISIBLE today and will stay answer-invisible on every existing row
# (the plant reads the same two names the field now encodes), so the corpus
# arm is not named. Stage 3 adds the answer-level detector the design names
# (the hybrid re-seed row stamp on the aws hybrid mover), once a SET row with
# another name exists to mis-price.
SAB_ID="S495-cand-ppm-reads-row-name"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candrows dfahat"
SAB_DESC="pcrec_dfa_cand_ppm recognises a byte-class row by strcmp on its NAME again (K84 regression), so a SET-scanning row with any other name is priced at 1,000,000 ppm"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/ssbuild01_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S495."
# [MECH-REACH] the planted line is reached: a VM hybrid whose prefilter is a
# byte-class row prices its adaptive re-seed through the SET arm.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''[a-z](?=the)'\'' && grep -q '\''^#define RX_VM_RESEED "adaptive-dense"'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_DFA_PREFILTER "byte-class"'\'' "$REACH_TMP/o.c" && echo REACH-HYBRID-RESEED'
SAB_REACH_EXPECT="REACH-HYBRID-RESEED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (pf->scan != PF_SCAN_SET)
            return 1000000u;'
SAB_AFTER='        if (strcmp(pf->c.name, "byte-class") && strcmp(pf->c.name, "byte-class-bounded"))   /* SABOTAGE S495 */
            return 1000000u;'
