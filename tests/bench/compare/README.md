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
default 0.3s), `RUN_TIMEOUT`, `PCREC_TIMEOUT`, `BUILD_TIMEOUT`.

Output: a streamed per-case log, a consolidated human-readable results
table, a machine-readable TSV block, and a full copy of both written to
`tests/bench/compare/results-<hostname>-<yyyymmdd>.md`.

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
  `docs/upstream_issues.md` first before assuming an INVALID case is a
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
  supplies a per-engine time-per-call estimate; if that's already
  `>= TARGET_SECS` (default 0.3s) the baseline measurement is reused
  as-is, otherwise one additional run is made with a scaled-up iteration
  count so the reported measurement accumulates at least `TARGET_SECS` of
  wall time. An engine whose *baseline* already failed to finish
  (DNF/error) is never retried at a larger iteration count — a call that
  didn't finish at `iters=1` within `RUN_TIMEOUT` would only be more
  likely to time out again at a larger count, for no new information.
- **Compile time excluded from every measurement.** See "Fairness" below.
- **MB/s per engine, plus a ratio column.** For throughput cases, the
  ratio is `pcrec MB/s / best-other-engine MB/s` (>1 means pcrec is
  faster). For the one latency case (short-subject regime, case i), the
  ratio is `best-other-engine ns/call / pcrec ns/call` (again >1 means
  pcrec is faster) — same sign convention, since for that metric lower is
  better.

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

- **No capture groups.** pcrec compiles span-only matching today. Every case
  here avoids captures, so PCRE2/python are never charged for populating them
  — but equally, a large slice of real-world regexes cannot run on pcrec at
  all yet. (Measured: ovector size makes <1% difference on these patterns, so
  this is a scope gap, not a timing thumb on the scale.)
- **No case-insensitive matching.** pcrec's only option is class expansion
  (`[Nn][Ee]...`), which loses ~11x to PCRE2-JIT's native CASELESS. It still
  beats pcre2-interp (2.8x) and python (7.9x) — and pcre2-interp forced onto
  the same class-expanded pattern is 663x slower than pcrec — but the honest
  headline is that pcrec loses this workload to JIT for want of a feature.
- **"Beats JIT" / "beats interp" are per-pattern-and-size claims**, not a
  ranking: PCRE2 JIT is itself slower than plain interp on some shapes/sizes.
- **Precision**: single-shot numbers on this harness carry run-to-run noise of
  up to ~30% on short-latency cases; ratios near 1.0 are ties, not wins. The
  harness does not yet pin CPUs or control the frequency governor (plan M2.9).
- **Determinism**: subjects are generated from a fixed seed (`random.Random(1729)`).
  A fixed seed only guarantees reproducibility while the draws are consumed in
  a fixed order — keep generation single-threaded and ahead of any worker pool.
