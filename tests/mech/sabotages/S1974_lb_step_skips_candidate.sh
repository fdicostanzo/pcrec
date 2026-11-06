# S1974 ([VLOOKBEHIND] stage 1, design §7 W14) -- THE STEP MOVES ONE CHARACTER.
SAB_ID="S1974-lb-step-skips-candidate"
SAB_FILE="src/enc/enc_byte.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the byte backend'\''s forward step moves two characters, skipping a candidate'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W14 red ((?<=\Ga{1,2})b on aab from 1) and W16; utf8 cells green.'
SAB_COUNT=1
SAB_BEFORE='"static inline size_t $_fwd_step(const unsigned char *s, size_t n, size_t pos)\n"
"{\n"
"    (void)s; (void)n;\n"
"    return pos + 1;\n"'
SAB_AFTER='"static inline size_t $_fwd_step(const unsigned char *s, size_t n, size_t pos)\n"
"{\n"
"    (void)s;\n"
"    return pos + 2 < n ? pos + 2 : n;  /* SABOTAGE S1974 */\n"'
