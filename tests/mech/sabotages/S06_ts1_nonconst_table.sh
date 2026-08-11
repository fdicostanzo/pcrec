# S06 — every emitted u8 table becomes a non-const static (TS-1 section of
# tests/codegen/CLAUDE.md). Documented result: 8 TS-1 checks fail, 0 corpus
# cases fail — the sharpest illustration in the repo of a thread-hostile
# change that is invisible to correctness testing.
SAB_ID="S06-ts1-nonconst-table"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="emit_u8_table: 'static const unsigned char' -> 'static unsigned char'"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 8 TS-1 checks fail, 0 corpus cases"
SAB_COUNT=1
SAB_BEFORE="    sb_printf(c, \"    static const unsigned char %s_%s[%d] = {\", p, tag, n);"
SAB_AFTER="    sb_printf(c, \"    static unsigned char %s_%s[%d] = {\", p, tag, n);"
