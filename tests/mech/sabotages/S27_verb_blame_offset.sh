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
SAB_COUNT=1
SAB_BEFORE="    else REFUSE(star, \"quantifier does not follow a repeatable item\");"
SAB_AFTER="    else REFUSE(at, \"quantifier does not follow a repeatable item\");"
