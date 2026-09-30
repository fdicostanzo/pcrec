# S406 (land4, [OPT-CLSPACK] x [CLS-TREE] S4) -- `-fno-cls-kit` DOES NOT REACH THE ATOM ROW.
#
# ANSWER-NEUTRAL: D129 Q2 made `-fno-cls-kit` the one kit-level deny ("emit
# today's class forms"), and the shared atom table is a kit form (manager
# ruling on clspack_report.md §6 (a), 2026-09-30). A kit deny that leaves the
# atom table in place makes cls_identity's `-fno-cls-kit` == base identity
# fail and the axes sweep compare the table with itself. The plant drops the
# kit flag from the table selection's deny mask.
SAB_ID="S406-clspack-kit-deny-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack"
SAB_DESC="vm_cls_tables no longer maps PCREC_NO_CLS_KIT onto the atom row's deny, so -fno-cls-kit builds still share one atom table"
SAB_DOC_FIGURE="MEASURED solo 2026-09-30 at the land4 tip: reach:ok(1/1),clspack:1fail/24pass DETECTED -- [deny-kit] alone (RX_VM_CLS_ATOMS 12 where 0 is due under -fno-cls-kit)."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    unsigned deny = (cx->opt->flags & (PCREC_NO_CLS_PACK | PCREC_NO_CLS_KIT))'
SAB_AFTER='    unsigned deny = (cx->opt->flags & (PCREC_NO_CLS_PACK))'
