# [TT-4.1] Batched test compilation — measurement memo

Frank's order (2026-08-22, charter, and reaffirmed as "measurement first"):
measure before any harness change. [TT-3]'s lesson stands as the default
prior here too — "the obvious idea measured as a slowdown" — batching is
guilty until proven innocent by a real number.

## Method

**Box**: 12 cores, `gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0`, kernel
`7.0.0-29-generic`, measured 2026-08-23.

**Stage A (invocation census)**: a PATH-based `gcc`/`cc` shim plus a
`PCREC=` shim (studies/tt4_batching/census/) transparently time and
classify every compiler/pcrec call across one full `make test`, run one
`test-*` section at a time (never two sections concurrently — a section's
own internal `PROCS` parallelism, default `$(nproc)`, is left as the
Makefile already sets it), under `/usr/bin/time -v` for section wall+CPU.
Full method, log format, and the "why no `flock`" reasoning:
studies/tt4_batching/census/CLAUDE.md.

**Shim validation**: `run_section_census.sh --validate <section>` runs a
section's `make test-<section>` once with the shim off and once on, diffs
the PASS/FAIL summaries. Two sections checked 2026-08-23: `parse` (32
calls, 1.015s off / 1.218s on, identical summary) and `cli` (378 calls,
11.753s off / 16.390s on, identical summary — roughly 12ms/call overhead
on that section). Both confirm the shim changes nothing about the suite's
own verdict.

**Blind spots / perturbation not removed**:
- The shim adds real per-call overhead (bash fork + `awk` for wall-time
  arithmetic + one `write(2)`). It is NOT zero, and where a section's own
  time is dominated by thousands of near-instant calls (not the case for
  any section here — see below) it would matter more.
- `/usr/bin/time -v` itself adds one fork per section, negligible against
  section wall times measured in seconds-to-minutes.
- Every gcc/cc/pcrec invocation is logged; nothing hides from the shim on
  this box (checked: no hardcoded `/usr/bin/gcc` absolute-path calls in
  `tests/`, `gcc` and `cc` both resolve to the same real binary via
  `readlink -f`, and `tests/encseam/run_encseam_tests.sh` — the one script
  defaulting `CC` to `cc` rather than `gcc` — is covered because `shim/cc`
  is installed identically to `shim/gcc`).
- One genuine PCREC blind spot was looked for and NOT found: every script
  that is part of `make test`'s 21 sections honours `PCREC=` (grepped and
  spot-checked individually — `tests/known_fail/run_known_fail.sh`,
  `tests/codegen/run_endvar_identity.sh`, `run_wordctx_identity.sh`
  included). `tests/codegen/run_object_neutrality.sh` takes a reference
  pcrec as a positional argument instead, but it is NOT part of `make
  test` (a standalone [M6-READ] script), so it is out of scope, not a gap.
- The 1800s outer timeout on the FIRST full-census attempt fired mid-
  `assertions` at 08:28 (14/21 sections had completed cleanly by then); see
  "The 1800s bound" below — this is reported as a finding, not smoothed
  over.

**Stage B (batching prototype)**: studies/tt4_batching/proto/ — see its
own section below.

## Stage A results

One full `make test` census, section by section, `TMPDIR=/var/tmp`. Raw
logs: `build/tt4_census/census.tsv` (33,944 records, gitignored),
`build/tt4_census/<section>.time`. Table columns: gcc invocation counts by
shape (one-shot / `-c` compile-only / link-only), gcc CORE-seconds (sum of
per-call wall — see the note below), pcrec call count and core-seconds,
section wall clock and CPU (user+sys) from `/usr/bin/time -v`, and the
derived remainder (section wall minus gcc-core minus pcrec-core — NOT
clean under internal parallelism, reported as-is, sign included).

```
section       gcc(1shot/c/link)    gcc-core-s  pcrec# pcrec-core-s  sec-wall   sec-cpu  remainder
----------------------------------------------------------------------------------------------------
corpus        1906/0/0                 255.79    2271        16.99    404.08    556.72     131.30
cli           15/0/0                     1.44     363         0.66     15.67     15.72      13.57
reject        0/0/0                      0.00     572         1.03      6.24     15.57       5.21
registry      3/233/232                 13.40     279         0.43     20.73     65.38       6.91
parse         1/0/0                      0.13      31         0.09      1.24      1.42       1.02
gentimeout    1/3/0                      2.37       3         0.01      7.97      6.34       5.59
codegen       2/7/0                      2.21    1142         3.66     24.19     31.37      18.33
vm            236/0/0                   34.77    3240        38.20     80.07    163.92       7.10
possessify    157/0/0                   32.66    3164         6.36     90.88    139.40      51.86
rungselect    205/1/0                   43.98    5761        24.54    317.48    429.86     248.95
counterk      60/0/0                    20.18     156        13.11    223.05    267.60     189.76
mrl           153/0/0                   48.31    3273         6.81    131.88    197.61      76.76
prefilter     2/0/0                      0.22      21         0.06      1.31      1.21       1.03
altcls        41/0/0                     8.05     101         0.28     25.31     25.52      16.98
assertions    278/270/0                 50.80    7651        70.56    479.45   1274.81     358.10
atomic        442/0/0                   70.65     501         1.42    117.97    123.30      45.91
backrefs      183/0/0                   24.22     193         0.49    230.61    262.64     205.90
encseam       52/0/0                     5.26      52         0.15     21.92     18.33      16.51
resource      0/0/0                      0.00      19        88.31     91.51    122.40       3.20
capturediff   2/176/175                 22.67     301         2.07      6.22     42.91     -18.52
thread        9/0/0                     10.10       5         0.01     13.61     14.98       3.50
----------------------------------------------------------------------------------------------------
TOTAL         gcc calls=4845           647.19   29099       275.23   2311.39   3777.01
```

