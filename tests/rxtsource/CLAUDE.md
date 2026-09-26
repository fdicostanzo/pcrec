# tests/rxtsource — INV-COMPAT, and the head grammar's only witnesses

[DD-13b.W1.1]. The `.rxt` format grew a HEAD; this directory is where the
claim that nothing existing changed meaning stops being a claim.

`make test-rxtsource`, and a section of `make test`. Cheap on purpose:
three parses of the corpus and NO COMPILES OF THE CORPUS, so it does not
compete with `test-corpus` for the box. [DD-13b.W1.2] added a section that
does compile — a handful of fixture targets, single digits — because
building a `.rxt` source cannot be checked without building one.

## Files

- **`run_rxtsource_tests.sh`** — the whole section. C1 (the parse
  differential), C3 (the oracle re-run), C0a (the composer was never
  invoked), the arm-block hash pin, the keyword census, and the head-path
  witnesses.
- **`build_c3_store.py`** — **[C3 THREE-WAY VERDICT, 2026-09-10/11, lane
  `pyrole`]** the store-capture script behind C3's redesign (below):
  populates `oracle_store/libpcre2-10.48/{match-at,captures}.tsv` (via
  `tests/oracle/`'s `LocalAdapter`) with exactly the hand-enumerated,
  cited questions C3's mechanism needs — not a corpus sweep. See
  `docs/design/c3_three_way.md` §4 for why this instance deliberately
  deviates from `oracle_store/CLAUDE.md`'s usual committed-reference-only
  rule, and its own header for the full argument.
- **`fixtures/*.rxtin`** — head-bearing `.rxt` files. **The extension is
  load-bearing**: `find tests -name '*.rxt'` must not see them, or they
  would join the corpus, move the pinned census, and be dispatched by
  `run.sh`'s own no-argument discovery during `test-corpus`. The runner
  copies them into a scratch directory under the real extension and
  invokes them explicitly.

## Why there are THREE parsers and that is deliberate

The `.rxt` format now has three readers: `pcrec --list-source`
(`src/parse/rxt_source.c`), `tests/harness/run.sh`'s arm chain, and
`tests/harness/verify_rxt.py`'s `parse_rxt`. Two of those are the
harness's and predate this step.

**The BODY has three readers on purpose** — that duplication is the
control C1 compares, and it is a real one: different languages, different
authors, one written years before this design existed.

**The HEAD has exactly one**, by the manager's seam ruling, and this
directory says so plainly rather than implying otherwise. `run.sh` gains
no head arms; for a head-bearing file it calls `--list-source` once and
starts its own loop at the `line` column of the first `pattern` row. So
C1 is a control for the body and **not** for the head. What covers the
head instead: the grammar's own refusals (each asserted to NAME what the
author must act on), the field manifest, the fixtures below, and the fact
— asserted twice, from two sources — that on this corpus the head is
empty.

## The two denominators differ, and it is a derivation not a discrepancy

```
census (all files)         189 files / 3,320 blocks / 26,799 lines
tests/known_fail/k34...      1 file  /     3 blocks /     11 lines
                           ---------------------------------------
run.sh's own population    178 files / 3,262 blocks / 26,680 lines
```

`run.sh`'s no-argument branch excludes `*/known_fail/*`. C1 is a PARSE
differential and reads every file, so it asserts 189 and invokes leg B
through the ARGUMENT branch, which applies no exclusion. C2 (which is
`make test-corpus`, not this directory) asserts 178. **C3 asserts
`verify_rxt`'s OWN discovery** and never either of the above — that script
has no `known_fail` exclusion and its own skip rules, and carrying a
denominator between two checks that discover independently is how a number
comes to look authoritative because it arrived from somewhere else.

The runner asserts the SUBTRACTION, not just the two totals: add a
`known_fail` file and only the relationship notices.

## What each check can and cannot see

| check | sees | is blind to |
|---|---|---|
| C1 (three-way parse differential) | a directive read differently by any two parsers; a value silently changed | anything both dumps agree about — including a key they BOTH stopped emitting (which is what the field manifest is for) |
| C1's field manifest | a column dropped from the declared header; a field containing a tab | a wrong VALUE in a correctly-shaped column |
| C3 (oracle re-run) | what a subject's bytes decode to; a skip predicate that widened; a genuine transcription error (checked against the C3 store even where python disagrees) | anything outside its own discovery; a divergence the store does not cover (falls back to today's verdict, counted STOREUNCOVERED rather than silently trusted) |
| C0a | the harness calling `--list-source` when it should not; a corpus file growing a head | anything after the call is made |
| the hash pin | any edit inside `run.sh`'s arm chain | an edit to an arm APPENDED after the END marker (correctly — that is the safe edit) |
| the keyword census | a corpus line whose first token is a word the grown grammar wants | a collision that arrives with a new corpus file between runs (it runs every time for that reason) |

## C3's THREE-WAY VERDICT (2026-09-10/11, lane `pyrole`)

C3 used to score a python-vs-expectation disagreement a FAILURE
unconditionally. It no longer does: per Frank's ruling (python is a
TRANSCRIPTION-ERROR TRIPWIRE, its independence from the expectations is
the only thing still worth checking, not its own correctness against
PCRE2 — D26 stays the compatibility target), a disagreement is now checked
against a COMMITTED oracle-store answer (`oracle_store/libpcre2-10.48/`,
`build_c3_store.py` above) before being scored: the store CONFIRMING the
expectation lands the cell in a new, always-printed, never-gated `INFO`
bucket (python was simply wrong); the store disagreeing too is a real
FAILURE; the store not covering the exact question at all is
`STOREUNCOVERED`, a counted fallback to the pre-existing verdict. This
resolved seven previously-red cells (`docs/dev/upstream_issues.md` U17 has
the measured record — two python `re` divergences from PCRE2, both
version-sensitive, closing entirely by python 3.11). **Full design:
`docs/design/c3_three_way.md`** — read it before touching any of C3's
verdict logic; it carries the verdict table, the `# pcre2-only` marking
recommendation (retire reliance on the colon spelling; it has never
actually worked — see that note's own §6), and a documented, pre-existing,
NOW-VISIBLE box-sensitivity population-pin gap this redesign surfaces
rather than causes (§7 there).

`C3_INFO`/`C3_STOREUNCOVERED` join the pin block below as two more
population pins (now eleven, not nine), checked and reconciled exactly
like the pre-existing nine.

## Two sabotage rows are DEFERRED, and the reason is written here

`docs/design/dd13_format/w1_impl.md` §3.4 lists twelve corpus rows.
**Ten are live** (`tests/mech/sabotages/S194`-`S203`). Two are not, and
neither is an oversight:

- **S-C8** — "assign a definition's re-based numbers from 1 instead of
  `base+1`". There is no composer in W1.1, so there is no code for the
  plant to land in and no corpus file that composes. The design already
  says this row is caught by "nothing on the corpus"; it arrives with the
  composer at W1.3.
- **S-C7** — "make the composer bind a definition on a block that
  references none". Same reason, one level over: its named detector is
  C0a's invocation counter, and in W1.1 the only way to move that counter
  is to make the head detector fire spuriously — which is **S-C12's
  plant, exactly**, live as S203. The two rows are the same edit until a
  composer exists to distinguish them.

**The row table, so nobody counts a row twice:**

| design row | status here |
|---|---|
| S-C1 | live as **S194** |
| S-C2 | live as **S195** |
| S-C3 | live as **S196** |
| S-C4 | live as **S197** |
| S-C5 | live as **S198** |
| S-C6 | live as **S199** (needed a witness — see below) |
| S-C7 | **deferred to W1.3 (its only W1.1 route is S-C12's plant)** |
| S-C8 | **deferred to W1.3 (no composer to plant in)** |
| S-C9 | live as **S200** |
| S-C10 | live as **S201** |
| S-C11 | live as **S202** |
| S-C12 | live as **S203** |
| (new) the four-kinds gap | live as **S204** (needed a witness) |

**All eleven live rows measured DETECTED**, one at a time through the
matrix's single-row filter.

Both are named here rather than left to inference, because the failure
this project keeps having is a row that scores green while certifying
nothing, and "the row does not exist yet" is much better than that.

**And one row was ADDED that the design did not have: S204.** W1.1 found
that `verify_rxt.py`'s parser knew 10 of the corpus's 14 line kinds and
RAISED on the other four. That was loud, which is why pointing the oracle
at the corpus surfaced it immediately. The dangerous version is the quiet
one — an unknown kind swallowed as a comment verifies nothing, reports
nothing, and subtracts from a total nobody compares — so S204 plants
exactly that, in the parser's fallthrough rather than against one kind,
and it is caught twice: by C1's leg B == leg C (which names WHICH kind
went missing) and by C3's pinned `giveup` count (which works even if both
dumps were changed together).

