# S04 — duplicate the emit_span_typedef() call so a two-engine file would
# carry the rx_span typedef twice (tests/codegen/CLAUDE.md table, row 4).
# Documented result: 2 fail (typedef-count and compile).
SAB_ID="S04-duplicate-typedef"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="emit_span_typedef(c, p) called twice in a row (per-file emit-once rule broken)"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 2 fail (typedef-count and compile)"
SAB_COUNT=1
SAB_BEFORE="        emit_span_typedef(c, p);
        emit_search_decl(c, p, fn);"
SAB_AFTER="        emit_span_typedef(c, p);
        emit_span_typedef(c, p);
        emit_search_decl(c, p, fn);"
