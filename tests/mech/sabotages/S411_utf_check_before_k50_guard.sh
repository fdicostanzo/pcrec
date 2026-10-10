# S411 — [UTF-VALID] THE CHECK RUNS BEFORE THE K50 GUARD
# (src/gen/emit_dfa.c, `pcrec_emit_startpos_guard`): the precheck line is
# written above the caller-startpos refusal instead of below it. D133 (Q10,
# measured on 10.46, utf_valid_design.md §1.2) rules the guard FIRST: a
# mid-character startpos is PCREC_ERR_STARTPOS whether or not the subject is
# well-formed. With the order swapped, a mid-character startpos on an
# ill-formed subject — and, since the validator walks from a continuation
# byte there, on a well-formed one too — reads PCREC_ERR_UTF.
#
# WHAT SEES IT: tests/utfcheck's pinned §1.2 rows (`a` on `\xc3\xa9\xffa`
# from 1: libpcre2 -36) and every mid-character row of the other sets, on
# every -futf-check config: want -7, get -9.
SAB_ID="S411-utf-check-before-k50-guard"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="utfcheck"
SAB_DESC="the -futf-check precheck is emitted ABOVE the K50 caller-startpos guard, so a mid-character startpos answers PCREC_ERR_UTF where D133 (and libpcre2's BADUTFOFFSET) put the guard first"
SAB_DOC_FIGURE="docs/design/utf_valid_design.md §1.2 (the order, measured); docs/spec/match_api.md §9.4's Order bullet (#utf-check). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S411"
SAB_REACH='"$PCREC" -p rx -e utf8 -futf-check -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "return PCREC_ERR_STARTPOS;" "$REACH_TMP/o.c" && grep -qF "return PCREC_ERR_UTF;" "$REACH_TMP/o.c" && echo REACH-ORDER'
SAB_REACH_EXPECT="REACH-ORDER"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, pcrec_startpos_guard_text(cx, t, sizeof t, indent,
                                                   posvar, subjvar, lenvar));
        emit_utf_check(cx, c, indent, posvar, subjvar, lenvar);
        return;'
SAB_AFTER='        emit_utf_check(cx, c, indent, posvar, subjvar, lenvar);   /* SABOTAGE S411 */
        pcrec_sb_puts(c, pcrec_startpos_guard_text(cx, t, sizeof t, indent,
                                                   posvar, subjvar, lenvar));
        return;'
