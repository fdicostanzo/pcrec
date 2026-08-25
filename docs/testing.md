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

`make test` is NOT equivalent to `run.sh`: it runs EIGHT scripts — the .rxt
corpus, `tests/cli/run_cli_tests.sh`, `tests/reject/run_reject_tests.sh` (the
"never miscompile" mandate, per construct),
`tests/registry/run_registry_tests.sh`, `tests/parse/run_parse_tests.sh`
(PARSE-1: facts the PARSER computes but never emits — see that directory's
CLAUDE.md), `make test-atomic` ([M6.4.2]:
`tests/atomic_groups/run_atomic_diff.sh`, the module's behavioural instrument
whose ENGINE arm is where §4's ceiling hazard lives — and since [M6.4.4] the
only script in that section; the byte-identity gate moved to the opt-in
`make test-atomic-identity`, see "The atomic landing gate" below),
`make test-backrefs` ([M6.5.2]: `tests/backrefs/run_backref_diff.sh` and
`run_dupnames_diff.sh` — see "The backrefs behavioural suite" below; that
module's byte-identity gate is likewise opt-in as
`make test-backrefs-identity`),
`make test-recursion` ([DD-14]: `tests/recursion/run_recursion_diff.sh`, the
module's behavioural instrument — it carries the `--no-captures` axis the
`.rxt` format has no directive for, the `--engine=dfa` refusal by name, and
the depth-capacity probe; that module's byte-identity gate is opt-in as
`make test-recursion-identity`, see "The recursion landing gate" below),
`tests/codegen/run_codegen_tests.sh`
(structural assertions that behaviour-preserving optimizations are actually
PRESENT in the emitted C — see that directory's CLAUDE.md), and
`tests/known_fail/run_known_fail.sh` (the ratchet that flags a deferred-bug
regression which has started passing). `run.sh` alone certifies only the first
of the eight.

`make strict` is separate and opt-in: it recompiles every source with
`-Werror` **and, since [M6.5.2], `-Wshadow`**, writes nothing, links nothing, and touches `build/` not at all, so it
is safe to run while `make test` is in flight. It exists because the project
already had a warnings-as-errors gate BY ACCIDENT —
`tests/codegen/run_trie_identity.sh` compiles the whole tree and fails on any
warning, and R7 measured that this accident was for a while the only thing
catching a class of offset bug. Now it is a gate someone chose. Validated the
way any gate should be: adding one unused variable to `src/core/sb.c` leaves
plain `make` succeeding and makes `make strict` fail.

**`-Wshadow` joined it at [M6.5.2], and it is a row that lane EARNED.**
`-Wall -Wextra` does not include it, and a local named after an enclosing
parameter is a silent miscompile of exactly the shape `src/gen/emit_vm.c` is
exposed to: a new arm declared `const unsigned entry = ...` for a seam-entry
id, shadowing `vm_emit`'s LABEL parameter of the same name, and every
`^(a)\1$`-shaped artifact came out with a DUPLICATE LABEL that would not
compile. The corpus caught it inside one run — but a shadowed variable that
happens to hold a PLAUSIBLE value is the version that does NOT get caught, and
this makes the whole class a compile error. The tree was measured clean under
it before it was added (0 warnings across every source plus `cli/main.c`), so
it costs nothing today and refuses the next one.

**TWO of the eight can SKIP, and both skips are loud** (three, counting
`make test-backrefs`, whose two scripts print PC-3's own SKIP banner and exit 0
when libpcre2 is absent at run time — a green run without it is a WEAKER result
than a green run with it, and the banner is how you tell which one you got). `run_parse_tests.sh` is
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

- Blank lines and lines starting with `#` are ignored (comments). Comments
  are WHOLE-LINE ONLY: a `#` after case fields is NOT a comment — it makes
  the line unparseable, a hard error. (Deliberate: a pattern or subject may
  legitimately contain `#`, so the parser never guesses where data ends and
  commentary begins. Found the hard way by the R22 D27 author.)
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
- `g <slot> <start> <end>` / `gp <slot> <start> <end>` — **[M4.5a]** asserts a
  per-GROUP capture-slot expectation, attached to the most recently preceding
  `m`/`ms` case in the current block (never `n`/`ns` — a no-match assertion
  has no captures). `<slot>` is a non-negative decimal integer indexing
  `caps[]` exactly as the frozen match API does (slot 0 is the whole match,
  same value as the case's own `<start> <end>`; group *k* occupies slot *k*
  when every group up to it delivers a slot — match_api_m4.md §2.2 C2/C9).
  `<start>`/`<end>` are two non-negative decimal integers for a real span, or
  the literal pair `-1 -1` for `RX_UNSET` (the group didn't participate) —
  one `-1` without the other is a hard parse error, since `RX_UNSET` is
  symmetric in both slots (C5). `g` is LIVE: the slot must be checkable
  *now*; `gp` is PENDING-VM: the slot may be beyond what today's DFA-only
  artifacts deliver. See "Capture-group expectations" below for the full
  design and the population-accounting rule.
- `gu <code> "<subject>"` — **[DD-14 wave A, 2026-08-24]** asserts that
  searching `<subject>` from byte offset 0 GIVES UP with the typed code
  `<code>`, one of `steps`/`frames`/`work`/`recurse` (`recurse` is
  `PCREC_ERR_RECURSE`, reserved with no producer yet, D71 item 1, so no
  block can pass with it today — the directive still accepts the word so
  a future producer needs no harness change). `internal` is REFUSED at
  parse time, by name, with its own diagnostic: `PCREC_ERR_INTERNAL` is
  the artifact catching its own analysis/emission bug, never a planned
  outcome a corpus block gets to EXPECT — that is what `tests/mech`'s
  sabotage rows are for (S136 exercises this exact code). Scored against
  the driver's exit `3` plus its printed word (see "The driver protocol",
  point 5, below) instead of the default HARD failure every other case
  kind gets on exit 3 — see below (`engine`, `budget`) for the two
  directives that let a block actually REACH a give-up.
- `engine vm` — block-scoped, like `flags`/`features`: forces
  `--engine=vm` for the current block's compile. Only `vm` is defined.
- `budget steps=<n>` / `budget frames=<n>` — block-scoped: passes
  `--step-budget=<n>` / `--backtrack-frames=<n>` respectively. Either,
  neither, or both may appear in one block (two separate `budget` lines).
  These, together with `engine vm`, are the minimal route — mirroring
  `tests/vm/run_vm_tests.sh`'s own `build()` calls, which drive the same
  two bounds through the identical pcrec flags via a separate C driver —
  that lets a `.rxt` block reach a give-up at all; before [DD-14] wave A
  nothing in the directive vocabulary could select `--engine=vm` or a
  tiny budget (see "The driver protocol", point 5, below).

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
   for `m`/`n`). For `n`/`ns`, stdout must be exactly `nomatch`. For `m`/`ms`,
   stdout must start with `match` followed by the WHOLE-MATCH pair
   (`<start> <end>`, parsed positionally as fields 2 and 3) — **[M4.5a
   fix]**: this is a parsed-field comparison, not a whole-line compare,
   because the driver line also carries every subsequent `RX_NCAPS` group
   pair (see "Capture-group expectations" below); trailing pairs are simply
   not looked at by this check. It is still strict, not a substring match:
   `match` vs `nomatch`, a short/malformed line, or a wrong whole-match pair
   all fail loudly. **[DD-14 wave A, 2026-08-24]**: for a `gu <code>` case,
   the same driver invocation must instead exit `3` with stdout exactly
   `<code>` — the ONE case kind that WANTS the exit every other kind
   treats as an unconditional hard failure ("The `.rxt` format" above and
   "The driver protocol", point 5, below have the full shape).

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
3. Calls `rx_search(buf, len, startpos, caps)` ([M4.4], D44.2: `caps` is a
   `ptrdiff_t (*)[2]`, not the retired `rx_span *m` out-struct), where `caps`
   is declared `ptrdiff_t caps[RX_NCAPS][2]` — `RX_NCAPS` comes from the
   pattern's own generated `gen.h`, so the array is always exactly the size
   the artifact under test actually delivers.
4. On a match, prints `match` followed by **every** `caps[k][0] caps[k][1]`
   pair for `k` in `[0, RX_NCAPS)` (`%td` each), then a newline; on no match,
   prints `nomatch\n`; exits `0` either way. **[M4.5a]**: since `RX_NCAPS` is
   1 on every artifact before [M4.5]'s VM lands (match_api_m4.md D42.2), this
   is exactly `match %td %td\n` today — the multi-pair form is a superset
   that activates automatically once `RX_NCAPS` grows, not a reshape. A `g`/
   `gp` capture-expectation line (see "Capture-group expectations" below)
   picks its slot's pair out of this line by position: fields `1+2*slot` and
   `2+2*slot` after the leading `match` token.
5. **[K21-class fix, 2026-08-15]**: `rx_search`'s return is actually
   three-valued, not boolean — a VM artifact can also GIVE UP (a negative
   RX_ERR_STEPS/RX_ERR_FRAMES/RX_ERR_WORK/RX_ERR_RECURSE sentinel when it
   exhausts its step budget, backtrack-frame capacity, or (RECURSE, [DD-14]
   wave A, reserved with no producer yet, D71 item 1) its recursion depth;
   a DFA artifact never returns one) — or, [DD-14] wave A commit 2, D71
   item 1, return the BELOW-THE-FLOOR `RX_ERR_INTERNAL`, which is NOT a
   give-up: the artifact caught its own analysis/emission inconsistency
   (module `lookaround`'s negative-polarity lookbehind end-check is the
   one producer today). The driver
   discriminates this explicitly rather than treating the return as a bool
   (the shape that was wrong — see docs/dev/known_issues.md K21): on a
   give-up or an internal code it prints
   `steps\n`/`frames\n`/`work\n`/`recurse\n`/`internal\n` (an
   unrecognized code prints `giveup <N>\n`, [DD-14] wave A —
   the earlier version of this line folded every non-STEPS code into
   `"frames"`, mislabelling WORK give-ups) and exits `3`, not `0`, and
   `run.sh`'s per-case loop treats exit `3` as its own HARD harness-level
   failure by default — alongside the existing timeout (`124`) and crash
   (`>=126`) branches, never compared against a `match`/`nomatch`
   expectation — UNLESS the case is a `gu <code>` directive (above), which
   scores exit 3 against its expected word instead. **[DD-14] wave A,
   2026-08-24**: before this wave nothing in the `flags`/`features`
   directive vocabulary could select `--engine=vm` or a tiny
   `--step-budget`/`--backtrack-frames`, so no `.rxt` case could reach this
   path at all — the `engine`/`budget` directives (above) are the minimal
   route that changed that, and `tests/harness/giveup.rxt` is the
   permanent positive cell exercising both a `steps` and a `frames`
   give-up through it.

A usage note that follows from [M4.6a]'s calibration sweep (2026-08-17):
`--engine=vm` is a DIAGNOSTIC mode — it disables the DFA prefilter so the
two engines are independently comparable (the R21 E-6 ruling), and without
the prefilter the VM's work on a large subject runs orders of magnitude
above the default path the budgets were calibrated against. Anyone forcing
`--engine=vm` over large subjects should pass an explicit `--work-budget`
sized for that run rather than relying on the default.

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
   `docs/dev/plan.md`), its tests should assert the clean "module required"
   compile error via `perr`, per `APPROACH.md` §7's *expected-unsupported*
   policy — this keeps the suite green at every milestone rather than
   red until the component lands.
3. Once the component is implemented, replace or extend those `perr`
   blocks with real `pattern` / `m` / `n` cases.

**[DD-14] A GENERATED CORPUS CAN DO STEP 2 WITHOUT LOSING THE ORACLE, and
`tests/recursion/gen_corpus.py` is the worked example.** Its `wave='D'`
argument renders a block as a `perr` — pinning the refusal that must exist
today — while DRIVING THE ORACLE ANYWAY and writing the answer into the block
as a `# WAVE D ORACLE:` comment beside each cell. So step 3 is "delete one
keyword argument and re-run the generator", and the `m`/`n`/`g` lines that
come back are the ones libpcre2 gives THEN rather than a transcription of what
it gave now. The marker carries its own liveness check: a block marked for a
wave that has LANDED fails the same guard `PERR` carries, so it cannot outlive
the wave it names.

**AND A CELL WHOSE ANSWER IS DISPUTED IS NOT A `perr` CASE.** The same
generator's `parked=` argument moves a block out of the live corpus into
`tests/known_fail/`, leaving a comment stanza at its former position saying
where it went and why. The two are deliberately different renderings: `wave=`
pins a REFUSAL that must exist, `parked=` pins an ANSWER that pcrec currently
disagrees with — which `known_fail`'s ratchet then keeps LOUD (it fails if a
parked cell starts passing) instead of silently green.
4. Run `bash tests/harness/run.sh tests/<component>` to iterate on just that
   directory while developing it.

## R1 review updates (2026-08-09)

- The python-re verification oracle is committed at `tests/harness/verify_rxt.py`
  (run: `python3 tests/harness/verify_rxt.py [files-or-dirs]`; default tests/base).
  Run it whenever corpus files change.
- **Oracle exclusions**: python `re` diverges from real PCRE2 on `\Z`
  (**python's `\Z` IS PCRE2's `\z`**, and python has no single escape for
  PCRE2's `\Z` at all — U11, [M6.2] wave A; the divergence is silent, python
  reporting no match or a shorter span exactly where PCRE2 matches, so a
  python-derived `\Z` cell would encode `\z` and go green on a miscompile.
  `tests/assertions/` is the affected directory and carries its own libpcre2
  verifier, `verify_pcre2.py`, which re-checks EVERY cell there — marked and
  unmarked — on every `make test` through `tests/fuzz/pcre2_oracle`; it is the
  only per-directory oracle in the tree and the only case where a
  `# pcre2-only` mark is applied WHOLESALE to a construct rather than
  per diverging cell, because a subject added to an unmarked `\Z` block later
  would silently start lying), bare `{,}`
  (python: {0,}; PCRE2 and pcrec: literal — note `{,n}` WITH a digit is a
  quantifier {0,n} in both since PCRE2 10.43, implemented in pcrec 2026-08-09),
  the BRACE possessive over a body whose iteration can end in TWO PLACES
  (**python cuts PER ITERATION and PCRE2 cuts at the GROUP EXIT**: `(?:a|ab){2}+`
  on "aba" is (0,3) in PCRE2 and NO MATCH in python, while `(?:a|ab)*+` on the
  same subject is (0,1) in BOTH — so the divergence is the brace forms
  specifically, and it runs in the dangerous direction. [M6.4.2];
  `tests/atomic_groups/` carries a libpcre2 verifier pass over its whole
  corpus and the affected blocks are `# pcre2-only`, with the `*+`/`++`
  controls beside them making it a family rather than a one-off),
  possessive quantifiers otherwise (python 3.11+ accepts), quantified bare anchors
  (`^*` — python accepts, PCRE2 rejects error 109), past-end `pos`
  clamping for nullable patterns (python clamps; pcrec/PCRE2 reject), and
  repeat counts above 65535 (`a{65536}` — python's ceiling is 4294967294,
  PCRE2's is 65535 with error 105; U5, added 2026-08-10 with K5's fix). Blocks
  that are correct-for-PCRE but not python-verifiable carry a `# pcre2-only`
  comment line immediately before `pattern`; the verifier skips them and reports
  the skip count. Keep such cases rare and justified; every exclusion must
  have a corresponding entry in docs/dev/upstream_issues.md.
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

**[M4.7e] (2026-08-17) applied this principle to the capture-span
differential, and it turned out to already be satisfied: no new code
needed.** `tests/fuzz/fuzz.py` passes no `--features` flag at all, so every
compile it runs (the fixed-seed gate below, and the at-scale campaign) goes
through the bare-invocation default — `PCREC_DEFAULT_FEATURES` (D37/STD1b,
`src/parse/enabled.c`), currently `"std1"` = `{classes, modifiers}`. That IS
open-gate, not closed-gate: both modules with real producers and PC-3
differential coverage are already ON for the whole fuzzer, not merely
recognized. FOCUSED still holds too — the generator produces no construct
gated by any module outside std1 (`EXCLUDED FROM GENERATION`,
tests/fuzz/README.md), so no cross-module interaction noise is smuggled in
either.

**GATE-ON, the wiring:** `make test-capturediff`
(`tests/fuzz/run_capturediff_gate.sh`) runs the SAME fuzz.py at one pinned
seed (its own argparse defaults — 300 patterns, 15 subjects), asserting
fuzz.py's own zero-divergence exit code. The distinction that makes this
different from `make fuzz` staying manual-only (README.md's own reasoning:
"a clean run today says nothing about tomorrow's random seed") is that a
FIXED seed has none of that problem — it is exactly as reproducible as any
other differential in this tree. The many-seed, many-thousand-pattern
CAMPAIGN (tests/fuzz/campaigns/) stays the manual/checkpoint instrument for
finding NEW divergences; the fixed-seed gate exists to catch a REGRESSION
against ones already known to be absent. It probes libpcre2 presence itself
before ever calling into fuzz.py (fuzz.py's own oracle plumbing is
deliberately fail-hard, right for a manual tool, wrong for a `make test`
section on a libpcre2-less box) and SKIPS loudly, PC-3's own pattern.

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
| `make test-vm` | `tests/codegen/run_vm_identity.sh` + `run_ir_listing.sh` + `tests/vm/run_vm_tests.sh` | yes |
| `make test-possessify` | `tests/possessify/run_possdiff.sh` + `run_possessify_tests.sh` | yes |
| `make test-rungselect` | `tests/rungselect/run_rungdiff.sh` + `run_rungselect_tests.sh` | yes |
| `make test-counterk` | `tests/counterk/run_counterkdiff.sh` + `run_counterk_tests.sh` | yes |
| `make test-mrl` | `tests/mrl/run_mrldiff.sh` + `run_mrl_tests.sh` | yes |
| `make test-prefilter` | `tests/prefilter/run_prefilter_tests.sh` | yes |
| `make test-assertions` | `tests/assertions/run_assertions_tests.sh` + `tests/codegen/run_endvar_identity.sh` + `run_wordctx_identity.sh` + `run_mlinectx_identity.sh` + `run_gstart_identity.sh` + `tests/assertions/run_mline_diff.sh` + `run_gstart_diff.sh` | yes |
| `make test-known-fail` | `tests/known_fail/run_known_fail.sh` | yes |
| `make test-thread` | `tests/thread/run_thread_tests.sh` | yes |
| `make test-capturediff` | `tests/fuzz/run_capturediff_gate.sh` | yes |
| `make test-spec` | `tests/spec_mod0/run_spec_mod0.sh` | **no** — standalone D27 suite, wrapped anyway |
| `make test-recursion-lbsweep` | `tests/recursion/run_lookbehind_call_sweep.py` | **no** — opt-in ([DD-14.LB]), see below |

