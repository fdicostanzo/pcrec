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

## Exit status, and why a green run is not available yet

Three per-check outcomes: **PASS** (the comparison ran and agreed), **FAIL**
(something disagreed, or a population fell below its floor), and
**AWAITING-SURFACE** (the oracle half ran and agreed, but the pcrec-side
comparison does not exist yet). The runner exits 0 only when everything
PASSes; an awaited surface exits nonzero on purpose, because a check that
cannot fail must not report a pass.

**As of 2026-08-11 (MOD-0.1 slice 7): 7 pass, 0 fail, 3 awaiting.** The suite
exits 1, and that is the correct state — three of the ten invariants describe
pcrec surfaces that do not exist yet. Invariant 10's surface LANDED first
(`--list-syntax`'s 14th column, `quantifiable`, values {yes, no, form,
lexical}); invariant 4's followed (the 15th column, `class_expect`, vocabulary
{"err N", "char 0xNN", "set N"}, empty on the 56 group/verb rows); invariant
2's followed that (`pcrec --count-groups [--] PATTERN`, a bare integer on
stdout exit 0, or pcrec's normal refusal diagnostic on stderr exit 1) — all
three checks now compare rather than await. `--oracle-only` exits 0 when the
only non-passes are awaited surfaces; it is for working on the oracle halves
and says so on every run.

## Files

- **spec_common.h** — the shared harness: the libpcre2 oracle (via
  `../fuzz/pcre2_abi.h`), the `--list-syntax` TSV parser, `spec_is_lexical()`,
  and the population/floor machinery. Fails hard when libpcre2 is absent
  rather than skipping — unlike `tests/registry/pcre2_check.c`, which runs
  inside `make test` and must skip loudly. Every invariant here is decided by
  libpcre2, so a missing oracle makes every check vacuous, and this suite is
  not in `make test`, so failing hard costs a stranger nothing.
- **floors.txt** — every ratcheting population floor, in one file. A check
  fails when a bucket drops below its floor AND when it reports a bucket with
  no line here. Unpinned is unchecked.
- **class_expectations.inc** — the measured class-position expectation of each
  of the 44 class-reachable rows plus 22 endpoint-adjacent probes
  (check04). Regenerate with `--emit-pins`; never hand-edit.
- **endpoint_deviations.inc** — the three cells where libpcre2 decides a range
  endpoint differently from check08's five-step model (check08).
- **run_spec_mod0.sh** — builds and runs everything; dumps the registry and
  verb tables from a *run* of pcrec, never a committed copy.
- **check01_isolation.sh**, **check06_cursor.sh**,
  **check09_every_feature_toggles.sh** — the three shell checks.
- **check02 / 03 / 04 / 05 / 07 / 08 / 10** `.c` — the seven C checks.

Each check's own header states its predictor, its oracle, its population, its
sabotage, and (where it applies) the surface it awaits. Read the header before
the code; the reasoning is there, not here.

## The method these follow

