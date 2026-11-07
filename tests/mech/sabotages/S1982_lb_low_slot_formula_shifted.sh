# S1982 ([VLOOKBEHIND] review r4 F15, the review's plant PA) -- THE LOW SLOT
# FORMULA DRIFTS ONE UP. Every varying branch's nearest start lands on the
# next family's slot (a lookaround mark); before the guard this compiled
# silently and the artifact crashed or hung (`(?<=a{1,2})x` on "abxa":
# SIGSEGV, measured). `vm_take_lblow` refuses the compile instead.
SAB_ID="S1982-lb-low-slot-formula-shifted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='vm_slot_lblow names the slot one above its own, so a varying lookbehind branch writes another family'\''s slot'
SAB_DOC_FIGURE='PREDICTED (lane vlbfix, measured on 3 patterns): every varying-branch cell refuses at compile with "internal error: the lookbehind low sub-block overflowed"; one-length cells green.'
SAB_COUNT=1
SAB_BEFORE='    return vm_slot_low(v, v->nlow_total - v->nlblow_total + j);'
SAB_AFTER='    return vm_slot_low(v, v->nlow_total - v->nlblow_total + j + 1);   /* SABOTAGE S1982 */'
