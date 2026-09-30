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
# RE-ANCHORED 2026-09-30 (lane clss2fix, [CLS-TREE] S2 review fixes, D139):
# the flags-to-ROWS-deny mapping moved from vm_cls into clskit.c's one
# mapping (DENY_FLAG, read by pcrec_clskit_deny_of for the VM AND the scan
# edge); the plant unmaps -fno-cls-kit there, intent unchanged and now
# reaching both sites.
# REACH PAIRED (review C-L6): the probe reads the witness WITH and WITHOUT
# the deny, so "denied" (1 -> 0) is told apart from "never fired" (0 -> 0).
SAB_ID="S431-clss2-byte-kit-deny-ignored"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="tunedial clspack"
SAB_DESC="pcrec_clskit_deny_of no longer maps PCREC_NO_CLS_KIT onto the byte-kit row deny, so -fno-cls-kit builds at --tune=-2/-1 still test scattered byte classes with kit matchers (VM class reads and DFA scan edges alike)"
SAB_DOC_FIGURE="Read the current figure from a run (lane clss2 measured it solo at landing; see docs/dev/lanes/clss2_report.md)."
SAB_REACH='echo "KIT-ON $("$PCREC" --engine=vm --tune=-2 -p rx -o - --pattern "[aeiou]+x" | grep "_VM_CLS_KIT ")"; echo "KIT-OFF $("$PCREC" --engine=vm --tune=-2 -fno-cls-kit -p rx -o - --pattern "[aeiou]+x" | grep "_VM_CLS_KIT ")"'
SAB_REACH_EXPECT='KIT-ON #define RX_VM_CLS_KIT 1
KIT-OFF #define RX_VM_CLS_KIT 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [CLSD_BYTE_KIT]  = PCREC_NO_CLS_KIT,'
SAB_AFTER='    [CLSD_BYTE_KIT]  = 0,'
