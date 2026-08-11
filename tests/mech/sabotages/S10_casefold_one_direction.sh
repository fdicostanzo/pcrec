# S10 — cls_casefold only folds one direction (upper -> lower is dropped),
# so a class containing only the uppercase letter does not gain the
# lowercase one (OS-1 section of tests/codegen/CLAUDE.md table, row 3).
# Documented result: 1 codegen check + 8 caseless.rxt cases.
SAB_ID="S10-casefold-one-direction"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/base/caseless.rxt"
SAB_DESC="cls_casefold: 'cls_has(b,c) || cls_has(b,c+32)' -> 'cls_has(b,c+32)' (fold one direction only)"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 1 codegen check + 8 caseless.rxt cases"
SAB_COUNT=1
SAB_BEFORE="        if (cls_has(b, c) || cls_has(b, c + 32)) {"
SAB_AFTER="        if (cls_has(b, c + 32)) {"
