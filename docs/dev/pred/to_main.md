# Predicate manager -> main (ONE writer: the predicate manager; `[pred]` commits on its branch)

Entries are `P-n`, dated, never deleted. `done:` lines name the branch tip and the report path.

## P-1 (2026-11-18, predicate manager) — up

- Acknowledges M-1. The predicate manager session is up: branch `lane/pred-rev28` (worktree `worktrees/pred`),
  cut from main f9ee6814e. From now the draft, COND-FAMILY.md and predicates_future.md are written here only.
- First with Frank: the hole-reads-capture confirm, then the R.8 queue. No lane and no critic round running;
  I will ask for a review number before the rev 28 round.

## P-2 (2026-11-18 night, predicate manager) — done: rev 28.1 of the predicate draft, review r52 filed

- done: branch `lane/pred-rev28`, tip at this commit's parent chain (merge it at its head); reports
  `docs/dev/lanes/predspec28_report.md` (the fold) and `docs/dev/lanes/predspec281_report.md` (the fixes);
  review `docs/dev/reviews/2026-11-18-r52-predspec28.md` (+ its directory; dispositions ruled by me; indexed).
- What lands: `docs/design/predicates_draft.md` REVISION 28.1 (NOT STABLE); `COND-FAMILY.md` with the owner's
  ELEVEN rulings of 2026-11-18 evening (hole-reads-capture, number-domain, padded-width, hole-flags,
  flags-propagate, unset-in-hole, construction-line, value-test, same-name-twice, array-in-hole = future
  direction, numeral-width); `predicates_future.md` items 32-33; evidence dirs `predspec28_evidence/`,
  `predspec281_evidence/`; `docs/dev/pred/` (journal, wake, this file). Lane branches `lane/predspec28`,
  `lane/predspec281` are merged into mine; their worktrees are yours to prune (wtprune).
- [COND-FAMILY] plan-row status line I ask you to record: "2026-11-18: draft rev 28.1 (NOT STABLE; review r52
  filed); the owner ruled eleven questions on holes, numbers, flags and the construction line; open with him:
  padded-order, flags-in-filter, flags-scope, class-order, dollar-diagnostic, number-edges, any-case-body,
  same-name-count; design only, no build go."
- PROPOSED EDITS to files you own (accepted by me from the r52 coordinator; verbatim text in
  `docs/dev/lanes/predspec281_report.md`, STATE AT HANDOFF, items 1-4): pcrec-critic skill section 3 (a FREEZE
  NOTE when the fold range ends past the record at the subject commit) and three lens drills (set-equal bodies
  drilled in SEARCHED/FIND-ALL with a prefix pair; a flag rule run with every PCRE inline flag, `#` under x and
  an `&` inside the place; an evidence enumerator's order checked against PCRE priority order).
- PROPOSED EDIT to the pcrec-predicate-manager skill (a lesson that is a rule): section 2, "Before asking
  anything, grep the record": add "and, for a recollection of his ('I proposed'), every file under
  docs/design/plan_row_bodies/ and docs/design/ (the label-only group was in POSTFACT.md, 2026-11-09)"; and:
  "a body or macro offered to him as EQUAL to a meaning is run in SEARCHED and FIND-ALL before it is said, not
  only WHOLE (padded, r52 item A)".
- Note: `docs/dev/reviews/CLAUDE.md` is near its 12 KB limit (the r52 index line is short).
