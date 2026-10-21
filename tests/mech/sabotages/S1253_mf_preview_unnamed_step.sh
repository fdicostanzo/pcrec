#!/usr/bin/env bash
# S1253 ([MEMFN] R-26.6, lane r26zk; docs/design/kit_proof.md §2.5, §7; docs/dev/lanes/r26zk_report.md §4) --
# MF_PREVIEW ACCEPTED FOR A STEP THE KIT DOES NOT NAME.
#
# WHAT IT BREAKS. finder.c's fd_preview_step stops matching its previewable-step table, so any step some row names (B4, B1) is accepted: family D's unnamed-step refusals go red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c family D).
# The same text is run_proof.sh's plant S1253 (`run_proof.sh --plant S1253`).
SAB_ID="S1253-mf-preview-unnamed-step"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'mf_preview accepted for a step the kit does not name: finder.c\'s fd_preview_step stops matching its previewable-step table, so any step some row names (B4, B1) is accepted: family D\'s unnamed-step refusals go red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26zk, build/r26zk/light/plants_all.log): run_proof.sh --plant S1253 goes red. The mech figure is OWED to the heavy job 500-kit-r26zk-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1253."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'        if (strcmp(step, fd_previews[i])) continue;'
SAB_AFTER=$'        if (0) continue;'
