# S1975 ([VLOOKBEHIND] stage 1, design §7 W16) -- THE NEAREST CANDIDATE IS TRIED.
SAB_ID="S1975-lb-nearest-never-tried"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the exhaustion test fires one character early, so the nearest candidate is never tried'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W16 red ((?<=a{1,2})x on bax). CORRECTED (lane vlbfix, review r4 F10): the predicted W3b cell (line 31 then, 33 now) stays GREEN, measured by the r4 CHECKS lens (failing lines 45 52 149 162 183 199 223); W3b is S1986'''s.'
SAB_COUNT=1
SAB_BEFORE='    pcrec_vm_b_branch(v->sb, vm_condf(v, "scan_position == (size_t)slot_values[%s]",'
SAB_AFTER='    pcrec_vm_b_branch(v->sb, vm_condf(v, "scan_position + 1 >= (size_t)slot_values[%s]",   /* SABOTAGE S1975 */'
