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
  `pcre2_oracle 'PATTERN' <subject-file> [startpos]`, prints
  `match S E [g1s g1e ...]` / `nomatch` / `cerr <code>` / `mlimit <code>` /
  `ovtoosmall <code>` (see below). **[M4.7d]**: the `match` line carries
  every capture-group span, not just the whole match — see "Capture-group
  span comparison" below.
- `pcre2_abi.h` — the hand-declared PCRE2 8-bit ABI slice + dlopen loader,
  shared with `tests/registry/pcre2_check.c`. **[M4.7d]** added
  `pcre2_pattern_info_8` (capture-group count) and `pcre2_get_ovector_count_8`.
- `fuzz_driver.c` — a small driver template for pcrec-generated matchers,
  used only by this fuzzer. Deliberately **not** a reuse of
  `tests/harness/driver.c` (which the base-tier harness owns and may
  change shape independently): this one reads its subject from a file
  (not argv) and accepts an optional `startpos`, mirroring
  `pcre2_oracle`'s CLI so the two are directly comparable. **[M4.7d]**:
  prints every `caps[k]` pair (`k` in `[0, rx_info.ncaps)`), matching
  `pcre2_oracle`'s own multi-pair format.
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

## Two-tier posture: the `make test` gate vs. the at-scale campaign ([M4.7e])

Everything above (`make fuzz`, an arbitrary `--seed`) stays a
manual/checkpoint tool for the reason already given: a clean run at a seed
nobody pinned says nothing about the next one, and a failure needs human
triage before it means anything. **That reasoning does not apply to a
PINNED seed** — the same seed always reproduces the same corpus (see
"Deterministic" above), so a fixed-seed run is exactly as reproducible as
any other differential in this tree.

