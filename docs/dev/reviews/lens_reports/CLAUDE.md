# docs/dev/reviews/lens_reports/ — the 2026-09-17 code review's per-lens reports

One file per lens of the code review chartered by
`docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED by Frank
2026-09-17). Each is one opus lane's own voice, read-only over the
primary tier (`src/`, `cli/`, `lib/`), delivered REPORT-ONLY — no
refactoring in the review phase. The manager's synthesis
(`docs/dev/reviews/YYYY-MM-DD-code-review.md`) dedupes across them and
ranks per A4; on any disagreement the synthesis wins.

Each report carries the charter's admissibility apparatus: A1 (cite and
argue against any ruled record it contradicts, or drop), A2 (a
duplication finding names the shared abstraction), A3's check-coupling
annex (what the finding's fix would stale), A4's severity/effort/blast
vocabulary, A5 (cite the metric artifact under `tools/review/out/`), and
a PROBED-AND-HELD list, because a seam that is adequately covered is a
result worth as much as a finding and stops the next wave re-arguing it.

## Files

- `lens5_unit_seams.md` — **lens 5, unit-testing recommendations** (lane
  `lens5unit`, base `main` @ `7d444f9e`). **Corrects the charter's own
  premise: the repo already HAS a unit tier** — ten C programs in six
  directories that `#include "core/internal.h"`, link `libpcrec.a` and
  assert an internal helper's property below any answer — with no name,
  no shared build, **four divergent flag policies**, and two of its
  scripts missing from `tests/lib/san_scripts.txt`, so
  `cpset_model_check.c` (the tree's best unit check, whose whole stated
  argument is that it reaches paths the corpus cannot) **has never been
  built under a sanitizer.** Seven recommendations: the tier's shape
  (one `tests/lib/unit_cc.sh` build helper, `san_scripts.txt`
  membership, `tests/core/` as the home for NEW core-helper checks
  rather than a generic `tests/unit/`, and a cost budget expressed as a
  shape — one gcc invocation and one spawn per SUBJECT); a
  `-include`+`BUILD_DIR` allocation-failure injector that needs zero
  `src/` edits and would have found lens 8's F1 directly (reclassified
  from lens 8's DESIGN-EVENT to LOCAL on that spelling); the
  `mrl_sat_add`/`vm_fadd`/`cg_sat_add` agreement check, whose
  requirement the tree states twice in prose and enforces nowhere; and
  unit surfaces SPECIFIED IN ADVANCE for the arena-vector and text-kit
  primitives lens 1 and lens 2 propose, so wave 1 builds them with their
  nets. Its A1 section reads the tree's **only** ruling on a unit test
  (`decisions.md:4602`, [M4.7a]'s reverted hand-built-`Ctx` test) and
  makes its distinction — fabricated input at sample size zero versus a
  helper's own total input domain against an independent oracle — a
  filing requirement for every item. Ten PROBED-AND-HELD entries, headed
  by the standing do-not: **a unit test of a rung's emitted shape would
  duplicate oracle coverage and is the thing this lens must not
  recommend.**

Maintenance: add a row per lens report as it lands; historical once the
synthesis is written, and never edited afterwards.
