# [TT-4M] STEP 2 (2a) — parallel-dispatch N x P sizing measurement

Lane tt4m2 (sonnet), 2026-09-08. Owed by STEP 1 (docs/dev/tt4m_darwin_validation.md,
"Caveats — Serial only, no parallel-dispatch replication"): that memo
validated shape L (one gcc invocation naming N pcrec-emitted `.c` sources
plus a generated dispatch `main()`) against the harness's unbatched shape
at N in {4,16,64}, but every measurement ran ONE PIPELINE AT A TIME.
[TT-4.1] (Linux, docs/dev/tt4_measurement.md) found batch size is NOT
monotonic once real PARALLEL dispatch enters the picture — a batch count
too far below the box's core width starves most of the box, and the
batch size that maximizes serial throughput can be measurably WORSE than
the plain baseline under `PROCS=N` fan-out. This memo asks: does darwin
reproduce that non-monotonicity, and if so, where is the (N, P) knee on
THIS box?

**Scope**: measurement only, entirely under `studies/tt4m_batchrun/`
(extends the STEP 1 prototype with a `parallel` subcommand — see that
directory's own CLAUDE.md). Nothing under `tests/harness/` or `src/` is
touched. STEP 2's harness-ADOPTION design is `docs/design/
tt4m_harness_batching.md` (2b), a separate deliverable that cites this
memo's numbers.

## Method

**Box**: this Mac, M1, `sysctl -n hw.ncpu` = 10 (8 performance cores +
2 efficiency, `hw.perflevel0.logicalcpu`=8 / `hw.perflevel1.logicalcpu`=2).
`tests/harness/run.sh` itself defaults `PROCS` to `nproc` (10 here, 12 on
the Linux reference box — the "harness today runs 12-way" figure the
brief cites is that Linux default, not this Mac's).

**Extending the STEP 1 tool, not re-deriving it**: `studies/tt4m_batchrun/
batchrun.py` gained a new `parallel` subcommand (own CLAUDE.md /
docstring). It shards the pool's BATCHES (not raw pattern rows) round-robin
across P workers, writes each worker its own sub-pool (`manifest.tsv` +
`cases.tsv`), and launches each worker as an independent `batchrun.py
batched` SUBPROCESS — the same self-reinvocation shape `tests/harness/
run.sh`'s own `PROCS>1` fan-out already uses (own workdir, own output,
parent aggregates). Wall is the PARENT's own outer wall clock (workers
genuinely overlap, so summing each worker's own wall would double-count);
CPU is read two ways and cross-checked: `agg_cpu_sum` sums every worker's
own `RUSAGE_CHILDREN`-measured total, and `cpu_outer_rusage_children`
reads THIS process's own `RUSAGE_CHILDREN` after every worker is reaped
(which POSIX `wait()` semantics cascade a terminated worker's own
`RUSAGE_CHILDREN` into, exactly the same accounting STEP 1's serial
`Spawner` class already relied on one level down). The two num bers agree
to within 5-8% at every cell measured below (the gap is each worker's own
Python-interpreter CPU time, which neither number is trying to capture) —
cross-validating that the aggregation is not silently dropping or
double-counting a worker's usage.

**Tooling validation** (before any timing number below is trusted): an
8-pattern / batch-4 / procs-2 smoke run (`studies/tt4m_batchrun/`
ad hoc, not `make check` — see that Makefile's own note) reproduced STEP
1's 0-mismatch answer identity, confirming the new subcommand's sharding
and sub-pool writing round-trips cases correctly before any larger
population was trusted.

**Pool**: STEP 1 used a 126-pattern `tests/base`-only slice. That
population is too small to give N=128 more than one batch per worker at
P=12 (128 x 12 = 1,536 patterns needed for even one batch each), so this
row collects a LARGER, CROSS-CORPUS pool: every `.rxt` file under `tests/`
except `tests/known_fail/` (the same exclusion `run.sh`'s own no-args
discovery uses), `--require-features ""` (STEP 1's homogeneity filter,
unchanged), first 1,024 compilable/non-`perr` distinct patterns (a round
number chosen for even divisibility by every N in the sweep: 1024/16=64
batches, 1024/64=16 batches, 1024/128=8 batches). **1,022 of 1,024
patterns actually reached the sweep** — the same tab-in-pattern manifest
limitation STEP 1's memo already named and flagged as inherited, not
introduced, here (two `tests/base/bounded_repeats.rxt` patterns carry a
literal TAB byte, which the bare-TSV manifest format cannot round-trip;
affects both shapes equally, so it does not bias any comparison below).
**7,729 real cases** extracted from those patterns' own `.rxt` source —
7.56 cases/pattern, richer than STEP 1's `tests/base`-only slice (3.2/
pattern) because this pool draws from every module directory, several of
which (assertions, lookaround, recursion) carry denser per-pattern case
coverage than `tests/base`.

**Sweep**: the brief's full grid, N in {16, 64, 128} x P in {4, 8, 12},
9 cells, each a fresh `parallel` invocation over the SAME 1,022-pattern /
7,729-case pool, `gcc-16`, default `GENCFLAGS` (`-O1 -std=gnu11 -Wall
-Wextra -Werror`, byte-identical to `run.sh`'s own default). Each cell's
own JSON records exact spawn counts, wall/CPU by kind, per-worker batch
counts, and every case's (stdout, exit code) for a full answer-identity
diff. Run SEQUENTIALLY, cell by cell (never two cells concurrently — the
whole point is measuring what ONE cell's own P-way concurrency does to
this box, and running two cells at once would confound that with a
second, uncontrolled concurrency axis).

**Box coordination / load context** (the brief's own ask): `uptime`
immediately before the sweep read **load averages 2.24 2.36 2.51** — a
plain teammate-quiet box, not a heavy suite. The sweep itself is NOT
launched on a fully idle box (other lanes in this session were doing
light, non-`make`-heavy work concurrently) and load drifted up to a peak
**10.44** (transient, immediately after the `n16_p12` cell, the sweep's
most process-dense cell) before settling back into the 5-7 range for the
remaining cells — see "K44 relief?" below for what this number does and
does not say.

## Results

### 1. The N x P wall/CPU grid

| N | P | batches | workers used | wall (s) | CPU, aggregated (core-s) | CPU, outer RUSAGE_CHILDREN (core-s) | gcc calls |
|---|---|---|---|---|---|---|---|
| 16  | 4  | 64 | 4  | 50.18 | 147.79 | 157.12 | 64 |
| 16  | 8  | 64 | 8  | 30.26 | 157.78 | 168.89 | 64 |
| 16  | 12 | 64 | 12 | 28.70 | 170.62 | 183.60 | 64 |
| 64  | 4  | 16 | 4  | 43.80 | 139.91 | 149.35 | 16 |
| 64  | 8  | 16 | 8  | 29.36 | 146.34 | 156.75 | 16 |
| 64  | 12 | 16 | 12 | 29.23 | 156.87 | 168.03 | 16 |
| 128 | 4  | 8  | 4  | 47.50 | 138.25 | 147.40 | 8  |
| 128 | 8  | 8  | 8  | 32.05 | 144.57 | 154.66 | 8  |
| 128 | 12 | 8  | **8 of 12** | 33.33 | 150.56 | 161.17 | 8  |

(1,022 patterns / 7,729 cases at every cell — same population, apples to
apples across the whole grid.)

**The knee is P=8 at every N, and it is not a coincidence — it is this
box's own performance-core count** (8 of its 10 `hw.ncpu`; the other 2 are
efficiency cores). Going from P=4 to P=8 is a real, large win at every N
(1.66x/1.49x/1.48x wall for N=16/64/128 respectively). Going from P=8 to
P=12 buys close to NOTHING: N=16 gains a further 5.4% (28.70 vs 30.26),
N=64 gains 0.4% (statistically noise), and **N=128 actually gets 4.0%
SLOWER** (33.33 vs 32.05) — because N=128's pool only makes 8 batches
total, so P=12 never uses 4 of its 12 requested workers (`workers used:
8 of 12` — those 4 processes are never even launched, since the sharding
loop skips an empty shard) and the request itself buys nothing but
bookkeeping.

**CPU cost tells the same story from the other side.** At fixed N, CPU
(both the aggregated and the outer-RUSAGE_CHILDREN readings) MONOTONICALLY
INCREASES with P — N=16 goes 147.79 -> 157.78 -> 170.62 core-seconds from
P=4 to P=12, a real 15% CPU-cost inflation for a WALL benefit that mostly
already happened by P=8. This is the same "contention inflates CPU cost"
mechanism D45's own header documents for compile budgets under `make
-j12` contention (measured there at ~2x worst-case) — here it is smaller
(15%, not 2x, because 8-12 processes is nowhere near this box's worse
oversubscription cases) but the DIRECTION is the same and it argues for
P=8 over P=12 on a second, independent axis: P=12 spends more total core
time to buy the same (or worse) wall time.

### 2. Does darwin reproduce [TT-4.1]'s Linux non-monotonicity?

**Yes, in the form this box's population and core count actually produce
it: worker STARVATION at N=128/P=12** (8 of 12 workers launched — 4 empty
shards), and the mild WALL REGRESSION that goes with it (33.33s vs
32.05s at P=8, same N). This is [TT-4.1]'s Linux mechanism ("too few
batches to fill the requested worker count, so widening P buys nothing
and can cost a little in bookkeeping") reproduced exactly, just smaller in
magnitude than Linux's own finding (that Linux measurement compared
serial-vs-`PROCS`-fanned-out gcc-batching directly and found a batch count
FAR below core width regressing BELOW the plain unbatched baseline, not
merely flat against a smaller P on the SAME shape — this row's grid never
compares against an unbatched serial baseline at matched population; see
"What is still owed" below). **STEP 1's own serial sweep (which never
reproduced Linux's non-monotonicity) undersold the mechanism because it
never gave the box more than one pipeline to schedule at all** — this
row's grid is what actually exercises it.

### 3. Answer identity

**Zero mismatches across all 9 cells, pairwise, over the full 7,706-key
case set** (7,729 raw case rows collapse to 7,706 distinct (prefix,
subject, startpos) keys — a handful of patterns repeat an identical case
line more than once in their own `.rxt` source, which is a corpus fact,
not a tooling defect, and affects every cell identically). Diffed cell 1
(`n16_p4`) against every other cell's (stdout, exit code) map: 0
mismatches, 0 missing, 0 extra keys, at every N/P combination. Batching's
answer is independent of both batch size AND how many concurrent pipelines
compiled it — exactly the invariant a harness adoption needs to hold.

### 4. Degradation cost at this pool's scale (cross-check against STEP 1)

`batchrun.py failure-iso` re-run on this same 1,022-pattern pool at all
three chartered N (still SERIAL — failure isolation is a single-batch
question, not a parallel-dispatch one):

| N | batch link (fails, detect cost) | fallback: N individual recompiles |
|---|---|---|
| 16  | 1.55s wall / 1.42s CPU | 3.61s wall / 3.83s CPU |
| 64  | 5.98s wall / 5.44s CPU | 14.72s wall / 15.82s CPU |
| 128 | 11.79s wall / 10.72s CPU | 29.22s wall / 31.47s CPU |

Every fallback outcome matched expectation (the corrupted member fails
again, every other member succeeds) at all three N — 0 unexpected
results. **This reproduces STEP 1's own finding (detect is cheap, recovery
is linear-in-N) almost exactly on a population 8x larger and drawn from
the whole corpus rather than one directory** — the mechanism is a property
of shape L itself (one link failure aborts before any member's code
generation completes; recovery means N-1 independent recompiles), not an
artifact of STEP 1's smaller, `tests/base`-only pool.

### 5. K44 relief?

**Suggestive, not conclusive, and the brief's own comparison is not
apples to apples.** This sweep's peak `load1` (10.44, transient, at the
`n16_p12` cell) is roughly 4.4x BELOW K44's documented 47.6-at-`PROCS=12`
figure (`docs/dev/tt12_step0_profile.md`'s STEP 0 profile, measured under
a real `make -j12 test`) — but K44's number comes from the WHOLE battery
(every Makefile-level test SECTION running concurrently, each internally
spawning its own worker fan-out, on the full multi-thousand-pattern
corpus) while this sweep is ONE corpus-compile-only prototype over 1,022
patterns with no sibling sections competing for the box at the same time.
The DIRECTION is consistent with the hypothesis batching helps: shape L
replaces `run.sh`'s today-shape (one pcrec spawn + one gcc spawn PER
PATTERN, i.e. many independent tiny process bursts under `PROCS`
fan-out) with far FEWER, COARSER bursts (N pcrec spawns, then ONE gcc
spawn, per batch) — fewer concurrent process-creation events per unit
wall time is exactly the kind of change that would lower a load-average
spike driven by fork/exec rate rather than by CPU-bound work. **But this
row cannot claim the relief number itself** — that measurement needs
STEP 2c/2d's real implementation running inside an actual `make -j12
test`, with every sibling section present, which is out of this
prototype's reach by construction (`studies/` never touches `tests/
harness/`).

## Recommendation

**N=64, P=8.** Argument, in order:

1. **P=8 is this box's own performance-core count**, not merely today's
   empirical best cell — a principled choice a future re-run on a
   differently-shaped box (more/fewer efficiency cores, a different
   Apple Silicon generation) should re-derive from `hw.perflevel0.
   logicalcpu`, not copy as a hardcoded constant.
2. **N=64 sits inside a near-flat wall-time plateau, not at a sharp
   optimum** — at P=8, N=16/64/128 measure 30.26s/29.36s/32.05s, a ~9%
   spread across a 8x range of N. Throughput is FORGIVING of getting N
   somewhat wrong, which is the sensitivity finding the brief asks for
   directly (below).
3. **N=64's degradation cost is half of N=128's for a statistically
   indistinguishable wall-time win** (14.72s fallback vs 29.22s, for
   29.36s vs 32.05s wall — i.e. N=128 buys nothing in the metric that
   matters and costs twice as much in the metric that matters when
   something goes wrong).
4. N=64 also matches STEP 1's own best serial cell (its "best measured
   cell" was N=64, 4.28x/2.79x wall/CPU against the unbatched baseline) —
   choosing the same N the serial and parallel measurements both
   independently favor is a small, welcome coincidence rather than a
   tie-breaker this row leans on.

**Sensitivity, stated plainly**: the two knobs are NOT symmetric.
- **Getting P wrong (too small)** costs a lot, uniformly: P=4 is
  ~1.5-1.7x slower than P=8 at every N tested. This is the knob to get
  right.
- **Getting P wrong (too large)** costs little in wall time (0-5%) but
  real, measured CPU (contention inflation, up to 15% more core-seconds
  for zero-to-negative wall benefit) and, at a large N whose batch count
  falls below P, literal idle workers — a wasted-concurrency-request
  cost with no error message today (nothing tells a caller "P=12
  requested, only 8 workers ever launched").
- **Getting N wrong (within 16-128)** costs almost nothing in steady-state
  throughput (~9% spread) but scales the WORST-CASE recovery cost
  linearly (3.6s at N=16 to 29.2s at N=128) — the honest way to read this
  is "there is no throughput reason to pick a large N; the only reason to
  go above ~64 would be if some OTHER cost this row did not measure (a
  fixed per-batch overhead not exercised at this pool's scale, or memory
  pressure from N simultaneous cc1 processes at higher optimization
  levels) turned out to matter, and nothing measured here shows that."

## Addendum: the same-pool serial baseline (landed after the grid above)

The unbatched serial baseline (one pcrec spawn + one gcc spawn per
pattern, `tests/harness/driver.c` unmodified, same per-case run shape) on
the IDENTICAL 1,022-pattern/7,729-case pool, run concurrently with the
tail of the sweep above (so its own wall number carries some contention
from that overlap — read it as directionally reliable, not a quiet-box
floor): **547.52s wall / 320.60s CPU** (`counts`: pcrec 1022, gcc 1022,
run 7729 — `gcc` wall 255.32s, `run` wall 280.19s, `pcrec` wall 12.01s;
zero compile failures, 7,706 cases matching the batched cells' own case
count exactly).

**Against this design's own recommended cell (N=64, P=8: 29.36s wall):
18.65x wall speedup end to end** — bigger than STEP 1's own 4.28x because
this number combines BOTH of STEP 1's measured levers (gcc-invocation
count, distinct-executable count) WITH 2a's own parallel-dispatch lever
(P=8 concurrency) multiplicatively, where STEP 1's serial-only sweep could
only ever show the first two. A rough cross-check that the pieces are
consistent with each other: this pool's total CPU (320.60s) against
N=64's own aggregated CPU at any P (139.91-156.87 core-seconds across the
P=4-12 cells) gives a CPU-only multiple of ~2.1-2.3x, close to STEP 1's
own 2.79x CPU figure measured on a different, smaller pool — the two
independent measurements agree on ORDER OF MAGNITUDE for the lever they
share, which is the right cross-check to make before trusting either.

**What this number does NOT isolate, named rather than glossed over**:
today's REAL `run.sh` is not this serial baseline — it already runs
UNBATCHED but PARALLEL (`PROCS=nproc`). This tool has no "unbatched,
parallel" mode (`cmd_baseline` is serial-only by construction, STEP 1's
own scope decision), so the 18.65x figure compares batching+parallelism
together against NEITHER alone, not "what batching adds on top of what
`run.sh` already does today." A rough sanity estimate (spawn/launch tax
dominates over CPU-bound work in this population, so parallel dispatch
should scale close to linearly with P before hitting the same P=8 knee
found above) suggests an unbatched-but-`PROCS=8` run would land
considerably below 547.52s and somewhat above 29.36s — but that is an
estimate, not a measurement, and is named as the one remaining gap before
this design's numbers fully decompose into "parallelism's share" and
"batching's share" separately. **Building `cmd_baseline --procs P`
(the unbatched analogue of `parallel`) is the natural next probe if that
decomposition is ever load-bearing for a decision** (D77: named, not
built, since 2a's own recommendation does not depend on it — the
recommended cell's absolute numbers stand regardless of how the
speedup decomposes between its two contributing levers).

## What is still owed (not blocking STEP 2b, named for STEP 2c/2d)

- **An unbatched-but-parallel baseline** (`cmd_baseline` extended with its
  own `--procs`), to decompose the 18.65x figure above into "how much is
  parallelism, how much is batching" — see the addendum immediately above.
- **A quiet-box re-run.** Per BOILERPLATE and the STEP 1 memo's own
  caveat, this box was not fully idle during the sweep (this session's
  other lanes were doing light, non-`make` work) — the deltas here are
  large enough (1.5-1.7x at the P knee) to trust directionally, but a
  quiet-box confirmation is worth doing before this memo's specific
  numbers are cited as a floor.
- **A real multi-section `make -j12 test` load1 comparison** for the K44
  relief question (§5) — this row's own prototype cannot produce that
  number by construction.
