#!/usr/bin/env bash
# S1226 ([MEMFN] R-26 Z1, lane r26z1fix; docs/design/kit_proof.md §3-§4, docs/dev/lanes/r26z1_report.md §4) --
# AN UNSTATED FIELD ACCEPTED.
#
# WHAT IT BREAKS. Compose.c reads an UNSTATED `absent` as FAILS instead of refusing it: the two refusal fixtures for an UNSTATED absent go red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c and proof_run.c).
# The same text is run_proof.sh's plant S1226 (`run_proof.sh --plant S1226`).
SAB_ID="S1226-unstated-field-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'an UNSTATED field accepted: compose.c reads an UNSTATED `absent` as FAILS instead of refusing it: the two refusal fixtures for an UNSTATED absent go red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26z1, build/r26/plants.log): run_proof.sh --plant S1226 goes red. The mech figure is OWED to the heavy job 500-kit-r26z1-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1226."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'    if (p->absent == MF_ABSENT_UNSTATED)\n        return'
SAB_AFTER=$'    if (0)\n        return'