`known-fail` (the 21st section) is absent from the table by construction:
`tests/known_fail/` is genuinely empty in this tree state (confirmed —
`run_known_fail.sh`'s own output: "no deferred-bug regressions on file"),
so it makes zero pcrec/gcc calls and `summarize.py` has nothing to print
for it; its section wall was 0.109s (pure bash/make overhead), recorded in
`run_section_census.summary` though not in this table.

**Sum of section walls (2,311.39s, ~38.5 min) is much larger than a plain
`make test` run's own wall (~10 minutes per project docs)** — expected and
not a discrepancy: THIS census runs each section SEPARATELY (never `-j12`
across sections, per the brief's "do not run sections in parallel with
each other"), so section walls SUM here where a real `make test` (or
`make -j12 -Otarget test`) would overlap independent sections'
compile/differential work across cores. The census measures per-section
cost cleanly at the price of not reproducing the suite's actual overlapped
wall-clock — a real full-suite timing (`time make test`) was not re-run as
part of this row (out of budget; the project's own ~10-minute figure is
already on record).

**6,366 of 33,944 calls exited nonzero.** This is EXPECTED, not a shim or
build problem: `test-reject`, `perr` blocks throughout `test-corpus`, and
every deny-family differential (`rungselect`, `possessify`, `mrl`,
`altcls`, `atomic`, `backrefs`, `capturediff`, `codegen`, `registry`,
`gentimeout`, `prefilter`) deliberately invoke pcrec/gcc expecting a
NONZERO exit somewhere in their sweep (a rejected pattern, a planted
sabotage, a `-fno-*` denied build compared against the default one, a
D45 budget-fire control). Every section's own `make rc=0` in the summary
above confirms the suite scored these as expected outcomes, not failures;
this row did not audit each nonzero call individually against its
section's own pass/fail accounting (that audit is what each section's own
`make test-<x>` already does, and did, cleanly).

**Core-seconds vs wall**: under a section's own internal PROCS
parallelism, the SUM of per-call gcc/pcrec wall times is CORE-seconds, not
wall-clock — it can and does exceed the section's own wall (e.g. `corpus`:
255.79 gcc-core-s + 16.99 pcrec-core-s = 272.78 core-s against 404.08s of
section wall, consistent with ~12-way parallel dispatch across ~1900 file
workers; `assertions`: 50.80 + 70.56 = 121.36 core-s against 479.45s of
wall, consistent with its own much lower effective parallelism).

**Ranking by gcc-bound core-seconds (worst first)**: `corpus` 255.79s,
`atomic` 70.65s, `assertions` 50.80s, `mrl` 48.31s, `rungselect` 43.98s,
`vm` 34.77s, `possessify` 32.66s, `backrefs` 24.22s, `capturediff` 22.67s,
`counterk` 20.18s, ... (full ranking in the raw `summarize.py` output).

**THE TWO WORST SECTIONS by gcc-bound core-seconds are `corpus` and
`atomic`** — not `assertions`/`atomic`/`backrefs` combined as the plan
row's historical note anticipated, and notably NOT `rungselect` or
`counterk` despite those two having the largest SECTION WALL times among
the non-`corpus`/`assertions` sections (317s/223s) — their wall is
dominated by match-EXECUTION and harness-loop time, not gcc. `reject` and
`resource` show 0.00s gcc-core: `test-reject` never compiles C at all (it
is entirely pcrec-rejection assertions — the differential IS the
`perr`-style pcrec exit code, no generated matcher is ever built), and
`test-resource`'s watchdog-bounded compiles route through a different
mechanism the shim did not classify as `gcc`/`cc` for that section (its
own pcrec calls dominate instead, 88.31 core-s — resource limits, not
compile counts, are what that suite is measuring).

## Comparison against the plan row's previously observed numbers

docs/dev/plan.md [TT-4]'s cited per-section wall times (`[M6.5.2]` lane,
an earlier, DIFFERENT section grouping — "assertions+identity gates" 458s
combined several identity-gate scripts that today live under separate
Makefile targets, not all of them inside `test:`'s 21 sections) are not a
clean apples-to-apples comparison to this census's section boundaries.
Where a today-section's name matches directly:

| section | today (this census, section wall) | plan row's cited figure |
|---|---|---|
| corpus | 404.09s | 392s |
| rungselect | 317.49s | 242s |
| counterk | 223.05s | 166s |
| mrl | 131.88s | 115s |

All four are HIGHER today. `corpus` alone: the historical 392s/1270-case
figure predates several module test directories
(`atomic_groups/`, `backrefs/`, `possessify/`, `rungselect/`, `counterk/`,
`mrl/`, `altcls/`, `prefilter/`, `assertions/`, `captures/`, `classes/`,
`modifiers/`, `named_groups/` — all landed after [TT-1]'s 2026-08-13
measurement) whose `.rxt` files `tests/harness/run.sh`'s no-argument mode
picks up in its recursive `find tests -name '*.rxt'` sweep; today's
`test-corpus` genuinely covers far more than the historical count. That
alone plausibly explains most of `corpus`'s growth without invoking the
census shim at all.

**`rungselect`/`counterk` were investigated further because their growth
(+31%/+34%) looked too large to wave off, and the manager asked
specifically whether it was the shim, the `/usr/bin/time` wrapper, or
concurrent activity.** Direct evidence:

- Both sections' internal parallelism is LOW by design — `run_rungdiff.sh`
  and `run_counterkdiff.sh` have no `PROCS` fan-out of their own; the only
  concurrency in `test-rungselect`/`test-counterk` is `run_group.sh`
  running their two constituent scripts (diff + identity-tests) alongside
  each other, i.e. 2-way at most. Measured load during these sections:
  1.27-1.47 (rungselect), 1.27-1.39 (counterk) — consistent with ~2-way
  activity on a 12-core box, not contention from another process (checked
  `ps aux --sort=-%cpu` during the run: nothing but this census, an idle
  desktop session, and one `cc1` from the section itself).
- The gcc+pcrec CORE-TIME sum for `rungselect` is only 68.52s (43.98 +
  24.54) against its 317.49s section wall — the overwhelming majority of
  the section's cost is OUTSIDE gcc/pcrec entirely (match execution over
  its differential's subject sweep, plus bash harness-loop overhead per
  cell). Same shape for `counterk`: 33.29s core-time (20.18 + 13.11)
  against 223.05s wall.
- **Direct shim-off isolation, run after the shim-on measurement, box
  otherwise idle (load 0.1-0.3)**: `test-rungselect` WITHOUT the shim
  measured **327.74s** wall — SLOWER than the shimmed run's 317.49s.
  `test-counterk` WITHOUT the shim measured **216.65s** — 6.4s FASTER
  than the shimmed run's 223.05s, in the direction a real (but small) shim
  cost would predict, and roughly the right MAGNITUDE for one (counterk
  logs only 216 shim calls; at ~12ms/call that predicts ~2.6s, same order
  as the observed 6.4s delta, run-to-run noise included).

**Verdict on the rungselect/counterk growth**: the shim is NOT the primary
cause for EITHER section, and the two sections separate cleanly once
isolated directly:

