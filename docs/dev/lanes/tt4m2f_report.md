# tt4m2f report — r55 revision on [TT-4M] STEP 2 (2a)+(2b)

Lane tt4m2f (sonnet), 2026-09-08, branch `lane/tt4m2f`, worktree
`worktrees/tt4m2f`. Charter: apply every disposition in `docs/dev/reviews/
2026-09-08-r55-tt4m-batching.md` (R55-1 through R55-9; R55-10's archive
bar moves to STEP 2c/2d's own brief, not this lane's) to the merged
tt4m2 deliverables plus the two tooling files the panel found bugs in.
Design/tooling-fix lane only: nothing under `tests/harness/`/`src/`
touched.

## Disposition-by-disposition checklist

Every R55 id below points at the exact hunk it landed in. "Charter" is
the review's own disposition text (condensed); "Committed" names the
file and location.

| id | charter | committed |
|---|---|---|
| R55-1 | routed-block exclusion: a block carrying `frames-buffer=` OR a non-default `RXTROUTE` floor is excluded from batching exactly as `perr`/H11, route grammar enumerated from `parse_route`, not one spelling | `docs/design/tt4m_harness_batching.md:108-140` (new third-exclusion paragraph in item 1, enumerates all four `parse_route`/`valid_route` route shapes) + `:156-165` (item 2's scope-limit reworded from "not modeled" to "explicitly enforced") |
| R55-2 | rewrite item 6 on option (a)'s structure: per-`-c` sub-compile at the UNSCALED per-pattern budget, link gets one additional unscaled budget, N-scaled number survives only as an outer backstop; S43's note updates to match | `docs/design/tt4m_harness_batching.md:418-446` (item 6 "Timeout story — REWRITTEN", three-step budget structure) + `:338-344` (item 5's S43 paragraph updated to cite the new shape) |
| R55-3 | reframe (not re-run): the N=128/P=12 cell demonstrates the starvation mechanism but was foreordained by the pool's own arithmetic, not an emergent hardware discovery; mark it in memo + report + docs/dev/CLAUDE.md | `docs/dev/tt4m_step2a_parallel_sizing.md:60-73` (Pool section correction) + `:204-218` (Section 2 reframe) + `docs/dev/CLAUDE.md:346-351` (file-list entry) |
| R55-4 | run the per-file block-count census for real, archive raw numbers, correct item 1's numbers if they move | `docs/dev/tt4m_step2a_parallel_sizing.md:408-424` (new Appendix, reproducible command + result: files=207, sum=3873, mean=18.71, median=12, min=1, max=357 — matches the design note's existing citation, so item 1's numbers do NOT move) + `docs/design/tt4m_harness_batching.md:35-38` (citation updated to point at the Appendix instead of an uncited claim) |
| R55-5 | fix `extract_cases.py`'s keying to (pattern, flags, features) or block ordinal; re-derive the density line with the learnings sec3 caveat | `studies/tt4m_batchrun/extract_cases.py:10-26,45-106` (docstring + full `cases_for_pattern` rewrite, keyed on the triple, whole-block-before-judging so a wrong candidate never leaks cases) + `docs/dev/tt4m_step2a_parallel_sizing.md:72-114` (Pool-section note + re-derivation: 12/1,022 patterns' content changed, count 7,729→7,730, density unchanged at 7.56) |
| R55-6 | dispatch_gen.py's decode() diverges from driver.c's on a trailing lone backslash; fix the code to match driver.c AND the claim | `studies/tt4m_batchrun/dispatch_gen.py` (new branch: `src[i]=='\\' && i+1>=srclen` now refuses identically to driver.c's decode(), `free`+`NULL`, matching error shape) |
| R55-7 | item 5 should say `SAB_FILE=`-anchored, not rows "naming" run.sh | `docs/design/tt4m_harness_batching.md:309-318` (reworded, with the false-recount arithmetic stated: 13 raw text-grep hits vs 8 real `SAB_FILE=`-anchored rows, six false positives named by id) |
| R55-8 | the 18.65x caveat must name its DIRECTION (baseline contention inflates the ratio favorably) | `docs/dev/tt4m_step2a_parallel_sizing.md:333,344-357` (Addendum) + `docs/dev/CLAUDE.md:366-370` + `docs/design/CLAUDE.md` (tt4m_harness_batching.md entry, final sentence) |
| R55-9 | "~1.5-1.7x" → the table's true 1.48-1.66x | `docs/dev/tt4m_step2a_parallel_sizing.md:305-309` (Sensitivity bullet, with the three per-N ratios spelled out) + `:391` ("What is still owed" bullet) |
| R55-10 | NOT this lane's charter; moves to 2c/2d's brief | `docs/dev/tt4m_step2a_parallel_sizing.md:394-402` (stated as a named, unfixed gap in "What is still owed" — not built here, per the outcome's own routing) |

Also fixed, found during this lane's own reading rather than named by an
R55 id: `studies/tt4m_batchrun/CLAUDE.md`'s "Prior art reused" section
claimed `extract_cases.py` was "adapted, logic-unchanged" and
`dispatch_gen.py`'s decode() was "byte-identical" — both statements were
made false by R55-5/R55-6 respectively (or, for the decode claim, were
already false and are now corrected to be true); both paragraphs updated
to describe the fixes and their measured effect.

## What R55-1..9 did NOT require touching

- `docs/dev/lanes/tt4m2_report.md` — never rewritten. A dated `## 2026-09-08
  CORRECTION` section is APPENDED after the original handback, restating
  every disposition above in the lane's own voice for a reader who lands
  on that file directly (house convention: lane reports are historical
  once merged, corrected forward rather than edited in place).
- `src/`, `tests/harness/`, `docs/spec/` — none of R55-1..9 touch pcrec
  itself or the harness; every fix lives in the design note, the
  measurement memo, their two CLAUDE.md file-list entries, and the
  `studies/tt4m_batchrun/` tooling the memo's own numbers came from.

## Validation

- `studies/tt4m_batchrun/make check` (both tooling fixes applied,
  `extract_cases.py` + `dispatch_gen.py`): **`cases: 15 mismatches: 0`,
  `check: OK (tooling smoke test passed, answer identity confirmed)`,
  5.8s wall** (well under the 4-minute do-then-finish threshold — ran
  and finished in the foreground). `dispatch_gen.py` is exercised by
  this smoke test's `batched` subcommand (confirmed by reading
  `batchrun.py`'s `import dispatch_gen` call sites), so the R55-6 decode
  fix compiled and ran cleanly, not merely syntax-checked.
- `python3 -c "import ast; ast.parse(...)"` on both edited `.py` files:
  clean.
- `extract_cases.py`'s fix additionally verified against a hand-built
  two-block fixture (identical pattern text, `flags i` on the first
  block, no flags on the second): each prefix now resolves to its own
  block's cases exclusively, confirmed by direct output inspection
  before any corpus-scale test was trusted.
- **R55-5's density re-derivation is a REAL re-measurement, not an
  estimate**: rebuilt the worktree (`make -j4 CC=gcc-16`), reproduced the
  2a memo's exact 1,022-pattern pool (same 207-file list minus
  `known_fail`, same `--count 1024 --require-features ""`), ran BOTH the
  pre-fix (`git show HEAD:studies/tt4m_batchrun/extract_cases.py`) and
  post-fix extractors against the identical manifest, and diffed the two
  case sets directly — 12/1,022 patterns differ in content, 10 in count,
  net aggregate change +1 case, density unchanged at 7.56/pattern to two
  decimal places (7.5626 vs 7.5636).
- **R55-4's census is a real command run against the live tree**, not
  copied from any prior claim: `find tests -name '*.rxt' -not -path
  'tests/known_fail/*'` (207 files, matching the design note's own
  population) piped through a per-file `grep -c '^pattern '` count and
  summarized — archived as a reproducible one-liner in the memo's new
  Appendix.
- No `make test`/`make` run against `tests/harness/` or `src/` — this
  revision touches none of it, so the top-level suite is unaffected by
  construction. `build/pcrec` was rebuilt once (`make -j4 CC=gcc-16`) to
  regenerate the pool for the R55-5/R55-4 re-measurements above.

**Nothing is OWED from this lane's own charter.** R55-1 through R55-9 are
all landed with a checked hunk above; R55-10 is explicitly named as moved
to STEP 2c/2d's brief (its own outcome text), not silently dropped.

## Handback

Branch `lane/tt4m2f`, one revision commit (plus this report), on top of
`lane/tt4m2`'s already-merged state on `main`. Never merged by this lane.
2c opens on this revision's landing per the r55 panel's own outcome,
carrying: the routed-block exclusion (R55-1, now in the design note
itself), the per-`-c` D45 composition (R55-2, likewise), and the
evidence-archiving bar (R55-10, explicitly named as owed in the memo's
"What is still owed").