**[DD-14.LB] (2026-08-24) — `test-recursion-lbsweep`, and why its verdict is a
CLASSIFICATION rather than a pass count.** A call inside a lookbehind, swept:
908 generated patterns (11 callee width-classes × 14 lookbehind body templates
× both polarities) × 22 subjects, every cell asked of libpcre2 AND of a real
compiled artifact. It is opt-in on `test-lookaround-identity`'s ruling — 900-odd
`gcc` invocations for an answer that cannot change unless someone edits the
width analysis — and it exists beside `tests/recursion/inlookaround.rxt` rather
than instead of it, because that corpus is a set of AIMED questions and
therefore inherits its author's alphabet, which is D27's own finding.

The part to understand before reading its output: **a pattern libpcre2 compiles
and pcrec REFUSES is expected and does not fail the run.** PCRE2 10.43+ ships
variable-length lookbehinds; `lookaround_design.md` §2.5 charters that loop
rather than shipping it, so the over-rejection is a ruled D26 tier-2 limit.
Scoring those as failures would make the instrument useless and scoring them as
passes would make it blind, so it checks instead that every one of them is the
§2.5 WIDTH refusal — never a crash, an internal error, a give-up, or a
diagnostic naming the wrong module. What DOES fail the run: a span
`disagree`, a `bad_refusal`, `pcrec_only` (pcrec compiling what libpcre2
refuses — the direction that would mean the width rule had gone soft), a build
failure, or a give-up. Measured at the wave: 9,240 cells, 9,240 agree, 0
disagree, 220 pcrec-refuses with bad_refusal 0, 268 both-refuse, 0 pcrec-only.

**[ENG-BREP] (2026-08-16) — the D45 positive control needed `-fno-revdet`, and
that is D46's own scenario reached from the outside.** `run_gen_timeout_tests.sh`
proves the compile budget FIRES by compiling a real artifact that must exceed
it, and the artifact it used was `((a)|b){0,64}c` — slow because the VM emitter
replicated its body sixty-four times (1,939 lines, 2.3 s at −O2). The
reverse-deterministic rung emits that same pattern as ONE body copy in 293 lines
and 0.12 s, so the control went green-because-fast: a positive control that had
stopped controlling anything, reported as "the CPU limit is not being applied".
Fixed the way D46 prescribes — PIN THE SELECTION — by denying the rung, plus a
SIZE FLOOR on the artifact so that the next strategy to absorb this shape fails
with a diagnostic naming the cause rather than looking like a broken budget.
Counter-K will meet the same line when it lands.

**[M4.6d] (2026-08-17) — `test-mrl`, and TWO things about it that do not
apply to the three deny-family sections below.**

MINIMUM-REMAINING-LENGTH pruning (K23's fix, D51 ruling 1) is NOT A RUNG. It
is a bound emitted ON whichever rung a quantifier already took, so
`-fno-length-prune` changes no rung, no slot and no capacity, and a denied
artifact is byte-for-byte the one pcrec emitted before MRL existed —
`run_mrl_tests.sh` asserts exactly that over every pattern in the tree (701 of
944 compilable ones carry no bound and are byte-identical). That is the
strongest form of "the denied build is the ground truth" available in this
project. It is also why the DENIAL LEAVES NO TRACE, including in the stamps:
`<PREFIX>_VM_PRUNE_CEILING` reads `"none"` under `-fno-length-prune`, exactly
as it does for a bound-free pattern, because a stamp announcing the denial
would destroy the byte-identity property it is there to support. The do-or-die
is asserted by the ABSENCE of a bound in the artifact.

**`run_mrldiff.sh` sweeps BOTH ENGINES, which no other differential in the
tree does, and the reason is that the two get DIFFERENT CEILINGS.**
`--engine=vm` turns the DFA prefilter off, so the bound measures to the subject
end; the default path threads the prefilter's match-end window (D51 ruling 2),
which is tighter and is the form that ships. A sweep on either alone leaves the
other's arithmetic untested, and the window form is the only conservative
choice in this design whose error direction is UNSOUND — a stale window is too
SMALL, which deletes real matches rather than merely pruning less. It also
carries the STRIDE axis for R26 E1/E2's reason (an 855-cell differential once
blessed an unsound clamp because every body in its corpus was single-byte, and
at stride 1 the broken clamp and the correct one emit equal code).

**Its driver carries the tree's one COMPARISON ASYMMETRY, opt-in and off by
default.** An optimization whose purpose is to turn a resource REFUSAL into an
ANSWER cannot be held to "the failure surfaces are identical" — taken
literally, that requirement forbids the feature. `possdiff_driver.c` gains
`-DDIFF_A_MAY_ANSWER_MORE`, which only `run_mrldiff.sh` passes: arm A may
ANSWER where arm B gave up, the reverse is still a divergence, and two arms
that both answer must still agree on the span and every slot. A give-up
carries no captures, so no cell where the answers COULD differ is excused.
Measured at the pinned budget: 22 of 202,458 cells take the exemption, across
two shapes. The count is not a comment — `run_mrldiff.sh` ASSERTS it against a
pinned expectation, so growth is loud and the figure is re-run rather than
copied. (The first version of that comment said "2", which was the number of
PATTERNS the driver reported, not cells; the assertion exists because a
hand-copied number describing an unmeasured quantity is exactly what happened.)

**`tests/mrl/`'s `.rxt` files are the IMPLEMENTATION lane's own**, and the
D27 corpus of record for K23 is `tests/base/d27_k23_ambiguous_decomposition.rxt`
from the separate `d27k23` cell — the two do not overlap, deliberately. That
directory's CLAUDE.md carries the episode worth reading: a cell-isolated
author's file located a real gap in the first implementation that the
differential, the structural checks and the step-collapse acceptance cell all
agreed with, because all three were derived from the model the bug was in. An
instrument derived from an implementation can only find the defects that
implementation's own model admits.

**[M4.6f] (2026-08-17) — a twelfth section, `test-prefilter`, and the ONE
DELIBERATE DEPARTURE from the three-part shape every deny-family section
above uses.** `docs/dev/decisions.md` D46 requires every strategy-selection
point to be OBSERVABLE (a stamp) and FORCEABLE (a flag the artifact's own
stamp can be checked against, do-or-die on the impossible direction); the
`RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES` family already has both halves
for their own axes, and this section gives `fit.prefilter`
(src/opt/select_engine.c, §6.1/§4.7) the same pair — `RX_VM_PREFILTER`
(`"hybrid"`/`"none"`) and the `-fprefilter`/`-fno-prefilter` FORCE PAIR
(lib/pcrec.h; a force pair rather than a deny-only flag, because the axis is
ONE verdict per artifact, not a per-quantifier ladder step D47.3's DENY
reasoning applies to).

There is no `run_prefilterdiff.sh` sibling, and that is not an oversight:
this substep adds no new ALGORITHM needing a pcrec-vs-pcrec differential of
its own — the hybrid prefilter's correctness is already carried by
`test-vm`'s §3.7 differential and `test-mrl`'s ceiling-form coverage. What
was missing before this substep was purely the OBSERVABILITY and
CONTROLLABILITY layer on top of an axis that already existed, so one
structural script is the whole of what the row owes. Its independent
controls (matching the K24-lane convention that a check must be shown able
to go red) pair every stamp assertion with a read of the actual emitted
`_prefilter(` machinery, never the stamp text alone; per R28-1
(`docs/dev/reviews/2026-08-17-r28-mrl-landing.md`: ad-hoc, reverted
sabotages are not validation — MRL had to add S58-S63 retroactively for
exactly this), the two failing directions verified during development are
PERMANENT rows, `tests/mech/sabotages/S64_*.sh`/`S65_*.sh` (their own
`prefilter` arm in `tests/mech/run_sabotage_matrix.sh`, both confirmed
DETECTED — the do-or-die refusal removed, and the `rx_info.flags` mask
bits dropped; see `tests/mech/CLAUDE.md`'s "[M4.6f] S64-S65" section for
the measured fail counts).

**[ENG-BREP] (2026-08-16) — an eleventh section, `test-rungselect`.** The
REVERSE-DETERMINISTIC rung's suite, the same three-part shape as
`test-possessify` one rung down the ladder, and everything said below about that
section applies here with `-fno-revdet` in place of `-fno-possessify`. Two
things are specific to it and worth knowing before reading a failure.

**Denying this rung falls to LITERAL REPLICATION, which is the ground truth in
the strongest sense available anywhere in the project** (§5.1): `X{m,n}` on the
frames rung is not an approximation of `{m,n}` semantics, it is `{m,n}`
unrolled, and it is what shipped before the rung existed. So `run_rungdiff.sh`
needs no external oracle to have an opinion.

**Its count ceiling is 64, and that is a property of the GROUND TRUTH rather
than of the rung.** §5.1 suggests keeping the differential below the replication
knee at N ≤ 256; the binding constraint here is tighter and it is
`PCREC_MAX_VM_REPEAT_COPIES`, because the DENIED build is the one that
replicates. A pattern above it compiles on the rung and is REFUSED on the ground
truth, and the script reports that as a FAILURE rather than skipping — a ground
truth that cannot be built is exactly the blindness §5.1 discloses, and it
should be visible. Above the cap, the `.rxt` corpus and the oracles are what
check the rung.

**[ENG-BREP] (2026-08-16) — a tenth section, `test-possessify`.** The
possessification rung's `.rxt` corpus rides `test-corpus` like every other
module's; the two scripts this section wraps check what a `.rxt` file
structurally CANNOT. `run_possdiff.sh` is the row's primary validation
instrument: it compiles the same pattern twice — once with the rewrite, once
with `-fno-possessify` — links both artifacts into ONE translation unit, and
compares the span, every capture slot and the failure surface at every start
position. Because the denied build is the shipped semantics rather than an
approximation of them, a disagreement is a bug by construction. It carries a
NON-VACUITY control (a sweep in which nothing possessified compared identical
artifacts and measured nothing, and fails saying so), and `--corpus` derives
and additionally sweeps every `.rxt` corpus pattern the analysis gives a
positive verdict on. `run_possessify_tests.sh` asserts the artifact's
per-quantifier `<PREFIX>_VM_STRATS` stamp against the emitted machinery, D47.3's
do-or-die (no artifact may stamp POSSESSIVE under `-fno-possessify`, checked
against the ARTIFACT and never against the flag having been passed), and the
BYTE-IDENTITY gate: every corpus pattern with zero positive verdicts must emit
identical C with the pass on and off. Both scripts also join the `make
ubsan`/`make asan` both-axes lists. See `tests/possessify/CLAUDE.md` — it
records the two ways this suite's own instruments measured nothing at first.

**[M4.5b] (2026-08-15) — the count moves from nine script invocations to
eleven, and the section list from eight to nine.** `test-codegen` gains
`run_vm_identity.sh` (engine_m4.md §5.4's zero-regression gate: a capture-free
pattern's emitted bytes must not move now that a second emitter and a capture
AST node exist), joining the two scripts it already wraps under the same
"codegen structural checks" concept. `test-vm` is a NEW section wrapping
`tests/vm/run_vm_tests.sh` — the VM engine's two bounds, its artifact stamps,
its selection surface, and the capture oracle plus engine_m4.md §3.7's
differential. It is a section of its own rather than a codegen line because
what it asserts is behavioural, not structural: it compiles and RUNS matchers
against subjects, which no script in `tests/codegen/` does.

`make test-vm` runs the QUICK oracle sweep, which is the same one `make test`
runs. The full sweep — the fuzzer's trap-template shapes instantiated with
capturing groups under every quantifier — is `bash tests/vm/run_vm_tests.sh
full` and is a checkpoint-scale run, not an inner-loop one.

**[M4.5c] (2026-08-15) — `test:` is TWELVE script invocations, and two of them
moved sections.** `run_ir_listing.sh` is new (DD-8's program listing held to
the artifact it describes). More interestingly, `run_vm_identity.sh` MOVED
from `test-codegen` to `test-vm`, and `run_ir_listing.sh` joined it there
rather than beside it in `test-codegen` — for the measured reason this
document asks about whenever a section grows.

Both scripts LIVE in `tests/codegen/` (they are identity and structural
differentials, kin to `run_trie_identity.sh` by technique) but they RUN under
`test-vm`, because `make smoke` includes `test-codegen` and they cost 8.0s and
2.9s against that section's own 0.7s + 7.4s. Measured on the project box,
2026-08-15:

| target | on merged main | after the move |
|---|---|---|
| `make test-codegen` | 16.28s | **9.33s** |
| `make smoke` | **62.98s** | **54.76s** |

**Two findings in that table, and the second is not [M4.5c]'s.** First, the
move is what puts smoke back inside its 60s target. Second, smoke was ALREADY
OVER that target on the main this lane merged — 62.98s — and the dominant term
is `test-known-fail` at **23.26s**, a section that used to be nearly free.
The K18 ratchet runs the corpus harness, and the harness grew the
capture-expectation machinery at [M4.5a]; the ratchet now pays for it on one
`.rxt` file. That is worth someone's attention on its own terms and is
recorded here rather than fixed by this lane, which does not own the harness.

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
| `src/gen/emit_vm.c`, `src/opt/select_engine.c`, `A_CAP`'s parse hook | `test-vm` (which carries the §5.4 gate and DD-8's listing check), `test-codegen`, `test-parse` | test-vm is where a wrong capture span or a broken bound shows up, and it is the ONLY section that runs a VM artifact against subjects; the §5.4 gate is what catches a capture-free pattern's bytes moving, which no correctness test can see because the VM computes the same spans; test-parse's ast-identity check is the D31 erasure's own net |
| `src/ir/*` (`nfa.c`, `dfa.c`) + `src/opt/*` (`minimize.c`) + `src/gen/*` (`emit_dfa.c`) | `test-corpus`, `test-codegen` (includes the trie identity differential and the §5.4 VM gate), `test-vm`, `bench` | corpus is correctness of what the emitted matcher actually matches; codegen asserts the optimization signatures (skip tables, fast paths, minimization) are structurally present, per R2-PR3's finding that these can be silently disabled with zero other signal; bench guards the throughput/compile-time budgets these components produce |
| `src/core/*` (`compile.c`, `arena.c`, `sb.c`) | all of the above, plus `test-thread` | `compile.c` is `pcrec_compile()`'s entry point and nearly every suite goes through it; `test-thread`'s TS-3 half specifically exercises concurrent `pcrec_compile()` calls, which only a change here would plausibly break |
| `cli/main.c` | `test-cli`; also `test-reject`/`test-registry` if the change touches how errors or `--list-syntax` are surfaced | cli/'s own suite is the CLI-surface test; the other two invoke `build/pcrec` as a subprocess and would show a broken diagnostic path |
| `lib/pcrec.h` | `test-cli` (the library-API smoke test), `test-thread` (both TS-2 and TS-3 call the public API directly) | |
| `src/gen/enc/*` (the encoding backends), `pcrec_options.encoding`, the emitted residual entries | `test-encseam`, `test-codegen`, `test-cli` | encseam RUNS docs/spec/match_api.md §3.1's find-all loop through `<prefix>_next_pos` against a python3 `re` oracle, on both engines — it is the only suite that runs a find-all loop at all; codegen carries the DD-12 (7) structural check that no engine body calls a residual entry, which no behaviour test can see (under the byte backend the residual is the identity, so a hot path routed through it matches identically); cli pins the `-e`/`--encoding=` surface and the utf8 refusal |
| `tests/mech/*` (sabotage definitions) | `make mech` (not a `make test` section — its own top-level target, run manually per its own CLAUDE.md when a sabotage table's figures are in doubt; the full matrix measures ~50 min at `PROCS=4`, 2026-08-21 — see "Sanitizer + lint battery" below for the stale "~6 minutes" figure's correction and the [TT-3] `CCACHE=1` toggle's own measured warm-row number) | |

### `make smoke`

A measured, sub-60-second inner-loop subset, sized from the table above —
never vibes. Runs the real section targets it lists, not a weakened variant
of any of them.

**Composition**: `test-cli`, `test-registry`, `test-parse`, `test-codegen`,
`test-known-fail`, `test-thread`. (Unchanged at [M4.5c] — what changed is what
`test-codegen` CONTAINS; see the re-check above, and note the measured total
has moved a long way from the ~32s recorded below, mostly in
`test-known-fail`.) Deliberately excludes the three slow
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

## The atomic landing gate ([M6.4.4], 2026-08-22) — OPT-IN, and its archived result

`tests/codegen/run_atomic_identity.sh` is module `atomic-groups`' byte-identity
gate. It is NOT part of `make test`, and not on the `ubsan`/`asan` lists
either. Run it on demand:

    make test-atomic-identity
    ATOMIC_IDENTITY_REF=<sha> make test-atomic-identity   # against a moved base

**WHY IT IS OPT-IN.** The design ruled it a ONE-SHOT LANDING GATE (atomic
groups design §11.2, §14 item 8) and [M6.4.2] did not honour that when it
wired the script into `test-atomic`. What it asserts is a claim about a
MOMENT — that the module changed no atomic-FREE pattern's emitted bytes when
it landed — measured against the PINNED PRE-MODULE COMMIT `e2f81d5`. That pin
is exactly what makes it one-shot: every run re-answers the same landing
question, and the answer cannot move unless someone edits pre-module code.

**IT IS NOT DELETED AND MUST NOT BE.** It still gates the module's own
re-landings (a rebase onto a moved base, a revert-and-reapply), and it is the
`atomicidentity` arm of the sabotage matrix, where it scores rows the
differential cannot.

**THE ARCHIVED RESULT** — so the landing claim survives without being
recomputed. Measured 2026-08-22 on `lane/agfix` at the [M6.4.4] fix, against
a reference compiler built from `e2f81d5`:

| arm | same | differing | refused by both | refusal mismatch |
|---|---|---|---|---|
| default | 1312 | 0 | 137 | 0 |
| `--engine=vm` | 1313 | 0 | 136 | 0 |

Corpus 1565 patterns; 116 atomic, 1449 atomic-free. POSITIVE CONTROL: the
reference refuses all 116 atomic patterns, so a zero-difference result is a
measurement against a genuinely different compiler rather than a build
compared with itself. The [M6.4.2] landing measured the same claim at
1311/1312 same, 0 differing — the counts moved only because [M6.4.4] added
atomic-free patterns to the corpus it extracts from.

**RUNTIME**, measured on this box (12 cores, 2026-08-22): 71 s standalone. It
was never the expensive part of `make test` — see the wall-time note in
"Tiered testing" — so this move is a correctness-of-composition change, not a
performance one, and it should not be reported as a speed-up.

## The backrefs landing gate ([M6.5.2], 2026-08-22) — OPT-IN, three axes, and its archived result

`tests/codegen/run_backref_identity.sh` is module `backrefs`' byte-identity
gate, and the second in the tree whose reference is a PINNED COMMIT rather than
a `-D` knob. It is NOT part of `make test`. Run it on demand:

    make test-backrefs-identity
    BACKREF_IDENTITY_REF=<sha> make test-backrefs-identity   # a moved base

**WHY IT IS OPT-IN AND WHY THE REFERENCE IS A COMMIT** — ASK-4, ruled with
R32, on the same reasoning `test-atomic-identity` was ruled on one module
earlier. It asserts a claim about a MOMENT, and NO STAGE OF THIS MODULE RUNS ON
THE CONTROL POPULATION: a backref-free pattern creates no `A_BREF`, stamps no
VM_ONLY row, marks no group, allocates no pending slot and adds no residual
entry to the artifact's mask. A `-D` knob would therefore gate DEAD CODE and
the sweep would report 100% identical no matter what was sabotaged — the
blindness `tests/mech/CLAUDE.md` records, in its purest form.

**THREE AXES, and the third is this module's own.** Under `--no-captures` the
parser now builds an `A_CAP` for EVERY numbered group and deletes the
unreferenced ones at end of parse — because §6.3 rules that a group a
BACKREFERENCE names keeps its internal slots and reports none, and "will any
reference name this group" cannot be answered at the opening paren (a FORWARD
reference makes it unanswerable there in principle). So "the tree is what it
always was" is a claim about a DELETION, and this axis is what turns it from an
argument into a measurement. **It earned its keep on the first run**: the
resolution pass's early return skipped the strip for a backref-FREE pattern, so
every `--no-captures` artifact with a group emitted different bytes while
answering identically.

