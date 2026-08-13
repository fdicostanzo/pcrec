# Testing pcrec

pcrec's test suite runs generated C code, not pcrec's internals directly: for
each test pattern, the harness invokes the `pcrec` CLI to generate a matcher,
compiles that matcher with the system C compiler, and runs it against a set
of subject strings, checking the reported match span (or lack of one)
against the expectation encoded in the test file.

## Running the tests

```sh
make test                                  # everything under tests/
bash tests/harness/run.sh                  # the .rxt corpus ONLY (see below)
bash tests/harness/run.sh tests/base        # one component directory
bash tests/harness/run.sh tests/base/quantifiers.rxt   # one file
```

`make test` is NOT equivalent to `run.sh`: it runs SEVEN scripts — the .rxt
corpus, `tests/cli/run_cli_tests.sh`, `tests/reject/run_reject_tests.sh` (the
"never miscompile" mandate, per construct),
`tests/registry/run_registry_tests.sh`, `tests/parse/run_parse_tests.sh`
(PARSE-1: facts the PARSER computes but never emits — see that directory's
CLAUDE.md), `tests/codegen/run_codegen_tests.sh`
(structural assertions that behaviour-preserving optimizations are actually
PRESENT in the emitted C — see that directory's CLAUDE.md), and
`tests/known_fail/run_known_fail.sh` (the ratchet that flags a deferred-bug
regression which has started passing). `run.sh` alone certifies only the first
of the seven.

`make strict` is separate and opt-in: it recompiles every source with
`-Werror`, writes nothing, links nothing, and touches `build/` not at all, so it
is safe to run while `make test` is in flight. It exists because the project
already had a warnings-as-errors gate BY ACCIDENT —
`tests/codegen/run_trie_identity.sh` compiles the whole tree and fails on any
warning, and R7 measured that this accident was for a while the only thing
catching a class of offset bug. Now it is a gate someone chose. Validated the
way any gate should be: adding one unused variable to `src/core/sb.c` leaves
plain `make` succeeding and makes `make strict` fail.

**TWO of the seven can SKIP, and both skips are loud.** `run_parse_tests.sh` is
the second: without libpcre2 it still compares pcrec's branch count against its
independent reference, but the stage that ARBITRATES that reference — libpcre2's
error-127 / error-154 thresholds — prints a SKIP banner instead. The comparison
still runs; what is lost is the outside authority validating the thing pcrec is
compared against. It also prints, on every run, the two properties it
deliberately does NOT assert (depth balance across a returning doorway, and
caseless save/restore), because no code exists that can exercise either yet and
a green run must not be mistaken for coverage of them.

**And the first one.** `run_registry_tests.sh` builds
and runs `tests/registry/pcre2_check.c` (PC-3), which dlopens libpcre2 at
runtime — the only external authority in the suite. Without the PCRE2 8-bit
runtime installed (Debian/Ubuntu `libpcre2-8-0`) it prints three `SKIP:` lines
saying exactly what stopped being checked, and exits 0, because a stranger who
clones this repo must still get a green `make test`. A green run on a box
without libpcre2 is a WEAKER result than a green run with it; the skip lines
are how you tell which one you got.

With no arguments, `run.sh` discovers and runs every `*.rxt` file under
`tests/` (recursively). Arguments may mix individual `.rxt` files and
directories; directories are searched recursively for `*.rxt` files.

The run exits `0` iff every case in every file passed, and `1` otherwise, so
it plugs directly into `make test` / CI.

### Environment variables

| Variable    | Default                    | Meaning |
|-------------|-----------------------------|---------|
| `PCREC`     | `<repo-root>/build/pcrec`  | Path to the `pcrec` binary to test |
| `CC`        | `gcc`                      | Compiler used to build generated code |
| `GENCFLAGS` | `-O1 -std=gnu11`           | Flags passed to `$CC` when compiling generated code |
| `KEEP`      | unset (0)                  | Set to `1` to keep the harness's temp working directory instead of deleting it on exit (path is printed to stderr) |
| `VERBOSE`   | unset (0)                  | Set to `1` to print a line for every *passing* case, not just failures |
| — | — | Per-block `.rxt` directives: `flags i` (caseless) and, since MOD-0.3c, `features <list>` (comma-separated module names passed as `--features`; the spec is validated once per distinct list so a typo is a loud harness failure, never a perr match) |
| `PROCS`     | unset (1)                  | Run N `.rxt` **files** concurrently (each in its own re-invocation with its own temp dir). Summary format and counts are identical to a serial run; the parent hard-fails if any worker vanishes without printing a summary, so a lost worker can never read as a pass. Measured on the project box: full corpus 4m25s serial → 55s at `PROCS=6`. Prefer `TMPDIR=/var/tmp` at higher `PROCS` (`/tmp` is a quota'd tmpfs there) |

Example: testing a debug build with a different compiler and keeping
artifacts around for inspection:

```sh
PCREC=build/pcrec-debug CC=clang KEEP=1 VERBOSE=1 bash tests/harness/run.sh tests/base
```

`tests/mech/run_sabotage_matrix.sh` takes the same `PROCS` variable for
concurrent sabotages (rows merged in listing order, so the matrix stays
byte-identical to a serial run's), and in both modes now guards the matrix
row count against the number of sabotage definitions requested — a sabotage
that produces no row is a loud FATAL, never a silently smaller denominator.
`make bench` deliberately supports no parallelism, in either direction: its
budgets are timing medians (D12/D17) and it gates on load average, so it runs
alone on a quiet box or its numbers mean nothing.

## The `.rxt` format

A `.rxt` file is a flat, line-oriented list of **pattern blocks**. Each block
starts with a `pattern` line and is followed by zero or more expectation
lines (`m`, `n`, or `perr`) that apply to that pattern, until the next
`pattern` line or end of file.

- Blank lines and lines starting with `#` are ignored (comments).
- `pattern <regex>` — starts a new block. `<regex>` is everything after the
  first space on the line, taken verbatim through to the end of the line
  (no quoting, no escaping — write the pattern exactly as PCRE would see
  it).
- `flags <letters>` — compile options for the current block, given after its
  `pattern` line. Only `i` is defined (case-insensitive, `pcrec -i`; OS-1).
  A block with no `flags` line compiles with defaults, and the setting does
  **not** carry to the next block. An unknown letter is a hard error, not a
  silent no-op: a dropped flag would compile a different automaton and the
  block's expectations would then be verified against something nobody asked
  for. `tests/harness/verify_rxt.py` honours the same directive, mapping `i`
  to `re.IGNORECASE | re.ASCII` — the `re.ASCII` is required, since python's
  IGNORECASE otherwise folds Unicode and would disagree with pcrec's
  deliberately ASCII-only fold.
- `features <list>` — enabled feature modules for the current block
  (MOD-0.3c): a comma-separated list of module names exactly as
  `--list-syntax`'s module column spells them, passed to pcrec as
  `--features <list>`. Block-scoped like `flags`. The harness validates
  each distinct list once against a trivially-valid pattern, because pcrec
  refuses an unknown module name with exit 1 and a `perr` block would
  otherwise read the typo as its expected rejection. `verify_rxt.py`
  understands the directive as a no-op — python re has no module gate, and
  gate-only constructs are `# pcre2-only` blocks like any other
  python-inexpressible pattern.
- `perr` — asserts that the current pattern **fails to compile** (`pcrec`
  must exit nonzero). A block using `perr` has no `m`/`n` lines — the
  pattern text itself is the entire test.
- `m "<subject>" <start> <end>` — asserts that searching `<subject>` from
  byte offset 0 finds a match spanning bytes `[<start>, <end>)`.
- `n "<subject>"` — asserts that searching `<subject>` from byte offset 0
  finds **no** match.
- `ms <P> "<subject>" <start> <end>` — asserts that searching `<subject>`
  with `startpos = <P>` finds a match spanning bytes `[<start>, <end>)`.
  `<P>` is a non-negative decimal integer, given before the quoted subject.
- `ns <P> "<subject>"` — asserts that searching `<subject>` with
  `startpos = <P>` finds **no** match.

`m`/`n` are exactly `ms`/`ns` with `<P>` fixed at 0; see "startpos support"
below for the `rx_search` contract these exercise.

`<subject>` is double-quoted text. Inside the quotes, these escapes are
recognized (no others are):

| Escape | Meaning |
|--------|---------|
| `\"`   | literal `"` |
| `\\`   | literal `\` |
| `\n`   | newline |
| `\t`   | tab |
| `\r`   | carriage return |
| `\f`   | form feed |
| `\v`   | vertical tab |
| `\xHH` | byte `0xHH` (exactly two hex digits) |

Subjects may contain literal spaces — the quotes, not whitespace, delimit
the subject.

### Example

```
# Literal matching and basic quantifiers.

pattern abc
m "abc" 0 3
m "xxabcxx" 2 5
n "ab"

pattern a+
m "aaa" 0 3
n "b"

# An invalid pattern: unbalanced group.
pattern (bad
perr

pattern colou?r
m "The color and colour are spelled differently." 4 9
m "colour" 0 6
m "byte \x41 then newline\n" 5 6
```

## How the harness evaluates a block

For each pattern block, `run.sh`:

1. Runs `$PCREC -p rx -o <tmp>/gen.c '<pattern>'`.
2. If the block is `perr`: passes iff `pcrec` exited nonzero; fails
   (reporting that compilation unexpectedly succeeded) otherwise.
3. Otherwise, if `pcrec` failed, every `m`/`n` case in the block is reported
   as failed, with `pcrec`'s stderr included in the message — and the
   pattern is counted once toward the "pattern-compile failures" total in
   the summary, however many cases it had.
4. Otherwise it compiles the generated matcher against the shared test
   driver:
   `$CC $GENCFLAGS -I<tmp> -o <tmp>/t tests/harness/driver.c <tmp>/gen.c`.
   A failure here is a **harness-level failure** (broken codegen or a
   driver/compiler mismatch, not a single bad test case) and is reported
   clearly, separately from ordinary case failures.
5. For each `m`/`n`/`ms`/`ns` case, runs `<tmp>/t '<subject>' '<P>'` (quotes
   stripped, escapes still encoded — the driver decodes them; `<P>` is `0`
   for `m`/`n`) and compares stdout exactly against `match <start> <end>` or
   `nomatch`.

Failures are printed as `file:line: expected ... got ...` along with the
pattern under test, so a failure can be traced straight back to the
offending line. The final summary reports total cases passed/failed, a
per-file breakdown of failures, and the distinct count of patterns that
failed to compile.

## The driver protocol

`tests/harness/driver.c` is a single small C program, shared by every test
case, that adapts the generated `rx_search` API to a simple CLI:

```
t <subject> [startpos]
```

`<subject>` is the case's subject text with escapes still encoded as literal
backslash sequences (exactly as they appear inside the `.rxt` file's
quotes). `[startpos]` is optional (defaults to `0`) — `run.sh` always passes
it explicitly (`0` for `m`/`n`, `<P>` for `ms`/`ns`). The driver:

1. Decodes escapes into a byte buffer, tracking the length explicitly (the
   decoded bytes may include `\0`, so the driver never uses `strlen` on the
   result). An invalid escape prints a message to stderr and exits `2`.
2. Parses `[startpos]`, if given, as a non-negative decimal integer; a
   malformed value prints a message to stderr and exits `2`.
3. Calls `rx_search(buf, len, startpos, &m)`.
4. Prints exactly one line to stdout: `match %zu %zu\n` (using `m.start`,
   `m.end`) if a match was found, or `nomatch\n` otherwise, and exits `0`.

The driver includes `"gen.h"`, so it must be compiled with `-I<dir>`
pointing at the directory containing the pattern's generated `gen.h`. It has
no dependencies beyond libc.

## Organizing tests by component

Per `APPROACH.md` §7, test files live in one directory per compiler
component, mirroring the component ladder in `APPROACH.md` §3:

```
tests/
├── harness/       run.sh, driver.c (this document describes both)
├── base/          literals, ., [...] classes, |, quantifiers, ^ $, groups
├── captures/      (...), (?<name>...), numbered/named capture
├── classes/       POSIX classes, \d \w \s and negations
├── assertions/    \b \B \A \z \Z, multiline ^ $
├── lookaround/    (?= (?! (?<= (?<!
├── backrefs/      \1, \k<name>
├── modifiers/     (?i) (?m) (?s) (?x), inline and scoped
├── unicode/       \p{...} and friends (UTF-8 tier)
├── advanced/      conditionals, atomic groups, possessive quantifiers, recursion
└── bench/         throughput + compile-speed budgets (not .rxt — see that
                   directory's own tooling once it exists)
```

Each directory holds one or more `*.rxt` files; there's no required naming
scheme within a directory beyond `*.rxt`, though grouping by sub-feature
(e.g. `tests/base/quantifiers.rxt`, `tests/base/anchors.rxt`) keeps failures
easy to scan.

### Adding a new component test directory

1. Create `tests/<component>/` and add one or more `.rxt` files there,
   following the format above. `run.sh` picks up any `*.rxt` under `tests/`
   automatically — no registration step needed.
2. If the component isn't implemented yet (see the milestone ladder in
   `docs/plan.md`), its tests should assert the clean "module required"
   compile error via `perr`, per `APPROACH.md` §7's *expected-unsupported*
   policy — this keeps the suite green at every milestone rather than
   red until the component lands.
3. Once the component is implemented, replace or extend those `perr`
   blocks with real `pattern` / `m` / `n` cases.
4. Run `bash tests/harness/run.sh tests/<component>` to iterate on just that
   directory while developing it.

## R1 review updates (2026-08-09)

- The python-re verification oracle is committed at `tests/harness/verify_rxt.py`
  (run: `python3 tests/harness/verify_rxt.py [files-or-dirs]`; default tests/base).
  Run it whenever corpus files change.
- **Oracle exclusions**: python `re` diverges from real PCRE2 on bare `{,}`
  (python: {0,}; PCRE2 and pcrec: literal — note `{,n}` WITH a digit is a
  quantifier {0,n} in both since PCRE2 10.43, implemented in pcrec 2026-08-09),
  possessive quantifiers (python 3.11+ accepts), quantified bare anchors
  (`^*` — python accepts, PCRE2 rejects error 109), past-end `pos`
  clamping for nullable patterns (python clamps; pcrec/PCRE2 reject), and
  repeat counts above 65535 (`a{65536}` — python's ceiling is 4294967294,
  PCRE2's is 65535 with error 105; U5, added 2026-08-10 with K5's fix). Blocks
  that are correct-for-PCRE but not python-verifiable carry a `# pcre2-only`
  comment line immediately before `pattern`; the verifier skips them and reports
  the skip count. Keep such cases rare and justified; every exclusion must
  have a corresponding entry in docs/upstream_issues.md.
- **Harness hardening**: `perr` passes only on exit code 1 (clean rejection) — a
  crash or timeout (>=124) is a failure; unparseable non-comment lines are hard
  errors; a file with zero pattern blocks fails; a run with zero total cases exits
  nonzero; generated code + driver compile with `-Wall -Wextra -Werror` by
  default; timeouts: pcrec 60 s, compiler 120 s, test binary 10 s per case.

## M2.4 coverage breadth (2026-08-09)

Closes R1's PLAN findings P-M1, P-M2, P-N1, P-N2.

- **`startpos` support (P-M2)**: the `.rxt` format gained `ms <P> "<subject>"
  <start> <end>` and `ns <P> "<subject>"` directives (documented above under
  "The `.rxt` format"), exercising `rx_search`'s `startpos` parameter — the
  contract documented in `lib/pcrec.h` (`^` anchors to absolute offset 0
  regardless of `startpos`; `startpos > n` returns no match). `driver.c` now
  takes an optional `argv[2]` startpos (default `0`); `run.sh` passes it for
  every case (`0` for `m`/`n`); `verify_rxt.py` checks `ms`/`ns` cases with
  `compiled.search(subject, P)` — python's `pos` parameter has the same `^`
  semantics as pcrec's `startpos` (absolute-offset anchoring unless
  MULTILINE), so no oracle exclusion is needed for this feature.
  `tests/base/startpos.rxt` is the new corpus file.
- **Long-subject and high-byte breadth (P-N1, P-N2)**: `tests/base/long_subjects.rxt`
  (200–900 byte subjects: end-of-subject matches, near-miss long scans, greedy
  `.*` spans, bounded `{50,60}`-style repeats over long runs) and
  `tests/base/high_bytes.rxt` (`\x80`–`\xFF` in both patterns — literals and
  classes like `[\x80-\xbf]` — and subjects) are new corpus files, both
  100%-verified by `verify_rxt.py`.
- **CLI + library-API regression net (P-M1)**: `tests/cli/run_cli_tests.sh` is
  a standalone bash script (same conventions as `tests/harness/run.sh`:
  `set -u`, repo-root detection, PASS/FAIL counts, nonzero exit on failure,
  temp dir via `mktemp -d`) covering `-o -`, `--emit-main`, prefix boundary
  validation (60/61 chars, leading digit, empty), `-o subdir/out.c`, `--`
  end-of-options, missing-value and unknown-option diagnostics, and a direct
  `lib/pcrec.h` + `build/libpcrec.a` smoke test of `pcrec_compile`/
  `pcrec_output_free`, plus a 512 KB-stack compile of a 9000-branch
  alternation (M2.8's trie regressed that to >1 MB and no correctness test
  could see it). It is part of `make test` since M2 — it was standalone when
  first written, and the stale claim that it is not wired in survived two
  checkpoint reviews before an R3 critic grepped for it.

## The differential gate principle (Frank, 2026-08-12, R20/0.8c)

Apples to apples: **a construct whose module has producers is differentially
tested against libpcre2 with that module ENABLED.** libpcre2 has everything
"on" always, so a closed-gate comparison of a producing construct compares
pcrec's refusal against pcre2's acceptance — a RECOGNITION-tier comparison
only, and it must be labelled as one, never mistaken for behavioral
coverage (SPEC-1, the `a(?i)*` miscompile, lived exactly in that mislabel:
every differential was closed-gate, so the accepting path was never
compared to the oracle at all).

And FOCUSED: **enable exactly the module(s) the sweep exercises — per
feature, not `--features all`.** Two reasons. Attribution: a failure in a
focused gated sweep implicates the module under test, not a cross-module
interaction. Coverage honesty: interactions between enabled modules are a
real axis, but they are tested DELIBERATELY as their own labelled sweeps,
not smuggled in as noise inside every differential. (This mirrors the
per-module-not-blanket rule the `--features` CLI surface already pins.)

## Tiered testing ([TT-1], 2026-08-13)

The full suite has crept from ~15 minutes to ~5 minutes parallelized and
keeps growing, because the project only ever ADDS tests. The fix is not to
weaken `make test` — **it stays the full suite, and a green `make test`
keeps meaning the complete claim, unchanged by anything below.** Instead:
section targets to spot-check just the area a change touches while working,
`make smoke` as a measured fast path for the tightest inner loop, and an
opt-in local push gate so the full suite still runs before code leaves the
machine — full load stays the standard at merge/checkpoint evaluation
points regardless of what ran during development.

### Section targets

Thin wrappers, one per section, over the exact scripts `make test` already
runs — no weakened variants, each target runs the real script(s). `test:`
in the Makefile is untouched (still the same nine `bash tests/.../*.sh`
lines it always was); the wrappers just let you invoke one line instead of
paying for all nine.

The plan row that created this tiering named eight targets by number
(`test-corpus`, `test-cli`, `test-reject`, `test-registry`, `test-codegen`,
`test-spec`, `test-thread`, `test-parse`). Reading the Makefile, `make
test:` actually runs **nine** script invocations, which this table groups
into eight sections (`test-codegen` wraps two scripts — `run_codegen_tests.sh`
and `run_trie_identity.sh` — since this file already describes them as one
"codegen structural checks" concept, and `test:` runs them back to back).
`test-spec` is the ninth target and the one genuine divergence: it wraps
`tests/spec_mod0/run_spec_mod0.sh`, which is **not** one of the nine `test:`
lines (its own CLAUDE.md: "Not part of `make test`, and it does not run
`make`") — it gets a target anyway because the plan row named it explicitly,
and the script already runs standalone and was green (14/14) at the last
project journal entry.

| Target | Runs | Part of `make test`? |
|---|---|---|
| `make test-corpus` | `tests/harness/run.sh` (the `.rxt` corpus) | yes |
| `make test-cli` | `tests/cli/run_cli_tests.sh` | yes |
| `make test-reject` | `tests/reject/run_reject_tests.sh` | yes |
| `make test-registry` | `tests/registry/run_registry_tests.sh` (registry_check, compliance_section.py, PC-3, PC-4) | yes |
| `make test-parse` | `tests/parse/run_parse_tests.sh` | yes |
| `make test-codegen` | `tests/codegen/run_codegen_tests.sh` + `run_trie_identity.sh` | yes |
| `make test-known-fail` | `tests/known_fail/run_known_fail.sh` | yes |
| `make test-thread` | `tests/thread/run_thread_tests.sh` | yes |
| `make test-spec` | `tests/spec_mod0/run_spec_mod0.sh` | **no** — standalone D27 suite, wrapped anyway |

Each target depends on `all`, so a stale binary never reads as a pass.
`make mech`, `make bench`, `make fuzz`, and `make strict` already had their
own top-level targets before TT-1 and are untouched — they are not `test:`
sections and this tiering doesn't wrap them again.

### Measured per-section runtimes

Measured 2026-08-13 at commit `f5e419a3e6c9d0e5629ab7bdd345d21e3b902586`, on
the project box, `TMPDIR=/var/tmp`, `PROCS` unset (serial — the same default
`make test` itself uses), 3 runs per section. Following the R3.10 lesson (a
single `/proc/loadavg` sample for a whole multi-minute run can call a
contended window "quiet"), `/proc/loadavg` was sampled immediately before
**and** after *each individual run*; a run was flagged CONTAMINATED if
either sample's 1-minute load exceeded 1.20 (the box's observed quiet
baseline was under 1.0). All 27 runs (9 sections x 3) came back clean — no
retries were needed. A first attempt at this measurement, taken while a
second concurrent lane was running its own `make test`/`make ubsan` in a
different worktree on the same box, was discarded in full rather than
partially trusted, because it only sampled load once for the whole sweep
and load visibly climbed (0.99/0.77/0.57 -> 2.41/1.45/0.92) across it.

| Section | run 1 | run 2 | run 3 |
|---|---|---|---|
| `test-corpus` | 303.45s | 303.89s | 304.18s |
| `test-cli` | 6.26s | 6.29s | 6.56s |
| `test-reject` | 54.70s | 54.71s | 54.70s |
| `test-registry` | 7.85s | 7.86s | 7.85s |
| `test-parse` | 0.89s | 0.91s | 0.96s |
| `test-codegen` | 10.08s | 10.98s | 10.06s |
| `test-known-fail` | 0.03s | 0.03s | 0.02s |
| `test-thread` | 7.68s | 7.72s | 7.70s |
| `test-spec` | 25.95s | 27.53s | 26.67s |

`test-corpus` dominates by nearly an order of magnitude over everything
except `test-reject`; `test-known-fail` is a no-op today (the directory is
empty per its own CLAUDE.md) and its near-zero time reflects that, not a
weak check. Summing the eight sections that make up `make test` (excluding
`test-spec`, which isn't part of it) by median gives ~391s (~6m31s) serial
for the full suite run as separate section invocations. A direct `make
test` run at commit f5e419a confirmed this: corpus 1270 cases, cli 221,
reject 486/0 failed, registry_check 168/0 failed, PC-3 163/0 failed (ran
against real libpcre2, not skipped), parse 2+8 checks, codegen 29/0 failed,
trie identity 7/0 failed, known-fail empty/nothing-to-ratchet, thread 8/0
fail — all green, zero FAIL lines anywhere in the output. Its own wall-clock
trailer was lost (an earlier, unrelated cleanup command killed the timing
wrapper after `make test` had already forked, so the run finished
unsupervised and unmeasured for elapsed time); the log's start-to-finish
window and the section sum above both put it at roughly 6-6.5 minutes,
consistent with each other.

**RE-RECORD TRIGGER**: re-measure a section (same method: 3 runs, per-run
load-before/after sampling, `TMPDIR=/var/tmp`) whenever its runtime doubles
from the figures above. `make smoke`'s composition and the touched-path
table below both derive from these numbers, so a re-measurement that moves
them is also a prompt to re-check whether `make smoke` still fits under 60s
and whether the composition should change.

### Touched-path -> sections (inner-loop guidance, not a substitute for full load)

Starting point from the TT-1 plan row, refined by reading the Makefile,
`src/`'s actual directory contents, and what each section's own CLAUDE.md
says it guards. This is guidance for **spot-checking while you work** — the
full suite (or at minimum every section the touched paths imply) still runs
at evaluation points (checkpoint review, merge, the opt-in pre-push gate).

| Touched path | Spot-check with | Why |
|---|---|---|
| `src/parse/*` (`parse.c`, `registry.c`, `enabled.c`, `ext.c`, `scans.c`, `syntax_dump.c`, `mod_*.c`) | `test-reject`, `test-registry`, `test-spec`, `test-cli` | reject asserts the "never miscompile" mandate per construct; registry checks the SR-1 table against the parser AND against libpcre2 (PC-3/PC-4); spec_mod0 is the D27 promise-derived suite, blind to `src/`'s own alphabet; cli exercises the CLI surface these modules gate ("requires module 'X'") |
| `src/ir/*` (`nfa.c`, `dfa.c`) + `src/opt/*` (`minimize.c`) + `src/gen/*` (`emit_dfa.c`) | `test-corpus`, `test-codegen` (includes the trie identity differential), `bench` | corpus is correctness of what the emitted matcher actually matches; codegen asserts the optimization signatures (skip tables, fast paths, minimization) are structurally present, per R2-PR3's finding that these can be silently disabled with zero other signal; bench guards the throughput/compile-time budgets these components produce |
| `src/core/*` (`compile.c`, `arena.c`, `sb.c`) | all of the above, plus `test-thread` | `compile.c` is `pcrec_compile()`'s entry point and nearly every suite goes through it; `test-thread`'s TS-3 half specifically exercises concurrent `pcrec_compile()` calls, which only a change here would plausibly break |
| `cli/main.c` | `test-cli`; also `test-reject`/`test-registry` if the change touches how errors or `--list-syntax` are surfaced | cli/'s own suite is the CLI-surface test; the other two invoke `build/pcrec` as a subprocess and would show a broken diagnostic path |
| `lib/pcrec.h` | `test-cli` (the library-API smoke test), `test-thread` (both TS-2 and TS-3 call the public API directly) | |
| `tests/mech/*` (sabotage definitions) | `make mech` (not a `make test` section — its own top-level target, ~6 minutes, run manually per its own CLAUDE.md when a sabotage table's figures are in doubt) | |

### `make smoke`

A measured, sub-60-second inner-loop subset, sized from the table above —
never vibes. Runs the real section targets it lists, not a weakened variant
of any of them.

**Composition**: `test-cli`, `test-registry`, `test-parse`, `test-codegen`,
`test-known-fail`, `test-thread`. Deliberately excludes the three slow
sections: `test-corpus` (~304s, two orders of magnitude over budget),
`test-reject` (~55s, which alone would consume nearly the whole budget and
leave no room for anything else), and `test-spec` (~27s, which — added to
the ~33s the other six sections cost together — lands at ~60s with
essentially no headroom against ordinary run-to-run variance; see the
per-section table's spread, e.g. `test-codegen`'s 10.06-10.98s). The six
included sections sum to ~33s by median, leaving comfortable headroom.

**Measured runtime** (2026-08-13, same commit and load-provenance method as
above): 32.16s clean (load 0.50/0.24/0.21 -> 0.65/0.31/0.24), 31.36s
(load 0.59/0.30/0.24 -> 1.44/0.54/0.32, flagged CONTAMINATED by the
1-minute-load-after sample — a second lane was mid-retime on the same box),
and 30.88s (load 1.13/1.08/0.89 -> 1.26/1.12/0.91, also flagged
CONTAMINATED). All three land in the same ~31-32s band regardless of the
mild contention on the two flagged runs, which is itself reassuring: even
under load this target has comfortable headroom under the 60s target, not
just on a perfectly quiet box.

**Floor check**: `SMOKE_FLOOR := 6` in the Makefile is a literal, kept
independent of `SMOKE_SECTIONS` on purpose — the project's own lesson
(memory: every check written for this repo that failed shared a source with
the thing it controlled; see e.g. registry_check's PASS-count guard, which
this mirrors). The target counts how many entries in `SMOKE_SECTIONS` it
actually ran and fails loudly, with a fix-it message, if that count drops
below `SMOKE_FLOOR`. Because `SMOKE_FLOOR` does not auto-track the list,
shrinking `SMOKE_SECTIONS` — by accident or on purpose — without also
updating `SMOKE_FLOOR` in the same commit trips the gate instead of
silently shrinking what "smoke" means.

**Sabotage validation** (2026-08-13): temporarily dropped `test-thread` from
`SMOKE_SECTIONS` (5 entries, `SMOKE_FLOOR` left at 6) and ran `make smoke`.
It ran the remaining five sections, then failed loudly:

    smoke: FLOOR TRIPPED — ran 5 section(s), expected at least 6.
    smoke:   SMOKE_SECTIONS shrank without SMOKE_FLOOR being updated to match.
    smoke:   Restore the missing section(s); if the shrink is deliberate, update
    smoke:   BOTH SMOKE_FLOOR here AND docs/testing.md's smoke composition in the
    smoke:   same commit.
    make: *** [Makefile:110: smoke] Error 1

Exit code nonzero (2, via `make`'s own wrapping of the target's `exit 1`).
The sabotage was never committed — `SMOKE_SECTIONS` was restored immediately
after, and `make smoke` re-verified green (6/6) before anything landed.

### Opt-in local pre-push gate

`make hooks` installs `scripts/hooks/pre-push` (runs the full `make test`,
not a tier) into the repository's real hooks directory, resolved via `git
rev-parse --git-path hooks` rather than assumed as `.git/hooks` — a
worktree's `.git` is a file pointing at the shared gitdir, and the install
must resolve that path correctly to work from a worktree clone (verified:
installing from inside a nested worktree correctly resolves to the shared
gitdir's `hooks/`, not a nonexistent `.git/hooks` under the worktree).
**Never installed automatically** by any other target and never by CI (D2's
"plain make for strangers" holds: cloning this repo and running
`make`/`make test` must not install anything into the cloner's git config).
Bypass with `git push --no-verify` when you deliberately need to push past
a failing local gate.

CI itself stays deferred, not rejected (Frank, 2026-08-12): revisit when a
red lands on `main` that this local pre-push discipline should have caught,
or when a second regular contributor appears.
