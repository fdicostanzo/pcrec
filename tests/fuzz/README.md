# tests/fuzz — PCRE2-oracle differential fuzzer

Plan step M2.5. Promotes the ad-hoc tool the R1 semantics critic built in
their session scratchpad (a hand-declared libpcre2-8 ABI oracle + a
generator/comparator script) into a committed, repeatable tool. See
`docs/dev/reviews/2026-08-09-m1.md` ("Critic: semantics") for the checkpoint
that found this worth keeping, and the triage summary's "PCRE2-oracle
fuzzing pulled forward from M7 (M2.5)" line.

This is a **differential fuzzer**, not a pass/fail regression suite: it
generates random patterns and subjects, runs both `pcrec` and real PCRE2 on
them, and reports where they disagree. It is run manually or at
checkpoints (`make fuzz`), **not** as part of `make test` — a clean run
today says nothing about tomorrow's random seed, and a failure here needs
human triage (see "Triaging a divergence" below), unlike a base-tier
regression which is an unconditional pass/fail gate.

## Files

- `pcre2_oracle.c` — a minimal PCRE2 8-bit CLI oracle. Hand-declares the
  slice of the PCRE2 ABI it needs and loads `libpcre2-8.so.0` at runtime
  with `dlopen`/`dlsym` (see the file's header comment for why: this box
  has the PCRE2 8-bit runtime but no `-dev` package, so there's no
  `pcre2.h`, no unversioned `.so` symlink, and no pkg-config file — direct
  `#include <pcre2.h>` / `-lpcre2-8` are both unavailable). Usage:
  `pcre2_oracle 'PATTERN' <subject-file> [startpos]`, prints `match S E` /
  `nomatch` / `cerr <code>` / `mlimit <code>` (see below).
- `fuzz_driver.c` — a small driver template for pcrec-generated matchers,
  used only by this fuzzer. Deliberately **not** a reuse of
  `tests/harness/driver.c` (which the base-tier harness owns and may
  change shape independently): this one reads its subject from a file
  (not argv) and accepts an optional `startpos`, mirroring
  `pcre2_oracle`'s CLI so the two are directly comparable.
- `fuzz.py` — the generator + comparator + runner. See its module
  docstring and the `EXCLUDED FROM GENERATION` comment block for the full
  rationale of what's deliberately not generated and why.
- `failures/<timestamp>/NNNN_<kind>/` — repro bundles written by a run that
  found divergences (see below). Not committed test fixtures — regenerated
  by every divergent run; safe to delete between sessions.

## Running

```sh
make fuzz                                            # default: seed 1, 300 patterns, 15 subjects/pattern
python3 tests/fuzz/fuzz.py                            # equivalent, no args
python3 tests/fuzz/fuzz.py --seed 2 --patterns 500 --subjects 20
python3 tests/fuzz/fuzz.py --seed 1 --keep             # keep the working dir (path printed to stderr)
```

Deterministic: `--seed N` (default 1) fully determines the patterns and
subjects generated — the same seed always reproduces the same run.
Exit code is `0` iff zero accept/reject divergences and zero content
divergences were found (the DFA state-cap bucket and oracle-inconclusive
count do **not** affect the exit code — see below). `--jobs N` controls
compile/run parallelism (default: `os.cpu_count()`).

Environment variables (same names as `tests/harness`, see `docs/testing.md`):
`PCREC` (default `build/pcrec`), `CC` (default `gcc`), `GENCFLAGS` (default
`-O0 -std=gnu11` — deliberately unoptimized here for compile speed, unlike
the harness's `-O1 -Wall -Wextra -Werror`; this tool is hunting for
semantic divergences, not compiler warnings).

A default run (300 patterns) takes a few seconds on this box (the dominant
cost used to be recompiling the driver from source for every pattern; see
"Performance" below for the fix that removed that).

## What gets generated

Random base-tier patterns: literals, `.`, character classes (including
negation and ranges, using only forms already verified accepted by pcrec —
see `tests/base/classes.rxt`), alternation, greedy/lazy `* + ? {m,n}`
(counts kept `<= 30`), capturing and non-capturing groups, and `^`/`$`
atoms (including mid-pattern `$`, fully supported since the R1 S-C1 fix).
Subjects: random bytes over each pattern's own literal alphabet plus
newlines and high bytes (0-120 bytes), and "derived" subjects that embed an
approximate matching fragment of the pattern (see `sample()` in fuzz.py) —
a best-effort bias toward interesting subjects, not a correctness
mechanism (both engines always run on the exact same bytes regardless of
how the subject was constructed).

## Excluded from generation (known tooling divergences)