**IT COMPARES PAST D37's THREE FEATURE-STAMP LINES**, with the filter asserted
to remove EXACTLY three from each side — `tests/cli` case10's precedent, not a
loosening. `render_modules` renders the enabled module list by walking the
registry in TABLE ORDER, and this module adds two rows naming module
`recursion` at `RK_ESC 'g'` (before the `RK_GROUP` rows where that name
previously first appeared), so under `--features all` the stamp's list moves
`recursion` earlier. The mask and the gate state are unchanged, D37's own
promise is order-independent, and `tests/cli` case14 pins the stamp's content.

**THE ARCHIVED RESULT** — measured 2026-08-22 on `lane/brimpl`, against a
reference compiler built from the pinned pre-module commit `5286265`:

| arm | same | differing | refused by both | refusal mismatch |
|---|---|---|---|---|
| default | 1501 | 0 | 149 | 0 |
| `--engine=vm` | 1502 | 0 | 148 | 0 |
| `--no-captures` | 1501 | 0 | 149 | 0 |

Corpus 1774 patterns; 124 backref-bearing, 1650 backref-free. POSITIVE CONTROL:
the reference REFUSES all 124, so a zero-difference result is a measurement
against a genuinely different compiler rather than a build compared with
itself.

## The recursion landing gate ([DD-14], 2026-08-24) — OPT-IN, FOUR axes, and its archived result

`tests/codegen/run_recursion_identity.sh` is module `recursion`'s byte-identity
gate, and the third in the tree whose reference is a PINNED COMMIT rather than
a `-D` knob. It is NOT part of `make test`. Run it on demand:

    make test-recursion-identity
    RECURSION_IDENTITY_REF=<sha> make test-recursion-identity   # a moved base

**IT LANDED IN TWO STEPS ON PURPOSE.** Wave D landed the DEFAULT-axis SEED so
the claim had a standing home in the tree rather than living only in a lane's
scratch run, with its own header saying wave E was expected to GROW it. Wave E
grew it: the other three axes, the D37 stamp strip, a per-axis positive
control, and the classifier's own self-test. Nothing about the reference, the
pin or the classification rule changed in kind.

**WHY IT IS OPT-IN AND WHY THE REFERENCE IS A COMMIT** — the same ruling
`test-atomic-identity` and `test-backrefs-identity` carry (ASK-4). NO STAGE OF
THIS MODULE RUNS ON THE CONTROL POPULATION: a call-free pattern builds no
`A_CALL`, and the call-graph pass returns immediately when `pcrec_has_call` is
false. A `-D` knob would gate DEAD CODE and the sweep would report 100%
identical no matter what was sabotaged — the blindness `tests/mech/CLAUDE.md`
records, measured at 1175/1175 on one wave.

**THE PIN IS `ac4917d`, AND IT IS NOT A PRE-`[DD-14]` COMMIT.** It is the last
commit whose `src/` carries the `A_CALL` KIND with no PRODUCER anywhere
reachable — wave A2's tagged-union member and walker arms, before wave B+C's
ports and wave D's `\g` wiring. That choice is what lets this gate have NO
RETIREMENT GUARD where its three siblings need one: those three predate
`[DD-14]` wave A's ABI event (`PCREC_ERR_RECURSE`, `ERR_FLOOR` −4 → −5,
`PCREC_ERR_INTERNAL`, main `0c75c96`) and no pin before it can ever again be
byte-identical to a subject tree that carries it. `ac4917d` is POST that event
by construction, so the event is baked into both sides of every comparison and
cannot retire this gate. A future ABI break past `ac4917d` would need its own
guard.

**FOUR AXES** (design `subroutines_design.md` §9.1, mirroring the `[M6.6.2]`
ASK 4 ruling): `default`, `--engine=vm`, `-fno-prefilter` and `--no-captures`.
The third is not ceremonial — §8.2 forces the prefilter OFF for a call-bearing
pattern, which is a touch on `select_engine.c`, and EVERY pattern goes through
that file; the axis that pins the prefilter constant is the one that localises
a predicate that over-fires. The fourth is the backrefs-precedent axis: §4.3
edits `pcrec_bref_mark`'s union, which is `--no-captures`' own machinery, and a
mark-set edit that over-marks makes `--no-captures` keep slots it used to
delete.

**THE POSITIVE CONTROL RUNS ON EVERY AXIS**, not once: §9.2's control is that
the pre-module reference REFUSES every call-bearing pattern (`ctl_bad == 0 &&
ctl_ok == nc`), and "refuses" is an answer the axis flags could in principle
change, since `--no-captures` and `-fno-prefilter` both reach `select_engine.c`
where a refusal lives. Without it the gate's headline claim — "a call-free
pattern is unmoved" — is trivially true and worth nothing.

**THE CLASSIFIER MASKS CHARACTER CLASSES AND TESTS ITSELF.** Design §0.3 item 9
is the census's own MEASURED instrument defect: a naive `\g<` scan counts
`tests/backrefs/octal_class.rxt`'s `^[\g<1>]$`, where the class doorway makes
those four bytes literal escapes, as a call. The classifier inherits the defect
unless it masks classes, so a 19-row self-test runs BEFORE it classifies
anything — `^[\g<1>]$` and `^[(?&x)]$` are call-free, `a[b]\g<1>` is not, `(?>`
is an atomic group and not a call (the row this classifier's first draft got
wrong), and an unrecognised `(?` tail FAILS SAFE toward the call bucket.

**IT COMPARES RAW AND STRIPPED, AND REPORTS THE DIFFERENCE.** The ruled
comparison (§9.1) is byte-identity past D37's three feature-stamp lines, with
the filter asserted to remove exactly three from each side. This gate makes
BOTH comparisons and counts `stamp-moved` — the pairs that differ RAW and agree
STRIPPED, i.e. whose only difference is the stamp. It is 0 on every axis, and
unlike `backrefs` it is *expected* to be: module `recursion`'s registry rows
PREDATE the module (P4 measured all 26 as VM_ONLY before any producer existed),
so `render_modules`' first-row walk never moved the name, where `backrefs`' two
new `RK_ESC 'g'` rows DID move it. A nonzero `stamp-moved` is a FAILURE here
rather than a note; wave F adds registry rows and must say so in its commit.

**THE ARCHIVED RESULT** — measured 2026-08-24 on `lane/srE`, against a
reference compiler built from the pinned commit `ac4917d`:

| axis | same | differing | refused by both | refusal mismatch | stamp-filter-bad | stamp-moved |
|---|---|---|---|---|---|---|
| `default` | 2200 | 0 | 242 | 0 | 0 | 0 |
| `--engine=vm` | 2201 | 0 | 241 | 0 | 0 | 0 |
| `-fno-prefilter` | 2201 | 0 | 241 | 0 | 0 | 0 |
| `--no-captures` | 2200 | 0 | 242 | 0 | 0 | 0 |

`checks passed: 8  checks failed: 0`, rc 0. Corpus 2610 patterns; **168
call-bearing** (floor 60), **2442 call-free** (floor 700). Classifier self-test
23/23. POSITIVE CONTROL on all four axes: the reference REFUSES all 168
call-bearing patterns, `ctl_bad == 0` and `ctl_ok == 168` on each.

**THE CALL-BEARING POPULATION MOVED 136 → 168 WHEN WAVE F LANDED**, and the
mechanism is worth naming because it is the gate working rather than the gate
drifting: D71 item 4 made `(?(DEFINE)` module `recursion`'s, so the classifier
grew a negative lookahead in its conditional arm and every DEFINE-bearing
pattern — INCLUDING four with no call in them at all — moved out of the bucket
required to be byte-identical and into the bucket the reference must refuse.
The gate found those four itself, as refusal mismatches, before the classifier
was fixed. The self-test carries F's arm as four of its rows, so the fix is
exercised rather than merely present: `^[(?(DEFINE)a)]$` checks that the class
mask reaches the newest doorway too, and `(?(DEFINE)(?<g>a))b` is the sharp one
— two `(?` occurrences, one unrecognised and one recognised — which pins the
ANY-occurrence rule against a classifier that reads the last verdict or lets a
recognised inner construct rescue the pattern.

