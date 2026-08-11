# S19 — add a brand-new registry row for a FABRICATED construct (\j, which
# PCRE2 does not define) naming a plausible-looking module, with no
# hand-written reject-table entry for it anywhere (tests/reject/CLAUDE.md's
# SR-4 table, row 4 — "a NEW row with a plausible wrong module and no
# hand-written entry"). Documented result: 0 hand-written fail, 0 iterated
# fail. This is the row SR-4's own text calls "the honest limit": iteration
# reads the same table the parser renders from, so a WRONG-BUT-INTERNALLY-
# CONSISTENT row is invisible to everything in this repository except PC-3
# (which needs libpcre2 and is out of scope for this matrix). The matrix
# should report this one UNDETECTED, and that is the correct, expected
# finding, not a bug in the harness.
SAB_ID="S19-new-wrong-row"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject"
SAB_DESC="add ESC('j', \"\\\\j\", misc, ...) for a construct PCRE2 does not define; no hand-written pin exists"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 0/0 -- expected UNDETECTED, this is the SR-4 blind spot itself"
SAB_COUNT=1
SAB_BEFORE="ESC('o', \"\\\\o{101}\", misc, ANY_ENGINE, \"character with the given octal code\", QF_YES, \"char 0x41\"),"
SAB_AFTER="ESC('o', \"\\\\o{101}\", misc, ANY_ENGINE, \"character with the given octal code\", QF_YES, \"char 0x41\"),
ESC('j', \"\\\\j\", misc, ANY_ENGINE, \"fabricated: PCRE2 does not define this escape (MECH-1 sabotage for the SR-4 blind spot)\", QF_NO, \"err 103\"),"
