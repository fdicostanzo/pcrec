# S1984 ([VLOOKBEHIND] review r4 F15) -- THE COUNT PASS SIZES THE LOW SUB-BLOCK
# TOO LONG (two slots per varying branch). Harmless slots, but the count pass
# and the emitter disagree; the equality check after emission refuses.
SAB_ID="S1984-lb-low-count-long"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the count pass gives each varying lookbehind branch two low slots, so the sub-block is larger than the emitter takes'
SAB_DOC_FIGURE='PREDICTED (lane vlbfix, measured on 3 patterns): varying-branch cells refuse at compile ("sized for 2 branches and 1 were emitted"); one-length cells green.'
SAB_COUNT=1
SAB_BEFORE='        if (vm_lb_varies(a, i)) {
            v->nlblow++;'
SAB_AFTER='        if (vm_lb_varies(a, i)) {
            v->nlblow += 2;   /* SABOTAGE S1984 */'