## The population that had to be built, and why

**0 of the corpus's 189 files are head-bearing** — measured, and asserted
every run. So the seam, the head productions and every refusal they carry
had a population of ZERO, and every check named as their detector would
have been green while detecting nothing. That is [MECH-REACH]'s failure,
and the fixtures are the answer:

| fixture | what it makes reachable |
|---|---|
| `head_basic` | the seam end to end: `--list-source` called EXACTLY ONCE (asserted through an external wrapper — "the answers were right" would also be true of a `run.sh` that never called and read the head as comments), the body-start line compared against an INDEPENDENT `grep`, row order, and the three new block directives reaching the dump |
| `head_only` | a head with no body: accepted by pcrec, and reported by `run.sh` as its existing P-C2 floor — a DISTINCT observable from a call that failed |
| `head_after_pattern` | the boundary refusal, which must name the boundary rather than the token |
| `from_cycle` | the cycle refusal, which must name the members |
| `wave2_keyword` | NOT IN THIS BUILD, never "unknown" |
| `dup_config` | a duplicate name, which must name BOTH sites |
| `block_scalar_in_body` | the one refusal all THREE parsers must share |

## The block scalar, and why it is refused in a pattern block

`format_design.md` §1.3 gives a block-line `description` the full
`prose-value` production, which includes the `|` block scalar. §1.2's
lexical rule says a pattern block's lines are NOT indented, and a block
scalar IS indented continuation. **Both cannot hold in the body.**

Resolved: `|` is a HEAD form. The body's no-indent rule is what
R-COMPAT-1 and 3,265 blocks depend on, and §1.2 calls the head/body
asymmetry "the only one"; and a body block scalar would need continuation
parsing inside `run.sh`'s per-line loop, i.e. head-shaped parsing back in
the harness, which is precisely what the seam ruling removed. All three
parsers refuse it with the reason stated, and the fixture asserts all
three — because a contradiction resolved differently in one of them
surfaces later as a bug report rather than as a design decision.

## [r46 / w11f fix lane, 2026-08-30] more fixtures, same shape

The r46 panel on the [DD-13b.W1.1] merge (`docs/dev/reviews/
2026-08-30-r46-w11-impl.md`) found the same class of gap the head path's
own fixtures above were built for, one level down: not "the head has an
empty population on the corpus" but **"the three parsers agree on the
corpus and diverge one line outside it"** — a control byte the corpus
never carries, a tab in a `with`/`from` list, a `flags`/`engine` value
outside the ruled vocabulary, an empty or `|`-trailing-space
`description`, a whitespace-only line, a directive before any pattern in
a headless file, a duplicate block name, and a handful more (findings
1-4, 7, 8, 11-16, 19-21, 23 of that review). Every one got a `.rxtin`
fixture here and a check in `run_rxtsource_tests.sh`, following the same
rule the table above states: a head-only construct (a tab in a config
list, `with` validation, the too-long-identifier caps, the budget
overflow) is checked through `pcrec --list-source` ALONE, because legs B
and C never read the head; a construct any of the three bodies can reach
(`flags`, `engine`, `description`, block `name`, a whitespace-only line,
a stray pre-block directive) is checked THREE WAYS, either
accept-with-agreement or refuse-in-all-three.

`check_refusal_all3` (in `run_rxtsource_tests.sh`) is the three-way
sibling of the pre-existing `check_refusal`: it asserts leg A's message
via the same needle mechanism and then asserts legs B and C ALSO refuse
(exit nonzero), without pinning their exact wording — D26 does not
require three parsers built by different authors in different languages
to phrase a refusal identically, only to agree that one is owed.

