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
- **Oracle DNF is a result, not a harness failure.** If *neither*
  `pcre2-interp` nor `python-re` returns a verdict within `RUN_TIMEOUT`
  (this genuinely happens — see case (e) below), the case is marked
  **UNVERIFIED** rather than discarded: pcrec's own result is still
  measured and reported standalone, clearly labeled as unverified, and the
  oracle timeout itself is reported as data (a backtracking engine
  genuinely failing to finish a catastrophic-backtracking-shaped input in
  90+ seconds is exactly the kind of result this suite exists to surface).
  The one engine that's truly mandatory for a case to proceed at all is
  `pcrec` itself — if it fails to run, that's a genuine harness problem.
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

### A subject-design caveat worth knowing about (case d)

Case (d)'s filler text is pure `[a-z]` random lowercase with no `@` or `.`
characters anywhere except at the ~100 planted email-ish tokens. Because
of that, `[a-z]+` at the very start of the pattern can greedily match the
*entire* lowercase prefix of the buffer, back off just enough to let `@`
match, and land on the **first** `@` in the whole buffer — which is the
first planted token, wherever it is. All four engines agree on this (it's
correct leftmost-match behavior, not a bug), but it means the match's
start offset is `0`, not the position of the first planted token, and the
measured MB/s is inflated because so little of the buffer actually needs
scanning before the engine can start trying to satisfy the rest of the
pattern. A future revision should use a mixed-character filler (letters +
digits/punctuation/spaces, i.e. not exclusively `[a-z]`) so `[a-z]+` runs
stay naturally short outside the planted tokens, making this case a
genuine "scan a lot of data before finding a token" measurement instead of
an accidental best-case one.

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
