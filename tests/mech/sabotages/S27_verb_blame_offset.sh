# S27 — the empty-name quantifier error blames `at` (the doorway's own
# default offset, the '(') instead of `star` (at + 1, the '*'). This is the
# migration's marquee hazard: a generic "collapse REFUSE(star, ...) to the
# doorway default" refactor would still produce the SAME message text
# ("quantifier does not follow a repeatable item"), so a check that only
# reads the message and not the offset cannot see it. MOD-0.4c.
SAB_ID="S27-verb-blame-offset"
SAB_FILE="src/parse/mod_verbs.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_ext_verb: empty-name REFUSE reports at 'at' (the '(') instead of 'star' (the '*', at+1)"
SAB_DOC_FIGURE="measured MOD-0.4c: UNDETECTED 0/437 against the message-only (*) pin; DETECTED 1/436 once the pin also asserts (pattern offset 1) — the offset suffix added in the same commit (tests/reject/run_reject_tests.sh)"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS AN OFFSET, and that is why it is spelled out in full.
# This row does not change WHETHER `(*)` is refused, only WHERE it is
# blamed (`star` -> `at`), so a reach check that asserted only the sentence
# would stay green on a tree that had lost the offset contract entirely.
# `(pattern offset 1)` is the whole claim.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "(*)"'
SAB_REACH_EXPECT="quantifier does not follow a repeatable item (pattern offset 1)"
SAB_COUNT=1
SAB_BEFORE="    else REFUSE(star, \"quantifier does not follow a repeatable item\");"
SAB_AFTER="    else REFUSE(at, \"quantifier does not follow a repeatable item\");"
