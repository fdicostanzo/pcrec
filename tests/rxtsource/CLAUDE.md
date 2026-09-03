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
| C3 (oracle re-run) | what a subject's bytes decode to; a skip predicate that widened | anything outside its own discovery |
| C0a | the harness calling `--list-source` when it should not; a corpus file growing a head | anything after the call is made |
| the hash pin | any edit inside `run.sh`'s arm chain | an edit to an arm APPENDED after the END marker (correctly — that is the safe edit) |
| the keyword census | a corpus line whose first token is a word the grown grammar wants | a collision that arrives with a new corpus file between runs (it runs every time for that reason) |

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
