#!/usr/bin/env bash
# S1251 ([MEMFN] R-26.6, lane r26zk; docs/design/kit_proof.md §2.5, §7; docs/dev/lanes/r26zk_report.md §4) --
# MF_PREVIEW ACCEPTED AFTER THE FIRST DEFINE.
#
# WHAT IT BREAKS. compose.c drops mf_preview's after-the-first-define refusal: family D's `mf_preview after the first define` goes red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c family D).
# The same text is run_proof.sh's plant S1251 (`run_proof.sh --plant S1251`).
SAB_ID="S1251-mf-preview-after-define"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'mf_preview accepted after the first define: compose.c drops mf_preview\'s after-the-first-define refusal: family D\'s `mf_preview after the first define` goes red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26zk, build/r26zk/light/plants_all.log): run_proof.sh --plant S1251 goes red. The mech figure is OWED to the heavy job 500-kit-r26zk-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1251."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'    if (art->nsites)\n        return kit_fail(art, "mf_preview: called after'
SAB_AFTER=$'    if (0)\n        return kit_fail(art, "mf_preview: called after'
