# S1962 ([VLOOKBEHIND] stage 1, design §7 W4) -- A VARYING BRANCH'S END-CHECK
# DECLINES ON BOTH POLARITIES (§5.3). Only a one-length branch's failed check is
# an inconsistency; a varying branch's is an ordinary candidate failing.
SAB_ID="S1962-lb-range-negative-internal"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the negative arm keeps the hard RX_R_INTERNAL return on a VARYING branch, where a candidate ending elsewhere is legitimate'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W4 red ((?<!ab?)x on acx: PCREC_ERR_INTERNAL for (2,3)).'
SAB_COUNT=1
SAB_BEFORE='        if (neg && !range) {'
SAB_AFTER='        if (neg) {   /* SABOTAGE S1962 */'
