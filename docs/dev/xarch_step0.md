# [XARCH] STEP 0 — macOS/M1/gcc-16 vs Linux/Ryzen/gcc-15.2, on identical emitted C

Lane xarch0, 2026-09-05, Mac-local. Measurement only — nothing under
`src/` changed. Two halves per the charter (docs/dev/plan.md [XARCH]):
(1) compile rates, joined against the already-committed Linux size log at
its own commit, no new Linux run; (2) matcher throughput, pcrec built at
the bench's pin `334fd10e`, timed against the bench's own PINNED ledger
numbers at that pin. Every absolute number here is SCRATCH TIER — nothing
in this memo enters the bench's store or is comparable to their quiet-box
floors (memory `pcrec-cross-platform-verification`). Ratios first,
absolutes with load/thermal caveats.

Machine: this Mac (M1, 10 cores), gcc-16 (Homebrew), clang not used here.
Bench machine: `budu-ryzen1600`, gcc-15.2.0.

## What step 0 deliberately does NOT measure

- No JIT column anywhere (local libpcre2 is 10.48-Homebrew vs the
  bench's reference 10.46 — U13's version noise; deferred).
- No clang column (time did not allow a second toolchain axis this pass;
  the charter allowed it optionally).
- Half 2's loglines cell used a SYNTHESIZED subject, not the bench's own
  subject-generation tooling (time did not allow reproducing it faithfully)
  — flagged inline, not comparable to the bench's pinned ratio.
- No conclusion about `make test`'s wall-clock suite time on this box —
  that question is answered already ([TT-14]: spawn tax, not compute);
  this memo only adds a second, independent confirmation via the gcc CPU
  ratio distribution below.
- Nothing about correctness. The size-log run surfaced 751 pre-existing
  test-case failures at commit `81731547` ([M5.0 stage 1], a mid-refactor
  WIP commit) — noted in §1.1 because it explains a row-count gap, not
  investigated further; out of this lane's scope.

## 1. Compile rates (Half 1)

### 1.1 The run

`tests/size/run_size_log.sh` (full corpus, no args) in worktree `xarch0a`,
pinned at commit `81731547` — the exact commit the committed
`docs/dev/artifact_size_log.tsv` was captured at on Linux
(`load1_at_start=5.35`, `rows=2962`, that date `2026-09-05T04:42:38Z`).
Mac run: `load1_at_start=6.13` (this box was NOT quiet — see §4), default
`PROCS=$NCPU=10` (parallel, not serial), wall time ≈10 minutes end to
end (build + full-corpus run) — evidence:
`xarch_step0_evidence/half1/run_size_log_tail.log`.

Result: **26,294 cases passed, 751 failed**, all failures in
`tests/assertions/{absolute,gate,multiline,wordb_empty_compose}.rxt`,
`tests/base/{eol_engine,eol_scan_avoidance,review_r1,review_r2}.rxt`,
`tests/captures/structure_anchors_misc.rxt`, `tests/mrl/{01_trailing,
08_nomatch}.rxt`, `tests/possessify/possessify.rxt`. Commit `81731547` is
`[M5.0 stage 1] the interval-payload refactor` — an interim WIP-stage
commit, not a green tree — so this is very plausibly pre-existing breakage
at that pinned state rather than anything Mac-specific; not investigated
further (out of scope; flagging for whoever owns that stage).

**Mac produced 2,925 size-log rows against Linux's 2,962 — a 37-row gap,
all in one direction.** Joined by `(pattern, engine)` key
(`xarch_step0_evidence/half1/join_size_logs.py`,
full output in `join_report.txt`): 2,925 rows in common, **0 rows only on
Mac**, 37 rows only on Linux — every one of them from the same four
assertions files listed above (`absolute.rxt`, `gate.rxt`,
`multiline.rxt`, `wordb_empty_compose.rxt`), consistent with those cases
failing to reach a compile+size-log-emitting state on this Mac build at
this WIP commit while they did on the Linux capture. Given the commit is
mid-refactor, this reads as the refactor being non-uniformly broken across
platforms at this exact pin rather than a Mac toolchain issue — but it is
a real, reportable asymmetry, not zero.

### 1.2 Byte identity — PERFECT

