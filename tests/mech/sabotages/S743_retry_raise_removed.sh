#!/usr/bin/env bash
# S743 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- the RAISE progress class removed from RETRY's re-locate into the prefilter (E7, RETRY -> NEXT): the handoff graph then holds the cycle NEXT -> VERIFIER -> RETRY -> NEXT with no edge that strictly raises the lower bound (O9).
# Detector: tests/codegen/run_cand_oracle.sh: the trace build's self-check aborts `table-progress-cycle` on every witness (MEASURED by plant at landing: 59 checks fail). No artifact byte moves: progress classes are data for the check.
SAB_ID='S743-retry-raise-removed'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='RETRY'\''s re-locate (E7) loses its RAISE class: the self-check must report a cycle with no RAISE edge'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S743.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                             .raise = CN(CAND_SLOT_NEXT) | CN(CAND_NODE_VERIFIER) },'
SAB_AFTER='                             .raise = CN(CAND_NODE_VERIFIER) },   /* SABOTAGE S743 */'