sem1 (the escape byte-value bug, the panel's one BLOCKER) is the fixture
to read first: `ctrl_bytes.rxtin` carries a literal VT/FF/DEL in its
pattern text and the check asserts all three legs escape it
IDENTICALLY, byte for byte — the corpus population for this bug was, and
remains, zero. `tests/mech/sabotages/S205_rxt_escape_index_not_value.sh`
re-plants the "index confused with value" shape against the fixed code
(the loop's POSITION substituted for the byte's own ordinal) and expects
this section's ctrl_bytes check, and nothing else, to go red.

**Finding 10 (RULED by the manager, 2026-08-30): a blank line ENDS a
`config` body's continuation, exactly as it ends a block scalar's** — the
body IS the indented continuation, a blank line is not indented, so it
terminates like any other non-indented line, and a directive after it
belongs to the file. `parse_prose` (the head's block-scalar production,
shared with `description`) used to disagree with `parse_config`'s own
body-ending rule, treating an interior blank line as part of the value;
both now stop at the first non-indented line, blank or not.
`blank_ends_config_body.rxtin` is the witness — a `config` body, a blank
line, then a file-level `description` — checked three ways: leg A parses
the config with only its pre-blank setting and the description as a
separate row; the seam (`run.sh`) still calls `--list-source` exactly
once and runs the one pattern block; leg C still refuses the head-bearing
file by name (unaffected).

Left at the manager's discretion, per the review's own triage (findings
18, 22 not fixed; finding 11, 12 fixed anyway, cheaply): a NUL byte
silently truncating leg A (finding 18) has no fix cheaper than a
different line-splitting scheme entirely, for a population the review
itself calls very-low-likelihood; the escape vocabulary being a stated
SUBSET of the full subject-escape table (finding 22) is now documented in
`docs/spec/rxt_format.md` rather than given a fixture, since nothing is
wrong to detect.

## [DD-13b.W1.2] the W1.2 section, and what stopped being cheap

W1.1 PARSED `target`/`config`/`lib` and resolved none of them, so this
directory could assert the head grammar's SHAPE and nothing about what it
MEANS. The W1.2 section is where resolution stops being a promise: N targets
-> N artifacts with N prefixes and ONE `rx_info.name`, the `-o` naming rule
in all three forms, `--target`'s selection and its unknown-name refusal,
`--lib-path` resolving the very reference that fails without it, the four
resolution refusals (no such definition, an unresolvable `lib` path, a
`<store>` reference, a `config` whose `pcrec` line reaches past compile
options), the library-builds-nothing outcome, and the compatibility default.

**THIS SECTION NOW COMPILES.** Its header used to say "three parses of the
corpus and no compiles at all", which was what kept it cheap enough to run
beside `test-corpus`. Building a `.rxt` source cannot be checked without
building one; the fixtures are small and the count is in single digits.

**H11's own check counts `--source` CALLS through the wrapper**, for the
reason the seam's check counts `--list-source` calls: three green cases
would also be true of a `run.sh` that never built a target at all.

**THE `head_basic` FIXTURE WAS WRONG AND NOTHING COULD SEE IT.** Its `lib`
named a file that does not exist and its `target` named the definition
`greeting`, which no block in it declares. Both were inert under W1.1 — a
recorded path is never opened, a parsed target is never resolved — so the
fixture was a perfectly good SEAM witness while carrying two declarations
that could not be satisfied. W1.2 resolves both, so it had to become true:
`common.rxtin` is a real sibling library and the target names `plain_run`.
**The generalisable half is that a fixture written for one property can be
false about another, and stops being merely unused the moment a step
downstream starts reading the declarations it carries.**

| new fixture | what it makes reachable |
|---|---|
| `three_configs` | format_design §6.3: three targets, one definition, `from` and `with` both exercised. The ONLY place N-targets/N-prefixes/one-name and H11's agreement control are observable |
| `common` | a `lib "path"` that RESOLVES, and the library-ships-nothing outcome (no target, several blocks) |
| `no_such_definition` | the tier-2 refusal naming the definition AND the lib chain |
| `lib_missing` | the tier-3 path refusal, `--lib-path`'s cure, and that `--list-source` still ACCEPTS the same file |
| `lib_store` | `lib <store>` refused as NOT IN THIS BUILD, never searched for as a filename |
| `config_pcrec_escape` | a `config`'s `pcrec -p …`, the one escape that would otherwise be SILENT (an artifact under the wrong prefix compiles perfectly) |

## [RXTNUL lane, 2026-09-12] two more silent-loss refusals, same shape

Chartered by pcrec-bench's `rxt_needs_v1.md` (`docs/design/dd13_format/
bench_rxt_needs_v1.md` §1.9 M1/M5, §2.7): two productions in
`src/parse/rxt_source.c` used to lose data silently, exit 0, no
diagnostic — a NUL byte mid-`pattern`-line TRUNCATED the pattern
(`slurp_lines`'s whole-file NUL-terminated-string split), and a pattern
block's second `description` line silently WON over the first
(`block->description` is a single field, unconditionally overwritten).
Both now refuse by name, naming the file, the line(s), and (for the NUL
case) that it is a NUL byte. A THIRD gap the bench note asked about —
whether the HEAD's own `description` should refuse a duplicate too — is
answered yes for consistency (`docs/spec/rxt_format.md`'s "a machine-
readable prose FIELD" is singular), even though the head's mechanism was
never the same silent-overwrite shape: a second head-level `description`
just became its own row with no cardinality check, never lost data.

**`dup_head_description` stays leg-A-only, and its reason does not
expire.** Checked with the single-leg `check_refusal`, never
`check_refusal_all3`: its fixture opens with two FILE-level
`description` lines above the `pattern` block, so it is head-bearing,
and the head has exactly one parser by the manager's seam ruling
(w1_impl.md §1.1) — a three-leg assertion on it is not available at any
point in this format's life, not merely not-yet-built. `head_basic.rxt`
is its accept control (it already carries exactly one).

**[DD-13b.W23.2] `nul_byte` AND `dup_description` MOVED TO
`check_refusal_all3`, and are no longer leg-A-only.** The "out of this
lane's scope" reason above was a temporary boundary and has expired:
legs B and C each closed their own gap in the attachment-arm step (the
same NUL rule now has ONE SCOPE in all three legs — the whole file,
before any line is interpreted — and both legs now refuse a second
block-level `description`, naming both lines). A scope note that
outlives its scope is the staleness shape this tree keeps catching, and
deleting a note two thirds of which is still true is the same defect
with the sign flipped — see `w23_impl.md` §1.8 item 5.

| new fixture | what it makes reachable |
|---|---|
| `nul_byte` | M1: a NUL byte mid `pattern` line, refused by all three legs, class value-shape |
| `nul_in_comment` | [DD-13b.W23.2] the fixture that DISCRIMINATES a whole-file pre-parse scan from a line-interpreting one — `nul_byte`'s own NUL sits mid `pattern` line, which every candidate scope catches |
| `dup_description` | M5: a pattern block's second `description` line, refused by all three legs naming both lines, class schema-constraint |
| `single_description` | the accept control for `dup_description` — byte-identical shape, one line, accepted by all three |
| `dup_head_description` | the head's own duplicate `description`, refused for consistency (leg A only, see above) |

## Maintenance

- The census is a **PIN**, not a derivation. When a corpus file is added
  or removed, change `CENSUS_*` and `RUNSH_*` in a reviewed commit that
  says which file moved. A pin that recomputed itself would agree with a
  shrunk corpus by construction.
- The arm hash moves when `run.sh`'s arm chain changes. That is intended
  and is never incidental — the rule lives in the check's own failure
  message, where a person looking at the failure will read it. New line
  kinds go AFTER the END marker and need no re-pin.
- Update this file when a check, a fixture or a deferred row changes role.

## [DD-13b.W1.3] — composition, the name grammar, and the dogfood

A fourth section at the end of `run_rxtsource_tests.sh`, and six new
fixtures. Every one of them exists because the population was ZERO: no
corpus file declares a `name`, so the widened name grammar, the prefix
mapping, the collision refusal and the composer itself would all have
shipped with nothing exercising them.

- `name_dashdot.rxtin` — a definition named `cls-upto-64` and one named
  `ctx.lazy`, each built through `target = <name>`. Two assertions, and the
  pair is the point: the ARTIFACTS are `cls_upto_64` and `ctx_lazy` while
  each one's `rx_info.name` is the UNMAPPED block name. The prefix says what
  the symbols are called; the name says what the artifact IS, and a build
  that mapped one into the other would lose the bench id the whole ruling
  exists to preserve.
- `target_prefix_collision.rxtin` — `a-b` and `a.b`, both mapping to `a_b`.
  The refusal must contain all THREE strings: naming only the shared prefix
  leaves a reader unable to tell which two of their names produced it.
- `compose_delivers.rxtin` — all three of D89's tiers in one artifact.
  `piece` = `(?<kept>a)(b)(c)\2` bound into `^(?&piece)$`: `kept` is named
  (DELIVERED, a `groups[]` row with `ref` "piece"), `(b)` is reached by the
  definition's own `\2` (HIDDEN, a slot and no row), `(c)` is unnamed and
  unread (ERASED, no number at all). It is where `nentries > nnames` is
  asserted for the first time, in its strongest form — 1 against 0, because
  the caller declares no named group. **The erasure assertion is a NUMBER
  with an external referent**: `RX_NCAPS` is 4, where the PCRE2 textual
  control for the same composition emits 5 (MEASURED 2026-09-03), so a
  build whose erased tier stopped erasing reads the naive append's value
  and the check says which.
- `compose_root_recursion.rxtin` — Q-W2 (D89 point 3): `(?R)` inside a bound
  definition is refused because the RULING is missing, not the meaning.
- `compose_unknown_name.rxtin` — a by-name call the closure cannot satisfy
  RE-RAISES `mod_backrefs.c`'s own sentence at its own offset, which is what
  keeps the four `perr` blocks in `tests/recursion/d27/sr_refusals.rxt` at
  today's wording.
- `compose_dup_definition.rxtin` — one name declared in two files of the
  `lib` closure. The within-file rule one scope out, naming both files.
- `bench_altwide_0_2.rxtin` — **THE DOGFOOD**: pcrec-bench's altwide@0.2
  pattern set as an `.rxt` source, verbatim, with a provenance header (repo,
  set, version, the bench commit, the date, and that the bench's own exporter
  replaces it). 33 blocks, 33 `target =` rows, and deliberately NO
  `config`/`flags`/`engine`/`budget`/`encoding` — the bench's own condition
  (their O-13 §4(b)), since D93 file-wins would otherwise pin their testee
  matrix from inside the set.

  **Its byte-for-byte arm SKIPS LOUDLY when pcrec-bench is not present.**
  That repo is a sibling, never a dependency, so a checkout without it must
  not fail this section; but where it IS present, all 33 patterns are
  compared against the bench's own `.rx` files, because a provenance header
  is a CLAIM and a claim nothing checks is a comment. `PCREC_BENCH_PATTERNS`
  overrides the path.

- `record()` / the C3 pin RECORD (2026-09-11, manager landing-bar,
  post-pyrole; **re-keyed 2026-09-22, [REL-1.6]'s first real CI run**):
  the C3 population-pin comparison asserts only where its pinned values
  are native. Originally keyed on `uname -s = Darwin`, because darwin was
  the only non-reference box in the picture and its python was always
  older than the reference's 3.14 — but the pins are PYTHON-VERSION-
  sensitive, not OS-sensitive (the BOX SENSITIVITY note in
  `run_rxtsource_tests.sh` above), and `uname` was only ever a proxy for
  that. CI's ubuntu-latest runner is `Linux`, so the darwin-only gate
  ASSERTED there against pins that are not its python's, which is exactly
  what the first CI run measured (13705 got vs 13721 pinned, PASS/SKIP/
  no-python-expression all off by 16 — the same 3.14-vs-older shape the
  darwin note already named). The gate now reads `python3`'s own resolved
  `major.minor` and compares it to the pinned reference version (`3.14`)
  directly — RECORDS the delta when they differ, on ANY box including a
  Linux one, and asserts the full pin only where the resolved python
  actually matches. The reconciliation check (sums = census) stays HARD
  regardless of python version, so a real local movement still fails
  loudly. Summary gained a `checks recorded:` line.

## [DD-13b.W23.1] the structure layer, its fixtures, and W23-S3

Ten fixtures land with the two-layer grammar, and they divide into three
kinds that are worth keeping apart when adding an eleventh.

**REGRESSIONS FOR A NARROWING TAKEN.** `config_tab_body.rxtin` and
`config_mixed_indent.rxtin` parse at **rc 0** on the pre-W23 binary. Each
fixture IS its narrowing's regression rather than an assertion about
something that never worked, which is the only form in which a narrowing
can be checked at all.

**PINS FOR A NARROWING AVOIDED.** `prose_hash.rxtin`,
`prose_ragged.rxtin` and `prose_paragraph_break.rxtin` were accepted
before and are accepted still. They exist because a later wave that
weakens S3 would re-create three narrowings SILENTLY; an avoidance needs a
cell exactly as much as a decision does, and an accident does not get one.

**A DEFECT, PINNED AS A DEFECT (AT LANDING; FIXED — see "[K57FIX lane,
2026-09-15]" below).** `prose_dedent.rxtin` used to assert TODAY'S WRONG
decoded value — the dedent strip was a byte count, so a continuation
line indented less than the block's first silently lost content — with
K57 named beside it. `tests/rxtsource/` has no known-fail bucket, so the
pin was the assertion itself: **the day K57 is fixed this fixture goes
RED**, and that red is the signal to invert it. A pin that cannot outlive
its defect is the cheapest form available here, because the fix breaks it.
That is exactly what happened; the fixture now asserts the refusal.

**EVERY PROSE CELL ASSERTS THE VALUE, NEVER THE VERDICT.** A reader that
opens a region and throws its content away still "accepts" the file. The
same logic makes `ws_only_line_positions.rxtin` assert PARSE IDENTITY with
its own deletion rather than acceptance, and makes the two comment
fixtures assert the LINE the refusal names rather than that one happened.

**W23-S3 drives BEHAVIOUR, never the table.** Its arms exercise what
each schema row CLAIMS — the opener set with a non-opener control,
the prose pair in both directions, the wave column IN TWO POPULATIONS
(arm 4: later-wave rows refuse BY NAME as NOT IN THIS BUILD; arm 4b:
RESERVED-sentinel rows refuse BY NAME as RESERVED, both boundaries read
from the dump's own `# wave-built:`/`# wave-reserved:` trailers, both
populations required non-empty), cardinality per row in
both directions, `children` with its control — and it never compares
`--list-schema` to `rxt_schema.def`, which is the same source twice. Its
denominator is the COMPILE-TIME row total the dump prints, because a check
that iterates the dump's rows cannot see a row that is missing.

