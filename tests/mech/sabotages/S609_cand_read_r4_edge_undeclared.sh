#!/usr/bin/env bash
# S609 ([START-TABLE] C6, lane stc67; docs/design/start_table.md §1.3, docs/dev/lanes/stc67_report.md) -- a SELECTION READ left undeclared: RETRY's read of NEXT (R4, `adaptive-dense` pricing the hybrid prefilter's scanned set through `pcrec_dfa_cand_ppm`) is dropped from the slot graph, keeping RETRY's BOUND read.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh. Since C6 R4
# reads NEXT through `cand_read` (`dfa_cand_scan`/`dfa_pf_read`, reader
# RETRY), checked against `reads`. The `adaptive-dense` witness
# (`[a-z](?=the)`, a VM hybrid whose byte-class prefilter the retry prices)
# aborts with `CANDORACLE undeclared-read RETRY NEXT`. The default build
# does not check the edge, so no artifact byte and no answer moves.
SAB_ID='S609-cand-read-r4-edge-undeclared'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='RETRY reads NEXT (R4, the adaptive-dense density) over an edge the slot graph no longer declares; the trace build read check must abort'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc67_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S609.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "[a-z](?=the)" && grep -qF "#define RX_VM_RESEED \"adaptive-dense\"" "$REACH_TMP/o.c" && echo REACH-R4'
SAB_REACH_EXPECT='REACH-R4'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             .reads = { [CAND_SLOT_BOUND] = CAND_ON(CAND_ROUTE_VM),
                                        [CAND_SLOT_NEXT]  = CAND_ON(CAND_ROUTE_DFA) |
                                                            CAND_ON(CAND_ROUTE_ATTEMPT) } },'
SAB_AFTER='                             .reads = { [CAND_SLOT_BOUND] = CAND_ON(CAND_ROUTE_VM) } },   /* SABOTAGE S609 */'
