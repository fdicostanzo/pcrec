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
SAB_COUNT=1
SAB_BEFORE="    if (i < n && p[i] == '^')
        i++;   /* negation caret: consumed, does NOT enter the 48-char
                  budget below (measured — see this file's header) */"
SAB_AFTER=""