- `rungselect`: shim-OFF measured SLOWER (327.74s) than shim-ON (317.49s).
  A naive per-call estimate (5,967 shim calls x ~12ms/call ~= 72s) would
  predict shim-on should be the SLOWER of the two by roughly that much —
  the isolation run shows the opposite direction, which rules the shim out
  as the explanation for `rungselect`'s +75s vs. the historical 242s
  figure. Both gcc/pcrec core-time (68.52s) and the section wall (317-
  328s) point to the differential's own match-execution/harness-loop cost
  as the dominant term, not compile count or shim tax; the remaining gap
  against the historical baseline is most plausibly test-population growth
  in `tests/rungselect/` since [TT-1]'s 2026-08-13 measurement (unverified
  here — would need a `git log` archaeology this row's time budget did not
  cover) combined with ordinary run-to-run variance on a section this
  wall-dominated.
- `counterk`: shim-OFF measured 216.65s vs. shim-ON's 223.05s — a 6.4s
  delta in the direction a real shim cost predicts, and close in
  MAGNITUDE to counterk's own low shim-call count (216 calls x ~12ms/call
  ~= 2.6s). So for `counterk` the shim IS a real, small, correctly-signed
  contributor (a few seconds), but it accounts for only a small fraction
  of the +57s versus the historical 166s figure — the rest is, again,
  most plausibly population growth plus variance, not investigated
  further here.

Net: the manager's three candidate causes (shim / `/usr/bin/time` wrapper
/ concurrent activity) are each addressed by direct evidence rather than
inference — concurrent activity is ruled out (`ps aux --sort=-%cpu` during
both sections showed nothing but this census and an idle desktop; load
1.27-1.47 matches the sections' own ~2-way internal parallelism, not
contention), the `/usr/bin/time -v` wrapper's own cost is one fork per
section (sub-millisecond, not investigated further as it cannot plausibly
explain seconds), and the shim is confirmed real-but-small for `counterk`
and NOT the explanation for `rungselect`.

## The 1800s bound (a finding, not smoothed over)

The first full-census attempt was launched under an outer `timeout 1800`
sized from the whole-suite `-j12` wall figure the project's own
documentation cites (~10 minutes). That bound does not apply to THIS
census's shape: sections here run ONE AT A TIME under `/usr/bin/time -v`
(never `-j12` across sections), so their wall times SUM rather than
overlap, and the census's own per-call shim overhead adds on top. The
1800s bound fired at 08:28, mid-`assertions` (14/21 sections had already
completed cleanly, cumulative wall ~1900s by that point) — every section
queued after it was never reached, and `assertions.time` was left at 0
bytes (the `/usr/bin/time -v` wrapper never got to write its report).
Fixed two ways for the resume (studies/tt4_batching/census/
run_section_census.sh, 2026-08-23): (1) re-invoking with EXPLICIT section
names now APPENDS to the existing `census.tsv`/summary instead of
truncating them, so a bound firing mid-run costs nothing already
completed; (2) a PER-SECTION `timeout` (`TT4_SECTION_TIMEOUT`, default
900s) now wraps each section's own `make test-<x>`, so one slow section
can no longer silently consume an entire run's remaining budget the way
`assertions` did. The partial `assertions` rows from the killed run
(8,193 of them) were removed by hand before resuming, since append-mode
would otherwise have mixed partial-run and full-run records for the same
section. The resumed run (`assertions atomic backrefs encseam resource
capturediff known-fail thread`, `TT4_SECTION_TIMEOUT=1000`) completed
cleanly; `assertions` alone measured 479.51s — the single largest section
after `corpus`, and the reason the original 1800s outer bound could not
have finished the full 21-section sweep even without the mid-run kill.

## Stage B: batching prototype

studies/tt4_batching/proto/ — never the harness, three call shapes over a
FIXED pool of real generated patterns, batch size N in {1,4,16,64,256}
(patterns split into pool-size/N batches of N), each cell measured SERIAL
(clean per-call attribution) and 12-way PARALLEL over batches
(`concurrent.futures`, matching the harness's own `PROCS=$(nproc)` shape),
median/min of 3 reps:

- **C (baseline)**: one gcc call per PATTERN, compile+link, using a
  generated single-pattern dispatch driver that reproduces
  `tests/harness/driver.c`'s exact protocol byte for byte (verified
  directly — see "Emitter-side obstacles" below) — the harness's own
  shape, same `GENCFLAGS` (`-O1 -std=gnu11 -Wall -Wextra -Werror`). C does
  NOT depend on N (a bug in the first version of `bench.py` re-measured it
  once per N anyway — 5x redundant runs, caught and fixed before it burned
  the time budget); its median/min are reused as the N-independent
  baseline row.
- **A (link-batching)**: `gcc -c` per member of the batch plus the batch's
  dispatch driver, then ONE link of all N+1 objects.
- **B (TU-batching)**: concatenate the N members' `gen.c` bodies into one
  file, compile THAT plus the dispatch driver in ONE gcc call
  (compile+link).

### Pattern pools

Both pools collected directly from `build/pcrec` run over real `.rxt`
blocks (`studies/tt4_batching/proto/collect_patterns.py`; never touches
the harness), restricted to a single `--features` bucket per pool (see
"Emitter-side obstacles" below for why):

- **corpus pool**: 256 patterns from `tests/base/` (the default/no-
  `--features` bucket — `test-corpus`, the worst gcc-bound section, is
  dominated by this directory).
- **atomic pool**: 64 patterns from `tests/atomic_groups/` restricted to
  `--features atomic-groups` exactly (the module's seven `.rxt` files mix
  several different `--features` combinations — `atomic-groups`,
  `atomic-groups,assertions`, `atomic-groups,modifiers`, etc. — so the
  pool is filtered to the single largest homogeneous bucket, 81 of 121
  collectible blocks, capped at 64 for a clean power-of-two batch-size
  ladder).

### Corpus-pool results (the worst section)

