# S401 ([OPT-CLSPACK], lane clspack) -- `-fno-cls-pack` DOES NOT REACH THE ROW.
#
# ANSWER-NEUTRAL: the deny is the answer-identity control axis, and a deny
# that is silently ignored makes `make test-axes` and run_clspack.sh's own
# differential compare the atom table with itself. The plant drops the flag
# from the table selection's deny mask.
SAB_ID="S401-clspack-deny-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack"
SAB_DESC="vm_cls_tables no longer maps PCREC_NO_CLS_PACK onto the atom row's deny, so -fno-cls-pack builds still share one atom table"
SAB_DOC_FIGURE="MEASURED solo 2026-09-30 at the clspack tip: clspack:4fail/16pass -- the three PART 1 site-artifact rows and [deny] DETECTED."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    unsigned deny = (cx->opt->flags & PCREC_NO_CLS_PACK) ? 1u << CLSTD_ATOM : 0;'
SAB_AFTER='    unsigned deny = 0;'