`tests/fuzz/run_capturediff_gate.sh` (`make test-capturediff`, part of
`make test` proper) is that fixed-seed slice: fuzz.py's own defaults
(seed=1, 300 patterns, 15 subjects), asserting fuzz.py's own
zero-divergence exit code. It exists to catch a REGRESSION against
divergences already known to be absent, not to find new ones — finding new
ones is still the at-scale campaign's job (`tests/fuzz/campaigns/`, run
manually across many seeds at checkpoints, same posture as `make fuzz`
itself, just bigger and logged). The gate probes libpcre2 presence itself
(builds `pcre2_oracle.c`, calls its own `--version`) and SKIPS loudly
(PC-3's pattern, `tests/registry/run_registry_tests.sh`) instead of letting
fuzz.py's own oracle plumbing fail hard, which is the right policy for a
manual dev tool but wrong for a `make test` section on a libpcre2-less box.

## What gets generated

Random base-tier patterns: literals, `.`, character classes (including
negation and ranges, using only forms already verified accepted by pcrec —
see `tests/base/classes.rxt`), alternation, greedy/lazy `* + ? {m,n}`
(counts kept `<= 30`), capturing and non-capturing groups, and `^`/`$`
atoms (including mid-pattern `$`, fully supported since the R1 S-C1 fix).
**[M4.7d]**: `CAPTURE_TEMPLATES` (fuzz.py) additionally injects, at ~20%
density, dedicated capture-bearing shapes — quantified capturing groups,
groups wrapping alternation, nested groups, nullable/optional group bodies —
the specific combinations that exercise cross-iteration retention and
empty-final-iteration overwrite (match_api_m4.md's [M4.5d] addendum), which
the unbiased grammar rolls far less often than "some capturing group exists
somewhere." See "Capture-group span comparison" below.
Subjects: random bytes over each pattern's own literal alphabet plus
newlines and high bytes (0-120 bytes), and "derived" subjects that embed an
approximate matching fragment of the pattern (see `sample()` in fuzz.py) —
a best-effort bias toward interesting subjects, not a correctness
mechanism (both engines always run on the exact same bytes regardless of
how the subject was constructed).

**FINDING ([M4.7e], 2026-08-17), CLOSED for `classes` the same day it was
found: the differential-gate principle's OPEN half was satisfied (see
docs/testing.md), but its FOCUSED half was VACUOUS for this generator —
measured, not assumed.** fuzz.py passes no `--features` flag, so every
compile in this file (gate slice and at-scale campaign alike) resolves
through `PCREC_DEFAULT_FEATURES` = `"std1"` = `{classes, modifiers}`
(D37/STD1b) — the gate is genuinely open. But at the time of the original
75,000-pattern campaign, `CLASS_ATOMS` was drawn only from base-tier
bracket-class forms already accepted with NO module enabled
(`tests/base/classes.rxt`'s own territory) — none of the classes-module
escapes (`\d \D \s \S \w \W`) or the classes-module POSIX `[:name:]`
delimiter form ever appeared, so the gate being open bought that campaign
nothing: zero of its 75,000 patterns exercised either module's OWN syntax.
Recorded because the distinction between "the gate is open" and "something
walked through it" matters and is otherwise invisible in a summary line
that only reports divergence counts (`tests/fuzz/campaigns/
2026-08-17_m47e_capture_diff.md` carries the original measurement in
full).

**The `classes` half is now fixed**: `MODULE_CLASS_ATOMS` (fuzz.py, next to
`CLASS_ATOMS`) adds `\d \D \w \W \s \S` and two POSIX forms
(`[[:alpha:]] [[:digit:]]`), drawn at a MODEST, named weight
(`MODULE_CLASS_WEIGHT = 0.15` of the existing class-atom branch in
`gen_atom`) rather than merged into `CLASS_ATOMS` outright, so its share of
the corpus is a controllable number, not "however many items are in the
list." Measured in-process (pure generation, no compiles): 37.1% of 3,000
sampled patterns at this weight contain at least one module construct —
comfortably nonzero, the proof the gate is now actually exercised rather
than merely open. A second, smaller addendum batch re-running the campaign
with this generator carries its own row in the campaign log with this
count measured for real (not the in-process sample above).

**`modifiers` stays OUT of scope, deliberately, and is recorded as an owed
cell rather than silently dropped**: no modifiers-module generation exists
anywhere in this file (no `(?i) (?m) (?s) (?x) (?U) (?J) (?a) (?n) (?r)
(?-i) (?^) (?)`). Extending the generator for `modifiers` is homed at
[M7.0] in docs/dev/plan.md ("differential fuzzing vs libpcre2" — M7's own
milestone, not a same-session addendum to [M4.7e]'s capture charter) rather
than done here.

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
  **[M4.7d]**: also absorbs `ovtoosmall` — `pcre2_oracle.c`'s own
  defensive-only "the ovector I sized from this pattern's own capturecount
  turned out too small" case (see "Capture-group span comparison" above),
  not expected to ever fire.
- **content divergences** — both engines accepted the pattern, both ran to
  a real verdict, and they disagree on match/nomatch or the exact span.
  **[M4.7d]**: "the exact span" now means EVERY capture-group span, not
  just the whole match — see "Capture-group span comparison" above for the
  format and the measured PCRE2 unset-group convention behind it. Always
  actionable; written to `failures/`.

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

## Capture-group span comparison ([M4.7d])

Both sides of the differential now compare **every capture-group span**, not
just the whole match. `fuzz_driver.c` prints `caps[k][0] caps[k][1]` for
every `k` in `[0, rx_info.ncaps)`; `pcre2_oracle.c` prints `ov[2k] ov[2k+1]`
for every `k` in `[0, capturecount]`, where `capturecount` is queried fresh
from the just-compiled pattern via `pcre2_pattern_info_8`
(`PCRE2_ABI_INFO_CAPTURECOUNT`, measured value `4` — see
`pcre2_abi.h`'s comment for the three-pattern probe that pinned it, since
this project measures PCRE2 constants rather than reading them off
documentation). Both lines are `"match "` followed by the pairs,
space-separated, index 0 always the whole match. Since group numbering is
shared between the two engines (C9, match_api_m4.md — left-to-right by
opening paren, non-capturing groups don't consume a number), the two lines'
pairs line up positionally with no renumbering step, and **the existing
line-level string comparison in `fuzz.py` (`pr != orr`) needed no change at
all** to start catching capture-span divergences — it was already comparing
full lines, not just a parsed whole-match pair; extending what both sides
*print* was the whole change.

**The unset-group convention — MEASURED, not assumed.** A small probe
(dlopen the same `pcre2_abi.h` machinery, compile `(a)(b)(c)`, `(a)|(b)`,
`(a)|(b)(c)`, `((a)|(b))*`, `(a)(b)?`, size the ovector to `capturecount+1`,
print every pair) established two facts before any oracle code was written:

1. `PCRE2_INFO_CAPTURECOUNT` is opcode `4` — confirmed against three
   patterns with distinct group counts (3, 2, 3), one candidate opcode
   consistent with all three.
2. With the ovector sized to `capturecount+1` pairs, **every group that
   never participated in the match reads back `(PCRE2_SIZE)-1` in BOTH
   offsets** — including groups numbered ABOVE the highest one that did
   participate, not merely ones within `pcre2_match`'s own return-value
   range. Verified: `(a)|(b)(c)` on `"a"` gives `rc=2` but groups 2 and 3
   (both unreached — the `(b)(c)` branch never ran) both read
   `(-1, -1)`, not garbage.

`PCRE2_UNSET` is `~(PCRE2_SIZE)0` — every bit set. Cast to a signed type of
the same width (`ptrdiff_t`, matching `<prefix>_search`'s own D44.2 element
type), that bit pattern IS the literal value `-1`. pcrec's own `PCREC_UNSET` is
`(ptrdiff_t)-1`. **These are the same value, not two conventions requiring a
mapping** — printing both sides with `%td` on a signed cast makes an unset
group read as `-1 -1` on both sides with zero conversion code anywhere in
`pcre2_oracle.c` or `fuzz_driver.c`. This was cross-checked against
match_api_m4.md's [M4.5d] as-built addendum (cross-iteration retention,
empty-final-iteration overwrite) by hand before folding the change in:
  - `((a)|(b))*` on `"ab"` → both engines `match 0 2 1 2 0 1 1 2` (group 2
    keeps its value from the FIRST iteration — the branch it ran in — while
    group 1, the whole-alternation group, and group 3 both reflect the
    SECOND iteration; retention, not "unset because it didn't run last").
  - `(a*)*` on `"aaa"` → both engines `match 0 3 3 3` (the empty final
    iteration's write is a write — group 1 is `(3,3)`, not retained from the
    non-empty iteration that matched `"aaa"`).
  - `(a)|(b)(c)` on `"a"` → both engines `match 0 1 0 1 -1 -1 -1 -1` (groups
    2 and 3, in the branch that never ran, both UNSET).

**Defensive-only bucket, not expected to fire**: `pcre2_oracle.c` sizes its
ovector from the SAME compiled pattern's own `capturecount`, so
`pcre2_match_8` returning `0` ("ovector too small") should be unreachable —
if it ever does happen it prints `ovtoosmall <ngroups>` rather than
crashing, and `fuzz.py` folds it into the existing "oracle inconclusive"
bucket (same reasoning as `mlimit`: not a verdict to compare).

**Generator extension**: `CAPTURE_TEMPLATES` (`fuzz.py`, same
`.format()`-template mechanism as `TRAP_TEMPLATES`) adds ~20% of patterns as
dedicated capture-bearing shapes — quantified capturing groups, groups
wrapping alternation, nested groups, groups with optional/nullable bodies —
because the unbiased grammar produces SOME capturing group often enough but
the SPECIFIC combinations that exercise cross-iteration retention and
empty-final-iteration overwrite (a quantifier directly around a group, or a
group nested inside another quantified group) are a much rarer joint draw.
Subjects for this lane run up to 8 characters (versus the trap lane's 4) so
multi-iteration semantics actually get exercised — a length-1 subject can't
distinguish "this group's value is from its last iteration" from "this
group's value is from its only iteration".

**Validation** (this extension's own build session, both runs against
libpcre2 10.46 2025-08-27): 5 seeds × 500 patterns × 20 subjects (seeds
1–5), foreground — 2,500 patterns generated, 1,435 both-accept, 28,660
subject-pair comparisons; then 3 more seeds × 1,500 patterns × 25 subjects
(seeds 10–12), run as an async background campaign — 4,500 patterns
generated, 2,573 both-accept, 64,325 subject-pair comparisons. Combined: **8
seeds, 7,000 patterns generated, 4,008 both-accept, 92,985 subject-pair
comparisons (every pair now including every capture-group span, not just
the whole match) — 0 content divergences, 0 accept/reject divergences**
across every seed. DFA state-cap hits (the known A-3 limitation, not a
divergence) appeared at their usual ~2-3% rate; a handful of
oracle-inconclusive and step-budget-exhausted cells appeared as usual and
were correctly excluded from comparison, not treated as verdicts.

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
generated `rx_search` prototype (`ptrdiff_t (*caps)[2]`, the [M4.4] FINAL
ABI shape) is byte-for-byte identical across every pattern. `fuzz.py`
compiles `fuzz_driver.c` to a `.o` once at startup against a throwaway
pattern's header, then for every subsequent pattern only runs `pcrec`
(generate) → `gcc -c` (compile the small generated matcher) → link against
the pre-built driver object — no driver recompilation, ever. Pattern
compilation and subject runs are also parallelized across `--jobs` worker
threads (subprocess calls release the GIL while waiting on the child
process). A default run (300 patterns, 15 subjects each ≈ 1500-2000
comparisons after accounting for rejects) takes roughly 3-5 seconds on
this box.

**`RX_NCAPS` is NOT part of what's shared, and this bit a real run.**
`RX_NCAPS` is a per-pattern preprocessor macro (`ngroups+1` on VM
artifacts since [M4.5]; always 1 before that — a DFA-only artifact never
promises more than the whole-match slot), unlike the fixed `rx_search`
signature above. `fuzz_driver.c` used to size its caps array with
`ptrdiff_t caps[RX_NCAPS][2]`, a stack array whose size is baked in at
THIS FILE's own compile time — i.e. from the throwaway one-off pattern's
macro (`RX_NCAPS==1`, no capture groups), not from whatever pattern's
`gen.o` the resulting `driver.o` later gets linked against. Every
group-bearing pattern that reported a match wrote its capture pairs past
that 1-slot array and smashed this driver's own stack (found this
session: 274 of 317 divergences on one run, all `rc=-6`/stack-smashing
aborts against patterns pcrec compiled and matched correctly — the
generated matcher was innocent; sizing the array from the same run against
a right-sized array reproduced the correct verdict). The fix keeps the
shared-driver optimization (it's the dominant cost saver above) but stops
reading `RX_NCAPS` at driver-compile time entirely: `fuzz_driver.c` reads
`rx_info.ncaps` — the [M4.4] reflection struct's `ncaps` field — at
RUNTIME, off whichever artifact it's actually linked against, and
`calloc()`s the caps array to that size. One compiled driver.o, correct
for every pattern, by construction rather than by luck of the throwaway
pattern's shape. `tests/registry/pc4_driver.c` uses the identical
shared-driver trick and had the identical latent bug (dormant only because
its pattern space has no capturing constructs today) — fixed the same way,
same session.

## Step/frame budget policy

Every pattern is compiled with an explicit `--step-budget=N` (see
`fuzz.py`'s `STEP_BUDGET`, overridable via the `STEP_BUDGET` env var)
rather than the bring-up default (`VM_DEFAULT_STEP_BUDGET`,
`src/gen/emit_vm.c`, 1,000,000 — a placeholder pending [M4.6]'s real
calibration). Without this, a sufficiently pathological VM-forced pattern
could spend a million backtrack resumptions and blow past this fuzzer's
own `RUN_TIMEOUT`/`CC_TIMEOUT` clocks — not an engine bug (DD-2/D22: the
step budget is a robustness bound on pathological backtracking, never a
security boundary, never traded against speed), but a harness-clock
collision the M4.6 calibration question arrived at early. A pcrec
`PCREC_ERR_STEPS`/`PCREC_ERR_FRAMES` verdict (`fuzz_driver.c` prints `steps` /
`frames` for these — never `TIMEOUT`, since the budget is what keeps the
matcher itself fast) is reported as its own counted **non-divergence**
class in the summary (`pcrec step-budget exhausted` / `frame-budget
exhausted`) rather than compared against whatever verdict PCRE2's
differently-limited backtracking engine reaches on the same input — the
mirror image of the existing "oracle inconclusive" (PCRE2 match-limit)
bucket. Wiring an equivalent explicit `pcre2_set_match_limit()` call into
the oracle so the two sides trip at directly comparable cost would need a
new ABI declaration + `dlsym` load in `pcre2_abi.h` for one classification
refinement; judged disproportionate against what the non-divergence bucket
already achieves.

Separately, `oracle_run()` (the PCRE2 side) did not used to catch its own
subprocess timeout at all — found during this fix's validation, when a
slow oracle invocation on a large/generated subject killed an entire
multi-thousand-pattern run with an uncaught `TimeoutExpired` traceback.
`oracle_run()` now mirrors `pcrec_run()`'s existing convention and returns
the sentinel `"TIMEOUT"` instead, folded into the same "oracle
inconclusive" bucket as a PCRE2 match-limit trip (both mean "the oracle
produced no usable verdict").