Three pattern shapes are deliberately never generated because they're
already-known, already-understood gaps that would otherwise dominate every
run's divergence list. Full rationale and verified examples are in
`fuzz.py`'s `EXCLUDED FROM GENERATION` comment block; summary:

1. **Possessive quantifiers** (`a++`, `a*+`, `a{m,n}+`) and **atomic
   groups** (`(?>...)`) — pcrec rejects them ("requires module
   'atomic-groups'" — not yet implemented); PCRE2 accepts. An
   accept/reject mismatch, but an expected one (unimplemented module, not
   a bug).
2. **`\x{...}` brace hex escapes** — pcrec rejects ("requires module
   'unicode-props'" — not yet implemented); PCRE2 accepts. Same rationale
   as (1). The generator uses only the supported `\xHH`/`\xH` form.
3. **`{,n}` / `{,}` quantifier forms** (no digit before the comma) — **not
   a live divergence.** `a{,3}` vs subject `"aaaa"` used to be pcrec
   `nomatch` / PCRE2 `match 0 3` (pcrec read the brace text as a **literal
   string**); this was **RESOLVED in the M2-era session** (see `fuzz.py`'s
   `EXCLUDED FROM GENERATION` block and `try_quant` in
   `src/parse/parse.c`, which has treated `{,n}` as `{0,n}` — matching
   PCRE2 10.43+ — ever since, pinned in
   `tests/base/fuzz_regressions.rxt`). Bare `{,}` (no digits at all) stays
   literal in pcrec, and PCRE2 agrees with that reading too — it's python
   `re` that diverges on the bare form, tracked separately in
   `docs/dev/upstream_issues.md`. Generation of `{,n}` stays off here only
   because the generator's `QUANTS` list predates the fix, not because of
   any remaining gap; safe to add as a generated form in a future fuzzer
   change.

**Not excluded** (checked and confirmed no longer needed): quantified bare
anchors (`^*a`, `a$*`, `${1,2}`, ...). Since the R1 S-M1 fix, pcrec rejects
these exactly like PCRE2 (error "quantifier does not follow a repeatable
item" / PCRE2 code 109) — verified across six forms. The generator
produces these naturally; both engines are expected to reject in lockstep.

## Output buckets

A run's summary breaks results into:

- **both accept / both reject** — agreement, no action needed.
- **accept/reject divergences** — one engine accepts a pattern the other
  rejects. Always actionable (after excluding the three known categories
  above); written to `failures/`.
- **DFA state-cap hits** — pcrec rejects with "pattern too complex for the
  DFA engine" or "NFA exceeds N states"; PCRE2 accepts. **Not** treated as
  a divergence and **not** written to `failures/`. This is checkpoint
  review R1 finding A-3 (`docs/dev/reviews/2026-08-09-m1.md`) doing its
  documented job: the M1 pipeline has hard complexity caps at NFA
  construction and DFA determinization and no VM fallback yet (planned
  M4), so sufficiently nested/bounded-repeat-heavy legal patterns are
  correctly rejected by pcrec while PCRE2's backtracking engine, which has
  no such structural limit, accepts them. The generator's use of nesting
  depth + up-to-30 bounded repeats + alternation makes this fire on
  roughly 2-3% of generated patterns; that's expected, not a regression.
- **oracle-inconclusive (mlimit)** — PCRE2's own match-time safeguard
  tripped (`pcre2_match_8` returned some negative code other than `-1`
  `PCRE2_ERROR_NOMATCH` — e.g. `-47` "match limit exceeded"). This is
  **not** a match/no-match verdict, so it's never compared against
  pcrec's output. See "Finding 1" below for why this exists and matters.
- **content divergences** — both engines accepted the pattern, both ran to
  a real verdict, and they disagree on match/nomatch or the exact span.
  Always actionable; written to `failures/`.

## Triaging a divergence

1. Read the bundle in `failures/<timestamp>/NNNN_<kind>/`: `pattern.txt`,
   `subject.hex` / `subject.bin` (raw bytes — content bundles only),
   `outputs.txt` (both engines' outputs side by side).
2. Reproduce independently of the fuzzer before trusting it — build the
   pattern with `pcrec` directly, compile against `fuzz_driver.c`, and run
   `pcre2_oracle` on the same subject file by hand. The fuzzer's own
   plumbing (thread pool, temp dirs) is one more thing that could be wrong;
   don't skip this step.
3. Try to minimize: strip characters from the pattern and subject one at a
   time, re-checking after each removal, until neither can shrink further
   without losing the divergence. A minimal repro (ideally under ~20
   characters total) is far easier to reason about and to hand to whoever
   owns the engine change. Both findings below were minimized this way.
4. Check the PCRE2 return code directly if the verdict is surprising —
   `pcre2_oracle` already distinguishes genuine no-match (`-1`) from a
   safeguard trip (`mlimit`), but if you're extending this tool, don't
   assume any negative `pcre2_match_8` return means "no match".

## Two findings from this session's runs (seed 1 and seed 2, default size)

Both were minimized by hand per the process above; see the git history /
build-session transcript for the delta-debugging script used.

**Finding 1 — `pcre2_oracle`'s original bug, now fixed: PCRE2 match-limit
errors were being misread as "no match".** First content-divergence
report (before the fix below) was pattern `(((b{0,})){2,}){0,}$` against a
9-byte run of `'b'` plus one trailing non-`'b'` byte: pcrec reported a
trivial zero-width match at the end of the subject; the oracle reported
"nomatch". Direct inspection of `pcre2_match_8`'s return code showed
`-47` ("match limit exceeded"), not `-1` ("no match") — PCRE2's own
backtracking-budget safeguard tripped on this deliberately
catastrophic-backtracking-shaped nested-quantifier pattern before it could
determine an answer. pcrec's DFA has no backtracking and hit no such
limit, so its answer is the *only* one of the two that's actually a
verdict. **This is not a pcrec bug** — arguably it's the DFA architecture
working exactly as designed on a pattern shape that's pathological for a
backtracking engine. Fixed in `pcre2_oracle.c`: `rc == -1` prints
`nomatch`; any other negative `rc` prints `mlimit <code>` and is treated
as inconclusive by `fuzz.py`, never compared to pcrec's output. Both
mandated runs (seed 1, seed 2) recorded zero `mlimit` hits after the fix.

**Finding 2 — tracked, not yet actioned: PCRE2's start-anchoring optimizer
appears to over-trigger on a `{0}`-quantified alternation containing `^`.**
Minimized repro: pattern `(()|^){0}[b]` against subject `"0b"` — pcrec
reports `match 1 2` (the `[b]` at offset 1); PCRE2 reports `nomatch` (a
genuine `-1`, confirmed via direct return-code inspection, not another
`mlimit` case). Isolated by testing each piece independently:
  - `(^){0}[b]` (anchor alone, no alternation) → **both agree**, match 1 2.
  - `(()|^){0}[b]` (anchor inside an alternation) → **diverges**.
  - `(()|a){0}[b]` (non-anchor alternative in the same shape) → **both
    agree**, match 1 2.
  - `(()|^){0,0}[b]` (`{0,0}` instead of `{0}`) → **diverges identically**.
  - When the actual match target is moved to offset 0 (subject `"b0"`
    instead of `"0b"`), both agree — consistent with PCRE2 restricting its
    search to offset 0 only.

Reading: `{0}` means this group can *never* actually execute — it
contributes nothing to any real match. pcrec correctly ignores its
contents entirely for match purposes. PCRE2 appears to still run its
static "can this pattern only match at the start of the subject" analysis
over the `^` inside the never-executed branch, concluding the whole
pattern is start-anchored, and restricting its search to offset 0 — where,
in this repro, there's nothing to match, so it reports `nomatch` even
though a real match exists later in the subject. This reads as a PCRE2
optimizer quirk (or at least a documented-nowhere edge case) rather than a
pcrec bug: pcrec's answer matches the pattern's declared semantics: `{0}`
exact-count groups are dead code, and dead code shouldn't influence
anchoring analysis. Flagged to the team rather than fixed here — this
fuzzer's job is to surface it precisely, not to adjudicate which engine
"should" change. Given how contrived the triggering shape is (a
`{0}`-exact-count group wrapping an alternation with an anchor branch is
not something any real pattern author would write), this is low priority
either way. Not added to the exclusion list — it's a genuine finding, not
generator noise, and only fired on 1 of 2 mandated runs (8 divergent
subject pairs, all the same pattern shape, out of 1905 both-accept pairs
compared across the two runs) — rare enough not to need suppressing.

## Performance

The dominant per-pattern cost is compiling the pcrec-generated matcher.
`fuzz.py` avoids recompiling `fuzz_driver.c` from source for every
pattern: since every pattern is compiled with a fixed prefix (`rx`), the
generated `gen.h` (the `rx_span` typedef and `rx_search` prototype) is
byte-for-byte identical across every pattern (only a leading comment
differs). `fuzz.py` compiles `fuzz_driver.c` to a `.o` once at startup
against a throwaway pattern's header, then for every subsequent pattern
only runs `pcrec` (generate) → `gcc -c` (compile the small generated
matcher) → link against the pre-built driver object — no driver
recompilation, ever. Pattern compilation and subject runs are also
parallelized across `--jobs` worker threads (subprocess calls release the
GIL while waiting on the child process). A default run (300 patterns, 15
subjects each ≈ 1500-2000 comparisons after accounting for rejects) takes
roughly 3-5 seconds on this box.
