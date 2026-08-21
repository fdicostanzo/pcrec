# S07 — emit_unanchored references errno without emitting the errno.h header
# it needs (TS-1 section of tests/codegen/CLAUDE.md). Documented result: 6
# TS-1 checks fail, plus the OS-0b compile check incidentally (errno needs a
# header the generated file does not get).
SAB_ID="S07-ts1-errno"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="emit_unanchored: append '(void)errno;' to the emitted prologue with no errno.h include"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 6 TS-1 checks (+ OS-0b compile check incidentally)"
SAB_COUNT=1
SAB_BEFORE="\"    size_t scan_position = search_from;\\n\""
SAB_AFTER="\"    size_t scan_position = search_from; (void)errno;\\n\""
