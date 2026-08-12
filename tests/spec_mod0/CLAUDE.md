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

**As of 2026-08-12, after the MOD-0.8b D27 pass: 13 pass, 1 fail, 0 awaiting —
exit 1, and the failure is a real defect, not an awaited surface.**
check14_option_runs fails on one family, and only that family: pcrec accepts a
quantifier after a bare option run (`a(?i)*`) where PCRE2 raises error 109, and
emits a matcher for it. The check is pinned to PCRE2's answer and will pass with
no edit once the producer refuses the form. See "The quantified-option-run
finding" below and check14's own FINDING block.

**As of 2026-08-12 (MOD-0.3c, the first module with producers): 10 pass, 0
fail, 0 awaiting — the suite's first exit-0.** The history below records the
awaiting era: as of 2026-08-11 it was 9 pass / 0 fail / 1 awaiting, exit 1,
and that was the correct state — invariant 7 (gate equivalence) now HAS a working pcrec-side
comparison (the `--features` surface exists, the comparison runs a full
sweep, and the instrument's own liveness is validated live), but it still
cannot PASS: every row is refused identically in all three configurations
because no module has an implementation yet, so `gate.compared_pairs` is
honestly 0. check07 therefore reports **AWAITING-POPULATION**, not
AWAITING-SURFACE — the distinction matters (see its own header and the
correction below) even though the runner still buckets both under "awaiting
a surface" in its summary line, a wording that is now slightly imprecise for
this one check and is left as-is rather than reworded for one caller.
Invariant 10's surface LANDED first
(`--list-syntax`'s 14th column, `quantifiable`, values {yes, no, form,
lexical}); invariant 4's followed (the 15th column, `class_expect`, vocabulary
{"err N", "char 0xNN", "set N"}, empty on the 56 group/verb rows); invariant
2's followed that (`pcrec --count-groups [--] PATTERN`, a bare integer on
stdout exit 0, or pcrec's normal refusal diagnostic on stderr exit 1); invariant
6's followed that (`pcrec --probe-ask WANT [--] CONSTRUCT`, one TSV line per
call reporting the parser cursor before and after) — all four checks now
compare rather than await. `--oracle-only` exits 0 when the only non-passes
are awaited surfaces; it is for working on the oracle halves and says so on
every run.

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
- **check02 / 03 / 04 / 05 / 07 / 08 / 10** `.c` — the seven C checks for the
  ten module-0 invariants.
- **check11_modifier_syntax.c**, **check12_modifier_semantics.c** — a SECOND
  D27 pass (2026-08-12, SR-mod05), scoped to the `modifiers` module (PCRE2's
  inline option settings, `(?i)` / `(?i:...)` / `(?-i)` / `(?^)` / ...) rather
  than the original ten invariants. Same method, same harness, a different
  promise: check11 owns the RECOGNITION BOUNDARY (which spellings are a
  construct at all), check12 owns the BEHAVIOUR (what a recognised spelling
  DOES). See their own headers for the full predictor set and the finding
  check12's scoping family is built around.
- **spec_pcrec.h** — running the pcrec BINARY as a black box: fork/exec with a
  timeout, and the four-way verdict classification (ACCEPTED /
  REFUSED-AS-UNIMPLEMENTED / REFUSED-AS-OUT-OF-SCOPE / REFUSED-AS-INVALID) that
  every pcrec-comparing check needs. Added by the MOD-0.8b pass and used by
  check13 and check14 only; check02, check07 and check11 keep their own older
  private copies, deliberately untouched (rewriting a passing check to route
  through a new header changes what it tests). It differs from those copies in
  one respect that is load-bearing: **stdout is counted, not discarded**, so
  "emitted no C" is an observation rather than an inference from the exit code.
