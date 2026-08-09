# Known issues — confirmed pcrec bugs (deferred fixes)

Confirmed correctness bugs in pcrec itself (distinct from docs/upstream_issues.md,
which tracks OTHER engines). Each has a minimal repro and a scheduled fix. Repros
live in tests/known_fail/ (NOT run by `make test`, so the suite stays honest about
what it certifies) and become passing regressions when fixed.

Status: `deferred` (scheduled) | `fixing` | `fixed` (moved to a passing corpus).

---

## K1 — FIXED 2026-08-09 (R2)

Zero-width `$` lost priority to a consuming alternative in a repeated group.
Root cause turned out to be general, not `$`-specific: `clo_visit` cut the
ε-path re-entering a loop-entry split, so an empty iteration never reached the
loop exit and never took its rightful priority. Same defect as R2-S1.
**Fix:** loop-entry states are marked in the NFA; on ε re-entry the closure
follows the loop EXIT once (PCRE's empty-iteration rule). Regressions moved to
tests/base/review_r2.rxt (passing). Note the original entry's scoping claim
("ENG_ATTEMPT only") was WRONG — the bug was live in both engines.

---

_No open confirmed bugs. Performance and architecture debt lives in
docs/plan.md; other engines' bugs in docs/upstream_issues.md._
