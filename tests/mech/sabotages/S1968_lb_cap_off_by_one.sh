# S1968 ([VLOOKBEHIND] stage 1, design §7 W9) -- THE CAP BOUNDARY, 255/256.
SAB_ID="S1968-lb-cap-off-by-one"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the 255 cap admits 256'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W9 red ((?<=a{1,256})x compiles).'
SAB_COUNT=1
SAB_BEFORE='            if (out[i].hi > LA_LOOKBEHIND_VAR_MAX) {'
SAB_AFTER='            if (out[i].hi > LA_LOOKBEHIND_VAR_MAX + 1) {   /* SABOTAGE S1968 */'
