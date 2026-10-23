# docs/dev/reviews — compiled checkpoint critic reviews

One file (or file + same-named directory of critic texts) per checkpoint (D6):
the adversarial critic panel's findings, the triage decision on each, and a
reflection. The densest "why is it like this" source in the project; most
non-obvious code in src/ and odd-looking test cases trace to a finding here.

## Standing rules

- Maintenance: add a file per checkpoint and list it here (the full
  per-review entries, in order, are in the history file).
- Findings are labelled CONFIRMED (reproduced, with the repro) or SUSPECTED,
  and triaged FIX-NOW | PLAN | DOC | REJECTED | NOTED.
- Every review carries a PROBED-AND-HELD list with case counts (a negative
  result with evidence is worth a finding and stops re-covering ground).
- Do not declare a milestone reviewed until the critics' reports are in hand
  (a checkpoint is not closed until every critic has IDLED; R3, R11).
- Review the artifact a stranger would get, not the working tree: clone and
  build is step 5 of the process critic's brief (R1/R2: unanchored `core` in
  `.gitignore` excluded `src/core/`).
- Narrow briefs (one clear primary question per critic) are the standard
  (R11 vs R12 measurement); design panels carry a lens that proposes the
  general form and unlocks, not only refutations.
- Before starting new work, read the NOTED list of the most recent review:
  it is the honest inventory of what is still unguarded.

## Files

- `YYYY-MM-DD-rN-<topic>.md` — one review per checkpoint, R1 (2026-08-09
  m1) through the 2026-10-21 panels r1-memfn-r27 (the R-27 window-search design) and
  r2-memfn-window-site (D172's unified window site,
  rev 1) and 2026-10-22-r1-memfn-window-site-rev2 (rev 2), and the 2026-10-18 panels (r1-e1, r2-kitverify-proof,
  r3-kit-proof-u1, r4-ctx-span); the dated index of what each covers is in
  the history file. Where a review has critic texts they sit in a sibling
  directory of the same name (e.g. `2026-10-05-r4-startset/`,
  `2026-10-07-r1-memfn-rowcon/`, `2026-10-08-r9-memfn-simd/`).
- `2026-10-23-r2-iter-code.md` (+ dir) — first round of the `pcrec-code-critic` skill: the find-all iterators on lane/iterland.
- `2026-09-17-code-review.md`, `2026-09-20-code-org.md`,
  `2026-09-20-frank-tour.md`, `2026-09-20-r61-fable-personal-review.md`,
  `2026-09-20-readability-experiments.md` (+ `2026-09-20-readability-data/`)
  — the 2026-09 code-review round; criteria in `code_review_criteria_draft.md`.
- `code_review_criteria_draft.md` — the code-review metric charter
  (artifacts under `tools/review/`).
- `lens_reports/` — per-lens review reports (own CLAUDE.md; e.g. lens1
  semantic duplication ... lens11 function altitude, emitvm/lens10 evidence).
- `plan_triage_2026-10-12.md` — [PLAN-LINT] step 1: plan.md classified item by item.

## Pointers

D6 (critic panels), D27 (blinded authors); `docs/dev/learnings.md` 3;
`docs/dev/decisions.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev__reviews.md
