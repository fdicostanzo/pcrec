# S1389 — \p{Nd} admitted in a name's FIRST position: `(?<٣>a)` (U+0663)
# compiles where PCRE2 says error 144. K116's first-character rule, lane
# langfix.
SAB_ID="S1389-ngname-digit-first"
SAB_FILE="src/parse/mod_named_groups.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/named_groups/utf8_names.rxt"
SAB_DESC="ng_name_char: \\p{Nd} accepted in the leading position too"
SAB_DOC_FIGURE="PREDICTED: 1 harness case of tests/named_groups/utf8_names.rxt (the U+0663-first perr). Canonical figure owed from run_sabotage_matrix.sh S1389."
SAB_COUNT=1
SAB_BEFORE="    return ng_in_prop(cx, \"L\", cp) || (!first && ng_in_prop(cx, \"ND\", cp))"
SAB_AFTER="    return ng_in_prop(cx, \"L\", cp) || ng_in_prop(cx, \"ND\", cp)"
