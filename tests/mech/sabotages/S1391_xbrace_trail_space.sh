# S1391 — `\x{...}` stops skipping the spaces/tabs after its digits:
# `\x{41 }` refuses again (K117's trailing half). Lane langfix.
SAB_ID="S1391-xbrace-trail-space"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/xbrace_space.rxt"
SAB_DESC="esc_char_value: no skip_quant_space before \\x{...}'s closing brace"
SAB_DOC_FIGURE="PREDICTED: 4 harness cases of tests/base/xbrace_space.rxt (every trailing-pad accept). Canonical figure owed from run_sabotage_matrix.sh S1391."
SAB_COUNT=1
SAB_BEFORE="            skip_quant_space(cx);   /* ... around the digits, never inside */"
SAB_AFTER=""