**0 size_bytes movers across all 2,925 common rows.** Every artifact
pcrec emits from this pattern set is byte-for-byte identical between the
Mac/gcc-16 build and the Linux/gcc-15.2 build at the same commit —
reconfirming the byte-identity claim plan.md's [XARCH] row already cites
(2,962 rows previously) on the smaller common set this run could reach.

### 1.3 gcc CPU-seconds ratio — the headline

**Mac (gcc-16, M1) ÷ Linux (gcc-15.2, Ryzen) gcc CPU-seconds, per
artifact, n=2,925:**

| stat | value |
|---|---|
| median | **0.518** |
| Q1 | 0.503 |
| Q3 | 0.536 |
| p95 | 0.574 |
| min | 0.425 |
| max | 1.688 (single outlier; not re-measured — one cell, no pattern) |

Split by engine stamp: **DFA n=1,226, median 0.518** (p95 0.568); **VM
n=1,699, median 0.519** (p95 0.579, carries the one outlier). The two
engines' compile-time ratio distributions are essentially identical — gcc
compile cost scales with emitted code shape/size on this axis, not with
which pcrec engine produced it.

**Headline: this Mac's gcc-16 compiles the identical emitted C in about
half the CPU-seconds of the bench's gcc-15.2/Ryzen box** (median ratio
0.518, i.e. ~1.93x faster CPU-seconds), tight across the whole corpus
(IQR 0.503–0.536) with only one outlier above 0.6.

**Wall-seconds ratio, same population: median 0.468** (Q1 0.458, Q3
0.480, p95 0.496) — **CAVEAT: load-contaminated on both sides.** The
Linux log's own header states `load1_at_start=5.35`; this Mac run's own
header states `load1_at_start=6.13` (§4) — neither side was a quiet box
at capture time, and CPU-seconds (process CPU time) is far less sensitive
to a busy machine than wall-clock is. Treat the CPU ratio (§1.3) as the
real number and the wall ratio as a caveated aside, per the charter.

### 1.4 The spawn-tax context, restated

