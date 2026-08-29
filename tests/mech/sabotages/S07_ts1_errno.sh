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
# RE-ANCHORED 2026-08-29 ([ENG-ABS]): the one-line anchor matched TWICE once a
# THIRD machine's scan body was emitted (`<prefix>_match`'s anchored scan opens
# with the same declaration), so SAB_COUNT=1 stopped resolving. The anchor now
# carries the preceding comment line, which differs between the two scans —
# the row still plants ONE `(void)errno;`, in the SEARCH body, which is the
# body TS-1's denylist sweep was validated against.
SAB_BEFORE='"    // match wins.\n"
               "    size_t scan_position = search_from;\n"'
SAB_AFTER='"    // match wins.\n"
               "    size_t scan_position = search_from; (void)errno;\n"'
