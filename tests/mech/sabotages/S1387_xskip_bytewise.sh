# S1387 — xskip reads the skip set BYTE-wise again instead of decoding the
# pattern character: under -e utf8 U+0085 (C2 85) is never seen as one
# character, so `(?x)a<U+0085>b` keeps a literal. K115, lane langfix.
SAB_ID="S1387-xskip-bytewise"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/xmode_utf8.rxt"
SAB_DESC="xskip_len: a byte >= 0x80 is tested as a byte, never decoded"
SAB_DOC_FIGURE="PREDICTED: at least 5 harness cases of tests/modifiers/xmode_utf8.rxt (every utf8 skip block). Canonical figure owed from run_sabotage_matrix.sh S1387."
SAB_COUNT=1
SAB_BEFORE="    if (c < 0x80) return xskip_char((unsigned)c) ? 1 : 0;"
SAB_AFTER="    return xskip_char((unsigned)c) ? 1 : 0;"
