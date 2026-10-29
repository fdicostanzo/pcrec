# S1680 ([INLINE-C] stage 2, design 9.1 S-IC8) -- AN UNKNOWN ATTRIBUTE IS
# ACCEPTED. The attribute list a code segment's tag carries (``(?C`c,once:
# ...`)``) is read by the same reader as a binding's; an unknown item is
# skipped instead of refused, so a typo (`c,onec:`) silently drops the
# author's declaration. Witness: tests/code/run_code_tests.sh arm 3, "an
# unknown attribute is refused (S-IC8)".
SAB_ID="S1680-code-unknown-attribute-accepted"
SAB_FILE="src/parse/mod_callouts.c"
SAB_SUITES="code"
SAB_DESC='the callout attribute reader skips an unknown item instead of refusing it, so a segment tagged c,bogus compiles'
SAB_REACH='"$PCREC" --allow-code=c -o "$REACH_TMP/o.c" --pattern '\''a(?C`c,bogus: return RX_PASS;`)b'\'' 2>&1; true'
SAB_REACH_EXPECT="unknown callout attribute 'bogus'"
SAB_COUNT=1
SAB_BEFORE='        if (k < 0)
            return pcrec_ext_msgf(cx, "unknown callout attribute '\''%s'\'' "'
SAB_AFTER='        if (k < 0) { if (j == n) return NULL; i = j + 1; continue; }   /* SABOTAGE S1680 */
        if (k < 0)
            return pcrec_ext_msgf(cx, "unknown callout attribute '\''%s'\'' "'
