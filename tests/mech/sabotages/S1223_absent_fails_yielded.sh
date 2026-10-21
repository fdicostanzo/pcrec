#!/usr/bin/env bash
# S1223 ([MEMFN] R-26 Z1, lane r26z1fix; docs/design/kit_proof.md §3-§4, docs/dev/lanes/r26z1_report.md §4) --
# AN ABSENT-FAILS CANDIDATE YIELDED.
#
# WHAT IT BREAKS. Generic.c renders every context item as SATISFIES: a candidate the contract refuses is yielded, and the byte-loop oracle finds it extra.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c and proof_run.c).
# The same text is run_proof.sh's plant S1223 (`run_proof.sh --plant S1223`).
SAB_ID="S1223-absent-fails-yielded"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'an absent-FAILS candidate yielded: generic.c renders every context item as SATISFIES: a candidate the contract refuses is yielded, and the byte-loop oracle finds it extra'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26z1, build/r26/plants.log): run_proof.sh --plant S1223 goes red. The mech figure is OWED to the heavy job 500-kit-r26z1-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1223."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'if (p->span_class != MF_SPAN_CONTEXT || p->absent != MF_ABSENT_SATISFIES)'
SAB_AFTER=$'if (p->span_class != MF_SPAN_CONTEXT)'