**EXERCISED IN THE FAILING DIRECTION**, which is the half a green run cannot
supply (measured before the wave-F rebase, on the 2439-pattern call-free
population — the plant is in a path every call-free artifact takes, so the
reading does not depend on which corpus generation it ran against). One byte of
an emitted comment was changed on a path every call-FREE artifact takes (`emit_dfa.c`'s `"/* Generated by pcrec. Pattern: "` → `",
Pattern: "`), and the gate was re-run whole: `checks passed: 4  checks failed:
8`, rc 1, every axis at `same=0` (`default` 2199 differing, `--engine=vm` 2200,
`-fno-prefilter` 2200, `--no-captures` 2199). The four PASSes are the four
positive controls, and their staying green is the right shape rather than a
hole — the control is a claim about the REFERENCE and the planted byte was in
the SUBJECT, so a control that went red would mean the gate's two halves were
reading each other. Each axis fired its floor check as well, which is a second
and independent reason the run is red. Reverted before the green run above.

**THE SECOND CONTROL IS NOT HERE AND IS NOT WAVE E'S.** §9.2's SPLICE-vs-LINKAGE
`A == B` over the corpus needs the `-fno-splice-calls` axis §6.3's linkage rule
introduces, which is wave G's. §9.3's sabotage rows carry that load until then.

## The backrefs behavioural suite ([M6.5.2], 2026-08-22)

`make test-backrefs` runs two scripts concurrently, and they are separate
because they ask different KINDS of question.

**`tests/backrefs/run_backref_diff.sh` — ten sections, five EXACT population
guards.** §1 sweeps 35 patterns x 91 subjects x every startpos in [0, n] against
libpcre2, comparing the match span AND EVERY GROUP SPAN — the group spans are
the sharper detector here, because the re-entry family contains subjects on
which the outer span agrees and the group does not. §2 asserts the DEFAULT
selection and `--engine=vm` agree (both are VM artifacts, but the default is
where the prefilter was forced OFF). §3 counts the RE-ENTRY population, which
is where publish-at-close is observable AND NOWHERE ELSE — a 5,808-cell
arm-vs-arm sweep found the backref-FREE control at 0 divergences in BOTH
publication disciplines. §4 is the `--no-captures` arm. §5 drives the three
entry points against the `\G(?:PAT)`-wrapped oracle. §6 is the find-all loop.
§7 asserts the `--engine=dfa` refusal BY NAME **with its OCTAL control**:
`(a)\10` is the byte 0x08 and must compile to a pure DFA, which is the
per-NODE half of SR-8's stamping rule. §8 is the SPAN-DIVERGENCE section. §9 is
the fold agreement. §10 (added 2026-08-22) is STRUCTURAL: it reads the
empty-iteration guard off the ARTIFACT for four unbounded-over-nullable-
backreference fixtures and asserts its ABSENCE on three bounded controls.

**§10 EXISTS BECAUSE A BEHAVIOURAL CELL COULD NOT SEE ITS PROPERTY.**
`vm_nullable(A_BREF)` is a static answer, but the guard it arms only DOES
anything when the referenced group publishes an EMPTY capture — a property of
the SUBJECT. The corpus held the shape (`^(a*)\1*$`) with every subject making
group 1 non-empty, so sabotage row S107 scored UNDETECTED in the 118-row matrix
on 5edba64 against a module that was CORRECT. The fix was both halves: the
corpus gained the "EMPTY CAPTURE UNDER AN UNBOUNDED QUANTIFIER" block
(numeric.rxt), and this section asks the pattern-only question that no subject
can silently satisfy. The bounded controls are what make it falsifiable —
`\1{3}` is a repeat over the same nullable body and correctly emits NO guard,
so "every backreference in a repeat body has a guard" would be green on a
compiler that emitted one unconditionally.

**§8 CORRECTS THE DESIGN, and the correction is worth reading.**
`backrefs_design.md` §11.2 names three cells as the span-divergence population;
measured here, only ONE of them is a DETECTOR. A span DIFFERENCE is not enough:
the hybrid uses the prefilter's span START to seed `attempt_position` (and the
emitted loop re-asks it on every retry, so a start that is too LOW costs
attempts and no answers) and its span END as the MRL ceiling. A planted
prefilter changes an ANSWER only when the erasure's window FAILS TO CONTAIN the
true match. On `11-1` for `([0-9]+)-\1` (true (1,4), erased (0,4)) and on `ba`
for `(a*)b\1` (true (0,1), erased (0,2)) the window contains the answer and the
VM still finds it — so those two would have scored the sabotage as UNDETECTED
while looking like coverage. The three subjects now used were found by SWEEPING
the family space for the containment property, and come from three different
families.

**BOTH SCRIPTS JOIN THE SANITIZER LISTS, on BOTH AXES.** They are on `make
ubsan`'s and `make asan`'s suite lists, and — unlike the atomic differential
beside them, which hardcodes its generated-code compile flags — they read
`GENCFLAGS` and `LIBPCREC` from the environment, so the emitted matchers they
compile and RUN are instrumented too. That is K27's lesson applied rather than
rediscovered: the battery's generated-code axis only ever sees what some script
actually runs, and the emitted backreference compare does pointer arithmetic
over subject offsets nothing else in the tree's generated code does.

**`tests/backrefs/run_dupnames_diff.sh` — the resolution rule, checked THREE
ways.** The `.rxt` cells separate four candidate readings ("first by number",
"last set", "any one of them", "first NON-empty") and each is caught by exactly
one cell. What a hand-picked set cannot show is that no FIFTH rule fits, so this
sweeps name-runs of size 1..4 with EVERY SUBSET participating and checks (1)
pcrec against libpcre2 on 828 cells, (2) an INDEPENDENTLY WRITTEN model of the
rule — implemented in python from the rule's own sentence — against libpcre2 on
158 cells, and (3) both populations EXACT. Failing direction demonstrated: the
model perturbed to "last set" disagrees with libpcre2 on 32 of 158.

**The 65,536-pair FOLD AGREEMENT (§9)** is the mechanism R32 E8 asked for.
pcrec's ASCII fold exists TWICE and cannot be made to exist once — a parse-time
class widener (D23) and match-time arithmetic in the encoding residual, because
a caseless backreference's operand is subject text nobody has seen at compile
time. `fold_agreement_check.c` compares the SHIPPED
`rx_bref_match_caseless` — compiled out of an artifact pcrec actually emitted —
against `pcrec_ascii_fold` (src/core/fold.c), which `cls_casefold` derives its
widening from. Ordered PAIRS, not the 52-byte set, because equality under a fold
is a RELATION and two sides could agree on WHICH bytes fold while disagreeing
about what they fold TO.

## Internal parallelism and section composition ([TT-2], 2026-08-15)

TT-1 gave `make test` PROCS-based parallelism for the corpus (`test-corpus`,
via `tests/harness/run.sh`'s own file-level worker mechanism). TT-2 extends
the same idea to the rest of `test:`'s section targets, on two axes: sharding
work WITHIN a single script (reject), and running INDEPENDENT scripts within
one section CONCURRENTLY (codegen, vm). A third axis — composing the section
targets themselves under `make -j` — falls out of `test:` already being
prerequisite-based (see "Tiered testing" above) rather than a flat recipe.

Every path here follows the same discipline `tests/harness/run.sh`'s own
PROCS mechanism set: **a lost or crashed worker is a HARD FAILURE, never
silently read as a pass** — validated for each new path below by planting a
`kill -9` mid-run and confirming a loud, nonzero-exit failure.

### `test-reject`: call-index sharding

`tests/reject/run_reject_tests.sh` has one file with hundreds of independent
`timeout ... $PCREC ...` checks (`reject`/`accept`/`reject_gated`/`pinned`/
`row_reject`), not many files — there is no natural file-level split the way
the corpus has one. Instead, every check call increments ONE shared
`callidx`, and only does its real work (the subprocess invocation and every
counter it drives) when `callidx % SHARD_TOTAL == SHARD_INDEX`.

`PROCS=1` (the default) makes `SHARD_TOTAL=1`, so `callidx % 1 == 0` always
— every check runs, in the same order, exactly as before; this path is
byte-for-byte unchanged from the pre-TT-2 script. `PROCS=N>1` re-invokes the
whole script N times as shard workers (`REJECT_SHARD_INDEX`/
`REJECT_SHARD_TOTAL` env vars), each with its own `mktemp -d` workdir,
waits, and aggregates: counters are summed, each shard's slice of `$seen`
(the MANIFEST's dedup set) is concatenated, and the unchanged
duplicate-check/MANIFEST/final-count tail then runs ONCE against the true
aggregate. A shard that produces no machine-readable result block (crashed,
timed out, killed) is counted as a hard failure, never silently dropped from
the denominator.

Each shard writes its result block (`shard_pass:`, `shard_nrej:`, ...) to
its OWN file (`REJECT_RESULT_FILE`), separate from the `.out`/`.err` the
parent replays for a human to read — an earlier version of this mechanism
wrote the result block to the same stream it displayed, which leaked ~80
lines of shard bookkeeping into `make test-reject`'s visible output at
PROCS>1; fixed before landing.

**Not byte-identical at PROCS>1**: shard output is replayed in shard order,
not call order, so individual `PASS`/`FAIL` lines interleave differently
than a serial run's. The underlying set is exactly conserved (verified with
`LC_ALL=C sort` — a locale-default `sort` was internally inconsistent run to
run on this file's punctuation-heavy lines and is not a safe comparison tool
here), and the `== Summary ==` block's format and figures are unchanged
either way, since it is printed once, by the parent, from the aggregate.

Measured on the project box (12 cores): 59.5s at `PROCS=1` -> ~5.8s at
`PROCS=12`.

### `test-codegen` / `test-vm`: independent-script groups

`tests/lib/run_group.sh` runs N independent shell commands concurrently as
one Makefile recipe, with the same hard-fail-on-lost-worker discipline. It
takes `GROUP_PROCS`: `1` runs the scripts serially in argument order with no
backgrounding at all (byte-for-byte the old flat multi-line recipe); any
other value runs every script at once (there are only ever 2-3 scripts per
group here, never enough to want real job-pool throttling). Each script's
complete stdout+stderr is captured to its own file and replayed as one
contiguous block, in argument order, once every script has finished, so
output never interleaves mid-line; a script whose wrapping subshell dies
before it can record an exit code is a HARD FAILURE distinct from an
ordinary nonzero exit, and is named as such.

`test-codegen` (`run_codegen_tests.sh` + `run_trie_identity.sh`) and
`test-vm` (`run_vm_identity.sh` + `run_ir_listing.sh` + `run_vm_tests.sh`)
both use it, with `GROUP_PROCS=$${PROCS:-$$(nproc)}` — the same `PROCS`
knob every other TT-2 path honours, so `PROCS=1 make test` serializes
everything uniformly. `test-vm` was the actual long pole under `make -j
-Otarget test` (three scripts run sequentially in one recipe, ~32s), more
so than `test-known-fail`'s ~23s single-file cost, which is not
parallelizable (one file, nothing to shard).

Measured on the project box: `test-vm` 30.4s -> 14.9s (PROCS=1 vs default);
`test-codegen` 10.1s -> 8.7s (the group's own long pole, `run_trie_identity.sh`
at ~10s, dominates either way — the win here is smaller by construction).

### Section composition: `make -j -Otarget test`

`test:` is prerequisite-based (`test: test-corpus test-cli test-reject ...`,
see "Tiered testing" above), not a flat multi-line recipe, specifically so
GNU make's own dependency engine can parallelize it: `make -j$(nproc)
-Otarget test` runs the ten independent section targets concurrently.
`-Otarget`/`--output-sync=target` buffers each target's output and prints it
as one contiguous block when that target finishes, so nothing interleaves
mid-line even though the targets themselves run concurrently — the same
legibility rule every other TT-2 path follows. No suite reads or writes
another's output (each has always used its own `mktemp -d` workdir and only
ever reads `build/pcrec`/`build/libpcrec.a`), so this is safe by the same
argument the PROCS mechanisms above already rely on. Plain `make test`
(no `-j`) is unaffected: GNU make runs a target's prerequisites in listed
order without `-j`, so it is still the same ten scripts run back to back,
same order, same claim.

Measured on the project box (12 cores): serial section sum (each target's
own runtime added up) is on the order of 6-7 minutes; `make -j12 -Otarget
test` completes in ~43-45s. This is noticeably more than the single longest
target under composition (`test-vm` at ~15s after its own internal
parallelism, above) — the gap is CPU oversubscription, not a missed
optimization: `test-corpus` and `test-reject` each fan out to `PROCS=nproc`
workers internally, and under `-j$(nproc)` up to nine OTHER section targets
can be runnable at the same time, so peak concurrent process demand well
exceeds the box's 12 cores. Total wall time is bounded by total CPU work
divided by available cores, not by the critical path alone. `PROCS=1 make
-j$(nproc) -Otarget test` would remove the internal fan-out's contribution
to that oversubscription while keeping section-level concurrency, for a
board with fewer cores or a noisier one — not benchmarked here because the
default composition already lands the full suite comfortably under a
minute, which was the point.

Verified: `make -j$(nproc) -Otarget test` and `PROCS=1 make test` both green,
with every suite's population exactly conserved (corpus 1679, cli 247,
reject 528, codegen 38, trie identity 7, registry 168, PC-3 163, vm 19,
thread 8, known-fail 1 deferred bug still failing as expected).

### `test-cli` / `test-registry`: considered, declined

The TT-2 plan row names these two alongside reject/codegen/vm. Both were
measured (`test-cli` 7.2s, `test-registry` 14.6s across four sub-phases:
`registry_check`, `compliance_section.py` x2, PC-3, PC-4/`run_pc4.sh`) and
both declined, for the same reason in each case: neither is on the critical
path under `make -j -Otarget test` — the ceiling there is `test-vm` (~15s
after its own TT-2 fix) and `test-known-fail` (~23s, one file, not
parallelizable), so shaving either script's own runtime would not move the
suite's overall wall time at all. `run_registry_tests.sh` in particular is
not `test-reject`-shaped for a callidx-style split (its 168+163 checks run
inside two compiled C binaries, one process each, not as hundreds of
independent shell-level calls) and is a dense, heavily correction-scarred
file (its own CLAUDE.md and the R9/C1 series comments throughout) where a
control-flow restructuring risks reintroducing exactly the "coverage
silently changed and nothing compared" failure mode that file has been
fixed for at least twice. Splitting its four phases into a `run_group.sh`
call remains possible future work if `test-registry` (or `test-cli`) ever
becomes the actual long pole — re-run this section's measurements first;
that is the trigger, not the plan row's original naming.

### mech's own PROCS mechanism (pre-existing, not TT-2 work)

**Measured setting (2026-08-23, [TT-8], after the PROCS-leak fix and the
[TT-6] timeout swap): `PROCS=6 make mech`** — full 118-row matrix 28:43 at
PROCS=6 vs 36:36 at PROCS=4 on the same HEAD (6b0ef30), rows byte-identical
except S18-tsv-empty's reject figure, which is shards+1 (K30, a reject-script
sharding property, not a detection difference). The inner suites get
INNER_PROCS = ncpu/PROCS explicitly; at PROCS=1 the inner suites now shard at
ncpu (a behaviour change from the leaked `1`, same figures).

`tests/mech/run_sabotage_matrix.sh` already had `PROCS=N` support (added
2026-08-12, three days before this row opened) — see "Running the tests"
above: N sabotages built and run concurrently, each in its own scratch tree
(so parallel rows need, and already get, per-row build dirs), rows merged
in sabotage-listing order so the matrix stays byte-identical to a serial
run's, and the row-count guard against the sabotage-definition count applies
in both modes. No new implementation work was needed for TT-2's mech item;
this note exists so a future reader of the TT-2 plan row does not go
looking for parallel mech and conclude it is missing.

### [TT-8] the PROCS leak into inner suite sharding, fixed (2026-08-23)

`run_sabotage_matrix.sh`'s `PROCS` is documented above as ROW-level
concurrency only. It was not: two of the suite arms it dispatches per row
— `reject` (`tests/reject/run_reject_tests.sh`) and `harness`
(`tests/harness/run.sh`) — read `PROCS` from **their own environment** to
size their own internal worker count (the reject-shard dispatch and the
per-file dispatch respectively, both pre-existing mechanisms unrelated to
mech). The driver invoked both without overriding `PROCS` on their command
lines, so whatever `PROCS` the driver itself was started with reached them
UNDIVIDED — a bash quirk where a variable already in a process's
environment keeps its export attribute through a plain reassignment
(`PROCS="${PROCS:-1}"` does not clear it). `make mech`'s own default
(`PROCS=${PROCS:-$(nproc)}`, Makefile) sets exactly this up: at
`PROCS=4`, every concurrently-running row that reached `reject` or
`harness` ALSO tried to shard 4-way internally — oversubscription on top
of the row-level concurrency the box was actually sized for.

**Measured directly**, not only read from the dispatch code
(`docs/dev/chain_profile.md` "(b) mech per-row scoping" named the risk
from reading it, and flagged that it had not been confirmed live): a
`ps`/`/proc/<pid>/environ` sample taken during a single-row `PROCS=4 bash
tests/mech/run_sabotage_matrix.sh S15` run showed `run_reject_tests.sh`
receiving `PROCS=4` from the environment and spawning 4
`REJECT_SHARD_TOTAL=4` workers — from a run that named exactly ONE
sabotage, so the leak does not need the row-level scheduler (which never
even engages for a single named row) to fire.

**Fix**: `INNER_PROCS`, computed exactly like `JOBS` already is
(`ncpu / PROCS`, minimum 1) and passed EXPLICITLY as `PROCS="$INNER_PROCS"`
on the `reject` and `harness` arms' own command lines — never left for the
environment to supply. At outer `PROCS=4` on this box's 12 cores,
`INNER_PROCS` is 3: the same sample re-taken post-fix shows
`run_reject_tests.sh` receiving `PROCS=3` and spawning
`REJECT_SHARD_TOTAL=3` workers, matching `JOBS`'s existing division for
the build step.

**Validated same-figures, not just same-mechanism**: `S15`
(`reject registry pc3`) and `S107` (`harness brefdiff`, `harness` scoped to
one file) each ran three ways — leaked `PROCS=4` (pre-fix), the default
with no `PROCS` set at all (genuinely serial, both pre- and post-fix since
1 leaked undivided equals 1 computed), and fixed `PROCS=4` — and all three
produced byte-identical per-suite fail/pass figures and verdicts
(`S15`: `reject:17fail/542pass,registry:3fail/177pass+compliance-FAIL,
pc3:0fail/168pass`, DETECTED; `S107`: `corpus:9fail/79pass,
brefdiff:4fail/10pass`, DETECTED, in all three runs). A full-corpus
`harness` row (`S66`) was confirmed by the same `ps`/environ method to
divide correctly post-fix (parent `run.sh` receiving `PROCS=3`, dispatching
3 file-workers instead of the pre-fix leaked 4) but was not run to
completion in either form under this fix's own single-row validation
budget — a full-corpus row's own wall time is a separate, larger
measurement (see "One mech row: cold/warm/plain, measured" above and
`docs/dev/chain_profile.md`), owed to the PROCS re-validation sweep this
fix unblocks (below), not to this fix's own correctness claim.

Note the asymmetry this creates at outer `PROCS=1` (the default, or an
explicit `PROCS=1`): `INNER_PROCS` is `ncpu/1 = ncpu`, so a LONE row now
gets the whole box for its `reject`/`harness` arms too — a real change
from the pre-fix behavior (nothing was in the environment to leak, so the
arms defaulted internally to serial), and the same precedent `JOBS`
already set for the build step at `PROCS=1`. The `S15`/`S107` measurements
above cover exactly this case (their "default, no `PROCS` set" runs) and
found no figure change, which is what licenses treating it as a speed-only
change rather than a behavior change.

**PROCS re-validation, still owed** (`docs/dev/plan.md` [TT-8]): with the
leak fixed, `docs/dev/chain_profile.md`'s standing `PROCS=4` figure (set
from a 20-sabotage measurement on 2026-08-12, never re-measured against
the current 118-row matrix or against higher `PROCS` on this box's 12
cores) needs a fresh sweep — a ~20-row sample spanning every target class
(harness-targeted, reject, the four full-corpus `harness` rows, script-only)
at `PROCS=3`, `4`, `6`, each under `/usr/bin/time -v` with logs under
`build/`, then ONE full 118-row matrix at the chosen setting as the
chain's mech "after" figure. This is box-exclusive, serialized-with-other-
lanes work (docs/dev/plan.md's BOX RULE) and is the manager's run, not a
lane's — see `docs/dev/tt8_mech.md` for the exact commands.

### D69 — the mech re-run policy is TIERED, and how to run it (2026-08-23)

The full 118-row matrix costs ~60 min per run (`docs/dev/chain_profile.md`)
and was never a documented merge obligation — this file's own table above
says "run manually … when a sabotage table's figures are in doubt". D69
(`docs/dev/decisions.md`) rules a cheaper default, on the argument that a
row's verdict is a property of the pair (compiler, corpus) and flips only
when (1) its `SAB_HARNESS_TARGET` changes (exact, grep-able), (2a) its own
anchor drifts (caught STATICALLY, seconds, by
`scripts/m6read_check_sab_anchors.py`, already on the merge bar), or (2b) a
compiler change elsewhere masks or unreaches the sabotaged path (the S108
single-site shape — not derivable from a diff, only a run finds it).

**The four tiers** (Frank: "I am ok with this risk"):

| what changed | run |
|---|---|
| docs / test-infrastructure only | the anchor tripwire only |
| tests changed, src unchanged | tripwire + the rows whose target is among the changed files (single-row runs) |
| src changed | tripwire + the rows whose `SAB_FILE` or target changed |
| module or milestone CLOSE | the FULL matrix (where 2b's risk concentrates, and where a lane's new rows run anyway) |

An UNDETECTED row from any of these tiers is a finding diagnosed by
measurement, per the 2026-08-22 lesson (`tests/mech/CLAUDE.md`'s "A
sabotage that zero checks catch is the finding, not a bug") — never argued
from reading the sabotage's own description.

**The tripwire**, every tier:

    python3 scripts/m6read_check_sab_anchors.py

**Finding the rows for a changed path**, tiers 2 and 3 —
`tests/mech/rows_for.sh` lists the `SAB_ID`s whose `SAB_FILE`,
`SAB_FILE2` (the [M6.5.2-FIX] second-site field) or `SAB_HARNESS_TARGET`
matches a given path at a path-component boundary (a directory argument
matches everything under it, and vice versa); a path matching no row
prints nothing and exits 0 (success — the tripwire alone covers it), a
malformed sabotage definition is a FATAL exit 2 naming the file, never a
silent skip:

    for r in $(bash tests/mech/rows_for.sh path/one path/two ...); do
        bash tests/mech/run_sabotage_matrix.sh "$r"
    done

It deliberately does NOT match a full-corpus `harness` row (no
`SAB_HARNESS_TARGET` set) against an unrelated changed path — that row's
own `SAB_FILE` still matches normally if IT changed; the "unrelated src
change I don't name" case is D69's accepted 2b risk, closed only by a
CLOSE running the full matrix, not by this helper. Validated in the
failing direction: a path matching nothing prints nothing (`docs/
APPROACH_typo.md` against the current sabotage set, exit 0), and a
sabotage file missing `SAB_ID` is a FATAL exit 2 naming the file (tested
with a scratch stub, never committed).

**The retro-diff evidence** the risk acceptance rests on:
`build/mech_m64.log` (99 rows, HEAD `c324091`, 2026-08-22 15:36) against
`build/mech_m65.log` (118 rows, HEAD `5edba64`, 2026-08-22 23:26) — 99 rows
in common. Of those, 50 show a changed CELL, and every one is a PASS-COUNT-
only move (fail counts and verdicts identical, DETECTED both times),
consistent with ordinary corpus/check growth between the two HEADs. The one
row whose VERDICT changed, `S48-poss-no-enclosing-first`
(`APPLY-FAILED`/ANOMALY in m64 -> DETECTED in m65), is category 2a: its own
anchor count needed fixing after an intervening refactor duplicated the
anchor text (`git log`: fixed in commit `34ede2c`, "the pss_verdict
refactor" — the sabotage's OWN definition changed, exactly the kind of
move D69 expects and excludes). The two UNDETECTED rows in m65
(`S107-bref-not-nullable`, `S108-rdshape-accepts-bref`) are both rows with
NO entry in m64 at all — new rows, undetected from birth
(`tests/mech/CLAUDE.md`'s own account of both), not a pre-existing row
flipping. **Zero rows were observed flipping DETECTED -> UNDETECTED without
their own `SAB_FILE`/definition changing**, across this 99-row-common pair
— the measurement D69's text names as still owed. Earlier journal figures
(`docs/dev/dev_journal.md`: 35 rows undetected:0 twice, pre-2026-08-15; the
85-row `undetected: 0` figure `tests/mech/CLAUDE.md` records at `ae6e41f`,
2026-08-21) corroborate the same "no flip" pattern as far back as archived
figures exist, though only m64/m65 have raw logs on disk to diff cell by
cell — the others are prose summaries only.

## Sanitizer + lint battery (SAN-1, 2026-08-13)

**K26 caveat (2026-08-18): the LEAK tier of this battery is currently a
no-op on this box** — LSan silently detects nothing under the battery's
own options (positive control: a deliberate 12,345-byte leak exits 0;
yama ptrace_scope=1 suspected). ASan proper is unaffected. See
docs/dev/known_issues.md K26 for the canary obligation and the ruling
needed before any host-config fix.


Three opt-in targets, the same shape as `make strict`: never part of `make
test`, never default, write nothing to `build/`, safe to run alongside
`make test` in another shell. `make ubsan` and `make asan` each build a
SEPARATE tree (`build-ubsan/`, `build-asan/`, gitignored, via the Makefile's
`BUILD_DIR` variable) so a subsequent plain `make`/`make test` is unaffected.
TSan already lives in `tests/thread` (part of `make test`, docs/testing.md's
existing coverage); this section completes the sanitizer family docs/dev/plan.md
[SAN-1] asked for, and adds `make lint` and the `LINTGEN` flag.

### Both axes, and why each target needs both

Trouble lands in two different pieces of code, and a battery that only
instruments one is blind to the other:

- **the COMPILER axis** — `pcrec` itself (parsing, the registry, IR
  construction, codegen, the CLI) and the small C test-driver binaries
  several suites build to link `libpcrec.a` directly (`registry_check.c`,
  `pcre2_check.c`, `branch_count_check.c`, `pc4_check.c`/`pc4_driver.c`).
  R20's tier-1 longjmp-into-uninitialized-`jmp_buf` bug (fixed the same
  session it was found) is this class — the kind of bug that surfaces as a
  lucky SIGSEGV without a sanitizer and as a precise, first-execution
  diagnostic with one.
- **the COMPILEE axis** — every GENERATED matcher the suite compiles and
  runs. This is where OPT-A/OPT-B will take real risk (memchr/SIMD
  prefilters, transition-table packing) once they open, so the tripwire is
  built first, per Frank: "we should expect some trouble when we start
  optimizing."

`make ubsan`/`make asan` set `PCREC`/`LIBPCREC`/`LIBA` to point every suite
at the sanitizer-built tree (compiler axis) and `GENCFLAGS` to carry the
sanitizer flags into every generated-matcher compile (compilee axis) in one
pass, over the SAME suites `make test` runs (minus `tests/thread`, see
Exclusions below).

### The GENCFLAGS compile-site audit (the actual SAN-1 finding)

The brief this landed from assumed the `GENCFLAGS` hook already reached
"every place a generated matcher is compiled" and asked to verify that.
It did not. `tests/harness/run.sh` and `tests/codegen/run_codegen_tests.sh`
honored it; four other compile sites that build or link generated-matcher
code had their own hardcoded flags and were completely deaf to it:

| site | what it compiles | was | now |
|---|---|---|---|
| `tests/cli/run_cli_tests.sh` | `gen.c` + small drivers, several cases | hardcoded `CFLAGS` | `CFLAGS="${GENCFLAGS:-...same default...}"` |
| `tests/registry/run_pc4.sh` | the 273-pattern sweep's `gen.c`/`gen.o`, per pattern | hardcoded `-O0 -std=gnu11` | honors `GENCFLAGS`, same default |
| `tests/registry/run_registry_tests.sh` | links `libpcrec.a` (`registry_check.c`, `pcre2_check.c`) | hardcoded `LIB=.../build/libpcrec.a` | `LIB="${LIBPCREC:-...same default...}"`, plus `$SANFLAGS` appended to both builds |
| `tests/parse/run_parse_tests.sh` | links `libpcrec.a` (`branch_count_check.c`) | same | same fix |
| `tests/codegen/run_trie_identity.sh` | the `-DPCREC_NO_TRIE` reference compiler, built from source | `PCREC` was already overridable (free compiler-axis coverage); `$REF`'s own build had no hook | `$SANFLAGS` appended to the `$REF` build |
| `tests/vm/run_vm_tests.sh` + `vm_oracle.py` ([M4.5b], 2026-08-15) | `gen.c` + `vm_driver.c`, once per pattern per engine mode | — (new) | born reading `GENCFLAGS` and `PCREC`, so both axes are covered from the first commit rather than retrofitted |

Two new env vars carry this, both empty/default-preserving when unset:
`LIBPCREC` (default `<repo-root>/build/libpcrec.a`) lets a suite that links
the library directly pick up the sanitizer-built one; `SANFLAGS` (default
empty) is appended to the small test-driver builds that don't already have a
`GENCFLAGS`-shaped hook, since those are compiler-axis code, not generated
matchers. `tests/reject/` and `tests/known_fail/` compile nothing directly
(known_fail delegates to `tests/harness/run.sh`, which already carries the
hook) and needed no change.

### Targets

- **`make ubsan`** — `-fsanitize=undefined -fno-sanitize-recover=undefined`
  (the `-fno-sanitize-recover` is deliberate: a first-hit abort with a
  stack trace, not a log line the harness's own PASS/FAIL scan could miss).
  Compiler axis at `-O1 -g`; compilee axis via
  `GENCFLAGS="-O1 -std=gnu11 -Wall -Wextra -fsanitize=undefined -fno-sanitize-recover=undefined"`.
- **`make asan`** — `-fsanitize=address,leak`, same `-O1 -g` / `GENCFLAGS`
  shape. `ASAN_OPTIONS="detect_leaks=1"` is set explicitly since LSan's
  default varies by platform.
  **[M4.5b] (2026-08-15)**: both targets' suite lists gain
  `tests/codegen/run_vm_identity.sh` and `tests/vm/run_vm_tests.sh`. The
  second matters more than a new line usually does — it is the only suite
  that RUNS a VM artifact, so it is the only place the sanitizers see the
  emitted resume stack, the capture trail, the computed `goto *`, and the
  span-loop cursor's pointer arithmetic at all. Everything else in the
  battery exercises DFA-emitted table walks.

- **`make lint`** — static analysis survey, degrading loudly-but-gracefully
  per tool present (the PC-3 libpcre2-absent SKIP pattern), never failing
  the target just because a tool is missing:

  | tool | verdict | reason |
  |---|---|---|
  | `gcc -fanalyzer` | **ADOPTED** | the only analyzer this box offers; 0 findings across the whole tree (17 lib files + cli/main.c), ~9s |
  | `clang-tidy` | absent on this box | SKIP, loud, per-run |
  | `cppcheck` | absent on this box | SKIP, loud, per-run |
  | `clang` (as a second compiler, for its own warning set) | absent on this box | SKIP, loud, per-run |
  | `valgrind` | absent on this box; noted below as the ASan-conflict fallback anyway | — |

  These are ABSENCE, not technical rejections — this box happens to offer
  only `gcc`. `make lint` prints `SKIP: <tool>: not installed` for each, the
  same shape as PC-3's libpcre2-absent skip, so a stranger's box with more
  tooling installed gets more coverage automatically without a code change
  here (the survey is re-runnable, not a one-time verdict pinned to this
  machine).

  `gcc -fanalyzer` is genuinely useful, not adopted by default: it catches a
  straight-line double-free immediately (`free(p); free(p);` in `main`,
  no branch), but MISSED the same bug moved into a helper function and
  gated behind one `if` branch, at `-O2`, in a throwaway probe — a real,
  documented limit of its interprocedural reach, not a claim that `make
  lint` catches every use-after-free. Record it so a future "why didn't
  lint catch X" has an answer already on file.

### LINTGEN — riding `make test`'s own compile pass (Frank, 2026-08-13)

`make test LINTGEN=1` is a second, complementary lint mechanism: rather than
a separate lint-only pass over generated code, it injects `-fanalyzer` into
the SAME `GENCFLAGS` compile every generated matcher already goes through
during a normal `make test` run. `LINTGEN` is `?= 0` and `export`ed from the
Makefile; `tests/harness/run.sh`, `tests/cli/run_cli_tests.sh`,
`tests/codegen/run_codegen_tests.sh`, and `tests/registry/run_pc4.sh` each
read it themselves (the same pattern as `GENCFLAGS`) and append `-fanalyzer`
(`run_pc4.sh` also adds `-Werror`, since its own `GENCFLAGS` default has none
— see below). Unset (default), the four scripts compute byte-identical
`GENCFLAGS`/`CFLAGS` to before; `make test` is unaffected.

**Findings surface loudly, by construction, not by a separate check**:
`harness`/`cli`/`codegen`'s default `GENCFLAGS` already carries `-Werror`, so
an analyzer finding on generated code is a hard compile failure, exactly
like any other warning on that path — no new machinery needed.
`run_pc4.sh`'s default (`-O0 -std=gnu11`, no `-Wall`/`-Werror` — this sweep
runs 273 patterns and stays fast on purpose) does NOT carry `-Werror`, so
`LINTGEN=1` adds `-Werror` there too, specifically so a finding does not
compile clean and vanish.

**False-positive survey before wiring, not after**: before adding the
`-Werror` coupling, 9 representative generated-matcher shapes (alternation,
anchors, bounded repeats `{2,5}`, character classes, keyword-alternation —
the trie/OPT-A's future target — case-insensitive, `--emit-main`) were run
through `gcc -O1 -Wall -Wextra -fanalyzer` by hand. **Zero findings, zero
false positives**, including on the keyword-alternation trie's
computed-goto shape — `-fanalyzer`'s treatment of `goto *table[state]`
turned out to be a non-issue for this codebase's generated output, contrary
to the a-priori worry that computed goto would be exactly where a
whole-program analyzer gets confused. If a future generated shape (a new
engine, a new prefilter) DOES produce a false positive under `LINTGEN=1`,
that is a finding to document here with the exact pattern and diagnostic,
not something to silently exclude.

Runtime delta (`make test` vs `make test LINTGEN=1`): **+53.7s on a 389.7s
baseline (+13.8%)**, measured 2026-08-13 on a quiet box, serial, with
`/proc/loadavg` sampled before and after each run (full table below).
Cheap enough to make the "2-fer" habitual at battery-grade evaluation
points; not free enough to fold into the default `make test` claim, which
stays byte-identical with `LINTGEN` unset. Placement ruling: see "Battery
integration" below.

### Measured runtimes (2026-08-13, QUIET box, san1 at `2e71606` plus these
landing edits, gcc 15.2.0 Ubuntu 15.2.0-16ubuntu1, libpcre2 10.46 present —
PC-3/PC-4's ~1000+ checks and ~700K probes run for real under both
sanitizers, nothing skipped)

**Load provenance, per R3.10**: every run below was taken SERIALLY on an
otherwise idle box (post-reboot), `/proc/loadavg` sampled immediately
before and after each individual run; every 1-minute sample stayed at or
under 1.05 against the sweep discipline's 1.20 contamination threshold.
An earlier figure set taken the same day during concurrent two-lane work
(ubsan 6m57s, baseline 6m28s, asan 7m58s) was recorded as
CONTENDED/load-unknown at the time and is SUPERSEDED by this table; for
the record, those contended figures landed within ~7% of the quiet ones —
the discipline cost little here and is kept because the one time it
doesn't, nobody would otherwise know.

| target | wall time | result | load (1-min, before → after) |
|---|---|---|---|
| `make test` (baseline) | 389.7s (6m30s) | **GREEN** | 0.58 → 0.91 |
| `make test LINTGEN=1` | 443.3s (7m23s) | **GREEN** — delta vs baseline **+53.7s (+13.8%)** | 0.91 → 0.76 |
| `make ubsan` | 408.9s (6m49s) | **GREEN** — full suite (harness, cli, reject, registry incl. PC-3/PC-4, parse, codegen, trie_identity, known_fail), both axes | 0.76 → 1.02 |
| `make asan` | 470.4s (7m50s) | **GREEN** — full suite, both axes (post-F1 fix; the pre-fix run stopped red at trie_identity, which is F1's story below) | 1.02 → 1.05 |
| `make lint` | 8.8s | **GREEN**, 0 findings | 1.05 → 1.04 |

Cross-check: the 389.7s baseline agrees with [TT-1]'s independent
per-section median sum (~391s serial, measured the same day by a different
method in the "Tiered testing" section above) — two instruments, one
number.

### Sanitizer findings inventory

**F1 — `-Wclobbered` on `pcrec_syntax_explain`'s `rows_shown`/`dissents`,
`src/parse/syntax_dump.c:881`, surfaced only under `make asan`** (not
`make ubsan`, not the default `-O2` build, not `make strict`). **TRIAGED
BENIGN and HARDENED (manager, 2026-08-13, same session)** — the manager
independently read the handler and confirmed the analysis below: neither
variable is read on the longjmp path, and the ASan-build-only appearance is
ASan's instrumentation shifting register allocation into gcc's clobber
heuristic. Both variables are now `volatile int` (one-liner, per SAN-1's
findings-discipline exception for trivial fixes — separate commit, this
warning quoted in it), so the invariant the comment already stated in
prose ("deliberately not read on the longjmp path") is now a defined-read
guarantee rather than a heuristic gcc happens to get right, closing off
the R20-shaped latent-bug risk a *wrong* instance of this warning would
represent. Rebuilt `build-asan/` after the fix: warning gone, `make`/
`make strict` still clean. **Full compiler output, verbatim (pre-fix):**

```
/home/duxevents/pcrec/worktrees/san1/src/parse/syntax_dump.c: In function ‘pcrec_syntax_explain’:
/home/duxevents/pcrec/worktrees/san1/src/parse/syntax_dump.c:881:9: warning: variable ‘rows_shown’ might be clobbered by ‘longjmp’ or ‘vfork’ [-Wclobbered]
  881 |     int rows_shown = 0, dissents = 0;
      |         ^~~~~~~~~~
/home/duxevents/pcrec/worktrees/san1/src/parse/syntax_dump.c:881:25: warning: variable ‘dissents’ might be clobbered by ‘longjmp’ or ‘vfork’ [-Wclobbered]
  881 |     int rows_shown = 0, dissents = 0;
      |                         ^~~~~~~~
```

Both variables named, both from the single declaration line
`int rows_shown = 0, dissents = 0;` at `src/parse/syntax_dump.c:881`, inside
`pcrec_syntax_explain` (the `--explain` query function, R20/MOD-0.7
territory). Repro: `gcc -O1 -g -fsanitize=address,leak -Wall -Wextra
-std=gnu11 -c src/parse/syntax_dump.c` (or `make asan`, which hits it while
rebuilding `tests/codegen/run_trie_identity.sh`'s `-DPCREC_NO_TRIE`
reference compiler from source — the same warning is present in the real
`build-asan/` library build too, confirmed in that build's own log; it
just has nowhere that treats a warning as fatal there).

**Analysis (confirmed correct by the manager's independent read).** The two
variables are declared at line 881, BEFORE the function's `setjmp(cx.jb)`
call (a few lines below, at line 907, per the function's own source), and
mutated only after it (`rows_shown++` at line 967, `dissents +=` at
line 1039, both well past the `setjmp`). The comment immediately above
that `setjmp` already stated the reasoning gcc's `-Wclobbered` heuristic
apparently can't see through: *"`body`, `sb` and `cx` are declared above
the `setjmp` and mutated only through their escaped addresses;
`rows_shown`/`dissents` are mutated after it and are deliberately not read
here [i.e. on the longjmp path]"* — the `if (setjmp(cx.jb)) { sb_free(&body);
sb_free(&sb); arena_free(&cx.arena); if (ndissent) *ndissent = 0; return
NULL; }` branch returns unconditionally without ever reading `rows_shown`
or `dissents`, so whatever clobbered value either holds on that path is
never observed — the manager verified the handler touches only `body`,
`sb`, `cx.arena` and the `ndissent` parameter. This is the same shape as
another `setjmp` earlier in the same file (~line 455) that this project's
own comments describe having already reasoned through as benign for an
analogous warning.

**Secondary observation, not a finding**: this is the FIRST time anything
in the repo has compiled `syntax_dump.c` under `-fsanitize=address` — the
default `build-asan/libpcrec.a` build doesn't fail on it (no `-Werror`
there), and it only becomes fatal because `run_trie_identity.sh`'s own
`$REF` build has always treated any warning as fatal (`comment: "Warnings
stay on so #ifdef rot is loud rather than silent"`) — a policy this row's
`$SANFLAGS` plumbing (added for bonus compiler-axis coverage on `$REF`;
`$PCREC` itself already covers the PRIMARY compiler axis there) newly
exposes to warnings from an unrelated file. **RULED (manager,
2026-08-13, same session): the coupling STAYS.** `make asan` surfacing a
real warning from a file outside `run_trie_identity.sh`'s own purpose is
the instrument working, not a defect — F1 is the existence proof: nothing
else in the repo had ever compiled `syntax_dump.c` under these flags, and
what it surfaced was worth a triage and a hardening one-liner. If a future
warning from this coupling is genuine NOISE, that instance is the evidence
to revisit with — document it here first, then re-open the scoping
question with a case in hand rather than a hypothetical.

No findings from `make ubsan` at commit `c509d944` — clean across the full
suite including the PC-3/PC-4 probe volume. `make asan` is clean too after
F1's fix — full quiet re-run GREEN, 470.4s, in the runtime table above.

### K7/K9 — read, not automated here

docs/dev/known_issues.md K7 (a large bounded repeat exhausts memory and can
abort the CALLER's process under a memory limit — ASan/LSan's home class)
has **no automated repro in `make test` today**; it is reproduced only by
hand (`ulimit -v ...; pcrec ... 'a{0,65535}'`) and by the probe
measurements the entry cites. There is therefore nothing K7-shaped to
exclude from `make asan` right now. If a K7 repro is ever added to the
standing suite, expect exactly the conflict the brief anticipated — ASan's
shadow-memory bookkeeping needs headroom a tight `ulimit -v` does not leave
it — and the no-rebuild alternative is **valgrind memcheck**
(`valgrind --leak-check=full build/pcrec ...`), which works under an
external memory limit the way ASan's in-process shadow memory does not.
(Not runnable on THIS box for this report — `valgrind` is one of the absent
tools above — but the substitution is the same "no-rebuild alternative"
pattern PC-3 documents for libpcre2-absent boxes: the recommendation
survives the tool's own absence.) K9 (`pcrec_compile()` takes no pattern
length, so an embedded NUL silently truncates) is a public-API/semantic
issue, not a memory-safety one — no sanitizer in this battery is the right
instrument for it, and it is out of SAN-1's scope by construction.

### Sabotage validation — the instrument has to be watched fire

Following `tests/thread/`'s and `tests/mech/`'s own convention (an
instrument nobody has watched fire is a claim, not a check), each axis of
each sanitizer was validated with a planted bug in a SCRATCH file
(scratchpad, never committed, never touching `src/`), built with the exact
flags the corresponding Makefile target uses, then removed:

| axis | sanitizer | sabotage | result |
|---|---|---|---|
| compiler | UBSan | signed overflow (`INT_MAX + 1`, `volatile`-sourced so gcc can't fold it) in a scratch `main()`, built with `make ubsan`'s exact `UBSAN_CFLAGS` | caught, precise diagnostic + stack trace, exit 1 |
| compilee | UBSan | signed overflow hand-planted into a REAL `pcrec`-generated matcher (`a(b|c)+d`)'s `rx_search`, forced live via `fprintf` (a dead computation with no observer is legally eliminated — see below), compiled via `GENCFLAGS` exactly as the harness would, linked with the real `tests/harness/driver.c` | caught, diagnostic names `gen.c:12`, exit 1 |
| compiler | ASan+LSan | heap-buffer-overflow (`memset` 1 byte past an 8-byte `malloc`, runtime-sized so gcc can't constant-fold it) + a leaked allocation, in a scratch `main()`, built with `make asan`'s exact `ASAN_CFLAGS` | caught (both classes), exit 1 |
| compilee | ASan | out-of-bounds READ on the emitted `rx_fcls[256]` global table (index depends on runtime subject length), hand-planted into a real generated matcher, compiled via `GENCFLAGS` | caught, `global-buffer-overflow`, names `rx_fcls` and its true 256-byte extent, exit 1 |

**One measured gotcha worth keeping, found while building the compiler-axis
ASan sabotage**: at `-O1` (the flag level both `make ubsan` and `make asan`
build at), gcc's dead-store elimination silently erased a heap-overflow
write that was never read before the buffer was freed — the sabotage
compiled clean and ran to exit 0 under ASan, looking like a sanitizer
failure until the write was made observable (an `fprintf` reading the
overflowed byte back). This is legal per the C standard (an unobserved
write has no side effect the compiler must preserve) and is not specific to
this project's sanitizer flags — but it means a "write-then-free-with-no-
read" class of real bug, if one ever exists in pcrec's own code, could in
principle be optimized away before ASan's instrumentation sees it at `-O1`.
Recorded as a known limit of the chosen build flags rather than fixed
(`-O0` would close it but cost real coverage speed across a suite this
size — a tradeoff for the manager, not decided here).

### D45 — every generated-code compile runs under a budget (2026-08-15)

`docs/dev/decisions.md` D45, ruled live: **every compile of generated C in the
test infrastructure runs under a timeout, and exceeding it is a loud FAILURE
naming the case — never a hang, never a silent skip.**

It came out of a battery in which two `cc1` processes ground for 1h40m and 55m
on one generated file. The reason nobody noticed for that long is the whole
point of the ruling: an unbounded compile reads as "still running", never as
"failed", so a suite with no compile bound cannot tell a slow machine from a
hung one and reports neither.

**One implementation**: `tests/lib/gen_timeout.sh`, sourced by all seven shell
suites that compile emitted C, and read as a command (`bash
tests/lib/gen_timeout.sh secs`) by the two python ones, so the rule lives in
one file rather than one per language. `gen_cc <case-label> <cc-argv...>` runs
the compile and leaves the compiler's output — or the timeout diagnostic — in
`$GEN_CC_LOG`, so a caller reports the same way whichever happened.

**The budget is CPU-PRIMARY with a wall backstop** (Frank, 2026-08-16, D45
third addendum). The original wall-only budget measured the wrong clock,
and the flake that proved it is the recorded measurement:
`tests/base/k18_cost_gates.rxt`'s
`((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}` emits 6,433
lines of C and needs 2.53s of CPU whether the box is quiet or loaded — but
under `make -j12` contention its WALL time crossed the then-5s budget and
failed one full-suite run while an identical run minutes earlier passed.
The work didn't change; the scheduling did. (The artifact itself is the
bounded-repeat replication class whose compiler-side SIZE cap is queued
with [ENG-BREP] counter-K.)

- **CPU budget (primary): 10s plain / 200s sanitizer** (`GENCPU`,
  `GENCPU_SAN`; the sanitizer figure was 60s until 2026-08-24, when the
  [DD-14] wave A battery measured the corpus's worst artifact —
  `tests/base/k18_cost_gates.rxt:91`, 351 KB of C — at 51.9s user CPU
  QUIET under `-O1 -fsanitize=address,undefined,leak` (2.2s plain): 1.15x
  a budget whose plain sibling sits at ~4x quiet, so one concurrent -j12
  build killed cc1 by SIGXCPU. 200s applies the same ~4x-quiet rule.)
  (`GENCPU`,
  `GENCPU_SAN`; integer seconds — it is `RLIMIT_CPU`). Load-RESILIENT
  rather than perfectly load-independent: contention inflates
  cycles-per-instruction, measured on the k18_cost_gates artifact at
  2.53s CPU quiet → 3.52s under 11 register-spinners → >5s under a real
  `make -j12` gcc mix (memory-subsystem thrash — the CPU-primary change's
  own first battery failed exactly there, at a 5s default). CPU inflation tops out near 2x where wall stretches without
  bound, so 10s (~4x quiet, ~2x worst real-contended) sits far tighter
  than any safe wall bound; a pathological compile dies after 10s of
  actual work no matter what else runs. Enforced as a soft rlimit so cc1
  dies by a clean SIGXCPU that gcc reports as "CPU time limit exceeded" —
  textually distinct from an OOM-kill's "Killed signal", keeping the
  crash/timeout/CPU diagnoses separate. One shared knob pair for compiles
  AND matcher runs (watchdog `-c`, exit 123, `verdict=cpukill`); split it
  only with a measurement.
- **Wall backstop: 60s plain / 180s sanitizer** (`GENTIMEOUT`,
  `GENTIMEOUT_SAN`). CPU cannot see a process stuck WITHOUT working
  (blocked, deadlocked — burns no CPU), so wall stays, loose: it must sit
  above the CPU budget times the worst plausible contention factor or a
  contended-but-working compile hits it first and the verdict lies (hence
  180 = 3x on the sanitizer axis). Its diagnostic says "STUCK, not
  working" and points the reader at what the compile was waiting on, not
  at the artifact's size.

Two bounds, two failure classes, two diagnoses — the step-budget /
frame-capacity precedent applied to the harness itself. (History: plain
wall was 5s from the ruling; raised to 10s on 2026-08-16 when the
k18_cost_gates flake first fired the revisit-when; superseded the same day
by CPU-primary, which is the durable fix — headroom pushes the flake
boundary back, the right clock removes it.) The axis is DERIVED from the
flags — `-fsanitize=` appears in `GENCFLAGS`/`CFLAGS`/`TSANFLAGS` exactly when
the compile is instrumented — so no site has to declare which axis it is on and
a site added later gets the right budget for free. `124` is checked exactly,
not as `>= 124`: a compiler that segfaults exits 139 and one that is OOM-killed
exits 137 (K7's `a{0,65535}` really does), and calling either a timeout would
send the reader looking for a slow machine instead of a crash.

**Deliberately NOT converted**: `tests/bench`'s compile timeouts, because they
ARE its measurement — it reports DNF against a compile-time budget, so
replacing them with a shared number would delete the instrument. And
`tests/thread`'s TS-3 builds, which compile libpcrec itself (compiler axis, not
emitted code).

**pcrec's OWN invocation is in the mechanism too, since 2026-08-15 (K18's
rewrite lane, discharging R23 V1).** `tests/harness/run.sh` wrapped the
compiler's own invocation in a bare, hardcoded `timeout 60` that predated D45
and sat outside it: the budget above is derived from a GENERATED-CODE compile's
flags, and pcrec's own invocation passes none — so the one compile a change to
pcrec can actually slow down had the one budget that did not scale with the
axis, and blowing it is scored `HARNESS FAILURE` rather than a graceful skip.
K18's path-sensitive closure is exactly such a change, so it folded the timeout
in rather than documenting the gap as acceptable. `pcrec_timeout_secs` reads
the same four flag variables and answers **20s plain / 60s sanitizer**
(`PCRECTIMEOUT`, `PCRECTIMEOUT_SAN`). The numbers are a different quantity from
the generated-code ones and are calibrated on their own measurement: pcrec's
own compiles are sub-millisecond for ordinary patterns, and MEASURED 0.38 s
plain / 0.84 s asan / 0.85 s ubsan for the worst case the corpus contains —
`tests/base/k18_deep_nesting.rxt`'s 250 nested nullable stars, which is the
deepest nesting the parser accepts at all. So the plain budget is ~50x the
worst legitimate case, with the same revisit-when as D45's own: raise it WITH
the measurement, never silently.

**EXECUTION is bounded too, since 2026-08-16 (the twenty-fifth session,
closing the gap tests/vm/CLAUDE.md flagged).** D45 bounded every COMPILE of
emitted C and nothing bounded its execution, so a merely-slow generated
matcher read as a hang for as long as it took — nine minutes of a battery
leg, 2026-08-15, on a run that was quadratic-and-correct. Same rule, same
file: `gen_run_secs` answers **10s plain / 60s sanitizer** (`GENRUNTIMEOUT`,
`GENRUNTIMEOUT_SAN`; the plain number keeps the calibration of the
harness's old per-cell `timeout 10`, which had never been approached by a
legitimate run), and exceeding it is a loud FAILURE naming the case. Two
shapes, chosen by invocation count:

- **`gen_run <label> <argv...>`** for per-pattern and one-off runs: routes
  the execution through `scripts/watchdog` (which see), adding a **512m
  peak-tree-RSS ceiling** (`GENRUNMEM`; a generated matcher is
  allocation-free by construction, so RSS beyond subject + driver overhead
  is a runaway, not a big workload) and **one key=value log line per
  execution** in `build/watchdog.log` — `section=` (from
  `WATCHDOG_SECTION`, exported once per runner) and `label=` make a run
  findable among every suite's lines, and `wall=` vs `cpu=` answers
  slow-vs-hung after the fact (cpu≈wall is spinning, cpu≪wall is blocked).
  Exit **124** = run timeout, **122** = memory kill, both checked EXACTLY
  (139 is a crash, 137 an external OOM-kill; calling either a timeout sends
  the reader hunting a slow box instead of a bug).
- **The cheap shape** for inner loops running hundreds+ of sub-millisecond
  executions, where watchdog's fixed per-invocation startup cost would
  multiply the loop's runtime: coreutils `timeout "$RUN_SECS"` with the
  number precomputed from `gen_run_secs` (`tests/harness/run.sh`'s per-cell
  runs), or python `subprocess.run(..., timeout=RUN_TIMEOUT)` reading `bash
  tests/lib/gen_timeout.sh runsecs` (`tests/vm/vm_oracle.py`). The NUMBER is
  shared even where the wrapper is not.

`tests/bench` stays excluded for the same reason it is excluded from the
compile rule: its budgets ARE its measurement.

**Its own checks**: `tests/lib/run_gen_timeout_tests.sh` (in `make test`;
read the count from a run, not from here). A positive control proves the
wrapper FIRES on a real over-budget compile and names the case; a coverage
assertion proves every suite routes through the one helper, which is the
check that survives future work, since a new compile site added without the
wrapper is the realistic way this protection erodes. Sabotage S43. The two
added with the pcrec budget hold it the same way: one asserts the per-axis
numbers and the overrides, and one greps `run.sh` for a hand-rolled numeric
timeout on `$PCREC` — a literal is exactly how this reverts. The run bound
gets the full mirror: per-axis budget/override checks, a fire control on a
REAL over-budget run (`(a*)*b` under `--engine=vm` with the step budget
sized so the natural run is ~5s — budget-bound, so the control terminates
instead of hanging even if the wrapper breaks), an oracle-verified
pass-through control, a run-coverage list that grows as suites adopt, and
the hand-rolled-number grep on the harness's per-cell run site. There is
deliberately NO memory-kill sibling control there: no real generated
artifact can runaway on RSS (allocation-free), so the 122 path's positive
control lives in `scripts/tests/watchdog.test` (D48: run on change via
`make testscripts`, not per suite run) where a synthetic allocator is
honest rather than a stub pretending to be an artifact.

### The pathology D45 was ruled over, and the compiler-side bound

`tests/vm`'s large-bounded-repeat case was `((a)|b){0,4000}c` — sixteen
characters, 3.5 MB and 113,545 lines of emitted C, because engine_m4.md §3.3's
ruled reading is that a bounded repeat REPLICATES its body.

**It is not a sanitizer pathology, and it is not the label count.** Measured on
the project box, 2026-08-15:

| N | labels | `&&label` | plain -O1 | plain **-O2** | ubsan -O1 | asan -O1 |
|---|---|---|---|---|---|---|
| 25 | 253 | 50 | 0.20 s | 0.40 s | 0.80 s | — |
| 50 | 503 | 100 | 0.40 s | 1.00 s | 1.71 s | — |
| 64 | 643 | 128 | 0.50 s | **1.40 s** | 2.30 s | — |
| 100 | 1003 | 200 | 0.70 s | 2.90 s | 4.11 s | 1.80 s |
| 128 | 1283 | 256 | 0.90 s | 4.61 s | 6.11 s | — |
| 200 | 2003 | 400 | 1.60 s | 11.21 s | 13.91 s | 3.60 s |
| 400 | 4003 | 800 | 3.50 s | 51.54 s | 49.94 s | 5.31 s |

ASan is linear; plain `-O2` is superlinear and *worse* than UBSan at `-O1`. So
UBSan and `-O2` are two routes to one wall, and the wall is R1 A-3's
computed-goto compile-time cliff reached from the VM side.

A control settles the cause: `(a×2000)b` emits 2004 labels with **zero**
address-taken labels and compiles in **2.70 s** at `-O2`, where
`((a)|b){0,200}c`'s 2003 labels with **400** address-taken labels take
**11.21 s**. Every `&&label` becomes a potential successor of the VM's single
`goto *`, so the indirect edge's fan-out is what gcc's dataflow goes
superlinear in.

**The compiler-side bound is on REPLICATION, not on size**
(`PCREC_MAX_VM_REPEAT_COPIES = 64`, src/core/limits.h). A first draft capped
total resume points at 128 and refused the wrong patterns: a 200-branch
capture-bearing keyword alternation has 199 resume points and is entirely
healthy (the 100-branch version measures 0.50 s at `-O2`), because its size is
PROPORTIONATE to what its author wrote. The defect is DISPROPORTION — sixteen
characters producing 3.5 MB — and only replication produces it. A body with no
choice point compiles to a span loop and never replicates, so `a{0,65535}` and
`(?:ab){0,9999}` are untouched.

**The case itself** is now `((a)|b){0,20}c` under an explicit
`--backtrack-frames=32`: the same D44.1 property (a frame requirement of 40
against a capacity of 32), 28 KB instead of 3.5 MB, 0.31 s at `-O2`, and 40
replicas against the 64 cap. Naming the capacity also decouples it from a
number it does not own — the default capacity is a bring-up placeholder [M4.6]
will calibrate, and had [M4.6] raised it above 4000 the old case would have
started fitting and gone silently vacuous while still passing.

**Residual, recorded not fixed**: the two guards are independent and neither
covers everything. A very long capture-bearing LITERAL still emits a large
artifact with zero resume points (20,000 characters → 2.3 MB, >180 s at both
`-O1` and `-O2`), bounded only by `PCREC_MAX_VM_NODES`, which at 131,072 is far
above what the compile budget can absorb. That shape is proportionate to the
pattern rather than disproportionate to it, so it is not what the replication
cap is for — and D45's harness wrapper now catches it loudly rather than
hanging. Lowering the node cap is a refusal decision for the manager.

### Exclusions

- **`tests/thread/`** — NOT re-run under `make ubsan`/`make asan`. TSan
  already covers it (part of `make test`); combining ASan/UBSan
  instrumentation with the pthread-heavy TS-2/TS-3 driver is not how these
  sanitizers compose cleanly on this toolchain, and concurrency bugs are
  TSan's class, not UBSan/ASan's. The exclusion is structural (the target's
  suite list omits it), not a skip printed at run time.
- **`make bench`, `make mech`, `make fuzz`** — never touched. `bench`'s
  numbers are timing medians that sanitizer overhead would invalidate;
  `mech` already costs ~50 min building the tree once per sabotage at
  `PROCS=4` (measured 2026-08-21, correcting an earlier "~6 minutes" figure
  that undercounted the full matrix — see the "CCACHE=1" section below for
  [TT-3]'s per-row numbers), and doubling that under a sanitizer is
  disproportionate to what SAN-1 needs to prove; `fuzz` is a separate,
  long-running, manually-invoked tool.
- **`tests/spec_mod0/`, `tests/probes/`** — never part of `make test` (D27
  hand-off artifacts / design-measurement probes), so never part of
  `make ubsan`/`make asan` either — SAN-1 rides the STANDING battery, it
  does not grow it.

### Battery integration — DECIDED (manager, 2026-08-13, from the quiet numbers)

The plan row deferred placement until runtime was measured, never asserted.
Measured (table above), the ruling:

- **`make smoke`: never.** Both sanitizers cost ~7-8 minutes against
  smoke's measured ~31-32s budget (the "Tiered testing" section) — the
  plan row's expected answer holds, now with numbers behind it.
- **The merge/close battery (wake §3 shape) GAINS `make ubsan` and
  `make asan`.** Each costs about one `make test` (~7-8 min serial).
  Whether they run serial or concurrent within a battery is the running
  session's load-discipline call: battery runs are pass/fail, not timing
  measurements, so contention there costs nothing that matters (R3.10
  applies to NUMBERS, not verdicts).
- **Battery-grade `make test` runs adopt `LINTGEN=1`** (+13.8%): the
  2-fer is cheap at evaluation points. Plain `make test` stays the
  default claim everywhere else, and for strangers, byte-identical to
  before SAN-1.
- **`make lint` (~9s) joins the battery alongside `make strict`**, and is
  cheap enough to run ad hoc at any point in the inner loop.
- `make asan` red BLOCKS a merge the way a red `make test` does; findings
  land in the inventory above with a triage before any fix (the
  findings-discipline that produced F1's clean arc).

### [TT-7] combined axis (2026-08-23) — ADOPTED: `make san` is the battery's sanitizer stage

`docs/dev/chain_profile.md` candidate (a), 2026-08-23: today's `ubsan` and
`asan` cost 32m35s + 42m25s = 75m00s combined at commit m65 — two separate
`BUILD_DIR` rebuilds and two full 26-script suite passes for two sanitizer
families gcc supports combining in one build (`-fsanitize=address,undefined`
compiled and linked together is a routine, well-supported combination).

**The stated reason two axes exist here is about TSan, not about
ASan-vs-UBSan** — `Makefile:576-580`, directly above the `ubsan:`/`asan:`
targets: "TSan already lives in `tests/thread` ...; combining ASan/UBSan
instrumentation with an already-TSan'd build is not how these sanitizers
compose on this toolchain." That is why `tests/thread/` is excluded from
BOTH `ubsan` and `asan` (Exclusions, above) — it says nothing about
combining ASan and UBSan WITH EACH OTHER, which SAN-1 was never asked.

**`make san`** — a THIRD tree, `build-san/` (gitignored, same shape as
`build-ubsan/`/`build-asan/`), both axes instrumented, same 26-script suite
list and `tests/thread/` exclusion as `ubsan`/`asan` (same TSan reason,
unchanged):

```
SAN_CFLAGS := -O1 -g -fsanitize=address,undefined,leak -fno-sanitize-recover=undefined
```

Mirrors `UBSAN_CFLAGS` and `ASAN_CFLAGS` combined; the two single-axis
`CFLAGS` differ in exactly one flag beyond their sanitizer lists
(`-fno-sanitize-recover=undefined`, UBSan-only in effect since it does not
apply to `address`/`leak`), carried into the combined flags since it costs
ASan/LSan nothing and keeps UBSan's own fatal-first-hit property. `SAN_ENV`
exports both single axes' `*_OPTIONS` together. `ubsan:`/`asan:` are
UNTOUCHED and stay available as opt-in singles either way.

**Diagnosis distinctness, budget behavior under D45, and the exact
measurement command for the manager's timing run**: `docs/dev/
tt7_combined_axis.md` — three scratch sabotages (UB, heap-overflow, a K26-
canary-sized leak) plus the same three planted into copies of `tests/
harness/driver.c` compiled against a real generated matcher, each caught by
its own tool with the right diagnostic and file/line (the leak reproduces
K26's documented LSan-no-op on this box either way, unaffected by
combining); `tests/lib/gen_timeout.sh`'s D45 budgets measured
byte-identical under the combined flags vs. either single axis (all four
budget functions, sourced and called directly — the axis check is a boolean
`-fsanitize=` substring match, not per-sanitizer).

**Status: ADOPTED (manager, 2026-08-23 14:2x, from the timing run).**
MEASURED on the same tree (HEAD 5935ea9/b2d3fce, docs-only commits
between; box load ~1.3 at start; `build/san_m1.log` vs
`build/battery_tt6.log`):

| stage | wall | PASS lines | FAIL | sanitizer reports |
|---|---|---|---|---|
| `make ubsan` | 26:58 | 1569 | 0 | 0 |
| `make asan` | 36:45 | 1569 | 0 | 0 |
| `make san` (combined) | **45:50** | 1569 | 0 | 0 |

`san` < `ubsan` + `asan` = 63:43 by **17:54**, identical PASS population,
zero reports — all three pass criteria met. RULING: the union battery's
sanitizer stage is `san`; the order is test → strict → san → lint (the
"Battery integration" section's chain, with one sanitizer stage instead of
two); `ubsan` and `asan` remain as opt-in single axes for diagnosing a
report the combined build attributes ambiguously. The chain_profile.md
estimate (~45-55 min) was confirmed at its low end. Caveat carried from
K26: LSan is a no-op on this box under every axis (`ptrace_scope=1`), so
the `leak` component of `san` is inert here exactly as `asan`'s was.

## Compile caching (`CCACHE=1`, [TT-3], 2026-08-21) — MEASURED NO for `make test`

**The charter's own predictions were refuted, not confirmed.** ccache 4.12.3
is installed (masquerade symlinks at `/usr/lib/ccache`). `CCACHE=1` (a
`make`/env toggle, the LINTGEN shape) routes every `gcc`/`cc` invocation in
the process tree through it via PATH masquerade — CC itself stays the single
word `gcc`, never `ccache gcc` (that shape breaks `env`'s word-splitting in
`UBSAN_ENV`/`ASAN_ENV`, discovered the hard way in the union battery). Toggle
off (default): PATH gets nothing prepended, `CCACHE=0` is exported, and
every compile-site behavior below reverts to its original one-shot call —
verified byte-for-byte identical compiler command lines with and without the
toggle (a full `make all` trace diffed clean; `tests/lib/run_gen_timeout_tests.sh`
and `tests/cli/run_cli_tests.sh` both pass 269/269 and 18/18 with `CCACHE`
unset, matching their toggled-on populations).

**Two blockers, diagnosed and fixed in turn, and the fix was still not enough.**

1. **Cacheable-call shape.** Nearly every compile site in
   `tests/lib/gen_timeout.sh`'s `gen_cc` passes one or more `.c` sources
   straight to `-o <binary>` in ONE gcc invocation (compile-and-link) — the
   shape ccache cannot cache at all. MEASURED under a naive PATH-masquerade
   wiring: 540/5,466 compile calls cacheable (~10%), 0 hits
   (`build/battery_union2.log`). Fix: `_gen_cc_run` splits each `.c` source
   into its own `-c` compile then links the objects, gated on `CCACHE=1` (a
   call that already passes `-c` — `run_pc4.sh`'s own split, the D45
   controls, the codegen multi-engine fixture — is untouched either way).
   Raised cacheable calls to 65.2%, but a full cold+warm `make test` cycle
   still measured essentially zero HITS: 2/11,765 (0.02%).
2. **Hash instability.** ccache always hashes the full compiler argument
   list. Every one of these call sites passes an `-I<dir>` naming its own
   per-case `mktemp` workdir — a fresh absolute path every single case — so
   even byte-identical content (`tests/harness/driver.c`, compiled
   essentially unchanged on every one of ~20,000 cases) never matched its
   own prior compile. Isolated with a micro-probe (compile identical content
   from two different directories): absolute `-I<dir>`, no `cd`, MEASURED
   0/2 hits even without `-g`. Fix: `gen_cc_relativize()` rewrites any
   `-I<outdir>`/`-I <outdir>` (the call's own `-o` directory — every site
   shares this one shape) to the textually-stable `-I.`, and `_gen_cc_run`
   `cd`s into that directory before compiling, referencing in-directory
   sources by bare basename. `-g` (the sanitizer axes' flag, and — since
   `CFLAGS` defaults to `-O2 -g` — the ordinary TREE BUILD too) compounds
   the problem: ccache's `hash_dir` option additionally folds the CWD into
   the hash for correct debug-info paths, so a `-g` compile from two
   different case directories still missed after fixing `-I` alone (probed
   0/2 hits at `hash_dir`'s default, 1/2 — a HIT — with
   `CCACHE_NOHASHDIR=1`). Both `CCACHE_NOHASHDIR=1` and `CCACHE_BASEDIR`
   (the repo root for `gen_cc`'s callers, `$(CURDIR)` — evaluated fresh per
   `make` invocation, so it self-adapts inside mech's ephemeral
   `git archive` trees too — for the Makefile's own tree-build rule) are
   exported once when the toggle is on.

**With BOTH fixes in place, real hits appear** — confirmed first on a real
suite (`tests/cli/run_cli_tests.sh` cold then warm, 269/269 passing both
times, hits 0 → 15/17 of the new calls on the warm rerun) and then on the
full corpus.

### `make test`: cold/warm, measured

| run | wall clock | notes |
|---|---|---|
| plain (no `CCACHE`) | 7m16s | the standing baseline, unchanged (docs/dev/plan.md [TT-3] row, 20,775 cases) |
| `CCACHE=1` cold | 32m01s | fresh `build-ccache/`; `ccache -s`: 65.28% cacheable, 41.13% of THAT already hitting (residual population from an earlier smoke check the cache dir wasn't cleared before — see caveat below) |
| `CCACHE=1` warm (rerun) | 29m48s | `ccache -s`: 65.23% cacheable, 64.59% of THAT hitting (7,599/11,765 — a REAL, healthy hit rate) |

**Verdict: NO, decisively, even with the fix working.** A 64.59% hit rate
still leaves wall time over 4x the plain baseline. The reason is the
workload's shape, not a wiring gap: `test-corpus` alone compiles ~20,000
generated matchers that each take sub-millisecond to a few milliseconds to
compile from scratch, and ccache's own per-call overhead — hash the
preprocessed output, check the manifest, and (since the split turns one
gcc invocation into two-or-three) do this MULTIPLE times per case — costs
more than the compile it is trying to avoid. Caching wins when the cached
work is expensive relative to the caching machinery's own overhead; this
workload is the opposite case by construction (thousands of tiny,
already-fast compiles), so `make test` is not a candidate for this toggle
at all, wiring correctness notwithstanding. (Caveat on the cold-run cell
above: `build-ccache/` was not fully empty at that run's start — a
same-session smoke check populated a handful of entries first — so the
41.13% cold-hit figure understates a truly-empty-cache run's wall time
slightly; it does not change the verdict, which rests on the WARM number
already being 4x plain.)

### One mech row: cold/warm/plain, measured

Different workload, tested because it plausibly differs: mech rebuilds the
WHOLE compiler tree from a fresh `git archive HEAD` copy once per sabotage,
and most sabotages touch only 1-2 source files — the tree-build compiles are
substantial real files (not sub-millisecond generated matchers), and most
of a sabotage's ~27 objects are BYTE-IDENTICAL to the previous sabotage's,
which is exactly the shape caching should help.

`bash tests/mech/run_sabotage_matrix.sh S26` (`SAB_SUITES="harness"`, a
heavier row than a codegen-only one):

| run | wall clock | `ccache -s` (cacheable / hit rate) |
|---|---|---|
| plain (no `CCACHE`) | 6.69s | — |
| `CCACHE=1` cold (fresh `build-ccache/`) | 6.80s | 82.69% cacheable, 16.28% hit (7/43 — intra-run reuse: the row's own 10-case corpus subset repeat-compiles the fixed `driver.c`, so even a "cold" cache warms itself mid-row) |
| `CCACHE=1` warm (rerun) | 5.00s | 82.69% cacheable, 56.98% hit (49/86, 71% of hits direct-mode) |

**Result: cold is a wash (~1.6% slower than plain — pure overhead, nothing
to hit yet), warm is 25% faster than plain.** A lighter row (`S01`,
`SAB_SUITES="codegen"` only, ~55-case suite) showed the same direction at
similar scale: 5.53s cold → 3.91s warm (29% faster), `ccache -s` going from
0/35 hits to 28/70 (71% direct-mode) — the tree's own ~27 object files
hitting near-completely on the second build of the SAME sabotage. Both
rows are a WITHIN-SABOTAGE repeat (same sabotage run twice), a weaker
signal than the real production case (the full matrix runs ~30+ DIFFERENT
sabotages back to back, each touching only 1-2 files out of ~27 — cross-
sabotage reuse should be even higher than what these two rows show, since
most of each fresh tree is byte-identical to the previous one). What both
rows DO prove directly: the tree-build fix (`CCACHE_NOHASHDIR`/
`CCACHE_BASEDIR` extended to the Makefile's own rule, not just `gen_cc`'s
callers) works across the different physical `mktemp` tree ccache saw each
run — the same cross-directory-identical-content mechanic the corpus fix
needed, now confirmed on the tree-build path too.

**Verdict: a qualified YES for mech, in contrast to `make test`'s decisive
NO** — modest (25-29% faster warm on these two single-row samples) but
genuine and mechanistically sound (real, substantial compiles being
reused, not thousands of sub-millisecond ones drowned in per-call
overhead). Not measured: the FULL ~50-minute matrix cold/warm (out of this
row's time budget) — the two single-row samples are the evidence on
record, with the reasoning for why cross-sabotage reuse should generalize
favorably stated above rather than assumed silently.

### The gen-timeout controls, verified under the toggle (the ruled caveat)

D45's positive control (a compile that must genuinely time out) and the
wall-backstop control both already compile with `-c` — they bypass
`_gen_cc_run`'s split/relativize path entirely (that path only activates for
the compile-AND-link shape) and are otherwise unaffected by the toggle. A
killed compile never completes, so ccache never gets a result to store,
regardless: `tests/lib/run_gen_timeout_tests.sh`'s full 18-check suite
(including both fire controls) was run twice under `CCACHE=1` — cold, then
warm on the SAME populated cache — and passed 18/18 both times. The
controls fire on every run, not just the first.

### Disk

`CCACHE_DIR` defaults to `build-ccache/` (repo-local, gitignored — already
listed in `.gitignore`), capped at ccache's own 5.0 GiB default `max_size`.
Measured usage after the full cold+warm `make test` cycle: 0.66% of that
cap (well under; the box has ~46G free regardless).

### Disposition

The wiring is CORRECT (both diagnosed blockers are actually fixed, not
papered over) and stays on the branch for the record — `CCACHE=1` is
opt-in, off by default, and a stranger's `make test` is provably unaffected.
Whether to merge it (someone doing a `-j1` single-core CI run, or a
tree-build-dominated workflow, might still want the toggle even though the
project's own generated-code-heavy suites do not benefit) is a manager
call, not this row's to make.

## The `timeout` binary itself (`TIMEOUT_BIN`, [TT-6], 2026-08-23)

**The finding** (`docs/dev/tt4_measurement.md`, "The `timeout` binary
itself"; [TT-4.1]/[TT-5] chartered [TT-6] off it). This box's default
`/usr/bin/timeout` is **uutils coreutils 0.8.0**, which polls its child
instead of blocking on it: MEASURED ~108.7ms of pure WALL per call, ~0 CPU.
`/usr/bin/gnutimeout` (GNU coreutils 9.7, also installed here) does the
identical job in ~4.2ms — uutils costs ~104.5ms of pure wall ABOVE bare
exec, per call, regardless of the duration being bounded. Every pcrec
invocation and every per-case matcher run in `tests/harness/run.sh`
(~19k calls in `test-corpus` alone, ~23,252 with the rest of the corpus
tally) and `gen_cc`'s wall wrapper each paid this once per call, unbounded
by what the harness itself does.

**The fix.** `tests/lib/timeout_bin.sh` (new) resolves `TIMEOUT_BIN` once
per process: an env override wins outright; otherwise the default `timeout`
on `PATH` is used bare if it self-identifies as GNU coreutils (the common
case on a stranger's box — this changes NOTHING for them, same binary, same
invocation, D2/R5-Q1's "a stranger's `make` must not fail" spirit extended
to "must not even notice"); otherwise `/usr/bin/gnutimeout`, then `gtimeout`
(Homebrew's coreutils prefix, macOS) are tried in turn if present and GNU;
otherwise it falls back to plain `timeout`, so a box with no GNU coreutils
`timeout` anywhere pays the uutils tax exactly as it did before this file
existed — never a hard failure over a missing binary. The resolved choice
is printed once per top-level script to stderr, only when it differs from
plain `timeout`, so a log names which binary ran without spamming a log
sourced by every one of a suite's per-case subshells.

`tests/lib/gen_timeout.sh` sources it (its `gen_cc` wall wrapper was the
single highest-traffic call site) and every other file in the tree that
invoked a bare `timeout` was swapped to `"$TIMEOUT_BIN"`: `tests/harness/
run.sh` (pcrec's own invocation, and the ~19k-call per-case matcher run —
the two sites the finding named directly), `tests/cli/run_cli_tests.sh`,
`tests/vm/run_vm_tests.sh` and `tests/thread/run_thread_tests.sh` (already
sourced `gen_timeout.sh`, so `TIMEOUT_BIN` came for free), and
`tests/reject/run_reject_tests.sh`, `tests/bench/run_bench.sh`,
`tests/bench/compare/compare.sh` and `scripts/Makefile`'s
`tests/%.testreport` recipe (`make testscripts`, not part of `make test`),
none of which sourced `gen_timeout.sh`, so each gained its own
`. tests/lib/timeout_bin.sh`. `tests/mech/run_sabotage_matrix.sh` needed no
separate change: it drives generated patterns through `tests/harness/
run.sh`, which now carries the fix.

**The bench gate's two budgets measure the wrapper's own launch cost, and
now measure it honestly instead of not at all.** `tests/bench/run_bench.sh`
COMPILE-SPEED and GCC-TIME bracket their wall-clock timer (`cs_t0`/`cs_t1`,
`g_t0`/`g_t1`) AROUND the `timeout` invocation itself, so the wrapper's
launch cost sat INSIDE `COMPILE_BUDGET_SECS` (0.4s, measured median
0.114s) and `GCC_O1_BUDGET_SECS`/`GCC_O2_BUDGET_SECS` (2s, measured
~0.214-0.222s) — a large fraction of a ~0.1-0.2s measurement was uutils'
own overhead, not pcrec's or gcc's. Both numbers read LOWER and MORE
HONEST after this swap; `tests/bench/CLAUDE.md`'s archived medians predate
it and need re-measurement before either budget is next retuned.
THROUGHPUT's `run_bdriver` (and `compare.sh`'s `run_driver`) are
unaffected: the driver binary reports `secs=`/`mbps=` (or `status=`/
`secs=`/`mbps=`) about its OWN internal loop, not wall time measured
around the wrapper, so the K22 guard's exit-124 assertion (`tests/vm/
run_vm_tests.sh`, see its own CLAUDE.md) and every other exit-124-shaped
check are unaffected in the same way — both uutils and GNU `timeout` exit
124 identically on a real timeout.

### Measured (this box, 2026-08-23)

| measurement | before (uutils `timeout`) | after (`TIMEOUT_BIN`=`/usr/bin/gnutimeout`) | ratio |
|---|---|---|---|
| `make test` wall (`-j12 -Otarget`, `build/before.log`/`build/after.log`) | 10:32.82 | 10:15.96 | 1.03x |
| `make test` user+sys (`/usr/bin/time -v`) | 2021.91s + 1970.06s = 3991.97s | 1988.06s + 1854.53s = 3842.59s | 1.04x |
| `make test-corpus` wall, isolated, quiet box (`build/corpus_before.log`/`build/corpus_after.log`) | 6:44.24 | 1:04.08 | **6.31x** |
| `make test-corpus` user+sys, isolated | 250.43s + 261.11s = 511.54s | 324.63s + 210.92s = 535.55s | ~1x (CPU-bound work is unchanged; wall dropped because the sleep-per-call tax is gone, not because less work ran) |

**Why the full `make test` figure barely moves while the isolated section
shows 6.3x.** `-j12 -Otarget` runs many independently-scheduled `test-*`
sections concurrently; at the load this produces (33-41 measured during the
full run), a section that is mostly SLEEPING (uutils polling a child) is
invisible in the wall total — other sections' real CPU work fills the same
wall-clock window regardless. The tax only shows up in wall time where
sections run close to serially: an isolated single-section run (`make
test-corpus` alone, box otherwise idle — the pair above), the sanitizer
axes' own serial-ish battery legs, `make mech`'s per-sabotage rows, and any
single-worker (`PROCS=1`) run. `test-corpus`'s own PROCS=12 internal
fan-out (`parallel: 121 of 121 file workers reported`) is unaffected either
way — both runs used it identically — which is why the isolated pair is the
number to trust for what this fix actually buys, not the full-suite total.

Case counts are IDENTICAL between before and after in every comparison
above (`corpus 22358/0`, `cli 270/0`, `reject` 282 rejections/105 rows
iterated/99 accept controls/0 known-wrong — checked line for line, sorted,
between `build/before.log` and `build/after.log`) — the swap changes which
binary runs, never what a check asserts.

### Overriding the choice

`TIMEOUT_BIN=/path/to/timeout make test` (or any suite script run
directly) pins a specific binary, skipping detection entirely — useful to
force plain `timeout` back on for an A/B comparison, or to point at a
binary this file's detection order does not find. `tests/lib/
timeout_bin.sh`'s own header has the full detection order.

### Sabotage anchor

`tests/mech/sabotages/S43_d45_timeout_removed.sh`'s `SAB_BEFORE` targets
`gen_cc`'s wall-wrapper line in `tests/lib/gen_timeout.sh`, which this
change edited (the bare `timeout` token became `"$TIMEOUT_BIN"`) — the
anchor was re-derived in the same commit; see that file's own history
comments. `scripts/m6read_check_sab_anchors.py`: 118 sabotages checked
(119 anchor sites), all anchors resolve. `bash tests/mech/
run_sabotage_matrix.sh S43`: `gentmo:2fail/16pass`, DETECTED.

## The encoding seam's checks ([M5-SEAM], 2026-08-18)

D58 built the DD-12 residual seam ahead of M6: an artifact embeds exactly
one encoding's residual block, chosen per compile call, and the first
residual entry is `<prefix>_next_pos`. Two new check classes came with it,
plus one rider, and each covers something no existing suite could.

**`tests/encseam/` (`make test-encseam`) — the find-all PROTOCOL, run.**
The `.rxt` corpus checks what a pattern MATCHES, one search at a time; it
never runs a find-all LOOP, so `docs/spec/match_api.md` §3.1's protocol —
the one piece of the contract a caller writes themselves — was documented
and measured but never pinned. This suite compiles that loop
(`findall_driver.c`, a transcription of the spec's own code) against real
artifacts and runs it over `findall_cases.txt`, on BOTH engines (each
pattern compiled captures-on and `--no-captures`).

Its oracle is `python3 re`, and it is TWO-ANSWERED, which is the part worth
understanding before adding a case. `findall_oracle.py` reports both what
`re.finditer` says and what §3.1's protocol says when driven by
`re.search`, because those differ for an empty-PREFERRING pattern: PCRE2 and
python retry an empty match position under "empty match not permitted here"
(`PCRE2_NOTEMPTY_ATSTART`) and pcrec's entry points cannot express that
retry. So pcrec must equal the PROTOCOL answer exactly, and each case's
declared class — `exact` or `lossy` against `finditer` — is checked in BOTH
directions: an `exact` case that starts diverging fails, a `lossy` case that
stops diverging fails, and a `lossy` case whose spans are not a strict
SUBSET of `finditer`'s fails. That last clause is the one that matters:
"differs somehow" would pass a real miscompile. What the oracle shares with
the artifact is the LOOP RULE, which is the spec text under verification;
every span in it comes from python's own independent engine.

Non-vacuity was measured by sabotaging the driver's advance
(`fa_next_pos(...)` -> `caps[0][0] + 2`): 26 failures, 0 passes.

**`tests/codegen/run_codegen_tests.sh`'s `[M5-SEAM/DD-12(7)]` check — no
engine body calls a residual entry.** DD-12 (7) rules that the per-encoding
header is the right seam for the runtime-identity RESIDUE and the wrong one
for the HOT PATH, "ENFORCED BY CHECK, NOT CONVENTION". A behaviour test
structurally cannot do it: under the byte backend `<prefix>_next_pos` IS
`pos + 1`, so an engine that advanced through it would match identically and
every oracle in the tree would stay green while the artifact acquired
exactly the cross-seam call the architecture forbids. The check reads the
emitted engine bodies across six emission shapes in both artifact forms
(split and self-contained). Its POPULATION IS DERIVED, not typed: the
residual entry names are extracted from the artifact itself (each residual
declaration is preceded by the backend's own `ENCODING RESIDUAL entry`
comment), so a backend that adds a second entry is covered the day it lands
— and finding NO residual entry is a hard failure, not a pass.

Sabotage: `tests/mech/sabotages/S68_residual_in_hot_loop.sh` makes the
emitted bitmap prefilter's skip loop advance through `<prefix>_next_pos` —
the shape a developer holding a fresh "advance one character" helper would
actually write. Measured DETECTED: `codegen 3fail/41pass`, `corpus
0fail/56pass`. The corpus staying green IS the finding.

**The `[K27]` rider — the legal `(s == NULL, n == 0)` subject, run under
the sanitizers.** `docs/spec/match_api.md` §3.1 admits a NULL subject when
`n == 0`, and the emitted `memchr` prefilter used to receive it (technical
UB in EMITTED code, which a user compiling a generated matcher under their
own `-fsanitize=undefined` sees pcrec's name on). The battery was green for
a structural reason worth remembering: its generated-code axis runs the
CORPUS, and no corpus case passes `s == NULL`, so the instrumented axis had
nothing to see. The check therefore compiles a memchr-prefilter artifact,
links a driver that calls `<prefix>_search(NULL, 0, 0, NULL)` and
`<prefix>_next_pos(NULL, 0, 0)`, and RUNS it — in
`run_codegen_tests.sh`, which is already in both the `make ubsan` and
`make asan` suite lists, so the run is instrumented on those axes and pins
the answers on the plain one. Both directions measured at landing: clean
under UBSan with the guard, and `null pointer passed as argument 1` with the
guard stripped back out.

**One infrastructure note that cost two suite failures.** Adding
`src/gen/enc/` put compiler sources TWO directory levels down for the first
time, and two suites assembled their own build of the compiler from a
one-level glob (`src/*/*.c` in `tests/codegen/run_trie_identity.sh`, a
hand-listed `for d in core parse ir opt gen` in
`tests/thread/run_thread_tests.sh`). Both now `find` the sources instead.
The failures were loud here (undefined references), but the shape is the
silent one: a differential's reference build, or a TSan library, quietly
assembled from a different source set than the subject.

## Capture-group expectations ([M4.5a], 2026-08-14)

engine_m4.md §3.6/§3.7 and match_api_m4.md §2 (the C1–C11 caps-array
contract) needed a test-format and oracle-tier home before [M4.5]'s VM
emitter lands and starts delivering per-group offsets. This section is that
home: the `g`/`gp` line syntax (already listed under "The `.rxt` format"
above), what `run.sh` and `verify_rxt.py` do with it, and the seed corpus at
`tests/captures/basic.rxt`.

### Design: backward-compatible, artifact-size-agnostic

Every `.rxt` file that existed before this landed is still valid and still
means exactly what it meant — `g`/`gp` are new, purely additive line kinds;
no existing line's grammar or semantics changed. `driver.c` prints one pair
per `RX_NCAPS` slot instead of a fixed two numbers, but `RX_NCAPS` is 1 on
every artifact today (match_api_m4.md D42.2 — captures only exist behind
[M4.5]'s VM), so the printed line is byte-identical to before on the entire
existing corpus; nothing needed re-verifying.

The format is deliberately artifact-size-agnostic rather than pinned to
today's `RX_NCAPS == 1` ceiling: a `.rxt` case can assert group spans for
slots the CURRENT compiled artifact cannot yet deliver (`gp`, pending-VM —
see below), so the corpus can be authored once, against the pattern's true
semantics, and grow LIVE automatically as the VM emitter lands, rather than
being rewritten when it does.

### `g` vs `gp`: live vs pending-VM, and the population-accounting rule

- **`g <slot> <start> <end>`** claims the slot is checkable RIGHT NOW. `run.sh`
  reads the artifact's actual `RX_NCAPS` out of its generated `gen.h` (the
  same value the compiled matcher itself was built against, not a guess) and
  compares it to `<slot>`. If `<slot> >= RX_NCAPS`, that is **a hard FAILURE,
  never a silent skip** — a corpus author claiming `g` for a slot the
  artifact cannot deliver is a corpus bug, not a harness gap, and the harness
  says so by name ("claimed with 'g' (LIVE) but artifact's RX_NCAPS=... does
  not deliver it — use 'gp'"). This is the population-accounting discipline
  the brief asked for: an out-of-range capture expectation is counted as a
  failure, so it cannot vanish from the pass/fail total by accident.
- **`gp <slot> <start> <end>`** claims the slot MAY be beyond today's
  artifact. If `<slot> >= RX_NCAPS`, the case is counted in a separate
  **pending-vm** bucket — not pass, not fail, printed on its own summary
  line (`group cases pending-vm: N`) so it is never invisible and never
  silently mixed into either count. This is deliberately NOT shaped like
  `tests/known_fail/` (a ratchet for a CONFIRMED, deferred BUG): a pending-vm
  case asserts nothing is wrong — it is a true statement about the pattern
  that today's DFA-only engine structurally cannot check yet, not a bug
  anyone is tracking. If `<slot> < RX_NCAPS` (the VM has landed and now
  covers this slot, or a future engine's ceiling simply grew), a `gp` line
  **self-activates**: it is checked exactly like `g`, no corpus edit
  required, and a wrong value fails it like any other live case. Authors are
  free to leave the `gp` marker in place after that point (it costs nothing)
  or promote it to `g` for documentation clarity — the harness behaves
  identically either way once the slot is in range.
- Both `g` and `gp` require an immediately-attachable `m`/`ms` case earlier
  in the same block (the most recent one) — a `g`/`gp` line after an `n`/`ns`
  case, or with no case at all yet, is a hard parse-time failure (a no-match
  assertion has no captures to check).
- `RX_UNSET` is spelled `-1 -1`, matching the ABI's own `{-1,-1}` convention
  exactly (match_api_m4.md §2.1, C5) — a lone `-1` in only one slot is a
  hard parse error in both `run.sh` and `verify_rxt.py`, since `RX_UNSET` is
  defined as symmetric.
- A block-level compile/build failure (pattern rejected, driver failed to
  build, `RX_NCAPS` unreadable from `gen.h`) fails every attached `g`/`gp`
  expectation too, `gp` included — "the block never got far enough to check
  anything" is not a reason to call a pending case's non-result a pass, or
  to leave it uncounted; extraction failure is FAIL, never a vacuous pass or
  a silent pending.

### The python `re` oracle tier

`verify_rxt.py` checks every `g`/`gp` line against python `re`'s
`match.span(<slot>)` on the same subject/startpos as the case's preceding
`m`/`ms` line, **identically for `g` and `gp`** — pending-ness is a fact
about what pcrec's CURRENT artifact can deliver (`RX_NCAPS`), which the
python oracle has no notion of and does not need: it verifies the
EXPECTATION written in the corpus, independent of whether `run.sh` can check
it yet. A `<slot>` beyond the pattern's own lexical group count
(`compiled.groups`) is a hard failure regardless of `g`/`gp` — that is
always a corpus authoring bug, never a pending-VM situation, since python
already knows the pattern's true group count without needing any engine to
run.

**The oracle rule governing this tier is the three-way rule from
engine_m4.md §3.6 (R21 E-ASK-1/D44)**, unchanged by this landing: python and
libpcre2 are BOTH checked once the libpcre2 differential exists ([M4.7]);
there is no pre-built exclusion mechanism, and a case where pcrec disagrees
with both oracles is a bug, never a silent exclusion. This tier is the
python half of that rule, staged first per D4's discipline — the same
staging the base tier already used.

### Seed corpus: `tests/captures/basic.rxt`

14 `m`/`ms` cases (13 `m`, 1 `ms` exercising startpos + group attachment
together) carrying 3 `g` (live, slot 0 — the whole match, deliverable by
every artifact today, C3) and 28 `gp` (pending-VM, slots 1+) capture
expectations — 45 total oracle-verified lines, all group values computed
from and cross-checked against python `re`'s own `match.span()`, all
whole-match spans additionally verified against the real `build/pcrec`
output before landing (not merely believed correct). Patterns cover:
sequential groups (`(a)(b)(c)`), an optional group both matching and
not-matching (`(foo)?bar`, exercising `RX_UNSET`), a repeated capturing
group keeping only its LAST iteration's span (`a(b|c)+d`, PCRE2
leftmost-first priority — engine_m4.md §3.1), nested groups
(`((a)(b))c`), alternation where exactly one branch's group participates
(`(a)|(b)`), a zero-iteration group (`(a)*b`), an optional MIDDLE group
(`(x)(y)?(z)`), and a three-way alternation/repetition mix
(`(ab|a)(c|bcd)(d*)`).

Directory tree row (already listed under "Organizing tests by component"
above) needed no change — `captures/` was always the planned home for this
corpus; this landing is what actually populates it.

### Sabotage validation

Every failure path this section describes was planted and observed to fire,
then reverted (scratch `.rxt` files, never committed):

- a wrong LIVE (`g`) group span — caught, `expected (...) got (...)`
- a `g` (LIVE, non-pending) line claiming a slot beyond the artifact's
  `RX_NCAPS` — caught, the "use 'gp'" message, NOT a silent skip
- an asymmetric `RX_UNSET` (`-1` in one slot only) — caught at parse time,
  both in `run.sh` and in `verify_rxt.py`
- a `g`/`gp` line with no preceding `m`/`ms` case, and one immediately after
  an `n`/`ns` case — both caught at parse time
- a pattern that fails to compile with a `gp` (pending-VM) expectation
  attached — the attached `gp` case is reported FAILED, not silently
  dropped and not counted as pending (a block that never ran proves nothing
  about a slot being "future-live")
- on the python oracle side: a wrong `gp` span, and a slot number exceeding
  the pattern's own group count — both caught, independent of the
  live/pending distinction (the python oracle only cares whether the
  EXPECTATION is correct, never whether pcrec can check it yet)
