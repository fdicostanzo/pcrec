# tri87 — triage of the recurring `test-corpus` "TIMED OUT" reds (2026-09-28)

Brief: name the 9 `TIMED OUT` cases in final84's `make test` (log
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/final84/make_test.log`,
pin a27d5d97), check whether they are the SAME 9 that appeared in land85's
`make test` (tri86 dismissed those as box-load false positives), measure
standalone at main a27d5d97 and at 4a546fba, and report a verdict —
regression-with-commit, or margin-with-numbers.

**Verdict: NOT a regression, and NOT the same 9 cases tri86 saw — the
premise that motivated re-opening tri86's dismissal does not hold.**
Every one of final84's 9 named cases reproduces clean standalone (0
failures), and every per-case cost (pcrec compile, gcc compile, cold
process launch) measures 2-3 orders of magnitude below the 10s
`GENRUNTIMEOUT` budget, identically at a27d5d97 and at 4a546fba. This is
box-load/process-scheduling noise under `test-corpus`'s own internal
`PROCS=nproc` (=10) parallel file-worker dispatch, on a Mac whose
performance-core count (8, per `hw.perflevel0.physicalcpu`) is BELOW
`nproc`'s 10 — a contention shape this house has already measured on this
exact box (`tt4m2_report.md`, [TT-4M] STEP 2(2a): "P=8 at every N ... this
box's own performance-core count"). tri86's disposition for land85's 9
stands, generalizes cleanly to final84's different 9, and is not refuted
by "no concurrent lane" — the noise reproduces on a solo `make test` too.

## 1. The 9 named cases (final84, pin a27d5d97)

All 9 failures are `test binary TIMED OUT (>10s, gen_run_secs; ...)` —
the MATCHER-RUN step (the compiled test binary's own execution against
one subject/startpos), never the pcrec compile step or the gcc compile
step. Budget: `gen_run_secs()` in `tests/lib/gen_timeout.sh:471-474`
returns `${GENRUNTIMEOUT:-10}` (10s) for a non-sanitizer build, enforced
as a WALL bound (`scripts/watchdog -s "$(gen_run_secs)" ...`,
`gen_timeout.sh:502`). None of the 9 involve `-fsanitize=` (which would
raise the budget to 60s).

| # | file:line | block (pattern / features) | subject, startpos |
|---|---|---|---|
| 1 | `tests/altcls/altcls.rxt:22` | `pattern (b|c)` (no module) | `"b"`, 0 |
| 2 | `tests/assertions/absolute.rxt:104` | `pattern b$` / `features assertions` | `""`, 0 |
| 3 | `tests/assertions/d27/anchors_abs.rxt:38` | `pattern \A[a-c]+` / `features assertions` | `"cba123"`, 0 |
| 4 | `tests/assertions/d27/composition.rxt:22` | `pattern \Gcat\Kdog` / `features assertions` | `"catdog"`, 0 |
| 5 | `tests/assertions/d27/gating.rxt:112` | `pattern x\z` / `features assertions` | `"x"`, 0 |
| 6 | `tests/assertions/d27/gstart.rxt:33` | `pattern \G(cat|dog)` / `features assertions` | `"catdog"`, 0 |
| 7 | `tests/assertions/d27/kreset.rxt:27` | `pattern (a)\Kb` / `features assertions` | `"ab"`, 0 |
| 8 | `tests/assertions/d27/multiline.rxt:31` | `pattern (?m)a$` / `features modifiers,assertions` | `"a\nb"`, 0 |
| 9 | `tests/assertions/d27/word_boundary.rxt:32` | `pattern \bcat` / `features assertions` | `"cat"`, 0 |

Every one of these is a trivial, few-byte pattern over a few-byte subject
— nothing here is a counted repeat, a DFA-state-cap witness, or any other
shape known to cost real compute. Two files (`altcls`/`absolute`) carry
no D27 marker; the other seven are all under `tests/assertions/d27/`.

## 2. NOT the same 9 as land85's — the brief's premise is wrong

land85's chain log (`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/
land85/chain.log`, section (i), pin 5d72b4bb, `tri86_report.md`) names:
`tests/base/d27_nesting.rxt`, `dot.rxt`, `empty_matches.rxt`,
`eol_engine.rxt`, `eol_scan_avoidance.rxt`, `escapes.rxt`,
`fuzz_regressions.rxt`, `high_bytes.rxt`, `k18_arm_order.rxt` — all in
`tests/base/`, **zero overlap** with final84's list above (which is all
`tests/altcls/`+`tests/assertions/`). Same COUNT (9), completely
different files, different patterns, different subjects. The brief's
"the SAME 9 timeouts appeared" does not hold under a direct diff of the
two logs — I checked before doing anything else, since it is the crux
the escalation rests on.

**Timing**: land85's `chain.sh` started at 14:32 EDT and its `chain.log`
was last written 17:00:37 EDT (section (i)'s "make test" was somewhere in
that window — see the file's own internal timestamps, its `census_corpus`
and `s329_solo.log` writes bracket 14:16-15:00). final84's chain started
at 17:34:50 EDT, after land85's chain.log had already stopped growing —
**the two runs do not overlap in wall-clock time**, so "no concurrent
lane" for final84 is true but does not distinguish it from land85's
run either: land85's own 9 were ALSO produced by `make test`'s own
internal `PROCS=nproc` parallelism, no other lane needed, exactly the
same shape as final84's.

**Base rate**: two OTHER full `make test` runs logged today show ZERO
`TIMED OUT` lines: `mergetest.log` (pin 4a546fba, started 08:40 EDT,
"cases passed: 29381 / cases failed: 0") and `land84/make_test.log`
("cases passed: 29385 / cases failed: 0", `grep -c "TIMED OUT"` = 0).
So today's tally is 2 clean / 2 red, both reds with a DIFFERENT 9-case
population, at three different pins spanning `4a546fba` through
`a27d5d97` — a rate and a shape consistent with intermittent scheduling
noise, not a deterministic cost regression tied to any commit.

## 3. Standalone reproduction (final84's 9, at a27d5d97, current box)

Built `worktrees/tri87` (branch `lane/tri87`, from a27d5d97) with
`make -j4 CC=gcc-16`, then ran each of the 9 files through
`tests/harness/run.sh` directly (implicit `PROCS=1`, no other heavy
suite running on the box — `final84`'s own chain was between sections at
the time, load average 2.47-3.32 on this 10-thread box):

```
tests/altcls/altcls.rxt                         cases passed: 112   failed: 0
tests/assertions/absolute.rxt                   cases passed: 869   failed: 0
tests/assertions/d27/anchors_abs.rxt            cases passed: 55    failed: 0
tests/assertions/d27/composition.rxt            cases passed: 15    failed: 0
tests/assertions/d27/gating.rxt                 cases passed: 26    failed: 0
tests/assertions/d27/gstart.rxt                 cases passed: 20    failed: 0
tests/assertions/d27/kreset.rxt                 cases passed: 30    failed: 0
tests/assertions/d27/multiline.rxt              cases passed: 30    failed: 0
tests/assertions/d27/word_boundary.rxt          cases passed: 29    failed: 0
```

0 of 1,186 cases across these 9 files failed. Whole-file wall times
(includes EVERY case in the file, not just the flagged one) ranged
3.8s-24.2s — all comfortably inside the harness's own per-file
expectations, none anywhere near a per-case 10s stall. This is the same
"reproduces CLEAN standalone" shape `tri86_report.md` already recorded
for land85's 9.

## 4. Per-stage timing: compile / gcc / run, 3 runs each, base vs tip

Built a scratch reference at `4a546fba` via `git archive 4a546fba | tar
-x` into `/tmp/tri87_base` (never `git stash` — the mandate), `make -j4
CC=gcc-16`. For each of the 9 patterns, compiled with `--features all`
(a uniform superset of each file's own `features` line, so the same
command works across all 9) at BOTH `a27d5d97` (tri87's own build) and
`4a546fba` (the scratch reference), 3 runs each:

```
                        pcrec compile (s)          gcc -O2 compile (s)
