# docs/dev/reviews/lens_reports/ — the code review's per-lens findings

One file per lens of the 2026-09-17 code review
(`docs/dev/reviews/code_review_criteria_draft.md`, RATIFIED). Each is one
opus lane's own voice, written READ-ONLY: findings with `file:line`
citations and concrete suggestions, never a refactor. The manager's
synthesis (`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes across
them and ranks per A4; on any disagreement the synthesis wins.

Every finding in these files is written to the charter's admissibility
rules — A1 (cite and argue against any ruled record it contradicts, or
drop), A2 (a duplication finding names the shared abstraction: proposed
signature, call sites replaced, what varies), A3 (name the sabotage/
codegen/abi anchors bound to the code it would move), A4 (severity /
effort / blast radius), A5 (cite the metric artifact under
`tools/review/out/`).

## Files

- `lens1_semantic_duplication.md` — LENS 1 (Frank #1), lane `lens1dup`.
  Twelve ranked extracts X1-X12 over `src/`, `cli/`, `lib/`, each with its
  named abstraction; four detector groups examined and REJECTED with
  reasons; the lens-11 join table (ADDENDUM 1); and the named unreviewed
  remainder (ADDENDUM 2), which asks for a second pass over
  `src/gen/emit_vm.c` and `src/parse/rxt_source.c`. Headline: the clone
  detector's largest group is not one duplication but every function
  containing an AST spine walk, and it under-counts — 75 hand-written
  spine sites, 48 exhaustive `AKind` switches. Read §5 before acting on
  X1: the nine `atomic.c` predicates must NOT be merged into one function,
  only their traversal extracted.

Maintenance: add a row per lens report as it lands.
