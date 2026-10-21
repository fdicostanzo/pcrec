#!/usr/bin/env bash
# S1255 ([MEMFN] R-26.6, lane r26zk; docs/design/kit_proof.md §2.5, §7; docs/dev/lanes/r26zk_report.md §4) --
# A REPORT SITE WHOSE PROVEN[D] IS NOT THE REQUIRED SET ACCEPTED.
#
# WHAT IT BREAKS. compose.c's kit_report_exact compares only span 0's offsets (d >= 0), so a REPORT site whose class leaves a REQUIRED context offset unproven (a two-offset SATISFIES item) is served: family D's does-not-apply refusal goes red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c family D).
# The same text is run_proof.sh's plant S1255 (`run_proof.sh --plant S1255`).
SAB_ID="S1255-report-proof-not-equal"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'a report site whose proven[d] is not the required set accepted: compose.c\'s kit_report_exact compares only span 0\'s offsets (d >= 0), so a REPORT site whose class leaves a REQUIRED context offset unproven (a two-offset SATISFIES item) is served: family D\'s does-not-apply refusal goes red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26zk, build/r26zk/light/plants_all.log): run_proof.sh --plant S1255 goes red. The mech figure is OWED to the heavy job 500-kit-r26zk-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1255."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE=$'    return !memcmp(req, c.proven, sizeof req);'
SAB_AFTER=$'    return !memcmp(req[-MF_PROOF_LO], c.proven[-MF_PROOF_LO], sizeof req - (size_t)(-MF_PROOF_LO) * 32);'
