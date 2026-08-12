# S33 — the leading negation caret is no longer consumed before the
# significant-character count starts, so `\p{^L}`'s `^` falls into the main
# scan loop as an ordinary (significant) character. Measured against
# libpcre2 10.46 (tests/probes/probe_uprops.c): the caret does NOT count
# toward the 48-character budget (`\p{^` + 48 A's `}` is still well-formed,
# one byte later than the no-caret case) — this sabotage makes pcrec
# disagree, both on the accumulated NAME (a caret-prefixed body no longer
# matches the same table entry) and on where the 48/49 boundary falls for
# a caret-prefixed body.
SAB_ID="S33-uprops-drop-caret-consume"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_modport_uprops: drop the leading-caret consume, so ^ enters the significant-character count"
SAB_DOC_FIGURE="measured at MOD-0.6 phase 2 landing: \\p{^L} moves from the GENERIC message (a known 1-letter name, L) to the NOT-RECOGNISED message (a 2-char name, ^L, outside the verifiable axis)"
SAB_COUNT=1
SAB_BEFORE="    if (i < n && p[i] == '^')
        i++;   /* negation caret: consumed, does NOT enter the 48-char
                  budget below (measured — see this file's header) */"
SAB_AFTER=""
