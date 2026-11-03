#!/usr/bin/env bash
# S1823 ([LANDWALK] stage 1, lane p1build; r7 FIX-2) -- LOCATE'S KIT ASK
# ABOUT NEXT'S SITE LEFT UNDECLARED.
#
# WHAT IT BREAKS. The walk's rarity row asks the kit for the start set of
# NEXT's row in the world without the walk (`cand_row_scan`, reader LOCATE).
# That ask must be a declared edge (`cand_nodes[LOCATE].kask[NEXT]`) so the
# `table-read-cycle` walk sees it. The plant drops the declaration.
#
# WHERE IT IS SEEN. The trace build's ask trap aborts with
# `CANDORACLE undeclared-ask LOCATE NEXT` on the landmark-walk witnesses of
# tests/codegen/cand_oracle_witnesses.tsv (arm candoracle).
SAB_ID='S1823-lmwalk-kask-undeclared'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='LOCATE asks the kit about the NEXT site for the landmark walk without declaring the ask'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1823.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             .by = { [CAND_SLOT_NEXT] = PCREC_NO_LANDMARK_WALK },
                             .kask = { [CAND_SLOT_NEXT] = CAND_ON(CAND_ROUTE_DFA) },'
SAB_AFTER='                             .by = { [CAND_SLOT_NEXT] = PCREC_NO_LANDMARK_WALK },
                             .kask = { 0 },   /* SABOTAGE S1823 */'