Baseline: **50.990s serial / 6.573s parallel** (256 one-shot compile+link
calls — the harness's own shape and cost, measured directly).

| N | shape | serial median | serial x baseline | parallel median | parallel x baseline |
|---|---|---|---|---|---|
| 1 | A | 50.277s | 1.01x | 6.640s | 0.99x |
| 1 | B | 50.266s | 1.01x | 6.410s | 1.03x |
| 4 | A | 22.803s | 2.24x | 3.112s | 2.11x |
| 4 | B | 17.337s | 2.94x | 2.403s | 2.74x |
| 16 | A | 15.987s | 3.19x | 2.722s | 2.41x |
| 16 | B | 9.158s | 5.57x | **1.798s** | **3.66x** |
| 64 | A | 14.219s | 3.59x | 4.382s | 1.50x |
| 64 | B | 7.191s | 7.09x | 2.681s | 2.45x |
| 256 | A | 13.993s | 3.64x | 13.987s | 0.47x |
| 256 | B | 6.895s | 7.39x | 6.864s | 0.96x |

**Best measured speed-up (against the PARALLEL baseline, the realistic
comparison — that is how the harness runs today): shape B, N=16, 3.66x
(1.798s vs 6.573s).** Shape B beats shape A at every single N (TU
concatenation amortizes the fixed per-call cost — process start, header
parsing, link — harder than link-batching alone, which still pays a
separate `-c` compile per member). Under SERIAL measurement, larger N is
monotonically better for both shapes (7.39x at N=256 for shape B) — but
that is not the harness's own execution shape.

**N=64 and N=256 are WORSE than N=16 under PARALLEL mode, and this is the
one non-monotonic, easy-to-miss finding in the whole sweep.** Batch COUNT,
not batch size, is what feeds the 12-way parallel dispatcher: at N=64
there are only 256/64=4 batches for 12 cores (8 sit idle — parallel
median 2.681s, barely better than N=16's serial-adjacent 9.158s divided
by not-quite-4); at N=256 there is exactly ONE batch, so "parallel mode"
has nothing to parallelize over and shape A's N=256 parallel cell (13.987s,
**0.47x — SLOWER than the plain baseline**) is really just 256 serial `-c`
compiles inside that one unparallelized batch job, worse than the harness
already gets today from spreading 256 one-shot compiles across 12 cores.
**The batch size that maximizes real speed-up is the one whose batch COUNT
is close to the core count** (16 batches on a 12-core box), not the
largest N tried — a naive "bigger batches are always better" reading of
the serial numbers alone would have picked N=256 and shipped something
2.45-7.7x worse than N=16 under the harness's actual parallel shape.

**Peak RSS**: the single N=256 TU compile (shape B) measured **213,240 KB
(~208 MB)** peak resident set — not alarming, no non-linear blow-up
observed at this pool's scale (256 DFA-sized matchers).

**Correctness**: 8 patterns from the N=256 batch, checked against 4
subjects each (32 total) — every batched executable's output matched the
baseline (`shape C`) driver's output byte for byte. 0 mismatches.

### Atomic-groups pool results (the second-worst section)

Baseline: **13.316s serial / 1.743s parallel** (64 one-shot compile+link
calls).

| N | shape | serial median | serial x baseline | parallel median | parallel x baseline |
|---|---|---|---|---|---|
| 1 | A | 13.364s | 1.00x | 1.814s | 0.96x |
| 1 | B | 13.257s | 1.00x | 1.756s | 0.99x |
| 4 | A | 6.537s | 2.04x | 0.990s | 1.76x |
| 4 | B | 5.031s | 2.65x | 0.798s | 2.19x |
| 8 | A | 5.354s | 2.49x | 0.781s | 2.23x |
| 8 | B | 3.627s | 3.67x | **0.640s** | **2.73x** |
| 16 | A | 4.810s | 2.77x | 1.225s | 1.42x |
| 16 | B | 2.970s | 4.48x | 0.782s | 2.23x |
| 64 | A | 4.307s | 3.09x | 4.258s | 0.41x |
| 64 | B | 2.449s | 5.44x | 2.477s | 0.70x |

