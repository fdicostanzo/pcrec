# Review r33 (round predspec23, design re-check of predicates_draft.md rev 23): the MANAGER's dispositions (2026-11-17, session 137)

Verdict ACCEPTED: NOT STABLE. The model as ruled is stated faithfully and every worked number re-derives; the fixes
below go to lane predspec23c, then a smaller re-check.

- F1, F3-F13, F15: FIX-NOW as proposed (F13 also keeps its PLAN item, filed in docs/design/predicates_future.md,
  not as a plan row: predicates are design only).
- F2: FIX-NOW by MANAGER RULING, told to the owner by name (**branch-order**), not asked: a branch of `|` whose own
  condition rejects its rows FALLS THROUGH to the next branch, and the order is PCRE's own preference order
  (branch-major: every row of the first branch, in its preference order, before any row of the second), because
  the ruled model says a searched program reports the PREFERRED SURVIVING ROW and `|` is PCRE's one parse; a
  condition inside a branch fails like any failing piece of that branch. The evidence engine's end-major order is
  a defect of the engine: fix it, re-run every count that moves (the review names 125 and 400 of 1,110), list them.
  `when`'s body is then stated with its mode. The owner may object.
- F14: FIX-NOW by the manager (the COND-FAMILY entry for the parked whole-text question is written with this
  disposition).
- F16, F17: DOC as proposed.
- The two NOTES: NOTED; the PLAN one becomes an item in predicates_future.md.
Process change (the fix-induced lens: when a revision RE-ALLOWS an operator, re-run every SAME row, warning and
compile error whose reason assumed the operator absent): ACCEPTED. Other proposals in process.md: plain additions
consistent with the skill are applied by the filing lane, anything else listed as open.
