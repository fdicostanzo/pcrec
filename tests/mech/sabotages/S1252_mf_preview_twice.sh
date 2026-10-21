#!/usr/bin/env bash
# S1252 ([MEMFN] R-26.6, lane r26zk; docs/design/kit_proof.md §2.5, §7; docs/dev/lanes/r26zk_report.md §4) --
# MF_PREVIEW ACCEPTED TWICE.
#
# WHAT IT BREAKS. compose.c drops mf_preview's called-twice refusal: family D's `mf_preview twice` goes red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c family D).
# The same text is run_proof.sh's plant S1252 (`run_proof.sh --plant S1252`).
SAB_ID="S1252-mf-preview-twice"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'mf_preview accepted twice: compose.c drops mf_preview\'s called-twice refusal: family D\'s `mf_preview twice` goes red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26zk, build/r26zk/light/plants_all.log): run_proof.sh --plant S1252 goes red. The mech figure is OWED to the heavy job 500-kit-r26zk-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1252."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'    if (art->preview)\n        return kit_fail(art, "mf_preview: called twice'
SAB_AFTER=$'    if (0)\n        return kit_fail(art, "mf_preview: called twice'
