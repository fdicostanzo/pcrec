#!/usr/bin/env bash
# S606 ([START-TABLE] C5b, lane stc5b; docs/design/start_table.md §1.3, §1.6, docs/dev/lanes/stc5b_report.md) -- a SELECTION READ left undeclared: NEXT's read of BOUND on the VM route is dropped from the slot graph (`cand_nodes[CAND_SLOT_NEXT].reads`), so N7 `first-class`'s anchoring conjunct reads BOUND over an edge the graph does not list.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh. Since C5b the
# four BOUND restatements (P2's two arms, N7, R3, N12) read BOUND through
# `cand_read`, and the trace build checks every read against the graph's
# `reads` column, aborting (`CANDORACLE undeclared-read NEXT BOUND`) on an
# edge it does not declare on the read's route. The `first-class` witness
# (`--engine=vm I`) reaches N7's predicate, so it aborts. The default build
# does not check the edge, so no artifact byte and no answer moves: the
# corpus arm is not named, by design.
SAB_ID='S606-cand-read-edge-undeclared'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='NEXT reads BOUND on the VM route (N7 first-class) over an edge the slot graph no longer declares; the trace build read check must abort'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc5b_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S606.'
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "I" && grep -qF "#define RX_VM_START_SCAN \"first-class\"" "$REACH_TMP/o.c" && echo REACH-VM-HAT'
SAB_REACH_EXPECT='REACH-VM-HAT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             CN(CAND_NODE_VERIFIER),
                             .reads = { [CAND_SLOT_BOUND] = CAND_ON(CAND_ROUTE_ATTEMPT) |
                                                            CAND_ON(CAND_ROUTE_VM) } },'
SAB_AFTER='                             CN(CAND_NODE_VERIFIER),
                             .reads = { [CAND_SLOT_BOUND] = CAND_ON(CAND_ROUTE_ATTEMPT) } },   /* SABOTAGE S606 */'
