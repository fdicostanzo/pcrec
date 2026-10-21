#!/usr/bin/env bash
# S1224 ([MEMFN] R-26 Z1, lane r26z1fix; docs/design/kit_proof.md §3-§4, docs/dev/lanes/r26z1_report.md §4) --
# A PROOF BIT SET ONLY BY A SIMD ROW.
#
# WHAT IT BREAKS. Compose.c clears proven[0] bit 0 when the policy allows SIMD: the proof depends on the layer, and C-PROOF (the proof identical across layers) finds it.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c and proof_run.c).
# The same text is run_proof.sh's plant S1224 (`run_proof.sh --plant S1224`).
SAB_ID="S1224-proof-bit-simd-only"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'a proof bit set only by a SIMD row: compose.c clears proven[0] bit 0 when the policy allows SIMD: the proof depends on the layer, and C-PROOF (the proof identical across layers) finds it'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26z1, build/r26/plants.log): run_proof.sh --plant S1224 goes red. The mech figure is OWED to the heavy job 500-kit-r26z1-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1224."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'    /* proven0 and proven_prev are COPIES'
SAB_AFTER=$'    if (!(s->policy & MF_P_PORTABLE_ONLY)) out->proven[0 - MF_PROOF_LO][0] &= 0xFE;\n    /* proven0 and proven_prev are COPIES'
