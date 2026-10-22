# S1390 — `\x{` stops skipping the spaces/tabs before its digits: `\x{ 41}`
# refuses again (K117's leading half). Lane langfix.
SAB_ID="S1390-xbrace-lead-space"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/xbrace_space.rxt"
SAB_DESC="esc_char_value: no skip_quant_space after \\x{'s opening brace"
SAB_DOC_FIGURE="PREDICTED: 6 harness cases of tests/base/xbrace_space.rxt (every leading-pad accept). Canonical figure owed from run_sabotage_matrix.sh S1390."
SAB_COUNT=1
SAB_BEFORE="            skip_quant_space(cx);   /* K117: 10.46 admits spaces/tabs */"
SAB_AFTER=""
