# S01 — skip-state selection forced off (tests/codegen/CLAUDE.md,
# run_codegen_tests.sh table, row 1). Documented result: 7 fail.
SAB_ID="S01-skip-states-off"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="pick_skip_states forced to return 0 immediately (skip-state optimization off)"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 7 fail"
SAB_COUNT=1
SAB_BEFORE="    int nout = 0;"
SAB_AFTER="    int nout = 0;
    return 0;"
