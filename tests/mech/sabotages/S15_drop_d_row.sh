# S15 — delete \d's registry row entirely, so it falls through to "unknown
# escape" instead of naming its module. ADAPTED from tests/reject/CLAUDE.md's
# "drop {'d', \"classes\"}, from esc_modules" row: esc_modules[] as a
# separate table no longer exists (it was folded into registry.c's ESC(...)
# rows by the SR-2 refactor; `grep -rn esc_modules src/` finds only stale
# comments referencing the old name). The functionally equivalent edit today
# is deleting the ESC('d', ...) row from esc_rows[]. Documented result (for
# the pre-SR-2 shape): 2 reject checks fail, 0 corpus cases.
SAB_ID="S15-drop-d-row"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject"
SAB_DESC="delete the ESC('d', ...) registry row entirely (adapted from the stale esc_modules[] reference)"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md (pre-SR-2 shape): 2 reject checks, 0 corpus cases -- ADAPTED, see report"
SAB_COUNT=1
SAB_BEFORE="ESC('d', \"\\\\d\", classes, ANY_ENGINE, \"any decimal digit\", QF_YES, \"set 10\"),
"
SAB_AFTER=""
