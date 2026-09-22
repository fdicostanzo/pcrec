# [REL-1.6] CI (lane rel16, sonnet, 2026-09-21)

Delivers `.github/workflows/ci.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, a
`docs/testing.md` "CI" subsection, and one line in root `CLAUDE.md`'s "Build
& test". I cannot run GitHub Actions from this worktree — the manager pushes
the workflow and reads the run. This report is the "fits?" measurement plan
the charter asks for, plus the fallback design (not built, per D77).

## 1. What the first run answers, and how to read it

The charter's own first measurement is the wall time of a plain `make test`
on a runner. The workflow's `make test` step is that measurement, not a
report about it: `{ time make test; } 2>&1 | tee build/ci_test.log`, no
`-j`, no `HARNESS_BATCH` — the same invocation `docs/testing.md` calls the
merge/close standard, run exactly as a stranger cloning the repo would run
it.

**To read the result:**

1. **Did it fit at all** — the job's own status (green / red / timed-out).
   A timeout shows as the `make test` step being killed at 90 minutes; the
   job-level 120-minute backstop only matters if some *earlier* step (the
   apt-get install, the build, `make strict`) itself hangs, which none of
   them have any history of doing.
2. **The wall/user/sys split** — `time`'s own three lines, at the tail of
   `build/ci_test.log` (uploaded only on failure, per the brief; on a GREEN
   run this number is only visible in the step's own GitHub Actions log,
   which is fine — nothing here is a standing artifact people should have
   to fetch to see the number). This is the actual headline: how much
   headroom is there against the 90-minute step budget.
3. **Section-completeness, independent of timing** — grep the log for
   `sections ran: N/M`, the trailer `docs/testing.md`'s own "`make test`'s
   completion trailer" section describes. `N/M` less than the section count
   (40 at this pin) with a nonzero exit means real sections failed to
   launch (a shared prerequisite broke), not merely that some section's
   *content* failed — a different, sharper failure than an ordinary FAIL
   line and worth distinguishing when triaging the first red.

**What is NOT available, and why no attempt was made to add it here:** a
per-section timing breakdown (which of the 40 sections dominates on THIS
runner's hardware). `make test`'s own recipe never times its sections
individually — I checked `tests/lib/run_group.sh` (the shared-script-group
runner `test-codegen`/`test-anchored-match` use) directly and it prints no
per-script timing either, only pass/fail. This is not new: `docs/dev/
tt4m_time.md`'s own two clean timing runs record the identical structural
fact — "attribution is structural (no per-section timestamps survive in
either log)" — for the *Mac* box, and nothing about a GitHub Actions runner
changes that; the trailer's `sections ran: N/M` line is a completeness
check, not a stopwatch. Building per-section instrumentation now, before
knowing whether the plain run even needs it, would be exactly the D77
violation the charter itself warns against ("wait, name the measurement
that would trigger it") — the trigger here is a first run that is red or
uncomfortably close to 90 minutes; a green run with real headroom needs no
new instrument at all.

If a real per-section number is later wanted, the cheapest path is not a
harness change: rerun the *same* commit's build with `TEST_SECTIONS`
temporarily split into a handful of `$(MAKE) target` invocations each
wrapped in `time`, in a throwaway workflow_dispatch job — read-only against
the section list, nothing under `tests/` touched. Named here as the
measurement to run if it becomes the actual question, not built.

**Reference points for the 90-minute budget** (both explicitly SCRATCH-TIER
and neither a confident prediction for a GitHub-hosted runner's own
hardware, which is why the budget is generous rather than tight):

| source | box | section count | wall |
|---|---|---|---|
| `docs/dev/tt4m_time.md`, 2026-09-12/13 | Mac dev box (M1 Max, serial) | 38 | 5124.29s (~85.4 min) |
| `dev_journal.md` 2026-09-09 part 7 ("S5 BATTERY, test stage") | same Mac dev box | 38 (nominally) | 42.6 min |

The two Mac numbers do not agree with each other at the same nominal
section count (different load, different point in the suite's growth, and
the second predates several sections' current cost profile) — which is
itself the reason not to treat either as a prediction for a GitHub Actions
runner's very different CPU/IO profile, only as evidence that 90 minutes is
generous against everything measured so far. `docs/testing.md`'s "Section
composition" note (`make -j$(nproc) -Otarget test` finishing in ~43-45s on
a since-retired 12-core box at a much smaller, 10-section suite) is `-j`
composition, not the plain serial run this workflow actually invokes, and
is cited in the workflow's own comments for that reason but not relied on
here.

## 2. Fallback if it does not fit: `test-ci`, DESIGNED not built

If the real run comes back red on the 90-minute step timeout (or green with
uncomfortably little headroom), the fallback is a new Makefile target,
`test-ci`, running a documented SUBSET of `TEST_SECTIONS` — never a
weakened variant of any kept section (the same rule `make smoke` already
follows). Per D77, this is not built here; the real run's own numbers pick
the cut, not a guess made before the numbers exist.

**Design, so the manager does not have to re-derive it from scratch under
time pressure:**

- The subset is chosen by REMOVING sections from the full 40, in the order
  below, stopping as soon as the remainder measures under budget with
  comfortable headroom (not merely under it) — never by re-deriving a list
  from vibes at the moment `test-ci` is actually built.
- **Removal order**, cheapest-to-lose first, each with the reason it is a
  reasonable first cut and NOT a reason to drop it blind:
  1. `test-tune-dial`, `test-entry-shape-identity`, `test-search-pinned`,
     `test-premul-table`, `test-anchored-match` — five sections the
     Makefile's OWN comments already single out as too heavy for `make
     smoke`'s 60s target and admit to a full corpus sweep each (one of them
     sweeping the corpus TWICE plus 19 differential drivers; another
     compiling and running sixteen matchers, ~6 min; another building a
     SECOND compiler for its overflow arm, ~7 min). These are optimization-
     SIGNATURE structural checks (did the compiler still emit the skip
     table / minimize / pin the search / pick the right entry rung), not
     end-to-end correctness checks — real answers still come from
     `test-corpus`/`test-reject`/`test-registry` even with these five gone.
  2. `test-dfa-uniform-fold`, `test-vm-frameless`, `test-prefilter-collapse`
     — narrower structural byte-identity checks over the same corpus,
     same argument as (1) at smaller individual cost.
  3. `test-corpus`'s own artifact-size ratchet tail (`check_size_tripwire.sh`,
     riding `test-corpus`'s recipe, not a separate section — cannot be cut
     independently of `test-corpus` itself, named here only so nobody
     proposes cutting it alone and is surprised it is not a target).
  4. Only past (1)-(2), if still not under budget: `test-reject` (55s at
     the last per-section measurement, cheap on its own, listed here
     because it is the next-cheapest REAL reach beyond the structural
     tier — cutting it loses "never miscompile" coverage for the reject
     table, a real loss, not a free one).
  5. `test-corpus` itself is NOT a candidate. It is the suite's dominant
     cost (~304s at the last per-section measurement, almost certainly
     more today) and also the suite's actual correctness backbone (every
     `.rxt` pattern's answer, the size log, the tripwire) — a `test-ci`
     that cuts it is not a lighter CI tier, it is a different, weaker
     product than what `make test` promises, which is the shape `make
     smoke` already refuses to be for the exact same reason.
- **Full `make test` still runs somewhere** if `test-ci` ships: the
  natural home is a second, non-blocking, scheduled (nightly or
  weekly) workflow_dispatch/schedule job running the real `make test`
  unmodified, so CI never becomes a permanently weaker promise than the
  README's own "clone and run `make test`" — not designed further here,
  since it is only needed if `test-ci` is.
- **What `test-ci` must NOT do**: silently redefine what "green" means for
  a contributor. If built, `CONTRIBUTING.md`'s checklist and this repo's
  `.github/PULL_REQUEST_TEMPLATE.md` line ("`make test` is green, or every
  failure is a documented, pre-existing skip") both need a rider naming
  `test-ci` as the CI-tier promise, distinct from the full suite — a
  `docs/spec/` hunk in D80's sense, since it changes what a caller (a
  contributor reading the badge) can observe.

## 3. Validation

- `.github/workflows/ci.yml` YAML: PyYAML was not present in this
  worktree's python3 (`import yaml` fails: `ModuleNotFoundError`), so the
  file was read carefully by hand instead — block structure, indentation,
  and the `${{ }}` expression syntax the `concurrency.group` line uses
  match GitHub Actions' documented `pull_request` +
  `github.event.pull_request.number` shape exactly, and there is exactly
  one top-level `jobs.test` with no duplicate keys at any level.
- `make -j4 CC=gcc-16` and `make strict CC=gcc-16` on this box: CLEAN,
  untouched-tree control (this lane's only tree edits are `.github/` and
  two documentation files; no `src/`/`cli/`/`lib/`/`tests/` change to
  regress).
- Package names cross-checked against the tree's own existing text:
  `tests/registry/run_registry_tests.sh:184` already names
  `libpcre2-8-0 libpcre2-dev` as the Debian/Ubuntu package pair; on
  Debian/Ubuntu, `libpcre2-dev` depends on the runtime package, so
  installing it alone satisfies both `run_registry_tests.sh`'s own
  "is `libpcre2-8-0` present" SKIP check and `tests/lib/resolve_pcre2.sh`'s
  pkg-config resolution (`pkg-config libpcre2-8`, confirmed by reading that
  file directly) used by PC-3, PC-4, and the definitions oracle.
- `CC := gcc` in the Makefile (not `?=`, per the Makefile's own comment on
  why `?=` does not work against GNU make's predefined `CC`) resolves to
  real GNU gcc on `ubuntu-latest` unconditionally — confirmed by reading
  the Makefile directly rather than assumed; no `cc_resolve.sh`-style
  CC-picking is needed in the workflow, unlike the darwin dev box.

## 4. What is owed

Everything in this brief is delivered. Nothing is OWED from this lane —
the workflow itself cannot be validated further without the manager
pushing it and reading a real Actions run, which is explicitly outside
this lane's own capability per the brief.
