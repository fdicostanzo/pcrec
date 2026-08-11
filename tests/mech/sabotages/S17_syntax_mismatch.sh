# S17 — \s's registry row gets a `syntax` probe string that does not reach
# its own doorway ("zz" instead of "\s") (tests/reject/CLAUDE.md's SR-4
# table, row 2). Documented result: 0 hand-written fail, 1 iterated fail (the
# --list-syntax iteration probes "zz" and finds it does NOT produce the
# promised "requires module 'classes'" diagnostic, because "zz" is two
# ordinary literal characters that compile fine).
SAB_ID="S17-syntax-mismatch"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject"
SAB_DESC="ESC('s', ...) syntax probe changed from '\\\\s' to 'zz' (a syntax field that never reaches its doorway)"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 0 hand-written, 1 iterated fail"
SAB_COUNT=1
SAB_BEFORE="ESC('s', \"\\\\s\", classes, ANY_ENGINE, \"any whitespace character\"),"
SAB_AFTER="ESC('s', \"zz\", classes, ANY_ENGINE, \"any whitespace character\"),"
