# tools/ — repo-owned developer/review tooling

Scripts that analyze the pcrec tree itself (as opposed to `scripts/`,
which runs/tests/manages the built compiler and its suites). Nothing
here is built or invoked by `make`/`make test`; each subdirectory's own
CLAUDE.md documents what its scripts do and how to run them.

## Subdirectories

- `review/` — the code-review metric artifacts (function census, clone
  candidates, literal census, include graph, churn hotspots) chartered
  by `docs/dev/reviews/code_review_criteria_draft.md`'s "Metric
  artifacts" section, for the eleven review lenses to cite per
  admissibility rule A5. See `review/CLAUDE.md`.

Maintenance: update this file when a subdirectory is added, removed, or
changes purpose.
