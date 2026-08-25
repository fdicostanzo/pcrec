# S15 — delete \d's registry row entirely, so it falls through to "unknown
# escape" instead of naming its module. ADAPTED from tests/reject/CLAUDE.md's
# "drop {'d', \"classes\"}, from esc_modules" row: esc_modules[] as a
# separate table no longer exists (it was folded into registry.c's ESC(...)
# rows by the SR-2 refactor; `grep -rn esc_modules src/` finds only stale
# comments referencing the old name). The functionally equivalent edit today
# is deleting the ESC('d', ...) row from esc_rows[]. Documented result (for
# the pre-SR-2 shape): 2 reject checks fail, 0 corpus cases.
#
# RETAGGED 2026-08-12 (MOD-0.8c slice 1) with `registry` and `pc3`. This row's
# subject is a DELETED registry row, and both of those suites' own docs name
# themselves as the relevant net for it: tests/registry/CLAUDE.md carries an
# EXACT row count ("so rows cannot be deleted silently — the same TABLE SHRANK
# guard tests/reject/ carries"), and its "What it does NOT establish" section
# makes PC-3 the only external reader of the same fact. Everything else in
# both suites ITERATES THE ROWS THAT EXIST, which is structurally blind to a
# deletion — so what these two arms measure here is exactly whether the
# count-shaped guards are the whole answer.
SAB_ID="S15-drop-d-row"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject registry pc3"
SAB_DESC="delete the ESC('d', ...) registry row entirely (adapted from the stale esc_modules[] reference)"
SAB_DOC_FIGURE="tests/reject/CLAUDE.md (pre-SR-2 shape): 2 reject checks, 0 corpus cases -- ADAPTED, see report"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS: the ESC('d') row this sabotage DELETES is what makes the
# bare default answer `\d` with a MODULE NAME. If `\d` ever stops being
# answered by a registry row -- because module `classes` builds it, the way
# module `assertions` built `\b` out from under S70 -- this row's reject
# population moves to a different site and the row certifies nothing.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "\\d"'
SAB_REACH_EXPECT="\\d requires module 'classes' (pattern offset 0)"
SAB_COUNT=1
SAB_BEFORE="ESC_SET('d', \"\\\\d\", classes, ANY_ENGINE, \"any decimal digit\", QF_YES, \"set 10\", pcrec_cls_digit_esc, 0),
"
SAB_AFTER=""
