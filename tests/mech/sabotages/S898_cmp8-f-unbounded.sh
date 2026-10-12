#!/usr/bin/env bash
# S898 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-8) -- F is compiled WITHOUT its one-attempt bound, so the floor part runs P's whole attempt loop: every answer is right and the K106 cell's work is back.
SAB_ID='S898-cmp8-f-unbounded'
SAB_FILE='src/core/compound.c'
SAB_SUITES='compound'
SAB_DESC='F is compiled WITHOUT its one-attempt bound, so the floor part runs P'\''s whole attempt loop: every answer is right and the K106 cell'\''s work is back'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG898@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                  PCREC_PE_DFA, PCREC_PB_ONE_ATTEMPT, PCREC_PART_NEED_SEARCH,'
SAB_AFTER='                  PCREC_PE_DFA, PCREC_PB_NONE, PCREC_PART_NEED_SEARCH,   /* SABOTAGE S898 */'
