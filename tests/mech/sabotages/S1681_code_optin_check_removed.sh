# S1681 ([INLINE-C] stage 2, design 9.1 S-IC9) -- THE OPT-IN CHECK IS
# REMOVED. pcrec_compile resolves EVERY code language as granted instead of
# the caller's `allow_code`, so a pattern string becomes code with no one's
# say-so. Witnesses: tests/code/t2/t2.rxt (the T2 check, design 5.7: a
# segment in a section without the opt-in expects the refusal), the refusal
# and entry-point arms, the library check.
SAB_ID="S1681-code-optin-check-removed"
SAB_FILE="src/core/compile.c"
SAB_SUITES="code"
SAB_DESC="pcrec_compile grants every code language whatever allow_code says, so embedded code compiles without --allow-code"
SAB_REACH='"$PCREC" -o "$REACH_TMP/o.c" --pattern '\''a(?C`c: return RX_PASS;`)b'\'' 2>&1; true'
SAB_REACH_EXPECT="which only the command-line option --allow-code=c"
SAB_COUNT=1
SAB_BEFORE='        if (pcrec_code_grant_resolve(defo.allow_code, &grant, gerr,'
SAB_AFTER='        if (pcrec_code_grant_resolve(pcrec_code_all_langs() /* SABOTAGE S1681 */, &grant, gerr,'
