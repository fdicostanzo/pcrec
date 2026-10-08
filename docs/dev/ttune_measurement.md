# [TT-JTUNE] — tuning `make test` parallelism by the natural process

Living document (lane ttune2, 2026-10-08, Linux dev box: Ryzen 7 7700X, 16
threads). Frank's ask: the suite "sometimes goes serial but we have 16 procs",
it may also "oversaturate the procs", and NO dedicated sweep: every `make
test` that runs anyway runs under a ROTATED shape and is measured
(`scripts/perfrun`). Ledger readings are appended to section 6 as they
accumulate. Prior art, not redone: known_issues.md K44 "DIRECTION (b)
MEASURED THREE WAYS" (old 12-core box: `-j4 PROCS=3` fastest and the only
clean shape; `-j12 PROCS=1` reds the `[a-z]{0,30000}` resource CPU cap) and
tt12_step0_profile.md.

## 1. The instrument

    scripts/perfrun --label decfbB1 -- "$L/test.log" [MAKEVAR=val ...]

Replaces the chain's raw `make -k -jN -Otarget test` line. Picks the shape
(J = make -j, P = PROCS) from `scripts/perfrun.shapes` (least-sampled
UNCONTAMINATED shape; ties in file order; `--shape J,P` overrides; `--next`
prints the pick), runs `gnutimeout 2700 make --debug=j -k -jJ -Otarget test`
with `PROCS=P`, returns make's rc unchanged. The log is BYTE-IDENTICAL to the
raw line's: `--debug=j` adds scheduler lines, and `scripts/sectiontimes stamp
SIDE` diverts exactly those lines (a closed regex) to the per-run sections
file. The verdict note goes to stdout and `LOG.perfrun`, never into LOG.

Per-run files (no merge conflicts): `<main tree>/build/perf/ttune/<run_id>.
{row.tsv,samples.tsv,sections.tsv}`, an absolute path found from any
worktree, gitignored, surviving worktree pruning. The manager runs
`scripts/perfrun --fold` in MAIN to append the rows to
`docs/dev/ttune_ledger.tsv` and copy the samples/sections into
`docs/dev/ttune_ledger.d/` (then `git add`). The rotation reads both places.

Ledger columns: run_id, date, tree (sha8, +dirty), label, J, P, wall_s, cpu_s
(user+sys of the whole make tree, from bash `times`), rc, sect_err (the
`*** [...test-X]` count), k44_1807 / k44_cpucap (RED if the log shows the
counterk.rxt:1807 cell failing / "CPU limit exceeded"; ok otherwise — a
log-grep heuristic, not a coverage claim), load1_start, contam, red_class,
mean_busy (mean all-core busy% over the 15 s samples), nproc.

CONTAMINATION (contam=YES) = box busy >25% in a 2 s probe before the start,
or any other git tree with a `make` running at the start or in ANY 15 s
sample (another lane's chain, the bench's `make check`; process names and
/proc cwd only). Contaminated rows are kept but do not count toward a
shape's sample total or the decision rule.

## 2. Triage: a red shape is not the lane's failure

`red_class` (also printed, with a NOTE line, by perfrun):

| class | meaning | chain reader's action |
|---|---|---|
| green | rc 0 | none |
| K44-ONLY | every red section is in {test-corpus, test-counterk, test-resource, test-cli} AND the log carries the 1807 or CPU-cap signature | FLAG, don't re-run in-chain. Re-run the named sections solo (`make test-counterk`...); green solo = GREEN-BY-DIAGNOSIS (K44) |
| LOAD-SUSPECT | red with TIMED OUT / INCONCLUSIVE / CPU-limit / exit 123-124 text on a contaminated box | same: re-run the red sections solo before blaming the change |
| WALL-TIMEOUT | the 2700 s cap fired (a too-serial shape) | a datum about the shape; sections that finished are in the log |
| RED-REAL | anything else | a real red |

Flag, not re-run: the wrapper must give the chain exactly the verdict a raw
run would, and a second pass would double the heavy run. The triage reader
re-runs only the named sections.

## 3. Profile #0 — the decfbB0 chain (`make -k -j6 -Otarget test`, PROCS default = 16)

Raw: `build/perf/decfbB0_chain.tsv` (main tree, 37 rows, 15 s). Trailer:
build 10:41:41, `make test rc=0` at 10:55:13 — 13 m 32 s wall, 0 section
errors, rc 0. CAVEATS: (1) the sampler was started at 10:48:33, so it covers
only the LAST 6.5 of the 13.5 minutes (27 test-window rows; 10:41:41-10:48:33
is unprofiled); (2) the run predates `--debug=j`, so there are no per-section
times, only the scripts column as a proxy; (3) the box was not otherwise
loaded (only this chain; ttune2's light selftests ran after 10:55).

Sampled window, 10:48:33-10:55:06 (27 rows):
- mean busy 82.9% ; 24 of 27 rows >= 69%; the first 4 rows 97-99%.
- load1 peaked at 84.0 with 148 processes running at 10:54:06-:21 (16 cores):
  that is the OVERSUBSCRIPTION signature. Cause visible in the scripts
  column: `-j6` outer x `tests/clskit/crosscheck.py` 35 processes +
  `tests/run_g2.sh` 16-18 + `tests/harness/run.sh` 9-10 simultaneously. Busy
  was already 88-99% there, so the oversubscription costs no idle time; its
  cost is the CPU-budget cells (K44) and noise, not wall.
- Earlier load1 38-44 / running 44-130 (10:48:33-10:50:49) is the same class.

Stretches below 60% busy (3 rows, ~45 s, 10:51:19-10:51:49): busy 59/53/58,
running 8-14, load1 25-36. Scripts then: `tests/harness/run.sh` (3-6),
`tests/recursion/run_recursion_diff.sh` (1-2), `tests/rxtsource`,
`tests/codegen/run_cpset_structure.sh`, `run_entry_shape_identity.sh`,
`run_prefilter_collapse.sh`, `tests/ucp`/`uprops` — a changeover between the
assertions/identity/recursion wave and the harness wave, where several
sections are mid-startup or serial. This is the SERIAL-STRETCH instance and
it is small: 45 s of 13.5 min.

Critical-path tail: 10:55:06 busy 69% / running 13 (`tests/run_g2.sh` 8, the
three startset checks 4, one `dfahat_checks.py`); the make test finished at
10:55:13. So the tail is ~25-30 s of `run_g2` + startset draining — short. The
10:55:21+ rows (29%, 14%, 9%) are the chain's strict/alloc stages, not make
test.

Long serial sections: NOT identifiable from this run (no per-section times).
Candidates seen alone in the scripts column over several rows:
`tests/recursion/run_recursion_diff.sh` (present 10:50:49-10:51:34, 2->1
procs), `tests/resource/run_resource_tests.sh` (1 proc), `tests/axes/
run_axes.sh` (1-3 procs, 10:51:34-10:53:04+), `tests/clskit/run_clskit_tests.sh`
(1 proc but spawns 22-35 python workers). Proposed Makefile schedule fix: NONE
YET — "start the long serial sections first" needs section start/end times,
which the first perfrun rows (sections.tsv) provide; D77 says name the
measurement before building. The order of `TEST_SECTIONS` only matters for the
first `-jJ` slots, and perfrun's sections.tsv will show the critical-path
section per run.

Headline: the default-PROCS `-j6` shape was ~83% busy, 13.5 min (vs 11.3 min
measured at `-j16`, docs/testing.md), never idle for long; the visible cost
is load1 up to 84 (5x oversubscribed), i.e. K44 exposure, not lost wall.
Serial stretches exist but are short here (45 s + ~25 s tail). The real
question is the oversubscription/K44 side, which needs the rotation to answer.

## 4. Decision rule: when is the ledger enough?

A shape is ELIGIBLE with >= 2 uncontaminated rows (a K44-ONLY or other red
in an uncontaminated row disqualifies the shape for the default unless the
same cell is also red at the baseline shape). The
rotation is enough when: (a) at least 4 shapes are eligible, including
`16,16` (today's behaviour) as the baseline; (b) for the best shape B,
median wall(B) < median wall(baseline) by more than the observed noise =
max(5%, the largest within-shape spread (max-min)/median among eligible
shapes), and B is not worse on cpu_s by >15%; (c) B has zero K44/cap reds
over its rows. If two shapes tie within noise, prefer the lower J x P product
(less load, fewer K44 chances). Then a FOLLOW-UP lane (not ttune2) changes the
default.

## 5. Options for the default (written for that follow-up lane)

Today `make test` uses whatever `-j` the caller passes and each PROCS-aware
section defaults to `tests/lib/procs_default.sh` (nproc on Linux, performance
cores on the Mac) — the two layers multiply (J x P).
1. Derive P from J: procs_default.sh reads `-jN` from `MAKEFLAGS` (make
   exports `-jN` in MAKEFLAGS to sub-makes; under the jobserver form the
   number is `--jobserver-auth` only, so read `-j` from the parent via an
   explicit `TEST_J` export in the `test:` recipe) and returns
   `max(1, ceil(NCPU / J))`. This caps the product near nproc by
   construction, on any box (Mac 8 perf cores included), no constant. Fits
   the house rule "derive, don't tune a constant".
2. Cap the product with a ceiling rather than dividing: P = min(nproc,
   max(1, floor(K x nproc / J))) with K (e.g. 1.5) the measured oversubscription
   the ledger shows the box tolerates; K would be an unmeasured constant
   unless the ledger sets it.
3. Change the `test:` recipe to default J itself (`$(MAKE) -j$(J)` when none
   given) as a function of nproc — only if the winner has J independent of
   P, which the rotation tests.
The ledger decides between 1 and 2 (it reports whether the winner's J x P is
near nproc); option 1 is the recommendation.

## 6. Ledger readings

(None yet: row #0 is the decfbB0 profile above; rotation rows are appended
here by whoever folds the ledger.)
