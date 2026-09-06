# Testing pcrec

pcrec's test suite runs generated C code, not pcrec's internals directly: for
each test pattern, the harness invokes the `pcrec` CLI to generate a matcher,
compiles that matcher with the system C compiler, and runs it against a set
of subject strings, checking the reported match span (or lack of one)
against the expectation encoded in the test file.

**This file is process record** (DEVDOC): battery composition, measured
runtimes, tiered-testing/section-target guidance, the sanitizer and lint
battery, compile-caching and timeout-binary findings, landing-gate results,
and the living oracle-exclusion catalog. **The `.rxt` format itself and the
driver protocol are contract documents and live in
`docs/spec/rxt_format.md`** ([SPEC-1.6], 2026-08-25, extracted from this
file) — read that first if you are adding a test or a test directory.

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

> **THE SENTENCE ABOVE HAS DRIFTED, AND [ENG-ISL] IS CORRECTING ONLY THE PART
> IT TOUCHES** (panel r53, 2026-09-03). `make test` runs **33** sections today,
> not eight — `TEST_SECTIONS` in the Makefile is the list of record, the
> completion trailer prints `sections ran: N/M` against it, and that is what a
> reader should consult rather than this paragraph. Two sections this narrative
> never gained a mention of:
>
> - **`make test-island`** ([ENG-ISL] STEP 1, new here):
>   `tests/island/run_island_tests.sh`, the alternation island's structural
>   half — that the island fired where the stamp says, declined where
>   `docs/spec/tuning.md` §2.20 says it must (including both directions of the
>   measured narrow-width knee), allocated no slot, and left the declined
>   population byte-identical under `-fno-alt-island`. 24 checks, **0.5 s** —
>   it compiles ~25 single artifacts and runs none of them, so it is one of the
>   cheapest sections in the suite. Its `.rxt` corpus rides `test-corpus` like
>   every other module's and is deliberately BLIND to the island, the axis
>   being answer-identity-preserving.
> - **`make test-altcls`** ([OPT-ALTCLS]) — **pre-existing drift**, missing
>   from this paragraph since that row landed, and noted here rather than
>   silently added because the gap is older and wider than this change: the
>   count has been wrong by a growing margin for many rows, and fixing the
>   sentence properly is a separate pass over `TEST_SECTIONS` that nobody has
>   taken.

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
| `RXTROUTE`  | unset (`default`)          | ([DD-14.FB]) The INITIAL `frames-buffer=` route for every block in the run, overridden per block by a directive. `RXTROUTE=null` is the useful one: spec §10.3 defines a NULL descriptor to BE the un-suffixed call, so re-running any corpus under it must reproduce that corpus's result cell for cell — the NULL-equivalence control as a corpus-wide axis rather than a handful of hand-written cells. A numeric value is accepted for symmetry but is a blunt instrument (a capacity that suits one block starves another). **It is MANUAL-ONLY, exactly like `RXTFLAGS`**: nothing in `make test` or in any section target sets it, so every automated run uses the default route and this axis is exercised only when a person asks for it by hand |
| `RXTFLAGS`  | unset (empty)              | ([DD-14 wave G]) EXTRA `pcrec` flags appended (last, so a directive-supplied flag on the same axis wins) to every compile in the run, for sweeping one corpus over a COMPILER AXIS the `.rxt` format has no directive for (e.g. `-fno-splice-calls`). Empty by default, so a plain run is byte-for-byte unchanged; manual-only like `RXTROUTE` — was previously documented only in `tests/harness/run.sh`'s own header comment (`run.sh:13-22`), not here — gap closed by [SPEC-1.6] |
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

## The `.rxt` test format and driver protocol

**Moved to `docs/spec/rxt_format.md`** ([SPEC-1.6], 2026-08-25): the `.rxt`
directive grammar (`pattern`/`flags`/`features`/`perr`/`m`/`n`/`ms`/`ns`/
`g`/`gp`/`gu`/`engine`/`budget`/`frames-buffer=`), the subject escape table,
oracle-verification requirements (the default python-`re` oracle, the
`# pcre2-only` exclusion convention, per-directory oracle overrides), how
`run.sh` evaluates a block, the driver protocol (`tests/harness/driver.c`'s
CLI, exit codes, the D45 budget policy), and how to add a new component test
directory all live there now — that document is the contract a contributor
adding a test needs; this file keeps the process record below (runtimes,
battery composition, sanitizer/lint measurements, TT-* notes, the specific
current oracle-exclusion catalog).


## R1 review updates (2026-08-09)

