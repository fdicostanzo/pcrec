# S409 — [UTF-VALID] THE VALIDATOR'S ASCII FAST PATH SKIPS A WINDOW'S FIRST
# BYTE (src/enc/enc_utf8.c, `$_valid_upto`): the eight-byte high-bit test
# masks out the window's first byte, so an ill-formed byte sitting at the
# start of an eight-byte window after an ASCII run is jumped over and the
# subject reads as well-formed. The byte-at-a-time path is untouched, so
# short subjects and every sequence the loop reaches outside a window still
# refuse; only the fast path's own reach moves.
#
# WHAT SEES IT: tests/utfcheck's `kinds` set drives one bad byte after k =
# 0..24 ASCII bytes, and the -futf-check configs then answer where
# libpcre2 10.46 refuses (and valid_upto returns n for PCRE2's startchar).
SAB_ID="S409-utf-fastpath-skips-window-lead"
SAB_FILE="src/enc/enc_utf8.c"
SAB_SUITES="utfcheck"
SAB_DESC="the subject validator's eight-byte ASCII fast path ignores the first byte of each window, so an ill-formed byte there after an ASCII run is skipped and -futf-check answers where PCRE2_UTF refuses"
SAB_DOC_FIGURE="docs/design/utf_valid_design.md §5 (the fast path, ruled Q8); tests/utfcheck/gen_cases.py's k = 0..24 windows. Exact re-run: bash tests/mech/run_sabotage_matrix.sh S409"
SAB_REACH='"$PCREC" -p rx -e utf8 -futf-check -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "0x8080808080808080ull" "$REACH_TMP/o.c" && grep -qF "return PCREC_ERR_UTF;" "$REACH_TMP/o.c" && echo REACH-FASTPATH'
SAB_REACH_EXPECT="REACH-FASTPATH"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"                if (w & 0x8080808080808080ull) break;\n"'
SAB_AFTER='"                if (w & 0x8080808080808000ull) break;   /* SABOTAGE S409 */\n"'
