# tests/bench/compare — cross-engine performance comparison

pcrec's stated intention is to be *faster* than general-purpose regex
engines, because it compiles each pattern ahead of time into specialized
native C rather than interpreting a general instruction stream at match
time. `tests/bench/run_bench.sh` guards pcrec against regressing against
**itself** (throughput floors, linearity — see that directory's README.md).
This suite instead measures pcrec against **other engines** on identical
inputs, so the project can track whether the stated intention actually
holds, across a matrix of case shapes chosen to stress different things.

## Running

```
bash tests/bench/compare/compare.sh
```

Needs a built `build/pcrec` (`make` at the repo root first), `gcc` (or
`$CC`), `python3`, and the PCRE2 8-bit runtime library (`libpcre2-8-0` —
just the `.so.0`, no `-dev` package needed; see "Why dlopen" below).
Nothing here modifies the repo; all work happens in a `mktemp -d` workdir
that is deleted on exit unless `KEEP=1`.

Env vars (see the header comment in `compare.sh` for the full list):
`PCREC`, `CC`, `KEEP`, `TARGET_SECS` (per-measurement minimum wall time,
default 0.3s), `RUN_TIMEOUT`, `PCREC_TIMEOUT`, `BUILD_TIMEOUT`,
`BENCH_CPU` (core to pin to, default 2), `BENCH_TRIALS` (repeats per
engine/case measurement, default 5), `CASES` (comma-separated case-id
subset, e.g. `CASES=e,d`, for a fast mechanics check instead of the full
13-case matrix).

Output: a streamed per-case log, a consolidated human-readable results
table, a machine-readable TSV block, and a full copy of both written to
`tests/bench/compare/results-<hostname>-<yyyymmdd>.md`.

## Measurement rigor (pinning, trials, order — R2-B1/B2/B3)

Checkpoint review R2 (`docs/dev/reviews/2026-08-09-m2.md`) found this script's
cross-engine numbers untrustworthy for three compounding reasons, all now
fixed, styled after `tests/bench/run_bench.sh`'s equivalent fix (M2.9):

- **No CPU pinning.** The box runs the `schedutil` governor with turbo on,
  and per-measurement wall times (15–160 ms) sat inside a frequency-ramp
  window. Every timed engine invocation is now wrapped in a probed `$PIN`
  prefix — `taskset -c $BENCH_CPU`, plus `chrt -f 50` only if that actually
  succeeds (it does not have permission on this box; the probe degrades
  quietly and the script still runs, pinned via `taskset` alone). Untimed
  setup work (subject generation, `pcrec`/`$CC` builds) is not pinned —
  only work whose wall time is reported.
- **Single-sample measurements.** A published "0.944 ratio" ranged
  0.820–1.113 across 7 repeat runs and flipped sign in 4 of 7; a headline
  "61 ns vs 76 ns" latency pair ranged 1.013–1.982. Every engine/case
  measurement now runs `BENCH_TRIALS` (default 5) independent, pinned
  trials. The reported `value` column is the **median**; a new **`spread`**
  column carries the max/min ratio across those trials alongside it, so a
  noisy result is visible instead of silently hidden behind one lucky (or
  unlucky) sample. `spread` near `1.00x` means the trials agreed closely;
  a wide spread (e.g. `2.11x`) means read the ratio-vs-pcrec column with
  caution — differences smaller than the spread are not distinguishable
  from noise. A DNF or error on *any single trial* fails that whole
  engine+case measurement, reported as `status=dnf`/`error` exactly as a
  single-shot failure would be — a flaky run is a result, never silently
  retried past or averaged away.
- **pcrec always measured first.** Every case previously ran pcrec, then
  pcre2-interp, then pcre2-jit, then python-re, in that fixed order, every
  single time — whichever engine runs first in a process-scheduling
  environment systematically pays or benefits from cold-cache/cold-frequency
  effects (direction depends on the box), and pcrec paid or benefited from
  that on every case. Engine order is now **rotated per trial**: trial `i`
  starts the engine list at index `i mod N` (N = number of engines active
  for that case) and wraps around, so across `BENCH_TRIALS` trials every
  engine leads roughly once. This is a genuine rotation across trials, not
  a one-time shuffle, and it only changes invocation *order* — it never
  changes which engines run for a case or which result gets attributed to
  which engine.

The `spread` column and the per-engine `value` (median) both come from the
same `BENCH_TRIALS`-trial set; `secs` in the TSV is that same median. The
one-shot `iters=1` baseline call used for the pre-timing agreement check is
a separate call from the timed trials (also pinned) — its own timing is no
longer reused as a measurement even when it already cleared `TARGET_SECS`,
so a genuine independent-process spread is always available.

Machine context output (streamed header and the markdown report's
"Machine context" table) now also records: whether pinning was actually
applied and how (`taskset` only vs `taskset`+`chrt`, or `none` if `taskset`
itself is unavailable/unprivileged), the trial count, the CPU governor and
turbo state for the pinned core, and the load average — R2's complaint was
partly that machine state wasn't captured alongside the numbers it affects.

## Engines measured

| engine | what it is | JIT/AOT? |
|---|---|---|
| `pcrec` | the generated matcher for this pattern, compiled `gcc -O2` | AOT-specialized native code |
| `pcre2-interp` | PCRE2 8-bit, `pcre2_compile_8` + `pcre2_match_8` loop | general backtracking interpreter |
| `pcre2-jit` | PCRE2 8-bit, `pcre2_jit_compile_8` + `pcre2_jit_match_8` loop | runtime-JIT native code |
| `python-re` | python3 `re` module, bytes pattern, compiled once | general backtracking interpreter (CPython's own) |

### Why dlopen for PCRE2 (`eng_pcre2.c`)

This box has the PCRE2 8-bit *runtime* library (`libpcre2-8-0`, providing
`libpcre2-8.so.0.*`) but not the `-dev` package: no `pcre2.h`, no
unversioned `.so` symlink, no pkg-config file. `eng_pcre2.c` reuses the
technique already established in `tests/fuzz/pcre2_oracle.c`: hand-declare
the small stable slice of the PCRE2 8-bit ABI it needs (opaque struct
pointers + extern prototypes) and `dlopen()`/`dlsym()` the library at
runtime. The `PCRE2_CONFIG_*` and `PCRE2_JIT_COMPLETE` constants it uses
are not guessed from a header memory: `PCRE2_CONFIG_JIT=1` and
`PCRE2_CONFIG_VERSION=11` were confirmed empirically against this box's
actual `libpcre2-8.so.0` (10.46) with a throwaway `ctypes` probe before
being hand-declared in the C source; `PCRE2_JIT_COMPLETE=1` is the
well-known stable value used by every PCRE2 JIT caller.

### PCRE2 JIT availability

`compare.sh` checks JIT availability **before** running any case, at two
levels:

1. **Library-level**: does this PCRE2 build export `pcre2_jit_compile_8`
   at all, and does a JIT-compile of a trivial pattern actually succeed?
   (`eng_pcre2 probe` — JIT can be compiled out of a PCRE2 build.) If
   unavailable at this level, the `pcre2-jit` column is omitted from
   *every* case, not just noted as N/A.
2. **Per-pattern**: even when the library supports JIT in general, a
   specific pattern shape can fail to JIT-compile. `eng_pcre2 jit` reports
   `status=jit_unavailable` for that one case if so, and it's omitted from
   that case's row without affecting the others.

## Methodology

- **Identical bytes.** One subject buffer per case; every engine searches
  the exact same bytes, whole-buffer leftmost search per iteration,
  `startpos` always 0.
- **Agreement before timing.** Every engine runs once (this doubles as the
  calibration baseline, see below — no wasted subprocess launch) before
  any timing loop. The reference/oracle is `pcre2-interp` (this project's
  established oracle everywhere else — see `tests/fuzz/pcre2_oracle.c`),
  with `python-re` as a fallback reference if `pcre2-interp` itself didn't
  finish within `RUN_TIMEOUT`. A case where an engine's single-call
  verdict (match/nomatch + span) disagrees with the reference is marked
  **INVALID** and is **not timed** — never silently dropped. Check
  `docs/dev/upstream_issues.md` first before assuming an INVALID case is a
  pcrec bug; it might be a known other-engine divergence.
- **A single engine's DNF never kills the case.** Every engine's baseline
  is attempted independently; a DNF or error on ANY one engine (reference
  or not) is recorded as that engine's own row (`status=dnf`, value
  `DNF>RUN_TIMEOUTs`) and does not stop the other engines from being
  measured. This matters most for case (e) (`a*b` over 8 MB of all-`a`,
  the R1 A-2 pathological shape): a naive backtracking interpreter with no
  JIT can genuinely be quadratic on this input, just like the *old* pcrec
  emitter was — `pcre2-interp` (and often `python-re`) simply not
  finishing in `RUN_TIMEOUT` is real data (this is precisely the shape
  pcrec's DFA architecture exists to avoid), not a mechanical failure, and
  earlier revisions of this script wrongly treated it as the latter,
  discarding pcrec's best result along with the failed engine's.
- **Oracle DNF specifically.** If *neither* `pcre2-interp` nor `python-re`
  (the two possible reference engines) returns a verdict within
  `RUN_TIMEOUT`, the case as a whole is marked **UNVERIFIED** rather than
  INVALID or discarded: pcrec's own result is still measured and reported
  standalone, clearly labeled as unverified. When exactly one of the two
  finishes, agreement is checked against whichever one did, and the DNF'd
  one is just another `status=dnf` row. The one engine that's truly
  mandatory for a case to proceed at all is `pcrec` itself — if it fails
  to run, that's a genuine harness problem, not a result.
- **Early-match honesty guard.** MB/s is computed as
  `buffer_bytes / wall_time`, which is only a genuine scan-rate figure if
  the engine actually had to look at most of the buffer. When the
  reference engine's leftmost match ends before 80% of the buffer length,
  every engine's MB/s in that case is inflated by the same early-exit
  effect (less work happened than the byte count implies) — `compare.sh`
  detects this from the reference engine's match span and appends an
  explicit note (`early match at byte N of M (X% of buffer scanned) --
  MB/s reflects early exit, not steady-state scan rate; compare within
  this case's rows only, not across cases`) to that case's verdict, in
  both the streamed log and the markdown report's case-matrix table. This
  is a **within-case, cross-engine** comparison caveat, not a per-engine
  correction: ratios between engines in the same (flagged) case are still
  meaningful, since all of them paid the same early-exit shortcut; the
  absolute MB/s number just shouldn't be read as "how fast this engine
  scans 8 MB" the way an un-flagged case's number can be.
- **Auto-scaled iterations.** Each engine's `iters=1` baseline call
  supplies a per-engine time-per-call estimate, used to compute an
  iteration count targeting at least `TARGET_SECS` (default 0.3s) of wall
  time (clamped to `iters=1` if the baseline alone already cleared it).
  That target iteration count is then run `BENCH_TRIALS` times (see
  "Measurement rigor" above) — the baseline's own timing is calibration
  input only, never itself reused as the reported measurement. An engine
  whose *baseline* already failed to finish (DNF/error) is never entered
  into the trial loop — a call that didn't finish at `iters=1` within
  `RUN_TIMEOUT` would only be more likely to time out again at a larger
  count, for no new information.
- **Compile time excluded from every measurement.** See "Fairness" below.
- **MB/s (or ns/call) per engine, a ratio column, and a spread column.**
  `value` is the median across `BENCH_TRIALS` trials; `spread` is that same
  trial set's max/min ratio. For throughput cases, the ratio is
  `pcrec MB/s / best-other-engine MB/s` (>1 means pcrec is faster). For the
  one latency case (short-subject regime, case i), the ratio is
  `best-other-engine ns/call / pcrec ns/call` (again >1 means pcrec is
  faster) — same sign convention, since for that metric lower is better.

## Fairness notes (what each engine's measurement includes/excludes)

- **pcrec**: AOT-specialized native code. Compile time (`pcrec` itself
  compiling the pattern to C, then `gcc -O2` compiling that C to a binary)
  is entirely excluded from every timed measurement — by design, this is
  pcrec's whole model: pay the compile cost once at build time, in
  exchange for the fastest possible per-call matching after that. A
  real-world caller who recompiles the pattern on every single search
  would not see these numbers; a caller who compiles once and searches
  many times (the normal use case for a compiled regex, and the one every
  other engine here is also measured under) does.
- **pcre2-jit**: runtime-JIT native code. `pcre2_jit_compile_8` happens
  once, before the timed loop, exactly like `pcre2_compile_8` for the
  interpreter and exactly like pcrec's own compile step — JIT-compile time
  is excluded from the timed loop for the same reason pcrec's build-time
  compile is.
- **pcre2-interp / python-re**: general-purpose engines, not specialized
  for any one pattern. `pcre2_compile_8` / `re.compile` still happens once
  before the timed loop (same exclusion as above), but the *matching*
  itself is genuinely more general-purpose work than pcrec's or
  pcre2-jit's specialized code path.
- **python-re specifically**: the timed loop calls `compiled.search(...)`
  from Python, so CPython's interpreter dispatch and Python-level
  function-call overhead around the C-implemented `re` engine are
  included in the measurement, not stripped out. This is intentional and
  not a handicap imposed on python-re relative to the others: a real
  Python caller of `re.search` pays exactly this overhead on every call,
  so leaving it in is what makes the comparison meaningful as an
  end-user-facing number for that engine, not just a microbenchmark of its
  C core.

## Case matrix

| case | pattern | shape being stressed |
|---|---|---|
| a | `needleXYZW` | literal, planted at 90% of 8 MB (match, happy path) |
| b | `needleXYZW` | literal, absent (full 8 MB scan, nomatch) |
| c | `(alpha\|beta\|gamma\|delta\|epsilon)` | alternation, absent (full 8 MB scan, nomatch) |
| d | `[a-z]+@[a-z]+\.[a-z]{2,3}` | character classes + bounded repeat, ~100 planted tokens (match) |
| e | `a*b` | R1 A-2 pathological nomatch shape: 8 MB of all-`a` |
| f | `[01]*1[01]{8}` | bounded-repeat DFA-state-heavy pattern, 8 MB random bits (match likely) |
| g | `x{40,60}y` | bounded repeat, one planted run near the end of 8 MB (match) |
| h | `.*=.*` | greedy backtracking stressor, 1 MB single key=value line (match) |
| i | `a(b|c)+d` | short-subject regime: 60-byte subject, measures **ns/call**, not MB/s |
| j | `([01]*)1([01]{8})` | DD-9's capture-bearing sibling of (f): forces the VM+prefilter hybrid, 8 MB random bits (match likely) -- the M4.6b non-regression floor (engine_m4.md 8.5) |
| k | `(a{10,20}){10,50}` | BENCH-VM: the K23/MRL exemplar class, one planted 110-byte hazard-band run near 90% of 8 MB (match) -- floors that the MRL fix (D51 ruling 1) stays cheap |
| l | `([a-z]{2,4}){2,8}b` | BENCH-VM: D51 ADDENDUM's site-dense +8%-cost shape, fixed 40-byte all-`b` subject, measures **ns/call** |
| m | `a(b|c)+d` (captures ON) | BENCH-VM: D53's hybrid-wins-past-~8-12-bytes crossover regime, 100-byte subject, match at offset 40, measures **ns/call** -- case (i)'s sibling with captures left on instead of `--no-captures` |

Subjects are generated deterministically (fixed `random.Random` seed) by
an embedded python3 script in `compare.sh`. Two subjects need active
protection against accidental self-sabotage, not just a hope that random
text won't happen to contain the target: case (c)'s 5 alternation words
are short enough (4–7 letters) that random lowercase text has a
non-negligible chance (roughly 1 expected occurrence, combined, across
8 MB) of accidentally containing one, which would silently turn a
"nomatch" case into a "match" case; `purge_words()` in `compare.sh`'s
subject-generation script actively scans for and mutates away any
accidental occurrence before writing the file. Case (g)'s filler alphabet
deliberately excludes `x` and `y` entirely so no accidental x-run (of any
length) can occur anywhere except the one deliberate plant.

### A subject-design pitfall, fixed (case d)

An earlier revision of case (d) used pure `[a-z]` random lowercase filler
with no `@` or `.` characters anywhere except at the ~100 planted
email-ish tokens. Because of that, `[a-z]+` at the very start of the
pattern could greedily match the *entire* lowercase prefix of the buffer,
back off just enough to let `@` match, and land on the **first** `@` in
the whole buffer — which is the first planted token, wherever it is. All
four engines agreed on this (it was correct leftmost-match behavior, not a
bug), but it meant the match's start offset was always `0`, not the
position of the first planted token, and the measured MB/s was inflated
because so little of the buffer actually needed scanning before the
engine could start trying to satisfy the rest of the pattern — not
representative of how this pattern behaves on real (mixed) text.

Fixed by `rand_wordy()` in `compare.sh`'s subject-generation script: case
(d)'s filler is now space-separated "words" of 3–12 lowercase letters with
an occasional digit run, instead of one unbroken run of `[a-z]`. Every
`[a-z]+` run outside the deliberately planted tokens is now bounded to at
most 12 bytes, so the leftmost match genuinely lands at the first planted
token, and the case now measures what it was meant to: scanning through a
realistic amount of text before finding a token. (The general lesson —
watch what a pattern's own metacharacters can do to a naive filler
alphabet, not just whether the filler could accidentally spell out a
literal target — applies to any future case using an unbounded repeat
like `+` or `*` at the start of the pattern.)

## Adding a case

1. Add a subject-generation block to the embedded python3 script in
   `compare.sh`'s `== SUBJECTS ==` section, writing to `$subj_dir/<name>`.
   If the pattern must NOT match anywhere outside a deliberate plant (or
   must not match at all), actively verify that — don't just assume random
   text won't collide; see case (c)'s `purge_words()` and case (g)'s
   restricted filler alphabet above for two different techniques.
2. Add entries to `CASE_IDS`, `CASE_DESC`, `CASE_PATTERN`, and
   `CASE_SUBJECT` in the `== Case matrix ==` section. If the case measures
   per-call latency rather than throughput (a short subject where MB/s
   isn't a meaningful number), add it to `CASE_METRIC` with value
   `latency` — see case (i).
3. Confirm the pattern actually compiles on pcrec's current base tier
   before adding it (`build/pcrec -p rx -o /tmp/x.c -- 'PATTERN'`) — this
   suite is about comparing performance on patterns pcrec supports, not
   about coverage (that's `tests/harness/`'s job; see the `esc_modules`
   table in `src/parse/parse.c` for what's implemented on the base tier).
4. Nothing else needs to change — `process_case` in `compare.sh` is
   pattern-agnostic and drives all four engines generically off the case
   matrix.


## Scope disclosure (added after checkpoint review R2)

Read the ratios with these limits in mind — the comparison measures what pcrec
CAN do, which is narrower than what the other engines do:

- **Mostly no capture groups.** Cases (a)-(i) are span-only matching, so
  PCRE2/python are never charged for populating captures in those nine — but
  equally, a large slice of real-world regexes exercise a shape those nine
  cannot represent. Case (j) is the deliberate exception (added M4.6b, DD-9's
  non-regression floor, engine_m4.md 8.5): it has two capturing groups, which
  routes pcrec to the VM+prefilter hybrid rather than the pure DFA the other
  nine take, and every engine pays for populating them there. (Measured on
  the span-only cases: ovector size makes <1% difference, so their omission
  of captures was a scope gap, not a timing thumb on the scale.) BENCH-VM's
  three cases (k)/(l)/(m), added 2026-08-17, are ALSO capture-bearing and ALL
  stamp `ENGM_VM` (see `CASE_EXPECT_ENGINE` in compare.sh) — (j) is no
  longer the sole VM-tier case in this matrix, just the first one.
- **No case-insensitive matching.** pcrec's only option is class expansion
  (`[Nn][Ee]...`), which loses ~11x to PCRE2-JIT's native CASELESS. It still
  beats pcre2-interp (2.8x) and python (7.9x) — and pcre2-interp forced onto
  the same class-expanded pattern is 663x slower than pcrec — but the honest
  headline is that pcrec loses this workload to JIT for want of a feature.
- **"Beats JIT" / "beats interp" are per-pattern-and-size claims**, not a
  ranking: PCRE2 JIT is itself slower than plain interp on some shapes/sizes.
- **Precision**: every reported value is now the median of `BENCH_TRIALS`
  pinned trials (previously single-shot; see "Measurement rigor" above),
  with a `spread` column carrying the max/min ratio across those trials —
  check `spread` before trusting a close ratio; values within the spread of
  1.0 are ties, not wins.
- **Determinism**: subjects are generated from a fixed seed (`random.Random(1729)`).
  A fixed seed only guarantees reproducibility while the draws are consumed in
  a fixed order — keep generation single-threaded and ahead of any worker pool.

## gate.sh — the headline-performance ratchet (M2.11, R2-PR7)

`compare.sh` produces the numbers this project quotes about itself, and until
M2.11 nothing checked them: it printed a table, a human read it, and a
regression in a case nobody happened to look at simply became the new
published baseline.

```sh
bash tests/bench/compare/gate.sh            # run compare.sh, then gate the result
COMPARE_TSV=path bash .../gate.sh           # gate a TSV you already have
UPDATE=1 bash tests/bench/compare/gate.sh   # rewrite the floors from this run
```

`floors.tsv` holds one reference value per case for **pcrec only**. That is a
deliberate choice: the `ratio-vs-pcrec` column moves when PCRE2, python, or
the box changes, and R2-B1 already documented those ratios swinging enough to
flip sign between runs — gating on them would fail for reasons that are not a
pcrec regression, and would bury the ones that are. Absolute per-case values
answer "did WE get slower", which is the only question a ratchet can answer
honestly.

A run fails when a throughput case drops below `reference * GATE_MARGIN`
(default 0.70) or a latency case rises above `reference / GATE_MARGIN`. The
0.70 comes from the measured per-trial spread on the reference box (1.03x to
1.49x, tighter at the median of `BENCH_TRIALS`), so it fires on a real ~1.4x
regression without firing on noise. Tighten it only together with a higher
`BENCH_TRIALS`.

**When the gate fails**, the fix is a diagnosis, not a wider margin. If the
slowdown is a deliberate trade, say so in `docs/dev/dev_journal.md` and regenerate
with `UPDATE=1`. It earned its keep immediately: within an hour of existing it
caught a 43% regression on case (f) that `make test`, the python oracle, and
the fuzzer were all green on, because the regression was behaviour-preserving.

**Caveat — the floors are machine-specific.** They were captured on the
development box named in the results snapshot. On different hardware,
regenerate them (`UPDATE=1`) and treat that as re-baselining rather than as a
comparison against the recorded numbers; a cross-machine comparison of these
absolute values is meaningless. This is the main thing standing between
`gate.sh` and CI use.

**Snapshot safety.** `compare.sh` names its report `results-<host>-<date>.md`,
so two runs on one day used to overwrite each other — including the annotated
baseline other documents cite. It now writes `-2`, `-3`, ... instead unless
`REPORT_FORCE=1`.

**Report header is now conditioned on measured load, not always "provisional".**
The markdown report used to open with a hardcoded
`# ... -- PROVISIONAL (load-compromised)` title and warning paragraph on
*every* run, regardless of whether the box was actually busy — actively
misleading once pinning/`BENCH_TRIALS`/`spread` were in place, since the
report separately surfaces load, governor, and turbo anyway. `compare.sh` now
compares the 1-minute load average against the same `LOAD_LIMIT` threshold
`tests/bench/run_bench.sh`'s `LOADED`/`INCONCLUSIVE` gate uses
(`max(2.0, cores/2)`, overridable via `LOAD_LIMIT`) and picks one of two
honest headers:

- **Loaded** (1-min load > `LOAD_LIMIT`): keeps the `PROVISIONAL
  (load-compromised)` title and warning, now naming the actual load figure
  and threshold instead of asserting it unconditionally, and noting that
  pinning + the trial median narrow (but do not eliminate) load
  contamination.
- **Quiet** (1-min load <= `LOAD_LIMIT`): a plain title with no provisional
  caveat, stating that absolute MB/s/ns-call figures — not just the
  cross-engine ratios — should be trustworthy.

The "Machine context" table also gets a `busy-box verdict` row spelling out
which branch fired and the numbers behind it.
