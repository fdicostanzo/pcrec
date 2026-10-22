# S1388 — the group-name grammar ignores the encoding (ASCII only, the
# pre-K116 rule): `(?<é>a)` under -e utf8 refuses again. Lane langfix.
SAB_ID="S1388-ngname-ascii-only"
SAB_FILE="src/parse/mod_named_groups.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/named_groups/utf8_names.rxt"
SAB_DESC="ng_name_char: a byte >= 0x80 is never a name character, whatever the encoding"
SAB_DOC_FIGURE="PREDICTED: the accepting blocks of tests/named_groups/utf8_names.rxt (about 14 cases). Canonical figure owed from run_sabotage_matrix.sh S1388."
SAB_COUNT=1
SAB_BEFORE="    if (pcrec_enc_by_id(cx->opt->encoding)->max_cp <= 0xFFu) return 0;"
SAB_AFTER="    return 0;"
