# S16 — \d's registry row is given the WRONG module name (classes -> misc).
# The parser renders its diagnostic FROM this same table, so a hand-written
# test that reads the same table cannot see this (tests/reject/CLAUDE.md's
# SR-4 table, row 1). Documented result: 2 hand-written reject checks fail,
# 0 iterated (the iterated loop reads the same wrong table and agrees with
# it — this IS the circularity SR-4 documents as unclosed).
SAB_ID="S16-wrong-module-d"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject"
SAB_DESC="ESC('d', ...) module changed from 'classes' to 'misc' (wrong but plausible)"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 2 hand-written fail, 0 iterated"
SAB_COUNT=1
SAB_BEFORE="ESC('d', \"\\\\d\", classes, ANY_ENGINE, \"any decimal digit\", QF_YES, \"set 10\"),"
SAB_AFTER="ESC('d', \"\\\\d\", misc, ANY_ENGINE, \"any decimal digit\", QF_YES, \"set 10\"),"
