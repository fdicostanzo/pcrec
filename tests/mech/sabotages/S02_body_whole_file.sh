# S02 — the run_codegen_tests.sh body() extractor returns the WHOLE FILE
# instead of scoping to one engine's function body (tests/codegen/CLAUDE.md
# table, row 2). This sabotages the TEST SCRIPT itself, not src/ — it is the
# meta-check that OS-0b's engine-scoped greps are actually scoped.
# Documented result: 3 fail.
#
# [M4.5b] the anchor text changed (it accepts an optional `static` now, so the
# VM artifact's private prefilter is extractable like any other engine body).
# The sabotage follows it — a sabotage whose BEFORE has drifted is not a
# passing check, it is an unmeasured one, and the matrix reports it as an
# ANOMALY precisely so this cannot be mistaken for coverage.
SAB_ID="S02-body-whole-file"
SAB_FILE="tests/codegen/run_codegen_tests.sh"
SAB_SUITES="codegen"
SAB_DESC="body() awk extractor: drop the '^(static )?int fn(' start anchor so it prints the whole file"
SAB_DOC_FIGURE="tests/codegen/CLAUDE.md: 3 fail"
SAB_COUNT=1
SAB_BEFORE="        \$0 ~ \"^(static )?int \" fn \"\\\\(\" { inside = 1 }"
SAB_AFTER="        { inside = 1 }"
