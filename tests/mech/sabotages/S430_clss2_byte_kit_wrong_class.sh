# S430 ([CLS-TREE] S2, lane clss2) -- A BYTE CLASS'S KIT MATCHER IS BUILT FROM
# ANOTHER CLASS'S SET: the byte kit's unsound direction.
#
# WHAT IT BREAKS. At the size-leaning `--tune` positions a scattered byte class
# is tested by `<prefix>_class_kit<N>`, whose sections are the class's own
# `ROWS` choice (`clsch[N].kit`). The plant emits matcher N from class N-1's
# kit, so every kit-read class but the first answers for its neighbour's set:
# it ADMITS bytes outside its own class and LOSES bytes inside it, in emitted
# code, at -2/-1 only. The default positions never read a kit matcher, so the
# default corpus stays green and the detector has to be a size-position one.
#
# THE DETECTOR is tests/codegen/run_clspack.sh PART 4 (arm `clspack`): the
# `site-10` witness carries ten distinct kit-read classes, and its --tune=-2
# artifact disagrees with the -fno-cls-kit build on the swept subjects.
SAB_ID="S430-clss2-byte-kit-wrong-class"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="clspack"
SAB_DESC="the class-table emission builds byte-class kit matcher N from class N-1's sectioning, so at --tune=-2/-1 every kit-read class but the first tests its neighbour's set (admits and loses bytes)"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2 measured it solo at landing; see docs/dev/lanes/clss2_report.md)."
SAB_REACH='"$PCREC" --engine=vm --tune=-2 -p rx -o - --pattern "([aeiou])[bcdfg][hjklm][npqrs][tvwxz][AEIOU][BCDFG][HJKLM][NPQRS][TVWXZ]"'
SAB_REACH_EXPECT='#define RX_VM_CLS_KIT 10'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                                      &v->clsch[i].kit);'
SAB_AFTER='                                      &v->clsch[i ? i - 1 : 0].kit);'
