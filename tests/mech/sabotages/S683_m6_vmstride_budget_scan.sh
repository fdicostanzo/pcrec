#!/usr/bin/env bash
# S683 ([MEMFN] M6, lane m6) -- VMSTRIDE'S D91 BUDGET WRONG.
# C10 (run_deleg_sites.sh) holds D91's classification as its own literal
# (VMSTRIDE in D91_LOOP); the plant gives the row DELEG_SCAN.
SAB_ID="S683-m6-vmstride-budget-scan"
SAB_FILE="src/gen/memfn_sites.def"
SAB_SUITES="memfndeleg"
SAB_DESC='DELEG_SITES row VMSTRIDE is given D91 budget 1 (DELEG_SCAN) although the strided span loop runs at every VM step that enters a cursor-rung repeat: MF_P_INLOOP is lost for its sites'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): memfndeleg 2 failed / 3 passed (VMSTRIDE has DELEG_SCAN, D91 says DELEG_LOOP; the planted-control line moves with it). The matrix figure is owed at the slot."
SAB_REACH='bash "$TREE/tests/memfn/run_deleg_sites.sh"'
SAB_REACH_EXPECT='checks failed: 0'
SAB_REACH_POP='src/gen/memfn_sites.def|^DELEG_SITE\(VMSTRIDE, MF_OP_SKIP|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='DELEG_SITE(VMSTRIDE, MF_OP_SKIP, DELEG_H(MF_H_ADVANCE),
           MF_TK_SET, DELEG_LOOP, MF_USE_POSITION)'
SAB_AFTER='DELEG_SITE(VMSTRIDE, MF_OP_SKIP, DELEG_H(MF_H_ADVANCE),
           MF_TK_SET, DELEG_SCAN, MF_USE_POSITION)  /* SABOTAGE S683 */'
