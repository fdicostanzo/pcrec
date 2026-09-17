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

- `lens11_function_altitude.md` — LENS 11 (Frank's function rubric), lane
  `lens11alt`. All 31 functions at 100+ code lines scored against the five
  questions, 15 findings (F1-F15) ranked MECHANICAL-first, the
  PASSES-AND-STAYS-LONG list (13 of the 31, with what a mechanical splitter
  would have broken), a PROBED-AND-HELD list, the ADDENDUM-1 loop run back
  into lens 1 (five extract candidates that live INSIDE long functions,
  plus one measured correction to lens 1's join table), and the named
  remainder. Headline: the tree does not have a length problem — median
  function 10 code lines, 644 of 860 at or under 20 — it has eight
  functions with one, headed by `pcrec_emit_vm`, ~30% of whose body is
  dataflow analysis that emits no text and which carries 26 sabotage
  anchors, the densest in the tree. Read §5.1 before acting on anything:
  seven extractions were probed and DECLINED with reasons.

Maintenance: add a row per lens report as it lands. When lens reports from
other lanes merge, the manager merges the Files lists; each lane's own
entry is written to stand alone.
