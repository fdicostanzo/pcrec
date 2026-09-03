# [TT-12] STEP 0 — the union battery's CPU-utilisation profile

Lane tt12a (sonnet), analysis only, no runs performed here. Source data:
`docs/dev/tt12_cpu_samples_battery_de32a4b.tsv` (535 rows, one per 30 s:
epoch, HH:MM, load1, all-core busy%, nproc=12, stage tag) and
`docs/dev/tt12_battery_stage_markers_de32a4b.log` (stage START/END
timestamps + rc), both from the union battery run on `de32a4b`,
2026-09-02 19:28:56 → 23:56:08 (`battery_v4`: `pre → test → strict → san →
lint → mech`, `mech` at `PROCS=4` per `battery.sh`). Stage-shape reads from
the session scratchpad: `battery_san.log` (34 `-- san: <script> --`
markers), `battery_mech.log`, `battery_test.log`, and opt5i's
`axes2.log` (the 21-axis `test-axes` run on the same tree, 2026-09-02,
its own `== axes summary ==` table with per-axis wall time).

## 1. Per-stage wall time, utilisation, idle core-hours

| stage | wall | mean busy% | median busy% | idle frac | idle core-hours |
|---|---|---|---|---|---|
| pre (not a battery stage — box baseline before `test START`) | 7.67 min | 11.3% | 11.0% | 0.89 | — |
| test (`make -k -j12 test`) | 16.72 min | 81.4% | 99.0% | 0.19 | 0.62 |
| strict (`make strict`) | 0.17 min (10 s) | n/a — no 30 s sample landed in the window | — | — | negligible (<0.05) |
| san (`make san`, 34 scripts, serial `for` loop) | 109.63 min | 15.7% | 10.0% | 0.84 | **18.49** |
| lint (`make lint`, `gcc -fanalyzer`) | 0.83 min (50 s) | 9.5% (2 samples) | 9.5% | 0.91 | 0.15 |
| mech (`make mech`, `PROCS=4`) | 132.18 min | 47.0% | 40.0% | 0.53 | **14.01** |
| **battery total (test…mech)** | **259.5 min (4h20m)** | — | — | — | **33.3 core-hours idle, of ~51.9 core-hours spent** |

idle core-hours = wall(h) × 12 × (1 − mean_busy/100). `san` and `mech` are
where the recoverable time is: together 96% of the battery's idle
core-hours, on 93% of its wall time. `test` is the opposite problem (§5).

## 2. `san` — attributing 109.6 minutes of ~1-core-busy across 34 scripts

**Mechanism, confirmed by reading every script `san_scripts.txt` names**:
`make san`'s suite loop (`for s in $(SAN_SCRIPTS); do ... bash "$s"; done`,
Makefile:1106) is **strictly serial across scripts** — no `-P`, no
backgrounding. `SAN_ENV` exports `PROCS=${PROCS:-$(nproc)}` into every
script's environment, but grepping each of the 34 scripts for `PROCS`/
`GROUP_PROCS` shows only **4 of the 34 read it at all**:
`tests/harness/run.sh`, `tests/reject/run_reject_tests.sh`,
`tests/lookaround/run_expansion_diff.sh`, `tests/anchored/run_anchored_diff.sh`.
The other 30 — including every one of the six whole-corpus identity
scripts (`run_trie_identity.sh`, `run_endvar_identity.sh`,
`run_wordctx_identity.sh`, `run_mlinectx_identity.sh`,
`run_gstart_identity.sh`, `run_vm_identity.sh`) and `run_registry_tests.sh`
— are **structurally single-process**: `PROCS=12` in their environment
does nothing, because nothing in the script reads it. That is the direct
cause of san's 15.7% mean busy (≈ 1.9 of 12 cores) and its 10% median
(≈ 1.2 cores, i.e. one core doing real work plus sampling noise).

