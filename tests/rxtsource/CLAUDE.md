# tests/rxtsource — INV-COMPAT, and the head grammar's only witnesses

[DD-13b.W1.1]. The `.rxt` format grew a HEAD; this directory is where the
claim that nothing existing changed meaning stops being a claim.

`make test-rxtsource`, and a section of `make test`. Cheap on purpose:
three parses of the corpus and no compiles at all, so it does not compete
with `test-corpus` for the box.

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
census (all files)         179 files / 3,265 blocks / 26,691 lines
tests/known_fail/k34...      1 file  /     3 blocks /     11 lines
                           ---------------------------------------
run.sh's own population    178 files / 3,262 blocks / 26,680 lines
```

`run.sh`'s no-argument branch excludes `*/known_fail/*`. C1 is a PARSE
differential and reads every file, so it asserts 179 and invokes leg B
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

**0 of the corpus's 179 files are head-bearing** — measured, and asserted
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
