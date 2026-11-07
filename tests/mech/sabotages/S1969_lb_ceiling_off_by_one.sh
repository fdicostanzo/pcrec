# S1969 ([VLOOKBEHIND] stage 1, design §7 W9b) -- THE CEILING BOUNDARY, 65535/65536.
SAB_ID="S1969-lb-ceiling-off-by-one"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the 65535 ceiling admits 65536'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W9b red ((?<=a{65535}b)x and (?<=(?:a{1000}){66})x... the first compiles; libpcre2 err 187).'
SAB_COUNT=1
SAB_BEFORE='        if (hi > LA_LOOKBEHIND_BRANCH_MAX) return LBW_CEILING;'
SAB_AFTER='        if (hi > LA_LOOKBEHIND_BRANCH_MAX + 1) return LBW_CEILING;   /* SABOTAGE S1969 */'
