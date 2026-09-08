# [TT-4M] STEP 1 — darwin batched-build validation

Lane tt4m (sonnet), 2026-09-08. Re-opens [TT-4]'s closed levers
(docs/dev/tt4_measurement.md, [TT-4.1], Linux, 2026-08-23; closed by Frank
2026-08-23 on the ruling "gcc is 17% of `make test`'s CPU ... spend the
effort where it has the greatest impact") on THIS Mac, where the profile is
different by measurement, not assumption: [TT-14] and [XARCH] STEP 0 half 1
both find the Mac's `make test` cost is PROCESS-DISPATCH spawn tax, not
compute (a serial `test-corpus` measured ~27x slower wall than the old
Linux box while gcc CPU-seconds on this Mac's gcc-16 are actually ~1.93x
*faster* per artifact than the bench's Ryzen/gcc-15.2 — docs/dev/
xarch_step0.md §1.3-1.4). Frank's directive verbatim (plan.md [TT-4M]):
"have pcrec simply build several at once as part of the rxt file process
then gcc them all at the same time into a single executable (have main()
take options to select) then we could test with fewer processes. validate."

**Scope**: measurement + prototype ONLY, entirely under `studies/
tt4m_batchrun/` (own Makefile/CLAUDE.md, studies/CLAUDE.md's convention).
Nothing under `tests/harness/` or `src/` is touched or read-write; both are
read-only reference for reproducing their exact protocol. Harness adoption
is [TT-4M] STEP 2, its own later row, gated on these numbers.

## Method

**Box**: this Mac, M1, 10 cores (`sysctl -n hw.ncpu`), gcc-16 16.2.0
(Homebrew), macOS. Measured 2026-09-08. **Bare `timeout` on this box IS GNU
coreutils 9.11** (`timeout --version` names it directly) — UNLIKE [TT-4.1]'s
Linux box, which had uutils coreutils' `timeout` on `PATH` by default and
measured a real ~104.5ms/call wall tax from it (docs/dev/
tt4_measurement.md, "The `timeout` binary itself"). That specific lever
does not exist on this Mac as a separate finding; every timing below
already runs under the fast binary.

**Box coordination**: a full-population `tests/codegen/
run_encoding_checks.sh` run was executing on this box (PID 84953,
`/tmp/encchk_investigate/enc_full_final.log`) for the whole construction
phase of this lane. Per the standing one-heavy-suite-at-a-time rule, every
timing sweep below was held until that log's "checks failed:" completion
line appeared (it did: `checks passed: 11 / checks failed: 0`, 16:14 EDT);
construction (writing/smoke-testing the tooling at n=8 patterns, collecting
a 128-pattern pool via pcrec-only spawns) proceeded in parallel since
neither touches gcc or runs a multi-minute batch.

**Load context for the sweep itself (2026-09-08, 16:15-16:19 EDT)**:
`uptime` immediately before the baseline run read **load averages 9.61 4.76
3.09** — elevated, NOT from another pcrec lane (`ps aux` sorted by CPU%
showed only OS housekeeping: `logd` 69.7%, `frauddefensed` 28.6%,
`spotlightknowledged.updater` 25.4%, `corespotlightd` 23.8%, `WindowServer`
19.4% — plausibly Spotlight re-indexing after the just-finished
encoding-checks run's file churn, not a concurrent heavy suite). By the end
of the batched sweep (~4 minutes later) load had settled to **2.39 3.32
2.91**. This box was NOT quiet for this sweep — wall-clock numbers below
should be read as directionally reliable (the deltas are large, 2-12x) but
not as the box's floor; a re-run on a quiet box is worth doing before this
memo's numbers are cited as a floor rather than a validation.

**Prior art reused directly, not re-derived**: `studies/tt4_batching/
proto/collect_patterns.py` and `extract_cases.py` ([TT-4.1], Linux,
2026-08-23) are copied into `studies/tt4m_batchrun/` unchanged in logic —
both are machine-independent (pull real `pattern`/`flags`/`features` blocks
and real `m`/`n`/`ms`/`ns` cases straight from `.rxt` source, compile
through the live `build/pcrec`). `dispatch_gen.py` is NOT reused: the
Linux version predates DD-14.FB's `frames-buffer=` route argument and the
current typed give-up codes (`work`/`recurse`/`internal`, `tests/harness/
driver.c` today), so a straight copy would silently mis-decode this tree's
protocol. This lane's `dispatch_gen.py` is written directly against the
current `driver.c` (decode() byte-identical, give-up naming
byte-identical), scoped to the DEFAULT route only — see its own header and
"Caveats" below.

**Pool selection**: 128 patterns, the first 128 compilable, `perr`-free,
no-`--features` (default bucket) blocks from `tests/base/` in file order
(`collect_patterns.py --count 128 --require-features "" tests/base`) —
the same selection rule [TT-4.1]'s `corpus` pool used on Linux (that
memo's worst gcc-bound section), scaled down from 256 for a first darwin
pass. 413 real cases extracted from those patterns' own `.rxt` source
(`extract_cases.py`) — **3.2 cases/pattern average, notably lower than
[TT-4.1]'s `corpus`-section average of ~10.1 cases/pattern** (Stage A2);
this pool is a plain-directive slice of `tests/base` specifically, not
`test-corpus`'s full population across every module directory, so a lower
per-pattern case count is expected, not a discrepancy — flagged so the
per-case-run share below is not over-read against the Linux figure.

**Shapes measured**:
- **baseline** — the harness's own unbatched shape, reproduced exactly:
  per pattern, one `build/pcrec -p rx ... -o gen.c -- pattern` spawn (fresh
  dir per pattern, same as `run.sh`), one `gcc-16 -O1 -std=gnu11 -Wall
  -Wextra -Werror -I bdir -o t tests/harness/driver.c gen.c` spawn (driver.c
  UNMODIFIED, default `RXT_PREFIX=rx`, matching run.sh's own compile line
  byte for byte), then one `timeout 10 t subj pos` spawn per real case.
- **batched (shape L)** — per batch of N patterns: N `pcrec` spawns
  (distinct prefixes `rxNNNN`, one shared batch directory — UNCHANGED
  count from baseline, this is the residual lever, see below), then **ONE**
  `gcc-16` spawn naming the batch's generated `dispatch.c` PLUS all N
  `gen.c` files as SEPARATE arguments on one command line (`gcc ... -o t
  dispatch.c rx0000.c rx0001.c ... rxNNNN.c`) — each `.c` is still its own
  translation unit by ordinary gcc semantics even though only one process
  is spawned, which is what dodges [TT-4.1]'s `PCREC_FEATURE_SET`/
  `PCREC_FEATURE_MODULES` unprefixed-`#define` TU-CONCATENATION collision
  by construction, without needing that memo's `--require-features`
  homogeneity restriction (confirmed directly below, not assumed). Then
  the same per-case `timeout` spawn shape as baseline, unchanged.
- Measured at N in {4, 16, 64} per the brief. TU-concatenation (literal
  source concatenation into one file, [TT-4.1]'s "shape B") was NOT
  measured — the brief's own ordering ("TU-concat measured second only if
  the link path leaves an obvious win unclaimed") and shape L's own result
  below (see "What the numbers say") answer that question without it.

**Deliberate scope hold, stated once**: the per-case matcher-run spawn
(`timeout ... t subj pos`) is IDENTICAL in count and shape between baseline
and batched. This isolates the gcc-invocation-count lever the charter asks
about. Exec-batching (collapsing the per-case spawn itself, one process per
PATTERN reading all its cases) is [TT-4.1] Stage A2's SEPARATE, ALREADY-
MEASURED lever (Linux: 5.57x net of the timeout-binary effect) and is not
this row's question — Frank's directive is specifically about the GCC
invocation count ("gcc them all at the same time into a single
executable").

**Instrumentation**: `studies/tt4m_batchrun/batchrun.py`'s `Spawner` counts
every `subprocess.run` call by kind (`pcrec`/`gcc`/`run`) and accumulates
wall (`time.perf_counter` deltas) and child CPU (`resource.getrusage
(RUSAGE_CHILDREN)` user+sys deltas) around each call — exact for this
process tree since the script is single-threaded and spawns serially (no
concurrent forking to attribute rusage deltas to the wrong call). All
sweeps below are SERIAL (no `--parallel`/`PROCS`-style concurrent batch
dispatch) — see "Caveats" for why, and for what a parallel-mode replication
of [TT-4.1]'s harness-realistic shape would still need to answer.

## Tooling validation (before any timing number is trusted)

**8-pattern / batch-4 smoke test** (`make check` in `studies/
tt4m_batchrun/`): baseline and batched both produce 15 real cases;
**0 answer-identity mismatches** across every case's (stdout, exit code)
pair. This confirms shape L's dispatch driver reproduces `driver.c`'s
match/nomatch/exit-code protocol correctly on real generated matchers
before any larger population is trusted.

**Feature-set collision, confirmed NOT to apply to shape L**: [TT-4.1]'s
obstacle is a TU-CONCATENATION-only failure (two matchers' unprefixed
`PCREC_FEATURE_SET`/`PCREC_FEATURE_MODULES` `#define`s landing in the same
preprocessing unit). Checked directly (not assumed): a 2-pattern batch of
`(?>a+)b` (`--features atomic-groups`) and `(?<foo>a)b` (`--features
named-groups`) — a heterogeneous pair that would fail TU-concatenation with
the exact `-Werror` redefinition error [TT-4.1] documented — compiled and
linked clean under shape L (`gcc -O1 -std=gnu11 -Wall -Wextra -Werror -I.
-o t dispatch.c rx0000.c rx0001.c`, rc=0, zero warnings) and both matchers
answered correctly (`match 0 3` / `match 0 2 0 1`). **Confirmed**: shape L
does not need [TT-4.1]'s `--require-features` homogeneity restriction at
all — a real, concrete advantage over TU-concatenation that follows
directly from never concatenating source in the first place.

## Results

Population: **126 of the 128 collected patterns** reached the sweep (see
"A methodological finding, not swept under the rug" below for the other
2), **413 real cases** — identical population for baseline and every
batched N, so every comparison below is apples to apples.

### 1-2. Baseline vs. batched: wall, CPU, process counts at N ∈ {4, 16, 64}

| shape | pcrec spawns | gcc spawns | run spawns | total procs | total wall | total CPU |
|---|---|---|---|---|---|---|
| baseline | 126 | 126 | 413 | 665 | **61.69s** | **34.02s** |
| batched N=4 | 126 | 32 | 413 | 571 | **25.62s** | **17.42s** |
| batched N=16 | 126 | 8 | 413 | 547 | **17.01s** | **13.26s** |
| batched N=64 | 126 | 2 | 413 | 541 | **14.41s** | **12.19s** |

**Speed-up vs. baseline**: N=4 → 2.41x wall / 1.95x CPU. N=16 → 3.63x wall
/ 2.57x CPU. N=64 → **4.28x wall / 2.79x CPU** — the best measured cell,
and bigger than [TT-4.1]'s own best Linux gcc-batching multiple (3.66x, on
CPU alone, at N=16 there). Every batch size tried is a clean win over
baseline; there is no batch size in {4,16,64} where batching loses, unlike
[TT-4.1]'s Linux finding that N=256 (batch count far below core count
under 12-way parallel dispatch) actively regressed — this darwin sweep is
serial-only (see Caveats), so that non-monotonic finding's mechanism
(starved cores) simply doesn't apply here yet; it would need a parallel
replication to check.

**Decomposed by spawn kind** (this is the more informative table — two
DIFFERENT levers are both firing, and the second was not the one this row
set out to measure):

| kind | baseline wall | N=4 wall | N=16 wall | N=64 wall | N=64 speed-up |
|---|---|---|---|---|---|
| gcc | 30.13s (126 calls) | 15.82s (32 calls) | 12.27s (8 calls) | 11.36s (2 calls) | **2.65x** |
| run (matcher-exec) | 31.12s (413 calls) | 9.41s (413 calls) | 4.34s (413 calls) | 2.64s (413 calls) | **11.79x** |
| pcrec | 0.44s (126 calls) | 0.39s | 0.40s | 0.41s | ~1.0x (unchanged by design) |

**A methodological finding, not swept under the rug**: only 126 of the 128
collected patterns reached the sweep. `studies/tt4m_batchrun/
collect_patterns.py`'s manifest is a bare TSV with no quoting — two
`tests/base/bounded_repeats.rxt` patterns contain a LITERAL TAB CHARACTER
inside the pattern text itself (`a{<TAB>1}`, `a{ 1<TAB>,<TAB>2 }` — the
corpus deliberately exercises PCRE2's whitespace-inside-braces leniency),
which adds extra tab-separated fields and fails the 5-field parse in both
`read_manifest`/`read_cases`. This is a limitation INHERITED from
[TT-4.1]'s Linux `collect_patterns.py` (copied unchanged here, per this
lane's own stated reuse policy) — not introduced by this lane, but real,
and it affects both shapes EQUALLY (both read the same manifest), so it
does not bias the baseline-vs-batched comparison; it does mean this pool
is 126, not literally 128, real patterns. Not fixed here (out of this
row's validation scope; a harness adoption would need a properly quoted
manifest format, which the harness itself never needs since `run.sh`
reads `.rxt` files directly rather than through an intermediate TSV).

### 3. Answer identity over the full 126-pattern / 413-case slice

**Zero mismatches at every batch size.** Diffed every case's (stdout, exit
code) pair, baseline vs. each of N=4/16/64: `mismatches=0`,
`missing_in_batched=0`, `extra_in_batched=0` at all three N. Combined with
the feature-heterogeneity check above and the 8-pattern smoke test, this is
three independent correctness checks (smoke-scale, full-scale identity,
heterogeneous-features) all clean.

### 4. Degradation: one non-compiling batch member

Re-run at all three chartered batch sizes on the real 128-pattern pool
(not just the 8-pattern smoke pool): plant the syntax error in member 0,
measure the batch's all-or-nothing link failure, then the per-pattern
fallback cost to recover the OTHER N-1 members.

| N | batch pcrec+link (fails) | fallback: N individual gcc compiles |
|---|---|---|
| 4 | 0.42s wall / 0.39s CPU (5 procs) | 0.84s wall / 0.88s CPU (4 procs) |
| 16 | 1.57s wall / 1.44s CPU (17 procs) | 3.67s wall / 3.89s CPU (16 procs) |
| 64 | 5.96s wall / 5.41s CPU (65 procs) | 14.70s wall / 15.81s CPU (64 procs) |

Every fallback compile matched its expected outcome (`fallback_results`:
the corrupted member fails again, rc≠0; every other member succeeds,
rc=0) — 0 unexpected fallback failures at any N. **The shape is exactly
[TT-4.1]'s Linux finding, confirmed on darwin and on shape L specifically**:
a batch's own failure is CHEAP to detect (the link fails fast — gcc never
gets far enough to do the good members' code generation work, since one
member's compile error aborts before the link step is reached) but the
REAL cost is redoing the other N-1 members' compiles from scratch, and
that recovery cost scales linearly with N (0.84s → 3.67s → 14.70s, roughly
4x per 4x increase in N, as expected for N independent recompiles). A
larger batch trades a lower steady-state cost (Results 1-2 above) against
a bigger blast radius on any single bad member — the same design tension
[TT-4.1] flagged as owed to STEP 2, now with darwin numbers to size it by.

### 5. Residual: the pcrec-spawn share

Standalone collection-phase measurement (128 pcrec spawns, before any gcc
work): 0.455s wall / 0.420s CPU total, ~3.55ms wall / ~3.3ms CPU per spawn.
**This matches the in-sweep numbers closely** (baseline: 0.44s/126 calls =
3.5ms/call; batched, all N: 0.39-0.41s/126 calls = 3.1-3.3ms/call) —
cross-validating the `Spawner`'s rusage-delta measurement against an
independent standalone timing, and confirming pcrec's own spawn cost is
genuinely N-independent (unchanged by design: batching never reduces the
pcrec-spawn count, only gcc's).

**The D77 trigger judgment**: at the best-measured cell (N=64), pcrec's
share of the BATCHED path's total wall is **0.41s / 14.41s ≈ 2.8%**. Even
at the worst chartered batch size (N=4), it is 0.39s / 25.62s ≈ 1.5%.
**Plainly: NOT triggered.** pcrec's own spawn cost is a small, roughly
flat, single-digit-percent share of the total picture at every batch size
measured — nowhere close to being the new bottleneck a multi-pattern pcrec
CLI mode (a `src/` change) would need to justify under D77's "wait for a
measured need" standard. The gcc-invocation lever (Results 1-2) and the
unplanned run-exec lever (below) both dwarf it. If a future STEP 2 harness
adoption pushes gcc/run costs down far enough that pcrec's ~0.4s floor
starts to dominate a batch's wall, THAT measurement — not this one — would
be D77's trigger.

## An unplanned second finding: batching also collapses per-binary launch cost

This row's scope decision (stated above) was to hold the per-case matcher-
run spawn IDENTICAL in count and shape between baseline and batched, so
the measured delta would be the gcc-invocation-count lever ALONE. **The
data says that scope decision did not actually isolate a single lever** —
"run" wall dropped by **11.79x at N=64** (31.12s → 2.64s). That is bigger
than the gcc lever's own 2.65x, on a component this row deliberately tried
to hold constant.

**Investigated directly, not left as a mystery**: the per-case spawn is
`timeout 10 <exe> ... subj pos` in both shapes — same argv shape, same
binary count of 413 total invocations either way. What DOES differ is the
number of DISTINCT executables those 413 invocations touch: baseline runs
413 cases through 126 different `t` binaries (~3.3 cases/binary); at N=64
the same 413 cases run through only 2 distinct batch executables (~206.5
cases/binary). A microbenchmark isolates this directly: invoking the SAME
already-built baseline binary 200 times in a tight loop (`timeout 10
<one-pattern's-t> a 0`, warm after the first call) measured **4.72ms/call
average** — matching the batched N=64 in-sweep average of 6.4ms/call
(413-way, includes the first cold touch of each of the 2 binaries) far
more closely than baseline's own 75.4ms/call average across 126 distinct,
mostly-cold-per-binary executables.

**Read plainly**: on this Mac, a large share of the per-case "run" cost in
the UNBATCHED shape is not the match itself (matches here are trivial,
sub-microsecond automatons over tiny subjects) — it is the cost of
launching a DIFFERENT, previously-unseen Mach-O executable almost every
time (first-touch: dyld loading, on-disk page-in, whatever this
platform's launch-path validation does for a fresh binary), not exec/fork
overhead in general (that part is shared by both shapes and is small,
consistent with `timeout`'s own GNU-coreutils ~3.5-4ms/call this box
already has). Batching collapses the number of DISTINCT executables
touched from one-per-pattern to one-per-batch, and that reduction alone —
never intended as a deliberate lever by this row's scope decision — is
responsible for MORE of the measured speed-up than the gcc-invocation
count reduction is. This is a genuinely Mac-relevant finding given
[TT-14]'s framing of the whole re-open (spawn tax, not compute): batching
narrows spawn tax on TWO independent axes (fewer gcc invocations, fewer
distinct binaries launched at run time), not the one axis this row set out
to isolate. It is reported here rather than re-scoped away, and STEP 2
should treat it as a real, separately-citable reason to batch — not a
side effect to ignore because it wasn't the question asked.

## Caveats — what this prototype does NOT model about the real harness

(Read `tests/harness/run.sh` read-only to name these; nothing here is
inferred without checking the actual script.)

- **No `timeout`-wrapping of the pcrec/build stages themselves.** `run.sh`
  wraps every pcrec invocation in `"$TIMEOUT_BIN" "$(pcrec_timeout_secs)"`
  (20s default / 60s under a sanitizer axis) and every compile in
  `gen_timeout.sh`'s `gen_cc` (a `bash -c 'ulimit ...; ...'` wrapper
  enforcing the D45 CPU/wall/memory budget) — this prototype spawns
  `pcrec`/`gcc-16` directly with no such wrapper. [TT-4.1]'s Stage A2 found
  this wrapper alone costs real, measurable overhead on Linux (`gen_cc`'s
  bash-fork+ulimit tax, ~75ms/call at `corpus`'s call volume) — a real
  harness adoption of shape L would still pay an analogous per-batch
  wrapper cost this prototype does not include.
- **No `GENCFLAGS` axis sweep.** Only the harness's DEFAULT `-O1 -std=gnu11
  -Wall -Wextra -Werror` is exercised. `LINTGEN=1` (`-fanalyzer`),
  `CLANGGEN=1` (compiler swap), and `RXTFLAGS` (an arbitrary extra-flag
  axis, e.g. `-fno-splice-calls`) all ride the SAME `gen_cc` call site in
  the real harness and are untested here — a batched build under
  `-fanalyzer` in particular could behave differently at the process level
  (one analyzer pass over N concatenated diagnostics contexts vs. N
  separate ones) and is unmeasured.
- **No per-case env/route diversity.** `run.sh` threads `RXTROUTE`,
  per-block `frames-buffer=` directives, and the `gu`/`engine`/`budget`
  vocabulary through `driver.c`'s third argument and its `_search_in`/
  `_match_in` cross-check machinery (DD-14.FB). This prototype's dispatch
  driver implements ONLY the default route (see `dispatch_gen.py`'s own
  header) — every pattern in this pool is from `tests/base`, which carries
  no `frames-buffer=` blocks, so the limitation is real but not exercised
  by this slice. A real adoption covering `tests/vm/`, `tests/atomic_groups/`
  or anywhere else `frames-buffer=`/`gu` appears needs a fuller dispatch
  driver.
- **No `.rxt` driver-protocol variance beyond `m`/`n`/`ms`/`ns`.** `g`/`gp`
  capture-group expectations, `perr` blocks (skipped at collection, never
  reaching gcc at all in either shape — a design question [TT-4.1] already
  flagged and left open: whether/how a `perr` pattern could even enter a
  batch), and head-bearing `.rxt` files' per-TARGET build path (H11,
  `pcrec --source --target`, a SEPARATE `gen_cc` call per target sharing
  the block's cases) are all untouched. A harness adoption needs a batching
  policy for each.
- **Serial only, no parallel-dispatch replication.** `run.sh`'s own
  `PROCS=N` fans out per-FILE workers, and [TT-4.1]'s Linux sweep found the
  single most important, easy-to-miss result was NON-monotonic under
  parallel dispatch: the batch size that maximizes real speed-up is the one
  whose BATCH COUNT is close to the core count, not the largest N — larger
  batches looked better serially and were measurably WORSE than the plain
  baseline once too few batches starved most of the box's cores. This
  darwin pass is serial-only (box-coordination: no concurrent heavy work
  while PID 84953 held the box). Stated plainly: this validation
  answers "does shape L save real wall/CPU at all on darwin" but NOT "what
  batch size is optimal under this box's own parallel dispatch" — that
  replication is owed to a follow-on measurement, not assumed transferable
  from the Linux finding just because the mechanism (starved cores at N
  near or above core count) is architecture-independent in principle.

## What the numbers say

**A measured YES, and a bigger one than [TT-4.1]'s Linux answer.** Shape
L — one gcc invocation naming N separate `.c` sources plus a generated
dispatch `main()`, never concatenating source — beats the harness's own
one-gcc-call-per-pattern shape at every batch size tried on this Mac, up
to **4.28x wall / 2.79x CPU at N=64** on a 126-pattern / 413-case slice of
`tests/base`, with **zero answer-identity mismatches** at any N and a
confirmed structural advantage over [TT-4.1]'s TU-concatenation approach
(no `--features` homogeneity restriction needed — checked directly with a
genuinely heterogeneous pair, not assumed from the mechanism alone).

**The win is bigger than the gcc-invocation lever alone accounts for**,
and that is this memo's most important qualification, not a footnote: of
N=64's 4.28x wall speed-up, the gcc lever this row set out to measure
contributes 2.65x on its own component, while an UNPLANNED second lever —
fewer DISTINCT executables launched at case-run time — contributes 11.79x
on its own component and is investigated and confirmed directly (a
same-binary-reuse microbenchmark lands at 4.72ms/call, matching the
batched shape's amortized per-call cost far better than baseline's
75.4ms/call across 126 mostly-cold binaries). Both levers point the same
direction and neither was held perfectly separate from the other in
practice, because the harness's real behavior does not offer a way to
change gcc-invocation count without also changing how many distinct
binaries get launched at run time in the SAME step — the "hold per-case
run shape identical" scope decision succeeded at the SPAWN level (same
count, same argv shape) but not at the binary-identity level, which turned
out to matter more.

**Answer identity: clean everywhere tested.** Zero mismatches across
413 real cases at N∈{4,16,64}, zero mismatches on the 8-pattern smoke
pool, and a direct heterogeneous-`--features` pair compiled and ran
correctly under shape L. No divergence was found or papered over.

**Degradation is real and scales with N, exactly as [TT-4.1] found on
Linux**: a batch's own link failure is cheap and fast to detect (0.42s-
5.96s across N=4-64), but recovering the batch's other good members costs
a full per-pattern recompile of all of them (0.84s-14.70s, scaling
linearly with N) — the steady-state win (Results 1-2) and the worst-case
blast radius (Result 4) both grow with N, and STEP 2's batch-size choice
is a real trade between them, not a free "bigger is always better" knob.
This darwin sweep did not replicate [TT-4.1]'s Linux discovery that a
too-large N actively regresses under PARALLEL dispatch (batch count
starving cores) — this sweep is serial-only, so that finding's mechanism
was never exercised here; STEP 2 needs its own parallel-mode replication
before picking a production batch size, not an assumption that darwin's
serial numbers alone name the right N.

**D77 residual trigger: NOT met.** pcrec's own spawn cost is ~1.5-2.8% of
the batched path's total wall at every N measured, essentially flat
(pcrec-spawn count and cost are unchanged by batching, by this row's own
scope decision) and cross-validated by an independent standalone
measurement. A multi-pattern pcrec CLI mode (`src/` change) is not
justified by today's numbers — the two levers already measured here
(gcc-invocation count, distinct-binary launch count) capture nearly all of
the available win, and pcrec is nowhere near becoming the new bottleneck.

**What STEP 2 (harness adoption, a separate future row) needs to decide,
per the Caveats above**: a batching policy for `perr` blocks (never reach
gcc — do they enter a batch at all?), head-bearing `.rxt` files' per-TARGET
build path (H11), routed/`frames-buffer=` cases (this prototype's dispatch
driver does not model them — real for `tests/vm/`/`tests/atomic_groups/`
populations, not for the `tests/base` slice measured here), the D45
budget-wrapper overhead a real adoption would still pay per batch (not
modeled here), the `GENCFLAGS` axis family (`LINTGEN`/`CLANGGEN`/
`RXTFLAGS`, untested), a fix for the discovered tab-in-pattern manifest
limitation if a TSV-shaped intermediate format is kept, and a chosen batch
size informed by BOTH this memo's degradation numbers AND a parallel-mode
replication this row did not run. None of these blocks STEP 1's verdict —
they are what STEP 2 needs to design against, the same relationship
[TT-4.1]'s Linux memo had to its own STEP 2 that never shipped.