- **check13_uprop_syntax.c**, **check14_option_runs.c** — a THIRD D27 pass
  (2026-08-12, MOD-0.8b), scoped to two construct families' RECOGNITION
  behaviour: `\p{...}` / `\P{...}` and the `(?...)` option run. Their method
  differs from check11/check12's in the way that turned out to matter: **every
  population is generated, not hand-listed**, and every bound on a sweep is
  stated at the family it bounds. check14 overlaps check11 on purpose, and in
  the space check11's 21-entry hand-written structural table does not reach it
  found the quantified-option-run defect below.

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
| 1 | check01_isolation.sh | **PASS** (surface landed, MOD-0.1 slice 9 — self-armed with no edit) | `nm` over `build/libpcrec.a` and `build/obj` — the linker | — (enabled.c defines the enabled-set symbols, scans.c the convention-named extent scans; 4 symbol/TU pairs asserted absent from the recogniser TU's undefined list) |
| 2 | check02_capture_count.c | **PASS** (surface landed) | libpcre2 `PCRE2_INFO_CAPTURECOUNT`, cross-checked against the err-115 boundary | — (`pcrec --count-groups -- BODY` is run, no shell involved, for every one of the 102 generated bodies; exit 0 compares its printed count against CAPTURECOUNT — `capture.pcrec_compared`, floor 1 — exit 1 means pcrec refuses the body as an unimplemented construct and is counted, not compared — `capture.pcrec_refused`, floor 101. Today only 1 of the 102 bodies is accepted, because pcrec implements only the base tier and every generator family here exists specifically to probe named groups / lookaround / verbs / callouts / branch-reset / `(?n)` / quote mode — the compared population grows module by module as those land) |
| 3 | check03_lexical.c | **PASS** | libpcre2 binding behaviour over all 100 rows | — |
| 4 | check04_class_position.c | **PASS** (surface landed) | libpcre2 256-byte class censuses | — (the `class_expect` column compares equal to the measured value on all 44 class-reachable rows — `class.expect_compared_cells`, floor 44 — and is verified empty on all 56 group/verb rows — `class.expect_verified_empty_rows`, floor 56) |
| 5 | check05_digits.c | **PASS** | libpcre2 over a digit-run × count grid | — |
| 6 | check06_cursor.sh | **PASS** (surface landed) | **none — see below; this check compares pcrec against itself** | — (`pcrec --probe-ask WANT [--] CONSTRUCT` drives one doorway once per call; every one of the 99 doorway-reaching rows is driven at `claim`, `verdict` AND `result` — `cursor.clear_compared`, floor 198, asserts pos_after == pos_before at the two WANT_RESULT-clear levels, and `cursor.set_compared`, floor 99, asserts pos_after >= pos_before at the WANT_RESULT-set level. The one row with no doorway at all, `(?:...)`, is named and floored separately — `cursor.base_answered_rows`, floor 1 — and the check fails if that set changes shape in either direction. Today every comparison is an equality: no recogniser is implemented yet, so nothing ever reaches a `result`-level answer, and the >= assertion's strictly-greater branch is unexercised but live) |
| 7 | check07_gate_equivalence.c | **PASS** (population arrived 2026-08-12: module `classes`, 12 eligible rows, 24 pairs — the suite's FIRST exit-0 run) | libpcre2 decides membership | — (the sweep now applies the TRANSITION RULE, a dated correction in the file header: a disabled-module row accepted at baseline MUST flip to refused-as-unimplemented NAMING ITS OWN MODULE — still-accepted is a dead gate (sabotage-verified: an ext_gate that never demotes fails 24 clauses), invalid is the second-quieter-grammar defect, and every other row keeps strict equality so cross-module leaks fail. `gate.eligible_rows` floored at 12, `gate.baseline_accepted_rows` at 13; `gate.compared_pairs` stays floor-0 DELIBERATELY — check09's per-name assertion arms on it and would demand all 17 modules toggle; the pair count is transitively ratcheted via eligible_rows through the pairs==eligible×2 self-consistency assertion) |
| 8 | check08_endpoints.c | **PASS** | libpcre2 censuses + an oracle-measured extent scan | — |
| 9 | check09_every_feature_toggles.sh | **PASS** (coverage half) | check07's per-name output vs the registry | check07's comparison now runs; the per-name-nonzero assertion (2) still arms only when `gate.compared_pairs` is floored above 0 — coverage (assertion 1, all module names present — 17 since MOD-0.3a added `extended-classes`) is checked and passing now |
| 10 | check10_quantifiable.c | **PASS** (surface landed) | libpcre2 `a<syntax>*` verdicts, two form sweeps, and the two LEXICAL discriminators | — (the `quantifiable` column arrived mid-work; it caught two real bugs on arrival, see below) |

## The modifiers module (check11, check12) — a second D27 pass, 2026-08-12

Not one of the ten numbered invariants above — the ten are about pcrec's
architecture in general; check11/check12 are about ONE module's promise
(PCRE2's inline option settings, `--features modifiers`), written by a
SEPARATE D27-blinded pass (same discipline: denied `src/`, `docs/`, and the
rest of `tests/`; derived from the module's promise and live libpcre2
measurement, never from a reading of pcrec's implementation).

| Check | Status | Owns | pcrec comparison today |
|-------|--------|------|-------------------------|
| check11_modifier_syntax.c | **PASS** (113 probes; **105 compared, 8 refused-as-unimplemented** since MOD-0.5c/d gave the module producers — was 52/61 at authoring; 0 disagreements). **R20 records what this check could not see**: its probe set is a hand-listed 21-spelling table with not one QUANTIFIED spelling, and `a(?i)*` was a tier-1 miscompile sitting inside this check's own subject area (fixed at R20/SPEC-1). D27's wager paid out a second time, one level in — blindness to `src/` was not sufficient; the writer's GENERATED sweep is what reached the cell | the RECOGNITION BOUNDARY: which `(?...)` / `(?...:body)` spellings are a construct at all — alphabet soundness (pcrec's own 9 declared letters are real), alphabet COMPLETENESS (the full A-Za-z complement, not the registry's one `(?q)` sample, is independently confirmed unrecognised), the option-run's structural grammar (`^` position, `-` count, doubled `x`, whitespace), and the shared `(?-` doorway (digit=recursion vs letter=modifiers) | pcrec's LEXER already does character-level recognition ahead of the module gate — `(?X)` (unknown letter) and `(?i^)` (malformed) are both refused as genuinely invalid TODAY, independent of `--features`, which is why this check is already armed rather than AWAITING-SURFACE |
| check12_modifier_semantics.c | **PASS** (39 cases: 8 compared — all "control" patterns containing no `(?...)` construct at all — 30 refused-as-unimplemented, 6 oracle-only, 0 disagreements) | the BEHAVIOUR of a recognised spelling: per-letter effect (i/m/s/x), options × classes (`x` vs doubled `xx` — whitespace inside a class), options × quantifiers (`U` inverts `+`/`+?`, `-U` restores), SCOPING (see the finding below), reset (`(?^)`), and capture (`(?n)`, via `--count-groups`) | every construct-bearing pattern is still refused as `requires module 'modifiers'` — none of the 30 refused-unimplemented cases has landed yet, so the compared 8 are patterns that happen not to need the module at all |

**The finding check12's scoping family is built around.** The textbook-
intuitive model of PCRE-family option scoping — "a bare `(?i)` applies to
the rest of its own branch, reset at the next `|`" — is WRONG, measured
against libpcre2 10.46: `^a(?i)b|c$` against `"C"` MATCHES. An option set
inside one branch of a group is still in effect for that group's LATER
branches; the scope ends at the group's own closing `)`, not at `|`. A
pcrec whose parser resets option state at every `|` — the natural
implementation an author recalling PCRE2's docs would reach for — would
agree with every single-branch case here and fail exactly the two
across-`|` cases, silently, because both models agree everywhere else. This
is the alphabet-inheritance risk D27 exists to guard against, one level up:
even the SPEC as commonly recalled is the wrong alphabet here; only
measurement gets it right.

**Two letters (`a`, `r`) are oracle-only by design.** Both are only
observable under PCRE2_UCP (Unicode property mode); pcrec's CLI exposes no
UCP-equivalent encoding flag today, so there is no surface a comparison
could target. check12 still measures and floors the libpcre2 facts
(`modsem.oracle_only_unicode`, floor 6) so a regression in the oracle side
is caught now, with no edit needed the day a UCP-capable surface exists.

## Two recognition families (check13, check14) — a third D27 pass, 2026-08-12

Scoped to the RECOGNITION behaviour of `\p{...}` / `\P{...}` (the
`unicode-props` module, which has a recogniser and no implementation) and of
the `(?...)` option run (the `modifiers` module, which is implemented).
Everything is compared under `--features all`, the maximal configuration, so a
cell that still comes back "requires module 'X'" is genuinely unreached rather
than merely switched off.

| Check | Status | Cells | Owns |
|-------|--------|-------|------|
| check13_uprop_syntax.c | **PASS** (2,587 cells, 0 disagreements) | every byte after `\p`/`\P`; every printable byte in five braced-body positions; 20 contexts x 31 spellings; every prefix of six canonical constructs; name lengths 0..79 in four paddings; quote mode; three `--features` settings; the `-i` flag | that the construct is REAL and whose it is, that no C is ever emitted, and **where pcrec stops** |
| check14_option_runs.c | **FAIL — one family, a real defect** (4,385 compared, 512 disagreements, all in `quantified`) | every byte at the `(?` doorway and at six positions inside a run; ordered letter pairs; every placement and count of `-` and `^`; junk-letter insertion; truncation; run lengths to 32; terminator variants; whitespace with and without x mode; **a quantifier after every accepted spelling** | that pcrec accepts exactly what PCRE2 accepts |

**The offset rule check13 pins, and why an offset is not "wording".** pcrec
prints `(pattern offset N)` with each refusal, and N is where its recogniser
stopped — the position it would resume parsing from the day the module lands.
Derived from the public grammar and then confirmed on all 2,587 cells: N is the
construct's grammatical EXTENT (`\p`/`\P`, then a braced body through the first
`}` or exactly one following character), except where libpcre2 itself stops
earlier, where N is libpcre2's own error offset. Both branches are populated —
2,525 at the extent, 31 at an earlier stop, the latter being the over-length
property names, where libpcre2 abandons the name at the same byte pcrec does.
D26 tiers the *sentence* out of scope; it does not tier out the *position*, and
this is the only assertion in the suite that reads one.

**The quantified-option-run finding — check14's failing family.**
`build/pcrec --features modifiers -o - 'a(?i)*'` exits 0 and emits a matcher
that accepts `"a"`, `"aa"`, `"aaa"`. libpcre2 rejects the same pattern with
error 109 at offset 5. pcrec has modelled a bare option run as a LEXICAL
construct contributing no atom — so the `*` bound the preceding `a` — which is
the intuitive model and the wrong one; PCRE2 does not allow a quantifier there
at all. `a(?i)**` is even diagnosed as "multiple quantifiers on the same item",
the same wrong model speaking twice.

Three things make this worth the space:

- The SCOPING form is unaffected: `a(?i:b)*` compiles under both. That split is
  exact — of 7,040 (spelling x quantifier) cells run while check14 was written,
  4,472 disagreed and 2,568 agreed, and the boundary was bare-run versus
  scoping-run with no exceptions. check14 keeps 512 of each so the agreeing half
  is a live control rather than an anecdote.
- **pcrec's own registry already has the right answer.** Every `modifiers` row's
  `quantifiable` cell reads `form` — quantifiability depends on which form the
  construct takes. The producer contradicts the registry, and `probe_quant.c`
  measured the same fact before either was written. Nothing was missing; two
  parts of pcrec disagree.
- check11 covers the same module and did not find it, because check11's
  structural family is a hand-listed table of 21 spellings and none of them is
  quantified. This is the D27 wager paying out a second time, one level in:
  blindness to the source was not enough on its own — the generated sweep is
  what reached the cell.

check14 is pinned to PCRE2's answer, not to pcrec's, so it fails today and will
pass with no edit once the producer refuses the bare-run form.

**Invariant 6 is the one with no oracle half, and that is not a gap in the
work.** Every other invariant is about what a pattern MEANS, and libpcre2 is
the authority on meaning. The cursor rule is about pcrec's internal
discipline, which libpcre2 cannot arbitrate. Building a libpcre2 sweep there
to have something runnable would be theatre — a check measuring something
adjacent and reporting it as though it covered the claim. Now that
`--probe-ask` exists, check06 compares pcrec against ITSELF instead: two (in
fact three — `claim`, `verdict`, `result`) observed runs of the same
construct, with the expected relationship between `pos_before` and
`pos_after` computed arithmetically (equal, or not-less-than) rather than
read from any field. `answered_at`, `at` and `end` are the implementation
talking about itself and are never consulted for the comparison.

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
- 17 distinct module names in the registry (16 until MOD-0.3a, 2026-08-12, split `extended-classes` out of `classes`).
- 70 of 100 rows have their syntax probe accepted by libpcre2 (check07's
  membership set).
- check07's armed sweep: **1700** verdict-class checks (100 rows x (1 all-off
  + 16 inverted-module configs)), **0** disagreements. Only **1** row (the
  base row, owned by no module) is accepted by pcrec under 'all on', so
  `gate.eligible_rows` and `gate.compared_pairs` are both honestly **0** —
  see the correction below for why that is the right number, not a bug.
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
- check13: 2,587 cells, 0 disagreements. **28** of the 510 single-byte forms
  after `\p`/`\P` compile — `C L M N P S Z` in either case, 14 codes each for
  `\p` and `\P` — and every other byte lands on error 146 or 147, never on a
  third error and never on "compiles as something else". libpcre2's property
  NAME length limit sits at 49 significant characters (`\p{` + 49 x `L` is
  error 146 at offset 52, and the offset does not move as the body grows).
- check14: 4,385 cells compared, 286 deferred to a module, 36 out of scope,
  **512 disagreements, all in one family** (see the finding above). **21**
  single bytes B make `(?B)` compile — `! # * - 0 : = > C J R U ^ a i m n r s
  x |` — of which **11** are letters (`C J R U a i m n r s x`); the other ten
  are the non-letter doorways `(?` shares with the rest of PCRE2's group
  syntax. Both sets are anchored literally, because a change in the wider set
  moves the boundary this check measures even when no letter moves.

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

## Three corrections this suite made to its own predictors

Recorded because the wrong version is the intuitive one in all three cases.

**A "compared pair" is NOT every (module-owned row) x (differing
configuration) — that definition is trivially satisfied today and hides the
vacuous-pass shape C4/F4 named.** check07's first draft of the counting rule,
before its first run against the real binary, counted any row owned by
module M compiled under a configuration where M's state differs from 'all
on'. Measuring it showed ~1700 such pairs TODAY, all agreeing, because every
module-gated row is refused as "requires module 'X'" in every configuration
regardless of whether that module is nominally on or off — nothing is
implemented, so the module's state changes nothing observable. A count of
1700 agreeing pairs reads as "gate equivalence holds over a real population,"
which is false: no row has ever been let through a gate. The corrected rule
counts a pair only when the row is a libpcre2 member, is owned by the varied
module, AND is ACCEPTED under 'all on' — only an accepted row demonstrates
the module does anything, so only disabling it tests something. That rule
gives 0 pairs today (`gate.eligible_rows` is 0; the only row pcrec accepts
under 'all on', the base row `(?:...)`, is owned by no module), which is the
honest number.

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
