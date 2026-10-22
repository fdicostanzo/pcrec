# S1386 — (?x)'s skip set loses the four Pattern_White_Space members above
# 0xFF (U+200E U+200F U+2028 U+2029), the K115 wrong answer: under -e utf8
# `(?x)a<U+2028>b` reads the separator as a literal again. Lane langfix.
SAB_ID="S1386-xskip-drops-unicode-space"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/modifiers/xmode_utf8.rxt"
SAB_DESC="xskip_char: U+200E U+200F U+2028 U+2029 removed from (?x)'s skip set"
SAB_DOC_FIGURE="PREDICTED: 4 harness cases of tests/modifiers/xmode_utf8.rxt (the U+200E, U+200F, U+2028 and U+2029 skip blocks). Canonical figure owed from run_sabotage_matrix.sh S1386."
SAB_COUNT=1
SAB_BEFORE="           c == 0x0d || c == 0x20 || c == 0x85 ||
           c == 0x200e || c == 0x200f || c == 0x2028 || c == 0x2029;"
SAB_AFTER="           c == 0x0d || c == 0x20 || c == 0x85;"
