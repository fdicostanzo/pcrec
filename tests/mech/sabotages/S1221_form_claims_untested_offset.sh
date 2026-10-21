#!/usr/bin/env bash
# S1221 ([MEMFN] R-26 Z1, lane r26z1fix; docs/design/kit_proof.md §3-§4, docs/dev/lanes/r26z1_report.md §4) --
# A FORM CLAIMING AN UNTESTED OFFSET.
#
# WHAT IT BREAKS. Compose.c's class proof marks one position past each RUN term as proven: a byte the form never tested is claimed, and the per-offset proof oracle finds a proven position the byte-loop does not.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c and proof_run.c).
# The same text is run_proof.sh's plant S1221 (`run_proof.sh --plant S1221`).
SAB_ID="S1221-form-claims-untested-offset"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'a form claiming an untested offset: compose.c\'s class proof marks one position past each RUN term as proven: a byte the form never tested is claimed, and the per-offset proof oracle finds a proven position the byte-loop does not'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26z1, build/r26/plants.log): run_proof.sh --plant S1221 goes red. The mech figure is OWED to the heavy job 500-kit-r26z1-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1221."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'long d = (long)t->offset + j;'
SAB_AFTER=$'long d = (long)t->offset + j + (t->kind == MF_T_RUN);'
