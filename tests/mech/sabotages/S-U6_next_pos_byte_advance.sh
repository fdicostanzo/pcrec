# S-U6 ([M5.0] stage 2; utf8_design.md §8.2) -- THE UTF8 NEXT_POS IS `pos + 1`.
#
# THE CLAIM: `$_next_pos` under utf8 answers the next CHARACTER BOUNDARY
# (§5.1), which is what keeps `docs/spec/match_api.md` §3.1's find-all loop
# off mid-character positions after an empty match. The sabotage is the byte
# backend's body — the `+1` every pre-seam caller would have written, and the
# bug the entry exists to delete.
#
# WHAT GOES WRONG: only a find-all over an empty (or empty-matching) pattern
# on a multi-byte subject sees it — the loop lands INSIDE a character, and a
# zero-width artifact then reports matches at positions that are not
# boundaries (4 "matches" on the 2-character `αβ` instead of 3). No single
# rx_search call can reach it, which is why the row's detector must be a
# find-all cell.
SAB_ID="S-U6-next-pos-byte-advance"
SAB_FILE="src/gen/enc/enc_utf8.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8"
SAB_DESC="the utf8 backend's next_pos body becomes pos + 1, so the find-all loop advances into the middle of a multi-byte character after an empty match and reports non-boundary positions"
SAB_DOC_FIGURE="PREDICTED (§8.2): tests/utf8 find-all cells over multi-byte subjects red. DEMONSTRATED at stage 2 pre-corpus: the match_api §3.1 loop over CE B1 CE B2 with pattern '' reports boundaries 0,2,4 clean and 0,1,2,3,4 sabotaged."
SAB_REACH='"$PCREC" -e utf8 -p rx -o - -- ""'
SAB_REACH_EXPECT='Pattern:  */'
# RE-POINTED 2026-09-05: the stage-2 lane wrote this population against a
# GUESSED corpus filename; the promoted D27 corpus (merge 698eea61) landed
# with the axis naming, so the pop line named a file that does not exist and
# the first full mech run read the row UNREACHED-UNEXPECTED. Floor unchanged
# where it still holds (K35: rounded down); measured count in parens.
SAB_REACH_POP='tests/utf8/axis09_nextpos_findall.rxt|^pattern|14'  # measured 20
# [2026-09-05, first solo run after the re-point]: REACHED but UNDETECTED —
# a next_pos byte-advance is observable only through the find-all protocol
# AFTER AN EMPTY MATCH AT A MULTI-BYTE BOUNDARY, and axis09 holds no such
# cell (its K49 cell is a nomatch; its ms cells' matches are nonzero-width,
# so the caller advances by the match, never through next_pos). The
# S150-family holding state per ../CLAUDE.md's doctrine: the row stays, the
# claim is stated, and the WITNESS THAT CLOSES IT is named below — an
# oracle-backed axis09 cell 'empty match, then a multi-byte character,
# find-all must continue at the character boundary', blocked on the
# tests/utf8 libpcre2 differential instrument (the corpus follow-up in the
# admin queue) for its oracle. When that cell lands, this flips NOW
# DETECTED and the expectation is re-measured and changed.
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='"    size_t i = pos + 1;\n"
"    while (i < n && (s[i] & 0xC0) == 0x80) i++;\n"
"    return i;\n"'
SAB_AFTER='"    (void)s; (void)n;\n"
"    return pos + 1;  /* SABOTAGE S-U6: the byte body */\n"'
