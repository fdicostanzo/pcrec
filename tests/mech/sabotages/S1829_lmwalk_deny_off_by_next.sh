#!/usr/bin/env bash
# S1829 ([LANDWALK] stage 1, lane p1build; r7) -- THE WALK'S DENY REMOVED
# FROM `cand_nodes[LOCATE].by[NEXT]`.
#
# WHAT IT BREAKS. LOCATE reads NEXT in the world without the walk (the
# counterfactual read); `by` names the row that read is made under, which is
# what lets `table-read-cycle` accept LOCATE -> NEXT beside NEXT's own read of
# LOCATE. Without it the edge is an undeclared cycle.
#
# WHERE IT IS SEEN. The trace build's table self-check (`table-read-cycle`)
# in tests/codegen/run_cand_oracle.sh (arm candoracle).
SAB_ID='S1829-lmwalk-deny-off-by-next'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='the counterfactual LOCATE to NEXT read no longer names the walk deny it is made under'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1829.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             .by = { [CAND_SLOT_NEXT] = PCREC_NO_LANDMARK_WALK },
                             .kask = { [CAND_SLOT_NEXT] = CAND_ON(CAND_ROUTE_DFA) },'
SAB_AFTER='                             .by = { 0 },   /* SABOTAGE S1829 */
                             .kask = { [CAND_SLOT_NEXT] = CAND_ON(CAND_ROUTE_DFA) },'
