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

`make test` is NOT equivalent to `run.sh`: since M2 it runs FOUR scripts — the
.rxt corpus, `tests/cli/run_cli_tests.sh`, `tests/codegen/run_codegen_tests.sh`
(structural assertions that behaviour-preserving optimizations are actually
PRESENT in the emitted C — see that directory's CLAUDE.md), and
`tests/known_fail/run_known_fail.sh` (the ratchet that flags a deferred-bug
regression which has started passing). `run.sh` alone certifies only the first
of the four.

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

Example: testing a debug build with a different compiler and keeping
artifacts around for inspection:

```sh
PCREC=build/pcrec-debug CC=clang KEEP=1 VERBOSE=1 bash tests/harness/run.sh tests/base
```

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
  (`^*` — python accepts, PCRE2 rejects error 109), and past-end `pos`
  clamping for nullable patterns (python clamps; pcrec/PCRE2 reject). Blocks
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