- The oracle-verification mechanism itself (the default python-`re` oracle,
  the `# pcre2-only` exclusion convention, per-directory oracle overrides)
  is now `docs/spec/rxt_format.md`'s "Oracle verification" section
  ([SPEC-1.6]). What follows here is the LIVING, evolving catalog of
  currently-known python/PCRE2 divergences behind existing `# pcre2-only`
  marks — process record, not contract.
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
  default. (The per-case timeout NUMBERS this bullet originally gave — "pcrec
  60 s, compiler 120 s, test binary 10 s" — were superseded by D45's
  CPU-primary budget regime below and are STALE as a description of today's
  numbers; current values live in "D45 — every generated-code compile runs
  under a budget" and `docs/spec/rxt_format.md`'s "The driver protocol",
  since they are recalibrated by measurement independent of either format
  document. Found during [SPEC-1.6]'s parser-vs-prose check.)

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
into eight sections (`test-codegen` wraps three scripts —
`run_codegen_tests.sh`, `run_dfa_stamps.sh` ([DD-13], 2026-08-25) and
`run_trie_identity.sh` — since this file already describes them as one
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
| `make test-codegen` | `tests/codegen/run_codegen_tests.sh` + `run_dfa_stamps.sh` + `run_trie_identity.sh` | yes |
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
| `make test-rxtsource` | `tests/rxtsource/run_rxtsource_tests.sh` ([DD-13b.W1.1] INV-COMPAT — see below) | yes |
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

**[DD-13] (2026-08-25) — `test-codegen` gains a THIRD script, and the section
re-check this document asks for was done.** `tests/codegen/run_dfa_stamps.sh`
holds the DFA artifact's three D46 selection stamps (`RX_ENGINE "dfa"`,
`RX_DFA_SCAN`, `RX_DFA_PREFILTER`; `docs/spec/match_api.md` §6.3) to the LOOP
THEY NAME — every verdict is derived from the emitted matcher text and
compared against the macro, so a stamp that drifts from its mechanism is a
red. It also carries NAMED WITNESSES, one per documented value.

**[DD-13c] (2026-08-25) — the same script, widened by the r37 panel's two
SCOPE findings.** Nothing about the derived-from-the-text design changed; what
changed is the population and one rule:

- `RX_DFA_SCAN` has a third value, `"empty"` — a pattern that provably matches
  nothing emits a body that is one `return 0`, on BOTH engines. The script used
  to EXEMPT those artifacts from the scan comparison (there was no value to
  compare against); it now asserts `"empty"` on them like any other bucket, and
  the exact named manifest (the four such patterns the corpus holds) stays.
- **The VM half became an IFF.** The old rule was "no `RX_DFA_*` macro may
  appear on a VM artifact". That was wrong about the §6.1 HYBRID, which inlines
  the DFA emitter's own scan as `static <prefix>_prefilter` and now stamps the
  two `_DFA_*` lines for it. Both directions are asserted, over the whole
  corpus and on named witnesses: a VM artifact carries those macros IFF its
  emitted text contains that inlined body IFF `RX_VM_PREFILTER` is `"hybrid"`.
  The middle term is matcher TEXT, so neither `#define` is ever checked
  against the other alone. The hybrid population is held to the SAME two
  agreement comparisons the DFA artifacts are.
- **The RUNTIME MIRRORS are checked here too**, because this is the script that
  already compiles every corpus pattern: `rx_info.scan`/`.prefilter` (the two
  fields `[DD-13c]` appended to the struct, `docs/spec/match_api.md` §6) must
  agree with the macros they mirror on EVERY compiled artifact of BOTH engines
  — 2,483 of them — with `NULL`/`"none"` where the macros are absent. A third
  source in the same one-pass `awk`, kept as separate from the other two as
  they are from each other: struct-literal initializer lines, not `#define`s
  and not matcher text. The line count is asserted as well (exactly one of
  each), so a mirror that stopped being emitted on one engine cannot leave the
  comparison vacuous on that half.
- **Every agreement denominator is COUNTED at its comparison site**, not
  derived from bucket sizes, and the count is itself asserted against the
  population that was due. This came out of the change's own validation: a
  plant that routed 1,263 artifacts past a comparison left the verdict reading
  "on all 2258 artifacts" — a true sentence about a population nobody compared.

It belongs in `test-codegen` rather than beside `run_vm_identity.sh` under
`test-vm` on the [M4.5c] test: it is compile-only (no `gcc`, no matcher is
RUN), which is exactly the "codegen structural checks" concept this section
already is. MEASURED on the project box, 2026-08-25, whole corpus (2,772
patterns, 995 DFA + 1,488 VM artifacts + 289 refused):

| shape | wall |
|---|---|
| `derive` + four `sed`/`grep` per artifact, serial | 3m50s |
| one `awk` per artifact, serial | 2m03s |
| the same, sharded at `PROCS=4` | **37.3s** |

Only the third shipped. The sweep shards by LINE CHUNKS of one pattern file
(`split -n l/N`) rather than by `xargs` over pattern text — a pattern is
arbitrary bytes and every quoting scheme for passing it as an argument is a
bug the corpus will find — and each worker writes verdict TOKENS to its own
file, so no counter crosses a process. `PROCS` selects the shard count
(default `nproc`); the population and all sixteen verdicts are identical
serial and sharded, measured both ways. Because `test-codegen` runs its three
scripts through `tests/lib/run_group.sh`, the section's own wall time is the
max of the three rather than the sum.

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

> **READ "The recursion identity gate is two comparisons" (below, [DD-14.FB],
> 2026-08-25) BEFORE ACTING ON THIS SECTION.** Everything here about the four
> axes, the opt-in ruling and the `ac4917d` pin still holds, but the gate now
> asks TWO questions per axis — (A) the PROGRAM REGION against `ac4917d` and
> (B) the WHOLE FILE against `c940551` ([DD-13c]; was `469a432`, [OPT-1]'s) — because the caller-buffer wave's
> announced `abi` 2 → 3 boundary put a change on every artifact's surface. A
> reader who stops at this section will expect one number per axis and find
> two.

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

## The recursion identity gate is two comparisons ([DD-14.FB], 2026-08-25)

`make test-recursion-identity` (opt-in) no longer asks one question. Since the
caller-buffer wave made the emitted surface change on EVERY artifact — an
announced `abi` 2 → 3 boundary, D40 regime 1 — a whole-file comparison against
the pre-module pin `ac4917d` can never be green again. The gate now runs:

- **(A) the PROGRAM REGION vs `ac4917d`** (unchanged reference): `goto
  <prefix>_L0;` … `<prefix>_accept:`, unfiltered past D37's three stamp lines,
  so comment sensitivity inside the region is kept. This is the module claim
  the gate exists for.
- **(B) the WHOLE FILE vs `c940551`** ([DD-13c]'s last `src`/`lib`/`cli`
  commit; was `469a432`, [OPT-1]'s, `5991d4c`, [DD-13]'s, and `8fc1e51`,
  [DD-14.FB]'s): byte-exact again from that pin forward. **Re-pinned 2026-08-25 by [DD-13]**, which gave every DFA artifact
  three D46 selection stamps (`RX_ENGINE`, `RX_DFA_SCAN`,
  `RX_DFA_PREFILTER`) and bumped `rx_info.abi` 3 → 4. That change moved NO
  struct offset and NO emitted program byte — (A) is byte-identical against
  the unchanged `ac4917d` pin on all five axes — and it re-pinned (B) anyway,
  because (B) compares WHOLE FILES and three new `#define` lines are a
  whole-file difference on ~2,000 artifacts. That is the reading to copy: (A)
  answers "did behaviour move", (B) answers "did bytes move", and only the
  second is what `abi` versions.

Both numbers are printed on their own lines. `RECURSION_IDENTITY_REF` and
`RECURSION_IDENTITY_FILEPIN` move them independently. The gate refuses rather
than skips when either pin is absent from history, and refuses if the FILE pin
predates the FB surface — a pin set too early would put every artifact's
surface back in the diff and report the failure the re-pin exists to retire.
`tests/codegen/CLAUDE.md` carries the measurement (200 distinct lines, the
`rx_match` over-strip, the blank-line residue) behind rejecting a wider filter.

**Re-pinned again 2026-08-25 by `[DD-13c]`** (`abi` 5 -> 6; `[OPT-1]`'s two-tier entry took 4 -> 5 immediately before),
for the same reason and with the same (A) result: the r37 panel's two scope
findings move emitted `#define` bytes on the four proven-empty DFA artifacts
and on every VM hybrid, and move nothing inside the program region.

**[TT-11]/D76 (2026-08-25): the two pins have two different OWNERS, and the
FILE pin's guard is now STRUCTURAL.** (A)'s pin is the MODULE's promise
(pre-module, never moves). (B)'s pin is owned by the emitted `abi` NUMBER
(`rx_info.abi`, stamped by `src/gen/emit_dfa.c`): it IS, by definition, the
commit that introduced the CURRENT `abi`, and any change to emitted
scaffolding — comments, declarations, layout — is an `abi` bump AND a re-pin
of (B) to that change's last `src`-touching commit, in the SAME change. The
gate used to guard the pin with an ad-hoc `grep -q RESUME_FRAME_SIZE` against
the pin's own `emit_dfa.c` source — a probe that encoded [DD-14.FB]'s own
boundary by name and would say nothing about the next scaffolding change. It
now builds an artifact from each compiler on a call-free pattern and requires
their `.abi = N` stamps to agree, refusing with a message naming the fix
("bump `abi` in src/gen/emit_dfa.c and re-pin comparison (B) ... in the same
change (D76)") when they do not.

## The caller-provided frame buffer's checks ([DD-14.FB], 2026-08-25)

D71 item 2's caller-provided buffer (`docs/spec/match_api.md` §10) is checked
in FOUR places, and the split is deliberate: what is a standing property of
every artifact rides `make test`, and what is a measurement about one
reservation does not.

**In `make test`:**

- **`tests/recursion/framebuffer.rxt`** — the behaviour, through the
  `frames-buffer=` directive documented above. 16 cases on three patterns: the
  give-up boundary through the default entry (n = 342 matches, n = 343 is
  `PCREC_ERR_FRAMES`), the SAME subject matching through `<prefix>_search_in`
  with a bigger buffer IN THE SAME BLOCK off ONE compile, the trail binding
  first (200000,3072 still gives up — design §4's measured finding, pinned),
  the frames binding too (512,400000), the NULL descriptor repeating the
  default entry's answers verbatim, and the same routes on a call-free VM
  artifact and on a DFA-selected one where the surface is inert.
- **`tests/codegen/run_codegen_tests.sh`'s `[DD-14.FB]` block** — six
  structural checks a corpus cell cannot make: the six entry declarations
  byte-exact on both engines (the three existing ones character for character
  — spec §10.8's compatibility promise, which the corpus cannot defend because
  it recompiles its driver every run), the five sizing macros real on a VM
  artifact and inert on a DFA one, the three `_Static_assert`s that reconcile
  the stamped sizes with the real `sizeof`, that NO capacity guard still
  compares against a stamped constant, the delegation direction on the emitted
  TEXT, and `rx_info`'s four fields at `abi` 3.
- **`make test-stackdepth`** (`tests/thread/run_stackdepth_tests.sh`) — the
  128 KB thread, [TS-4]'s matcher instance. Deliberately NOT under
  ThreadSanitizer: TSan changes the stack a call needs, so a stack-fit
  question asked under it is a question about TSan. It prints a `KNOWN:` line
  on a green run — K33 is a live defect D73 chose to keep — and FAILS if the
  default entry ever stops dying. See its own header for the causal control.

- **`make test-premul-table`** (`tests/codegen/run_premul_table.sh`) —
  [OPT-3]'s PRE-MULTIPLIED DFA TRANSITION TABLE
  (`docs/design/premultiplied_dfa_table.md`). **In `make test`, deliberately
  NOT in `SMOKE_SECTIONS`**: it sweeps the whole corpus and compiles and runs
  sixteen matchers, measured **~6 minutes** on this box at 2026-08-26, and
  `make smoke` includes `test-codegen` and is already at its target. That is
  the same placement argument `run_endvar_identity.sh` (under
  `test-assertions`) and `run_ir_listing.sh` (under `test-vm`) already carry.
  What it guards is invisible to every answer-checking suite in the tree,
  because the transform is answer-preserving by construction: the state
  variable left `int` (correct, and the optimization then buys nothing — a
  SILENT performance regression), the generation-time bound not switching, and
  a cell that is not premultiplied or a sentinel that collides. Validated in
  three failing directions; the numbers are in the script's own header and in
  `tests/codegen/CLAUDE.md`.

- **`make test-anchored-match`** — [ENG-ABS]'s ANCHORED MATCH-HERE FORM
  (`docs/design/anchored_match_unwrapped.md`), a `run_group` of TWO scripts
  that check different things and do not substitute for each other. **In
  `make test`, deliberately NOT in `SMOKE_SECTIONS`**, `test-premul-table`'s
  argument: the pair sweeps the whole corpus twice, compiles and RUNS 1,213
  two-artifact drivers, and builds a second compiler — measured **~7 minutes**
  at `PROCS=8` on this box, 2026-08-29.
  - `tests/codegen/run_anchored_match.sh` (14 checks) reads the ARTIFACT: the
    stamp against the emitted body, the anchored body's freedom from all three
    candidate-start mechanisms (r39's MISCOMPILE-1 one row over — a set
    derived for the SCAN role is unsound in a MATCH-HERE), `_match_caps`'s
    span and dead-group fill, the OVERFLOW arm through a
    `-DPCREC_ANCHORED_MAX_STATES=6` reference compiler, and the corpus census
    with every population pinned.
  - `tests/anchored/run_anchored_diff.sh` (5 checks) is the ANSWER half, and
    **the measurement that justifies it is the entry to read**: before it,
    NOTHING in this tree asked what `<prefix>_match` answers.
    `tests/harness/driver.c` drives `<prefix>_search` and touches the anchored
    entries only as an `_in`-vs-un-suffixed cross-check (both sides one code
    path); `make test-axes` compares the corpus's SEARCH answers under each
    deny flag. Sabotage **S189** is that made real: `prune=false` on the third
    machine makes `a|ab` at `ctx->pos` 0 over `"ab"` return 2 where it must
    return 1, and on the planted tree `tests/base/alternation.rxt` — the file
    that CONTAINS that pattern and that cell — is **26 passed / 0 failed** and
    `run_anchored_match.sh` is **14 passed / 0 failed**. Landing figures:
    1,213 corpus patterns × 18 subjects, every position 0..n+1, all four
    anchored entries plus the search control — **147,620 cells, 0
    divergences**; plus §2, the captures-on arm added at the r41 close
    (finding S4), 8 named `RX_NCAPS >= 2` witnesses over **976 cells**,
    which is the only thing in the tree that can see `_match_caps`'s
    dead-group fill (sabotage S190).
  - **THE OVERFLOW ARM'S POPULATION IS ZERO AND THAT IS MEASURED**, not
    assumed: the DFA caps are shared between the three machines and the
    MANDATORY pair is built first and is at least as large, so a corpus
    pattern reaches a cap on the pair before the optional machine can. Census
    at landing over 2,786 corpus patterns: 1,489 vm, 288 refused, **825
    unwrapped**, 180 `search-filter`(attempt), 4 `search-filter`(empty), **0
    `search-filter`(overflow)**. That is why the arm gets a lowered-cap
    reference build rather than a corpus witness, and why §5's ceiling on it
    is pinned at 0 — a pattern landing there is a red that says the
    assumption expired.
  - **The differential's own first version reported 1,213 FALSE divergences**,
    from one mis-ordered `gen_run` argument, because it collapsed "the driver
    exited nonzero" into "the answers disagree". It classifies the exit code
    now (1 = divergence, 2 = malformed/zero cells, anything else =
    infrastructure) and asserts the infrastructure count is zero: a check that
    cannot tell its own breakage from its subject's is not a check.

**On demand — `make test-frame-buffer`** (`tests/recursion/run_frame_buffer.sh`):

- **the NULL-equivalence spread.** `<prefix>_search_in(..., NULL)` compared
  BYTE FOR BYTE against `<prefix>_search` over 12 patterns chosen to reach
  every ANSWER KIND — match, no-match, capture spans, a zero-width loop, a
  `\K` entry, a backreference, a give-up, the constant-time runaway refusal —
  across both engines. `RXTROUTE=null` is the blunter, broader version of the
  same control and runs over any corpus.
- **the seven capacity sites, exact in BOTH directions, under
  AddressSanitizer.** For each nesting depth the driver allocates EXACTLY the
  capacity design §4's measured per-level ratios say is needed and asserts
  three things: the exact fit MATCHES (so under ASan nothing wrote past either
  region), one frame short gives up, one trail entry short gives up. The
  absence of slack is the point — an off-by-one capacity guard is invisible on
  a generously sized buffer in BOTH directions at once, because too loose
  writes into slack the caller happens to own and too tight never fires. ASan
  is a PREFLIGHT: the section skips loudly to a non-sanitized run, and says so,
  if `$CC` cannot build with it. This is the design's own S-FB6 ASan cell, and
  it covers rather more than that row.
- **spec §10.6's `MAP_NORESERVE` worked example, run.** 2 x 64 MB reserved,
  driven to its ceiling. It is opt-in because it touches ~105 MB of resident
  memory and builds 940 KB subjects; that is a measurement about a
  RESERVATION, and `make test`'s job is the population. It SKIPS LOUDLY (a
  `NOTE:`, never a pass) on a machine that will not give it the reservation.

**And six sabotage rows, S179-S184** (`tests/mech/sabotages/`), under two
registered suite words `framebuffer` and `stackdepth`. Two are worth reading
for what they say about the CELLS: S180 (the two capacities bound to each
other's array) is a NO-OP under any cell that supplies EQUAL capacities, which
is why `framebuffer.rxt` uses `1024,8192`; and S184 (`_RESUME_FRAME_SIZE`
stamped from the wrong struct) does not produce an under-allocated buffer at
run time at all, because the artifact's own `_Static_assert` turns it into a
generated file that does not compile.

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

## `test-rxtsource` — INV-COMPAT ([DD-13b.W1.1], 2026-08-30)

`bash tests/rxtsource/run_rxtsource_tests.sh` (`make test-rxtsource`), added
when the `.rxt` format grew a HEAD: the question it answers is whether
growing the format changed what any EXISTING corpus file means. Cheap on
purpose — three parses of the corpus and **no compiles OF THE CORPUS**
(189 files, 26,799 expectation lines), so it does not compete with
`test-corpus` for the box. Full design and per-check rationale:
`tests/rxtsource/CLAUDE.md`, `docs/design/dd13_format/w1_impl.md` §3.

**[DD-13b.W1.2], 2026-08-31 — IT COMPILES NOW, AND THE HEADLINE ABOVE IS
NARROWED RATHER THAN LEFT TO BE DISCOVERED.** The section gained a W1.2
half that builds a handful of TARGET FIXTURES (single digits: the
three-config file's three targets, a few one-target files, and `run.sh`
building the same three again through the H11 path, which also invokes the
C compiler for their drivers). Building a `.rxt` source cannot be checked
without building one. **The cost is bounded by the FIXTURE count, not by
the corpus**, so it does not grow as the corpus does, and the corpus half
is unchanged — C1, C3, C0a, the arm-block hash pin and the keyword census
still read all 189 files and compile none of them. The measured
section-runtime delta is recorded at the lane's validation
(`docs/dev/lanes/w12_report.md`).

What it asserts, briefly (each against a PINNED census, never a
self-derived one — a pin that recomputed itself would agree with a shrunk
corpus by construction):

- **C1** — the three-way parse differential (`pcrec --list-source`,
  `run.sh --dump`, `verify_rxt.py --dump`), byte for byte over their shared
  projection, plus a FIELD MANIFEST (exact column names, exact per-row
  field count, exact total row count) so the differential cannot silently
  stop comparing a directive both dumps quietly drop.
- **C3** — the oracle re-run: `verify_rxt.py` wired to the WHOLE corpus for
  the first time (previously invoked by nothing in the tree, its default
  discovery covering 40 of 179 files), over a `find`-derived file list with
  a `--min-files` short-list hard fail, and a per-file wall bound
  (`--file-timeout`) with a named, counted allowance (`--allow-timeouts`)
  for the one file known to overrun today.
- **C0a** — that the composer (unbuilt in W1.1) was never invoked, from two
  independent sources (an external call-counting wrapper, and a raw-byte
  census of head-bearing files) that must agree.
- The arm-block hash pin (`run.sh`'s existing 17-arm chain is unchanged
  byte for byte) and the keyword census (no corpus line's first token
  collides with a word the grown grammar wants).
- The HEAD PATH's own fixtures (`tests/rxtsource/fixtures/*.rxtin`,
  described in that directory's own CLAUDE.md) — the corpus has 0
  head-bearing files, so without them every head-grammar check would be
  green while detecting nothing ([MECH-REACH]'s failure).

**The r46 panel's fix lane (w11f) added roughly thirty more fixture-backed
checks to this section**, one per finding in `docs/dev/reviews/
2026-08-30-r46-w11-impl.md` whose population was, like the head path
itself, ZERO on the real corpus — the class of finding was "the three
parsers agree on the corpus and diverge one line outside it" (a control
byte in a pattern, a tab in a `with`/`from` list, `flags`/`engine` values
outside the ruled vocabulary, an empty or `|`-trailing-space description,
a whitespace-only line, a directive before any pattern in a headless
file, a duplicate block name, and more) — see that review and
`tests/rxtsource/fixtures/*.rxtin`'s own headers for the full list. None
of them touch the pinned census or the arm hash; they are ADDITIONAL
fixture-driven checks, in the same section, for the same reason the
original head-path fixtures exist.

**The mech battery gained ELEVEN rows for the `rxtsource` arm at
[DD-13b.W1.1]'s own landing** (`tests/mech/sabotages/S194`-`S203`, ten
live, plus `S204`; two more, `S-C7`/`S-C8`, are DEFERRED until the
composer exists — `tests/rxtsource/CLAUDE.md` states which and why). Each
sabotages one of the mechanisms this section defends (the escape, the
field manifest, the composer-invocation counter, the keyword census, the
oracle's own skip-reason accounting, an unknown line kind's silent
swallow) and is scored through `bash tests/mech/run_sabotage_matrix.sh
S194` (etc.) exactly like every other row in that directory.

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

### The sabotage-row format: PROCESS, not spec ([SPEC-1.10]/F4, 2026-08-30)

`docs/dev/spec_survey.md`'s F4 row flagged the sabotage-row format (mech's
mutation-testing rows: `SAB_ID`, `SAB_FILE`, `SAB_BEFORE`/`SAB_AFTER`,
`SAB_SUITES`, `SAB_EXPECT`, the `[MECH-REACH]` fields above, ...) as
UNSURVEYED and left its spec-vs-process classification open. Read
(`tests/mech/CLAUDE.md`, `tests/mech/sabotages/CLAUDE.md`) and ruled here:
**it stays PROCESS documentation, here and in the two `CLAUDE.md` files
above — never docs/spec/.**

The test here is docs/spec/CLAUDE.md's own charter: spec documents state
how the SHIPPED TOOL works and how to USE it — a contract pcrec makes with
a caller or a contributor writing tests AGAINST that tool's observable
behaviour (which is exactly why `docs/spec/rxt_format.md` moved out of this
file at [SPEC-1.6]: `.rxt` blocks state expectations about what `pcrec`
compiles and what the compiled matcher answers, a caller-facing surface one
level removed). A sabotage row states neither. `SAB_BEFORE`/`SAB_AFTER`
edit **pcrec's own source** to prove a CHECK catches a planted defect —
testing the tests, not the tool — and nothing about that mechanism is
observable from a compiled artifact or a CLI invocation. It is exactly
[F5]'s own precedent one row up in the same survey table (identity gates'
GATE MECHANISM — pin commits, program-region-vs-whole-file — "stays in
docs/testing.md/tests/codegen/CLAUDE.md as DEVDOC/contributor-process, not
spec"): a project-internal QA convention, not a tool surface.

**The format itself is not restated here.** `tests/mech/sabotages/CLAUDE.md`
is the field reference (Required/Optional tables, the `[MECH-REACH]` fields,
closed vocabularies, the numbering convention, and the traps that have
actually been hit); `bash tests/mech/run_sabotage_matrix.sh --help` prints
the driver's own normative field list, which is authoritative over any
prose copy including this one. `tests/mech/CLAUDE.md` is the directory
survey (what each file does, `SAB_EXPECT`'s contract, the suite-name
vocabulary). This file's own `[MECH-REACH]` subsection below restates four
of those fields inline for readers already mid-topic on reach checks — that
restatement is a convenience for THIS narrative, not a second source of
truth, and drifts should be fixed by deleting the copy here in favor of a
pointer, not by editing both.

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

**[SABANCHOR], 2026-08-26: the tripwire ALSO runs as a `make test-codegen`
check now** (`tests/codegen/run_codegen_tests.sh`'s "[SABANCHOR]" block),
not only as a manual command someone has to remember for the tiers above.
It was still ad-hoc when S67/S179/S183 went stale under [OPT-1]/[DD-13c]'s
emitter refactors — a manager battery script outside this tree caught them
at a run's start, not `make test-codegen` — so a stale anchor now fails the
codegen suite in the same run as the change that caused it, while the
tiered policy above still governs when a full row re-run (not just the
tripwire) is owed.

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

### [MECH-REACH] a row whose witness is a construct declares its reach (2026-08-25)

`SAB_EXPECT` (above, and `tests/mech/CLAUDE.md`) made a sabotage row's
OUTCOME a checked contract. Nothing made its PREMISE one, and the gap is not
hypothetical: **S70's four witnesses expired BY BEING IMPLEMENTED.** They were
`reject_gated assertions` rows probing `\b`, `\B`, `\G` and `\K`, retired one
per wave through [M6.2] as module `assertions` built those constructs; after
[M6.5.2] retired the last pin on that arm, not one row in the tree still
reached the site S70 deletes. The row scored for two milestones and certified
nothing. The expired-claim doctrine watches `UNDETECTED → DETECTED` only, so
this direction had no checker.

**Four optional fields on a sabotage definition, and a third verdict.**

| field | asks |
|---|---|
| `SAB_REACH` + `SAB_REACH_EXPECT` | does the WITNESS still reach the SITE? A command run on a CLEAN reference tree BEFORE the sabotage; one required literal substring per line, all of which must appear in its stdout+stderr. `$PCREC` is the clean binary, `$TREE` its root, `$REACH_TMP` its cwd |
| `SAB_REACH_POP` | is the POPULATION still there? `FILE\|EREGEX\|MIN` lines. **The count is printed on every run**, green or red |
| `SAB_REQUIRE` | can this RUN measure at all? Closed vocabulary (`asan`). Unsatisfiable ⇒ ANOMALY |
| `SAB_EXPECT=UNREACHED` + `SAB_EXPECT_REASON` | a row that DECLARES its witness dead, and is told (`NOW REACHED`) when it comes back |

A failing reach check is the verdict **`UNREACHED`**: RED in the headline,
counted in the completion trailer beside `undetected` and `anomalies`, and the
sabotaged tree is **not built or run** — the verdict is already known.

    == mech run COMPLETE: N rows (unexpected: X, undetected: U, unreached: R,
       anomalies: A, oracle-skipped: S) at <SHA> ==

`bash tests/mech/run_sabotage_matrix.sh --help` prints the full field list.
`tests/mech/sabotages/CLAUDE.md` carries the conventions and the traps.

**Cost:** one extra `git archive` + `make all` per RUN (not per row), built
lazily and only when a selected row declares a reach field, against a matrix
that measures in the tens of minutes. Rows read the clean tree but never write
to it — a probe's cwd is its own scratch dir, so `-o out.c` cannot land in the
shared tree.

**Checking definitions without running them:** `VALIDATE_ONLY=1 bash
tests/mech/run_sabotage_matrix.sh` sources every definition, runs the same
field validations, and stops — seconds instead of the up-to-eighty-minute wait
for the row to come round. It prints `== mech FIELD VALIDATION COMPLETE: N
definition(s) valid, 0 rows measured ==` and deliberately NOT the
`== mech run COMPLETE` trailer, so a watcher polling for a finished matrix can
never be answered by a run that measured nothing. Measured 2026-08-25: 180
valid. Four planted malformed fields each produce a named `FATAL` and exit 2.

**Validated three ways, each plant made and removed** (2026-08-25):

| plant | row | measured |
|---|---|---|
| an EXPIRED witness (a `SAB_REACH_EXPECT` no clean tree produces) | S34 | `reach:MISSING(1/1)` → `UNREACHED … ***UNEXPECTED***`, `unreached: 1`, exit 1 |
| a POPULATION FLOOR above the file's count (20 → 999) | S110 | `pop:tests/backrefs/octal_class.rxt:/^(m\|n) /=29(want>=999)` → `UNREACHED`, exit 1 |
| `SAB_REQUIRE=asan` under a `cc` wrapper refusing `-fsanitize=` | S155 | `require:asan-UNAVAILABLE` → `ANOMALY`, `undetected: 0, anomalies: 1` |

The third plant's FIRST run found a defect in the mechanism's own prose: the
ANOMALY sentence contained the word `UNDETECTED`, and the headline's
`undetected` count is a `grep -c` over the row text — so the verdict counted
itself and printed `undetected: 1` for a row that was never measured. Reworded
and re-run at `undetected: 0`. A control sharing a source with its subject,
this time the subject being the control's own wording.

**Twenty-one rows carry reach fields today** (S15-S20, S27-S35, S70, S110,
S111, S119, S155, S172): every row whose detector is a diagnostic string, the
three dump-driven rows, the class-port row, and the two the mechanism was built
for. All 21 witnesses were verified live against the clean binary before
landing. The remaining rows declare none, deliberately — a reach field is worth
writing where the detector is a witness that CAN retire, and a row whose
detector is a byte-identity gate or a whole differential population has no
single witness to name.

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

### CLANGGEN — a second COMPILEE toolchain, riding the same compile pass ([CC-CLANG], 2026-08-31)

`make test CLANGGEN=1` is `LINTGEN`'s exact shape, one compiler over: rather
than a separate clang-only pass over generated code, it defaults the SAME
generated-matcher compile every test suite already runs through to `clang`
instead of `gcc`, in the same `GENCFLAGS` compile pass `LINTGEN` rides.
`CLANGGEN` is `?= 0` and `export`ed from the Makefile; `tests/harness/run.sh`,
`tests/cli/run_cli_tests.sh`, `tests/codegen/run_codegen_tests.sh`, and
`tests/registry/run_pc4.sh` each read it themselves (the same four scripts
`LINTGEN` rides) and default their own `CC` to `clang` — **only when the
caller left `CC` unset**: an explicit `CC=` on the command line always wins,
which is the one precedence rule `LINTGEN` never needed (it only ever
APPENDS to `GENCFLAGS`, never overrides an axis someone else chose). Unset
(default), the four scripts compute `CC=gcc` exactly as before; `make test`
is unaffected, and nothing is written to `build/` — this axis never rebuilds
`pcrec` itself, which stays gcc-built (D2). `pcrec` the compiler and `clang`
the compilee toolchain are deliberately independent knobs: `make test
CLANGGEN=1` builds `build/pcrec` with `gcc` as always and points every
generated-matcher compile at `clang`; `make CC=clang` (below) is the
SEPARATE, one-time survey of building pcrec's own SOURCES under clang, and
the two are not meant to be combined casually.

**Why this is the right place for it and not a new script.** [CC-CLANG]'s
probe (docs/dev/plan.md) found gcc and clang agreeing cell-for-cell on every
artifact shape it tried apart from one structural incompatibility (a
frameless VM artifact's indirect-goto dispatch, fixed by [CC-CLANG] step 1 —
see `src/gen/emit_vm.c`'s `has_push` comment) and one cosmetic warning
(`noclone`, now `__has_attribute`-guarded). The remaining question is
breadth: does clang accept EVERY shape the corpus produces, not just the
four hand-probed ones — exactly the question `LINTGEN` asks of `-fanalyzer`,
answered the same way, by riding the compile pass every suite already runs
rather than building a parallel one.

**One known interaction, named rather than special-cased around.** The K24
partial-inlining check in `tests/codegen/run_codegen_tests.sh` (search "K24
noclone control") asserts that gcc's OWN partial-inlining pass clones a
function once `noclone` is stripped from it — a claim with no clang
analogue, since clang performs no such pass at all. That one check is
expected to behave differently under `CLANGGEN=1`, not incorrectly; it is
not a finding about the mechanism, and no attempt was made to make that
specific check compiler-agnostic (D18: gold-plate under measurement, not
ahead of it).

**Findings surface the same way `LINTGEN`'s do**: `harness`/`cli`/`codegen`'s
default `GENCFLAGS` already carries `-Werror`, so a clang diagnostic on
generated code is a hard compile failure exactly like any other warning on
that path, with no new machinery. `run_pc4.sh`'s `-O0 -std=gnu11` default
carries neither `-Wall` nor `-Werror` (unaffected by this flag, same as
under `LINTGEN`) — a caller who wants clang WARNINGS to fail loudly there
needs `GENCFLAGS` set explicitly, same as today.

**A ONE-TIME `make CC=clang` survey of the COMPILER itself** (pcrec's own
`src/`, `cli/`, `lib/` sources, gcc-dialect per D2) is a separate, narrower
question from the sweep above: not "does clang accept every generated
artifact" but "does clang accept pcrec's OWN source". Findings from that
one-time run are recorded in the lane report rather than wired into any
`make` target — D2 keeps gcc the target compiler, so this is a survey, not
a standing axis.

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

**EVERY OTHER SCRIPT'S OWN INVOCATION WAS STILL BARE, UNTIL K37
(2026-08-25).** The paragraph above closed the gap for `tests/harness/run.sh`
alone; `docs/dev/known_issues.md` K37 is the finding that nothing else in the
tree was covered — `tests/recursion/run_recursion_diff.sh` called `build/pcrec`
with no bound at all, and sabotage row S159's non-terminating compiler turned
that into a 50-minute hang that took a `make mech` matrix's evidence down with
it. `pcrec_run` (`tests/lib/gen_timeout.sh`) is the ONE helper every harness
script now routes a compiler invocation through — a bash function rather than a
bare `"$TIMEOUT_BIN"`/`scripts/watchdog` call at each site, because K37's sweep
touched ~360 call sites across 55+ scripts and a shared function is what let
that be mechanical rather than error-prone. TWO PATHS, MEASURED rather than
assumed: `pcrec_run <argv...>` defaults to `"$TIMEOUT_BIN" "$(pcrec_timeout_secs)"
<argv...>` (the same cheap wall-only wrap the paragraph above already used) and
routes through `scripts/watchdog` instead — wall + tree-RSS + CPU + a
`build/watchdog.log` line — only when the pattern (the invocation's last
argument, pcrec's own `--` convention) is CALL-BEARING (`(?R)`, `(?0)`, `(?N)`,
`(?±N)`, `(?&name)`, `(?P>name)`, `\g<...>`, `\g'...'` — S159's own construct
family) or the caller passes `--hostile` explicitly. MEASURED 2026-08-25: 50
calls each of `scripts/watchdog -s 20 -- true` vs `"$TIMEOUT_BIN" 20 true` — 8.55s
vs 0.127s, ~171ms/call against ~2.5ms/call, a ~68x multiplier — so routing
every one of the ~360 sites through watchdog unconditionally would multiply the
harness's own wall time rather than merely bound it, the identical tradeoff
`gen_run`'s cheap-shape/watchdog split above already documents for its own
high-count inner loops. `pcrec_run`'s own comment in `tests/lib/gen_timeout.sh`
carries the full measurement and the construct list. A structural check
(`tests/codegen/run_codegen_tests.sh`, "[K37] THE BARE-COMPILER-CALL GUARD IS
STRUCTURAL") sweeps `tests/**/*.sh` for a compiler token used bare — every
non-invocation match (a diagnostic echo, an env-var prefix onto a
self-recursive or python worker invocation, an argument two positions past the
command word) is a reasoned, non-vacuity-checked allowlist entry, exactly K35's
own shape one directory over — so a NEW bare call site cannot recur silently
the way `run_recursion_diff.sh`'s did. **NOT COVERED, and recorded rather than
silently widened into K37's fix**: `registry/compliance_section.py` and
`vm/vm_oracle.py` both call the compiler via python's `subprocess.run()` with
NO `timeout=` at all (`recursion/run_lookbehind_call_sweep.py`'s
`pcrec_compile()` likewise) — the identical hazard class, one level down, and
outside a textual sweep over bash source. `tests/fuzz/fuzz.py`, by contrast,
already carries `PCREC_TIMEOUT` on every one of its own compiler calls.

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

  **THE EXCLUSION IS BY DIRECTORY, WHICH IS WHY IT COVERS MORE THAN ONE
  TARGET** (verified against the Makefile at the [DD-14] close, 2026-08-25):
  neither `ubsan:`, `asan:` nor `san:` names ANY script under `tests/thread/`,
  so `tests/thread/run_stackdepth_tests.sh` — the [TS-4]/[DD-14.FB] emitted-
  matcher-on-a-128 KB-stack suite behind `make test-stackdepth` — is excluded
  by the same structural rule and for the same TSan reason, without needing a
  line of its own. Read the exclusion as "the directory", not "the one script
  that existed when this paragraph was written".
- **`tests/recursion/run_frame_buffer.sh`** (`make test-frame-buffer`) —
  OPT-IN, and in NO sanitizer suite list (verified 2026-08-25). It is not an
  omission: the script BUILDS ITS OWN drivers under
  `-fsanitize=address,undefined` (§2's exact-fit driver is the instrument, and
  `REQUIRE_ASAN=1` makes a missing sanitizer an ANOMALY rather than a pass —
  see sabotage row S155), so re-running it inside `make san` would instrument
  an already-instrumented build to prove nothing new. It rides `make
  test-frame-buffer` and `make mech`'s `framebuffer` arm instead.
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

### The suite list is ONE manifest, not three copies ([TT-9], 2026-08-25)

`ubsan`/`asan`/`san` used to each carry their own hand-written
`for s in tests/... ; do` list in the Makefile — the SAME list, copy-pasted
three times, which is exactly how they drifted: wave B+C's first patch
added `tests/recursion/run_recursion_diff.sh` to `ubsan`'s copy only, and
`san` (added later by copying `asan`, itself copied from `ubsan` before
that patch landed) never ran it — nobody's `make san` instrumented that
script until an unrelated later edit happened to reconcile the copies.

`tests/lib/san_scripts.txt` is now the ONE list all three targets read
(`SAN_SCRIPTS := $(shell grep -vE '^[[:space:]]*(#|$) ' tests/lib/
san_scripts.txt)` in the Makefile, `for s in $(SAN_SCRIPTS); do ... done` in
each target) — a plain manifest file rather than a Makefile-only variable,
because `tests/codegen/run_codegen_tests.sh`'s "[TT-9] THE SANITIZER SUITE
LIST IS STRUCTURAL" check needs to read the identical list from bash
without parsing Makefile syntax (same shape as [SR-11]'s
`table_contract.md` manifest and `mlscan.py`'s self-contained rule table:
one file, two readers, never a transcription). That check sweeps every
`tests/*/run_*_diff.sh` in the tree and requires each to be IN the manifest
or in a reasoned exclusion — there is no exclusion list today because the
sweep found none of the tree's 9 `run_*_diff.sh` scripts belongs in one;
if a future differential script is deliberately NOT a sanitizer-axis
candidate (no generated-code compile of its own, the way
`run_atomic_identity.sh`'s TEXT-only comparison above has none), it needs
a stated reason there, not a silent gap.

**FIVE SCRIPTS WERE MISSING WITH NO STATED REASON, found by enumerating
every `run_*_diff.sh` and diffing against the three (byte-identical, as of
this measurement) lists**: `tests/lookaround/run_lookaround_diff.sh` and
`tests/lookaround/run_expansion_diff.sh` (the ruling's own named example),
plus `tests/assertions/run_gstart_diff.sh`, `run_kreset_diff.sh` and
`run_mline_diff.sh`, which the same enumeration surfaced. All five compile
generated C under `GENCFLAGS`/`$CC` exactly like their already-listed
sibling scripts, so there was no reason to exclude them — added to the
manifest rather than recorded as an exception. Verified with `make -n
ubsan|asan|san` (the sanitizer suites themselves were not run): all three
targets' `for s in ...` line now expands to the identical 33-script list
read from the manifest.

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

**`battery_v5` ([TT-12] STEP 2, Frank's ruling 2026-09-03, "2 yes"):**
`test-axes` joins the chain as its own stage, between `strict` and `san`
— `test → strict → axes → san → lint → mech`. Landed as `scripts/battery.sh`
([TT-12] STEP 1 item 5): every stage besides `axes` itself also picked up a
STEP 1 measurement over the manager's prior ad-hoc `battery_v4.sh` — the
test stage runs at `-j4 PROCS=3` (item 4's K44 table, below), `san` runs
its 34-script loop through a `SAN_PROCS`-wide job pool (item 3, above), and
`mech` runs at `PROCS=6` ([TT-8]'s own measured setting, which
`battery_v4.sh` was contradicting at `PROCS=4`). Runs detached under
`setsid` with per-stage logs and a trailer the caller polls; see
`scripts/CLAUDE.md`'s `battery.sh` entry. The first full end-to-end run is
owed at the next merge/close battery — not performed by the STEP 1 lane.

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

### [TT-12] STEP 1 item 3 (2026-09-03) — `san`'s 34-script loop runs through a bounded job pool

`docs/dev/tt12_step0_profile.md` §2: `san` (and `ubsan`/`asan`) ran its
34-script suite list STRICTLY SERIALLY at ~1.9 of 12 cores busy through the
whole 109.6-minute stage — 18.5 idle core-hours, the single biggest number
in the STEP 0 profile — because only 4 of the 34 scripts
(`tests/harness/run.sh`, `tests/reject/run_reject_tests.sh`,
`tests/lookaround/run_expansion_diff.sh`, `tests/anchored/run_anchored_diff.sh`)
read `PROCS` themselves; the other 30, including all five whole-corpus
identity scripts, are structurally single-process.

`tests/lib/run_san_group.sh` (new) replaces the Makefile's bare serial loop
with a bounded job pool (`SAN_PROCS`, default 4), reusing `PROCS` = the
outer `-j` shape's own ceiling (`ceil(nproc/SAN_PROCS)`) for the four
PROCS-aware scripts — [TT-8]'s own mech fix (`INNER_PROCS = ncpu/PROCS`)
applied to the identical shape, since running those four concurrently with
pool siblings at their old `PROCS=nproc` would double-stack exactly the
K44 way. See `tests/lib/CLAUDE.md`'s `run_san_group.sh` entry for the
mechanism (buffered per-script output replayed in argument order, a
lost/crashed worker scored a HARD FAILURE, why this is a new script rather
than `tests/lib/run_group.sh`'s own GROUP_PROCS).

**D77 pre-measurement** (the trigger STEP 0 named before wiring anything):
the five whole-corpus identity scripts, sequential vs `-P4`, same tree,
box load 1.4-4 through the run (quiet-ish). **Sequential: 831s. Concurrent:
351s — a 2.37x speedup.** No shared-resource contention: every script's own
wall time was flat to slightly FASTER concurrently (each isolates itself
with its own `mktemp -d` and only ever reads `$PCREC`), and every script's
verdict tail was byte-identical between the two runs. Clears the D77
trigger.

**NOT run**: a full `make san` end to end under the new wiring (45-50 min
at the measured shape) — owed at the next merge/close battery alongside
`scripts/battery.sh`'s own first full run.

## The load guard ([TT-10], 2026-08-25) — a THIRD outcome for CPU-bounded checks under contention

`tests/lib/load_guard.sh` is D45's CPU-primary budgets' own answer to a
finding D45 did not anticipate: CPU-TIME ACCOUNTING ITSELF inflates under
real contention (memory-subsystem thrash, reduced instructions-per-cycle
under SMT/cache pressure), not merely wall stretching around fixed work.
`tests/resource`'s 45s compile-CPU cap (`K7_CPU`, already wired through
`scripts/watchdog -c` — CPU summed across the process tree, not wall) still
went RED under real load: on a box at load average 31 on 12 cores (ratio
2.58), the cap failed at a MEASURED 53s of CPU, and the A/B control (the
box's own reference build) crossed it too, 53s vs 49s (K31 addendum,
`docs/dev/plan.md` [TT-10] row). `tests/counterk`'s `((a)|ab){4000}c` cell
(K32) lost 28-29 dependent cases to the shared corpus harness's wall
backstop the same night. Both cells are green solo every time.

**The guard is not a bigger cap** — D45's budgets (`K7_CPU`, `GENCPU`,
`GENTIMEOUT`, ...) are unchanged by it and are not the thing to retune here.
It is a pre-flight reading: `load_guard_tripped` compares the 1-MINUTE load
average divided by `nproc` against `LOAD_GUARD_RATIO` (default **2.0**).
Justified from the two numbers above rather than picked: ratio 1.0 is one
concurrent `-j<nproc>` build, the contention level this project's own
"CPU inflation tops out near 2x" figure was measured at and which every CPU
budget already prices into its own headroom (the resource cap carries ~2.9x
over its 15.4s quiet baseline); ratio 2.58 is the K31 addendum's own
MEASURED failure point, where that headroom still was not enough. 2.0 sits
strictly between the two — high enough that this project's own ordinary
concurrent work never trips it, low enough to fire before the exact
contention level the addendum measured actually breaking a cap.

**Where it is wired.** `tests/resource/run_resource_tests.sh`'s section-1
loop and `tests/counterk/run_counterk_tests.sh`'s new K32 compile-cost pin
(mirroring `tests/resource`'s own shape, since a `.rxt` cell cannot assert
what a compile COSTS) both source it. When a cell's `scripts/watchdog` call
returns 123 (CPU exceeded) or 124 (wall exceeded), the guard is checked
*at that point* — a box that was fine when the loop started and got
contended by the time this cell ran must not be read as quiet — and only
those two outcomes are ever reclassified: every other outcome (0, 1, 122,
134, 137) keeps its full meaning regardless of load, since none of them can
be produced by CPU-time inflation. A tripped guard reports **INCONCLUSIVE**
— a THIRD outcome, counted and printed separately from PASS/FAIL, never
folded into either (an inconclusive run misreported as PASS would validate
nothing; misreported as FAIL would misattribute box contention to a
regression).

**Validated (2026-08-25, srLoad lane).** Solo, both suites are unaffected —
`tests/resource` 19/0/0, `tests/counterk` 24/0/0 (23 pre-existing + the new
K32 pin), identical to their pre-[TT-10] counts. Under an 8-way artificial
`yes`-spinner load (backgrounded, killed afterward with `scripts/safekill`;
1-min-load/nproc ratio never crossed the 2.0 threshold on this box's
concurrent-lane mix) both suites stayed fully green, 0 INCONCLUSIVE. The
guard's two directions were confirmed by forcing a CPU-cap breach directly
(`K7_CPU=0`/`K32_CPU=0`): at a real load ratio of 2.47 (a 24-way spinner
load) the forced breach was correctly reported INCONCLUSIVE; the identical
forced breach at a quiet-box ratio of 1.18 correctly reported a real FAIL —
confirming the guard discriminates by load rather than always passing or
always failing.

**tests/counterk's K32 pin is independent of the shared corpus harness.**
`counterk.rxt`'s own `((a)|ab){4000}c` block still rides
`tests/lib/gen_timeout.sh`'s D45 budget exactly as before — D45's budgets
are not touched by [TT-10] — and can in principle still lose dependent
cases to that shared wall backstop under the same load the K31 addendum
measured; the box-concurrency rule (one heavy suite at a time) is that
failure's real mitigation. `run_counterk_tests.sh`'s new pin is a SECOND,
purpose-built, load-guarded instrument for the same compile-cost pathology
(K32), not a replacement for the .rxt cell's own oracle-verified answers.

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
emitter lands and starts delivering per-group offsets. This section is the
design/history record of that landing — the `g`/`gp` line syntax itself now
lives in `docs/spec/rxt_format.md` ([SPEC-1.6]) — and the seed corpus at
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

### `g` vs `gp`, and the python oracle tier: moved

**Moved to `docs/spec/rxt_format.md`** ([SPEC-1.6], 2026-08-25): the
live-vs-pending-VM distinction, the population-accounting rule (an
out-of-range `g` is a hard failure, an out-of-range `gp` is counted
separately and self-activates once `RX_NCAPS` grows to cover it), the
`RX_UNSET` symmetry rule, and how `verify_rxt.py` checks `g`/`gp`
identically are all contract statements a `.rxt` author needs — see that
document's ".rxt format" section (the `g`/`gp` bullet) and "Oracle
verification".

**The oracle rule governing this tier is the three-way rule from
engine_m4.md §3.6 (R21 E-ASK-1/D44)**, unchanged since this landing: python
and libpcre2 are BOTH checked once the libpcre2 differential exists
([M4.7]); there is no pre-built exclusion mechanism, and a case where pcrec
disagrees with both oracles is a bug, never a silent exclusion. This tier
is the python half of that rule, staged first per D4's discipline — the
same staging the base tier already used. (Kept here rather than moved: it
is a design-rationale statement, not a contract clause.)

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

Directory tree row (`docs/spec/rxt_format.md`'s "Organizing tests by
component") needed no change — `captures/` was always the planned home for
this corpus; this landing is what actually populates it.

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

## The axis registry check ([CHK-2] piece 1, 2026-08-28)

`tests/registry/axes_registry_check.sh`, run from `tests/registry/
run_registry_tests.sh` and therefore part of `make test`'s `test-registry`
section (unlike the two opt-in instruments below, which are `make
test-axes` only). Reads `pcrec --list-axes`'s TSV — the optimization-axis
registry's FOURTH surface, `docs/spec/registry.md` §6 — against
`docs/spec/tuning.md` §2 (every documented `(bit N)` heading),
`cli/main.c`'s flag parser and `docs/spec/match_api.md` §6.3 (the D46
stamp family's own home — see DIRECTION 3 below), in BOTH directions:
every dumped deny/force bit checked against `lib/pcrec.h`'s own
definition, its CLI spelling where it has one, and `tuning.md`'s own
documentation of that bit; then the reverse sweep, every bit `tuning.md`
documents and every `PCREC_NO_*`/`PCREC_FORCE_*` bit `lib/pcrec.h`
defines in the family's own 4-15 range confirmed present SOMEWHERE in
the dump — catching an axis quietly dropped from `--list-axes` rather
than only one wrongly added. Every discrepancy named by name
(`docs/dev/learnings.md` §3), never a bare count; the wiring script's own
coverage guard pins the total PASS count exactly (53, `registry_check.c`/
PC-3's own exact-count-guard shape).

**DIRECTION 3 (added 2026-08-28, manager review): the STAMP-VALUE half of
the charter's direction (a)** — "every dumped row has its tuning.md §2.N,
its §6.3 VALUE and its CLI flag, every spec value appears in the dump".
The first revision covered bits/flags/headings and skipped the VALUE
half; this direction closes it, both ways, for every stamp macro with a
non-empty dumped value: `RX_DFA_TABLE` and `RX_DFA_PREFILTER` against
`match_api.md` §6.3's own markdown value-set tables, `RX_VM_PREFILTER`
and `RX_ENGINE` against its prose/code-block string-literal pairs, and
the nine D46 bit constants (`PCREC_VM_RUNG_*`/`_STRAT_*`/`_PRUNE_*`)
against `src/gen/emit_dfa.c`'s own literal `#define` block — NOT
`lib/pcrec.h`, which does not declare them at all (§6.3's own `[ABI-NS]`
paragraph: they are emitted-ARTIFACT text). Two NAMED, CITED exceptions
to the spec->dump sweep, neither a gap: `RX_DFA_TABLE`'s `"mixed"`/
`"none"` are artifact-level compositions of the forward/reverse
machine's own per-machine choice, never a value this dump's per-machine
`table` axis could select on its own; three of the nine bit constants
(`_RUNG_CURSOR`/`_FRAMES_BOUNDED`/`_FRAMES_UNBOUNDED`) have no individual
`-fno-*` deny flag at all (only `-fno-revdet`/`-fno-counter` address a
rung of their own — `src/gen/CLAUDE.md`'s `[ENG-BREP]` rung-ladder
section), so no axis in this dump can ever carry them.

**A real bug caught while WRITING direction 3, not after**: the first
markdown-table extraction ran clean but silently read the WRONG table —
`match_api.md`'s tables sit indented two spaces under their bullet point
(`  | value | meaning |`), and a naive `^\|` row test skips straight past
them to the next UN-indented `|`-starting line, which happened to be a
different macro's table entirely. The extraction looked like it worked
(it printed five plausible-looking values) and was wrong. Caught only by
eyeballing the output against the file by hand before trusting it; fixed
by testing `^[ \t]*\|` instead. Recorded because "some column extracted"
is not evidence "the right column was read", the same lesson the IFS/tab
bug below teaches from the opposite direction (a loud collapse vs. a
silent misread).

**Runtime**: well under a second (`build/pcrec --list-axes` plus a
handful of `grep`/`awk` passes over five small text files — no compile,
no subject sweep).

**Sabotage validation** (2026-08-28, scratchpad only, never committed),
one per direction — three at the check's landing, a fourth from [OPT-K]:
- A scratch copy of `tuning.md` with `-fno-counter`'s `(bit 6)` heading
  deleted, run via `TUNING=<scratch> bash tests/registry/
  axes_registry_check.sh`, fires exactly one named failure —
  `[counter/counter] bit 6 has no '(bit 6)' heading anywhere in
  <scratch>/tuning_sabotaged.md` — with the other checks unaffected.
- A scratch copy of `match_api.md` with `RX_DFA_PREFILTER`'s
  `"memchr-bounded"` table row deleted, run via `MATCHAPI=<scratch> bash
  tests/registry/axes_registry_check.sh`, fires exactly one named
  failure — `[RX_DFA_PREFILTER] dump stamps value 'memchr-bounded' that
  docs/spec/match_api.md §6.3's own value-set table for RX_DFA_PREFILTER
  does not list`.
- A scratch copy of `emit_dfa.c` with the `PCREC_VM_RUNG_REVDET`
  `#define` line deleted, run via `EMITDFA=<scratch> bash
  tests/registry/axes_registry_check.sh`, fires exactly one named
  failure — `[D46 bit constants] dump stamps 'PCREC_VM_RUNG_REVDET' that
  <scratch>'s own emit_rx_abi_types literal block does not define`.
Each sabotage fires exactly one failure, every other check green (52 of
53) — no cascade, no false negatives.

**A FOURTH, ADDED BY [OPT-K] BECAUSE ITS AXIS EXPOSED A BOUND THIS CHECK
COULD NOT SEE PAST** (2026-08-28, scratchpad only, never committed). The
header→dump arm filtered the header's bits to `4..15` before comparing —
the deny/force family's extent on the day it was written — so
`PCREC_NO_OFFSET_SKIP` at bit 16 was dropped before the comparison and that
arm could not report it missing. Fixed to `>= 4` with no upper bound (the
LOW bound is the one doing real work: bits below 4 are unrelated `1u << N`
constants in the same header), and both verdict strings and the section
comment now DERIVE the range from the bit set instead of spelling it.

The sabotage is a `--list-axes` whose `offset-skip` rows are removed by a
wrapper on `$PCREC`, i.e. exactly "an axis landed in the header with no
dump coverage". Baseline 59 of 59 green, with the ok line naming the bit:
*"every PCREC_NO_*/PCREC_FORCE_* bit lib/pcrec.h defines at or above bit 4
(4 5 6 7 8 9 10 11 12 13 14 15 16) appears in --list-axes' output"*.

| bound | result | the header→dump arm |
|---|---|---|
| **fixed (`>= 4`)** | 50 pass / **4 fail** | **FIRES, by name**: *"lib/pcrec.h defines PCREC_NO_*/FORCE_* bit(s) **16** (of bits 4-16 found in the header) that --list-axes names on no row"* |
| pre-fix (`4..15`) | 51 pass / 3 fail | **SILENT** — the arm passes |

**THE HONEST READING, AND IT IS NARROWER THAN "THE CHECK WAS BLIND".** Three
of the four failures fire under BOTH bounds: the `tuning.md`→dump arm and
`match_api.md` §6.3's two value-set arms catch this particular sabotage
anyway. The bound's fix contributes exactly ONE check — and it is the one
that is supposed to be INDEPENDENT OF THE DOCS. An axis added to
`lib/pcrec.h` and to the emitter but never written into `tuning.md` §2 or
§6.3 — the likelier omission, since the doc hunks are what a reviewer asks
for — would have been caught by nothing at all. The arm exists to be the
source-side witness, and a source-side witness with a hand-maintained
ceiling stops being one the first time the ceiling is passed.

**[OPT-K] tripped THREE count-in-prose pins in one change**, which is the
transferable part: this file's own `"its five values are the whole set"`
anchor into `match_api.md` §6.3 (the row gained two values, the sentence
correctly became "seven", and the extractor then found NO table and
reported all seven values undocumented, the four pre-existing ones
included); this check's `/^## 2\. The thirteen axes/` anchor into
`tuning.md`; and `tests/axes/run_axes.sh`'s identical one. All three now
anchor on the part of a sentence a new member does not change, and
`tuning.md`'s §2 heading no longer carries a count at all.

**Found while writing it, not before**: bash's `IFS=$'\t' read` collapses
runs of EMPTY tab-delimited fields — tab is IFS *whitespace* regardless of
what IFS is set to, so a row with several unset deny/force/stamp columns
(most rows have at least one) had every field after the first empty one
shift left, silently reading a later column's value into an earlier
variable. This is the exact gotcha `tests/lib/table.sh`'s own header
comment already names from `tests/reject/`'s history ("never on IFS
whitespace, which is why this is not a bash `read -a` on the raw line");
the fix separates the row-reconstruction step's fields with `\001`
(Ctrl-A, not in bash's whitespace class) before the one `read` loop that
can see an empty field.

**What this dump does NOT prove, and where the independent evidence
lives** (`docs/spec/registry.md` §6 states this in full): the dump shares
its source with the emitter for six of its seventeen axes (`src/gen/
emit_dfa.c`'s own candidate-list arrays), and the eleven predicate axes'
one-line descriptions are hand-authored prose, never a live evaluation.
This check reads the dump against two OTHER files it never opens, which
closes the "control shares a source with what it controls" gap for the
dump's OWN claims about bits/flags/documentation — it does not and cannot
prove that a stamp or a flag behaves as its `applies` text says.
`tests/codegen/run_dfa_stamps.sh` (reads emitted artifacts) and
`docs/spec/tuning.md` §2's own per-axis differentials (compile twice,
compare answers) are that independent side.

## Answer-identity sweep + form census ([CHK-2], 2026-08-26)

Two opt-in instruments, `make test-axes` (`tests/axes/run_axes.sh` +
`tests/codegen/run_form_census.sh`), the same shape as `make strict`/`make
ubsan`: never part of `make test`, never default, writes nothing outside
its own temp dir, safe to run alongside anything else. Chartered from a
gap in the tuning-axis family's own convention (docs/dev/plan.md [CHK-2]):
every axis gets a stamp, a deny flag, an identity gate and a structural
check BY CONVENTION, and before this row only 4 of the 13 documented axes
(`docs/spec/tuning.md` §2) had ANY corpus-wide answer sweep at all.

### The answer-identity sweep (`tests/axes/run_axes.sh`)

Sweeps the WHOLE `.rxt` corpus over every bit-flag axis (12, derived live
from `lib/pcrec.h`'s `1u << N` constants and `cli/main.c`'s flag-parsing
loop — never hand-copied, cross-checked against `tuning.md` §2's own
`(bit N)` headings so a new axis with no doc heading, or vice versa, is
RED) plus the coarse `--engine=vm`/`--engine=dfa` axis, comparing PER-CASE
answers (match/nomatch/span/captures/give-up code) against the default
build — not pass/fail COUNTS, which can agree while the cases that passed
disagree.

**The mechanism**: `tests/harness/run.sh` gained an `RXTDUMP` env var (this
row's own addition, documented in that file's header, threaded through the
`PROCS>1` worker re-invocation the same way `RXTFLAGS`/`RXTROUTE` already
are) — one line per evaluated case, `<file>\t<line>\t<kind>\t<route>\t
<trc>\t<out>`, appended regardless of how the harness's own pass/fail logic
later scores the case, PLUS (since the classification-rule addendum below)
one line per case whose BLOCK failed to COMPILE, with a sentinel
`trc=REFUSED` and `<out>` carrying pcrec's own diagnostic text. Two dumps
(default, one per axis) are compared by `tests/axes/dump_diff.awk`, keyed
by `<file>:<line>` (unique — one `.rxt` case per source line).

### The classification rule (manager's ruling, 2026-08-26)

The FIRST full-corpus run of `make test-axes` FAILED four axes with **zero
genuine answer disagreement** — the comparator had only AGREE and
everything-else, where the axis family's own documented behaviour needs
several distinct, non-failing shapes. `dump_diff.awk` now classifies every
BASE key in order: **AGREE** (identical `trc`/`out`); **REFUSED** (the axis
side is a compile-time refusal — pcrec itself declined the pattern; the
diagnostic text is carried, not merely the fact of absence); **BUDGET**
(the two disagree and EITHER side is a give-up, `trc=3`, or a per-case
timeout, `trc=124` — `tuning.md` §2.5's "identity holds modulo which
budget binds" extended to the harness's own wall timeout: a budget
boundary moving under a denied optimization is not an answer
disagreement); **LOST** (no record at all, not even REFUSED — a
structural gap, always a failure); **MISMATCH** (a genuine answer
difference, always a failure); **GAINED** (a key only the axis produced,
never documented as possible, always a failure).

`run_axes.sh` does the axis-specific half: `REFUSAL_PATTERN` is a per-flag
substring lookup — verified live against the shipped `ctx_fail` text, never
guessed — that decides whether a REFUSED case names THIS axis's own
documented limit (`"would replicate its body"` for `-fno-counter`'s
replication cap; `"-fprefilter requires the VM engine"` for `-fprefilter`'s
force-refusal; `"requires the VM engine"`, the shared phrasing every
`select_engine.c` do-or-die refusal under `--engine=dfa` uses, for the
coarse engine axis). A match is **REFUSED-DOCUMENTED**: a population,
floored (K35, `REFUSAL_FLOOR`) so a change that quietly stops the
mechanism firing is caught, never a failure. **A REFUSED case that does
NOT match — or whose axis has no `REFUSAL_PATTERN` entry — is PROMOTED to
a real failure**, printed loudly as undocumented. This is deliberately not
a blanket per-axis exemption: every bit-flag axis except the force-prefilter
pair is documented as NEVER refusing under the default engine this sweep
uses, so an axis with no entry treats any refusal as worth investigating.

**The four axes the first full-corpus run failed, reclassified:**

| axis | shape | reclassified as |
|---|---|---|
| `-fno-counter` | 228 LOST, all `tests/counterk/counterk.rxt` (the above-replication-cap patterns, `docs/spec/tuning.md` §2.3: "the cap is what refuses it") | REFUSED-DOCUMENTED |
| `-fno-length-prune` | 24 MISMATCH, all axis `trc=124` (the K23 ambiguous-decomposition patterns are intractable without pruning) | BUDGET |
| `-fno-prefilter` | 2 MISMATCH, same `trc=124` shape on the same K23 patterns | BUDGET |
| `-fprefilter` | 13,242 LOST (the documented force-refusal on every DFA-selected pattern) + 2 MISMATCH in `tests/harness/giveup.rxt` (default gives up steps/frames, the forced prefilter answers nomatch) | REFUSED-DOCUMENTED + BUDGET |

Per-axis output line: `agree=N budget-bound=N refused-documented=N
(floor F) lost-other=N mismatches=N gained=N` — every bucket printed
beside the verdict, K35's "populations printed" convention extended from
the census's stamp vocabulary to the sweep's own case buckets.

**The oracle cross-check**: one DFA-side answer-identity axis
(`-fno-premul-table`, bit 15) is additionally run through
`tests/registry/run_pc4.sh` — PC-4, the tree's only LIVE libpcre2
match-semantics differential — via a one-line wrapper that prepends the
flag to every `pcrec` invocation. PC-4's own pattern space is capture-free
(compiles to the pure DFA engine), which is exactly the population
`-fno-premul-table` touches, and its own pinned population (273 patterns,
232 accepted, 62,872 cells) is asserted 0-failure under both the plain and
the denied build — a control whose ground truth is external, so a bug
that broke default AND denied identically (which a default-vs-axis
comparison alone cannot see) would still be caught here.

**Detect demonstration** (docs/dev/learnings.md §3): `premul_val`
(`src/gen/emit_dfa.c:1521`), the identity function on the indexed-table
form `-fno-premul-table` selects, was changed to `st + 1` in a scratch copy
outside this worktree (never `src/`, never committed). Rebuilt, pointed
`run_axes.sh` at the sabotaged binary for the `-fno-premul-table` axis
alone against `tests/base/alternation.rxt`: **22 of 26 cases MISMATCH**,
each named individually (span and capture-slot divergences both), e.g.
line 38: default `match 0 2 0 1`, sabotaged axis `nomatch`. Full transcript
in `run_axes.sh`'s own header.

**Runtime**: 22 full `tests/harness/run.sh` passes (19 bit-flag axes + 2
engine directions + the baseline; [OPT-K] grew the bit-flag family from 12
to 13, and further axes since) at roughly `test-corpus`'s own per-pass
runtime with `PROCS=$(nproc)`. **SEQUENTIAL reference: 4205s (70:05)**,
opt5i's full-corpus run, `docs/dev/tt12_step0_profile.md`'s source data
(2026-09-02, `axes2.log`).

**[TT-12] STEP 1 item 1 (2026-09-03, lane tt12b): axes now run PAIRWISE**
— two at a time, each at `PROCS=ceil(nproc/2)` (see `tests/axes/run_axes.sh`'s
own header and `tests/axes/CLAUDE.md`'s "Pairwise execution" section for the
mechanism). **MEASURED, full corpus + oracle cross-check, same tree: 2868s
(47:48)** — a 1.47x speedup (31.8% off the sequential reference), but ABOVE
the STEP 1 charter's ≤40 min target. The shortfall is load, not the
mechanism: the reference run's own box sat at load 4.5-6 through its
sequential sweep (docs/dev/plan.md [TT-12] row), while the paired run's box
sat at load 12-18 throughout (other daytime work per the day/night
handshake, not a hold on this run) — every pair's own per-axis wall time
landed 25-30% above the reference's solo figure, consistent with contention
rather than the pairing itself. **Answer identity fully verified**: every
one of the 21 axes' AGREE/BUDGET/REFUSED/LOST/MISMATCH/GAINED counts is
BYTE-IDENTICAL to the sequential reference (K45's five axes' `refused_doc`
counts read exactly 2 higher each — the K45 fix landing in the same run,
not a pairing artifact); zero MISMATCH, zero LOST, zero GAINED anywhere.
Pairing THREE at a time was not measured (D77: no trigger for it — two
already meets the "close to additive" bar the STEP 0 profile predicted,
and a third full ~45+ minute run was not spent chasing a stretch target
the charter listed as optional). A re-run on a quiet box would be the
confirming measurement for whether ≤40 min is reachable under normal
conditions; not performed here.

### The form census (`tests/codegen/run_form_census.sh`)

Compiles every corpus pattern twice — default (auto) engine, and
`--engine=vm` forced where accepted, the WIDER population for the VM-only
stamps since auto routes only ~54% of the corpus to the VM — and counts
artifacts per STAMP VALUE for every stamp `docs/spec/match_api.md` §6.3
documents (`RX_ENGINE`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`, `RX_DFA_TABLE`,
`RX_VM_PREFILTER`, the `RX_VM_RUNGS`/`_STRATS`/`_PRUNES` bitmasks read
per-bit, `RX_VM_PRUNE_CEILING`, `RX_ALTCLS_MERGES`/`_FACTORED`), plus the
two joint distributions §6.3 singles out. K35's rule applies to the
vocabulary itself: a FLOOR for every value the corpus reaches (rounded
down generously) and a REQUIRED, BUILT, ASSERTED synthetic witness for
every value with zero corpus population — a value neither reaches is RED.

**Measured this session, 2,772 corpus patterns (floor 2,620), clean run,
135s at `PROCS=4` uncontended (checks passed: 1, re-verified at 120s under PROCS=6 contended by a concurrent battery run):**

Default (auto) engine selection: 995 DFA / 1,488 VM (1,263 hybrid, 225
plain) / 289 refused.

DFA-containing artifacts (995 DFA + 1,263 hybrids = 2,258): `RX_DFA_SCAN`
unanchored 1,882 / attempt 368 / empty 8. `RX_DFA_PREFILTER` memchr 1,152 /
none 644 / byte-class 313 / memchr-bounded 81 / byte-class-bounded 68.
`RX_DFA_TABLE` premultiplied 1,882 / none 376 (= attempt + empty) —
**"indexed" and "mixed" both measure ZERO corpus population**: every
DFA-containing artifact in the corpus is small enough that the
pre-multiplied form wins by default. "mixed" was tuning.md §2.13's own
documented likely-first gap; "indexed" was NOT documented anywhere and is
exactly the kind of gap this census's completeness loop exists to catch
rather than a hand-picked exclusion list. Both are covered by synthetic
witnesses (below).

(RX_DFA_SCAN, RX_DFA_PREFILTER, RX_DFA_TABLE) triples: unanchored/memchr/
premultiplied 1,125; attempt/none/none 341; unanchored/byte-class/
premultiplied 313; unanchored/none/premultiplied 295; unanchored/
memchr-bounded/premultiplied 81; unanchored/byte-class-bounded/
premultiplied 68; attempt/memchr/none 27; empty/none/none 8.

(RX_ENGINE, RX_VM_PREFILTER) pairs: vm,hybrid 1,263; dfa,- 995; vm,none 225.

VM artifacts (default population, 1,488): `RX_VM_PRUNE_CEILING`
prefilter-window 217 / subject-end 224 / **none 1,047** — a third value
this census measured live (§6.3 gives `RX_DFA_PREFILTER` a value-set
table but not this macro; "none" reads as "no MRL clamp applied at all",
`RX_VM_PRUNES` both bits clear). `RX_VM_RUNGS`/`_STRATS`/`_PRUNES` bit
populations printed per bit (see a run's own tally for the current
counts — every bit is set on at least 38 artifacts). `RX_ALTCLS_MERGES`/
`_FACTORED` (pre-engine-selection, so measured on every compiled default
artifact): >0 on 86/87 respectively.

The WIDER `--engine=vm`-forced population (2,484 compiled, 288 refused —
one fewer refusal than the default sweep, an observed fact rather than an
asserted invariant): `RX_VM_PREFILTER` reads "none" on ALL 2,484 — the
direct, corpus-wide confirmation that `--engine=vm` disables the DFA
prefilter (D46/R21 E-6) exactly as documented. `RX_VM_PRUNE_CEILING`
subject-end 574 / none 1,910 (computed) — the OTHER ceiling arithmetic
tuning.md's MRL differential note describes, reached here for free by
forcing the wider population rather than needing a hand-picked cell.

**Synthetic witnesses** (both asserted, both confirmed):
`RX_DFA_TABLE "mixed"` <- `[01]*1[01]{13}` (forward machine 73,728
entries, over the 65,535-entry premultiplication bound; reverse machine
premultiplied — both sides of the bound in one artifact).
`RX_DFA_TABLE "indexed"` <- `(?:[a-z]+)@(?:[a-z]+)` with
`-fno-premul-table` (§2.13's own deny flag forces the indexed form
directly — the corpus-gap witness §2.13 predicts a compiler-axis
controllability lever should be able to reach).

**Detect demonstration**: `dfa_table_name` (`src/gen/emit_dfa.c:2288`),
which returns `"mixed"` when the forward and reverse machines disagree,
was changed in a scratch copy to `return f ? "premultiplied" : "indexed";`
(collapsing "mixed" into whatever the forward machine chose). Rebuilt, ran
the full census against the sabotaged binary: the `"mixed"` witness
pattern (built specifically to produce it) now stamps `"indexed"` instead
(its FORWARD machine is the one over the 65,535-entry bound, so `f` is
false in the sabotaged branch), and the census FAILS TWICE — the witness's
own check, then the completeness loop independently — naming the exact
value and the exact witness pattern: `"mixed" is a form nobody can reach
on this tree`, `checks passed: 0`. Full transcript in
`run_form_census.sh`'s own header.

**Runtime**: 135s at `PROCS=4` uncontended, 120s at `PROCS=6` contended (2,772 patterns × 2 engine
requests, compile-only, no `gcc`) — well under the 2-minute
`test-codegen` budget in isolation, but run as part of `make test-axes`
(alongside the answer-identity sweep) rather than folded into
`test-codegen`, since the two share the opt-in/heavy-battery placement
and this keeps `test-codegen` itself at its documented smoke-friendly
runtime.

## `make test`'s completion trailer (2026-08-26, manager finding, journal part 7)

**The bug**: under `make -j12 test`, GNU make's DEFAULT (non-`-k`) behaviour
on a failing prerequisite is to print `Waiting for unfinished jobs....` and
launch NO FURTHER top-level targets. `test:` used to list its 26 sections as
plain prerequisites ([TT-2], "Section composition" above), so when
`test-corpus` failed (the known counterk cell under load) upstream of
`test-premul-table` in scheduling order, `test-premul-table` — LAST in the
list — silently never ran, in two separate battery runs. The
checks-passed/checks-failed COUNT AGGREGATION could not see the absence: a
target that never ran contributes nothing to either side of the sum, which
reads identically to "ran and found nothing to fail" — K35's shape
(docs/dev/learnings.md §3, "populations nobody counts"), applied to
SECTIONS rather than to a corpus.

**The fix, two halves.** (1) `test:`'s recipe now invokes
`$(MAKE) -k TEST_TRAILER_DIR=<dir> $(TEST_SECTIONS)` instead of listing the
sections as its own prerequisites — `-k` keeps launching independent
targets after a failure, and `$(MAKE)` (never a bare `make`) inherits the
PARENT's jobserver automatically, so `make -j$(nproc) test`'s parallelism
is unaffected; plain `make test` is unaffected in ORDER (`-k` only changes
what happens after a failure, never the sequence up to one). (2)
`tests/lib/test_trailer.sh` verifies (1) actually worked, independent of
trusting `-k`'s own behaviour: every section target's recipe
(`Makefile`, all 26 in `TEST_SECTIONS`) touches a marker file
(`$(TEST_TRAILER_DIR)/<name>.ran`) as the FIRST line of its recipe, before
running its real test script — the marker means "make launched this
recipe", regardless of what the recipe's content then did. A section whose
shared `all` prerequisite fails never touches its marker, correctly: if the
build itself is broken, no section legitimately ran, and the trailer
reports that absence too. `test:`'s own exit code still reflects BOTH the
inner `-k` run's failures and the trailer's own verdict.

**Why this shape** (`-k` + an independent marker-based trailer) rather than
either alone: `-k` by itself changes SCHEDULING but nothing then confirms
every section actually reached "launched" — a recipe could still silently
no-op, or (the corpus-sabotage arm below) a SHARED prerequisite could fail
in a way that takes down every section at once without naming which. A
marker-based trailer by itself, with no `-k`, would faithfully report the
original bug (`N/M` short) but not FIX it — `make test` would still
silently skip sections on every contended run. Together: `-k` is the fix,
the trailer is the check that the fix is doing its job, in the same
control/detector shape every other instrument in this tree uses.

**Validated in a scratch toy Makefile** (five fast fake sections, `sec-a`
through `sec-e`, `sec-e` playing `test-premul-table`'s "last in the list"
role; never built inside this worktree, never committed):

1. **The bug, reproduced.** Old prerequisite-based shape, `make -j2
   old-test`, `sec-a` fails immediately:
   ```
   sec-a: FAILING (simulates the known counterk cell under load)
   make: *** [Makefile:26: sec-a] Error 1
   make: *** Waiting for unfinished jobs....
   sec-b: ok
   old-test rc=2
   ```
   `sec-c`, `sec-d`, `sec-e` NEVER RAN — no error, no mention, nothing:
   exactly the manager's finding, reproduced on demand.

2. **The fix, same sabotage.** New `-k`-wrapped shape, `make -j2 test`:
   ```
   sec-a: FAILING (simulates the known counterk cell under load)
   make[1]: *** [Makefile:26: sec-a] Error 1
   sec-b: ok
   sec-c: ok
   sec-d: ok
   sec-e: ok (this is test-premul-table's role -- LAST in the list)

   == make test: completion trailer ==
   sections ran: 5/5
   trailer: every section in TEST_SECTIONS was launched
   make: *** [Makefile:15: test] Error 1
   test rc=2
   ```
   All five sections ran (the trailer independently confirms `5/5`), and
   the overall `test` target still exits non-zero — `sec-a`'s failure is
   not hidden, only no longer able to silently take a later section with
   it.

3. **The trailer's OWN detection**, a genuine "section never ran" case that
   survives even under `-k`: sabotaging the shared `all` prerequisite to
   fail (`all: @echo '...SABOTAGED...'; false`) makes every section's
   prerequisite fail, so NONE of them are "remade" — `-k` correctly does
   not help here, because there is no independent target left to keep
   going with:
   ```
   make[1]: *** [Makefile:8: all] Error 1
   make[1]: Target 'sec-a' not remade because of errors.
   make[1]: Target 'sec-b' not remade because of errors.
   make[1]: Target 'sec-c' not remade because of errors.
   make[1]: Target 'sec-d' not remade because of errors.
   make[1]: Target 'sec-e' not remade because of errors.

   == make test: completion trailer ==
   sections ran: 0/5
   MISSING — make never launched this section's recipe at all (its
     own output, if any exists from a stale prior run, is NOT
     evidence it ran this time):
     - sec-a
     - sec-b
     - sec-c
     - sec-d
     - sec-e
   test rc=2
   ```
   Named every section, by name, rather than merely reporting a shortfall
   count.

## The artifact-size log ([ART-SIZE.1b], 2026-08-28)

Frank's ruling on docs/dev/plan.md's `[ART-SIZE.1b]` row: the zero-cost
size ratchet rides `test-corpus`'s existing compile pass rather than
adding one, and the METRICS LOG is the deliverable ("or log metrics and
examine post-test" — RULED: the log is the deliverable; the only red is a
corpus-level tripwire; per-pattern movement is a `git diff` a reviewer
reads, never a gate). This section is the implementation record: the
recording mechanism, its measured overhead, the log format, the tripwire,
and the sabotage validation.

### Where it rides

`tests/harness/run.sh`'s existing compile site (the `gen_cc` call that
compiles `gen.c`+`driver.c` for every corpus block) is wrapped in bash's
own `time` reserved word rather than re-run: `TIMEFORMAT` is set to a
fixed, parseable shape and its output goes to a private file (gen_cc's own
compiler output is captured internally via a command substitution into
`$GEN_CC_LOG`, so nothing collides on the real stderr `time` writes to —
verified empirically before wiring this in). When `SIZELOG` is set (same
per-worker-path/parent-merge shape `RXTDUMP` already has under
`PROCS>1`), one TSV row is appended per SUCCESSFUL compile: pattern id
(`file:line`), the D46 engine/rungs/prefilter stamps, comment-excluded
size, gcc CPU/wall seconds, and `load1`. `SIZELOG` unset (the default)
means zero rows are computed — a plain run's cost and output are both
unchanged.

### Measured overhead, and why it needed a second pass

The first cut spawned 8 short-lived processes per compile (2x `awk` for
the size scan on `gen.c`+`gen.h` separately, 3x `sed` for the three D46
stamps, 1x `awk` to sum gcc's user+sys CPU time, 1x `cut` to read
`/proc/loadavg`, 1x `grep` to parse `time`'s own TIMEFORMAT line) and cost
**20.4%** of `test-corpus`'s own wall time — MEASURED on `tests/base/*.rxt`
(40 files, 712 successfully-compiled artifacts) at `PROCS=2`:

```
without SIZELOG: wall=75.648s   (cases passed: 3603, cases failed: 0)
with    SIZELOG: wall=91.075s   (size-log rows: 712)
```

Nowhere near "zero cost". Consolidated into `tests/lib/size_count.sh`'s
`size_count_row` — ONE `awk` invocation that reads `gen.c` and `gen.h`
together, folding the comment-exclusion size scan and the three D46 stamp
greps into a single pass (`FNR==1` resets the comment-tracking state per
file; the stamps are only read from the first file, matched by
`FILENAME == FC`) — plus pure-bash arithmetic at the call site for
everything else: `read` sources the `time` output file and
`/proc/loadavg` directly (no `grep`/`cut`), and the CPU-time sum treats
`user`/`sys` (both fixed 3-decimal strings from `TIMEFORMAT`'s `%3U`/
`%3S`) as integer milliseconds by stripping the decimal point (`10#`
forces base-10 so a value like `"0.089"` -> `"0089"` is never misread as
invalid octal) and reformats with `printf -v` — zero subprocesses beyond
the one `awk` call. Re-measured on the identical 712-artifact sample:

```
without SIZELOG: wall=76.752s   (cases passed: 3603, cases failed: 0)
with    SIZELOG: wall=78.125s   (size-log rows: 712)
```

**1.79%** overhead (76.752s -> 78.125s), an ~11x reduction from the naive
cut. This is the number reported as "the two measured wall times" per the
lane brief; it is not literally zero (there is no way to read gcc's own
CPU-time rusage without at least one syscall/utility per compile in a bash
harness), but it is now dominated by the actual gcc compiles themselves
rather than by this instrumentation.

### The size definition, and why a flat scan agrees with the census's depth-aware one

`tests/lib/size_count.sh`'s comment-exclusion rule (a line is `prose` if
it opens a `/* */` block or is a `//` line, tracked as a simple three-state
scanner: outside / in-block-comment / not) is applied VERBATIM by the
`[ART-SIZE]` census's own Python classifier
(`docs/dev/artifact_size_census/census.py`'s `attribute_source()`) at
BOTH its top level and inside every nested function/table scan — with no
depth-dependent variation. That means a flat top-to-bottom scan (this
file's own approach, no brace-depth or function-name tracking needed)
yields the exact same PROSE byte total the census's five-bucket classifier
does. VERIFIED, not assumed:

```
$ python3 -c "... census.attribute_source() on gen.c/gen.h for 'a(b|c)+d' ..."
gen.c total 34809 prose 15226 nonprose 19583
gen.h total 11159 prose 4794  nonprose 6365

$ . tests/lib/size_count.sh; size_count_bytes gen.c gen.h
25948          # == 19583 + 6365, exact agreement
```

A second, corpus-scale spot check against the same census, on the
corpus's own largest witness pattern (`((a)|ab){4000}c`, rxt-00127 in the
census, `tests/counterk/counterk.rxt:1807`), comparing the CENSUS's own
self-contained (`-o -`) compile form against this file's function:

```
$ build/pcrec -p rx --features all -o - -- '((a)|ab){4000}c' > witness.c
$ wc -c witness.c
675595 witness.c
$ . tests/lib/size_count.sh; size_count_bytes witness.c
651412
$ python3 -c "... census.attribute_source() on witness.c ..."
total 675595 prose 24183 nonprose 651412      # exact agreement, again
```

...and against the SPLIT `.c`+`.h` form `tests/harness/run.sh` actually
compiles (the form the log's own `size_bytes` column measures):

```
$ build/pcrec -p rx -o normtest.c -- '((a)|ab){4000}c'   # writes normtest.c + normtest.h
$ wc -c normtest.c normtest.h
664464 normtest.c
 11011 normtest.h
675475 total
$ . tests/lib/size_count.sh; size_count_bytes normtest.c normtest.h
651349
```

651,349 (split form) vs 651,412 (self-contained form) — a 63-byte
difference, consistent with the census's own §6 finding that the two
forms differ only by small ABI-header/`#include` boilerplate spelling
(their witness measured a 494-byte difference on a much larger artifact).
The size DEFINITION agrees exactly; the two compile FORMS differ by a
noise-level amount, as expected.

### The log format

`docs/dev/artifact_size_log.tsv` (`tests/size/run_size_log.sh`'s stable
output — see `tests/size/CLAUDE.md` for the full column description and
why it is deliberately NOT under `docs/measurements/`):

```
# artifact_size_log.tsv (docs/dev/plan.md [ART-SIZE.1b]) commit=<sha> date=<ISO8601 UTC> load1_at_start=<f> rows=<N> harness_args=(full corpus)
# pattern	engine	rungs	prefilter	size_bytes	gcc_cpu_s	gcc_wall_s	load1
<file>:<line>	dfa|vm	0x..|	hybrid|none|	<int>	<float>	<float>	<float>
...
```

### The tripwire and its pins

`tests/size/check_size_tripwire.sh` (run as the tail of `test-corpus`'s recipe inside `make test`; `make test-size` standalone post-test — the first shape, `test-size:
test-corpus` — reads the log `test-corpus`'s own recipe just produced, no
recompile) is the ONE red this row produces: the corpus-level MAX
`size_bytes` and MAX `gcc_cpu_s` anywhere in the log, each pinned with
headroom over the `[ART-SIZE]` census's own numbers (675,555 B source /
6.995 s CPU, docs/dev/artifact_size_census.md §3/§4) — but NOT at those
raw numbers, because this log measures a different compile shape (`-O1`
compile+link with `driver.c`, not an isolated `-O2 -c`):

- `MAX_SIZE_BYTES = 1,400,000` (default; `ARTSIZE_MAX_BYTES` overrides). RULED
  at landing (manager, 2026-08-28) from the lane's proposed 700,000: the first
  baseline's max was 651,344 B, 7 % under that pin — a drift detector, and drift
  is `size_diff`'s job; the tripwire is for BLOWUPS, so it sits at ~2× the
  measured max (a doubling of the corpus's largest artifact is the red). The
  sabotage transcripts below that cite the 700,000 pin were run against it
  (`ARTSIZE_MAX_BYTES=700000` reproduces them); the shipped pin's own sabotage
  is the doctored-log run recorded after them.

  SABOTAGE OF THE SHIPPED PIN (manager, at landing, 2026-08-28 ~21:2x; three
  arms, no recompile): (1) `bash tests/size/check_size_tripwire.sh <file>` →
  `FAIL: … takes no positional arguments … set ARTSIZE_LOG=<file>` rc 2 — the
  guard exists because the manager's FIRST doctored-log run passed the file as
  `$1`, the script silently checked the REAL log and printed OK: a sabotage
  that passes against the wrong input is the worst outcome a check can have;
  (2) `ARTSIZE_LOG=<copy of the baseline with k18_cost_gates.rxt:103's size set
  to 1500000>` → `FAIL: … SIZE TRIPWIRE — 'tests/base/k18_cost_gates.rxt:103'
  is 1500000 bytes (comment-excluded .c+.h source), 1.071x the 1400000-byte
  pin (load1 at measurement: 10.65; log commit f446f1c)` rc 1; (3) the real
  baseline → `OK — 2875 rows (commit f446f1c), worst size 651344 B
  ('tests/counterk/counterk.rxt:1807', pin 1400000), worst gcc CPU 5.462s
  ('tests/base/k18_cost_gates.rxt:103', pin 8.0s)` rc 0.
  `size_bytes` is comment-EXCLUDED while the census's 675,555 B ceiling is
  comment-INCLUDED — comments only ADD bytes, never subtract, so pinning
  at the census's own raw (larger) ceiling is headroom by construction for
  the same worst-case pattern, before the round-number margin on top.
- `MAX_GCC_CPU_S = 8.0s` (default; `ARTSIZE_MAX_CPU_S` overrides). A row
  can only exist in the log for a compile that SUCCEEDED — D45's own
  `gen_cpu_secs` (`tests/lib/gen_timeout.sh`) kills any compile at ~10s of
  CPU before this call site's append ever runs, so `gcc_cpu_s` cannot
  exceed that ceiling for any logged row at all. 8.0s sits with headroom
  over the census's own 6.995s worst case while staying comfortably under
  D45's 10s hard kill.
- `MIN_ROWS_FLOOR = 1500` (default; `ARTSIZE_MIN_ROWS` overrides) — the
  UNPINNED-MAX GUARD's population floor, calibrated against the census's
  own measured 2,488-artifact corpus population with headroom for ordinary
  corpus growth/shrinkage while catching a truncation-style sabotage by a
  wide margin.

All three are D45-style revisit-when pins: raise one only with a fresh
measurement recorded here, never silently. The baseline full-corpus run
this lane took (see below) confirms these sit comfortably above the real
population's own worst case.

### Sabotage validation

**(a) A real, compiled blowup, caught BY NAME with a ratio.** The corpus's
own largest pattern (`((a)|ab){4000}c`, `tests/counterk/counterk.rxt:1807`)
compiled through the harness with a forced larger unroll chunk
(`RXTFLAGS=--unroll=48`, a real accepted value — `--unroll=56` and above
refuse outright at `PCREC_MAX_VM_REPLICATION_PRODUCT`, so 48 is the
largest accepted blowup on this pattern):

```
$ RXTFLAGS='--unroll=48' SIZELOG=raw.tsv PROCS=1 bash tests/harness/run.sh blowup.rxt
size-log rows: 1
$ cat raw.tsv
blowup.rxt:1	vm	0x10	hybrid	713076	0.831	0.830	4.97
```

(default `--unroll` on the same pattern: 664,464 B split-form size,
i.e. this sabotage is a real +7.3% blowup on the artifact itself.)
Assembled into a log with the standard header and run through the
tripwire:

```
$ ARTSIZE_LOG=sabotage_log.tsv ARTSIZE_MIN_ROWS=1 bash tests/size/check_size_tripwire.sh
FAIL: check_size_tripwire.sh: SIZE TRIPWIRE — 'blowup.rxt:1' is 713076
bytes (comment-excluded .c+.h source), 1.019x the 700000-byte pin
(load1 at measurement: 4.97; log commit 615febe)
rc=1
```

Named by pattern, with the ratio, per the brief.

**(b) A truncated log, caught by the unpinned-max guard.** A log whose
header claims 27 rows, truncated to 10 data rows after assembly:

```
$ ARTSIZE_LOG=truncated.tsv ARTSIZE_MIN_ROWS=5 bash tests/size/check_size_tripwire.sh
FAIL: check_size_tripwire.sh: truncated.tsv has 10 data rows but its own
header claims 27 (written by the SAME run that produced the rows) —
TRUNCATED after assembly
rc=1
```

And independently, a log with zero data rows:

```
$ echo "# artifact_size_log.tsv ... rows=0" > empty.tsv
$ ARTSIZE_LOG=empty.tsv bash tests/size/check_size_tripwire.sh
FAIL: check_size_tripwire.sh: empty.tsv has ZERO data rows — a vacuous
log must not read as 'no blowup found'
rc=1
```

**(c) `scripts/size_diff` on real logs.** Self-diff (identical file
against itself — the "trivial emitter-irrelevant change" control, since
nothing at all changed):

```
$ scripts/size_diff assembled.tsv assembled.tsv
(no patterns moved past the size/CPU thresholds)
totals:
  patterns in OLD only (VANISHED): 0
  patterns in NEW only (NEW):      0
  patterns in both, moved:         0 / 27 common
  total size_bytes: OLD=423980 NEW=423980 (+0.00%)
```

A log with one planted extra row shows up correctly as NEW, with the
total delta:

```
$ scripts/size_diff assembled.tsv assembled_plus_planted.tsv
pattern	status	old_size	new_size	size_ratio	old_cpu	new_cpu	cpu_ratio
tests/base/PLANTED.rxt:1	NEW		999999			0.500	
totals:
  patterns in OLD only (VANISHED): 0
  patterns in NEW only (NEW):      1
  patterns in both, moved:         0 / 27 common
  total size_bytes: OLD=423980 NEW=1423979 (+235.86%)
```

The size-definition agreement with the census (the "spot check against
the census's own numbers" the brief asks for) is the byte-exact witness
comparison in "The size definition" section above, rather than a
`size_diff` run — the census's own `census.tsv` is a different schema
(per-artifact facts, not a size-log row) and the meaningful cross-check is
the DEFINITION agreeing on the shared witness pattern, which it does
exactly.

### Baseline

First taken at commit `53588b9` on the quiet box (load1 0.13-0.20/12
cores), `bash tests/size/run_size_log.sh` (no arguments — the full
corpus), `PROCS=12` — and RE-TAKEN at `f446f1c` after that first run
exposed a real bug this section records rather than smooths over: the
no-args (full-corpus) invocation discovers files via `find
"$ROOT_DIR/tests" ...` (absolute paths), so every pattern id in the first
log read as an absolute, worktree-specific path
(`/home/duxevents/pcrec/worktrees/sizeratchet/tests/...`) instead of the
repo-relative `tests/...` a targeted run produces — silently breaking
`scripts/size_diff`'s premise of comparing "the same pattern" the moment a
log is regenerated from a different checkout (a merge to `main`, a
different worktree name). Fixed at the SIZELOG row site
(`${cur_file#$ROOT_DIR/}`, a no-op when the prefix does not already
match, so every existing call shape is unaffected) and the corpus
re-compiled once more to produce the log actually committed. Final run,
`f446f1c`, load1 5.09 at start (this box, not perfectly idle, but the
run's own numbers are unaffected — CPU accounting is load-resilient per
D45, and size is deterministic regardless of load):

```
cases passed: 26659
cases failed: 0
pattern-compile failures (distinct): 0
group cases pending-vm: 0
size-log rows: 2875
parallel: 177 of 177 file workers reported (PROCS=12)
run_size_log.sh: wrote 2875 rows to docs/dev/artifact_size_log.tsv (commit f446f1c)
```

`check_size_tripwire.sh` against that log, with the pin this lane
originally proposed (`MAX_SIZE_BYTES=700,000`):

```
check_size_tripwire.sh: OK — 2875 rows (commit f446f1c), worst size
651344 B ('tests/counterk/counterk.rxt:1807', pin 700000), worst gcc CPU
5.462s ('tests/base/k18_cost_gates.rxt:103', pin 8.0s)
```

(Same population, same worst-size pattern and value, worst-CPU pattern
unchanged and its value within normal run-to-run CPU jitter of the
first run's 5.475s — confirming the id fix did not otherwise change
what the log measures.)

**The size pin was RULED UP at landing** (manager, 2026-08-28, from
Frank — see "The tripwire and its pins" above for the full reasoning and
the manager's own sabotage transcript): 651,344 B against a 700,000 B pin
is only 7% headroom, which makes that pin a DRIFT detector (any ordinary
corpus/emitter change trips it) rather than a BLOWUP detector, and drift
is `scripts/size_diff`'s job, not this tripwire's. `MAX_SIZE_BYTES` is
1,400,000 B (~2x the measured max) in the shipped script; re-running the
identical log against it:

```
check_size_tripwire.sh: OK — 2875 rows (commit f446f1c), worst size
651344 B ('tests/counterk/counterk.rxt:1807', pin 1400000), worst gcc CPU
5.462s ('tests/base/k18_cost_gates.rxt:103', pin 8.0s)
```

No recompile, same log, same worst-size/worst-CPU pattern and value —
only the pin changed. Every number below is read against the SHIPPED
1,400,000 B / 8.0s / 1,500-row pins unless stated otherwise:

- **Row count**: 2,875, self-consistent (header's `rows=2875` == 2,875 data
  rows == `run.sh`'s own printed `size-log rows: 2875`), 91.7% above the
  1,500-row `MIN_ROWS_FLOOR`. Higher than the `[ART-SIZE]` census's 2,488
  compiled population — expected, not a discrepancy: the census DEDUPS
  identical pattern text across the whole corpus (2,758 distinct patterns
  in, 2,488 compiled), while this log counts every `.rxt` BLOCK the harness
  actually compiles, including the same pattern text appearing in more than
  one file/module (the census's own report names several such repeats,
  e.g. the email specimen appearing in both `tests/base/` and its bench
  copy).
- **Size**: worst 651,344 B (`((a)|ab){4000}c`, the census's own largest
  witness) against the shipped 1,400,000 B pin — 46.5% of pin, well over
  2x headroom by design (the pin is a doubling of this very number).
  Matches this lane's own manual measurement of the same pattern's
  split-form size almost exactly (651,349 B, a 5-byte difference from a
  harness `mktemp` working-directory artifact, not from the pattern or the
  definition).
  `size_bytes` is deterministic given an unchanged emitter and pattern, so
  this headroom is not "noise margin" the way the CPU pin's is — it only
  moves on a real emitter or corpus change, which is the ratchet's whole
  point.
- **gcc CPU**: worst 5.462s (`tests/base/k18_cost_gates.rxt:103`, the
  committed `f446f1c` log's number) against the 8.0s pin — 68.3% of pin,
  31.7% headroom. Notably a DIFFERENT pattern
  from the census's own worst-CPU pattern (the nested-repeat family at
  6.995s isolated `-O2 -c`) — expected, since this log's compile shape
  (`-O1`, compile+link with `driver.c`) is a different quantity from the
  census's isolated `-O2 -c`, so which pattern is hardest to compile is not
  guaranteed to match between the two; the row count and the size ceiling
  are the two numbers that transfer across the two shapes, CPU-time
  ranking does not.

The row count and gcc-CPU pins held at their FIRST proposed values with
no adjustment. The size pin was RULED UP explicitly (not silently, and
not to make a failure pass — the lane's proposed 700,000 B pin was
already passing; the ruling moved it because 7% headroom makes a pin a
drift detector rather than a blowup one), with the reasoning and the
manager's own sabotage transcript recorded above under "The tripwire and
its pins". Nothing here was moved to paper over a red result.

## The boxes (calibration record)

Every runtime, budget and pin in this file was calibrated on the box that
measured it; state the box when citing a number (memory: cross-box timings
are never compared).

- **ubuntubudu** (through 2026-09-04, now the bench's machine + pcrec's
  full-suite/battery venue by slot request — see the fifty-third session's
  journal): Ryzen 5 1600, 12 threads, x86_64 Ubuntu, gcc 15.2, GNU
  userland, libpcre2-8-0 **10.46 (the reference oracle)**, GNU timeout at
  /usr/bin/gnutimeout (default `timeout` is uutils). All D45 budgets, the
  load-guard thresholds, K32's compile pin, the battery shapes
  (-j4/PROCS=3 test, PROCS=6 mech, -P4 san, paired axes) are THIS box's
  numbers.
- **The Mac dev box** (from 2026-09-04, [MACPORT]): Apple M1 Max, 10
  cores, arm64, macOS. Real GNU gcc = Homebrew `gcc-16` (bare `gcc` is
  Apple clang; tests/lib/cc_resolve.sh resolves); bare `timeout` IS GNU
  coreutils 9.11 (no `gnutimeout` name; timeout_bin.sh resolves at its
  step 2); `bash` on PATH is Homebrew 5.3.15 — a box DEPENDENCY (Frank's
  install, 2026-09-04); /bin/bash stays 3.2 forever and six formerly
  hardcoded `#!/bin/bash` shebangs were moved to `env bash`; libpcre2 is
  Homebrew **10.48, NOT the reference** — PC-3 reads 119 expected reds
  here (upstream_issues.md U13); `ulimit -v` does not bind, so
  tests/resource Section 2 SKIPS loudly (its CLAUDE.md); no /proc — the
  watchdog/safekill/loadavg darwin arms ([MACPORT], validated 16/16 +
  13/13 on BOTH platforms at the merge). MEASURED 2026-09-04: serial
  `make test-corpus` 1,717.5 s wall for 27,045/0 (old box 64.1 s at
  22,358 cases) — the gap is macOS's ~10x process-spawn cost across
  ~100k per-case execs, NOT compute (user+sys is only 1,067 s of that
  wall; the worst gcc cell needs 1.416 s CPU against the 8.0 s
  Ryzen-sized pin; all 2,962 size-log rows byte-identical to the old
  box's log). Budgets/pins are CEILINGS calibrated on the slower box and
  pass here; quiet-box timing floors stay on ubuntubudu. Frank's rule:
  light/targeted testing locally, never the whole suite — full validation
  goes to ubuntubudu by slot ([TT-15] PARKED is the chartered exit).

### The `sed` binary itself — GNU-only constructs SILENTLY NO-OP on this box

[MACPORT] follow-on, 2026-09-06 (lane k50bnd), and it is the same shape as
"The `timeout` binary itself" one tool over: **this box's `sed` is BSD sed**
(no `--version`, no `gsed` installed), and the failure mode is worse than a
missing feature.

**A GNU-only construct does not fail here. It matches nothing, exits 0, and
passes the text through unchanged.** So a substitution that is the whole point
of a step becomes a no-op, and what surfaces is a downstream symptom several
steps away that names the wrong cause. Two measured instances, both in
`tests/codegen/run_codegen_tests.sh`, both red on this box since the Mac move:

| construct | where | what actually happened |
|---|---|---|
| `\b` (word boundary) | the OS-0b two-engine fixture's `sed 's/\brx_search\b/rx_search_b/g'` | engine B's entry was never renamed, so the fixture carried a DUPLICATE `rx_search` and all three OS-0b checks failed on a compile error |
| `\|` (alternation inside `\(...\)`) | the [K24] de-sugaring's `rx_\(forward\|reverse\)_accepts(...)` rules | the accessor calls were never de-sugared, and the check reported "the sed above has been outrun by an emitter change" when nothing had changed but the sed dialect. The two `_step` rules carry no alternation and DID fire, which is why the residue read as 4 stray calls rather than as an extraction failure |

Verify either directly:

```
$ echo "int rx_search(void)" | sed 's/\brx_search\b/rx_search_b/g'
int rx_search(void)          # unchanged — no error, no diagnostic
```

**THE RULE: spell test-script `sed` portably, never darwin-conditionally** —
the harness runs these on Linux too, so a `case $(uname)` fork would double the
thing under test. `\b` becomes "not followed by an identifier character"
(`rx_search\([^_A-Za-z0-9]\)`, verified byte-identical to GNU `\b` on the real
body before landing); `\|` becomes one rule per alternative, which needs no
`-E` and therefore no re-escaping of the literal parens these patterns are full
of.

**AND THE SAME RUN FOUND A SECOND, INDEPENDENT DARWIN LAYER UNDER THE FIRST.**
`run_codegen_tests.sh` resolved its own `CC` and was the one straggler NOT
sourcing `tests/lib/cc_resolve.sh`, so on a box where bare `gcc` is Apple clang
the **[K24] block — which is GCC-SPECIFIC BY DESIGN** — was being asked of a
compiler with no partial-inlining pass at all. With the shim sourced (before
the script's own defaulting, since `cc_resolve` acts only when `CC` is unset)
the block runs under real GNU gcc and its control fires for the first time on
this box: *"the de-sugared, attribute-stripped control DOES split (1 clone) —
the partial-inlining pass is live."* The file goes **104 passed / 4 failed →
109 passed / 0 failed**; the count rises by five rather than four because
K24's control check is only reachable once the de-sugaring works.

**The generalisable half**: when a check on this box reports that the tree has
drifted, rule out the TOOL before believing it. Both of these named an emitter
change that had not happened.

## The `\p{...}` membership differential (`tests/uprops/`, [M5.0] stage 3, 2026-09-06)

`make test-uprops` (the `byte` arm, **33 s measured**, part of `make test`);
`make test-uprops-utf8` (the whole code-point space, opt-in). Four sections;
`tests/uprops/CLAUDE.md` carries the per-section argument and this entry
carries the process record.

### A whole-space differential that is affordable

The differential compares pcrec's emitted matcher against libpcre2 for every
shipped property over **every code point**, both encodings, and it is a
`make test` section rather than a battery because neither side calls the
matcher per code point. Both build ONE subject that is every code point in
order and do a single FIND-ALL pass, turning 45 x 1,112,064 membership
questions into 45 scans of a 3.3 MB string per side. The first version did
call per code point and was still unfinished after ten minutes **on one
property** — libpcre2 re-validates the whole UTF subject on every resumed
call unless `PCRE2_NO_UTF_CHECK` is passed, which is why that flag is a
correctness-of-the-instrument matter here and not an optimisation.

### The Unicode-version drift policy, and why it is not a skip

**No libpcre2 this project can reach is at pcrec's pinned Unicode version**,
measured 2026-09-06:

| | libpcre2 | Unicode |
|---|---|---|
| Linux reference (`ubuntubudu`) | 10.46 | 16.0.0 — **the pin** |
| Mac, Homebrew (headers, `pkg-config`) | 10.48 | 17.0.0 |
| Mac, what the suite's dlopen shim RESOLVES | **10.42** | **14.0.0** |

The third row is `docs/dev/upstream_issues.md` U15(b) and is a fact about
every dlopen-based oracle in this tree, not about this suite.

So `uprops_compare.py` reads the oracle's Unicode version at run time and
applies EXACT agreement when it matches the pin, and otherwise a stated
budget: every disagreement must be a code point UNASSIGNED on one side or the
other — read from both sides' own `\p{Cn}` line, out of the same sweep, so the
rule is symmetric and consults no version number — or appear in one of two
small NAMED exception lists (`RECLASSIFIED`, per code point;
`PCRE2_SEMANTIC_DRIFT`, per property and bounded INSIDE properties pcrec's own
sweep reports in the same run).

**Deliberately not a skip.** A skipped check certifies nothing, and the value
of stating a budget is that the residue after drift is still checked.
Measured at landing against 10.42/14.0.0: `byte` **14/0 with ZERO code points
attributed to drift**; `utf8` **14/0 with 62,121 attributed and none
unexplained**.

### §4 is why the suite has four sections and not three

The oracle-free invariants (`\P{X}` is the complement of `\p{X}`; `\p{^X}` is
`\P{X}`; `[^\p{X}]` agrees with `\P{X}`; under `-i`, `\p{Lu}`/`\p{Ll}`/`\p{Lt}`
are `\p{L&}` and nothing else moves) hold at every Unicode version, so they
never degrade to a drift budget — and each has a **non-vacuity control that
must DISAGREE**, because a compiler answering one set for everything would
satisfy the agreements alone.

**§4 found a real bug on its first run** that no other instrument here could
have: `[^\p{L}] == \P{L}` went red because `esc_class_value` never advanced
the cursor for a produced `EXT_MEMBERS`, so `[^\p{L}]` excluded `{` and `}`
as well as the letters. Both sides of the MEMBERSHIP differential compile
`\p{L}` at an ATOM, where the bug does not live, and the corpus's `\p` blocks
are atom-position too. The general shape is this tree's own recurring one:
**an agreement check between two engines is blind to a construct's other
POSITION.**

### What lives elsewhere, and why

- **Refusal wordings** — `tests/reject/` (twelve `reject_gated unicode-props`
  rows). A `perr` block asserts only that compilation failed.
- **The name axis over a generated space** — PC-3
  (`tests/registry/pcre2_check.c`). Its CLOSED-gate uprops differential still
  reads green and stopped certifying what its name claims the day a producer
  landed, so stage 3 ADDED `check_gated_uprops_space` rather than rewriting
  it: the closed-gate sweep's refusal taxonomy and offsets do not change when
  the gate opens, and the open gate is the only place the ACCEPTANCE question
  (T1) can be asked.
- **The answers themselves** — `tests/utf8/axis04_p_categories.rxt`, the
  D27-blinded corpus, promoted at this stage.
