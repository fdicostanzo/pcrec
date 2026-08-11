# S03 — isolate the multi-engine ATTRIBUTION check from fixture construction:
# replace the second body() call (which extracts engine B's body for the
# attribution check) with a plain cp, so the "attribution" comparison is
# comparing the whole file to itself instead of a scoped extraction
# (tests/codegen/CLAUDE.md table, row 3). Documented result: 1 fail (the
# attribution check alone).
SAB_ID="S03-attribution-cp"
SAB_FILE="tests/codegen/run_codegen_tests.sh"
SAB_SUITES="codegen"
SAB_DESC="multi-engine control: replace 'body ... rx_search_b ...' with 'cp' for engine B's extraction"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 1 fail (attribution check alone)"
SAB_COUNT=1
SAB_BEFORE="        && body \"\$WORKDIR/multi.c\" rx_search_b \"\$WORKDIR/multi.b.body\"; then"
SAB_AFTER="        && cp \"\$WORKDIR/multi.c\" \"\$WORKDIR/multi.b.body\"; then"
