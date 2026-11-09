#!/usr/bin/env bash
# S1224 ([MEMFN] R-26 Z1, lane r26z1fix; docs/design/kit_proof.md §3-§4, docs/dev/lanes/r26z1_report.md §4) --
# A PROOF BIT SET ONLY BY A SIMD ROW.
#
# WHAT IT BREAKS. Compose.c's ask clears proven[0] bit 0 when the art's stated CPU target admits a SIMD level: the proof depends on the layer, and C-PROOF (the proof identical across every kit target) finds it.
# RE-AIMED 2026-11-08 (lane u3tgt, [XARCH-DEV] U3): the old plant read the site's MF_P_PORTABLE_ONLY bit, which no kit code reads after U2 and no pcrec caller sets after U3; the layer is now the art's target (mf_art_target), so the plant reads it (kit_target_levels) in mf_ask's class path, where the art is in hand.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c and proof_run.c).
# The same text is run_proof.sh's plant S1224 (`run_proof.sh --plant S1224`).
SAB_ID="S1224-proof-bit-simd-only"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'a proof bit set only by a SIMD layer: compose.c\'s ask clears proven[0] bit 0 when the art\'s target admits a SIMD level: the proof depends on the layer, and C-PROOF (the proof identical across every kit target) finds it'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26z1, build/r26/plants.log): run_proof.sh --plant S1224 goes red. The mech figure is OWED to the heavy job 500-kit-r26z1-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1224."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'    if (!row || kit_class(row, s, out)) return -1;\n    if (fd_pres('
SAB_AFTER=$'    if (!row || kit_class(row, s, out)) return -1;\n    if (kit_target_levels(art->target)) out->proven[0 - MF_PROOF_LO][0] &= 0xFE;\n    if (fd_pres('
