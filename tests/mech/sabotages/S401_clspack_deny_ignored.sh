# S401 ([OPT-CLSPACK], lane clspack) -- `-fno-cls-pack` DOES NOT REACH THE ROW.
#
# ANSWER-NEUTRAL: the deny is the answer-identity control axis, and a deny
# that is silently ignored makes `make test-axes` and run_clspack.sh's own
# differential compare the atom table with itself. The plant drops the flag
# from the table selection's deny mask (re-anchored at land4: the mask now also
# carries -fno-cls-kit, which S406 covers).
SAB_ID="S401-clspack-deny-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack"
SAB_DESC="vm_cls_tables no longer maps PCREC_NO_CLS_PACK onto the atom row's deny (only -fno-cls-kit still does), so -fno-cls-pack builds still share one atom table"
SAB_DOC_FIGURE="RE-MEASURED solo 2026-09-30 at the land4 tip (run_clspack.sh gained [deny-kit], 24 -> 25 checks): clspack:5fail/20pass -- the three PART 1 site-artifact rows and [deny] DETECTED. The fifth failure is [deny-kit], which compares its bitmap count against the -fno-cls-pack artifact the plant has left packed."
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    unsigned deny = (cx->opt->flags & (PCREC_NO_CLS_PACK | PCREC_NO_CLS_KIT))'
SAB_AFTER='    unsigned deny = (cx->opt->flags & (PCREC_NO_CLS_KIT))'
