# S264 — [OPT-ENDWIN] THE END-ANCHOR START WINDOW IS CLAMPED ONE BYTE TOO
# FEW (src/gen/emit_dfa.c, `pcrec_emit_end_window_clamp`), so a search over a
# long subject begins one byte AFTER the earliest position a match can start
# and a legal match at exactly that position is DELETED.
#
# THIS IS THE ONE ROW OF THE [OPTLOOP.1] BATCH-1 TRIO WITH A REAL ANSWER-LEVEL
# DETECTOR, and the asymmetry is worth stating because the other two rows
# (S263, S265) exist to certify they have none. [OPT-ANCHOR-VM] and
# [OPT-REQBYTE] remove only work an artifact would have done and thrown away;
# this mechanism MOVES THE POSITION A SEARCH STARTS AT, so an error in it
# loses matches rather than time.
#
# THE PLANT IS THE OFF-BY-ONE THAT AN IMPLEMENTATION ACTUALLY RISKS, not an
# arbitrary corruption: `eps` exists because `$`/`\Z` hold BEFORE A FINAL
# NEWLINE as well as at the subject's end, and dropping it is exactly what a
# reader who thinks "the match must end at n" would write. Under the plant,
# `abc$` on "…abc\n" starts its scan at the `b` and reports no match; on
# "…abc" (no trailing newline) it still starts one byte late and loses that
# match too, since `maxw` alone leaves no room for the earliest start.
#
# WHY IT IS THE SHARED EMITTER AND NOT ONE ENGINE'S SITE: both search entries
# call this one function, so the plant reaches the DFA route and the VM route
# at once — which is what makes a single row's detection a statement about
# the mechanism rather than about one emitter.
SAB_ID="S264-end-window-one-byte-narrow"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_DESC="the end-anchor start window's clamp raises search_from to subject_length - (W-1) instead of subject_length - W, so a search over a subject longer than the window begins one byte past the earliest position a match can start and a legal match there is lost — the \$-before-final-newline allowance is exactly the byte this drops, which is why tests/assertions/end_window.rxt carries every claim at a subject length that makes the clamp fire as well as at one that leaves it inert"
SAB_DOC_FIGURE="tests/harness/run.sh over tests/assertions/end_window.rxt is the detector (the long-subject rows of blocks 1, 2, 3, 6, 7, 8, 9 and 11 report nomatch or a shifted span where the file expects a match); tests/codegen/run_prechecks.sh §2.1b is the structural detector, reporting that each artifact's clamp does not carry its own stamped bound. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S264."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `abc$`
# stamps a window of 4 and emits the clamp this row plants on, so the function
# the plant edits really does run for this witness.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "abc\$" && grep -q "^#define RX_END_WINDOW \"4\"" "$REACH_TMP/o.c" && grep -q "search_from = subject_length - 4ULL;" "$REACH_TMP/o.c" && echo REACH-END-WINDOW-CLAMP-EMITTED'
SAB_REACH_EXPECT="REACH-END-WINDOW-CLAMP-EMITTED"
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c,
        "%sif (%s > %lluULL && %s < %s - %lluULL)\n"
        "%s    %s = %s - %lluULL;\n",
        indent, lenvar, (unsigned long long)w, posvar, lenvar,
        (unsigned long long)w,
        indent, posvar, lenvar, (unsigned long long)w);'
SAB_AFTER='    /* SABOTAGE S264: the window is one byte too FEW -- the $-before-
     * final-newline allowance dropped, so the earliest legal start is
     * outside the scanned range and that match is lost. */
    pcrec_sb_printf(c,
        "%sif (%s > %lluULL && %s < %s - %lluULL)\n"
        "%s    %s = %s - %lluULL;\n",
        indent, lenvar, (unsigned long long)w, posvar, lenvar,
        (unsigned long long)(w - 1),
        indent, posvar, lenvar, (unsigned long long)(w - 1));'
