# S414 — [UTF-VALID] -fstartpos-guard=align MOVES ONE BYTE, NOT TO THE NEXT
# CHARACTER START (src/gen/emit_dfa.c, `pcrec_emit_startpos_guard`): the
# search form's seek increments once instead of looping until the backend's
# character-start predicate holds. On a two-byte character that happens to
# be the same thing; on a three- or four-byte one the search starts INSIDE
# the character — exactly the misaligned pointer D133's option exists to
# repair — and answers from there.
#
# WHAT SEES IT: tests/utfcheck's `align` set (every startpos of subjects with
# three- and four-byte characters) on the KA and A configs, which compare
# the aligned call against libpcre2 10.46 at the ALIGNED position.
SAB_ID="S414-align-seeks-one-byte"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="utfcheck"
SAB_DESC="the search form of -fstartpos-guard=align advances a mid-character startpos by one byte instead of to the next character start, so on a three- or four-byte character the search still starts inside it"
SAB_DOC_FIGURE="docs/design/utf_valid_design.md §10 (the alignment, D133). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S414"
SAB_REACH='"$PCREC" -p rx -e utf8 -fstartpos-guard=align -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "RX_STARTPOS_GUARD \"align\"" "$REACH_TMP/o.c" && echo REACH-ALIGN'
SAB_REACH_EXPECT="REACH-ALIGN"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%sif (!(%s == 0 || %s)) do %s++; while (!(%s));\n",
                        indent, posvar, g, posvar, g);'
SAB_AFTER='        pcrec_sb_printf(c, "%sif (!(%s == 0 || %s)) %s++;   /* SABOTAGE S414 */\n",
                        indent, posvar, g, posvar);'
