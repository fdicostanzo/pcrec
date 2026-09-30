# S406 (land4, [OPT-CLSPACK] x [CLS-TREE] S4) -- `-fno-cls-kit` DOES NOT REACH THE ATOM ROW.
#
# ANSWER-NEUTRAL: D129 Q2 made `-fno-cls-kit` the one kit-level deny ("emit
# today's class forms"), and the shared atom table is a kit form (manager
# ruling on clspack_report.md §6 (a), 2026-09-30). A kit deny that leaves the
# atom table in place makes cls_identity's `-fno-cls-kit` == base identity
# fail and the axes sweep compare the table with itself. The plant drops the
# kit flag from the table selection's deny mask.
# RE-ANCHORED 2026-09-30 (lane clss2fix, [CLS-TREE] S2 review fixes, D139):
# the flags-to-TAB_ROWS-deny mapping moved from vm_cls_tables into clskit.c's
# pcrec_clskit_tabdeny_of (the one mapping); the plant drops -fno-cls-kit from it,
# intent unchanged.
SAB_ID="S406-clspack-kit-deny-ignored"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clspack"
SAB_DESC="pcrec_clskit_tabdeny_of no longer maps PCREC_NO_CLS_KIT onto the atom row's deny, so -fno-cls-kit builds still share one atom table"
SAB_DOC_FIGURE="MEASURED solo 2026-09-30 at the land4 tip: reach:ok(1/1),clspack:1fail/24pass DETECTED -- [deny-kit] alone (RX_VM_CLS_ATOMS 12 where 0 is due under -fno-cls-kit)."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return (flags & (PCREC_NO_CLS_PACK | PCREC_NO_CLS_KIT)) ? 1u << CLSTD_ATOM : 0;'
SAB_AFTER='    return (flags & (PCREC_NO_CLS_PACK)) ? 1u << CLSTD_ATOM : 0;'
