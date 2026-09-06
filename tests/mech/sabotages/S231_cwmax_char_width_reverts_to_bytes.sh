# S231 ([ENCCHK-DD12A] admin row) — tests/mrl/cwmax_check.c's `char_width`
# helper degenerates back into a BYTE count, reproducing the exact K49-era
# unit mismatch the 2026-09-05 repair fixed.
#
# THIS IS A REAL PAST BUG RESTORED, not an invented one (the S69/S229
# shape): before that repair this file compared an ORACLE SPAN in bytes
# against `pcrec_cwmax`, a CHARACTER quantity, and 21 cells of
# axis01_encoded_length.rxt read as false CHECK 2 violations ("span 2
# EXCEEDS cwmax=1" on a single two-byte character). The fix replaced the
# byte count with a one-line, independently-sourced character count (a
# non-continuation-byte scan, sharing no code with pcrec's own notion of a
# boundary). This row deletes that scan and falls back to `end - start`
# again -- the literal pre-repair spelling.
#
# WHY THIS IS THE PLANT WORTH ENCODING PERMANENTLY. tests/mrl/CLAUDE.md
# records this exact edit as one of two "validated in the failing
# direction" demonstrations behind the repair's own two population floors
# (docs/dev/known_issues.md K52's sibling admin obligation, [ENCCHK-DD12A],
# is what chartered turning both into permanent mech rows rather than a
# one-time manual note) -- floor (ii), "at least one compared span's byte
# width exceeds its character width", is exactly what a byte-count
# `char_width` can never produce (byte width and "character" width are now
# the SAME number for every span), so the floor fires by construction.
#
# AND IT DOES MORE THAN TRIP THE FLOOR, MEASURED (scratch build, same tree,
# whole corpus): floor (ii) fires (0 multibyte spans), the utf8 block
# population itself stays fully intact (216/307, unlike S230's plant, which
# is the point of keeping these as two separate rows rather than one edit --
# S230's detector is "the reader stopped resolving encodings", this one's is
# "the resolved encoding's spans are measured in the wrong unit", and a
# single row could not tell them apart), and CHECK 2 reports 84 REAL
# violations reproducing the pre-repair defect on today's larger utf8 corpus
# (e.g. `(?:α|β)` and `[αβ]` reading "span 2 characters EXCEEDS cwmax=1").
#
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS: the reach probe
# builds and runs the SAME checker binary the `mrl` arm's §8 runs, on the
# CLEAN tree, and reads its own printed counter for the multibyte-span
# population -- not a re-derivation of what that population ought to be.
SAB_ID="S231-cwmax-char-width-reverts-to-bytes"
SAB_FILE="tests/mrl/cwmax_check.c"
SAB_SUITES="mrl"
SAB_DESC="cwmax_check.c's independent character-count predicate (char_width) degenerates back into the raw byte count it replaced at the 2026-09-05 K49-adjacent repair, so CHECK 2 compares byte-width oracle spans against a character-tier cwmax again -- the exact unit mismatch that repair fixed, and floor (ii)'s planted failing direction, never before encoded as a permanent mech row"
SAB_DOC_FIGURE="tests/mrl/CLAUDE.md's 2026-09-05 repair account: 'turning the character count back into a byte count trips the second [floor] (and is caught twice, since it also produces 84 CHECK 2 violations)'. MEASURED here for the first time as a permanent row (whole corpus, this tree): multibyte spans 101 -> 0 (floor (ii) fires), utf8 blocks/spans UNCHANGED at 216/307 (floor (i) stays green -- this row's symptom is disjoint from S230's), CHECK 2 violations 0 -> 84, matching the CLAUDE.md figure exactly."
SAB_REACH='"$CC" -O1 -w -I "$TREE/lib" -I "$TREE/src" -o "$REACH_TMP/cwmax_check" "$TREE/tests/mrl/cwmax_check.c" "$TREE/build/libpcrec.a" && "$REACH_TMP/cwmax_check" "$TREE/tests/utf8/axis01_encoded_length.rxt"'
SAB_REACH_EXPECT='spans whose BYTE width exceeds their CHARACTER width: 66'
SAB_REACH_POP='tests/utf8/axis01_encoded_length.rxt|^encoding utf8|50'
SAB_COUNT=1
SAB_BEFORE='    long w = 0;
    for (long i = start; i < end; i++)
        if ((b[i] & 0xC0) != 0x80) w++;
    return w;'
SAB_AFTER='    /* SABOTAGE S231: reverts the 2026-09-05 repair -- the character
     * count degenerates back into the byte count it replaced. */
    return end - start;'
