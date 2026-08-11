# S11 — the test HARNESS stops mapping the .rxt 'flags i' directive to -i, so
# every caseless.rxt block silently runs case-sensitive (OS-1 section of
# tests/codegen/CLAUDE.md table, row 4). This sabotages the harness, not the
# compiler — it demonstrates the corpus's OWN blind spot when its flag
# plumbing breaks. Documented result: 21 of 56 caseless.rxt cases.
SAB_ID="S11-casefold-flag-noop"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/caseless.rxt"
SAB_DESC="harness: 'flags i' directive no longer maps to the -i CLI flag"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 21 of 56 caseless.rxt cases"
SAB_COUNT=1
SAB_BEFORE="    [[ \"\$cur_flags\" == *i* ]] && pflags+=(-i)"
SAB_AFTER="    true # [[ \"\$cur_flags\" == *i* ]] && pflags+=(-i)"
