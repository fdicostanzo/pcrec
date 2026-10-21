# tests/spec_mod0 — spec-first checks for the ten module-0 invariants

Executable checks for the ten invariants of the module-0 work, written under
D27: **by an author denied `src/`, `docs/`, and the rest of `tests/`**. The
only inputs were the ten invariant statements, the probe programs in
`tests/probes/`, `tests/fuzz/pcre2_abi.h`, and `build/pcrec` as a black box.

That blindness is the point. Tests derived from an implementation inherit the
implementation author's alphabet; these are derived from the promise, so where
the promise and the code disagree, the check fails instead of agreeing.

Not part of `make test`, and it does not run `make`. One entry point:

    bash tests/spec_mod0/run_spec_mod0.sh            # the gate
    bash tests/spec_mod0/run_spec_mod0.sh --oracle-only   # NOT the gate

## Files

- **spec_common.h** — the shared harness: the libpcre2 oracle (via `../fuzz/pcre2_abi.h`), the `--list-syntax` TSV parser, `spec_is_lexical()`, and the population/floor ...
- **floors.txt** — every ratcheting population floor, in one file.
- **class_expectations.inc** — the measured class-position expectation of each of the 44 class-reachable rows plus 22 endpoint-adjacent probes (check04).
- **endpoint_deviations.inc** — the three cells where libpcre2 decides a range endpoint differently from check08's five-step model (check08).
- **run_spec_mod0.sh** — builds and runs everything; dumps the registry and verb tables from a *run* of pcrec, never a committed copy.
- **check01_isolation.sh**, **check06_cursor.sh**, **check09_every_feature_toggles.sh** — the three shell checks.
- **check02 / 03 / 04 / 05 / 07 / 08 / 10** `.c` — the seven C checks for the ten module-0 invariants.
- **check11_modifier_syntax.c**, **check12_modifier_semantics.c** — a SECOND D27 pass (2026-08-12, SR-mod05), scoped to the `modifiers` module (PCRE2's inline option ...
- **spec_pcrec.h** — running the pcrec BINARY as a black box: fork/exec with a timeout, and the four-way verdict classification (ACCEPTED / REFUSED-AS-UNIMPLEMENTED / ...
- **check13_uprop_syntax.c**, **check14_option_runs.c** — a THIRD D27 pass (2026-08-12, MOD-0.8b), scoped to two construct families' RECOGNITION behaviour: `\p{...}` / ...

## Exit status, and why a green run is not available yet

Three per-check outcomes: **PASS** (the comparison ran and agreed), **FAIL**
(something disagreed, or a population fell below its floor), and
**AWAITING-SURFACE** (the oracle half ran and agreed, but the pcrec-side
comparison does not exist yet). The runner exits 0 only when everything
PASSes; an awaited surface exits nonzero on purpose, because a check that
cannot fail must not report a pass.

**As of 2026-08-13, at the [STD1] close (D37: bare default is the named
set `std1` = {classes, modifiers}): 14 pass, 0 fail, 0 awaiting — exit 0.**
check02 is the only check here that invokes `pcrec --count-groups` with no
`--features`, so it measures the bare default directly: of the 102
generated bodies, 4 that use `classes`/`modifiers` constructs now compile
instead of being refused (`capture.pcrec_compared` 1 -> 5, floor raised by
the STD1b lane; `capture.pcrec_refused` 101 -> 97, lowered under manager
review — population conserved at 102, see floors.txt's comment). The
transient 13-pass/1-fail state this paragraph previously recorded existed
only between the lane's measurement and that review, same day. STD1c then
re-armed check09 (per-name `gate.pairs.<name>` floors + set-membership
honesty against the artifact stamp) and check01 (aperture widened to the
9 enabled-set symbols incl. `pcrec_default_features`, discovery floors) —
see those checks' own rows below.

**As of 2026-08-12, after the MOD-0.8b D27 pass: 13 pass, 1 fail, 0 awaiting —
exit 1, and the failure is a real defect, not an awaited surface.**
check14_option_runs fails on one family, and only that family: pcrec accepts a
quantifier after a bare option run (`a(?i)*`) where PCRE2 raises error 109, and
emits a matcher for it. The check is pinned to PCRE2's answer and will pass with
no edit once the producer refuses the form. See "The quantified-option-run
finding" below and check14's own FINDING block.

(Rest of this section: see the history file.)

## Conventions

- Populations print on PASS lines with their floors. Raising a floor is a
  one-line diff in `floors.txt`; lowering one is a claim that the suite should
  compare less and belongs in review with a reason.
- Pins (`*.inc`) fail in **both** directions: a value that moves fails, and a
  pinned exception that stops applying fails as stale.
- Checks compare error **numbers**, never message wording — D26 tiers wording
  out of scope, and the number is what "whose validity PCRE2 decides" turns on.
- Build any check standalone:

      TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
          -o /var/tmp/checkNN tests/spec_mod0/checkNN_*.c -ldl

  `TMPDIR` matters on the project box: `/tmp` is a quota'd tmpfs.

Maintenance: update this file when a check is added, when an awaited surface
lands (move the row in the table and say what it now compares), or when a
measured number above changes.

- Also (one-line entries for these are in the history file): `check02_capture_count.c`, `check03_lexical.c`, `check04_class_position.c`, `check05_digits.c`, `check07_gate_equivalence.c`, `check08_endpoints.c`, `check10_quantifiable.c`.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__spec_mod0.md`.
