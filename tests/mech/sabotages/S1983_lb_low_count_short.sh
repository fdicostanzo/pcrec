# S1983 ([VLOOKBEHIND] review r4 F15) -- THE COUNT PASS SIZES THE LOW SUB-BLOCK
# ONE SHORT (it skips each lookbehind's first varying branch). The emitter's
# take then runs past the sub-block, the K27 class; `vm_take_lblow` refuses.
SAB_ID="S1983-lb-low-count-short"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the count pass skips the first varying branch of each lookbehind, so the low sub-block is one slot short'
SAB_DOC_FIGURE='PREDICTED (lane vlbfix, measured on 3 patterns): varying-branch cells refuse at compile ("overflowed (branch 1 of 0 ...)"); one-length cells green.'
SAB_COUNT=1
SAB_BEFORE='        if (vm_lb_varies(a, i)) {
            v->nlblow++;'
SAB_AFTER='        if (vm_lb_varies(a, i)) {
            v->nlblow += i > 0;   /* SABOTAGE S1983 */'