**Order reconstruction** (san log has no timestamps; the 30 s CPU samples
do). `san_scripts.txt`'s line order is the execution order (`$(shell grep
...)` preserves it). Matching the 219 san-tagged samples' busy-% spikes
against script POSITION and PARALLEL/serial classification:

| sample window | time | busy% | script (by position + parallel-classification match) | confidence |
|---|---|---|---|---|
| i=2–10 | 19:54–19:58 | 51→98→96 | `tests/harness/run.sh` (**pos 1**, PARALLEL) | high — first script, only candidate for an early full-box spike |
| i=11 | 19:58 | 38 | harness's tail (its own worker-drain: "parent aggregates once every worker reports") | high |
| i=20–21 | 20:03 | 49, 26 | `tests/reject/run_reject_tests.sh` (**pos 3**, PARALLEL; `cli` at pos 2 is serial and short, consistent with the gap) | medium-high |
| i=22–86 | 20:04–20:35 (~32 min) | 9–15%, one 2-sample blip to 34% at i=87–88 (20:36–20:37) | 25 serial scripts, **pos 4–28** (registry, parse, codegen_tests, all 6 identity scripts, ir_listing, vm_tests, encseam, possdiff/possessify, rungdiff/rungselect, altdiff/altcls, assertions+3 diffs, atomic_diff, backref/dupnames diffs, lookaround_diff) | low on per-script boundary, high on "this whole window is single-threaded serial work" |
| i=194–195 | 21:30 | 98, 98 | `tests/lookaround/run_expansion_diff.sh` (**pos 29**, PARALLEL) | high — matches ordinal position (29th of 34, ≈94% seen at 94% of the way through wall time... this run is further along since the 25-script middle window ate disproportionate time, see below) and is the only remaining PARALLEL script before `anchored_diff` |
| i=213–217 | 21:39–21:41 | 77→79→65→45→28 | `tests/anchored/run_anchored_diff.sh` (**pos 31**, PARALLEL), tapering as workers finish | high |
| i=218–219 | 21:42–21:43 | ~9–10% (baseline) | `recursion_diff`, `run_gen_timeout_tests.sh`, `run_known_fail.sh` (pos 32–34, serial, short) | medium |

**Stated uncertainty**: the four PARALLEL-script windows are identified
with high confidence (ordinal position in the script list matches ordinal
position of the CPU spike among san's 34-script run, and no other script
in the manifest reads PROCS). The ~86-minute middle stretch (pos 4–28,
i=22–193) cannot be disaggregated into per-script durations from this
data — it has no internal timestamps and its scripts' log output (line
count) is not a reliable wall-time proxy (`tests/harness/run.sh` itself
logs only 8 lines despite being the single biggest CPU consumer of the
whole stage). One structural fact narrows it anyway: five of those 25
scripts (`run_endvar_identity.sh`, `run_wordctx_identity.sh`,
`run_mlinectx_identity.sh`, `run_gstart_identity.sh`, `run_vm_identity.sh`)
each extract **every** `pattern` line from **every** `.rxt` under `tests/`
(their own header comments: "every `pattern` line from every .rxt under
tests/... the gate's population grows with the corpus") and compile it
**twice** — once per build variant — in one process, no PROCS. That is a
substantially bigger single-threaded population than `run_trie_identity.sh`'s
fixed 500-pattern×2 (its own env default `TRIE_N=500`).

**Top five san idle-core-minute contributors** (ranked by best available
evidence — probe volume / population size, NOT measured wall time, which
the data cannot separate at script grain):

1. `tests/registry/run_registry_tests.sh` — single-threaded, largest log
   volume of any san script (966 lines), documented "~1000+ checks and
   ~700K probes" (PC-3 vs libpcre2 + PC-4 differential, docs/testing.md).
2. `tests/codegen/run_vm_identity.sh` — whole-corpus × 2 compiles, single process.
3. `tests/codegen/run_endvar_identity.sh` — same shape, whole-corpus × 2.
4. `tests/codegen/run_wordctx_identity.sh` / `run_mlinectx_identity.sh` /
   `run_gstart_identity.sh` — same shape; grouped, indistinguishable from
   this data.
5. `tests/codegen/run_trie_identity.sh` — fixed 500×2 compile, single
   process; smaller population than the whole-corpus family but the
   biggest single-threaded consumer NOT drawing on the live `.rxt` corpus.

## 3. `mech` — attributing the 35–96% swing at `PROCS=4`

**Structural setup** (`tests/mech/run_sabotage_matrix.sh`, read directly):
`PROCS` is the number of sabotage ROWS run concurrently (default 1;
`battery.sh` sets `PROCS=4` explicitly, overriding the Makefile's own
`PROCS=${PROCS:-$(nproc)}` default of 12). `JOBS` (the per-row `make -j`
build width) and `INNER_PROCS` (the per-row budget handed EXPLICITLY to
the two suite arms — `harness`, `reject` — that read `PROCS` themselves)
are both `ncpu/PROCS = 12/4 = 3`. Every OTHER suite arm in the vocabulary
(`registry`, `pc3`, `cli`, `vm`, `possdiff`, `rungdiff`, `altdiff`,
`assertions`+diffs, `atomicdiff`, `brefdiff`, `lookaround`, `recursion`,
`anchdiff`, `sizeterm`, `resource`, `framebuffer`, `stackdepth`, …) is the
SAME single-process script `san` runs — no internal PROCS awareness at
all (confirmed by the identical PROCS/GROUP_PROCS grep in §2).

**Reading the busy-% histogram (265 samples)**:

| band | share of samples |
|---|---|
| < 25% | 4.2% |
| 25–35% | 9.1% |
| **35–45%** | **44.5%** |
| 45–60% | 22.6% |
| 60–80% | 11.7% |
| ≥ 80% | 7.9% |

44.5% of mech's samples sit in a narrow band 2–12 points above the
theoretical `PROCS=4` row-concurrency ceiling (`4/12 = 33.3%`). This is
the **steady state**: at any moment, most of the 4 concurrently-running
rows are executing one of the ~28 single-threaded suite arms (or the
120 s-bounded, also single-process `SAB_REACH` witness probe that runs
BEFORE each row's build), so no more than 4 cores are doing real work no
matter what the box has spare — a hard structural cap, not a scheduling
accident. The ≥60% tail (19.6% of samples) is when 2+ rows overlap their
`git archive`+`make all -j3` build phase (up to 4×3=12-way) or land in
`harness`/`reject` simultaneously (their own INNER_PROCS=3 fan-out,
same 12-way ceiling). The 4.2% below 25% (down to a measured 4% minimum)
is windows where fewer than 4 rows are concurrently compute-bound at all
— plausible near the run's start/end (row-scheduler fill/drain) or when
multiple rows are simultaneously mid-`SAB_REACH` (single process each,
bounded ≤120 s).

**Verdict**: the dip is `PROCS=4` leaving 8 cores idle throughout for
every row that isn't in `harness`/`reject`/a build burst — which is most
rows most of the time, because only 2 of ~30 suite arms carry any internal
parallelism. This is NOT primarily "the matrix's serial phases" in the
sense of one shared bottleneck; it is that PROCS=4 caps row-level
concurrency below what the box could sustain if more rows ran at once,
given that per-row work is overwhelmingly single-threaded. [TT-8]
(docs/dev/plan.md, CLOSED 2026-08-23) already measured this exact
trade-off on the SAME script, an EARLIER (118-row) matrix, at 6b0ef30:
**`PROCS=6` 28:43 vs `PROCS=4` 36:36**, byte-identical rows — i.e. MORE
row-concurrency (fewer inner-arm threads per row: `JOBS`/`INNER_PROCS`
drop to `12/6=2`) was ~21% faster, exactly because most rows never use
their inner-parallel budget. `PROCS=6` was recorded there as "the
documented matrix setting" — **`battery.sh` currently hardcodes
`PROCS=4` for the battery's own `mech` invocation, contradicting that
finding**. The matrix has grown since (118 rows at TT-8 → 222
`tests/mech/sabotages/S*.sh` today), so the absolute minutes will differ,
but the mechanism generating the win is unchanged.

## 4. `test-axes` — what bounds each axis's parallelism (opt5i's `axes2.log`)

**Structure** (`tests/axes/run_axes.sh`, read directly): ONE baseline dump
(`RXTFLAGS=` empty, 178 s) is computed once and reused for all 21 axes —
axes are NOT each paying a redundant baseline run. Each axis then runs
`tests/harness/run.sh` once (`RXTFLAGS=<axis flags>`, `PROCS=${PROCS:-$(nproc)}`
= 12), producing a dump, followed by a serial `dump_diff.awk` comparison
against the shared baseline (fast — tens of ms over ~22K lines) and a
final two-run PC-4 oracle cross-check (~107 s total, ~2.5% of the 4205 s
run). So each axis's wall time is dominated by ONE `harness` run at
`PROCS=12` over the corpus.

**Per-axis wall times** (from `axes2.log`'s `== axes summary ==` table):
19 of 21 axes land in a tight 174–180 s band; two are outliers —
`-fno-length-prune` at **517 s** (3× the rest — this axis removes a
backtrack-cost prune, so its own answer computation is genuinely slower,
not a parallelism artifact) and `--engine=dfa` at **94 s** (fastest — 9,483
of 22,309 cases REFUSED immediately at compile time, so most of the
corpus never reaches a match run at all). `-fprefilter` (135 s) is the
same shape, 13,535 refusals.

**What caps utilisation short of 12 cores**: the plan row's own
observation ("load 4.5–6 on 12 cores... roughly half idle... 9 live
harness workers observed") is explained by `tests/harness/run.sh`'s own
documented dispatch unit — **`PROCS=N` runs N `.rxt` FILES concurrently**,
one file per worker, not one case. The corpus is **190 `.rxt` files**
(excluding `known_fail/`) with a heavily skewed case-count distribution:
median 20 cases/file, p90 122, but the single largest file,
`tests/assertions/multiline.rxt`, holds **3,065 cases** — 56% more than
the next-largest (`tests/possessify/possessify.rxt`, 1,972). Because a
file's cases run serially inside its one worker, `multiline.rxt` alone
takes as long as roughly 150 median-sized files combined, and the other
11 workers exhaust the small-file queue and go idle well before it
finishes. This is a **file-granularity long-tail** effect, not a `PROCS`
cap not reaching `nproc` (`PROCS` IS already `nproc=12` here) and not
primarily the dump/compare phase (which is a small, fast, serial tail —
seconds, not the sustained ~50–58% idle seen through most of each axis's
wall time).

## 5. `test` at `-j12` — the OPPOSITE problem (oversubscription)

`battery.sh` runs `test` as `make -k -j12 test`: make's OWN `-j12` (for
the top-level Makefile's recipe graph) is combined with `test`'s
sub-suites, several of which ALSO default their internal `PROCS`/
`GROUP_PROCS` to `nproc()=12` when unset. The sample data shows this
directly: busy% ramps to 99–100% within the first ~5 samples and *load1*
peaks at **47.61** on a 12-core box (row at 19:44, `test` stage) — roughly
4× the core count, the multiplicative signature of two independently-sized
parallelism layers (`-j12` outer × `PROCS=12` inner) stacking rather than
sharing the box. This is the "opposite problem" the plan row flags — K44's
cell reds — and is a correctness/stability risk (thrashing, false timeouts
under contention), not merely a wasted-idle-core one, so it doesn't add to
§1's idle-core-hour total but belongs in the same profile.

## 6. Recommendations, ranked by idle core-hours recovered per unit of change

Every recommendation names the measurement that would confirm it (D77) —
none of this is built here; STEP 0 is analysis only.

1. **`make mech` at `PROCS=6`, not `PROCS=4`** (battery.sh:11). Zero new
   code — this is a one-line change to a shell script already reverting
   a documented finding. [TT-8] measured 28:43 vs 36:36 (−21%) on an
   earlier, smaller matrix; expected saving on today's 222-row matrix is
   proportionally larger in absolute minutes, plausibly ~25–30 min off
   this run's 132 min. **Confirming measurement**: `PROCS=6 make mech`
   once, full matrix, compare wall time and row-for-row DETECTED/
   UNDETECTED/ANOMALY counts against this run's `battery_mech.log`
   (must be byte-identical bar known shard-count artifacts, per TT-8's
   own precedent).
2. **STEP 1's pairwise `run_axes.sh`** (already chartered): two axes
   concurrently at `PROCS=nproc/2=6` each. §4 shows each single axis
   already sits well below full utilisation for its own structural
   reason (one dominant file, `multiline.rxt` at 3,065 cases, serialises
   inside one worker regardless of `PROCS`) — pairing a SECOND axis's
   independent bottleneck onto the other half of the box should roughly
   double throughput rather than contend with the first axis's own
   ceiling. Sequential total is 4,205 s (70 min); ≤40 min is a
   plausible target if pairing is close to additive, which the "already
   half-idle, for a reason unrelated to PROCS width" finding supports.
   **Confirming measurement**: STEP 1's own delivery (pairwise run,
   wall time + per-axis AGREE/MISMATCH/LOST/GAINED counts unchanged from
   the sequential run).
3. **Run san's four single-threaded-adjacent PARALLEL scripts aside, and
   consider concurrency among the 30 genuinely single-threaded ones** —
   they are independent corpus compiles/compares with no shared state
   (each opens its own `mktemp -d`, reads `$PCREC`/`$CC` read-only). A
   small `-P` (e.g. 3–4) over `san_scripts.txt`'s serial `for` loop could
   recover a large slice of san's 18.5 idle core-hours — the single
   biggest number in §1 — without touching any script's internals.
   **Confirming measurement**: before building anything, time the 5
   whole-corpus identity scripts (§2's #2–4) run concurrently vs
   sequentially on a quiet box, to confirm they don't serialise on a
   shared resource (e.g. `$PCREC`'s own file, `/tmp` contention) that
   would blunt the win — the D77 trigger this recommendation needs before
   it's worth `-P`-wiring `make san`.
4. **`battery_v5` stage order and start time, given the day/night rule**
   (`docs/dev/dev_journal.md`, part 7 addendum 4: "pcrec lanes and
   batteries by day... the bench's blocking windows overnight"). This
   run started at 19:28 and finished at 23:56 — already into the evening
   — and battery_v5 adds `axes` (target ≤40 min) between `strict` and
   `san`, pushing the finish later still. Recommendations #1–#3 above
   would claw back roughly 25–45 min of that addition. If they land
   before `test-axes` joins the battery (STEP 2), the net wall-time
   change may be close to zero; if not, **start the battery earlier in
   the day** rather than reorder stages — `san` and `mech` are the two
   long AND the two most-compressible stages (recommendations #1 and
   #3), so moving them earlier or later in the sequence doesn't change
   the total, only when the risk window falls. **Confirming
   measurement**: battery_v5's first full run's own stage markers,
   diffed against this run's total wall time.
5. **`test` at `-j12`**: not an idle-core-hours recommendation (§5 is
   oversubscription, not idle), but flagged for STEP 3/K44: decouple the
   two parallelism layers — either cap the outer `make -j` (e.g. `-j1`
   or `-j2`) and let each sub-suite's own `PROCS=nproc` own the fan-out,
   or vice versa. **Confirming measurement**: `make -k -j1 test` (relying
   solely on internal `PROCS=nproc`) vs this run's `-j12`, wall time and
   peak `load1` (this run: 47.61) compared.
