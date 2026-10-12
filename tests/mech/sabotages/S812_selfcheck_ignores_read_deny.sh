#!/usr/bin/env bash
# S812 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE SELF-CHECK FOLLOWS A READ ITS
# DENY BITS REMOVE: `cand_read_reaches` ignores `CandNode.by`, so the slot
# graph's PRESENCE -> NEXT -> FIRST -> PRESENCE edge reads as the cycle the
# deny-masked read makes acyclic, and the trace build aborts
# (`CANDORACLE table-read-cycle`). Detector (arm candoracle):
# tests/codegen/run_cand_oracle.sh; the default build does not run the
# self-check, so no artifact byte moves.
SAB_ID='S812-selfcheck-ignores-read-deny'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='the start table'\''s structural self-check ignores the deny bits a slot'\''s read is made under, so the masked PRESENCE-NEXT-FIRST read reads as a cycle and the trace build aborts'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S812.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!cand_nodes[sl].reads[t] || (cand_nodes[sl].by[t] & mask)) continue;'
SAB_AFTER='        if (!cand_nodes[sl].reads[t]) continue;   /* SABOTAGE S812 */'
