# S1967 ([VLOOKBEHIND] stage 1, design §7 W8) -- THE CAP COVERS EVERY BRANCH.
# PCRE2's err 200 applies to every alternative once any alternative's length
# varies, including a fixed one.
SAB_ID="S1967-lb-cap-varying-only"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the 255 cap is applied only to the branches that vary, not to every branch once one varies'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W8 red ((?<=a{300}|b{1,2})x compiles; libpcre2 err 200); vlb_accept (gate 3) red on the same shape.'
SAB_COUNT=1
SAB_BEFORE='            if (out[i].hi > LA_LOOKBEHIND_VAR_MAX) {'
SAB_AFTER='            if (out[i].lo < out[i].hi && out[i].hi > LA_LOOKBEHIND_VAR_MAX) {   /* SABOTAGE S1967 */'
