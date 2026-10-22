#!/usr/bin/env bash
# S1256 ([MEMFN] R-26.6, lane r26zk; docs/design/kit_proof.md §2.5, §7; docs/dev/lanes/r26zk_report.md §4) --
# NONE ACCEPTED ON A REPORT SITE (THE ROW APPLIES WHERE IT CANNOT PROVE).
#
# WHAT IT BREAKS. finder.c's REPORT row drops its PROOF_EXACT fact, so it replies on a REPORT site its form cannot prove exactly instead of not applying (K96): family D's does-not-apply refusal goes red.
#
# WHERE IT IS SEEN (arm memfnfinder, tests/memfn/run_finder.sh, part `proof`:
# tests/memfn/run_proof.sh over tests/memfn/proof_check.c family D).
# The same text is run_proof.sh's plant S1256 (`run_proof.sh --plant S1256`).
SAB_ID="S1256-report-none-accepted"
SAB_FILE="memfn/src/finder.c"
SAB_SUITES="memfnfinder"
SAB_DESC=$'none accepted on a report site (the row applies where it cannot prove): finder.c\'s REPORT row drops its PROOF_EXACT fact, so it replies on a REPORT site its form cannot prove exactly instead of not applying (K96): family D\'s does-not-apply refusal goes red'
SAB_DOC_FIGURE="Plant run 2026-10-21 (lane r26zk, build/r26zk/light/plants_all.log): run_proof.sh --plant S1256 goes red. The mech figure is OWED to the heavy job 500-kit-r26zk-heavy; read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1256."
# DECLARED EQUIVALENT (D172 S2 commit 6, lane wsc6): the context spans and
# `absent` retired (R1), and with them every old-field REPORT site on which
# the composer's chosen form proves other than EXACTLY the REQUIRED sets
# (every REPORT term is REQUIRED and every row tests its REQUIRED terms; the
# last witness was family D's two-offset SATISFIES item). The REPORT row's
# exactness fact and its comparison are unobservable until S3 retires RPT,
# kit_report_exact, SF_PROOF_EXACT and FF_PROOF (window_site.md §4; the kit
# manager's R3 keeps them until then).
SAB_EXPECT=UNDETECTED
SAB_EXPECT_REASON="equivalent since D172 S2 commit 6: no REPORT site exists that the REPORT row's form cannot prove exactly (the context spans and absent retired), so the exactness test is unobservable until S3 retires RPT"
SAB_COUNT=1
SAB_BEFORE=$'{ "RPT", FD_FIND, KN_P, SF_SPAN0 | SF_PROOF_EXACT, 0,'
SAB_AFTER=$'{ "RPT", FD_FIND, KN_P, SF_SPAN0, 0,'
