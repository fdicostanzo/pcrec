# S05 — the multi-engine fixture's rename step stops renaming: engine B keeps
# the name rx_search instead of rx_search_b, so the hand-built two-engine file
# declares rx_search twice (tests/codegen/CLAUDE.md table, row 5). Documented
# result: 1 fail — compile, "error: redefinition of 'rx_search'".
SAB_ID="S05-no-rename"
SAB_FILE="tests/codegen/run_codegen_tests.sh"
SAB_SUITES="codegen"
SAB_DESC="fixture rename: sed replacement target changed from rx_search_b back to rx_search"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 1 fail (compile, redefinition of 'rx_search')"
SAB_COUNT=1
SAB_BEFORE="        sed 's/\\brx_search\\b/rx_search_b/g' \"\$WORKDIR/engb.body\""
SAB_AFTER="        sed 's/\\brx_search\\b/rx_search/g' \"\$WORKDIR/engb.body\""
