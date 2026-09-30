# S431 ([CLS-TREE] S2, lane clss2) -- `-fno-cls-kit` DOES NOT REACH THE BYTE
# ROWS.
#
# ANSWER-NEUTRAL: D129 Q2's one kit-level deny means "emit today's class
# forms", and at S2 that includes the byte classes' kit matchers. The plant
# drops the flag from the per-class `ROWS` deny mask, so a -fno-cls-kit build
# at --tune=-2/-1 still reads kit matchers. No answer moves, so the detectors
# are structural: run_tune_dial.sh §3e's `scattered-denied` rows (the class
# tested as `kit` where the deny says `bitmap`) and run_clspack.sh PART 4's
# non-vacuity check (the denied build carries kit matchers).
SAB_ID="S431-clss2-byte-kit-deny-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="tunedial clspack"
SAB_DESC="vm_cls no longer maps PCREC_NO_CLS_KIT onto the byte-kit row's deny, so -fno-cls-kit builds at --tune=-2/-1 still test scattered byte classes with kit matchers"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2 measured it solo at landing; see docs/dev/lanes/clss2_report.md)."
SAB_REACH='"$PCREC" --engine=vm --tune=-2 -fno-cls-kit -p rx -o - --pattern "[aeiou]+x"'
SAB_REACH_EXPECT='#define RX_VM_CLS_KIT 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                       ((fl & PCREC_NO_CLS_KIT) ? 1u << CLSD_BYTE_KIT : 0)'
SAB_AFTER='                       (0)'
