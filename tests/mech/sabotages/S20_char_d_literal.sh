# S20 — esc_char_value grows a case for 'd' that decodes it as the literal
# character 'd', so "\d" silently compiles as if it were the pattern "d"
# instead of reaching the registry doorway at all: the exact shape of the
# real \v bug (tests/reject/CLAUDE.md's "Validated sabotages" table, row 2).
# Documented result: 2 reject checks fail, 0 corpus cases, 0 codegen checks —
# "a silent miscompile of a class escape is invisible to every other test in
# this repo" is the line this sabotage exists to prove.
SAB_ID="S20-char-d-literal"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="reject"
SAB_DESC="esc_char_value: add case 'd': return 'd'; so \\\\d silently compiles as literal 'd'"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md: 2 reject checks, 0 corpus, 0 codegen"
SAB_COUNT=1
SAB_BEFORE="    case 'e': return 0x1b;"
SAB_AFTER="    case 'e': return 0x1b;
    case 'd': return 'd';"
