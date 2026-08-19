# S81 — [D63] THE CANDIDATE-START SET HARDCODED TO THE NEWLINE DEFINITION.
#
# D63 charters ENG_ATTEMPT's candidate-start prefilter as a TOOL rather than a
# one-off, and the derivation it shares with ENG_UNANCH is "state row -> byte
# set -> memchr-vs-bitmap choice -> table emission". For `(?m)^` the set is
# derived from WHICH SEEDED START STATES ARE LIVE: an attempt at `start > 0`
# enters `s1u[upc_of_class(s[start-1])]`, so a predecessor byte whose seeded
# state is DEAD cannot begin a match and only those bytes are candidates.
#
# THE SHORTCUT THIS ROW GUARDS AGAINST is the one a reader of
# assertions_design.md §3.7.2 would take: that section says a `(?m)^`-anchored
# attempt "can only begin at offset 0 or immediately after a '\n'", which is
# TRUE OF A FULLY-`(?m)^`-ANCHORED PATTERN and false of the general case. The
# sabotage writes exactly that sentence as code — candidates are the newline
# set, full stop — and it is wrong the moment any branch does not require the
# anchor:
#
#     (?m)^a|b   on "zzzb"   ->  libpcre2 (3,4);  sabotaged pcrec: no match
#
# because the `b` branch's attempts all start after a non-newline and are
# skipped. The live-seed derivation gets this right by construction: with a
# non-anchored branch present, EVERY predecessor byte seeds a live state, the
# candidate set is all 256, `cand_derive` reports it unusable, and no
# prefilter is emitted at all.
#
# It is also a POSITIVE control on the derivation being shared rather than
# reimplemented: the sabotage cannot be written against the ENG_UNANCH caller,
# because that caller derives its set from a state row too.
#
# **THE SUBJECTS ARE WHAT MAKE THIS ROW FIRE, and the corpus did not have them
# until this row was validated.** A skipped attempt is one whose start has a
# NON-newline predecessor, so a cell whose match begins at offset 0 or right
# after a line break sees nothing. multiline.rxt's first `(?m)^a|b$` block was
# exactly that — every match at 0 or after a `\n` — and it stayed GREEN under
# this sabotage. Section 6b exists for this row: `(?m)^a|b` on "zb" is (1,2),
# and the sabotaged build reports no match. Measured directly first
# (`a|^b` on "cac": [(1,2)] becomes []) over the 13 corpus patterns whose
# artifact this edit changes.
SAB_ID="S81-cand-set-hardcoded-newline"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness mlinediff"
SAB_HARNESS_TARGET="tests/assertions/multiline.rxt"
SAB_DESC="D63's candidate-start set is taken as 'the newline definition' rather than derived from which seeded start states are LIVE, so a (?m)^ pattern with a non-anchored branch skips every attempt that branch needs ('(?m)^a|b' on \"zzzb\" loses its match)"
SAB_DOC_FIGURE="tests/assertions/multiline.rxt SECTION 6b goes red (the block exists for this row) and run_mline_diff.sh's (?m)^a|b arm diverges"
SAB_COUNT=1
SAB_BEFORE='        set[b] = (uint8_t)(d->s1u[upc_of_class(d, d->clsmap[b])] >= 0);'
SAB_AFTER='        set[b] = (uint8_t)cls_has(pcrec_cls_newline, (unsigned)b);   /* SABOTAGE S81 */'