**THE FIXTURES ARE LEG A ONLY AT THIS PIN**, and that is the staging
rather than the rule: legs B and C gain their attachment arm and their
child consumption at W23.2. `block_scalar_in_body.rxtin` is the visible
edge of it — a shipped refusal that changed DIRECTION (§1.2.5's widening)
and is asserted against leg A alone until the other two legs are taught.

## [DD-13b.W23.2] the ATTACHMENT ARM, legs B and C, and CLASS agreement

Legs B (`tests/harness/run.sh`) and C (`tests/harness/verify_rxt.py`)
each gain S1's attachment mechanism — an indented line's PARENT is the
immediately preceding non-indented content line, and nothing this
build's BLOCK scope declares admits a child, so an indented line is
ALWAYS a structural error — and the DIAGNOSTIC CLASS TAG on every
per-line refusal (`record_fail_class`/`_fail`, format_design.md
§2.25.5), not only the two new fixtures below. `check_refusal_all3`
(this directory's own three-leg helper) now compares CLASS across all
three legs rather than exit code alone (W23-S2), reading each leg's
class off ITS OWN OUTPUT independently — never the dump against the
table, and never one leg's tag inferred from another's.

| new fixture | what it makes reachable |
|---|---|
| `indent_pre_body` | an indented `m` line BEFORE the first `pattern`. THE POSITION IS THE CHECK (r57 S-M5) — leg C's old indentation test ran AFTER its not-seen_pattern branch, so a post-body fixture would have reported GREEN against the ordering defect |
| `indent_under_m` | an indented line under an `m` case line, mid-block, naming the PARENT — S-R1's detector (S239): flipping `m`'s `children` column makes leg A ACCEPT while legs B/C still REFUSE, so only the three-leg differential sees the row move |

**[FINDING] `w23_impl.md` §3.2's fixture table says `indent_under_m`'s
class is schema-constraint; the DELIVERED W23.1 code disagrees with its
own design note.** `src/parse/rxt_source.c`'s S1 attachment block files
EVERY "indented line continues nothing" failure under RXTD_STRUCTURE
(`structure-attachment`) regardless of WHY there is nowhere to attach —
no parent open at all, or a parent whose `children` column is NONE —
MEASURED against the shipped binary at three call sites
(`rxt_source.c:1169`, `:1173`, `:1184`). Per this step's own boundary
("must not touch `rxt_source.c`'s grammar"), legs B and C are made to
MATCH leg A rather than the note: all three legs read
`structure-attachment` for `indent_under_m.rxtin`, and the fixture's own
header records the discrepancy. See `docs/dev/lanes/w232_report.md` for
the full account.

**THE CLASS-TAG RETROFIT REACHES EVERY PER-LINE REFUSAL IN LEGS B AND
C**, not only the two new fixtures — including the existing seven
`check_refusal_all3` call sites (`bad_flags`, `bad_engine`,
`desc_pipe_trailing_space`, `directive_before_pattern`,
`bad_name_ident`, `bad_encoding_ident`, `dup_block_name`), each now
naming its class, and the catch-all ("unrecognized line" / "unparseable
.rxt line") in both legs, which reads `unknown-token-in-scope`.

## [DD-13b.W23.3] the fourteen productions, and two witnesses the step ATE

Eleven fixtures land, one is deleted and one is re-aimed. The deletions
are the part worth reading, because they are this step consuming its own
population rather than anything going wrong.

**THE WAVE TIER'S POPULATION WENT TO ZERO.** `refuse_wave`'s
NOT-IN-THIS-BUILD branch fires for a row whose `wave` sits strictly
between this build's and the RESERVED sentinel. Every W23 row's wave IS
this build's now, so the tier is empty and no fixture can construct a
member — the table is compile-time. `format_design.md` §1.3 and
`w23_impl.md` §2.3 both state that emptiness IN ADVANCE, which is why it
is a staging fact rather than a finding:

- **`wave2_keyword.rxtin` is DELETED** (its keyword, `include`, shipped)
  and **`include_head.rxtin` replaces it**, asserting the acceptance. A
  file named for the refusal it pinned, asserting the opposite, would be
  a lie about itself; inverting an assertion in place is how a fixture
  stops meaning what its header says.
- **`unknown_kind.rxtin`'s token moves `tag` → `no-such-kind`**, chosen
  because it cannot graduate the way `tag` did. "Not in this build" and
  "unparseable" stay distinguishable through this file and
  `version_reserved.rxtin` rather than through one token wearing both
  hats — the general repair for a witness whose subject graduates.
- **W23-S3 arm 4 gains an EXTRACTOR-HEALTH assertion** and then reports
  an honest zero as a PASS. W23.1 wrote "a population of ZERO is also a
  failure here" and was right for its reason (the arm had read 0 rows out
  of a real population of 7 because `read` collapsed the dump's empty TAB
  fields). That rule conflates two zeros. The repair runs the SAME awk
  with the wave threshold lowered to 0, which must find rows; a zero
  there is still the broken-extractor zero and still fails. **The general
  form: a population of zero is a failure only while you cannot tell it
  from a broken instrument — make the instrument's health a separate
  non-vacuous assertion and the honest zero becomes reportable.**

**THE HEADLESS/HEAD-BEARING SPLIT IS WHY FOUR AUX FIXTURES LOOK ALIKE.**
A FILE-scope production is a head declaration and the head has ONE parser
(the seam ruling), so a three-leg assertion on one is unavailable at any
point in W23 — r59-A2's disposition for `dup_head_description.rxtin`, one
production over. `aux_arbitrary_keys.rxtin` is leg A only and says so;
`aux_deep_tree`, `aux_literal_pipe`, `aux_malformed_body` and
`aux_subtree_extent` are HEADLESS ON PURPOSE so all three legs answer.

| new fixture | what it makes reachable |
|---|---|
| `aux_arbitrary_keys` | §2.27's whole promise in one cell, as an ACCEPTANCE fixture: aux's failure mode is pcrec deciding it UNDERSTANDS something, which a refusal fixture structurally cannot catch. S245's first detector |
| `aux_deep_tree` | aux being INTERPRETED — keys that are real format keywords three levels deep, and the assertion is an ABSENCE (no extra block, no extra case, no provenance record) |
| `aux_literal_pipe` | §2.27.2 decision 3's falsification point: inside an open subtree a trimmed bare `\|` is the LITERAL byte. Its VALUE-level half activates with `#section aux` at W23.4; what it asserts here is acceptance and three-leg agreement |
| `aux_malformed_body` | a RAGGED DEDENT inside a subtree, refused locally with the `pattern` block below NOT implicated. **The shape had to be a ragged dedent and not a deep indent**: inside a subtree any deeper indent is a legal child, because the subtree has no rows and so no kind that takes no continuation |
| `aux_subtree_extent` | §5.2a item 9's sharpest attack, run by the delivery on itself. THREE positive assertions, because an extent bug that swallows the next line and one that closes early produce opposite symptoms |
| `prov_verbatim_no_adaptation` + `prov_adapted_no_adaptation` | S-R2 (S240)'s pcrec-side pair. LEG A ONLY by the schema's own `validated_by` column — legs B and C CONSUME a provenance body without reading it |
| `derived_call_collision` + `derived_call_bind` | §2.22/D100, and the accept half is what stops the refusal being satisfied by a composer that binds nothing. Leg A only, and the instrument is `--source` rather than `--list-source` |
| `under_key_distinct` + `under_key_duplicate` | `under`'s four-component key tuple. **The accept half found a defect the refuse half could not**: the extractor read a colon the spelling does not have, so the tuple collapsed and the refusing fixture still went red — for a reason with nothing to do with the rule |
| `include_head` | a head `include` line PARSES (it refused as a later-wave keyword before this step) |

**EVERY THREE-LEG ASSERTION COMPARES CLASS, and where a fixture is leg A
only the reason is stated at the call**, never left looking like an
oversight. The two reasons are the seam (a FILE-scope production) and the
schema's own `validated_by` column (a row reading `pcrec` is a row legs B
and C are not claimed to check — §3.3's rule, and claiming otherwise
would be the named failure of asserting three legs on the strength of
one).

## [DD-13b.W23.3a] `include`'s harness half, and why it is TWO-LEG not three

`include` is head-scoped by design (`format_design.md` §2.5): any file
carrying one is head-bearing, and `verify_rxt.py`'s seam-ruling refusal —
UNCHANGED — already raises on it, in both plain and `--dump` mode,
before any body line is reached. **`w23_impl.md` §1.10.2's own table
reads "legs B and C" symmetrically for report/splice/failure-attribution;
the tree says leg C's half is discovery SUBTRACTION only, never a
three-way block-count comparison** — the same disposition class
`dup_head_description.rxtin` already established one production over
(§3.1's own "the head has one parser" reasoning), recurring here because
`include` cannot be moved to block scope the way `ext` at least
theoretically could be. Ruled by the manager on the merge request that
produced this section; `docs/dev/lanes/w233a_report.md` §2 carries the
full argument, and `w23_impl.md`'s own text is corrected AT THE MERGE
(w232's own precedent — a lane does not edit the ruled design note).

**W23-S7** (§3.1) is therefore a LEG A / LEG B differential over three
fixtures, `include_dup_path.rxtin` checked single-leg
(`check_refusal`, `dup_head_description.rxtin`'s own wording pattern):

| new fixture | what it makes reachable |
|---|---|
| `include_basic` + `include_basic_frag.rxtfrag` | §1.10's whole mechanism in one cell: a flat splice, one fragment, no nesting. Leg A's own include-row count, leg B's `entry files`/`fragments spliced`, and the case-count arithmetic (`1 + fragments'`) are asserted as three independent numbers |
| `include_nested` + `include_nested_frag1.rxtfrag` + `include_nested_frag2.rxtfrag` | TWO DEEP — `include_nested_frag1` itself includes `include_nested_frag2` — the fixture "in include order, depth first" needs. Leg A's own row count on the entry stays 1 (a nested fragment's own include is invisible to a single `--list-source` call on the entry, `closure_walk`'s own recursion made visible), leg B's total is 2 |
| `include_dup_path` (reuses `include_basic_frag.rxtfrag` as its collision target) | the same resolved real path, reached by two spellings, in ONE file's own `include` lines — leg A's own duplicate-target refusal, single-leg for the same reason `dup_head_description` is |

**The FOURTH FAILURE CLASS is asserted through leg B on a scenario built
inline in `run_rxtsource_tests.sh` itself** (the W23.4 item 3b
"synthetic stream" precedent, one production over): two DIFFERENT
includers that both reach the same fragment, transitively, which only a
multi-file closure walk can see (a same-file duplicate, like
`include_dup_path`, never reaches `rxt_expand_closure` at all — leg A
already refused the entry's own `--list-source` call). The entry's own
body still runs (rule 1 of §1.10.2 — a broken closure does not delete
the entry's own cases), asserted as `cases failed: 1`.

**THE CORPUS CONTROL** (§1.10.3/§1.10.4) runs through `--dump`, never a
bare `bash run.sh`: this section's own header says it is cheap because it
compiles nothing, and a bare full-corpus run would duplicate
`test-corpus`'s own compile workload inside a section built specifically
not to compete with it for the box. `--dump` still walks every file
through subtraction and splice (parsing only), so it answers the same
question — `entry files == CENSUS_FILES`, `fragments spliced == 0` — at
zero compile cost. The two lines print to STDERR under `--dump`
specifically so they never join the rows the C1 differential compares.

**S247** plants the one thing that would make `include_nested` alone
insufficient: `rxt_expand_closure`'s own recursive call deleted, so a
fragment's OWN nested includes are silently never followed. Detected on
`include_nested` (`fragments spliced` 2 -> 1) and invisible on
`include_basic` (nothing at depth two to lose) and on the corpus control
(zero include lines to begin with) — the FIXTURE-arm-red/corpus-arm-green
split §6.3a's own acceptance line names.

## [DD-13b.W23.4] the four `#section` blocks, R5/R6's repair, and six
## pre-existing checks made section-aware

`--list-source` now carries `#section provenance`/`variants`/`cases`/
`aux` after its main table — everything W23.3's leg A recognised and
validated but did not store. `src/core/internal.h`'s `RxtProv`/
`RxtVariant`/`RxtCase`/`RxtAux` and `src/parse/rxt_source.c`'s own
CLAUDE.md entry carry the mechanism; this file is the CHECK side.

**`section_count SECTION FILE` is the one shared helper** (defined
beside `pass`/`fail`, near the top of `run_rxtsource_tests.sh`) every
fixture check below routes through, so there is one section-boundary-
tracking awk script rather than five hand-rolled copies. `SECTION=""`
means the main table.

**R5 AND R6, REPAIRED** (w23_impl.md §1.5, the `NF != 15`-shaped defect
this tree had inherited): both assertions used to read EVERY non-`#`
row of `$DUMP_A_RAW` as if it belonged to the main table, which four
`#section` blocks violate on every row — R5's own field-count check and
R6's head-declaration counter (an INEQUALITY reader, broken by the exact
same fact an equality reader like R2/R3 survives by luck: every
section's own field 1 is the `line` integer, which can equal no `kind`
token, but a COUNT of rows whose field 2 is not `"pattern"` catches
every `#section cases` row too). Both are now SECTION-AWARE: they track
the stream's own `#section NAME` / `#kind` boundaries and use the
matching section's own expected width, hard-failing on an unrecognised
section name rather than defaulting to the main table's — a detection
helper that defaults on missing input fails in the silent direction
([ABI-NS]). **The synthetic-stream control** (item 3b, a hand-written
stream never real `pcrec` output, at a section width that differs from
16 — `#section cases` is ALSO 16, so a width-blind repair would pass a
`cases`-only control by coincidence) exercises both repaired arms.
**W23-S4** asserts the invariant that makes R2/R3 safe rather than
merely lucky (no section row's field 1 equals a main-table `kind`
token) and that sections FOLLOW the main table, on `aux_deep_tree.rxtin`
— the fixture whose whole point is colliding keys is also the sharpest
witness that a section row's `key` VALUE containing "pattern" never
collides with its `line` FIELD 1.

**SIX PRE-EXISTING CHECKS HAD TO LEARN THE SAME LESSON** the corpus
itself is too clean to teach: any fixture whose block carries a real
case line (`m`/`n`/etc.) now legitimately grows a `#section cases`
block, and a check that read "every non-`#` row" as if it were the main
table now mis-reads section data rows as extra "kinds" or extra
"blocks". `sem10`'s `be_kinds`, `w23s1/ws-positions`'s twin-file
diff (which also had to blank section rows' OWN `line`/`block_line`
fields, not just the main table's `line` column — the two dumps'
absolute line numbers genuinely differ once whitespace-only lines are
deleted), `head/head_basic`'s row-order check, `W23-S3 arm 1`'s opener
probe (whose synthetic two-block file now carries an `m` case each) all
stop at the first `#section` line or route through `section_count`.
Every one of these was reproduced as a genuine regression against a
scratch build of the branch point (`b9a49d35`, 184/0/0) before being
attributed to this change — BOILERPLATE's own rule.

**`aux/deep-tree` and `aux/subtree-extent`'s "exactly N rows" assertions
were OBSOLETE BY DESIGN**, not merely stale: W23.3 asserted a total dump
row count of 1 (or 2) because aux content was structurally invisible;
W23.4's whole point is making it visible via `#section aux`, so a
nonzero row count there is now CORRECT and the absence claim narrows to
the surfaces that must still show nothing — the main table (`section_count
""`), `#section cases` and `#section provenance`/`variants`. Both checks
now assert each population explicitly rather than one combined total.

**`aux_literal_pipe`'s central assertion, owed since W23.3**
(`w233_report.md` §3.2: "the VALUE half is W23.4's"), is now built: the
`separator |` row's own `#section aux` value is the single byte `|`, and
`terminator`/`note` below it share its `parent_line` as SIBLINGS rather
than being swallowed as its children.

**Two new fixture pairs, `opener_pattern_esc_pair`/`opener_m_not_opener`
and `aux_identity`/`aux_identity_edited`**, and their own checks (S242/
S243/W23-S6 below). `aux_identity`'s pair shares an IDENTICAL one-line
preamble on purpose — format_design §3.4(a)'s own constraint, so no
row's `line` is downstream of the aux-body edit the check makes.

**S242 (S-R4a) MEASURED A DIFFERENT SYMPTOM THAN THE DESIGN PREDICTS,
AND IT IS THE STRONGER ONE.** `pattern-esc` losing `opens_group` does
not merely misattribute a SECOND `pattern-esc` line's case rows (the
design's own first reading) — the FIRST `pattern-esc` line in a file has
no OTHER way to reach BLOCK scope (`f->base == RXT_SCOPE_FILE` maps to
BLOCK exclusively through the opener transition), so a file whose first
block opens with `pattern-esc` refuses outright. `opener_pattern_esc_pair
.rxtin` catches this at its own first line, before the block_line-drift
shape is ever reached.

**S243 (S-R4b): `m` gaining `opens_group` reaches every `m` line in the
file, not only ones at file scope** — because `pcrec_rxt_schema_opener`
is scope-FREE (a kind-text lookup over every `opens_group` row) and the
gate that matters, `pcrec_rxt_schema_group_scope(f->base)`, reads the
ROOT FRAME's `.base`, which stays `RXT_SCOPE_FILE` for the frame's whole
lifetime — block after block, case line after case line. `opener_m_not
_opener.rxtin` (one block, two `m` cases) becomes three blocks and zero
cases under the plant; on the shipped corpus the same mechanism produced
15,513 spurious block rows in this lane's own hand-verification run.

**S246, TWO VARIANTS, and the FIRST DRAFT OF VARIANT (a) TARGETED THE
WRONG SCOPE.** `ext`'s `cardinality: repeat` is declared at BOTH FILE
and BLOCK scope as two separate schema rows; `aux_identity_edited
.rxtin`'s own two `ext` blocks (`bench`, `other`) are BLOCK-scoped
(inside its one pattern block), so a plant against the FILE-scope row
alone is exercised by nothing — caught only by re-running the hand-
verify rather than trusting the first draft, and fixed to the BLOCK-scope
row. Variant (b) corrupts `section_count()` itself (the SHARED helper,
never the corpus-only `a_blocks` snippet the design's own text names,
which the corpus's zero-`ext` population cannot arm) to fold an aux
tree's `ext`-opener rows into the main-table count — reachable through
`aux_deep_tree.rxtin`'s own opener, no dedicated fixture needed.

**W23-S6** (format_design §2.27.3 clause 5): edit `aux_identity`'s own
body and require every pcrec output except `#section aux`'s rows to stay
byte-identical. TWO ARMS built — `--list-source` with the section
elided, and the COMPILED ARTIFACT (`.c` AND `.h`, via `--source`'s
implicit-single-unnamed-block default, W1.2's own compatibility rule).
**THE THIRD ARM THE DESIGN SKETCHES — "every diagnostic the file
produces" — IS DELIBERATELY NOT BUILT AS A SEPARATE FIXTURE PAIR**:
`--list-source` performs no pattern-TEXT validation at all
(`validated_by: none` on every `pattern`/`pattern-esc` row, §2.24's own
table), so a `pattern a(` fixture does not refuse under `--list-source`
— it is accepted, rc 0, exactly like any other rest-of-line text — and a
genuine format-level refusal (a malformed `provenance` field, say) would
introduce content unrelated to the aux edit into the comparison. The
diagnostic arm is discharged for free by the cardinality-corrupted half
of S246's OWN plant, whose detection is exactly a diagnostic changing
(`aux_identity_edited.rxt` starts refusing where it used to accept) —
recorded here as a deliberate narrowing rather than an omission.

## [DD-13b.W23.5] the pattern-esc seam, the `all-readers` receipts, the
## withdrawal-absence check, and the owed `mc` fixture

Four additions, and the receipts mechanism is the one worth understanding
before touching `check_refusal_all3` again.

**R-A — `pattern_esc_value_seam.rxtin`** gives the dump-value seam
`w233_report.md`/`w234_report.md` left at population ZERO its first
population of one: a `pattern` block first (leg C's `seen_pattern` gate
only exempts the literal token `pattern`, a gap named below), then a
`pattern-esc "a\nb"` block. Leg A's `pattern` column DECODES
(`a\nb` — one literal byte, one real newline, one literal byte);
legs B and C report the text AS WRITTEN (`"a\\nb"`, quotes and the
doubled backslash both present). The check asserts B == C and states
the exclusion of A explicitly, rather than comparing three legs on a
column two of them cannot agree with the third about by design.

**[FINDING] leg C refuses a file whose FIRST block opens with
`pattern-esc`.** `verify_rxt.py:667`'s `first != 'pattern'` test has no
`pattern-esc` exemption, so `[unknown-token-in-scope] '...': 'pattern-esc'
line before any pattern block` fires even though legs A and B both
accept the identical file. This is S242's own finding one production
over — a fixture cannot exercise a three-leg claim a leg structurally
refuses before reaching it — and it means `opener_pattern_esc_pair
.rxtin` (leg A only, S242) has never actually been reachable by a
three-leg comparison either. Not fixed here (out of this step's brief);
`pattern_esc_value_seam.rxtin` works around it by ordering.

**[RULEFIX, 2026-09-15] FIXED, per Frank's ruling** (not left as a
documented seam): `verify_rxt.py`'s check is now `first not in
('pattern', 'pattern-esc')`. This did NOT change the finding directly
above — leg C still reports a `pattern-esc` row's VALUE as written, never
decoded, exactly as R-A's own check asserts — only the OPENER
recognition was broken. `opener_pattern_esc_pair.rxtin` is now
reachable by all three legs; S242's own check (above) gained a
three-legged extension confirming legs B and C both report its two
blocks at their own lines (8, 10), matching leg A. The ordering
workaround this section names in `pattern_esc_value_seam.rxtin` is no
longer load-bearing (leg C would now accept a `pattern-esc`-first
file) but was left as originally written — that fixture's own claim is
about the VALUE column, not about opener position, so its ordering was
never the thing under test.

**R-B — the withdrawal-absence check (`w23_impl.md` §4.3) is a COMMITTED
CHECK now**, two of its three arms. The DATA ARM is NARROWED
structurally: an INDENT STACK tracks attachment under an `ext` (and only
`ext` — `freq`'s body is the schema's DATA scope, not TREE, so it is not
an aux subtree) opener, exactly S1/S2's own rule (a blank line or a
column-1 comment closes every attachment; a dedent pops to the matching
level), so `ext bench` / `testee pcre2/10.46` — `format_design.md`
§2.27's own worked example, now restored verbatim in `aux_identity
.rxtin`/`aux_identity_edited.rxtin` (this step reverted `w234_report.md`'s
`ref` workaround per the manager's ruling) — is correctly excluded while
a top-level `testee` line is still caught. `withdrawn_data_arm()`'s own
self-check proves the discrimination on two scratch files built inline,
never on the real corpus (which the arm above has already proven
clean). The PARSER ARM greps each of the four readers' own live-keyword
spelling (a quoted `PCREC_RXT_SCHEMA` kind in `rxt_schema.def` — the ONE
dispatch table since W23.1 retired `config_vocab`/`head_vocab`/
`block_vocab` — a quoted string in `verify_rxt.py`, a `^`-anchored bash
arm in `run.sh`, a quoted flag in `cli/main.c`). **Sabotage S248**
(`tests/mech/sabotages/S248_withdrawn_testee_returns.sh`) plants a
`config`-scope `testee` row back into `rxt_schema.def` and the PARSER
ARM alone goes red — the DATA ARM and the self-check are unaffected,
three independent arms seeing three independent things. The SPEC ARM
(§4.3(c)) is deliberately NOT a grep, and stays a standing review step.

**W23-S5, the `all-readers` POPULATION check (§3.3), walks
`--list-schema`'s OWN output** for every BLOCK-scope row reading
`validated_by: all-readers` (today: `name`, `description`, `flags`,
`encoding`, `engine`) and fails naming any row with no line in
`$RECEIPTS`. The log is written by exactly two functions and nothing
else — `check_refusal_all3_kind KIND ...` (a thin wrapper around
`check_refusal_all3` that appends a receipt after it runs, so all
thirteen existing call sites keep their positional needle arguments
unchanged; five of them were renamed to the `_kind` form) and
`check_accept_all3_kind KIND FIXTURE LABEL` (the accept-side sibling
§3.3 names, built here for the first time — `block_kinds_accept.rxtin`
carries `name`/`flags`/`encoding`/`engine` together, `description`'s own
receipt rides the pre-existing `single_description.rxtin` accept
control). **A receipt is written only when all three legs actually ran
and answered** — never a declared fixture name — which is the whole
point: a fixture that stopped reaching its own call site (a call
commented out, an early return) would still exist on disk and would
still be named by the schema row; only the invocation log notices its
absence.

**`mc_illformed_utf8.rxtin`** is `w23_impl.md` §3.2's OWED W23.3 fixture
that never landed there (SW7's ill-formed-UTF-8 advance rule). `x?`
(nullable) over three bare continuation bytes `\x80\x80\x80` under
`-e utf8`: WITH the skip rule the loop finds an empty match at 0, skips
all three continuation bytes in one step, and finds a second empty match
at 3 — count 2; WITHOUT it (naive `pos + 1` alone) it would find four.
Both `run.sh`'s C loop (the real `<prefix>_next_pos` residual) and
`verify_rxt.py`'s independent python transcription report 2, and both
were confirmed to FAIL loudly against the naive 4 before this fixture
was committed.

## [K57FIX lane, 2026-09-15] K57 fixed — the dedent refusal, and its
## three-leg sibling

`docs/dev/known_issues.md` K57's hold expired when [DD-13b.W23]
delivered and merged (30b1f7f2). The manager's standing ruling: a
continuation line indented LESS than the block's own dedent depth (set
by the first continuation line) is a REFUSAL by name, class
`value-shape`, naming the shallower line's own indent and the depth the
first line set — never the silent byte-loss the entry filed, and never
a silent reinterpretation either. `src/parse/rxt_source.c`'s
`read_prose_region` (leg A), `tests/harness/run.sh`'s `prose_take` (leg
B) and `tests/harness/verify_rxt.py`'s prose-region arm (leg C) all
carried the identical byte-count dedent and all three now refuse it
identically.

**`prose_dedent.rxtin` is UNCHANGED IN CONTENT and INVERTED IN
ASSERTION**, exactly as its own header and this file's note above
predicted: the fixture that used to pin the wrong decoded VALUE now pins
the refusal. It stays LEG-A-ONLY — it is head-scoped (`description |`
above the first `pattern`), and the head has one parser by the seam
ruling, so legs B and C never reach it regardless of what their own
dedent code does.

**`prose_dedent_body.rxtin` is NEW, and it exists because leg-A-only
would have left legs B's and C's own dedent fix UNREACHED by any check**
— the identical shallow-continuation shape, at BLOCK scope (a pattern
block's own `description`) rather than the file's head, so all three
legs parse it. Checked with `check_refusal_all3_kind description ...`:
all three refuse, class `value-shape` agrees, and `description`'s
existing `all-readers` receipt population (W23-S5) gains another entry
rather than a new kind.

**LEG B NEEDED A LATCH, not just the validation check.** `prose_take` is
called per streaming line, and `record_fail` never aborts the file the
way leg A's C-level `return` does — so the naive fix (validate, record,
clear `prose_open`) let the region's REMAINING lines fall through to the
top-level per-line dispatch as if they were ordinary directives, which
raised a SECOND, unrelated `structure-attachment` failure ("indented
line continues nothing") that `extract_class`'s last-bracket read then
reported instead of the real one — caught live on
`prose_dedent_body.rxtin` before this note was written, not assumed. The
fix is `prose_bad`, a per-region latch (reset at all three sites that
open a region, alongside `prose_dedent`): once set, `prose_take` keeps
swallowing the region's lines silently rather than handing them back to
the dispatcher, which is what leg A's single-pass extent scan does for
free by never re-entering per-line dispatch inside a region at all.

`docs/spec/rxt_format.md`'s S3 section states the decode rule (dedent
depth, the paragraph-break exemption for a whitespace-only line, and the
refusal) normatively — it previously stated only the region's EXTENT and
left the decode to `docs/dev/known_issues.md` K57's own text.

## [O29FIX lane, 2026-09-16] a FOURTH closing site, and it was missing

pcrec-bench's O-29 (found at pin cd371441): with several `pattern` blocks
in one file, each carrying its own valid `provenance` (or `variant`)
sub-block, `--list-source`'s `#section provenance`/`variants` rows
appeared for the TEXTUALLY LAST block only — the others vanished, exit
0, no diagnostic. The brief's working hypothesis (a pending accumulator
flushed by a following content line and by EOF, but not by the next
`pattern` opener) turned out to be WRONG when read against the code:
that path (the S1 "else" branch's dedent-pop while loop, `rxt_source.c`
around the main loop's S1 attachment logic) already calls
`RXT_CLOSE_FRAME` correctly whenever the next line is ordinary CONTENT —
including a `pattern`/`pattern-esc` opener, which reuses the SAME
top-level frame rather than pushing a new one, so the dedent that lands
on it pops every deeper frame first. Traced by hand line by line, that
path could not reproduce the drop.

**The real fourth site was in S0**, right above the attachment logic:
"a BLANK and a COMMENT each close every open attachment" was implemented
as a bare `ndepth = 1` reset rather than a call to `RXT_CLOSE_FRAME` —
`rxt_source.c`'s own comment on the macro had said "three sites" for as
long as the macro existed, and the fourth was the omission itself. Since
two `pattern` blocks are ordinarily separated by a blank line (or a
comment), this is the shape that actually reproduces O-29 on essentially
any real multi-block file using `provenance`/`variant`: a `tag` line
placed AFTER a block's provenance (the bench's own "suppresses the
drop" observation) works because `tag` is CONTENT and closes the frame
through the already-correct dedent-pop path before any blank line is
reached; with nothing but a blank/comment between the provenance body
and the next block, nothing ever called the macro.

**The fix is the general mechanism, not a `provenance` special case**:
the S0 branch now runs the SAME closing loop the dedent-pop and
end-of-file sites already use (`while (ndepth > 1) RXT_CLOSE_FRAME(...)`),
so any currently-open frame of ANY scope gets its `constraints` checked
and, for PROVENANCE/VARIANT, its `#section` row pushed — never a
provenance-specific branch. `cases` and `aux`/`ext` were measured
UNAFFECTED and the reason each is different: a CASE row (`m`/`n`/`mc`/…)
is pushed immediately when its own line is read, never deferred to any
frame close, so there was never a pending record to lose. An aux row is
ALSO pushed per line (`aux_push`, at dispatch), but on top of that
`RXT_CLOSE_FRAME` is a no-op for a tree frame regardless — its whole
body is `if (!(F)->tree) { ...constraints...; ...push...; }` — so the
old buggy reset and the fixed closing loop behave IDENTICALLY for `ext`;
neither one ever had anything to do there. `o29_multi_aux_control.rxtin`
below is a measured artifact for that claim, not just the assertion.

Four fixtures, all LEG A ONLY (`provenance`'s and `variant`'s own
`validated_by: PCREC` column — legs B and C consume a sub-block's body
without reading it):

| fixture | what it makes reachable |
|---|---|
| `o29_multi_provenance` | THE REPRODUCTION: three blocks, each provenance the block's last content, closed by a blank line (block 1), a comment line (block 2) and end of file (block 3) in turn — one fixture exercising all three real closing sites, with per-block line/block_line/name/fidelity attribution asserted, not just a count |
| `o29_multi_variant` | the same shape for `variant` — the GENERAL-mechanism claim's own witness: a second scope reached by the identical fix with no scope-specific code |
| `o29_suppressed_order` | the CONTROL: `provenance` then `tag` (not the reverse) in each of two blocks — pins that this order needed no fix and gets none, both before and after |
| `o29_multi_aux_control` | the CONTROL for `ext`: the same three-closing-site shape, asserting all 6 aux rows (opener + one child, times 3 blocks) present and correctly attributed — `ext` never shared this bug, and this fixture is the measured reason rather than the claim |

See `docs/dev/lanes/o29fix_report.md` for the diagnosis-vs-hypothesis
account and the validation numbers.

## [FINDINGS] B0 (lane findb0, 2026-09-26) — the `analysis` bundle's format rows

`run_rxtsource_tests.sh`'s `[FINDINGS] B0` section, LEG A ONLY (every row
is head-scoped; the head has one parser). Design:
`docs/design/findings/design.md` §3.1/§13 B0; contract:
`docs/spec/rxt_format.md`'s "`analysis` — the bundle".

| fixture | what it makes reachable |
|---|---|
| `analysis_bundle_accept` | THE ACCEPT HALF, asserted on the dump's ROWS: two bundles (one `include <log>`, one without) as two `analysis` rows; each kind block's `provenance` four frames deep (file → bundle → `freq` → provenance) reaching `#section provenance` attributed to its bundle; an `exemplar` owing `bytes`/`sha256` and no `url`, an `authored` block owing neither (the conjunctive `required-if`) |
| `analysis_in_fragment` + `analysis_frag_mid.rxtfrag` + `analysis_frag_leaf.rxtfrag` | the fragment rule (r2 M-B3): a bundle TWO include links down refuses the ENTRY's parse, naming the leaf's own `file:line` |

The REFUSALS are generated inline (`fb0_case LABEL CLASS NEEDLE BODY`,
one scratch file per case, asserted on the class tag AND a needle naming
the rule), with a population floor of 34 (the case count) so a case that stops being driven
is red. Controls: an exemplar with `bytes`/`sha256`, a `pcrec` line whose
word is not `--analysis`, and a fragment broken for ANOTHER reason (it must
NOT fail the entry's parse — only the bundle rule propagates; everything
else stays leg B's `[resolution]` class).

**THE BUNDLE-LEVEL (query, encoding) COLLISION HAS AN EMPTY DESIGNED
POPULATION AT B0**: `freq` is the only kind row and a bundle holds one, so
no file can put two blocks in one bundle. The claim table lives on the
BUNDLE frame regardless; its one reachable input is one `serves` line
claiming one pair twice (`serves-collision`). B5 (`cpfreq`) owes the
two-block fixture. Sabotage rows: S290 (the ` and ` conjunction read as its
first conjunct only), S291 (the fragment refusal swallowed).
