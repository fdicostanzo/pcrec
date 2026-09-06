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
#
# [MACPORT], 2026-09-06 — RE-ANCHORED. The rename dropped GNU sed's `\b`,
# which BSD sed does not implement and silently ignores, for a POSIX
# not-followed-by-an-identifier-character spelling verified byte-identical to
# `\b` on this exact body. The row's MECHANISM is unchanged: it still renames
# engine B's entry to itself, so the two-engine fixture keeps one `rx_search`
# and the compile fails.
SAB_BEFORE="        sed 's/rx_search\\([^_A-Za-z0-9]\\)/rx_search_b\\1/g' \"\$WORKDIR/engb.body\""
SAB_AFTER="        sed 's/rx_search\\([^_A-Za-z0-9]\\)/rx_search\\1/g' \"\$WORKDIR/engb.body\""
