# S410 — [UTF-VALID] THE SUBJECT VALIDATOR ACCEPTS SURROGATES
# (src/enc/enc_utf8.c, `$_valid_upto`): the U+D800..U+DFFF exclusion is
# dropped, so `ED A0 80` reads as a well-formed character. The automaton's
# own classes still exclude it, so no MATCH moves — only the refusal set and
# the offset do, which is why nothing but the check's differential sees it.
#
# WHAT SEES IT: tests/utfcheck's `kinds` set (two surrogate sequences at
# three depths) and the §1 pinned row `a` on `ab\xed\xa0\x80` (libpcre2 -16
# at 2): the -futf-check configs answer, or report a later offset, where
# libpcre2 10.46 refuses at the surrogate's lead. It is also the shared
# validator's `var_valid` caller's defect (one validator, D133 Q7).
SAB_ID="S410-utf-validator-surrogate-accepted"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="utfcheck"
SAB_DESC="the subject validator stops excluding UTF-16 surrogates (U+D800..U+DFFF), so -futf-check accepts a subject PCRE2_UTF refuses and valid_upto misses the offset"
SAB_DOC_FIGURE="docs/design/utf_valid_design.md §1.1 (surrogate: -16 at the lead). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S410"
SAB_REACH='"$PCREC" -p rx -e utf8 -futf-check -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "0xD800u" "$REACH_TMP/o.c" && echo REACH-SURROGATE'
SAB_REACH_EXPECT="REACH-SURROGATE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (c < floor || c > 0x10FFFFu || (c >= 0xD800u && c <= 0xDFFFu))\n"'
SAB_AFTER='"        if (c < floor || c > 0x10FFFFu)   /* SABOTAGE S410 */\n"'
