# S1978 ([VLOOKBEHIND] stage 1, design §7 fwd_step (ii)) -- ONE CHARACTER, NOT ONE BYTE.
SAB_ID="S1978-fwd-step-utf8-byte"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="encoding harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the utf8 $_fwd_step body steps one BYTE'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): encoding checks RED on K49'\''s boundary tie (fwd_step vs next_pos) and its utf8 non-vacuity; W14 utf8 cells red.'
SAB_COUNT=1
SAB_BEFORE='"static inline size_t $_fwd_step(const unsigned char *s, size_t n, size_t pos)\n"
"{\n"
"    size_t i = pos + 1;\n"
"    while (i < n && (s[i] & 0xC0) == 0x80) i++;\n"
"    return i;\n"'
SAB_AFTER='"static inline size_t $_fwd_step(const unsigned char *s, size_t n, size_t pos)\n"
"{\n"
"    (void)s; (void)n;\n"
"    return pos + 1;  /* SABOTAGE S1978 */\n"'