[TT-14] (the chartering measurement for the suite-slowness question,
already ANSWERED and out of this lane's scope) found a SERIAL `make
test-corpus` on this same Mac at 1,717.5 s wall against the old Linux
box's 64.1 s serial figure — a ~27x wall gap — while the compute itself
was fine: only 1,067 of the 1,717 seconds were CPU at all, and the worst
single gcc cell then was 1.416 s CPU against an 8.0 s Ryzen-sized pin.
This run's own CPU-ratio distribution (§1.3, median 0.518, meaning Mac
gcc is CPU-*faster*, not slower) is a second, independent confirmation of
that finding's premise: the wall-time gap [TT-14] measured is almost
entirely the macOS fork/exec spawn tax, not compute — this run used
`PROCS=10` (parallel) rather than [TT-14]'s serial baseline, which is
exactly why it finished in ~10 minutes rather than [TT-14]'s ~29-minute
(1,717 s ÷ ~60x-fewer-execs) extrapolation. Compute was never the
problem, on either measurement.

## 2. Matcher throughput (Half 2)

Built at the bench's pin `334fd10e` (worktree `xarch0b`, `gcc-16 -O2
-std=gnu11`, matching `pcrecbench/driverrun.py`'s own default `-O2
-std=gnu11`). All cells: interleaved trials where process-launch overhead
allowed it, internal warmup+multi-trial-median where a single call was
too fast for process-level interleaving to stay clean (noted per cell).
`uptime` checked before each block; this box stayed under load1 2.2
throughout Half 2 (§4).

### 2.1 THE HOOK — floor forced-VM at `--vm-entry-shape=1/2/3` on ARM

**Verdict: on this Mac (ARM64/gcc-16), `forward` does NOT lose to
`plain`/`shared` the way gcc-15.2/x86 measured (×2.0). It TIES `plain`,
confirming o17facts's I-50 §2 prediction — and a THIRD shape, `shared`,
is the actual outlier here, ~3x slower than both.**

Pattern `#` (the `floor` witness), built three ways
(`--engine=vm --vm-entry-shape=N`), timed via `<prefix>_search` over a
128 KB all-`a` subject (no match anywhere — the worst-case/full-scan
regime), 3 independent runs of 9 interleaved trials each (200–2,000
internal iterations per trial; evidence:
`xarch_step0_evidence/half2_hook/{driver.c,hook_run1,2,3.log}`):

| shape | run 1 | run 2 | run 3 | ns/byte (run 3) |
|---|---|---|---|---|
| `plain` (1) | 43,238.0 | 43,108.0 | 42,975.0 | 0.328 |
| `shared` (2) | 129,088.0 | 129,292.0 | 129,521.0 | 0.988 |
| `forward` (3) | 43,048.0 | 43,296.0 | 43,068.0 | 0.329 |

Ratios (median of the three runs): **forward ÷ plain = 0.996–1.004**
(statistically tied, spread <1%), **shared ÷ plain ≈ 3.00**, **forward ÷
shared ≈ 0.333**.

This directly answers the discriminating probe o17facts named in
`pcrec-bench/docs/dev/inbox_from_pcrec.md` I-50 §2 ("time `floor`
forced-VM at `--vm-entry-shape=1/2/3` on your box; if plain or shared
recovers 0.296 ns/B, STEP 2's governor needs a LOWER bound"). **Plain and
forward both land at ~0.33 ns/B here — close to the pre-regression
"fast" figure the x86 ledger cites (0.296 ns/B), not the regressed 0.593
ns/B.** So on ARM, the x86 ledger's ×2.0 `floor`-forced-VM regression
(271,666 → 543,708 ns/set, cross-pin at the `forward` shape both times)
reads as toolchain/arch-specific to gcc-15.2/x86's inline-merge idiom
loss, exactly as o17facts hypothesized — it is NOT a property of the
`forward` shape in general, and this ARM data does not argue for a
program-bytes lower bound on STEP 2's governor.

**New finding, not in either side's prior hypothesis: `shared` is the
one that loses on ARM, by ~3x, not `forward`.** `shared`'s defining
difference (per docs/spec/tuning.md §2.21) is the `noinline` body called
through a static empty descriptor with the three un-suffixed entries
forwarding to their `_in` siblings — an actual out-of-line call plus an
indirection layer neither `plain` (no attribute, direct call) nor
`forward` (body inlined into the three `_in` entries, no call at all)
carries. On this floor witness (`RX_VM_RUNGS 0x0`, a single byte-compare
in a goto chain, per o17facts's I-50 structural read) that call+forward
overhead is ~100% of the per-attempt cost, same reasoning o17facts gave
for why `floor` has zero rung work to amortize an entry-chain cost
against — it just turns out the ARM-costly entry chain is `shared`'s, not
`forward`'s. Worth relaying back to the bench/o17facts channel: if
STEP 2's governor or the auto-shape heuristic ever prefers `shared` for
a large ARM-targeted artifact, this is a real, reproducible penalty to
weigh against `shared`'s frame/canary savings.

### 2.2 Altwide `w-8`/`w-64`/`w-256`, forced-VM and auto (DFA)

Subjects: the bench's own four throughput subjects (`t-128k-clean`,
`t-128k-sparse`, `t-128k-dense`, `t-512k-sparse`), reproduced by calling
the bench's own `gen_throughput_subjects.build()` in-process (read-only;
confirmed zero writes to the pcrec-bench tree —
`xarch_step0_evidence/half2_altwide/gen_subjects_readonly.py`), same
`SEED`, sha256-verified content. Patterns: the bench's own
`gen_patterns.py --out <scratch>`, same derivation. Metric: a full
search-to-completion sweep per subject (leftmost search, following
matches to their end, matching the bench's own "ns/set" = sum over the
4-subject set), 8 interleaved rounds
(`xarch_step0_evidence/half2_altwide/{throughput_driver.c,interleave.py,
altwide_interleaved.log}`). x86 pinned numbers cited from
`pcrec-bench/reports/2026-09-05-altwide-0.2-budu-ryzen1600-after-334fd10e.md`,
`large-subject-throughput` regime, `plain` form,
`pcrec_334fd10e_{vm,auto}-caps-simdna` rows.

| cell | Mac median ns/set | Linux pinned ns/set | ratio Mac÷Linux |
|---|---|---|---|
| `w-8` vm | 4,521,500 | 9,201,403.7 | **0.491** (Mac ~2.0x faster) |
| `w-8` auto | 1,819,500 | 2,257,727.6 | 0.806 (Mac ~19% faster) |
| `w-64` vm | 9,545,500 | 13,181,207.7 | 0.724 (Mac ~28% faster) |
| `w-64` auto | 3,661,500 | 3,425,522.3 | 1.069 (Mac ~7% slower) |
| `w-256` vm | 10,779,000 | 15,886,650.0 | 0.679 (Mac ~32% faster) |
| `w-256` auto | 3,182,500 | 2,899,328.6 | 1.098 (Mac ~10% slower) |

No cell exceeds a 5x ratio in either direction (`w-8` vm's 0.491 is the
widest, and it reproduced consistently — a separate non-interleaved block
run earlier gave 4,629,000, within 2.4% of the interleaved 4,521,500 — so
not re-measured further). **Pattern: this Mac is consistently FASTER on
the forced-VM engine (0.49–0.72x, i.e. 1.4–2.0x) and slightly SLOWER on
the DFA/auto engine for the two wider rungs (1.07–1.10x), while faster on
`w-8` auto too.** Plausible reading: the VM's computed-goto dispatch
favors this core's branch predictor/indirect-branch handling more than
the DFA's table-walk does, but this is a hypothesis, not something this
lane disassembled to confirm.

### 2.3 Bounded — `cls-upto-4/32/1024` and `dig-upto-16`, the `d-01024`/`d-00016` dispatch cells

Whole-subject anchored `<prefix>_match` (the "match-compliance" regime),
forced-VM. Two independent process runs per cell (warmup + 9 internal
trials each, since a single call is single-digit nanoseconds — process
launch noise dominated a naive external-interleave attempt, so this cell
uses internal warmup+trials instead; both runs' evidence in
`xarch_step0_evidence/half2_bounded/{match_driver.c,bounded_timing.log}`).
x86 pinned numbers cited from
`pcrec-bench/reports/2026-09-05-bounded-0.3-budu-ryzen1600-fold-334fd10e.subject-grain.md`,
`pcrec_334fd10e_vm-caps-simdna` rows.

`cls-upto-N` cells: subject SYNTHESIZED as 1,024 bytes of `'0'..'9'`
repeating (not drawn from the bench's own `d-01024` subject generator —
content shouldn't matter here since `[a-z]{0,N}` fails on any non-`a-z`
byte immediately, but flagged). `dig-upto-16` cell: subject corrected to
16 bytes of digits (`d-00016`'s length) after an initial mismatched
1,024-byte attempt was caught and discarded — `\d{1,16}` against a
16-digit subject is the SUCCESSFUL whole-match case the bench's
`d-00016` row measures, not a failing one.

| cell | Mac run 1 median (min) | Mac run 2 median (min) | Linux pinned | ratio (run2 median ÷ Linux) |
|---|---|---|---|---|
| `cls-upto-4` / d-01024 | 2.370 (1.945) | 2.042 (1.725) | 8.7 | **0.235** |
| `cls-upto-32` / d-01024 | 2.358 (1.933) | 1.583 (1.550) | 7.3 | **0.217** |
| `cls-upto-1024` / d-01024 | 2.454 (2.043) | 1.550 (1.549) | 7.0 | **0.221** |
| `dig-upto-16` / d-00016 (whole match) | 8.528 (8.524) | 8.527 (8.523) | 18.2 | **0.469** |

**The `cls-upto` ratios (~0.22–0.35 across two runs, i.e. Mac is roughly
3–4.5x faster on this failed-dispatch overhead) are the widest in this
memo and the two runs disagree with each other by up to 35%** (2.04–2.45
ns run 1 vs 1.55–2.04 ns run 2) **while `dig-upto-16`'s two runs agree to
four significant figures (8.523–8.545 ns both times).** The likely
explanation is Apple Silicon's P-core/E-core heterogeneity: a
single-digit-nanosecond measurement is short enough that the whole timed
region can land on whichever core class the OS scheduled the process
onto for its entire duration, and a process that happens to land on an
efficiency core would read exactly this kind of 1.3–1.6x inflation
without any load or thermal signal to catch it — `dig-upto-16`'s ~20 ns
cell is long enough (relative to scheduling-quantum noise) not to show
the same spread. **This is flagged as a genuine methodological
limitation of nanosecond-scale single-process timing on this chip class,
not corrected for here** (no ARM-tier code exists in this repo to pin
core affinity, and building one was out of scope for step 0). The
direction (Mac faster, by at least 2.5x even on the least favorable run)
is not in doubt; the precise ratio is not pinned tighter than that band.

### 2.4 Loglines `iso-ts` — INCONCLUSIVE, subject mismatch flagged

Pattern `\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?`,
built `auto` and `auto -fno-scan-edge` (`noedge`). **The subject used here
was HAND-SYNTHESIZED (2,000 short lines, 1 in 10 carrying a matching
timestamp) — this lane did not have time to reproduce the bench's own
loglines subject-generation tooling faithfully, unlike altwide's §2.2.**
Two runs (25 internal trials each,
`xarch_step0_evidence/half2_loglines/loglines_timing.log`):

| run | auto median ns/set | noedge median ns/set | noedge÷auto |
|---|---|---|---|
| 1 | 184,000 | 312,000 | 1.696 |
| 2 | 72,000 | 125,000 | 1.736 |

The absolute numbers swing ~2.5x between runs (same P/E-core suspicion as
§2.3), but **the noedge÷auto RATIO is stable across both runs (1.696,
1.736) since both arms were measured in the same run and presumably
shared whatever core placement affected that run.** This ratio's
DIRECTION is the opposite of the bench's pinned cross-pin ledger figure
(`docs/dev/ledgers/2026-09-05-b37-denysplit-after-334fd10e.md` §2.1:
`iso-ts` noedge÷auto = 0.9846 search / 0.9945 throughput at pin
`334fd10e` — noedge slightly FASTER or flat on x86, not ~1.7x SLOWER).
**This is reported as a flagged anomaly, not a finding**: the subject
mismatch (my synthetic log lines vs the bench's real corpus, which the
bench's own ledger notes has flavor-dependent edge economics — "the edge
still costs 3% on syslog text" even on x86) is fully capable of producing
this on its own, and this lane did not control for it. A re-run with the
bench's actual `iso-ts` subject-generation tooling is needed before
drawing any cross-arch conclusion here.

## 3. Byte-identity sanity arm (Half 2, informal)

Not a formal check like §1.2's — but every artifact built for Half 2 was
generated fresh from this Mac's own `pcrec` at the stated pin, so
`.rx` pattern text and pcrec invocation flags are the full reproduction
recipe; no separate byte-comparison was run for Half 2's artifacts against
the bench's own compiled objects (out of scope — Half 2 measures
matcher speed at a shared pin, not code-generation identity, which §1.2
already establishes generally for this same pin's sibling code state).

## 4. Load and thermal context

Half 1 build+run: `uptime` load1 read 18.17 → 9.60 in the minutes before
launch (a fading spike from something already finished — no `make`/`gcc`
process was found running, and no HOLD/lock artifact existed for this
box), settling to load1 ≈6–7 by the time the full-corpus run started
(header `load1_at_start=6.13`). Half 2: load1 stayed in the 0.9–2.2 band
throughout (checked before every timing block per the interleaved-trials
protocol); no block was aborted for load.

## Evidence index

`docs/dev/xarch_step0_evidence/`:
- `half1/` — both size logs (Mac and Linux copies), the join script and
  its full output, the harness run's summary tail.
- `half2_hook/` — the floor/`--vm-entry-shape` driver and all three run
  logs.
- `half2_altwide/` — the generic throughput-sweep driver, the interleaved
  round-robin orchestrator, the read-only bench-subject reproduction
  script, and the interleaved run's log.
- `half2_bounded/` — the whole-subject match-dispatch driver and both
  runs' log.
- `half2_loglines/` — the synthesized subject and both runs' log.

## Offered to the bench

The §2.1 HOOK result (forward ties plain on ARM, shared is the ARM
outlier at ~3x) is a direct, load-bearing answer to o17facts's I-50 §2
discriminating probe and should go back through the inbox/outbox channel
per D78 — this lane does not write there itself.