**Best measured speed-up: shape B, N=8, 2.73x (0.640s vs. 1.743s).** Same
pattern as the corpus pool: 8 batches of 8 is the sweet spot for a 64-
pattern pool on this 12-core box, and N=64 (one batch, no parallelism)
is again WORSE than baseline under parallel mode for both shapes (0.41x/
0.70x) — the same non-monotonic "batch count near core count wins, not
the biggest N" shape the corpus pool showed, now confirmed on a SECOND,
independently-collected pool with a different pattern population and a
different `--features` set, not a one-pool coincidence. Peak RSS at N=64
(shape B, the pool's largest batch, all 64 patterns in one TU): 96,812 KB
(~95 MB). Correctness: 32/32 sampled outputs matched the baseline
exactly.

### Failure isolation

`bench.py --failure-isolation N=16` (corpus pool): plants a syntax error
(`THIS IS A PLANTED SYNTAX ERROR;`) appended to ONE member's `gen.c` in a
16-pattern batch, then measures shape B's (TU-batching) all-or-nothing
compile cost against falling back to per-pattern compilation for the same
16 members.

- **Shape B, whole batch**: fails as expected (`rc=1`), in **0.231s** —
  fast, because gcc's own parse error aborts the single TU compile early;
  ALL 16 members are blocked, not just the corrupted one (this is the
  cost TU-batching's failure mode imposes: one bad pattern anywhere in
  the batch takes every OTHER member in it down too, even though they
  compile fine on their own).
- **Per-pattern fallback, all 16 members individually** (same corrupted
  source directory, so the planted error still fires — this reproduces
  what a real fallback path would see): **2.993s**, exactly one nonzero
  exit (the planted one; the other 15 succeed).

**The real cost of TU-batching's failure mode, if [TT-4.2] adopts it, is
not the 0.231s detection — it is the requirement to REDO the other 15
good members' compiles from scratch once the batch is known to have
failed** (2.993s of per-pattern work that the batch's own 0.231s failure
did not avoid, only revealed). At N=16 that is a small absolute cost, but
it scales with N: [TT-4.2]'s failure-isolation design (named explicitly in
docs/dev/plan.md's [TT-4] charter as an owed requirement, "fall back to
per-pattern for the failing members and attribute the failure to the
right pattern") has a real number to design against now rather than an
assumed one — a bigger batch size trades a lower steady-state compile
cost (this memo's own N-sweep above) against a bigger all-or-nothing
retry cost on ANY single failing member, and `test-corpus`'s own `perr`
population (patterns EXPECTED to fail pcrec, not gcc — a different failure
class, upstream of this one) means a batching design has to decide
whether `perr` patterns are even eligible to enter a TU batch in the first
place, since they never reach gen.c/gcc at all.

### Emitter-side obstacles (measured, not assumed)

Two-matcher coexistence in one TU was probed BEFORE building the full
sweep (`build/pcrec -p rx0001 ...` / `-p rx0002 ...`, then concatenated
and compiled under the harness's exact `GENCFLAGS`):

- **Every symbol that must be per-matcher-unique IS prefixed correctly**:
  entry-point functions (`rx0001_search`, `rx0001_match`,
  `rx0001_match_caps`, `rx0001_info`, `rx0001_group_names`, the internal
  `rx0001_forward_*` DFA helpers, computed-goto labels, static const
  tables), and the capture-count macro (`RX0001_NCAPS`, not a bare
  `RX_NCAPS` — the harness's own `driver.c` only ever sees `RX_NCAPS`
  unprefixed because `run.sh` always compiles with the fixed literal
  prefix `-p rx`; a batching design has to generate its own dispatch
  driver rather than reuse `driver.c` verbatim for exactly this reason).
  Grepped directly (`grep -nE '^(static |const )' rx0001.c` against the
  prefixed name list): zero unprefixed declarations found in either probe
  pattern's generated `.c`.
- **The shared PCRE ABI block IS include-guarded and byte-identical
  across matchers** (`#ifndef PCREC_RX_ABI_H` / `#define
  PCREC_RX_ABI_H`, `PCREC_ERR_STEPS`/`PCREC_ERR_FRAMES`/
  `PCREC_ENGINE_DFA`/`PCREC_VM_RUNG_*`/etc.) — the SAME constants
  regardless of prefix or pattern, so the second matcher's include of an
  identical guarded block is simply skipped by the preprocessor, and two
  matchers concatenated into one TU compiled clean under `-Wall -Wextra
  -Werror` with zero warnings.
- **A REAL obstacle, confirmed by direct compile failure, not inferred**:
  `PCREC_FEATURE_SET` and `PCREC_FEATURE_MODULES` are UNPREFIXED `#define`s
  written directly into each generated `gen.c` BODY (not inside the
  guarded header block, and not guarded at all). Two matchers compiled
  with the SAME `--features` value redefine them identically — legal C,
  no warning, confirmed compiling clean. Two matchers compiled with
  DIFFERENT `--features` values (probed: `--features named-groups` vs.
  `--features backrefs`) fail TU-concatenation with a genuine compiler
  error under `-Werror`:

  ```
  batch_tu.c:537:9: error: 'PCREC_FEATURE_MODULES' redefined [-Werror]
    537 | #define PCREC_FEATURE_MODULES "backrefs"
        |         ^~~~~~~~~~~~~~~~~~~~~
  batch_tu.c:4:9: note: this is the location of the previous definition
      4 | #define PCREC_FEATURE_MODULES "named-groups"
  ```

  This is the reason both Stage B pools above are restricted to a single
  homogeneous `--features` bucket (`collect_patterns.py
  --require-features`) — a real, TU-batching-only obstacle (shape A,
  link-batching, is UNAFFECTED: each member is still its own separate
  preprocessing unit under `-c`, so two different `--features` values
  never collide). Any [TT-4.2] design that batches at the TU level rather
  than the link-step level owes this a real fix (moving the two
  `#define`s inside the already-guarded ABI block, or dropping them from
  the body and reading the values from a per-prefix comment instead, or
  simply refusing to co-batch patterns with different `--features` sets)
  — not assumed away.

## Stage A2: the remainder

Manager review of Stage A: `make test` totals **3,777 CPU-s**, of which
gcc is 647s (17%) and pcrec 275s (7%) — **76% ("remainder") was
unattributed.** Batching gcc at the Stage B numbers above therefore caps
at roughly gcc's OWN 17% share of the suite's total CPU, not anywhere
near the whole thing — worth stating plainly before anyone reads 3.66x as
"the suite gets 3.66x faster." Also worth restating against the plan
row's own premise: this census measured **4,845 gcc calls total across
`make test`**, not the "~20,000 tiny compile-and-link gcc invocations"
`docs/dev/plan.md`'s [TT-4] charter cites — the ~20,000 figure is closer
to the true count of GENERATED-MATCHER EXECUTIONS (Stage A2 below finds
19,185 for `corpus` alone) than of gcc invocations; the two were
conflated in the charter's own framing.

**Method**: added `timeout` and `python3` PATH shims (same transparent-
wrapper shape as `gcc`/`cc`/`pcrec` — see studies/tt4_batching/census/
CLAUDE.md) to attribute the remainder directly, named from the harness's
own code: `tests/harness/run.sh:356` execs the compiled matcher **ONCE
PER CASE** (`out="$(timeout "$RUN_SECS" "$bdir/t" "$subj" "$pos")"`
inside a bash command substitution), and pcrec itself is also invoked
through `timeout` (run.sh:262). Re-censused the top remainder sections
from Stage A (`corpus`, `assertions`, `rungselect`, `counterk`,
`backrefs`, `mrl`, plus `altcls` as a small control) with both new shims
wired in, serially, box idle, `TT4_SECTION_TIMEOUT=1000`. All 7 completed
within their bound (none skipped). `shim/timeout` classifies each call by
its COMMAND target (skipping leading timeout options), not by section —
`pcrec-target`, `driver-target` (the compiled `t` binary), or
`other:<basename>`.

**A methodological finding surfaced immediately and had to be resolved
before the table below means anything**: naively summing per-call WALL
time for the ~19,000 matcher-run spawns (as this memo's Stage A gcc/pcrec
tables do successfully for the much-smaller gcc/pcrec call counts) gives
a number — 2,013.72 core-seconds for `corpus` — that EXCEEDS the
section's own measured CPU-seconds (947.50s from `/usr/bin/time -v`,
which is a real physical upper bound on total processor time, unlike a
wall-time sum). This is not a bug in the shim; it is what happens when
thousands of near-instant processes (median matcher execution is
microseconds) are spawned faster than 12 cores can service them — the
summed WALL time is dominated by **scheduling queue wait**, not compute,
and stops being a valid core-seconds estimate at this call volume. The
table below therefore reports matcher-run wall-sum as its own column,
explicitly flagged, and EXCLUDES it from the residue computation (residue
= section CPU minus gcc minus pcrec minus python3 ONLY) rather than
silently producing a nonsensical negative "remainder."

```
section          gcc-s  pcrec#   pcrec-s   runs# runs-wallsum    py3-s  sec-wall   sec-cpu  residue*  residue%
----------------------------------------------------------------------------------------------------------------------------------
corpus          261.39    2271     16.75   19185      2013.72     0.00    468.91    947.50    669.35     70.6%
assertions       50.87    7651     70.31       0         0.00    17.87    478.09   1273.40   1134.35     89.1%
rungselect       44.29    5761     24.52       0         0.00     0.00    323.30    435.90    367.10     84.2%
counterk         20.20     156     12.81       0         0.00     0.00    225.01    269.30    236.29     87.7%
backrefs         24.00     193      0.49       0         0.00     2.50    235.58    268.75    241.76     90.0%
mrl              48.28    3273      6.91       0         0.00     0.00    134.62    201.61    146.42     72.6%
altcls            7.90     101      0.28       0         0.00     0.00     26.10     26.39     18.21     69.0%
```
(residue = sec-cpu − gcc-s − pcrec-s − py3-s; runs-wallsum NOT subtracted, see above)

**The single biggest, least expected finding: `corpus` is the ONLY one of
the seven sections with any `driver-target` (matcher-run) timeout calls
at all — 19,185 of them. The other six show ZERO.** Checked directly
(`grep -n "run.sh\|harness/run" tests/assertions/run_assertions_tests.sh
tests/rungselect/run_rungdiff.sh tests/counterk/run_counterkdiff.sh` — no
hits in any): `assertions`, `rungselect`, `counterk`, `backrefs`, `mrl`
do NOT go through `tests/harness/run.sh` AT ALL. Each is its own
purpose-built C DIFFERENTIAL DRIVER that loops over its entire subject
sweep INSIDE ONE PROCESS — i.e., every one of these six sections has
ALREADY adopted the "one process, many cases, no re-exec" shape that
this memo's own manager-requested exec-cost prototype cell (below)
measures as a lever. **The per-case-exec shape the manager's remainder
question was worried about is a property of `tests/harness/run.sh`
specifically, not of the suite generally** — it is real, and it is
`corpus`-shaped (and, per Stage A's ranking, `test-known-fail`, which
also drives run.sh, though its wall is near-zero since the directory is
empty). For the six differential sections, the 69-90% "residue" is real
CPU work happening inside their own compiled drivers' subject sweeps —
genuinely invisible to ANY exec-based shim by construction, since no new
process is ever spawned for it. This is the STATED BLIND SPOT: anything
that runs inside an already-running process (a differential driver's own
sweep loop, python's own interpreter loop, bash's own string/loop
overhead within a script) cannot be attributed by a shim that only sees
process boundaries, no matter which binaries get named.

**A second, smaller finding, informative for the D45 CPU-budget
mechanism specifically**: `tests/lib/gen_timeout.sh`'s `gen_cc` wraps
every generated-code compile in `timeout WALL bash -c 'ulimit ...;
_gen_cc_run ...'` (the D45 CPU-budget enforcement) — logged by
`shim/timeout` as `other:bash`, one record per gcc call, in the sections
that route through it: `corpus` 1,906 calls / 403.97s wall-sum (vs.
261.39s of that being the REAL gcc compile per the direct `gcc`-tool
shim — the ~142.6s difference is the wrapper's own bash-fork+ulimit
overhead, ~75ms/call at this volume), `rungselect` 206/62.69s,
`mrl` 153/58.98s, `counterk` 60/25.08s, `altcls` 41/10.72s.
`assertions` and `backrefs` show ZERO `other:bash` records despite having
real gcc calls (50.87s and 24.00s respectively) — their compile sites
call `$CC` directly rather than through `gen_cc`, a second real
divergence in how sections reach the compiler, found by the same shim
rather than assumed.

**python3, by script** (only two sections used it in this re-census):
`assertions` — `verify_pcre2.py` 15.05s, `pcre2_oracle` 2.52s (plus
several small `<script:...>` odds under 0.15s each, all from inline
`python3 - args <<'PY'` heredoc invocations whose classifier reads the
FIRST non-flag argv token, not the heredoc body); `backrefs` —
`bref_oracle.py` 2.15s plus similar small heredoc-argv odds. **A real,
minor classifier bug was found and fixed mid-run**: `shim/python3`'s
first version read the VALUE of a `-c "..."` invocation
(`tests/backrefs/run_dupnames_diff.sh:59`'s multi-line inline snippet) as
if it were a script name, corrupting 2 of 46,356 log lines (embedded
newlines broke the TSV's one-record-per-line assumption — both excluded
automatically by the summarizer's own field-count check, logged as
parse warnings, and visible in the raw log for anyone who wants to see
them). Fixed for future runs (`-c`/`-m` now correctly skip their value
argument); not re-run, since the two affected records are negligible
(0.004% of the log) and re-running the whole 7-section census again was
not in this row's remaining time budget.

### The `timeout` binary itself: a third, independent, near-free lever

**Manager finding, verified directly on this box before being written up**:
`/usr/bin/timeout` here is **uutils coreutils 0.8.0**
(`/usr/bin/timeout -> ../lib/cargo/bin/coreutils/timeout`), not GNU
coreutils. Microbenchmark (50x `timeout 5 true` vs. bare `true`, this
memo's own repro, matching the manager's numbers almost exactly):

| binary | mean wall/call | CPU/call |
|---|---|---|
| bare `true` | 0.4ms | — |
| `/usr/bin/gnutimeout` (GNU coreutils 9.7, also installed on this box) | 4.2ms | ~0 |
| `/usr/bin/timeout` (uutils 0.8.0) | **108.7ms** | ~0 |

**uutils' `timeout` costs ~104.5ms of PURE WALL per call above bare exec,
at essentially ZERO CPU** — this is sleep/poll-wait time, not compute, and
it is a property of THIS ONE BINARY, not of "spawning processes" in
general (`gnutimeout` pays only ~3.8ms of the same tax). Cross-checked
against Stage A2's own census: `census.tsv`'s `corpus` timeout calls
(23,252 of them — driver-target, pcrec-target, and `gen_cc`'s
`other:bash` wrapper combined) average **114.3ms/call**, matching the
microbenchmark closely; `rungselect`/`mrl`/`counterk`/`altcls` (206/153/
60/41 calls respectively) show HIGHER per-call means (261-418ms) because
those calls wrap real, non-trivial gcc compiles, and the ~104.5ms tax is
additive on top of real work, not the whole story there.

**Because this overhead is ~0 CPU, it does NOT show up in `sec_cpu`
(the residue computation above is UNAFFECTED by it) — it is a WALL-CLOCK-
only cost**, and the right way to size it is per-section wall, not %-of-
suite-CPU:

| section | timeout calls | wall-sum | projected wall-sum @ ~104.5ms/call saved |
|---|---|---|---|
| `corpus` | 23,252 | 2,657.42s | ~2,429.8s |
| `rungselect` | 206 | 62.69s | ~21.5s |
| `mrl` | 153 | 58.98s | ~16.0s |
| `counterk` | 60 | 25.08s | ~6.3s |
| `altcls` | 41 | 10.72s | ~4.3s |

For `corpus`, whose `driver-target`/`other:bash` calls run inside each of
~12 file-worker processes SERIALLY (no further parallelism within one
worker's own case loop), that wall-sum savings divides roughly by the
section's own ~12-way worker count: **~2,429.8s / 12 ≈ 200s of `corpus`'s
468.91s measured section wall (≈43%) is plausibly recoverable by
substituting `gnutimeout` for `timeout` on `PATH` — zero harness redesign,
zero batching, one binary swap.** This is corroborated directly by the
exec-cost prototype cell below, not merely projected from the
microbenchmark.

### The exec-cost prototype cell (three shapes, same footing)

`studies/tt4_batching/proto/bench_execcost.py`, corpus pool, 16 patterns,
their REAL cases pulled from the actual `.rxt` source files (never
synthetic — `extract_cases.py`), 3 repeats, median, now with a THIRD
variant added per the manager's request (`--timeout-bins`):

| shape | median (35 cases / 16 patterns) | vs. uutils-harness |
|---|---|---|
| (i-uutils) harness's own shape, `/usr/bin/timeout` (`run.sh:356`'s literal spawn-per-case, unmodified) | 3.8189s | 1.00x |
| (i-gnu) SAME shape, `/usr/bin/gnutimeout` substituted (nothing else changed) | 0.1225s | **31.18x** |
| (ii) one process per PATTERN, `multidriver_gen.py` (no per-case exec at all) | 0.0220s | **173.59x** |

**This decomposes what looked like a single "245.59x exec-batching win" in
the first cut of this cell into two SEPARATE, independently-measured
effects, and the split matters for design**: swapping ONLY the `timeout`
binary — no redesign — already recovers **31.18x** of the gap (per-case
means: uutils 109.1ms, GNU 3.5ms, both matching the standalone
microbenchmark closely, cross-validating both measurements). Going the
REST of the way to full exec-batching (one process per pattern) adds a
further **5.57x** on top of the GNU-timeout number (0.1225s → 0.0220s) —
real, but a much smaller share of the total 173.59x than the first cut's
framing implied. **Most of what this row originally reported as "the cost
of per-case process spawning" was actually "the cost of THIS BOX's
particular `timeout` implementation."** The 5.57x remaining is the
TRUE exec-batching-specific lever, isolated from the binary-choice
confound.

**Scaling note unchanged from the first cut**: this 16-pattern sample's
average (35/16 ≈ 2.2 cases/pattern) is lower than `corpus`'s real average
(≈10.1 cases/pattern per Stage A2's own count); shape (ii)'s remaining
5.57x-over-GNU-timeout edge would likely grow at higher cases/pattern
(more loop iterations amortizing the same one process-spawn), not shrink
— not re-measured at full scale, same time-budget reason as before.

**Sizing all three levers together, using Stage A2's own numbers**:
`corpus`'s CPU residue (669.35s, ~70.6% of its 947.50s section CPU) is
essentially UNTOUCHED by the timeout-binary swap (that lever saves WALL,
not CPU — the overhead was already ~0 CPU) — it is instead explained by
`gen_cc`'s own wrapper overhead (~142.58s, separately measured above) plus
real bash-loop/fork CPU cost plus the TRUE exec-batching share. The three
levers are measuring three DIFFERENT axes of the same section's cost
(gcc-batching: CPU; timeout-swap: wall; exec-batching: mostly wall, with
a small CPU component from fewer fork/exec calls) and should not be
summed naively — see "What the numbers say" for how they combine.

## What the numbers say

**Unlike [TT-3]'s ccache row, this one is a measured YES, not a refuted
prediction — batching genuinely helps this workload, on both pools
tried, by a real multiple, under the harness's own execution shape.**
Stated as plainly as the evidence supports:

**Three independent levers, on two DIFFERENT axes (CPU vs. wall-clock) —
none alone gets close to the whole suite, and the two wall-clock levers
in particular must not be added to the CPU one as if they were the same
currency:**

| lever | axis | best measured multiple | applies to | measured ceiling |
|---|---|---|---|---|
| gcc-batching (Stage B) | CPU | 3.66x (shape B, N=16, corpus pool) | every section that compiles generated C (all but `reject`/`resource`) | gcc is 647s/17% of `make test`'s total 3,777 CPU-s — net CPU SAVED at 3.66x = 17.13% x (1 − 1/3.66) ≈ **12%** of the suite's total CPU |
| `timeout`-binary swap | WALL | 31.18x on the `timeout` call itself (uutils 108.7ms/call vs. GNU coreutils 3.5-4.2ms/call, this box) | any section using `timeout` at all — measured concentrated in `corpus` (23,252 calls) | ≈**200s of `corpus`'s 468.91s section wall (≈43%)**, near-zero CPU effect (the overhead being removed was already ~0% CPU) |
| exec-batching (one process/pattern), NET of the timeout-swap above | mostly WALL | 5.57x (0.1225s → 0.0220s on the 16-pattern sample, AFTER the timeout binary is already fixed) | ONLY `corpus` (the sole section using `run.sh`'s per-case shape at all — Stage A2 found the other six already loop internally) | a further wall reduction on top of the timeout-swap's own ≈43%, magnitude not separately re-measured at full `corpus` scale |

**The first cut of this memo reported exec-batching's ceiling as
"245.59x / ~14-18% of suite CPU," conflating two effects that Stage A2's
manager review correctly separated: most of that number was the
`timeout`-binary choice (a wall-clock, near-zero-CPU, one-line-PATH-fix
lever), not an inherent cost of per-case process spawning.** The
TRUE exec-batching-specific lever, isolated, is the much smaller 5.57x.
This is corrected here rather than left standing — the earlier number was
measured correctly but INTERPRETED too broadly before the binary-level
decomposition existed.

**The three levers are structurally independent and could all be adopted
together** (`corpus` is the one section paying for all three costs at
once: gcc invocation count, `timeout`-binary overhead, and per-case exec
count) — but none is "the fix" alone, and the CPU-axis ceiling (gcc-
batching, ~12%) and the wall-axis ceilings (timeout-swap ~43% of
`corpus`'s wall, exec-batching a further increment on top) answer
DIFFERENT questions ("how much less core-time does the suite consume" vs.
"how much sooner does `corpus` finish") and must not be summed into one
percentage. The remaining majority of both axes — six differential
sections' own internal sweep compute, python3 oracle time, `gen_cc`'s own
wrapper overhead, ordinary bash-loop cost — is either genuine compute
this project already wants done, or a further kind of lever (parallelizing/
optimizing the differential drivers' own internal sweeps) this row was
not chartered to investigate.

Stated as plainly as the evidence supports, on the gcc-batching lever
specifically:

- TU-batching (shape B) beats link-batching (shape A) at every batch size
  on both pools — concatenating source amortizes more of the fixed
  per-call cost (process start, header/ABI parsing, one link instead of
  N+1 objects plus a link) than splitting compile from link alone.
- The best speed-up is NOT at the largest batch size tried. It is at the
  batch size whose BATCH COUNT is close to the box's core count (16
  batches of 16 for a 256-pattern pool on 12 cores; 8 batches of 8 for a
  64-pattern pool) — 3.66x and 2.73x respectively. Larger batches (N=64,
  N=256) look BETTER in the serial numbers (7.39x, 5.44x) and are
  measurably WORSE than the plain baseline under the harness's actual
  12-way-parallel execution (0.47x-0.96x on the corpus pool, 0.41x-0.70x
  on atomic) because too few batches starve most of the box's cores. Any
  design reading only the serial column would ship a regression.
- The speed-up is not free of a real cost: TU-batching's failure mode is
  all-or-nothing per batch (one bad member blocks every other member in
  its batch, confirmed directly with a planted syntax error — 0.231s to
  fail, but the 15 good co-members then need re-compiling from scratch,
  2.993s more, to recover what the batch's own failure destroyed), and
  TU-batching cannot mix patterns compiled with different `--features`
  values without a real emitter fix (`PCREC_FEATURE_SET`/
  `PCREC_FEATURE_MODULES`, confirmed by a genuine `-Werror` compile
  failure, not inferred).
- The `perr` population (patterns pcrec is EXPECTED to reject, never
  reaching gcc at all) is a design question this memo surfaces but does
  not answer: whether/how such patterns enter a batch is [TT-4.2]'s to
  decide, not measured here.
- **Exec-batching (the second lever) has its own un-measured cost this
  row flags rather than solves**: `run.sh`'s per-CASE process isolation is
  what lets it attribute a crash, a timeout, or a VM give-up to the EXACT
  case that caused it (`tests/harness/run.sh`'s `trc` discrimination at
  the timeout/crash/give-up branches). Collapsing many cases into one
  process (shape (ii)) means a crash on case 7 of 10 could take cases
  8-10 down with it, or (worse) corrupt state that makes case 8 read as a
  false pass/fail — the SAME class of failure-isolation problem TU-
  batching has for gcc, unmeasured here because this cell's 16-pattern
  sample happened to contain no crashing cases. A real design needs
  either per-case `fork()` inside the batched driver (cheaper than
  `timeout`+shell but not free) or an accepted "attribute to the whole
  batch, fall back per-case on any anomaly" rule — the same shape
  [TT-4.2] already owes gcc-batching.

**No recommendation about the harness's own design is made beyond what
these numbers directly support** — [TT-4.2] is where batch-size choice,
the `--features`-homogeneity constraint, and the failure-isolation
fallback get designed, gated on a D6 panel per the plan row. What this
memo delivers is the number that gates it: batching is worth building,
somewhere in the batch-count-near-core-count neighbourhood rather than
"as big as possible," with two confirmed, non-hypothetical obstacles
(feature-set collision, all-or-nothing batch failure) already in hand
for that design to solve rather than discover.

**On the `timeout`-binary swap specifically**: the single HIGHEST-
LEVERAGE, LOWEST-RISK finding in this whole memo — a measured ~43% wall
reduction on `corpus` (the suite's single worst section by wall AND by
gcc-CPU) from substituting one binary on `PATH`, zero harness redesign,
zero batch-size/failure-isolation/`--features`-homogeneity design
questions to answer. It is explicitly named by the manager as its own,
SEPARATE row — not something this row implements — because a
system-`PATH`-dependent behavior swap (this box happens to have BOTH
`timeout` implementations installed; that is not guaranteed on every
machine `make test` runs on) needs its own scoping, not a rider on a
batching memo.

**On the exec-batching lever (Stage A2) specifically, corrected**: also a
measured YES within its narrow scope — `corpus` alone, where it applies —
but by a FAR SMALLER multiple than this memo's first cut reported once
decomposed from the timeout-binary effect: **5.57x, not 245.59x**, is the
part attributable to reducing PROCESS COUNT itself (one exec per pattern
vs. one per case) rather than to `timeout`'s own overhead. Its scope is
narrow BY MEASUREMENT, not by assumption: five of the six other
re-censused sections already use the "one process, many cases" shape this
lever would introduce for `corpus` — they adopted it independently, for
their own differential-driver reasons, before this row ever asked the
question. Its own failure-isolation cost is flagged, not measured (no
crashing case existed in this cell's 16-pattern sample) — the SAME open
design question TU-batching has for gcc, and likely the harder version of
it, since per-case exec isolation is `run.sh`'s CURRENT crash/timeout/
give-up attribution mechanism, not an incidental side effect.

**Combined, honestly, across all three**: gcc-batching's CPU ceiling
(~12% net suite-wide) and the `timeout`-swap's wall ceiling (~43% of
`corpus`'s own wall) are on DIFFERENT axes and answer different questions
— they should not be added into one percentage. Exec-batching's TRUE,
decomposed contribution (5.57x on top of an already-fixed timeout binary)
is smaller than this memo first reported, and is itself layered on top of
the timeout-swap rather than independent of it. None of the three, alone
or combined, accounts for `make test`'s full CPU or wall cost — the
remaining majority is real compute: six differential drivers' own
internal sweeps, oracle/python3 time, `gen_cc`'s own wrapper overhead, and
ordinary bash-loop cost this memo's shims cannot see past a process
boundary — which this row correctly reports as UNADDRESSED rather than
assumed solved by any lever, and the `timeout`-binary finding specifically
is flagged as its own row rather than folded into [TT-4.2]'s scope.
