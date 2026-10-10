#!/usr/bin/env bash
# S608 ([START-TABLE] C6, lane stc67; docs/design/start_table.md §1.3, docs/dev/lanes/stc67_report.md) -- a SELECTION READ left undeclared on ONE route: PRESENCE's read of NEXT (G1, the `dominated` row's look at the candidate-start scan) keeps its CAND_ROUTE_DFA edge and loses CAND_ROUTE_ATTEMPT, so G1 on an ENG_ATTEMPT artifact reads NEXT over an edge the graph does not list.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh. Since C6 G1
# reads NEXT through `cand_read` (`dfa_cand_scan` -> `attempt_next_read` on
# the ATTEMPT route), checked per route against `reads`. The `pred-memchr`
# witness (`(?m)^ERROR`, ENG_ATTEMPT, a necessary byte, so the admission
# walk reaches `dominated`) aborts with `CANDORACLE undeclared-read PRESENCE
# NEXT`. A route-blind check (one that tested the edge without its route)
# would pass this plant: that is the property it pins. The default build
# does not check the edge, so no artifact byte and no answer moves.
SAB_ID='S608-cand-read-g1-attempt-edge-undeclared'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='PRESENCE reads NEXT (G1) on the ATTEMPT route over an edge the slot graph no longer declares on that route; the trace build read check must abort'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc67_report.md §2); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S608.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?m)^ERROR" && grep -qF "#define RX_DFA_SCAN \"attempt\"" "$REACH_TMP/o.c" && grep -qF "#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && echo REACH-ATTEMPT-G1'
SAB_REACH_EXPECT='REACH-ATTEMPT-G1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2): PRESENCE's reads gained the LOCATE edge after NEXT; the plant still drops NEXT's ATTEMPT bit. Intent
# unchanged.
SAB_BEFORE='                                        [CAND_SLOT_NEXT]  = CAND_ON(CAND_ROUTE_DFA) |
                                                            CAND_ON(CAND_ROUTE_ATTEMPT),
                                        /* [OPT-REVEND] L2 `dominated`'\''s'
SAB_AFTER='                                        [CAND_SLOT_NEXT]  = CAND_ON(CAND_ROUTE_DFA),   /* SABOTAGE S608 */
                                        /* [OPT-REVEND] L2 `dominated`'\''s'
