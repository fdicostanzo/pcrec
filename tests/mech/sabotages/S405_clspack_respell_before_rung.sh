# S405 ([OPT-CLSPACK], lane clspack) -- THE TABLE SELECTION RUNS BEFORE THE
# ENTRY RUNG IS CHOSEN.
#
# ANSWER-NEUTRAL, and the defect the lane's own first build had: the entry
# rung is chosen on the program's LENGTH, and the atom spelling of a table
# read is shorter than the bitmap spelling, so re-spelling first lets the
# table form move the rung. Measured on atom-reads (4,621 program bytes): rung
# `inline` and 2.5x the __text of its bitmap twin. The plant calls
# vm_cls_tables ahead of vm_plan_entry as well as after it.
SAB_ID="S405-clspack-respell-before-rung"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack"
SAB_DESC="vm_cls_tables re-spells the program before vm_plan_entry reads its length, so the atom table moves the entry rung and RX_VM_PROGRAM_BYTES"
SAB_DOC_FIGURE="(measured below at landing)"
SAB_REACH='"$PCREC" --engine=vm -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ][02468]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_ATOMS 12'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    vm_plan(&v, root, &pl);
    vm_plan_entry(&v, &pl, &en);
'
SAB_AFTER='    vm_plan(&v, root, &pl);
    vm_cls_tables(&v);
    vm_plan_entry(&v, &pl, &en);
'
