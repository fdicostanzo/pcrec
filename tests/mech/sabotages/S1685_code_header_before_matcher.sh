# S1685 ([INLINE-C] stage 2, design 9.1 S-IC30) -- A USER HEADER IS EMITTED
# BEFORE THE MATCHER. `code-header` lines belong after the matcher and its
# `#undef` block ([r1 A8]): a header can define anything, and before the
# matcher its macros and pragmas rewrite pcrec's own code. Here each one is
# also emitted in the artifact's prologue. Witness: tests/code/poison.h
# (arm 6), which poisons names a matcher uses.
SAB_ID="S1685-code-header-before-matcher"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="code"
SAB_DESC="every code-header line is also emitted in the artifact prologue, before the matcher"
SAB_REACH='"$PCREC" --allow-code=c --code-header '\''c:"poison.h"'\'' -o "$REACH_TMP/o.c" --pattern '\''hello(?C`c: return RX_PASS;`)world|[a-z]+@[a-z]+\.com'\'' && grep -cE "memchr|memcmp|memcpy" "$REACH_TMP/o.c" >/dev/null && echo REACH-POISON-NAMES'
SAB_REACH_EXPECT='REACH-POISON-NAMES'
SAB_COUNT=1
SAB_BEFORE='    if (need_string_h)
        pcrec_sb_puts(c, "#include <string.h>\n");'
SAB_AFTER='    if (need_string_h)
        pcrec_sb_puts(c, "#include <string.h>\n");
    for (int sab = 0; cx->emit_in && sab < cx->emit_in->ncode_headers; sab++)   /* SABOTAGE S1685 */
        pcrec_sb_printf(c, "#include %s\n", cx->emit_in->code_headers[sab].header);'
