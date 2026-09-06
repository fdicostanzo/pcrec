# S33 — the leading negation caret is no longer consumed before the
# significant-character count starts, so `\p{^L}`'s `^` falls into the main
# scan loop as an ordinary (significant) character. Measured against
# libpcre2 10.46 (tests/probes/probe_uprops.c): the caret does NOT count
# toward the 48-character budget (`\p{^` + 48 A's `}` is still well-formed,
# one byte later than the no-caret case).
#
# HISTORY (design note §8): this sabotage's first landing predicted `\p{^L}`
# would flip to the not-recognised message, and mech measured it UNDETECTED
# (0/465) — the prediction misread ruling 3's design: a two-significant-char
# name (`^L` once the caret leaks into the count) takes the GENERIC message,
# same as the un-sabotaged known-letter case, so no message and no offset
# moves there. What DOES move is the 48/49 boundary for a caret-prefixed
# body: caret + 48 A's overflows the budget one character early (generic ->
# malformed AND offset 53 -> 52), and caret + 49 A's blames one byte
# earlier. The two caret-boundary pins are this sabotage's guard.
SAB_ID="S33-uprops-drop-caret-consume"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_modport_uprops: drop the leading-caret consume, so ^ enters the significant-character count"
SAB_DOC_FIGURE="measured at MOD-0.6 phase 2 landing (post-§8 fix): both caret-boundary pins flip — caret+48 A's goes generic->malformed with offset 53->52, caret+49 A's blames 52 where 53 is pinned"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS THE CARET-PREFIXED BOUNDARY, and tests/reject's own
# comment records WHY it has to be: `\p{^L}` never flips under this
# sabotage, because a two-character name gets the generic message either
# way. What moves is the 48/49 boundary WITH a caret -- the caret costs one
# OFFSET byte (53, not 52) and zero BUDGET. Both sides are asserted for
# S32's reason.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "\\p{^AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}"; "$PCREC" --features none -p rx -o "$REACH_TMP/o1.c" -- "\\p{^AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}"'
SAB_REACH_EXPECT="\\p requires module 'unicode-props' (pattern offset 53)
\\p: malformed property escape — requires module 'unicode-props' (pattern offset 53)"
SAB_COUNT=1
# [M5.0 stage 3] RE-ANCHORED, intent re-verified. The site gained a `caret`
# flag (the producer needs to know, because `\P{X}` and `\p{^X}` XOR: the
# selector is a property of the ESCAPE and the caret of the BODY), so the two
# lines became a braced block. THE SABOTAGE IS UNCHANGED IN WHAT IT DOES —
# the caret is not consumed and falls into the main scan loop as an ordinary
# significant character — and `caret` is left DECLARED and false, because it
# is read below and a sabotage that does not compile measures nothing.
#
# Leaving `caret` false additionally makes `\p{^L}` non-negated under the
# sabotage, which changes NOTHING this row observes and is consistent with its
# own §8 history: with the caret in the count, `^L` is a two-significant-
# character name, misses the table, and takes the generic message either way.
# What moves is still the 48/49 boundary, still by one offset byte.
SAB_BEFORE="    bool caret = false;
    if (i < n && p[i] == '^') {
        i++;   /* negation caret: consumed, does NOT enter the 48-char
                  budget below (measured — see this file's header) */
        caret = true;
    }"
SAB_AFTER="    bool caret = false;
    /* SABOTAGE S33: the caret consume dropped — ^ now falls into the main
       scan loop as an ordinary significant character */"
