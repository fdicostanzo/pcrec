#!/usr/bin/env bash
# S1225 ([MEMFN] R-26 Z1, lane r26z1fix; docs/design/kit_proof.md §3-§4, docs/dev/lanes/r26z1_report.md §4) --
# AN OVER-FILTER ON AN OPTIONAL POSITION.
#
# WHAT IT BREAKS. Generic.c tests an OPTIONAL SET term with one member fewer: a candidate the contract yields is filtered out, and the oracle finds it missing.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c and proof_run.c).
# The same text is run_proof.sh's plant S1225 (`run_proof.sh --plant S1225`).
SAB_ID="S1225-optional-position-overfilter"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'an over-filter on an OPTIONAL position: generic.c tests an OPTIONAL SET term with one member fewer: a candidate the contract yields is filtered out, and the oracle finds it missing'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26z1, build/r26/plants.log): run_proof.sh --plant S1225 goes red. The mech figure is OWED to the heavy job 500-kit-r26z1-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1225."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'            if (tm->kind == MF_T_SET) {\n                if (member_test(rc, b, tm, id, bx)) {'
SAB_AFTER=$'            if (tm->kind == MF_T_SET) {\n                mf_term nt = *tm;\n                for (int q = 0; tm->need == MF_OPTIONAL && q < 256; q++)\n                    if (nt.set[q >> 3] >> (q & 7) & 1) { nt.set[q >> 3] &= (uint8_t)~(1u << (q & 7)); break; }\n                if (member_test(rc, b, &nt, id, bx)) {'
