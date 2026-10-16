#!/usr/bin/env bash
# S844 ([CAND-PATH-READS], lane pathreads) -- RECOVER'S READ OF NEXT LOSES ITS
# DENY BIT: the plant re-opens the cycle 9dec5e6f closed (axtri_report.md §2).
# RECOVER `landing` reads NEXT without `-fno-req-handoff`, so NEXT `handoff`
# reads FIRST, FIRST `handoff` reads the path, and the path selects RECOVER
# again. The default build recurses until the stack overflows (pcrec SIGSEGV on
# `-e utf8 -fno-offset-skip '€+'`). Before [CAND-PATH-READS] the trace build's
# `table-read-cycle` self-check could not see it, because FIRST's path read was
# not a `cand_nodes[].reads` edge. With the path reads declared, the self-check
# walks FIRST -> RECOVER -> NEXT -> FIRST and aborts at every checked decision
# (`CANDORACLE table-read-cycle`), on every witness. Detector (arm candoracle):
# tests/codegen/run_cand_oracle.sh. The default build does not run the
# self-check; its SIGSEGV is the plant's reach, not this row's detector.
SAB_ID='S844-recover-read-drops-handoff-deny'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='the start table'\''s RECOVER node reads NEXT without the handoff deny bit, so the path read closes the FIRST-RECOVER-NEXT-FIRST cycle and the trace build'\''s self-check aborts'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/pathreads_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S844.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                        [CAND_SLOT_LOCATE] = CAND_ON(CAND_ROUTE_DFA) },
                             .under = { [CAND_SLOT_NEXT] = PCREC_NO_REQ_HANDOFF },'
SAB_AFTER='                                        [CAND_SLOT_LOCATE] = CAND_ON(CAND_ROUTE_DFA) },   /* SABOTAGE S844 */'
# Re-aimed by lane fdb1 (R17-b' B1, 2026-10-16): RECOVER's node gained the
# kit-ask fields after `.under`, so the node no longer closes there; the plant
# still drops RECOVER's read-under deny bits and nothing else (intent
# re-verified).
