#!/usr/bin/env bash
# S1254 ([MEMFN] R-26.6, lane r26zk; docs/design/kit_proof.md §2.5, §7; docs/dev/lanes/r26zk_report.md §4) --
# A --memfn= SPELLING OF MF_PREVIEW ACCEPTED.
#
# WHAT IT BREAKS. options.def gains a `preview` row, so mf_opts_check accepts `--memfn=preview`: family D's spelling refusals and its no-row check go red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c family D).
# The same text is run_proof.sh's plant S1254 (`run_proof.sh --plant S1254`).
SAB_ID="S1254-memfn-spelling-of-preview"
SAB_FILE="memfn/src/options.def"
SAB_SUITES="memfnfinder"
SAB_DESC=$'a --memfn= spelling of mf_preview accepted: options.def gains a `preview` row, so mf_opts_check accepts `--memfn=preview`: family D\'s spelling refusals and its no-row check go red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26zk, build/r26zk/light/plants_all.log): run_proof.sh --plant S1254 goes red. The mech figure is OWED to the heavy job 500-kit-r26zk-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1254."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'MF_OPT("vrun-w32", MF_OPT_DENY,'
SAB_AFTER=$'MF_OPT("preview", MF_OPT_PAIR, MF_B_ANY, MF_L_SCALAR, "plant")\nMF_OPT("vrun-w32", MF_OPT_DENY,'