From `tests/probes/CLAUDE.md`, binding here: state the predictor BEFORE
running; generate probe sets from the claim's FAILURE DIRECTIONS, not from the
examples that produced the claim; and feed the predictor from the oracle
(libpcre2's own verdicts and introspection), never from the row data under
test.

Two consequences worth stating plainly, because both were paid for during this
work:

**Populations are checked, not just printed.** An empty population is
indistinguishable from a pass — a sweep that compared nothing prints the same
"0 disagreements" as a sweep that compared everything. So every count is
floored, and an unfloored bucket is itself a failure.

**A predictor that survives its first run has probably not been tested.**
check05's clause 3 and check08's endpoint model were both *wrong* when first
written, in ways that read as obviously correct. They were corrected by
measurement, and both corrections are recorded in the file headers rather than
edited away, because the wrong version is the intuitive one and the next
reader will arrive holding it.

## Per-invariant status

| # | Check | Status | Oracle | Awaited pcrec surface |
|---|-------|--------|--------|----------------------|
| 1 | check01_isolation.sh | awaiting | `nm` over `build/libpcrec.a` and `build/obj` — the linker | An enabled-set symbol (none matching `enabled_set\|feature_enabled\|…` exists in the archive), and any TU defining a recogniser or extent scan |
| 2 | check02_capture_count.c | **PASS** (surface landed) | libpcre2 `PCRE2_INFO_CAPTURECOUNT`, cross-checked against the err-115 boundary | — (`pcrec --count-groups -- BODY` is run, no shell involved, for every one of the 102 generated bodies; exit 0 compares its printed count against CAPTURECOUNT — `capture.pcrec_compared`, floor 1 — exit 1 means pcrec refuses the body as an unimplemented construct and is counted, not compared — `capture.pcrec_refused`, floor 101. Today only 1 of the 102 bodies is accepted, because pcrec implements only the base tier and every generator family here exists specifically to probe named groups / lookaround / verbs / callouts / branch-reset / `(?n)` / quote mode — the compared population grows module by module as those land) |
| 3 | check03_lexical.c | **PASS** | libpcre2 binding behaviour over all 100 rows | — |
| 4 | check04_class_position.c | **PASS** (surface landed) | libpcre2 256-byte class censuses | — (the `class_expect` column compares equal to the measured value on all 44 class-reachable rows — `class.expect_compared_cells`, floor 44 — and is verified empty on all 56 group/verb rows — `class.expect_verified_empty_rows`, floor 56) |
| 5 | check05_digits.c | **PASS** | libpcre2 over a digit-run × count grid | — |
| 6 | check06_cursor.sh | awaiting | **none exists** — see below | A way to drive one recogniser with `WANT_RESULT` set and clear and read `cx->pos` before and after |
| 7 | check07_gate_equivalence.c | awaiting | libpcre2 decides membership | A way to vary the enabled feature set (`--features=…`, `PCREC_FEATURES`, or an entry point) |
| 8 | check08_endpoints.c | **PASS** | libpcre2 censuses + an oracle-measured extent scan | — |
| 9 | check09_every_feature_toggles.sh | **PASS** (coverage half) | check07's per-name output vs the registry | Same as 7; the per-name-nonzero assertion arms when `gate.compared_pairs` is floored above 0 |
| 10 | check10_quantifiable.c | **PASS** (surface landed) | libpcre2 `a<syntax>*` verdicts, two form sweeps, and the two LEXICAL discriminators | — (the `quantifiable` column arrived mid-work; it caught two real bugs on arrival, see below) |

**Invariant 6 is the one with no oracle half, and that is not a gap in the
work.** Every other invariant is about what a pattern MEANS, and libpcre2 is
the authority on meaning. The cursor rule is about pcrec's internal
discipline, which libpcre2 cannot arbitrate. Building a libpcre2 sweep there
to have something runnable would be theatre — a check measuring something
adjacent and reporting it as though it covered the claim. What check06 does
today is enumerate the row population the comparison will run over, so that
count stays live, and state exactly what it needs.

## Measured numbers a reader will rely on

All against **libpcre2 10.46 2025-08-27**, registry of **100 rows**, on
2026-08-11. Read them from a run, not from here — the floors are in
`floors.txt` and the checks print every count.

- 100 registry rows: 41 `esc`, 55 `group`, 3 `class-bracket`, 1 `verb`; 44 are
  class-reachable (41 esc + 3 class-bracket), 56 carry no class-position value.
- 50 of 100 rows are quantifiable (`a<syntax>*` compiles).
- **2** rows satisfy invariant 3's binding criterion (D1); **1** more satisfies
  the star-became-a-literal criterion (D2); **3** rows are `lexical` in the
  column, and the two sets agree exactly — see the finding below.
- `quantifiable` column: 46 yes, 38 no, 13 form, 3 lexical. check10 compares 84
  two-valued rows, accepts 13 form-resolved and 3 lexical, and rejects any
  other value.
- D2's witness search cannot reach **4** rows whose quantified form still
  compiles (`(?<=...)`, `(?<*a)`, `(?R)`, `(?0)` — empty languages for
  structural reasons, not a bound that is too small). That is the blind spot
  where a false `yes` could hide, and it is capped by an explicit CEILING in
  check10 rather than a floor, because it is a number that must not GROW.
- 16 distinct module names in the registry.
- 70 of 100 rows have their syntax probe accepted by libpcre2 (check07's
  membership set).
- Verb forms: 50 names → 18 quantifiable, 6 not, **26 undefined** (the
  unquantified form does not compile at all — start-of-pattern-only verbs).
  Counting those 26 as "not quantifiable" would be wrong, so they are a third
  outcome rather than folded into "no".
- check08 scores 200 cells against the five-step model with **3** deviations.
- check02 compares 102 bodies across 7 generator families, with 757
  non-compiling probes past the err-115 boundary. Of those 102, pcrec's
  `--count-groups` accepts and agrees with libpcre2 on exactly **1** (the
  base-tier `(a)(b)`) and refuses the other **101** as unimplemented
  constructs — every generator family here except part of scoped_n exists
  specifically to probe constructs outside the base tier.
- check05: 904 single-digit cells, 244 running-count cells, 123 leading-8/9
  cells, 24 octal cells, 12 overflow cells.

## Four findings against the invariant statements

**1. Invariant 3's "(Today: exactly three.)" is wrong under its own
definition — it is two. RESOLVED: the definition widened, and the count is
three again.** The definition originally given is "`a<syntax>*` compiles and
the quantifier binds the preceding atom". Swept over all 100 rows, exactly two
rows satisfy it: `\E` and `(?#...)`. The third lexical-*mode* construct, `\Q`,
fails and not narrowly: `a\Q*` does compile, but quote mode turns the `*` into
a **literal**, so there is no quantifier to bind anything. `^Z\Q*$` accepts
exactly one string, `"Z*$"` — the `$` is swallowed too. Confirmed by two
independent discriminators.

The resolution went the widening way, not the shrinking way: invariant 10's
`quantifiable` fact gained a fourth cell value, `lexical`, meaning *quantifying
the row does not create a quantifier for the construct at all*. That covers
both ways it happens, and check10 now enforces exactly those two:

- **D1** — the `*` binds the PRECEDING atom transparently (`spec_is_lexical()`,
  check03's criterion). Holds for `\E` and `(?#...)`.
- **D2** — the `*` stops being a quantifier and becomes a LITERAL. Holds for
  `\Q`, and only `\Q`.

D1 ∪ D2 = three rows, which reconciles the invariant's original "three" with
check03's measured "two" without either being wrong: check03 still pins the
two rows that satisfy invariant 3's own narrower binding criterion, and
invariant 10's `lexical` cell covers all three. check10 accepts a `lexical`
cell only on a D1-or-D2 row, and **fails a plain `yes` on a row satisfying
either discriminator** — `a\Q*` and `a\E*` both compile, so a check that only
asked "does it compile" would record `yes` for both, but in neither case is the
CONSTRUCT what got quantified: D1's star bound the atom before it, D2's star is
not a quantifier at all. The compile verdict is silent on the question the
column asks.

**How D2 is measured, since the obvious test is wrong.** "`^Z S *$` does not
accept 'Z'" fires for every row whose syntax contains a mandatory consuming
atom, and `(a)(?-1)` is not lexical. The property that actually separates them
is monotonicity: *a quantifier with a minimum of zero can only ADD strings to a
language, never remove one*. So D2 is witnessed when adding the `*` REMOVES a
string — some subject `^Z S` accepts and `^Z S *` rejects. For `\Q` the witness
is `"Z"`; for a genuine quantifier no such witness can exist, whatever S
consumes. It is a witness search, so no witness leaves D2 false, which is the
safe direction; the rows the search cannot reach are named on every run and
capped by a ceiling (see below).

**2. Invariant 8's "both deviating cells" is confirmed, and they are the
high-side delimiter-eaters.** `[0-[.a.]]` and `[0-[=a=]]` are err **150**
(invalid range) where the same text standalone is err **113** (collating
element / equivalence class not supported): at an endpoint the range-validity
check runs first, so the endpoint position changes which of two real errors
surfaces. The **low** side does not deviate — `[[.a.]-z]` is 113 and matches
the model — so the asymmetry is the finding. A third cell, `[0-(?[[a]])]`,
deviates only because this sweep also covers the 56 rows that are not
class-reachable; it is pinned separately with its own reason.

**3. The verb row's own syntax probe is unrepresentative of the verb row.**
`a(*ACCEPT)*` **compiles** while `a(*FAIL)*` is err 109 — and ACCEPT and FAIL
sit in the same table in `--list-verbs` with identical `forms` text. So the
quantifiability split is *not* upper-vs-lower case, and a row-level
`quantifiable` fact read off the row's `(*ACCEPT)` probe would record
"quantifiable" for a family in which 6 of the 24 askable names are not (with
26 more unaskable). check10 pins this cell so the reason survives.

**4. The `quantifiable` column caught two real bugs within minutes of
landing.** On its first appearance the column had `(?>...)` = `no` where
libpcre2 compiles `a(?>...)*`, `a(?>b)*`, `a(?>b)+` and `a(?>b){2}` — atomic
groups are quantifiable — and `(?:...)` = `-`, a fifth value outside the
documented set {yes, no, form, lexical}, on a row libpcre2 says is plainly
`yes`. Both were corrected while this amendment was being written; the column
now reads 46 yes / 38 no / 13 form / 3 lexical. check10 rejects an unrecognised
cell value outright rather than routing it into the form-resolved branch,
because a value the check does not know cannot be checked, and a placeholder is
not a verdict.

## Two corrections this suite made to its own predictors

Recorded because the wrong version is the intuitive one in both cases.

**`\7777` is err 151, not `chr(0377)` followed by `'7'`.** The first version of
check05's clause 3 reasoned that since octal fallback reads at most three
digits, a longer run could never overflow. libpcre2 disagreed. The rule reads
three digits and *then* range-checks them; it does not shorten the read to keep
the value in range. So a longer run overflows exactly when its first three
octal digits do.

**A range endpoint consumes one *item*, not the whole text.** check08's first
model classified the endpoint text by censusing `[S]`, which cannot tell "one
item denoting many characters" (`\d`, ten bytes) from "many items"
(`\k<name>`, seven bytes — `\k` is a literal `'k'` in class position, then
`<name>` are literals). It predicted err 150 for `[0-\k<name>]`, which libpcre2
compiles as the range `0-k`. The fix is the **extent scan**: the item is the
shortest prefix P of S such that `[P]` compiles and the census of `[S]` is
exactly the union of the censuses of `[P]` and `[S-minus-P]`. Every input to
that test is a libpcre2 verdict. A **tail rule** goes with it — whatever is
left over is an ordinary class body that can fail on its own, which is why
`[0-\g{-1}]` is err 108 despite a perfectly good endpoint (the leftover
`{-1}` is the descending range `'{'` to `'1'`).

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