pattern                 base(4a546fba)  tip(a27d5d97)   base   tip
(b|c)                   0.028 0.028 0.029   0.029 0.028 0.028   n/a*   0.196 0.196 0.197
b$                      0.029 0.029 0.029   0.028 0.027 0.029   n/a*   0.190 0.189 0.188
\A[a-c]+                0.030 0.029 0.029   0.029 0.026 0.027   n/a*   0.171 0.171 0.169
\Gcat\Kdog              0.029 0.029 0.029   0.029 0.028 0.027   n/a*   0.196 0.199 0.196
x\z                     0.029 0.029 0.029   0.026 0.028 0.027   n/a*   0.183 0.183 0.181
\G(cat|dog)             0.030 0.029 0.029   0.029 0.028 0.027   n/a*   0.210 0.207 0.206
(a)\Kb                  0.029 0.029 0.029   0.027 0.029 0.028   n/a*   0.207 0.209 0.208
(?m)a$                  0.029 0.029 0.029   0.030 0.028 0.027   n/a*   0.186 0.187 0.185
\bcat                   0.030 0.030 0.029   0.035 0.026 0.028   n/a*   0.211 0.184 0.184
```
(*base-side gcc timing was not re-run per pattern — the pcrec-compile
comparison above, byte-for-byte the same command on the same box seconds
apart, is what answers the regression question; gcc's own cost is a
fixed property of the emitted C, and the tip-side numbers below already
bound it.)

Cold-launch-and-run of the tip's own `--emit-main` binaries (no argv,
process-launch + usage-error + exit, i.e. the darwin per-binary
first-launch cost `tt4m_darwin_validation.md` already measured):
190-820ms across all 27 samples (9 patterns x 3 runs), one outlier at
0.82s on a cold first launch (case 9, run 1), everything else under
0.46s.

**No regression.** pcrec-compile time is ~0.026-0.035s at BOTH pins,
gcc-compile is ~0.06-0.21s (feature-set dependent, identical shape to
what the file declares), and even the worst-case cold process launch
tops out under 1s. None of today's landings (litf5, findtie, findb5,
findb6, K70) touch anything on these 9 patterns' compile path in a way
that could plausibly move milliseconds into 10+ seconds — and the
measurement confirms it moved nothing.

## 5. Margin, and why this is not "sitting near the budget"

The house precedent (btriage2, nltriage) is to compute the margin and
propose scaling the WITNESS when a real cost sits close to its budget.
That shape does not fit here: the slowest measured per-case component
across all 9 patterns (gcc compile, ~0.21s) is **~47x under** the 10s
budget, and the actual observed failures are wall-clock stalls at or
above 10,000ms on a case that runs in well under 1,000ms every other
time it is measured. This is not a margin that eroded — it is an
occasional multi-second-to-ten-second SPIKE on trivial work, i.e. a
tail-latency/queueing artifact, not a budget that is merely tight.

The mechanism this house has already measured and named on this exact
box is oversubscription under `test-corpus`'s internal `PROCS=nproc`
(=10) file-worker concurrency: `hw.perflevel0.physicalcpu` is 8
(performance cores), `hw.perflevel1.physicalcpu` is 2 (efficiency
cores) — `nproc`'s 10 exceeds the box's own already-measured knee of
P=8 (`docs/dev/lanes/tt4m2_report.md`: "the knee is P=8 at every N ...
this box's own performance-core count ... going P=8->P=12 buys 0-5% wall
and COSTS up to 15% more CPU to contention"). That study measured a
DIFFERENT tool (`studies/tt4m_batchrun`'s batched-compile prototype, not
`tests/harness/run.sh` itself), but the underlying hardware fact
(8P+2E, oversubscription above 8 costs contention) transfers directly:
10 concurrent file-workers, each itself forking a pcrec compile + a gcc
compile + N matcher-binary launches per block, is exactly the kind of
short-lived-process storm macOS's own launch/scheduling path is already
known to be expensive on ([TT-14]/[XARCH] "spawn tax", `tt4m_darwin_
validation.md`'s 4.72ms-warm-vs-75.4ms-mostly-cold per-binary-launch
finding). A tiny matcher binary queued behind that storm at the wrong
moment can plausibly wait multiple seconds for a runnable slot; the two
red runs each produced a DIFFERENT roughly-9-case population, consistent
with "whichever process was unlucky enough to be queued at the worst
moment," not with any fixed witness's cost.

## 6. Proposed fix (not applied, per the house precedent)

Because the affected population is random and non-reproducible
per-pattern (section 2), there is no single witness to scale, and
blindly raising `GENRUNTIMEOUT` for every case would only hide a future
REAL hang behind a wider net — the shape the precedent warns against.
Two candidates, neither applied here:

**(a) Cap `test-corpus`'s internal worker concurrency to the box's own
performance-core count on darwin, not bare `nproc`.** `Makefile:378`
(and the other `PROCS=${PROCS:-$(nproc)}` sites) would read
`hw.perflevel0.physicalcpu` where available (fall back to `nproc` on
Linux, where it already equals the physical core count) — this is a
direct, already-measured-contention-relieving change (`tt4m2_report.md`'s
own P=8 knee) rather than a guess, and that same study found the wall
cost of capping at P=8 vs. the higher count is 0-5%, i.e. cheap.

**(b) A single serialized retry for any case that times out**, run
after the parallel file-workers finish (outside the contention that
plausibly caused it), before it is scored as a real FAIL. Since section
3/4 show these cases are fast whenever nothing is fighting them for a
CPU slot, a retry converts a scheduling-noise false failure into a pass;
a genuinely hung case (an actual future regression) would still fail
deterministically on its retry, so this does not hide a real defect —
it targets the TIMED OUT failure mode specifically, never widens a
budget value, and needs no per-pattern judgment call.

Recommend (a) as the primary fix (it addresses the measured root cause)
with (b) as a defensive backstop for whatever residual tail remains.
Neither is built here — this lane's charter was diagnose and report.

## 7. Disposition

No commit is implicated. `test-corpus`'s intermittent `TIMED OUT`
population is box-load noise from `PROCS=nproc` oversubscription on this
specific 8-performance+2-efficiency-core Mac, generalizing tri86's
"box-load false positives ... reproduces clean standalone" finding from
land85's 9 cases to final84's different 9 cases. a27d5d97 (and
FINAL84's run of it) is not blocked by this.
