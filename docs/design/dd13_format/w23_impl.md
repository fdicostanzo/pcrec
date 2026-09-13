# [DD-13b.W23] Implementation note — the one W23 delivery

**Status: REVISION 1.1 — the r59 FIX ROUND. NO CODE IS WRITTEN.**
The design is `format_design.md` **REVISION 3.4.1**, panel-gated at r58
(`docs/dev/reviews/2026-09-13-r58-w23-aux.md`) with the Frank queue
EMPTY (D99 withdrew W23-F1/F2, D100 ruled W23-F4 ACCEPT, W23-F3 was
resolved at revision 3.1). Revision 1 of THIS note was panelled at r59
(`docs/dev/reviews/2026-09-13-r59-w23-impl.md`: 4 blockers, 13 must-fix
groups, all FIX-NOW, plus manager rulings R1-R4) — **§0.5 is the
finding-by-finding record and is where a reader of revision 1 starts.**
This note is the build plan that opens the
implementation: what lands where, in what order, behind which merges,
with which checks, and what each step owes the spec. It is
`w1_impl.md`'s shape — §6's per-step briefs are §7/§8's there — and
it is written so three adversarial critics can attack it section by
section.

Against: `format_design.md` 3.4.1 (the normative design), D99, D100,
D101, D80, D77, D76, D94, D26, the r57 and r58 review records,
`bench_rxt_needs_v1.md` (the received bench input, and Frank's F-Q1 /
F-Q2 rulings in its header), the `rxtnul` lane report (STEP 0), the
`w23aux` and `w23fix3` lane reports, `docs/dev/learnings.md` §3, and a
read-only survey of the tree at this lane's merge base.

---

## 0. How to read this

### 0.1 Claim marking

- **MEASURED** — a command was run over this worktree and its output is
  quoted or its `file:line` cited. **This lane ran no `make`, no
  compile, no suite and no battery**: every MEASURED fact here is a
  read, a grep or a line count. Where a number would need a build, the
  note says OWED and names the step that produces it.
- **CITED** — quoted from a ruling, a review, a spec or the tree, with
  its `file:line`.
- **ARGUED** — reasoning over the above. The panel's natural target.
- **DECIDED** — a point `format_design.md` left to the implementer, or
  where the tree and the design need reconciling. Each is flagged
  inline and collected in §7.2.

**The rule this note inherits from `w1_impl.md` §0.1 and applies to
itself**: a grep COUNT is MEASURED; what the count MEANS for
reachability is ARGUED, and in a tree with per-section test scripts it
is usually wrong. §1.5's format-reader survey is written under that
rule — it reports what each site *does with* the dump's shape, not
merely that the site exists.

### 0.2 The delivery in one paragraph

W23 is one delivery and **SIX merges** (revision 1 said five; r59-B2's
`include` harness half is a sixth, W23.3a — §1.10). The
**STRUCTURE LAYER** (S0-S3 and
three schema parameters, `format_design.md` §1.2.1) stops being a
property of leg A's control flow and becomes a declared table,
`src/parse/rxt_schema.def`, that leg A WALKS and `--list-schema`
PRINTS — one derivation, two readers. Legs B (`tests/harness/run.sh`)
and C (`tests/harness/verify_rxt.py`) grow the ATTACHMENT arm they have
never had, plus a **diagnostic CLASS tag** so the three-leg differential
compares a rule and not an exit code. On that base the productions land:
`pattern-esc`, `provenance`, `vocabulary`, `tag`, `mc`, `under`,
`oracle` at a version, `variant` as a sub-block, `include`, `@file:`
with `as`/`sha256`, the `freq` data block, `use`, the §2.22
derived-identifier call binding, and the AUX production `ext
<consumer>` — the one production pcrec deliberately does not
understand. `--list-source` then grows four `#section` blocks and the
appended columns, which is the change that carries a **format-reader
survey obligation by grep** (§1.5) rather than by memory. Nothing in
W23 touches emitted scaffolding, so **there is no abi event** (§1.9),
and `--list-source`'s own dump shape is the only caller-observable
surface that moves.

### 0.3 What this note does not design

- **The design itself.** Where this note and `format_design.md` 3.4.1
  differ, the design note is right and this one is the bug. Every
  normative statement here is a citation.
- **Diagnostic WORDING** — D26. The note specifies diagnostic CLASS
  (a machine-read tag, §3.1), never a sentence.
- **W1.3.1 and W1.4** (run.sh's composed-block path;
  `w13_runsh_composed_path.patch`, and the in-pattern delivery
  follow-ons). `format_design.md` §1.4 states W23 interacts with
  neither, and §1.2's file table here is the check on that claim: no
  W23 step opens `rxt_compose.c` except §2.22's lookup, which is
  additive.
- **The bench's side of anything.** Their sixteen-config matrix, their
  loader, their roster spelling and whether they use `ext bench` at all
  are theirs (D78, D99 item 3). §5 maps their 41-check acceptance bar
  onto our steps so the staging satisfies it; it does not plan their
  lane.
- **`--list-source --resolved`** — named and unbuilt, and it stays that
  way (§2.24's third non-validated home).

### 0.4 The ruled record this note is built on

Six inputs bind the plan, and each is cited where it bites rather than
summarised once:

| input | what it fixes |
|---|---|
| **D99** | the format's PURPOSE; the two withdrawals; the AUX production; the GRADUATION RULE; D93 decoupled |
| **D100** | W23-F4 ACCEPT — §2.22's derived-identifier binding lands as designed, and the two `rxt_source.c` comment sites move with it (SW12) |
| **r58 R1** | structure-layer **parameter 3**, the OPEN SUBTREE (`children: tree`): S2's opener set is EMPTY and S3 never opens inside it. This is what the parser implements for `ext` |
| **r58 R3** | `tag-prose` is REMOVED. A `tag` item is a bare label or a `key=value` with no whitespace, as W2 shipped it |
| **F-Q1** (bench input header) | there is no W2-only cut: the first delivery is Tier 1 AND Tier 2 |
| **F-Q2** (bench input header) | multi-line patterns are a MUST; `pattern-esc` is first-delivery scope alongside the NUL refusal |

**Three things a reader of an earlier revision must not carry a memory
of**, restated here because the r58 residue class is disposition text
and this note is 900 lines of it:

1. There are **SEVEN** constraint kinds (§2.25.3), not eight.
2. The structure layer takes **THREE** parameters over **THREE**
   columns (§1.2.1), not two over three.
3. **No prose values inside an aux body.** A trimmed bare `|` there is
   the literal byte `|` (§2.27.2 decision 3, RULED at r58). Every aux
   value is one line.

And two mechanisms are **WITHDRAWN and have no implementation in any
step of this plan**: the head declaration `configs build`/`describe`
and the `config`-body lines `testee`/`option`/`provides`. §4.3 makes
that absence a *checkable* landing condition rather than a promise,
on SW19's own model.

---

## 1. What lands where

### 1.1 The seam, restated: who parses what after W23

W1 ruled the seam and W23 does not move it. **CITED**, `w1_impl.md`
§1.1: for a file whose first non-comment line is not `pattern`,
`run.sh` calls `--list-source` ONCE, reads the `line` column of the
first `pattern` row, and starts its per-line loop there; the head is an
untouched byte range whose boundary comes from the one head parser.
**MEASURED, the shipped tree**: that call is `tests/harness/run.sh:1642`,
the boundary extraction is `:1651-1652`, and the skip is applied at
`:1684`/`:1691`.

What W23 changes about the seam is narrower than it looks, and stating
it precisely is what keeps the staging honest:

- **The HEAD still has ONE parser.** Every W23 head declaration
  (`include`, `vocabulary`, `oracle`, `tag`, `use`, `ext`, the `freq`
  data block) is above the first `pattern` line and is therefore inside
  the byte range legs B and C never read. They gain **no head arms**.
  **`include` IS THE ONE HEAD DECLARATION WITH A CONSEQUENCE FOR LEGS B
  AND C, AND IT IS NOT A HEAD ARM** (r59-B2 — revision 1 stated this
  bullet and §1.7 row 5's *"include discovery"* two sections apart and
  never reconciled them, which is how the harness half of H5 came to
  have no step at all). The distinction that makes both sentences true:
  legs B and C never PARSE an `include` line — they read the resolved
  fragment list off the SAME `--list-source` call they already make for
  the body boundary, exactly as `w1_impl.md` §1.2's H11 target
  inventory does (**MEASURED**, `run.sh:1671-1675` is that read) — and
  then they SPLICE each fragment's blocks into the entry's own run.
  Reading a list of paths out of a TSV column is not a head arm; it is
  the seam working. **§1.10 is the whole mechanism**, and it is a
  separate merge because it changes `run.sh`'s FILE DISCOVERY, which is
  the most load-bearing loop in the tree.
- **The BODY has three parsers, and W23 grows all three.** `tag`, `mc`,
  `under`, `provenance`, `variant`, `ext` at block scope, `pattern-esc`
  and `@file:`'s suffixes are all block-scoped, so leg B's arm chain and
  leg C's `parse_rxt` must each grow them. That is the deliberate
  control (`w1_impl.md` §1.1's r45chk F2 correction) and it is why the
  three-leg differential is the delivery's central instrument.
- **The ATTACHMENT arm is new in two legs and re-shaped in one.**
  **MEASURED**: leg B has no indentation test at all — its arm chain is
  **TWENTY-TWO** `^`-anchored `[[ =~ ]]` arms, none of which tolerates
  leading whitespace, so an indented line reaches the catch-all at
  `:2105-2109` by fall-through. **The derivation, because revision 1
  said "seventeen" and that is the PINNED REGION's count read as the
  chain's** (r59-B-M7): 17 arms inside the hash-pinned region
  (`run.sh:1713` BEGIN .. `:1967` END, arms at `:1714`, `:1742`,
  `:1759`, `:1767`, `:1778`, `:1781`, `:1792`, `:1798`, `:1801`,
  `:1827`, `:1843`, `:1859`, `:1875`, `:1891`, `:1907`, `:1918`,
  `:1942`) plus **5 appended after it** (`:1984`, `:2000`, `:2015`,
  `:2057`, `:2092`). That is `format_design.md` §0.6's own ruled
  derivation, re-run against the file for this revision; the note's
  own §2.25.5 and §1.1 both state 22. The substance is unchanged — no
  arm tolerates leading whitespace either way — but the number a code
  lane sizes its rewrite from must match the ruled record. Leg C has a
  dedicated refusal
  (`verify_rxt.py:424-427`) that is a REJECTION of indentation, not an
  attachment rule. Leg A has the only real test
  (`rxt_source.c:1021-1030`). §1.7 is what each must become.

### 1.2 File by file

Every row names the step (§2) that opens it. A file appearing in two
steps is named twice on purpose — that is a merge-order fact, not a
duplication.

| # | file | lang | change | step |
|---|---|---|---|---|
| F1 | `src/parse/rxt_schema.def` (**new**) | C (X-macro) | THE SCHEMA TABLE. One row per (scope, kind) with `format_design.md` §2.25.2's ten columns. `src/core/limits.def`'s shape (**MEASURED**: 393 lines, header `:1-77` documents the X-macro row and the home-dispatch idiom) | W23.1 |
| F2 | `Makefile` | make | `rxt_schema.def` joins the object prerequisite list. **MEASURED**: `Makefile:150` is the rule, and `:118-146` is the comment recording the same defect **THREE** times — `limits.def` at `[LIM-1]`, `limits.def` again at `[CC-DIFF]` STEP 2, and `uprops_tables.inc` at `[M5.0]` stage 3 — each found the same way, by `touch` + `make` printing "Nothing to be done" (revision 1 cited `:121-137` and said "twice"; the third instance is in the same comment and is the one that made `gen-tables` a LIST). A `.def` that is not a prerequisite lets an edit rebuild nothing (`ccd2_report.md` §6b) | W23.1 |
| F3 | `src/parse/rxt_schema.c` (**new**) | C | the table's READER: `pcrec_rxt_schema_row(scope, kind)`, the three structure-layer parameter queries (`opens_group`, the `value`+`children` PAIR, `children == tree`), and ONE exhaustive `default:`-less switch over the constraint enum — `src/parse/definitions.c`'s `pcrec_def_tag_applies` shape, so a kind added later is a compile error at the one site that must handle it | W23.1 |
| F4 | `src/parse/rxt_source.c` | C | leg A's dispatch becomes a WALK over F1 rather than three `vocab_find` tables. **MEASURED, what is displaced**: `head_vocab :137-142`, `config_vocab :145-150`, `block_vocab :156-167`, `vocab_find :169-174`, and the per-line dispatch inside `pcrec_rxt_source_parse :984-1365` (head branch `:1068-1136`, body branch `:1139-1314`). S1 attachment replaces the flat `line_indented` test at `:1021-1030`; S3's extent rule replaces `parse_prose`'s `:513-564` loop condition; the diagnostic CLASS tag joins `rxt_fail :196-219` (**MEASURED: 61 CALL SITES** — `grep -c 'rxt_fail('` returns 63 and two of those are the prototype at `:193` and the definition at `:196`, r59-B-N3). **Also displaced: `config_vocab`'s two WITHDRAWN rows** `{ "testee", 3 }, { "option", 3 }` at `:149` — see §4.3, which is where revision 1's absence claim was wrong | W23.1 |
| F5 | `src/parse/schema_dump.c` (**new**) | C | `--list-schema`, `src/parse/limits_dump.c`'s shape (**MEASURED**: 89 lines, `pcrec_limits_tsv :55-89` (revision 1 said `:57`; the function opens at `:55`, r59-C), and it `#include`s the `.def` directly with the macro defined at the call site). Plus the `surface` section: the declared NON-coverage rows (§2.24's table, four rows at 3.4.1) | W23.1 |
| F6 | `cli/main.c` | C | `--list-schema` joins the registry-dump guard. **MEASURED**: the six existing dumps dispatch at `:651-656`, `--list-source` separately at `:664` with its own branch `:1177-1216` (revision 1 said `:1230`; the branch's closing brace is `:1216` and `--probe-ask`'s comment opens at `:1218`, r59-C), and the shared guard block is `:1330-1379`. `--list-schema` is the **SEVENTH registry dump** and the eighth conforming table producer (§2.25.1, corrected at r57 S-N1 — `docs/spec/cli.md:586` already gives `--list-limits` the sixth ordinal) | W23.1 |
| F7 | `tests/harness/run.sh` | bash | leg B: the ATTACHMENT arm; the diagnostic CLASS tag it has never had; the STEP 0 parity refusals (§1.8); the block-scoped W23 arms (`tag`, `mc`, `under`, `pattern-esc`, `provenance`, `variant`, `ext`); `@file:` subjects; cells; `use` | W23.2, .3 |
| **F7a** | `tests/harness/run.sh` | bash | **leg B's `include` half (§1.10, NEW at revision 1.1 — r59-B2).** Entry-set SUBTRACTION at discovery (**MEASURED**: discovery is `:293-307` — the no-arg `find … -not -path "*/known_fail/*"` at `:296-297` and the directory-argument `find` at `:302`. Revision 1 named no site at all and `format_design.md` §2.11 cites `run.sh:184-216`, which is the `tests/lib` shim sourcing and the `CC` resolution — §1.10's first finding); the fragment SPLICE into the entry's own per-file loop; the CLOSURE tally; the fourth failure class; the two new summary lines | **W23.3a** |
| F8 | `tests/harness/verify_rxt.py` | python3 | leg C: the same three lists. **MEASURED**: `parse_rxt :343-615`, eighteen kinds, catch-all `:613-614`; the head-bearing refusal `:407-417` stays (the seam ruling); `dump_file :649-712` gains the new kinds | W23.2, .3 |
| **F8a** | `tests/harness/verify_rxt.py` | python3 | **leg C's `include` half (§1.10).** Its `discover` (`:715`) does the same subtraction; its own walk splices the fragment's cases. **Its head-bearing refusal (`:407-417`) is UNCHANGED, and that is exactly why leg C reads the fragment list off `--list-source` rather than parsing the `include` line** — the seam ruling survives the fold-in intact | **W23.3a** |
| F9 | `cli/main.c` | C | the `pattern-esc` DECODE flag (working name `--pattern-esc`; `cli.md`'s hunk owns the spelling, §2.19). The pattern OPERAND is taken in the quoted-escape form and decoded by the format's OWN decoder — the one `--source`/`--list-source` use. **No bash decoding anywhere** | W23.3 |
| F10 | `src/parse/rxt_source.c` | C | the productions: `pattern-esc` (with `\x00` refused by name citing K9), `provenance`, `vocabulary`, `tag`, `mc`, `under`, `oracle` at a version, `variant` as a sub-block, `include`, `@file:`'s `as`/`sha256`, the `freq` data block + `analysis`, `use`, and **`ext`** | W23.3 |
| F11 | `src/parse/rxt_compose.c` | C | §2.22's DERIVED-IDENTIFIER lookup: a second key on the SAME definition set, built with `pcrec_rxt_prefix_from_name` (**MEASURED**, its one home, `rxt_source.c:337-343`), consulted by the existing lookup. The at-use collision refusal naming BOTH definitions. **REFUSE BEFORE MAPPING** — the over-long name is refused first, because the mapping silently TRUNCATES at `dstsz` | W23.3 |
| F12 | `src/parse/rxt_source.c`'s TWO comment sites | C | SW12/D100: **`:269-297`** (`defname_ok`'s header — the function itself opens at `:298`) and **`:1177-1180`** (the `name` arm's pointer to it, inside the arm that opens at `:1175`) record the repealed "buildable and NOT callable" boundary AS A RULING. They move in the same change as F11 or the code contradicts the behaviour. **BOTH RANGES WERE WRONG AT REVISION 1 AND ARE WRONG IN `format_design.md`'s SW12 ROW, WHICH IS WHERE THEY WERE INHERITED FROM** (r59-B-M2): `:280-291` is the middle of `defname_ok`'s header rather than its extent, and **`:1126-1130` is the file-level duplicate-`description` refusal — a different production entirely**. The design's row is corrected as a drive-by in this same change (`w23implfix_report.md` §3). Read the file; do not carry a range | W23.3 |
| F13 | `tests/harness/driver.c` | C | H6's `@<path>` subject argument (byte-exact, additive — every existing invocation is untouched) and H7's find-all loop for `mc`, written to `match_api.md` §3.1's restart protocol | W23.3 |
| F14 | `src/parse/rxt_source.c` | C | `--list-source` at W23: the appended columns (`tags`, `oracle`, `esc`), the new head ROW kinds, and the **four `#section` blocks**. **MEASURED, what moves**: `rxt_columns[] :2074-2082` (sixteen columns today), the header comment `:2091-2107` — which states outright at `:2105-2107` that the stream is SECTIONLESS — `put_escaped :2035-2054` applied to columns 4/5/15 at `:2131`/`:2133`/`:2153`, and the row emitter `:2116-2157` | W23.4 |
| F15 | `tests/rxtsource/run_rxtsource_tests.sh` | bash | the C1 differential extended to W23; the MANIFEST re-pinned; **the field-count assertion repaired for sections** (§1.5 — this is a FINDING, not bookkeeping); the census re-pinned; the `all-readers` POPULATION check | W23.1..W23.5 |
| F16 | `tests/rxtsource/fixtures/*.rxtin` | data | §3.2's fixture table: **twenty-three ROWS naming twenty-six FILES** at revision 1.1 (one row names a pair, one row re-aims an existing file rather than adding one, and revision 1.1 adds four — §1.10's three and §1.8's NUL-in-comment). Revision 1 said "nineteen fixtures" without saying whether that counted rows or files, and it was neither (r59-C#3) | each step |
| F17 | `tests/mech/sabotages/S239..` | bash | §3.5's **EIGHT** rows (revision 1 had six; r59-A-M2(a) adds S246 and r59-B2 adds S247). **MEASURED**: the highest existing id on main is **S238** (`tests/mech/sabotages/S238_size_drop_unstamped.sh`), by the procedure `tests/mech/CLAUDE.md:649-656` names | each step |
| F18 | `docs/spec/*` | md | §4's SW1-SW19, distributed per step (D80) | each step |
| F19 | `docs/dev/known_issues.md` | md | **NO-OP — a POINTER, not a change** (r59-B-N5). K57 (the block-scalar dedent strip) was FILED by lane `w23fix` at revision 3.2 and the entry exists; `prose_dedent.rxtin` CITES it (§3.2, and R4 in §7.3 defines the fixture's waiting state). The row stays in this table only so a lane does not go looking for an unfiled issue. Revision 1's conditional wording ("if it is not already filed") read as work that might be owed | — |

**Not opened by any step, and it is worth naming what is NOT touched**:
`src/ir/`, `src/opt/`, `src/gen/`, `lib/pcrec.h`. That is the file-level
statement of §1.9's no-abi claim, and it is checkable by `git diff
--stat` at every merge rather than by reading this sentence.

### 1.3 The grammar W23 accepts, and what it still refuses

Exactly `format_design.md` §1.3's EBNF and §1.4's W23 row. Restated as
what a lane types, because the EBNF is written for a reader and a lane
needs a checklist:

**Head declarations added**: `include`, `oracle`, `tag`, `use`,
`vocabulary`, `ext` — plus the `freq` data block with `analysis`
selecting it from a `config` body.

**Block lines added**: `pattern-esc` (a second BLOCK OPENER — S2's set
goes to two members), `tag`, `mc`, `under`, `oracle`, `provenance`,
`variant`, `ext`; and `@file:` gains optional `as <defname>` and
`sha256 <hex64>` suffixes.

**Still refused after W23, BY NAME** (SW13's "NOT IN THIS BUILD" list,
DERIVED from the schema's `wave` column rather than hand-kept):
`version` (RESERVED, §1.6.3 — reserved without a production), and
nothing else from this delivery. The list's membership is what makes
the `wave` column earn its keep during the five-merge rollout: at every
intermediate tree some W23 keywords parse and the rest must refuse BY
NAME rather than as unknown tokens. **This is the column's only
consumer and its population is empty at the FINAL pin** (§2.25.2 states
that honestly); §2.3 is where the rollout consumes it.

**Never entering the list, and the derivation is why**: `configs`,
`testee`, `option`, `provides` have no schema row, therefore no `wave`
value, therefore no entry. A withdrawn production cannot be forgotten
in a hand-kept list because there is no hand-kept list (SW13's own 3.4
note).

### 1.4 The schema table — `src/parse/rxt_schema.def` (H16)

The table is one row per (scope, kind), ten columns
(`format_design.md` §2.25.2). Three implementation facts the design
leaves to this note:

**DECIDED (1) — the row shape is an X-macro with HOME DISPATCH, on
`limits.def`'s model.** `limits.def`'s header (`:1-77`) documents a
`PCREC_LIMIT(name, value, unit, kind, override, anchor, desc, home)`
row where the consumer defines the macro before `#include`ing and
everything else defaults to a no-op. The schema's consumers are three:
the parser's dispatch walk (F3), the dump (F5), and the spec renderer
(§4). A fourth consumer — the `all-readers` POPULATION check (§3.3) —
reads the DUMP rather than the table, deliberately, because a check
that read the table would share a source with the parser that enforces
it.

**DECIDED (2) — `constraints` is a list column and the switch over it
is the one exhaustive site.** `format_design.md` §2.25.1 names
`src/parse/definitions.c`'s `pcrec_def_tag_applies` as the shape: ONE
`default:`-less switch, so an eighth constraint kind added later is a
compile error at exactly the site that must handle it
(`src/opt/mrl.c:18-24`'s stated house rule). The seven kinds are
`required`, `required-if`, `forbidden-if`, `exactly-one-of`, `closed`,
`unique-by`, `functional-binding`. **SEVEN. `cross-scope` is NOT among
them** — its only customer left with D99 and it is back on §2.25.4's
deferred list with a sharpened trigger.

**DECIDED (3) — `under`'s key tuple is PARSER CODE and the `.def` says
so.** The row carries `unique-by under-key`; the arm that EXTRACTS
(convention, subject, kind, startpos) out of a `qualified-line` value is
C, because `value: qualified-line` already means the parser decomposes
the value and a declared extractor would be a second description of a
decomposition the parser performs anyway (§2.25.3). **This is the one
named exception and the note that claims completeness must say
"seven kinds and one named parser-code exception"** — a schema
presenting itself as complete while a refusal rule lives in control
flow is §5.2a item 4's dangerous outcome, and `--list-schema` would
then be a confident wrong answer.

**The cardinality values are DECIDED BY THE DESIGN and the lane types
them, it does not choose them** (§2.25.2's table, ruled at 3.3):
`at-most-one` for `name`, `engine`, `encoding`, `features`, `flags`,
`description`, `export`; **`accumulate` over the field set `{steps,
frames}` for `budget`**, with a repeated FIELD refused. `budget` is the
row the measurement changed — `tests/harness/giveup.rxt:19-23` writes
`budget steps=` and `budget frames=` in one block on purpose, and
`parse_setting` (**MEASURED**, `rxt_source.c:573-672`) routes them to
separate slots, so `at-most-one` would refuse a shipped corpus file.

### 1.5 `--list-source` at W23, and THE FORMAT-READER SURVEY

This is the change with the largest blast radius and the smallest
apparent one, and `format_design.md` §2.24 names the obligation it
carries: *sweep the tree BY GREP for every site that parses
`--list-source`'s SHAPE — field counts, positional splits, assumptions
about which `#section` lines appear — not only for sites that read a
particular column's VALUE.* The precedent is
`registry_built_status_memo.md`'s own CORRECTION: the `built` column's
landing swept every reader of the dump's MEANING and missed two readers
of its FORM, both hard-coding **`NF != 15`**, and the union battery
found them rather than the survey.

**THE SURVEY WAS RUN FOR THIS NOTE, read-only, at this lane's merge
base.** It is reproduced here as a table because a survey whose result
lives in a lane's context is a survey nobody can re-run. The command is
the contract, not the table:

```
grep -rn -- "--list-source\|NF *[!=]= *[0-9]\|cut -f\|IFS=\$'\\\\t'\|awk -F'\\\\t'" \
  tests/ scripts/ tools/ cli/ src/ docs/
```

| # | site | what it does with the SHAPE | survives a new COLUMN? | survives a new `#section`? |
|---|---|---|---|---|
| R1 | `tests/harness/run.sh:1642` | issues the call; no shape parsing | — | — |
| R2 | `tests/harness/run.sh:1651-1652` | `awk -F'\t' '$1 == "pattern" { print $2; exit }'` | **YES** — reads from the front by position | **YES, BY LUCK** (see the invariant below) |
| R3 | `tests/harness/run.sh:1671-1675` | `IFS=$'\t' read -r _k _l _n _v _rest` over `grep -v '^#'`, keyed on `_k = "target"` | **YES** — appends land in `_rest` | **BY LUCK**, and it degrades SILENTLY: a section data row reaches the loop, fails the key test, and is skipped with no signal |
| R4 | `tests/rxtsource/run_rxtsource_tests.sh:464-477` | `MANIFEST`, a hand-pinned literal of the column names, compared verbatim against the live header | **BREAKS LOUDLY AND CORRECTLY** — this is the intended gate for column growth, with its own "add it to MANIFEST" instruction at `:473-476` | yes |
| **R5** | **`tests/rxtsource/run_rxtsource_tests.sh:479-494`** | **`awk -F'\t' -v want="$ncols" '$2 ~ /^#/ { next } NF != want + 1 { ... }'` — asserts EVERY non-comment row has exactly `ncols+1` fields, unconditionally of kind** | yes (`ncols` derives from `MANIFEST`, which moves in lockstep) | **NO. THIS IS THE `NF != 15` DEFECT, ALIVE, IN THIS REPO, FOUND BY GREP BEFORE LANDING** |
| **R6** | **`tests/rxtsource/run_rxtsource_tests.sh:499-505`** | **`awk -F'\t' '$2 !~ /^#/ && $2 != "pattern" { n++ }'` and its `== "pattern"` twin at `:500`, asserted ZERO at `:501-505` ("the corpus has no head")** | yes (`$2` is positional from the front) | **NO. IT IS R5'S DEFECT IN THE INEQUALITY DIRECTION, AND A GREEN W23-S4 WOULD PROVE IT BROKEN** |
| R7 | `tests/rxtsource/run_rxtsource_tests.sh:561-568` | the leg A→B/C projection: explicit positional column selection, `print "block", $1, $3..$13, $17` | **YES for APPENDS** (reads 1-13 and 17); an INSERTED column breaks it silently — which is what `table_contract.md`'s append-only rule exists to forbid | YES (`$2 == "pattern"` filter) |
| R8 | `docs/spec/rxt_format.md:418-499` | the prose column contract | needs its SW11/SW14 hunk | needs the section column lists |
| R9 | `tests/mech/sabotages/S200,S201,S202,S203` | plants whose detectors ARE R4/R5 (and, once repaired, R6) | — | — |
| — | `tests/harness/verify_rxt.py` | **does NOT read the dump at all** — it refuses a head-bearing file by name (`:407-417`) per the seam ruling | — | — |
| — | `cli/`, `tools/`, `scripts/` | **no hits** | — | — |
| — | `src/parse/rxt_source.c:2085` | `pcrec_rxt_source_ncols()` — **ZERO callers anywhere in the tree**; the field-manifest check derives its own `ncols` from the `MANIFEST` string instead | — | — |

**R5 IS THE SURVEY'S RESULT AND IT IS A FINDING, NOT A CHORE.** The
check at `run_rxtsource_tests.sh:482` asserts a single uniform column
shape for every non-`#` row in the stream. Four `#section` blocks whose
rows are narrower (`#section aux` has eight columns against the main
table's sixteen-plus) violate it on every row of every section, so
W23.4 would deliver a red check that is *right to fire* — the check is
not wrong about today's stream, it is unaware that the stream can have
more than one shape.

**And its failure message would MISDIRECT, which is what turns a bad
afternoon into a wrong fix.** The `fail` branch at `:484-492` names
exactly one cause — *"A field contained a TAB, which is what the
rxt-escape on columns 4, 5 and 15 exists to prevent"* — and goes on to
name the three corpus blocks that carry a literal tab. A lane meeting
that red after emitting a section would go looking at the escape
function. The message was true when it was written, because a field
count could only go wrong one way; a second row shape is a second way,
and the message has to gain it in the same change.

**The repair is stated as part of the step and not
left to whoever meets the red** (§6.4 item 3): the assertion becomes
section-aware — one expected field count per section, derived from that
section's own declared column list, with the main table keeping its
`ncols+1` — and the "no section declared" arm HARD-FAILS rather than
defaulting, because an extraction helper that defaults on missing input
fails in the silent direction (learnings §3, the `[ABI-NS]` entry).

**R6 IS THE SAME DEFECT ON THE OTHER SIDE OF THE COMPARISON, AND
REVISION 1 MARKED IT SAFE** (r59-A1, and it is the sharpest single
observation of the round). R6 counts every non-comment row whose `kind`
field is **not** `pattern` and asserts the total is ZERO — *"the corpus
has no head"*, a third view of C0a's zero. **An EQUALITY reader
(`$1 == "pattern"`, `$2 == "pattern"`) is protected by the
first-column-is-`line` invariant below: a section row's integer can
never EQUAL a kind token, so the row is never selected and the reader
survives. An INEQUALITY reader is broken by exactly the same fact**:
every one of `#section cases`' thousands of rows has a field 2 that is
not `pattern`, so every one of them is COUNTED, and the check fails
with *"leg A emitted N head-declaration row(s); the corpus has no head"*
at roughly the corpus's own case-line count.

**And its misdirection is worse than R5's**, which is the argument for
fixing both in one step rather than meeting them one at a time: R5's
message names a TAB in a field, which at least points at the dump; R6's
names a HEAD DECLARATION in a corpus that has none, which points at the
parser. A lane that emitted `#section cases` and then read *"the corpus
has no head"* would go looking for a head-detection bug that does not
exist.

**Its repair joins R5's, in W23.4's build order, BEFORE any section is
emitted** (§6.4 item 3): both counters gain the section-aware scope —
they count rows of the MAIN TABLE, identified by the section boundary
the stream itself declares, not by "every non-comment row". The
alternative (excluding rows whose field 2 is an integer) is rejected for
the reason the taxonomy lesson gives: a filter defined by what a row is
NOT will one day hold something else.

**THE INVARIANT THAT MAKES R2 AND R3 SAFE IS AN ACCIDENT UNTIL IT IS A
CHECK, AND IT PROTECTS EQUALITY READERS ONLY.** Two readers key on a
field being EQUAL to a main-table `kind` token. They survive sections
only because every section's first column is `line`, an integer, which
can never equal `pattern`, `target` or any other kind token. **That is a
statement about SELECTION BY EQUALITY and it does not extend to
selection by inequality, exclusion or count** — R6 is the live proof,
and revision 1's sentence said "R2, R3 and R6" and so certified a reader
the same fact breaks. **DECIDED (4): the invariant becomes an assertion
in the C1 differential** — *no `#section` row's field 1 may equal any
main-table `kind` token* — walked over the dump's own header lines
rather than a hand-written list of section names. It costs one awk arm
and it is the difference between two readers that are safe and two
readers that are lucky. §3.1 carries it as check **W23-S4**. **What it
does NOT do is make an inequality reader safe, and saying so is the
whole of A1's lesson**: this invariant is a licence to keep matching a
kind token, never a licence to keep counting rows.

**Ordering is also load-bearing and the design does not state it**:
R2 takes the FIRST `$1 == "pattern"` row, so the MAIN TABLE must be
emitted before any `#section` block. **DECIDED (5): sections follow the
main table, always, and `#section cases`'s rows are not interleaved
with it.** This is free today (nothing emits a section) and impossible
to recover once a consumer has seen the other order. **AND IT IS
ASSERTED, not merely decided** (r59-A-N5): DECIDED (5) is load-bearing
for R2 — it is the whole reason R2's "first `pattern` row" is the body
boundary and not a `#section cases` row that happens to mention a
pattern — and revision 1 left it stated and untested. **W23-S4 gains a
second awk arm**: over the dump of a fixture that emits every section,
the ordinal of the last main-table row is LESS than the ordinal of the
first `#section` line. One arm, same walk, and it fails the day an
emitter interleaves.

### 1.6 `--list-schema` — the seventh registry dump

`limits_dump.c`'s shape (F5). Three things it must get right, each
because the design says so and one because the tree does:

1. **It walks the SAME table the parser enforces** — one derivation,
   two readers — so a dump that disagrees with the parser is not
   expressible. S-R3 (§3.5) is the sabotage that proves the walk is
   real rather than a parallel hand-written copy.
2. **It prints the three structure-layer parameters as ROW SETS
   SELECTED BY A COLUMN VALUE**: `opens_group: true`; `value: prose`
   AND `children: prose`; `children: tree`. All three are filters over
   one TSV and no predicate escapes into a consumer (§3.3 of the
   design, CLOSED at 3.4.1 — and the reason r58 R1 closed it is worth
   the sentence: under the reversed decision parameter 2's answer would
   have been "these five rows, PLUS every line in any `ext` scope",
   a row set plus a predicate, which is not a shape a TSV returns).
3. **It carries a `surface` SECTION** — the declared NON-coverage rows,
   four at 3.4.1: subject CONTENT, pattern TEXT, config RESOLUTION, and
   an `ext` tree's CONTENTS. The last two are not (scope, line-kind)
   pairs at all, which is why they are a sibling section and not a
   `validated_by` cell. **An absence in a table reads as something
   nobody got to; a declared non-coverage row reads as something
   somebody decided, with the reason attached** (§2.27.4).

It is a conforming table producer, so it takes `table_contract.md`'s
Scope row AT BIRTH (SW17, r57 S-M7) — the D94 failure verbatim if
skipped, and this note has now had that shape pointed out to it twice.
**And the Scope row is not the whole of it** (r59-B-N6): the contract
has ONE IMPLEMENTATION in the tree, `tests/lib/table.sh`, whose own
header names the `NF != 15` incident as the reason it exists — *"each
had hand-rolled its own copy of 'resolve this dump's shape' rather than
sharing one"*. **So `--list-schema`'s own structural check routes
through `table_col_index`/`table_check_truthfulness` rather than
hand-rolling a positional read**, and the spec row and the shared
helper land together. A producer that adopts the contract in prose and
hand-rolls its consumer in awk has adopted half of it — which is
precisely the half the incident was in.

### 1.7 What the harness gains (legs B and C)

| # | leg B (`run.sh`) | leg C (`verify_rxt.py`) |
|---|---|---|
| 1 | **the ATTACHMENT arm** — compute a line's parent from its indent BEFORE dispatching its first token, consume children for a kind that admits them, raise the two refusal arms (attaches-to-nothing; parent-takes-no-children) | the same, replacing the flat indentation REJECTION at `:424-427` |
| 2 | **the DIAGNOSTIC CLASS tag** — the four classes `structure-attachment`, `unknown-token-in-scope`, `schema-constraint`, `value-shape`. **This is the bigger of leg B's two jobs and the design says why**: leg B refuses every unrecognised line by catch-all fall-through (`:2105-2109`) with one sentence, so a VERDICT-only differential reads "all three legs refuse" for a rule leg B has never heard of (§2.25.5, r57 S-S8) | the same four classes on its `ValueError` catch-all (`:613-614`) |
| 3 | **child CONSUMPTION for `provenance`, `variant`, `ext`, and any prose value.** `ext` is the CHEAPEST of the three: consuming a tree nobody validates is consumption with no dispatch at all | the same |
| 4 | **the STEP 0 parity refusals** (§1.8) | the same |
| 5 | the block-scoped W23 arms; `@file:` subjects; `mc`'s find-all; `under` as a counted, labelled SKIP (scoring is the consumer's, §2.17); cells; `use` | the same, plus `mc` verified by the PROTOCOL loop in python and **never `finditer`** (§2.21) |
| **6** | **`include` DISCOVERY, SUBTRACTION and SPLICE — §1.10, step W23.3a.** Revision 1 put "include discovery" in row 5 above while §1.1 said legs B and C gain no head arms, and the two sentences were never reconciled; the reconciliation is §1.1's first bullet (it is not a head arm — the fragment list is read off the `--list-source` call the leg already makes) and the mechanism is §1.10 | the same, through its own `discover` (`verify_rxt.py:715`) |

**`under` is a counted, labelled skip and not a silent one**, because
AR-3's failure mode is exactly a skip nobody counted. **`mc`'s rule is
`match_api.md` §3.1's shipped protocol BY REFERENCE**, which is W23-F3's
resolution: the bench's own find-all formula `pos = max(end, pos+1)`
DOUBLE-COUNTS an empty match found beyond the scan position (`(?=a)` on
`"xax"`: 2 against 1), so the format cites the protocol rather than
restating a formula.

### 1.8 FOLD-IN 1 — the LEGS B/C PARITY FIX for STEP 0's refusals

**The `rxtnul` lane closed two silent-loss defects in leg A only, said
so in its own report, and named the parity gap rather than leaving it
to be discovered.** **CITED**, `docs/dev/lanes/rxtnul_report.md:140-155`
("What is NOT fixed, named rather than left to be discovered"):

- A **NUL byte** is silently DROPPED by bash's own `read` in leg B, and
  silently REPLACED WITH A SPACE by leg C's decoder.
- A **duplicate block-level `description`** is silently resolved
  LAST-WINS by both legs — the exact pre-fix leg A behaviour.

The lane's three new fixtures therefore use the single-leg
`check_refusal` (**MEASURED**, `run_rxtsource_tests.sh:1362-1386`)
rather than `check_refusal_all3` (`:1492-1507`), and the asymmetry is
stated in that script's comments and in `tests/rxtsource/CLAUDE.md`.
`dup_block_name.rxtin` is the contrast: both legs already detect it
independently, so it uses `check_refusal_all3`.
**Two of the three are HEADLESS and one is not**, which is the
distinction item 5 below turns on and which revision 1 did not draw.

**W23 SCHEDULES THE PARITY FIX, in step W23.2, and the reason it
belongs THERE rather than anywhere else is structural**: the same step
is already teaching both legs to classify a refusal, and a refusal
neither leg can currently produce is exactly a refusal with no class.
Landing the parity fix in the step that builds the classification
machinery means the two new refusals get their class from the mechanism
rather than from a special case.

What lands:

1. **Leg B** reads file bytes in a way that does not lose a NUL, or —
   the cheaper and more honest arm — **detects one and refuses**. Bash
   cannot hold a NUL in a variable at all, so the fix is a DETECTION
   pass (`LC_ALL=C grep -q -- $'\0'` over the file, or a `tr`-based
   probe) ahead of the per-line loop, raising class
   `value-shape`. **DECIDED (6): detection, not carriage.** Making leg
   B carry NUL bytes would be a rewrite of the arm chain for a
   population of zero; making it REFUSE one restores three-leg
   agreement, which is the only property the differential asks for.
2. **Leg C** refuses an embedded NUL rather than replacing it. Its
   decoder already reads bytes, so this is a test, not a redesign.
3. **THE NUL RULE HAS ONE SCOPE IN ALL THREE LEGS: THE WHOLE FILE,
   BEFORE THE LINE SPLIT** (r59-A-M5). Leg A already works this way —
   its refusal is raised by `slurp_lines`' whole-file scan ahead of the
   split, which `nul_byte.rxtin`'s own header records — and items 1 and
   2 as revision 1 wrote them would have given leg B a file-wide
   pre-pass and leg C a DECODER-scoped test, i.e. two scopes for one
   rule. A decoder-scoped test in leg C sees a NUL inside a quoted
   subject and never sees one in a `#` comment line, a blank line's
   trailing bytes, or a head declaration the leg skips. **So: all three
   legs scan the file's bytes before any line is interpreted**, which
   is also the only scope at which the three can be COMPARED.
   **`nul_in_comment.rxtin` is the fixture that makes the divergence
   visible** (§3.2): the existing `nul_byte.rxtin` puts its NUL mid
   `pattern` line, which every candidate scope catches, so it is
   structurally incapable of discriminating between them.
4. **Both legs** refuse a second block-level `description` and a second
   head-level `description`, naming the earlier line — the same
   discipline the shipped duplicate-block-name refusal uses.
5. **TWO of the three fixtures are RE-AIMED from `check_refusal` to
   `check_refusal_all3` — `nul_byte.rxtin` and `dup_description.rxtin`,
   both HEADLESS. `dup_head_description.rxtin` STAYS SINGLE-LEG, and the
   reason is the seam ruling itself** (r59-A2). **MEASURED**: that
   fixture opens with two file-level `description` lines above its
   `pattern` block, so it is HEAD-BEARING; and `verify_rxt.py:407-417`
   refuses EVERY head-bearing file by name — *"a head-bearing .rxt file
   is not verifiable by this script in this build"* — with `description`
   itself in the `head_words` tuple at `:409-410`. Re-aiming it would
   therefore have produced a check that goes GREEN with leg C refusing
   for a reason that has nothing to do with duplicate descriptions, and
   that is the BEST case: **the moment W23-S2's class comparison lands
   (§3.1), the same re-aim goes RED**, because leg C's class is
   `unknown-token-in-scope`-shaped where legs A and B raise
   `schema-constraint`. Revision 1 scheduled both and they contradict.
   The head's duplicate-`description` refusal is a HEAD rule, the head
   has one parser, and a three-leg assertion on it is not available at
   any point in W23 — so the fixture keeps `check_refusal` and the
   script's comment says WHY in one sentence, rather than leaving the
   asymmetry looking like an oversight nobody got to.
6. **The `tests/rxtsource/CLAUDE.md` scope note is NARROWED, not
   deleted.** Its "Leg A only, deliberately" section (`:320-332`) covers
   three fixtures; two of them stop being leg-A-only at W23.2 and one
   does not. The edit removes the NUL and block-`description` halves,
   keeps the head-`description` half, and replaces the reason: today it
   reads *"out of this lane's scope (`src/parse/rxt_source.c` only)"*,
   which expires at W23.2; afterwards it reads that the head has one
   parser by ruling, which does not. **A scope note that outlives its
   scope is the staleness shape this tree keeps catching — and deleting
   a note two thirds of which is still true is the same defect with the
   sign flipped.**
7. **`single_description.rxtin` and the NUL-free twin stay as the
   accept controls.** The twin is built FROM the refusing fixture at
   test time (`tr -d '\000' < fixture`), so the two are byte-identical
   except for the byte under test — which is why it is a control and not
   a second fixture. `head_basic.rxtin` stays `dup_head_description`'s.

**Acceptance for the fold-in** (§6.2): `run_rxtsource_tests.sh`'s
`sem22`/`sem24` blocks assert all three legs and `sem25` states its
single-leg reason, **two of the three `check_refusal` calls become
`check_refusal_all3`** (**MEASURED**: the three are `:1642`
`dup_description`, `:1657` `dup_head_description`, `:1674` `nul_byte`;
the middle one stays) with their accept controls unchanged, and the
corpus census
(**MEASURED**: `CENSUS_FILES=210` / `CENSUS_BLOCKS=3936` /
`CENSUS_LINES=28943` at `:196-198`; leg B's own `RUNSH_FILES=209` /
`3933` / `28932` at `:225-227`) does not move, because the shipped
corpus has zero NUL bytes and zero blocks with two `description` lines.

### 1.9 The abi: W23 carries NO event, and here is the check on that claim

`format_design.md` §1.4 and §3.4 both state it: *no `match_api.md`
struct hunk and no abi bump anywhere in W23* — the schema is a
parser-side table and a CLI dump, aux is a parser-side production and a
dump section, and nothing either touches is emitted scaffolding.

**This note's file-by-file plan CONFIRMS that and does not discover an
unavoidable event**, which the lane brief asked to be checked rather
than assumed. The reasoning, stated as the property rather than as a
list:

- D76's ritual fires on **emitted scaffolding** — the text
  `src/gen/` writes into a generated `.c`. §1.2's table opens no file
  under `src/gen/`, `src/ir/`, `src/opt/` or `lib/pcrec.h`.
- The two files that look like they might and do not: **`cli/main.c`**
  (F6, F9) emits no scaffolding — it dispatches dumps and passes a
  decode flag; and **`tests/harness/driver.c`** (F13) is the HARNESS's
  driver, which LINKS AGAINST a generated matcher and is not part of
  one. `w1_impl.md`'s own F13 row treats it the same way.
- The one caller-observable surface that DOES move is
  **`--list-source`'s dump shape**, and its contract is
  `docs/spec/table_contract.md` (append-only, resolved by name), not
  `abi`. SW11/SW14/SW17/SW19 are that contract's hunks.

**If any step discovers otherwise, it STOPS and escalates rather than
bumping**: the abi number has six readers found by grep
(`w1_impl.md` §8.7's command, re-run at the event), a bump re-pins the
identity gate's (B) commit, and a W23 step doing that silently would
contradict a design statement the r58 panel confirmed.

### 1.10 FOLD-IN 5 — `include`'s HARNESS HALF (H5), and why it is its own merge

**NEW AT REVISION 1.1. This is r59-B2, and it is the largest thing the
fix round adds.** Revision 1 gave `include` a leg-A step (W23.3 item 4,
among the head declarations) and gave the HARNESS nothing: no
discovery change, no subtraction, no closure accounting, no fixture, no
check, no acceptance bullet, and — the contradiction that hid it —
§1.1 saying legs B and C gain no head arms while §1.7 row 5 handed them
"include discovery" in a list of things they gain. **Under F-Q1 that is
a Tier-1 capability deferred by staging: the smuggled cut, on the
harness axis.** `include` that parses but never splices is `include`
that does nothing a set can use.

#### 1.10.1 What `include` MEANS for a leg that RUNS cases

**CITED**, `format_design.md` §2.5: *"`include <path-ref>` splices the
referenced file's **blocks** as if they had been written at that
point"*, an included file may contain pattern blocks and nested
`include` lines and nothing else, a second `include` of the same
resolved real path in one closure is REFUSED naming both sites, and
cycles are refused naming the cycle.

Leg A's obligation is therefore a PARSE obligation and it is nearly a
solved problem in the shipped tree: **MEASURED**, `lib`'s closure
machinery already exists — `lib_resolve` (`rxt_source.c:1666`),
`closure_walk`'s depth-first lib arm (`:1754-1781`) with
`closure_seen`'s resolved-real-path dedupe at `:1763`, and a parse
failure inside the closure reported against the REFERENCING line
(`:1767-1768`). `include`'s resolution is that mechanism with a
different row kind and a different body restriction, not a new one.

**Legs B and C's obligation is a POPULATION obligation and they have no
machinery for it at all.** Each one discovers `.rxt` files by a flat
`find`/glob, runs one worker per file, and prints a per-file summary.
An `include` changes three things at once for them:

1. **Which files run.** A fragment must NOT be discovered as a file of
   its own, or its blocks run twice and the population doubles.
2. **What runs in an entry.** The fragment's blocks must run AS PART OF
   the entry's own sequence, in the entry's own option scope.
3. **What the summary says.** §2.11 rule 1 makes the accounting unit
   the CLOSURE, reported under the entry's name.

#### 1.10.2 The three legs, stated ONE way

The rule is written once and each leg implements it; that single
statement is what makes the C1 differential able to compare them at
all. **The resolution happens in leg A, and legs B and C READ it** —
they never parse an `include` line, which is why §1.1's "no head arms"
survives this fold-in.

| # | the rule | leg A | legs B and C |
|---|---|---|---|
| 1 | **RESOLVE**: a `path-ref` becomes a resolved REAL PATH, `"local"` against the referencing file's own directory and `<store>` on the library path | `lib_resolve`'s sibling, against `closure_seen`'s dedupe | — (they read the resolved path out of the dump) |
| 2 | **REPORT**: an `include` head ROW carries the path AS WRITTEN in `value` (§2.24's existing head-row rule) **and the RESOLVED REAL PATH in its `name` column** | emits the row | read it off the `--list-source` call the leg ALREADY makes for the body boundary (`run.sh:1671-1675`'s H11 read, one key over) |
| 3 | **ENTRY SET**: an entry file is a discovered file that is not included by any entry in the run (§2.11 rule 2) | — | resolve every discovered file's includes FIRST, subtract the union of the included sets, and run the remainder |
| 4 | **SPLICE**: a fragment's blocks run inside the entry's own loop, at the `include` line's position | — | after the entry's own body is parsed, each fragment's blocks are parsed and appended in include order, depth first |
| 5 | **CLOSURE TALLY**: the summary reports `entry files: N` and `fragments spliced: M` (§2.11 rule 2), and a failure still prints the FRAGMENT's own `file:line` | — | both new lines; the per-failure location is unchanged |
| 6 | **NAMED-AND-ABSORBED**: a file both named on the command line and included by another entry in the same run is counted ONCE, under the includer, and the summary says `named, absorbed into <entry>` | — | the one case where the subtraction must REPORT rather than silently drop |
| 7 | **FOURTH FAILURE CLASS**: an unresolved include, a duplicate include in one closure, and a cycle are RESOLUTION failures — reported separately in the summary, and scored as a pattern-compile failure for the block (§2.11) | raises it | reports it in the new class |

**Rule 2 is the design decision of this fold-in and it needs its
reason.** `--list-source` is deliberately AS-WRITTEN — **CITED**,
`rxt_source.c:1388-1389`: *"resolution is a third thing only pcrec
does, so a resolved dump would compare pcrec's resolver against no
counterpart"*, which is why `--list-source --resolved` is named and
unbuilt. **That objection does not reach INCLUDE resolution, and the
difference is the counterpart**: definition/composition resolution is
pcrec's alone, so a resolved dump has nothing to be differentiated
against; file discovery is something ALL THREE legs must now do, so a
resolved include path has two counterparts and becomes an ordinary C1
column. The `--resolved` surface stays unbuilt and §2.24's third
declared non-coverage row is untouched.

**Rule 4's "depth first, in include order" is not a taste.** It is the
order `closure_walk` already uses for `lib` (`:1754-1778`), and a
differential whose three legs agree on the SET but not the ORDER would
compare multisets — which `run.sh --dump`'s own serial mode
(`:284-286`: *"the row order is the file order the caller gave and a
differential can compare streams rather than sorted multisets"*)
exists specifically to avoid.

#### 1.10.3 The census consequences, which are the part that bites

**The pinned corpus census is over FILES, and `include` makes "file"
and "entry" two different words.** `run_rxtsource_tests.sh:196-198`
pins `CENSUS_FILES=210` / `CENSUS_BLOCKS=3936` / `CENSUS_LINES=28943`
and `:225-227` pins leg B's own `RUNSH_FILES=209` / `3933` / `28932`.
Three facts follow, and all three are free TODAY:

- **The shipped corpus has ZERO `include` lines** (it cannot — the
  keyword is refused by name at this pin), so `entry files` equals
  `CENSUS_FILES` and `fragments spliced` is 0 at the delivered pin.
  **The pins do not move, and that is a prediction this step must
  verify rather than assume.**
- **The three §1.10.4 fixtures are `.rxtin` and therefore not corpus**
  (`run_rxtsource_tests.sh:1234-1239` copies them under `.rxt` into a
  WORKDIR), so they add no census rows either. **If the census moves at
  W23.3a, a fixture has leaked into the corpus** — `utf8k53_report.md`
  §5's own finding, one step over.
- **The census becomes a THREE-number statement once a fragment
  exists**: files discovered, files that are entries, blocks in the
  closure. The step adds the second number to the script's pin block
  with its derivation, so a later wave that adds a fragment to the
  corpus moves a number somebody wrote down rather than discovering
  that two counts disagree.

#### 1.10.4 Fixtures, and the check with a counted population

Three fixtures land at W23.3a (§3.2 carries their rows):
`include_basic.rxtin` + its fragment, `include_nested.rxtin` + two
fragments, and `include_dup_path.rxtin` (the same resolved real path
reached by two spellings). The fragments themselves are named
`*.rxtfrag` rather than `.rxtin` for one reason worth stating: a
fragment must not be COPIED into the fixture workdir as a `.rxt` of its
own, or it becomes a discoverable entry and the fixture tests the
opposite of its own subject.

**The check is W23-S7 (§3.1) and its population is COUNTED, not
sampled.** The failure mode to design against is K35's: a splice check
satisfied by a closure of zero. So W23-S7 asserts, for each fixture,
**the three legs' block counts are equal AND the entry's count EXCEEDS
its own file's block count by the fragments' own** — the second
conjunct is what makes a leg that silently spliced nothing fail. It
also asserts `fragments spliced` is the number the fixture declares in
a comment, which is the population nobody would otherwise count.

**And one assertion runs the other way**: over the SHIPPED corpus, at
this delivery's pin, `fragments spliced` must be **0** and
`entry files` must equal `CENSUS_FILES`. That is the control for the
subtraction — a subtraction bug that removed real corpus files would
otherwise show up only as a quieter suite.

#### 1.10.5 What this owes the spec, and E7's pcrec-side path

**The spec hunk is S3, and revision 1 asserted it had already landed.**
**MEASURED, and it has not**: `format_design.md:5782` labels S3 *W1* —
*"'How the harness evaluates a block' gains the **cell** notion and the
`perr` one-cell rule; the summary's reported quantities grow (entry
files, fragments, cells, resolution failures)"* — while
`docs/spec/rxt_format.md`'s own "How the harness evaluates a block"
(`:531-565`) has no cell notion, no entry/fragment counts and no
resolution-failure class; its summary paragraph at `:562-565` reports
cases passed/failed, the per-file breakdown, the compile-failure count
and the pending-vm count, and nothing else. A grep of `docs/spec/` for
`entry file`, `fragments spliced` and `resolution failure` returns
**zero**. §4.1's *"the W1-era rows S1-S11 are already landed"* is true
of the others and false of this one, which is how a spec obligation
came to be booked as discharged.

**SW20** (§4.1) carries it: the harness-evaluation section gains the
entry/fragment distinction, the closure as the accounting unit, the two
new summary lines, and the RESOLUTION failure class with its
*"scored as a pattern-compile failure for the block"* rule — the clause
that keeps `sr_refusals.rxt`'s four `perr` blocks correct whether the
resolver or pcrec said no.

**E7's pcrec-side path** (bench group E: *"the set's `content_hash`
covers the `.rxt`, every `include`d fragment and every `@file:`
subject"*). §5 books E6/E7 bench-side and that stays true of the HASH —
but the bench cannot hash what it cannot enumerate, and the format's
contribution is exactly the enumerability. It is discharged by rule 2
above plus one sentence of guidance in the outbox message: **the
closure is walked by calling `--list-source` on the entry and following
each `include` row's resolved-path column, transitively** — one call
per file, the fragments' own `include` rows carrying the next level —
**and `@file:` subject paths come out of `#section cases`** (§2.24), so
all three of E7's inputs are dump-derivable with no second parser. The
alternative — emitting the whole closure in the entry's one dump —
loses for the reason rule 2 gives: the dump is the file AS WRITTEN, and
a dump carrying another file's rows would be a resolved dump wearing
the as-written dump's name.

---

## 2. The staging — five merges, in dependency order

### 2.1 The steps

| step | what lands | why HERE | H rows |
|---|---|---|---|
| **W23.1** | the SCHEMA table, its reader, `--list-schema`, leg A's dispatch as a table walk, S0-S3 in leg A, the diagnostic CLASS tag in leg A, the cardinality decisions, the taken narrowings (TAB indentation; the ragged head body) | **everything else is written against it.** The productions in W23.3 are schema ROWS; writing them before the table exists means writing them twice. And leg A is the only leg the table touches (§2.25.4's DECLINE), so this step is self-contained by construction | H16 |
| **W23.2** | the ATTACHMENT arm in legs B and C, their diagnostic CLASS tags, child consumption, **and the STEP 0 parity fix** (§1.8) | the differential cannot compare a CLASS until two legs can produce one, and W23.3's productions are useless to check without it. It is also the only step that is pure harness, which makes its blast radius readable in a diff | H12 |
| **W23.3** | the productions — `pattern-esc` + the CLI decode flag, `provenance`, `vocabulary`, `tag`, `oracle`, `variant`, `include`, `@file:` + `as`/`sha256`, `under`, `mc`, the `freq` data block + `analysis`, `use`, **`ext`**, and §2.22's derived-identifier repair with its two comment sites | the bulk, and it is one step rather than eight because every production is a row in W23.1's table and an arm in W23.2's two legs — splitting it would mean re-opening the same three files eight times | H13, H14, H15, H6-H10, D100 |
| **W23.3a** | **`include`'s HARNESS half** (§1.10): entry-set subtraction in both legs' discovery, the splice, the closure tally, the two summary lines, the fourth failure class, three fixtures, W23-S7 and S247 | **NEW at revision 1.1 (r59-B2).** It comes after W23.3 because a leg cannot read an `include` row out of a dump before the keyword parses, and it is its OWN merge rather than a W23.3 commit because it changes `run.sh`'s FILE DISCOVERY (`:293-307`) — the one loop every other section of `make test` inherits. A discovery bug is a population bug, and a population bug is quiet | — |
| **W23.4** | `--list-source`'s appended columns, the new head row kinds, **the four `#section` blocks**, and **the FORMAT-READER SURVEY as a landing condition** (§1.5) | it must come AFTER the productions, because a section with no rows is not emitted (§2.24's unconditional-when-non-empty rule) and there would be nothing to survey against. It is its own step because **R5's AND R6's** repairs are a real change to the tree's most load-bearing differential | — |
| **W23.5** | the remaining fixtures, the six sabotage rows, the spec hunks not already carried, and the BENCH ACCEPTANCE DRY RUN (§5) | the only work that is genuinely last: §3.3's population check needs every `all-readers` row to exist, and §5's 41 checks need the whole delivery | — |

**Fixtures, sabotage rows and spec hunks travel with the step that
makes them true** (D80, and `w1_impl.md` §7.1 item 7's rule that a row
lands in the SAME COMMIT as the code it detects). W23.5 carries only
what is genuinely cross-cutting. §3.2 and §3.5 name the step per row.

### 2.2 What each step must NOT touch

Stated as a negative because a step that quietly reaches forward is how
a five-merge rollout stops being five landable pieces:

- **W23.1 touches no leg but A**, and no production. It may not add
  `tag` or `ext` arms — only their ROWS, marked with their `wave`, so
  SW13's refusal list is derived and correct at the intermediate pin.
- **W23.2 touches no `src/`** except the diagnostic-class tag's shared
  enum (which W23.1 landed). If it finds itself editing
  `rxt_source.c`'s grammar, the step boundary is wrong and the manager
  hears about it.
- **W23.3 touches no dump SHAPE.** New productions appear in
  `--list-source` at W23.4; until then they parse and are simply not
  reported. **This is deliberate and it is the step boundary's whole
  value**: R5's repair and the section emission land together, so the
  differential is never red for two independent reasons at once.
- **W23.3a touches no `src/`, no production and no dump SHAPE.** It is
  the two harness legs' discovery and accounting only. If it finds
  itself editing `rxt_source.c`, the `include` row it needs is missing
  from W23.3 and the boundary is wrong.
- **W23.4 adds no production and no refusal.**
- **No step bumps `abi`** (§1.9).

### 2.3 The partial-build contract, and the `wave` column's one real service

At every intermediate tree, some W23 keywords parse and the rest must
refuse **BY NAME**. **MEASURED, the gap this closes**: `vocabulary`
reads *"not a file-level directive"* on today's binary — the K14 shape,
sending a reader hunting a typo in a word that is in the spec.

`refuse_wave` exists already (**MEASURED**, `rxt_source.c:677-685`),
and W23.1 re-bases it on the schema's `wave` column so the list is
derived. The contract each step signs:

1. A keyword whose row exists but whose step has not landed refuses by
   name with its wave.
2. `version` refuses by name in every build, forever — reserved without
   a production (§1.6.3).
3. The three legs agree on (1) and (2), which is a C1 assertion at
   every intermediate pin and not only at the last one.

**The honest limit, restated from §2.25.2 so nobody re-argues it**:
after W23 lands the `wave` column's population is ONE value and its
consumer is dormant until the next wave. It is kept because the rollout
is when SW13's rule matters, and the permission to drop it later is
already written.

---

## 3. The check and sabotage plan

**Read `docs/dev/learnings.md` §3 before adding a row to this section.**
The three failure shapes it names are all live here: a control sharing
a SOURCE with what it controls (the schema table is leg A's, so a check
that reads the table to verify leg A checks nothing — §3.3's population
check reads the DUMP); a population nobody counts (K35 — §3.4's aux
identity check is written against exactly that hazard); and a witness
that stopped reaching its site ([MECH-REACH] — §3.2's `indent_pre_body`
position is the check, and a post-body fixture reports GREEN against
the defect it exists to pin).

### 3.0 The denominators, and they differ on purpose

- **C1** (the three-leg differential) asserts the full corpus:
  **MEASURED, 210 files / 3,936 blocks / 28,943 expectation lines**
  (`run_rxtsource_tests.sh:196-198`).
- **C2** (leg B's own run) asserts **209 / 3,933 / 28,932** (`:225-227`)
  — leg B excludes one known-fail file.
- **C3** asserts `verify_rxt.py`'s OWN discovery, never either of the
  above.

**Every one of those three numbers MOVES in this delivery**, because
W23.3 and W23.5 add fixtures and §3.2's nineteen `.rxtin` files are
deliberately NOT corpus (the `.rxtin` extension is why — **MEASURED**,
`run_rxtsource_tests.sh:1234-1239` copies them to `.rxt` in a WORKDIR
so `find tests -name '*.rxt'` never picks them up). So the census should
NOT move on fixtures alone, and **if it does, that is a finding about a
fixture that leaked into the corpus** — which is exactly the defect
`utf8k53_report.md` §5 records the rxtsource census catching once
before.

### 3.1 The three-leg differential at W23 — and CLASS, never verdict

C1 extends. Five new assertions, each named so a sabotage row can cite
it:

| id | what it proves | its source | what it must NOT share |
|---|---|---|---|
| **W23-S1** | the three legs recover the SAME TREE from a file with attachment, sub-blocks and an open subtree | three independent dumps of parent/child/depth | leg B's tree is built by bash, leg C's by python, leg A's by the schema walk — three implementations of ONE written specification (§2.25.5), which is the most this instrument can be and is stated as such |
| **W23-S2** | the three legs agree on the **DIAGNOSTIC CLASS** of every refusal in §3.2's table | the class TAG, not the exit code and not the sentence | a verdict-only comparison is satisfiable by accident on a population of one message, because leg B refuses everything identically (§2.25.5). D26 is untouched: the class is a tag the check reads, never a sentence a human reads |
| **W23-S3** | `--list-schema` agrees with what leg A ENFORCES, column by column | the dump vs. a BEHAVIOURAL probe per row | it must not compare the dump to the table — that is the same source twice. S-R3 is the plant |
| **W23-S4** | **no `#section` row's field 1 equals any main-table `kind` token** (§1.5's DECIDED (4)) | the dump's own header lines, walked | a hand-written list of section names would go stale the day a fifth section lands — the exact `NF != 15` shape one level up |
| **W23-S5** | every `validated_by: all-readers` row is **REACHED BY A THREE-LEG INVOCATION** | `--list-schema`'s output walked against per-fixture RECEIPTS emitted by the three-leg helper itself | §3.3 — and it must NOT read a declared fixture NAME, which is [MECH-REACH] stated backwards |
| **W23-S7** | `include`'s CLOSURE: the three legs run the same blocks, the entry's count EXCEEDS its own file's, and `fragments spliced` is the number the fixture declares | three independent runs plus the fixtures' own declared counts | leg B's subtraction is bash and leg C's is python; **the corpus arm (0 fragments, entries == `CENSUS_FILES`) is the control on the subtraction itself** (§1.10.4) |

**W23-S2 is the delivery's load-bearing instrument and the one most
likely to be built wrong.** The failure mode to design against: a class
tag that leg B derives from the same arm that produced the message, and
leg A from a lookup — then the two agree because both are reading one
implementation's opinion twice. The tag must be attached **at the rule
that fired**, in each leg independently, and the fixture table (§3.2)
is what makes disagreement observable.

**W23-S3 NEEDS A DENOMINATOR IT DOES NOT GET FROM THE DUMP** (r59-A-M7).
The check iterates `--list-schema`'s rows and probes each one's
behaviour — so a row that is MISSING from the dump is invisible to it,
and after W23.1 there is no third source to compare against: the
parser's kind set IS the table. Two candidate denominators, and the
first is the one to build:

1. **A COMPILE-TIME TOTAL from the exhaustive switch.** `rxt_schema.c`'s
   one `default:`-less switch (F3) already forces a compile error when a
   constraint kind is added; the same file computes `PCREC_RXT_NROWS`
   from the `.def` at compile time and `--list-schema` prints it in a
   trailing comment line. W23-S3 asserts `rows printed == NROWS`. A
   dropped row then fails the check rather than shrinking its
   population, and nothing is hand-maintained.
2. A PINNED count with a re-pin ritual — rejected, because it is a
   number in a second place, and this delivery already has enough of
   those.

**The one thing it must not be** is "the number of rows the dump
emitted", which is what an un-denominated iteration silently is: a
check whose population is defined by the thing it checks agrees with a
truncated table by construction.

### 3.2 FOLD-IN 2 + 4 — the A3/A4 fixture plan, with the r57 probe cells and the owed EXTENT fixture

**Every row is `format_design.md` §9.1's, verbatim in substance**, plus
one the design's own fix round named as owed and deliberately did not
add. Every fixture lands in `tests/rxtsource/fixtures/` as `.rxtin`
(**MEASURED**: 46 files there today). **Every three-leg assertion
compares DIAGNOSTIC CLASS, never exit code.**

| fixture | step | position | asserts | provenance |
|---|---|---|---|---|
| `indent_pre_body.rxtin` | W23.2 | an indented `m` line **BEFORE the first `pattern`** | all three refuse, class `structure-attachment` | **THE POSITION IS THE CHECK** (r57 S-M5). Leg C's `:424` test is unconditional once a block is open; its pre-body dispatch is the only place the ordering defect is reachable. A post-body fixture reports GREEN against the defect it exists to pin |
| `indent_under_m.rxtin` | W23.2 | an indented line under an `m` case line, mid-block | all three refuse, class `schema-constraint`, naming the PARENT (`m` declares `children: none`) | S-R1's detector: flipping `m`'s `children` makes leg A accept while B and C refuse, so only the DIFFERENTIAL sees it |
| `prose_hash.rxtin` | W23.1 | an indented `#` inside a `description \|` body | all three ACCEPT; all three decode the `#` line AS PROSE | **r57 grammar-lens PROBE CELL**, reproduced at §0.8. §1.6.1a candidate (2), a narrowing AVOIDED by S3 — it pins the AVOIDANCE, which is what a decision needs and an accident does not |
| `prose_ragged.rxtin` | W23.1 | prose lines at differing depths inside a `description \|` body | all three ACCEPT and agree on the decoded value, relative indentation preserved | §1.6.1a candidate (3); S-M1's owed fixture — no fixture carried a ragged prose body before |
| `prose_dedent.rxtin` | W23.1 | a prose line indented LESS than the block's first continuation | **ASSERTS TODAY'S WRONG DECODED VALUE, with a comment naming K57 — so it goes RED the day K57 is fixed** (manager ruling **r59-R4**, §7.3). Three legs, agreeing on the truncated value | the shipped strip is a BYTE COUNT, so content is lost silently at exit 0 |
| `config_tab_body.rxtin` | W23.1 | a TAB-indented `config` body | all three REFUSE, class `structure-attachment`, the diagnostic naming the tab | **r57 grammar-lens PROBE CELL.** §1.6.1a narrowing (4), TAKEN — accepted today at rc 0, so this fixture IS the narrowing's regression |
| `config_mixed_indent.rxtin` | W23.1 | a `config` body mixing a 2-space line and a TAB line | all three REFUSE, same class | the case that shows the tab rule is not cosmetic: parses FLAT today at rc 0, and has no defined tree under any depth rule |
| `comment_in_config_body.rxtin` | W23.1 | a column-1 `#` between two indented `config` body lines | all three REFUSE **at the line BELOW the comment**, class `structure-attachment` | the comment TERMINATES the body (r57 R2-F2), measured rc 1 today. Stops a future reader implementing the transparent reading |
| `comment_in_prose_region.rxtin` | W23.1 | a column-1 `#` between two prose lines of a `description \|` body | all three REFUSE at the line BELOW, same class | the sharper of the pair: under the transparent reading this file produces an opener with TWO DISJOINT prose regions, which S3's single-extent rule cannot express at all. **A shape the specification cannot describe needs a fixture, not a sentence** |
| `prose_paragraph_break.rxtin` | W23.1 | an indented WHITESPACE-ONLY line between two prose paragraphs | all three ACCEPT and agree on the decoded value, **which CONTAINS the empty break line** | §1.6.1a candidate (6): the format's ONLY paragraph break. Asserting the VALUE is what catches the failure mode — a reader that ends the region there still "accepts" the file, it just loses the second paragraph |
| `ws_only_line_positions.rxtin` | W23.1 | whitespace-only lines at FOUR positions: between case lines, in a `config` body, as the file's FIRST line, and immediately after a blank | all three ACCEPT, and the parse is IDENTICAL to the same file with those lines deleted | the INERT half of the rule. The existing `whitespace_only_line.rxtin` (`sem15`) covers position one only; the other three are where the rejected "attachment-relevant" reading would have refused |
| `block_scalar_in_body.rxtin` | W23.1 | **EXISTING — re-aimed, not deleted** | inverted from "all three refuse" to "all three accept and agree on the DECODED VALUE" | §1.2.5's widening; SW16 carries it. A three-way agreement on a VALUE catches more than one on a rejection |
| `prov_adapted_no_adaptation.rxtin` + `prov_verbatim_no_adaptation.rxtin` | W23.3 | a `provenance` sub-block under a pattern block | the first refused (class `schema-constraint`), the second ACCEPTED | S-R2's **pcrec-side** detector (r57 S-M3). The bench's C5/C6 test the same rule in the OTHER repo and cannot turn this repo's matrix red |
| `derived_call_collision.rxtin` | W23.3 | `(?&x_y)` with `x_y` AND `x-y` both defined | refused, naming BOTH definitions and the shared identifier | **r57 probe cell**; §1.6.1a narrowing (5) — accepted today with a byte-identical artifact, so this fixture is that narrowing's regression. **Leg A only**: legs B and C resolve no calls |
| `mc_illformed_utf8.rxtin` | W23.3 | an `mc` over an ill-formed UTF-8 subject under `-e utf8` | the driver's C loop, `verify_rxt.py`'s python loop and the count AGREE | SW7's newly-normative advance rule (from `pos + 1`, skip `0x80`-`0xBF`), because `match_api.md` §3.1.1 never defines "character boundary" on invalid input |
| `aux_arbitrary_keys.rxtin` | W23.3 | an `ext bench` block at FILE scope whose keys are nothing pcrec has ever heard of | all three ACCEPT; leg A's `--list-source` reproduces every key and value VERBATIM in `#section aux` | §2.27's whole promise in one cell, S-R6's first detector. **An ACCEPTANCE fixture on purpose**: aux's failure mode is pcrec deciding it understands something, which an acceptance fixture catches and a refusal fixture cannot |
| `aux_deep_tree.rxtin` | W23.3 | an `ext bench` body three levels deep whose keys deliberately COLLIDE with real format keywords (`pattern`, `m`, `provenance`, `config`) | accepted; **and the dump contains NO extra block, NO extra case and NO provenance record** — the colliding keys appear only as `#section aux` rows | the sharper of the pair: the first catches aux being NARROWED, this one catches aux being INTERPRETED. **At 3.4 it asserted something the SPECIFICATION contradicted** (S2 ranged over siblings at any depth); the fixture was right and the rule was wrong, and it is now parameter 3's first regression |
| `aux_literal_pipe.rxtin` | W23.3 | an aux line whose value is a trimmed bare `\|` (`separator \|`), with an ordinary sibling key below it at the SAME indent | accepted; `#section aux` carries a row whose `value` is the single byte `\|`, and the sibling below it is a SIBLING ROW — not a continuation, not prose | REPLACES 3.4's `aux_prose_value.rxtin`, which asserted the opposite. **Falsifiable exactly here**: if S3 still opens inside an open subtree, the `\|` row's value is empty and the sibling has been swallowed |
| `aux_malformed_body.rxtin` | W23.3 | an `ext bench` block one of whose body lines is mis-indented so it attaches to nothing, followed by an ordinary `pattern` block | all three REFUSE, class `structure-attachment`, naming the MIS-INDENTED LINE — **and the `pattern` block below is not implicated** | D99's parenthesis as a check. **The assertion that matters is the second half**: a refusal that names the right line proves the error is LOCAL, which is the entire argument for structural parsing over opaque bytes |
| **`aux_subtree_extent.rxtin`** | **W23.3** | **an `ext bench` block whose body ends and is FOLLOWED, at indent 0, by an ordinary head declaration and then a `pattern` block whose own `m` line uses a key spelled identically to one inside the aux body** | **all three ACCEPT; the declaration after the block is a DECLARATION and not an aux row; the `pattern` block is a block; and `#section aux` contains exactly the body's own lines and no more** | **NEW, AND IT IS THE ONE §9.1 DOES NOT HAVE.** `w23fix3_report.md` §5 names it: *"§9.1's plan has no fixture for an open subtree's own EXTENT (where it ends). `aux_malformed_body` probes an attachment error INSIDE the subtree, not the boundary at its foot."* §5.2a item 5 lists it among the known-weak points, and item 9's sharpest attack is *"construct a file where the open subtree's extent under S1 differs from what `--list-source` reports"* — **this fixture IS that attack, run by the delivery on itself** |

| **`nul_in_comment.rxtin`** | **W23.2** | **a NUL byte inside a `#` COMMENT line of an otherwise-valid headless file** | **all three REFUSE, class `value-shape`** — and the NUL-free twin (`tr -d '\000'`) is ACCEPTED, the existing fixture's own control shape | **NEW at revision 1.1 (r59-A-M5).** The shipped `nul_byte.rxtin` puts its NUL mid `pattern` line, which EVERY candidate scope catches — file-wide pre-parse, per-line, decoder-scoped — so it is structurally incapable of discriminating between them and cannot pin §1.8 item 3's one-scope rule. A comment line is the cheapest position no line-interpreting scope reaches |
| **`include_basic.rxtin`** + `include_basic_frag.rxtfrag` | **W23.3a** | **an entry with one `include "…"` above its own `pattern` blocks** | **all three run the ENTRY's blocks AND the fragment's; the three block counts are EQUAL; the entry's count EXCEEDS its own file's by the fragment's; `fragments spliced: 1`; the fragment is NOT an entry** | **NEW at revision 1.1 (r59-B2).** The four assertions are separate on purpose: equal counts alone are satisfied by three legs that all splice nothing (K35), and a non-zero count alone is satisfied by a fragment discovered as its own entry — the defect the subtraction exists to prevent |
| **`include_nested.rxtin`** + two `.rxtfrag` | **W23.3a** | **an `include` whose fragment `include`s a third file** | **depth-first, include order, all three legs agreeing on the ORDER and not merely the set; `fragments spliced: 2`** | order is asserted because `run.sh --dump`'s serial mode exists to compare STREAMS rather than sorted multisets (`run.sh:284-286`), and a closure walk is the first thing in W23 that can reorder one |
| **`include_dup_path.rxtin`** | **W23.3a** | **the same resolved real path reached by two different spellings in one closure** | **all three REFUSE, class `schema-constraint`, naming BOTH sites** — §2.5's rule, and the RESOLUTION failure class (§2.11) is what it is reported under | the two alternatives §2.5 names — splice twice, or silently ignore — respectively DOUBLE a population and HIDE one, which is why this fixture asserts the refusal rather than a count |

**`aux_subtree_extent.rxtin` is the fold-in the brief asked for and it
is worth one
more sentence, because its ABSENCE had a reason and the reason has
expired.** The design's fix round declined to add it, correctly, on the
ground that *"the fixture table is the implementation lane's to grow
and the gap is now named where a critic looks."* This note is that
lane's plan, so the row lands here. Its assertion is deliberately
POSITIVE on three different things (the declaration, the block, the
section's contents) rather than negative on one: an extent bug that
swallows the next declaration and an extent bug that closes early
produce opposite symptoms, and a fixture asserting only "the file is
accepted" sees neither.

**THE POPULATION CHECK is what does not go stale** (§3.3).

### 3.3 The `all-readers` population check

A check walks `--list-schema`'s OWN OUTPUT, selects every row with
`validated_by: all-readers`, and **fails naming any row with no
fixture** in §3.2's table. Three properties earn it:

1. It reads the same table the parser enforces, so a row added in a
   later wave fails the check the day it lands rather than the day
   somebody remembers.
2. **WITHDRAWN AT REVISION 1.1 — it was [MECH-REACH] STATED BACKWARDS**
   (r59-A-M1). Revision 1 claimed the check *"cannot be satisfied by a
   fixture that stopped reaching its site, because it counts ROWS
   against fixture NAMES declared per row"*. **A declared name is
   exactly what a witness that stopped reaching its site still has**:
   the fixture file exists, the row still names it, and the check is
   green while the three-leg assertion it stands for has silently
   stopped running — a call site commented out, a `.rxtin` that no
   longer copies, a helper whose early return skips it. Counting names
   measures the TABLE, not the RUN.
   **What replaces it: the check reads the INVOCATION.** The three-leg
   helper (`check_refusal_all3` and its accept-side sibling) emits one
   RECEIPT line per fixture it actually ran, naming the fixture and
   which legs answered; W23-S5 walks `--list-schema`'s `all-readers`
   rows against the RECEIPTS and fails naming any row with none. The
   receipt is written by the code path that does the work, so a
   fixture that stopped being invoked stops producing one — which is
   the property revision 1 claimed and did not have.
3. It makes the honest fallback cheap: **a row whose fixture is not
   written yet takes `validated_by: pcrec`**, which is a true
   statement, instead of `all-readers`, which would be a claim about
   two parsers nothing tests.

**The third is a rule for the lane and not just for the check**: W23.3
will land productions faster than W23.5 lands fixtures, and the correct
intermediate state is `pcrec` on the rows whose fixtures are pending.
A row claiming three legs on the strength of one is the failure this
rule exists to stop.

### 3.4 The AUX NON-INTERPRETATION check — clause 5 as an instrument

§2.27.3's fifth clause is stated over VALUES rather than over readers:

> Nothing in pcrec — no test, no dump summary or count, no refusal, no
> diagnostic, no selection — may take a value that CHANGES when an aux
> body changes, except the faithful per-line rows of `#section aux`
> themselves.

**That is a property of pcrec's OUTPUTS, so it is checkable in exactly
one direction and the check is cheap**: take a fixture with an `ext`
block, edit the aux body, and require **every pcrec output except
`#section aux`'s rows to be BYTE-IDENTICAL**. Concretely
(check **W23-S6**, step W23.4):

- `--list-source` with the `#section aux` block elided: byte-identical.
- `--list-schema`: byte-identical (an aux body has no rows).
- the compiled artifact for every `pattern` block in the file:
  byte-identical.
- every diagnostic the file produces: byte-identical.

**THREE THINGS REVISION 1 GOT WRONG ABOUT THIS CHECK** (r59-A-M2 +
r59-B-M3), each of which would have shipped a check weaker than its own
sentence:

**(a) The BYTE-IDENTITY CLAIM IS UNSATISFIABLE AS SPECIFIED, because an
aux edit moves LINE NUMBERS.** `--list-source`'s every row carries a
`line` column and `#section cases`' rows carry `block_line` too, so
adding one line to an aux body shifts every row below it — and the
edit §3.4 demands is deliberately one that *"changes the number of aux
lines"*. **The fixture constraint is therefore stated, not discovered:
every `ext` block in `aux_identity.rxtin` sits at the FOOT of the file,
below every `pattern` block and every declaration**, so no row's `line`
is downstream of the edit. (The alternative — a line-normalised
comparison — was rejected: it throws away the one column most likely to
carry an accretion bug.) **And the line-number movement is a NAMED
EXCEPTION to §2.27.3 clause 5, not a violation of it**: clause 5
forbids pcrec taking a VALUE that changes when an aux body changes, and
a row's own source line number is a property of the FILE's bytes rather
than of the aux body's meaning — the same number moves when a comment
is added. It is not a graduation event, because nothing has begun to
read what the aux body SAYS. Stating it here is what stops a later
reader treating the exception as precedent.

**(b) TWO OF THE FOUR ARMS ARE ZERO-POPULATION UNLESS THE FIXTURE IS
BUILT FOR THEM.** "The compiled artifact for every `pattern` block"
asserts nothing if the fixture has no `pattern` block, and "every
diagnostic the file produces" asserts nothing if the file is accepted
silently. **The fixture therefore carries a COMPILING `pattern` block
AND a refusing sibling file** (the same aux body, one block edited to a
pattern pcrec rejects), so both arms have exactly one cell each — and
the acceptance says so, rather than reporting four green arms two of
which ran over nothing.

**(c) IT GETS A SABOTAGE ROW AFTER ALL — S246 (§3.5).** Revision 1
declined one on the ground that clause 5's violation *"is not a
corruption of a mechanism, it is the arrival of a feature"*. **That
reason is refuted by §3.4's own text two paragraphs down**, which names
the two routes clause 5 exists for: an opener-row CARDINALITY and a
derived COUNT. Both are one-line defects in shipped code — flip the
`ext` rows' `cardinality` from `repeat` to `at-most-one`, or count aux
openers into `a_blocks` — and neither is a feature anybody would write
on purpose. The honest residual survives and is stated at §3.5: a plant
that makes some output depend on an aux body's CONTENT is still a patch
somebody writes deliberately, and no row covers that.

**Why this is the right instrument and a reading of the code is not.**
The graduation rule's failure mode is accretion — *a field everybody
writes, that one tool reads "just this once", that becomes load-bearing
without ever being specified*. A code review catches the patch that
reads an aux value; it does not catch the two routes clause 5 was added
for (an opener-row cardinality; a derived COUNT pinned in CI), because
neither reads an aux body at all. A byte-identity check over outputs
catches all three, because all three move a value.

**Its own limit, stated rather than tidied**: it proves the aux body
changes nothing for the EDITS it makes. It cannot prove it for edits
nobody makes. So the fixture's edit must be chosen to move as many
plausible derived quantities as it can — change the number of aux
lines, their depth, their key spellings AND the number of `ext` blocks
— which is the difference between a check with a population and a check
with an example.

### 3.5 The sabotage rows — S239 onward

**MEASURED**: the highest existing S-id on main is **S238**
(`tests/mech/sabotages/S238_size_drop_unstamped.sh`), by the procedure
`tests/mech/CLAUDE.md:649-656` states. W23's rows are **S239-S247**
(revision 1 had S239-S245; r59-A-M2(c) adds S246 and r59-B2 adds S247).
Re-check the highest id ON MAIN before numbering at each step — that
file records a past collision at S100/S101, and this delivery lands
behind five merges.

Two rules the design applied to every row and that these inherit: **a
row's detector must live in THIS repo's matrix**, and **a row must fail
on the tree it is planted into rather than on a later drift.**

| id | design row | the plant | detector | step |
|---|---|---|---|---|
| S239 | S-R1 | flip one schema row's `children` from `none` to a scope (say `m` admits children) | `indent_under_m.rxtin` — leg A stops refusing while B and C still refuse, so **only the C1 differential goes red**. Planted in the direction where leg A alone would simply accept more | W23.2 |
| S240 | S-R2 | drop `provenance`'s `required-if` constraint for `adaptation` | the pcrec-side fixture PAIR. **RE-HOMED at r57 S-M3**: the bench's C5/C6 live in the other repo, so planting this row would turn nothing red in our own battery and `make mech` would score it UNDETECTED and be right to | W23.3 |
| S241 | S-R3 | make `--list-schema` print a HAND-WRITTEN table instead of walking the enforced one — **and the copy DISAGREES on exactly one row** (it reports `provenance.fidelity` as `closed` while the parser's row is edited to `source: file` with no set) | W23-S3, the dump-vs-behaviour cross-check, widened past `closed`: a violating value for `closed`, a missing line for `required`, a present-when-forbidden line for `forbidden-if`, a conflicting re-binding for `functional-binding`, a duplicate tuple for `unique-by`, an indented line for `children`, a second opener for `opens_group`. **The disagreeing row is what makes it fail NOW** — a faithful hand-written copy detects DRIFT, and a sabotage row must fail on the tree it is planted into | W23.1 |
| S242 | S-R4a | **remove `pattern-esc` from `opens_group`** | the structure layer's own fixture: a `pattern-esc` line stops opening a block, so its case lines attach to the PRECEDING block and `#section cases`'s rows move `block_line`. The symptom is the moved `block_line` | W23.4 |
| S243 | S-R4b | **add a THIRD member to `opens_group`** (say `m`) | a DIFFERENT detector, which is why the row is split: a case-bearing fixture whose `m` lines become blocks of their own, caught by the block COUNT and by leg B's case totals. **Revision 3.1 bundled this with S-R4a and the first half was SILENT** — the opener set is consulted by first-match-wins membership, so a duplicate `pattern` row changes no answer at all, and a row that plants two things where one does nothing scores DETECTED on the strength of the other | W23.4 |
| S244 | S-R5 | **break `description`'s prose PAIR, in EITHER column**: (a) flip `value` from `prose` to `line`; (b) flip `children` from `prose` to `none` | the ragged-prose and prose-`#` fixtures. **Plant (b) is why parameter 2 reads the PAIR**: if the structure layer read `value` alone, (b) would change nothing observable anywhere — the region still opens, its lines are bytes, and bytes reach no validity check — so a normative column would carry a corruption with NO detector | W23.1 |
| S245 | S-R6 | **make an `ext` body SCHEMA-CHECKED**: flip the `ext` rows' `children` from `tree` to a named scope (say `provenance`) | **three detectors, and the third arrived for free at 3.4.1.** `aux_arbitrary_keys.rxtin` (leg A refuses what it must accept) catches aux being NARROWED; `aux_deep_tree.rxtin` catches aux being INTERPRETED — the graduation rule's failure mode as a check rather than a sentence; and because `children` is now structure-layer parameter 3, the same flip RE-ARMS S2 and S3 inside the subtree, so `aux_literal_pipe.rxtin` sees it on a STRUCTURAL axis as well | W23.3 |

| **S246** | **W23-S6** (§3.4) | **the AUX IDENTITY plant, TWO variants**: (a) flip the `ext` rows' `cardinality` from `repeat` to `at-most-one`, so a second `ext` block at one scope is refused; (b) count aux OPENER rows into `a_blocks` in `run_rxtsource_tests.sh:500`, so the block total moves with an aux edit | W23-S6's byte-identity arms. **(a)** moves the diagnostic arm (the refusing sibling file's stderr changes) and **(b)** moves a COUNT that reads an aux body's size. **NEW at revision 1.1** — revision 1 declined this row on a reason its own §3.4 refutes two paragraphs later, which is why it is written in BOTH variants: each is a one-line edit to shipped code, and they fail in different arms | **W23.4** |
| **S247** | **§1.10 / W23-S7** | **DROP THE ENTRY-SET SUBTRACTION** in leg B's discovery (`run.sh:293-307`) — every discovered file, fragments included, becomes an entry | W23-S7's fixture arms: `include_basic`'s fragment runs TWICE (once as a fragment, once as an entry of its own), so the three legs' block counts diverge and `fragments spliced` disagrees with `entry files`. **The CORPUS arm is silent by construction and that is the point** — the shipped corpus has zero `include` lines, so nothing but the fixtures can see this plant, which is the argument for the fixtures having a COUNTED population rather than an example | **W23.3a** |

**The row this plan does NOT write, and the reason is the NARROWED
one** (r59-A-M2(c) took the broad version away). S246 covers clause 5's
two named STRUCTURAL routes — an opener-row cardinality and a derived
count — because both are one-line corruptions of shipped code. What
stays uncovered is the CONTENT route: a plant that makes some pcrec
output depend on what an aux body *says* is not a corruption of a
mechanism, it is the arrival of a feature, and a `mech` row planting an
arbitrary dependency nobody would have written measures the plant
rather than the code. **For that route the check is the detector and
the review is the gate**, and §6.3's reviewable question — *"does any
pcrec output change when an aux body changes"* — is the form it takes.

### 3.6 What each check does not share a source with

The table exists because `learnings.md` §3's first line is the project's
most recurring finding class, and because three of these checks are one
edit away from being vacuous:

| check | would be USELESS against | because |
|---|---|---|
| W23-S1 (tree identity) | all three legs implementing the same wrong rule | it compares three implementations of one written spec. §2.25.5 says this plainly: the schema narrows the failure from "three disagree and none is authoritative" to "three agree against a printed rule", which is **strictly better and is not the same as correct** |
| W23-S2 (diagnostic class) | a class tag derived in both legs from one implementation | the tag must be attached at the rule that fired, in each leg independently |
| W23-S3 (dump vs behaviour) | a check that compared the dump to the TABLE | that is the same source twice. It must exercise the BEHAVIOUR the dump claims, per row |
| W23-S4 (section field 1) | a hand-written list of section names | the list goes stale the day a fifth section lands — `NF != 15` one level up |
| W23-S5 (population) | a fixture LIST maintained by hand — **and equally against declared fixture NAMES**, which is what revision 1 proposed | it walks the dump's rows against RECEIPTS the three-leg helper emits as it runs (§3.3 property 2) |
| W23-S6 (aux identity) | an edit chosen to be small; **a fixture with no `pattern` block and no refusal, which makes two of its four arms vacuous** | the edit must move line count, depth, key spellings and block count at once, and the fixture must carry a compiling block and a refusing sibling |
| W23-S7 (include closure) | a fixture pair whose counts are merely EQUAL across three legs | three legs that all splice nothing satisfy equality; the entry's count must EXCEED its own file's, and `fragments spliced` must equal a number the fixture DECLARES |
| R5's repaired field-count assertion (§1.5) | a per-section count that DEFAULTS when a section is unknown | a detection helper that returns a default on missing input fails in the silent direction ([ABI-NS]). It hard-fails naming the section |

---

## 4. FOLD-IN 3 — the spec delta (D80), SW1-SW19 as a landing checklist

`docs/spec/rxt_format.md` is the contract and a parser landing without
its spec hunk is rejected on sight. **MEASURED**: that file is 723
lines with fourteen headings today, `## --list-source` at `:418-499`,
`### Lexical rules` at `:145`. Every row below names the step that
carries it, because D80 is a per-change rule and a table of hunks
deferred to the end is the rule's violation with extra steps.

### 4.1 The hunks, by step

| # | file(s) | the hunk | step |
|---|---|---|---|
| **SW2** | `rxt_format.md` | the LEXICAL RULES section becomes **the TWO-LAYER statement** — the STRUCTURE layer (S0's four line classes, S1 attachment, S2's two-member opener set) and the pointer to the schema for everything else. The head/body indentation asymmetry is DELETED rather than narrowed; the bare-indented-line refusal survives in its two arms; `prose-value` becomes legal wherever the schema declares a prose value, at any depth | W23.1 |
| **SW16** | `rxt_format.md` | **THE THREE-DEVICE STATEMENT, THE VERSION RULE, AND THE WHOLE NARROWING CENSUS.** (a) the ragged HEAD BODY; (b) **TAB indentation refused by name** — indentation is spaces, a tab inside a VALUE is still data; (c) the two narrowings AVOIDED and the rule that avoids them (inside a `\|` region an indented `#` is PROSE and ragged indentation is legal, while OUTSIDE one the indented-`#` refusal is unchanged); (d) the FOUR LINE CLASSES and what each does — BLANK is the EMPTY line and closes attachment, a COMMENT closes attachment and ends a prose region exactly as a blank does, a WHITESPACE-ONLY line is INERT outside a region and BYTES inside one; (e) a prose region opens on a `\|` whose trailing whitespace is TRIMMED and only for a kind the schema declares prose-region-opening — **both conditions, since without the first `description \| ` is a literal and without the second `pattern \|` is a refusal**; (f) the CARDINALITY rules for the settings kinds; **(g) THE STRUCTURE LAYER TAKES THREE PARAMETERS, and the third is the OPEN SUBTREE** — stated here, with the layer, because it is a rule a second `children: tree` production would inherit for free. Also carries `block_scalar_in_body.rxtin`'s re-aim: a shipped refusal changing DIRECTION is named in the spec, not left to a fixture diff | W23.1 |
| **SW17** | `rxt_format.md` + `cli.md` + **`table_contract.md`** + `registry.md` | **THE SCHEMA AND ITS SURFACE.** The columns (including `children: prose` and `children: tree` with structure-layer parameter 3), **the SEVEN-kind constraint vocabulary** with its membership rule, the one named parser-code exception (`under`'s key tuple), the deferred/DECLINED split, and the statement that the parser is the table's reader. `cli.md` gains `--list-schema` as the **SEVENTH** registry dump. `registry.md` gains its row **with its own numbered sequence RECONCILED** — it stops at the fifth surface while two dumps are undocumented there, so the row is added to a reconciled list rather than appended to a gap. `table_contract.md` gains its Scope row **AT BIRTH** | W23.1 |
| **SW13** | `rxt_format.md` | the "NOT IN THIS BUILD" recognised-keyword list, **DERIVED from the schema's `wave` column**, plus `version` RESERVED | W23.1 |
| **SW1** | `rxt_format.md` | `pattern-esc`: the second block starter, the seven-escape vocabulary shared with subjects, **the `\x00` refusal naming K9 and its lifting trigger**, and the CLI decode-flag cross-reference | W23.3 |
| **SW3** | `rxt_format.md` | `provenance`: the eleven fields, the per-parent required sets, the `authored` agreement rule, adaptation-iff-not-verbatim, one-per-parent, the `license`/`license-note` spelling. **Also the `freq` data block's body**: its five one-off provenance fields are REPLACED by this same record |  W23.3 |
| **SW4** | `rxt_format.md` | `vocabulary` — **and NOT `tag-prose`, REMOVED at 3.4.1 under r58 R3**: the hunk loses the quoted-tag-value paragraph with the production, so a `tag` item is a bare label or a `key=value` with no whitespace, exactly as W2 shipped it. Declaration, enforcement points (tag both scopes, `under`'s convention, `variant`'s kind), and `vocabulary`'s nesting as the FILE-declared rows of the schema. `requires` is stated as the ONE-ENDED truth: an ordinary `tag` key, closable like any other, **with no reserved status and no second end in the format** | W23.3 |
| **SW5** | `rxt_format.md` | **ONE SENTENCE, the MUST-tier half**: a file with no `target` and no `config` parses, builds nothing, and exits 0 — **as a CONTRACT, permanently.** The behaviour is already shipped; the hunk makes it a promise rather than an observation, which is the whole of the ask (bench N-43, acceptance check F1) | W23.3 |
| **SW6** | `rxt_format.md` | the subject subsection: `as <id>` / `sha256 <hex64>`, the per-file id namespace, the functional-binding rule, and WHO checks the hash | W23.3 |
| **SW7** | `rxt_format.md` + `match_api.md` | `mc` and its COUNTING RULE — one normative paragraph citing `match_api.md` §3.1 as the rule's single home, the empty-advance-from-reported-start clause, the finditer-divergence class named. **PLUS the ILL-FORMED-UTF-8 ADVANCE RULE, stated NORMATIVELY** (from `pos + 1`, skip `0x80`-`0xBF`), landing in `match_api.md` §3.1.1 where the gap is as well as in the `mc` paragraph where its consumer reads | W23.3 |
| **SW8** | `rxt_format.md` | `under`: qualifier semantics, fallback, duplicate refusal, the no-`g`/`gp` rule, the harness's COUNTED-SKIP treatment | W23.3 |
| **SW9** | `rxt_format.md` | `oracle` widened to `engine-ref [/version]`; `python`/`pcre2` meanings unchanged; absent-oracle = labelled skip | W23.3 |
| **SW10** | `rxt_format.md` | `variant` as a SUB-BLOCK: the five attributes, exactly-one-of-text/unsupported, `kind`'s vocabulary hook. **Its name is a `defname`, not an `ident`** (r58 B4 — the bench's real testees `pcre2-dfa` and `pcre2-interp` are unspellable under `ident`), validated as an identifier and as unique within its block, **and against nothing else**: cross-checking is the consumer's tooling's job, stated as a deliberate non-check | W23.3 |
| **SW12** | `rxt_format.md` **+ `rxt_source.c`'s TWO comment sites** | the `name` grammar's "cannot be called from a pattern" paragraph AMENDED: still true of the hyphenated SPELLING (D26), and the definition is now reachable through its DERIVED identifier — the mapping, the at-use collision refusal naming BOTH definitions, exact-spelling-does-NOT-win. Plus the **refuse-before-mapping LENGTH rule** and the 128-byte callability bound. **The two comment sites move in the SAME change** — **`:269-297`** (`defname_ok`'s header, the function opening at `:298`) and **`:1177-1180`** (the `name` arm's pointer, the arm opening at `:1175`), **CORRECTED at revision 1.1 from `:280-291`/`:1126-1130`, which this note inherited from the design's own SW12 row and which name a mid-comment offset and an unrelated production respectively** (r59-B-M2; `format_design.md`'s row is corrected in the same change). They state the repealed boundary AS A RULING, and D100 accepts the loss, so leaving them would put a shipped comment in direct contradiction with shipped behaviour | W23.3 |
| **SW15** | `rxt_format.md` | the driver protocol: the find-all mode, the `@<path>` subject form's byte-exactness, the sha256 mismatch refusal | W23.3 |
| **SW11** | `rxt_format.md` | `--list-source`: the appended columns, **the FOUR `#section`s with their column lists**, and the **VALIDATES vs RECOGNISES table as normative text, RENDERED from the schema's `validated_by` column rather than hand-written beside it**. `table_contract.md` needs no hunk for sections — they were already its mechanism | W23.4 |
| **SW14** | `cli.md` | the `pattern-esc` decode flag; `--list-source`'s section output named in its entry | W23.3/.4 |
| **SW18** | `rxt_format.md` + `cli.md` | **THE AUX PRODUCTION.** `ext <consumer>` at file and block scope, the consumer namespace as a free `defname` resolved against nothing, the body as ordinary indented records under the SAME structure rules as everything else, `cardinality: repeat` at both scopes, **`children: tree` and what it means for a reader — structure-layer parameter 3, so no line inside an `ext` body opens a group and no bare `\|` there opens a prose region; every aux value is one line** — and, normatively, in its own paragraph, **the GRADUATION RULE with its FIVE clauses**, plus the disambiguating sentence: *an `ext` block extends what a file CARRIES, never what the format MEANS.* It states the non-coverage in the words a consumer needs: **pcrec parses the structure, dumps it faithfully, and interprets nothing.** `cli.md` gains `#section aux`'s column list. **This hunk is the one place the format promises something by promising NOT to do it**, which is why it is spec text: a consumer who cannot cite a sentence saying "pcrec will not read this" has no basis for putting anything there | W23.3 (rule) / W23.4 (section) |
| **SW19** | `rxt_format.md` + `table_contract.md` | **THE WITHDRAWALS' SPEC CONSEQUENCE, which is mostly an ABSENCE and is named so the absence is CHECKABLE** (§4.3). Plus `table_contract.md`'s `#section aux` Scope row, and **the FORMAT-READER SURVEY as a landing condition** | W23.4 |

| **SW20** | `rxt_format.md` | **`include`'s HARNESS CONTRACT — this is the W1-era row S3, WHICH HAS NOT LANDED** (§1.10.5, r59-B2). "How the harness evaluates a block" (`:531-565`) gains: the ENTRY/FRAGMENT distinction and the rule that an entry is a discovered file no entry includes; the CLOSURE as the accounting unit, reported under the entry's name, with a failure still printing the FRAGMENT's own `file:line`; the two new summary lines (`entry files: N`, `fragments spliced: M`) and the `named, absorbed into <entry>` line; and **the FOURTH FAILURE CLASS, RESOLUTION failure** — reported separately and scored as a pattern-compile failure for the block, which is the clause that keeps `sr_refusals.rxt`'s four `perr` blocks correct whether the resolver or pcrec said no. Also: the `include` head row's RESOLVED-path column, and why it is not `--list-source --resolved` (§1.10.2 rule 2) | **W23.3a** |
| **SW21** | `cli.md` | **THE DIAGNOSTIC CLASS STRUCTURE, under manager ruling r59-R1.** A NEW ROW rather than an extension of SW2, and the reason is which document it lands in: SW2's hunk is `rxt_format.md`'s LEXICAL RULES — the format's own grammar — while a diagnostic emitted on stderr in a stable machine-parseable position is a property of the **CLI's output contract**, which is `cli.md`'s. Folding it into SW2 would have put a CLI surface in the format spec and left `cli.md` silent about a channel callers parse. The hunk states: the four class tags (`structure-attachment`, `unknown-token-in-scope`, `schema-constraint`, `value-shape`), that the tag's POSITION is stable and its SET is closed, and — D26 explicitly — that the sentence beside it is not a contract | W23.1 |

**The W1-era rows S1-S11 are MOSTLY already landed, and revision 1's
"already landed" was a claim about the set that was false of one
member** (r59-B2): **S3 has NOT landed** and is SW20 above —
`format_design.md:5782` labels it W1 and `docs/spec/rxt_format.md`'s
harness-evaluation section has none of what it promises (**MEASURED**:
`docs/spec/` contains zero occurrences of "entry file",
"fragments spliced" or "resolution failure"). S4/S5/S6/S7/S8 were
labelled W2/W3 and land in this delivery inside SW6/SW15/SW3/SW9/SW10
above rather than as separate rows, because their productions are the
same productions. **Two rows have no W23 work**: S9/S9b (`match_api.md`
§6) — W23 carries no abi event and changes nothing about `rx_info`.
**The general lesson, and it is this round's cheapest**: a row's WAVE
LABEL says when it was scheduled, never whether it shipped; the only
way to book a spec row discharged is to read the spec.

### 4.2 SW18/SW19 carry the dump-shape obligation, and it is a LANDING CONDITION

**CITED**, SW19: *"the implementation lane greps the tree for every
site parsing `--list-source`'s SHAPE (field counts, positional splits,
section-presence assumptions) before landing the fourth section."*

§1.5 is that grep, run. **The landing condition for W23.4 is that the
survey is RE-RUN at the step's own pin and its output — not §1.5's
table — is what the commit answers to.** The table will be stale by
then: W23.1 through W23.3 add checks, and a check added in this very
delivery is exactly the kind of reader a survey written before it
cannot contain. That is `w1_impl.md` §8.7's discipline applied to a
shape instead of to a number: **the command is the contract, not the
list.**

### 4.3 The withdrawals' absence, made checkable — RE-MEASURED AT 1.1

SW19's shape, and this note adopts it rather than writing disposition
prose about mechanisms that do not exist.

**REVISION 1'S MEASUREMENT WAS WRONG IN BOTH DIRECTIONS AND ITS LANDING
CONDITION WAS UNSATISFIABLE** (r59-B-M1, extended by this round's own
re-measurement). It claimed a naive grep for `configs describe`,
`configs build`, `provides`, `capable` and `cross-scope` returns **0**
over `docs/spec/`, `src/` and `tests/`, and made "that grep returns 0"
the landing condition at every step. **MEASURED, at this revision's
pin, on the untouched tree:**

| token | `docs/spec/` | `src/` | `tests/` | `cli/` |
|---|---|---|---|---|
| `configs describe` / `configs build` | 0 | 0 | 0 | 0 |
| `provides` | 0 | **2** | **1** | 0 |
| `capable` | 0 | **2** | **12** | 0 |
| `cross-scope` | 0 | 0 | 0 | 0 |

Every one of the seventeen hits is ORDINARY ENGLISH — *"structurally
incapable of moving"*, *"a UCP-capable surface"*, *"provides the names
it intends to export"* — so the grep as written can never return 0 and
a step signing the checklist line would be signing a falsehood or
deleting prose to satisfy a check.

**AND THE ERROR RUNS THE OTHER WAY TOO, WHICH IS THE PART THE REVIEW
DID NOT REACH: revision 1 grepped the wrong five tokens.** The
withdrawals are FOUR productions — `configs build`/`describe`,
`provides`, and `config`-body `testee`/`option` (N-42) — and
`testee`/`option` were never in the grep. **They are LIVE FORMAT
SPELLINGS in the shipped tree, at three sites:**

1. **`src/parse/rxt_source.c:149`** — `config_vocab` carries
   `{ "testee", 3 }, { "option", 3 }`, so leg A RECOGNISES both today
   and refuses them by name with their wave.
2. **`docs/spec/rxt_format.md:57-62`** — the later-wave keyword
   paragraph names `testee` and `option` among the keywords that are
   *"recognised and refused by name, as NOT IN THIS BUILD"*. The
   withdrawal is therefore a SPEC EDIT, not merely an absence.
3. **`tests/rxtsource/run_rxtsource_tests.sh:1188`** —
   `CENSUS_WORDS_32` lists both, and the list's LENGTH is asserted
   against the literal `32` at `:1200-1206` with a failure message
   reading *"It is format_design §1.1's list verbatim; if it changed,
   say so there too."* So removing them moves a word list, a count pin,
   and the design section the pin cites.

**So the withdrawal does NOT cost "a diff and nothing else".** For
`configs` and `provides` it does — neither ever shipped. For
`testee`/`option` it costs four sites (parser row, spec sentence,
census word list, census count `32 → 30`) plus the §1.1 list the census
cites, **and it carries a deliberate narrowing that needs its own
sentence**: a `.rxt` file writing `testee` in a `config` body goes from
*"NOT IN THIS BUILD, the keyword is real"* to *"not a config
directive"*. That is correct — the keyword is no longer real — but it
is the K14 shape running in reverse, and SW19's hunk says so. **W23.1
carries the parser row and the census; SW19 carries the spec
sentence.** MEASURED: no `.rxt` or `.rxtin` file in the tree writes
either word in first-token position (0 over 262 files), so no corpus
file changes meaning.

**The landing condition, restated as something a step can actually
satisfy.** Three arms, and the third is deliberately not a grep:

- **(a) THE DATA ARM** — no `.rxt`/`.rxtin` file has a line whose first
  token is `configs`, `testee`, `option`, `provides` or `capable`:
  `grep -lE '^[[:space:]]*(configs|testee|option|provides|capable)([[:space:]]|$)'`
  over `git ls-files '*.rxt' '*.rxtin'`. **MEASURED 0 of 262 today**,
  and it stays 0 because these are not productions any more. No English
  hazard: a first token is a keyword position.
- **(b) THE PARSER ARM** — none of the three legs' keyword tables or
  dispatch arms names one, spelled as each leg spells a keyword (a
  quoted token in `rxt_source.c`, a `^`-anchored `=~` in `run.sh`, a
  `startswith`/tuple member in `verify_rxt.py`), plus `cli/main.c`.
  **MEASURED 1 today — `rxt_source.c:149`, the two rows above** — and
  the arm's landing value is exactly that it reads 1 now and must read
  **0** after W23.1. A check whose baseline is zero from the start
  proves nothing about the change that was made.
- **(c) THE SPEC ARM IS NOT A GREP AND SAYING SO IS THE POINT.**
  `rxt_format.md:130` already reads *"configs are three artifacts with
  three prefixes and ONE …"* — legitimate English in which `configs` is
  a plural noun — so no pattern separates a withdrawn production's
  spelling from prose about configurations. The obligation is the third
  pass: **read every hit against the claim that names it.** §7.1 keeps
  it as the standing risk rather than pretending a grep closes it.

**The general lesson this section now carries, because it cost two
revisions**: an absence check is only as good as its TOKEN LIST, and a
token list derived from the two mechanisms somebody remembers withdrawing
will miss the third. Derive it from the ruling's own enumeration — D99
items 1, 2 and N-42 — not from the section that discusses them.

---

## 5. The bench's 41-check acceptance bar, mapped to the staging

The bench runs these at their restart against the delivered pin
(`bench_rxt_needs_v1.md` §3, seven groups, forty-one checks). **They
are the EXTERNAL acceptance bar the staging must satisfy**, and mapping
them to steps is what makes "W23 is done" a testable claim rather than
a feeling. Their pairs — C1/C2, C5/C6, C8/C9, B3/B4, F2/F3 — are
their own check-design rule (*"every gate is exercised against an input
it must REJECT in the same run that exercises it against one it must
accept"*), and this delivery does not get to choose which half it
satisfies.

| group | checks | satisfied by | notes |
|---|---|---|---|
| **A** (the productions parse) | A5 | W23.3 | `tag` accumulation and mixed labels/pairs, unchanged W2 design |
| | **A1** | W23.3 + W23.3a, **with a bench-side CORRECTION** | A1's BEFORE is "refused by name with its wave", which SW13 keeps true at every intermediate pin. **But A1's fixture types `include` at head AND BLOCK scope, and `include` is a DECL-LINE ONLY** — **CITED**, `format_design.md` §1.3's EBNF: `decl-line = … \| "include" , ws , path-ref …`, with no `include` alternative anywhere in `block-line`. A block-scoped `include` is an unknown token in block scope at the delivered pin, so A1's probe exits 1. **This is A2's shape a second time** (r59-B-M5): the verbatim need was read, the keyword list was checked against the delivery, and the SCOPE the fixture types was not. Their fix is one line — move the `include` to the head — and it joins §9's correction list NOW rather than at their restart |
| | **A2** | W23.3, **with a bench-side CORRECTION** | **A2's fixture literally types `config … testee` and `config … option`, both removed at 3.4, so A2 exits 1 at the delivered pin. Their fix is TWO DELETED LINES.** This is r58 B1 and it is why Appendix A was gated: a true two-token measurement had been generalised into "no probe script needs an edit". One does |
| | A3, A4 | W23.1 (the unknown-token and wrong-scope refusals are schema facts) | A3 wants the diagnostic to name the CONTEXT — which is what `unknown-token-in-scope` is |
| **B** (raw bytes round-trip) | B1, B2 | W23.3/.4 (existing behaviour, **must not regress**) | B1/B2 already pass; a regression is a delivery failure |
| | **B7** | W23.3, **and it is a FIRST LIVE VERIFICATION, not a regression guard** | revision 1 booked B7 with B1/B2 as *"existing behaviour, must not regress"*. **The ruled disposition is the opposite** — **CITED**, `format_design.md` §9's B7 row: *"SATISFIED BY DESIGN, and this delivery is where it gets its first live verification"*, quoting their own row's *"nothing has ever verified it"*. **So it owes a FIXTURE and revision 1 scheduled none**: a `@file:` subject whose file is the three bytes `\x00\xff\x41`, reaching the matcher WHOLE through `driver.c`'s `@<path>` argument form (H6/S5), asserted on the engine's own answer rather than on the file being read. Booking a never-run promise as a regression guard is how a thing stays unverified through the delivery that was supposed to verify it |
| | **B3, B4** | **ALREADY LANDED by STEP 0** (lane `rxtnul`) | the NUL refusal — *"the single highest-value item in the checklist"*. Leg A is done; §1.8 brings legs B and C to parity |
| | **B5** | W23.3, **PARTIAL and the deviation is named** | `pattern-esc` round-trips a newline and a trailing CR; **`\x00` is REFUSED BY NAME, parked on K9** (the compile entry takes no pattern length, so a NUL-bearing pattern would compile as its prefix and report success). Their own N-4 split — *"SHOULD to express, MUST to refuse"* — is honoured in both halves |
| | **B6** | **PREMISE DISSOLVED** | the refusal it tests has an EMPTY POPULATION: both spellings are S2 openers, so a `pattern-esc` line after a `pattern` line is the NEXT BLOCK, not a second line in one block. **Not a deviation and not a failure** — a bench-side rewrite |
| **C** (refusal by name + negative arms) | C1, C2, C3 | W23.3 (`vocabulary`) | C3 is the compatibility control: a key with no `vocabulary` line keeps free-vocabulary behaviour |
| | C4, C5, C6, C7 | W23.3 (`provenance` + `cardinality: at-most-one`) | C5/C6 are S-R2's corroboration in the other repo; §3.2's fixture pair is the detector in ours |
| | C8, C9 | W23.3 (`sha256`) | |
| | **C10** | **ALREADY LANDED by STEP 0**, as a REFUSAL | their row explicitly admits *"the check records the CHOICE"*. The choice is refusal |
| **D** (`--list-source` columns) | **D1** | W23.4 | **D1 lists SEVEN items and types neither `capable` nor `config`** — r58 B6. `#section aux` is a new section D1 does not ask about, and claiming it "answers half of D1" was false at two sites |
| | D2, D3, D5 | W23.4 | D5 (a stream with no `#section` reads as one anonymous section) is satisfied by the unconditional-when-non-empty rule: a file using no W23 production emits NO `#section` line |
| | D4 | W23.1 + W23.4 | the VALIDATES-vs-RECOGNISES table, **RENDERED from `validated_by`** |
| **E** (the set loads and measures) | E1-E4, E6 | bench-side, on our delivered pin | |
| | **E7** | bench-side HASH, **pcrec-side ENUMERABILITY — §1.10.5** | E7 wants `content_hash` to cover the `.rxt`, every `include`d fragment and every `@file:` subject. The hash is theirs; **the bench cannot hash what it cannot enumerate**, and the format's contribution is that the closure is walkable from the dump alone: `--list-source` on the entry, follow each `include` row's RESOLVED-path column transitively, and read `@file:` paths out of `#section cases`. Revision 1 booked E7 "bench-side" with no pcrec-side path at all, which is the same omission as §1.10's |
| | **E5** | W23.3 (`under`) **plus a bench-side harness change they name themselves** | *"This check cannot pass on the format alone"* — their `harness.outcome_for()` has no convention parameter. Our half is `under` as a counted, labelled skip |
| **F** (D93 and engine neutrality) | **F1** | **SW5's ONE SENTENCE** | the parse already works; the CONTRACT is the ask, and SW5 is exactly that sentence |
| | **F2** | **PREMISE DISSOLVED, and D93 is UNCHANGED** | its setup — a set file declaring `engine` in a `config` — has no construction in a set file with no configs. **Its literal pass condition still fails for every config-BEARING file**, because D93 is untouched and decoupled (D99 item 5). This is r58 B7: B6 four rows up gets the honest word for the same situation and F2 had been given "satisfied more completely" |
| | F3, F4 | bench-side | |
| **G** (the format's own regressions) | **G1** | every step (`make test` green over the whole corpus) | R-COMPAT-1 |
| | G2 | W23.4 (their five committed exports round-trip) | the dump's escape vocabulary is unchanged; the columns append |
| | **G3** | W23.5 | **M1 MUST change** (the NUL refusal — already true at STEP 0). **M10 changes by design** (the W2/W3 keywords stop being refused). **M5 changes** (C10 accepted). **M2-M4, M6-M9, M11-M13 must be UNCHANGED; any other movement is a FINDING** |

**THE CORRECTION LIST IS `format_design.md` §9's, BY REFERENCE. THIS
NOTE DOES NOT RE-DERIVE IT** (r59-B1 — and the re-derivation is the r58
disposition-text class, fifth recurrence).

Revision 1 named three rows — A2, B6, F2 — and called that "the
correction list". **It is not**: §9's own table (whose header says the
D78 outbox message *"carries exactly this list"*) holds nine live rows,
and Appendix A's drafted message enumerates them. Revision 1 reached
three by reasoning about which rows THIS note discusses, which is the
exact derivation error §9's own closing note records going wrong twice
already — *"a moved spelling's affected checks are found by GREPPING
THEIR §3 CHECKLIST for the token, not by reasoning about which
check-group the production belongs to."* It also generalised §9's note
about a DELETED row (`capable` → `provides`, deleted because the bench
never has to make that rename) onto `licence` → `license`, **which the
bench does have to make: their C4 row literally types `drop \`licence\``
and exits 1 at the delivered pin.**

**So: the list lives in `format_design.md` §9 and in Appendix A's
drafted body, and W23.5 item 4 produces the DELIVERY-TIME list by
reading §9 — never by reading this section.** For a reader's
orientation only, §9's live rows at 3.4.1 are: the `provides`
withdrawal (their C-group SET FILE changes shape), the
`configs describe` withdrawal, `testee`/`option` leaving `config`'s
body, **A2's two deleted fixture lines**, `licence`/`licence-note` →
`license`/`license-note` (**C4**), the `freq` block's four one-off
provenance fields becoming a `provenance` child, **D1's provenance key
count NINE → ELEVEN plus the two renames**, `description` accepting
`prose-value`, and **B6's dissolved premise** — plus **F2's dissolved
premise with the D93-unchanged note** from the disposition table, and
**the `mc` adapter edit** (empty-match advance from the reported START,
not `max`) which Appendix A carries. **Revision 1.1 adds one: A1's
block-scoped `include`** (the A1 row above), which is A2's shape and
belongs on the same list.

**STANDING LESSON, and it is why this paragraph is a pointer and not a
table** (r59-B1's disposition, recorded for the journal): *a correction
list that exists in a ruled document travels BY REFERENCE and is never
re-derived. Re-derivation is how the disposition-text class
propagates* — the second copy is right on the day it is written and
wrong on the day the first one moves, and nothing compares them.

---

## 6. The step briefs

Written so a lane's first action is CODE, not planning. Each brief
names its build order, its acceptance, what it must not touch, and the
risk worth naming before starting.

### 6.1 [DD-13b.W23.1] — the schema table and its surface

**Build order**

| # | build | why here |
|---|---|---|
| 1 | **`src/parse/rxt_schema.def`** + the Makefile prerequisite (F1, F2) | the prerequisite lands with the file, not after it. `ccd2_report.md` §6b: editing a `.def` that is not a prerequisite rebuilds nothing and one binary carried two values of one constant |
| 2 | **`rxt_schema.c`** — the row lookup, the three parameter queries, the exhaustive constraint switch (F3) | the walk is what item 3 replaces control flow with |
| 3 | **leg A's dispatch as a table WALK** (F4): S0's four line classes, S1 attachment, S2 the two-member opener set, S3's parameterized trigger and extent, **parameter 3's OPEN SUBTREE** | this is the step's substance. `head_vocab`/`config_vocab`/`block_vocab`/`vocab_find` are displaced by the table |
| 4 | **the diagnostic CLASS tag** on `rxt_fail` (63 call sites) | it must exist before W23.2 can compare against it |
| 5 | **`--list-schema`** (F5, F6), including the `surface` section | item 6's checks read the DUMP, never the table |
| 6 | **W23-S3, S-R3 (S241), S-R5 (S244)**, and the eleven structure-layer fixtures of §3.2 marked W23.1 | the rows land in the same commit as the code they detect |
| 7 | **SW2, SW16, SW17, SW13** | D80 |

**Acceptance**

- `make test` green; the corpus census **210 / 3,936 / 28,943**
  unmoved (fixtures are `.rxtin`).
- `--list-schema` emits a row for every (scope, kind) the parser
  dispatches, **verified by W23-S3's per-row behavioural probe**, not by
  comparing two renderings of one table.
- **The three structure-layer parameters are each ONE query**:
  `opens_group: true` returns exactly `pattern` (one row at this step —
  `pattern-esc` arrives at W23.3); the `value`+`children` PAIR returns
  exactly five rows; `children: tree` returns **zero** rows at this
  step and that is correct, because `ext` has not landed. **A parameter
  whose row set is legitimately empty must be distinguishable from a
  parameter that is not implemented** — the query returns an empty set,
  never an error.
- `make strict` clean.
- S241 and S244 each turn their NAMED check red; **S244 must be run in
  BOTH its plants** (a) and (b), since (b) is the one that would be
  invisible if the parameter read `value` alone.
- **The narrowings' fixtures are RED before the change and GREEN after**
  — `config_tab_body.rxtin` and `config_mixed_indent.rxtin` are
  accepted at rc 0 today, so running them against the branch point is
  what makes them regressions rather than assertions.

**Must not touch**: legs B and C; any production; the dump's shape.

**The risk worth naming**: **leg A's dispatch is the most load-bearing
parser in the tree and this step replaces its control flow with a table
walk.** The corpus is 210 files and every one of them goes through it.
The mitigation is not care, it is ORDER: land the table and the reader
first with the OLD dispatch still in place and a debug-only assertion
that the two agree on every corpus file, then delete the old dispatch
in a second commit. A byte-identical `--list-source` over 210 files
across that pair is the real acceptance, and it is cheap because
`--list-source` is parse-only.

### 6.2 [DD-13b.W23.2] — legs B and C, and the STEP 0 parity fix

**Build order**

| # | build | why here |
|---|---|---|
| 1 | **REWRITE `check_refusal_all3` TO COMPARE CLASS** (`run_rxtsource_tests.sh:1492-1507`) **and give its SEVEN existing call sites their classes** | **r59-A-M6, and nothing in revision 1 scheduled it.** §3.2's *"every three-leg assertion compares DIAGNOSTIC CLASS, never exit code"* is a rule about a helper that is **MEASURED verdict-only**: legs B and C are run as `… > /dev/null 2>&1` and only their exit status is read (`:1497`, `:1502`), while leg A's message IS checked through the `check_refusal` it delegates to. The helper grows a class argument; the existing seven sites (`:1538` `bad_flags`, `:1541` `bad_engine`, `:1590` `desc_pipe_trailing_space`, `:1614` `directive_before_pattern`, `:1628` `bad_name_ident`, `:1629` `bad_encoding_ident`, `:1633` `dup_block_name`) each name theirs. **They are not left on the old signature**: a helper with two modes is a helper whose weaker mode is what a hurried author reaches for |
| 2 | **the diagnostic CLASS tag** in both legs: the four classes attached AT THE RULE THAT FIRED | leg B's catch-all at `:2105-2109` today refuses a W23 production it has never heard of, an indented line, a schema violation and a typo with the same verdict and the same sentence. Item 1 is what makes this observable; this is what gives it something to observe |
| 3 | **the STEP 0 PARITY FIX** (§1.8) in both legs: **TWO fixtures re-aimed to `check_refusal_all3`** (`nul_byte`, `dup_description` — both headless), `dup_head_description` keeping `check_refusal` with its seam reason stated in the script, the `tests/rxtsource/CLAUDE.md` scope note NARROWED, and `nul_in_comment.rxtin` added | it is the smallest complete three-leg agreement in the delivery and it retires an owed item. **It moves BELOW the class work rather than above it** (revision 1 had it first): the re-aim's whole value is that the two new refusals *"get their class from the mechanism rather than from a special case"*, and a re-aim landing before the mechanism has no class to get |
| 4 | **the ATTACHMENT arm** in both legs: parent from indent BEFORE first-token dispatch; the two refusal arms | leg B has no indentation test at all (its 22 `^`-anchored arms reach the catch-all by fall-through); leg C's `:424-427` is a rejection, not an attachment rule |
| 5 | **child CONSUMPTION** for a kind that admits children, and for a prose value | `ext`'s arrives at W23.3, but the MECHANISM is here |
| 6 | **W23-S1, W23-S2**; **S-R1 (S239)**; `indent_pre_body.rxtin`, `indent_under_m.rxtin`, `nul_in_comment.rxtin` | S239 is planted in the direction only the differential sees |
| 7 | the SW rows this step makes true (none new — SW2/SW16 landed at W23.1 and describe rules all three legs now implement; SW21's diagnostic-class hunk landed with the tag at W23.1) | **a step with no spec hunk states so explicitly**, because "no hunk" and "forgot the hunk" look identical in a diff |

**Acceptance**

- C1 three-way over the full corpus, **byte-identical trees**, at
  210 / 3,936 / 28,943; C2 at 209 / 3,933 / 28,932; C3 over its own
  discovery.
- **W23-S2 green on every refusal fixture in §3.2 that exists at this
  pin**, comparing CLASS.
- **`indent_pre_body.rxtin` refuses in all three legs at the PRE-BODY
  position.** The position is the acceptance, not a detail: leg C's
  `:424` check is unconditional once a block is open, so a post-body
  fixture would report GREEN against the defect.
- **`check_refusal_all3` compares CLASS at all SEVEN existing call
  sites and at every new one**, and no call site remains on a
  verdict-only signature.
- **`nul_byte.rxtin` and `dup_description.rxtin` move from
  `check_refusal` to `check_refusal_all3` and pass.
  `dup_head_description.rxtin` DOES NOT MOVE** — it is head-bearing, so
  `verify_rxt.py:407-417` refuses it for being head-bearing rather than
  for its duplicate, and a class comparison would go red for a reason
  that is the seam ruling working correctly. The script's comment states
  that in one sentence.
- **`tests/rxtsource/CLAUDE.md`'s leg-A-only scope section (`:320-332`)
  is NARROWED in the same commit, not deleted**: the NUL and
  block-`description` halves go, the head-`description` half stays, and
  its reason changes from *"out of this lane's scope"* (which expires
  here) to the seam ruling (which does not).
- **`nul_in_comment.rxtin` refuses in all three legs** — the fixture
  that discriminates between a file-wide pre-parse scan and a
  line-interpreting one, which `nul_byte.rxtin` structurally cannot.
- S239 turns C1 red and leg A alone green — **both halves asserted**,
  because a row that only proves "something went red" does not prove it
  went red for its reason.

**Must not touch**: `rxt_source.c`'s grammar. If the step finds itself
there, the boundary is wrong.

**The risk worth naming**: **leg B is bash and the attachment arm is
state.** Seventeen `^`-anchored arms become a dispatch that first
computes a parent. The hazard is not correctness, it is the pinned arm
region: `run.sh:1713-1967` is HASH-PINNED by
`run_rxtsource_tests.sh`, deliberately, and the pin must move with the
change rather than the change being shaped to avoid the pin. State the
new hash in the same commit.

### 6.3 [DD-13b.W23.3] — the productions

**Build order** — grouped by what shares a mechanism, which is also the
order in which a reviewer can read them:

| # | build | why here |
|---|---|---|
| 1 | **`pattern-esc`** + the CLI decode flag (F9, F10). `\x00` refused by name citing K9 | it is a second BLOCK OPENER, so `opens_group` goes to two rows and S2's set is complete. Everything after it lands inside blocks |
| 2 | **the CHILD-ADMITTING kinds**: `provenance` (both parents), `variant` as a sub-block with a `defname` name | they are W23.2's consumption mechanism's first real customers |
| 3 | **`ext`** — the AUX production, `children: tree`, `cardinality: repeat`, at both scopes | it is the CHEAPEST of the three for legs B and C (consumption with no dispatch) and the one whose correctness is a property of what pcrec does NOT do |
| 4 | **the head declarations**: `vocabulary`, `include`, `oracle` at a version, `tag`, `use`, the `freq` data block + `analysis` | leg A only — they are above the seam |
| 5 | **the case-line work**: `under` (H14), `mc` (H14, H7), `@file:` + `as`/`sha256` (H15, H6), and `driver.c`'s `@<path>` argument and find-all loop | `mc` is verified by the PROTOCOL loop in both C and python, **never `finditer`** |
| 6 | **§2.22's derived-identifier repair** (F11) **and its two comment sites** (F12): **`rxt_source.c:269-297` and `:1177-1180`, READ BEFORE EDITING** | D100. The comment sites move in the same change or the code contradicts the behaviour. **Both ranges were wrong in revision 1 and in the design's SW12 row**, so the step's first action here is to open the file at `defname_ok` and at the `name` arm and confirm the spans |
| 7 | the fixtures marked W23.3 in §3.2 — **including `aux_subtree_extent.rxtin` and B7's `@file:` NUL+invalid-UTF-8 subject fixture** (§5's B7 row: a FIRST live verification, not a regression guard) — and **S-R2 (S240), S-R6 (S245)** | |
| 8 | **SW1, SW3, SW4, SW5, SW6, SW7, SW8, SW9, SW10, SW12, SW15, SW18's rule half, SW14's flag half** | D80, and it is the largest spec landing in the delivery |

**Acceptance**

- Every production parses in all three legs where it is block-scoped
  and in leg A where it is head-scoped; C1 green.
- **`aux_arbitrary_keys.rxtin` ACCEPTED by all three legs**, and
  **`aux_deep_tree.rxtin` accepted with NO extra block, NO extra case
  and NO provenance record anywhere.** The absence assertions are the
  check.
- **`aux_literal_pipe.rxtin`**: the `\|` row's value is the single byte
  `|` and the sibling below it is a SIBLING — if S3 still opens inside
  an open subtree, the value is empty and the sibling has been
  swallowed, so this cell is decision 3's falsification point.
- **`aux_subtree_extent.rxtin`**: the declaration after the block is a
  DECLARATION, the `pattern` block is a block, and `#section aux` holds
  exactly the body's own lines.
- `derived_call_collision.rxtin` refuses **naming BOTH definitions and
  the shared identifier** — a refusal naming only the prefix is a RED.
- **The over-long definition name is refused BEFORE the mapping runs.**
  `pcrec_rxt_prefix_from_name` (`rxt_source.c:337-343`) silently
  TRUNCATES at `dstsz` — its loop condition is `j + 1 < dstsz` with no
  over-length return — so two long names differing only past the buffer
  would bind silently. **The existing consumer is safe only by an
  ORDERING nobody had written down as a rule, and revision 1 cited the
  wrong lines for it** (r59-C): `parse_target` refuses the definition
  name's LENGTH at **`:848-851`**, refuses its GRAMMAR at
  **`:856-861`**, and only then maps at **`:863`**. Revision 1's
  `:826-830`/`:840` are the `target` PREFIX's own length cap and a local
  declaration — a different name, in the same function, two refusals
  earlier. The second consumer reproduces the ordering, and the
  acceptance is a fixture with two names colliding only past the bound.
- S240 and S245 each turn their named fixtures red; **S245 is asserted
  on all THREE of its detectors**, since parameter 3 gave it a
  structural blast radius the plant did not change.
- `make strict` clean; `make test` green.

**Must not touch**: the dump's SHAPE. New productions parse and are not
yet reported. That is the boundary's value.

**The caveat that makes the intermediate pin landable, stated rather
than left latent** (r59-B-N7): between W23.3 and W23.4 a file can carry
a `pattern-esc` block whose dump row has **no `esc` column** — the
column appends at W23.4 — so the dump says "pattern" for a block whose
bytes were decoded. **Its population at this pin is ZERO**: the corpus
has no `pattern-esc` line and the fixtures are `.rxtin`, outside the
dump census. The pin is therefore landable as written, and the caveat
is recorded here so a reader of the intermediate tree does not read an
undecorated row as a claim that no decoding happened. Moving the column
earlier was considered and rejected: it would put a dump-shape change
in the step whose whole boundary is "no dump-shape change".

**Two risks worth naming**

- **`mc` is where a plausible implementation is silently wrong.** The
  bench's own find-all formula double-counts an empty match found
  beyond the scan position, and a python implementation reaching for
  `finditer` inherits a different divergence. Both legs implement
  `match_api.md` §3.1's protocol; the fixture that discriminates is
  `(?=a)` on `"xax"` (1, not 2), and it belongs in the corpus rather
  than in a comment.
- **`ext` is the production most likely to be built too well.** Every
  instinct a parser author has — validate the keys, normalise the
  values, dedupe the blocks, count the rows — is a graduation event.
  §3.4's check is the instrument, and it lands at W23.4; until then the
  discipline is the review's. **The reviewable question is not "does
  this read an aux body" but "does any pcrec output change when an aux
  body changes".**

### 6.3a [DD-13b.W23.3a] — `include`'s harness half

**NEW AT REVISION 1.1 (r59-B2). §1.10 is the mechanism; this is the
build order.**

**Build order**

| # | build | why here |
|---|---|---|
| 1 | **the `include` head ROW's RESOLVED-PATH column** in leg A's dump (§1.10.2 rule 2) | legs B and C read the closure off this column, so nothing else in the step can start without it. It is the one `src/` touch in a step that is otherwise pure harness, and it is a COLUMN on a row W23.3 already emits — not a new row kind |
| 2 | **leg B's ENTRY-SET SUBTRACTION** at `run.sh:293-307`: resolve every discovered file's includes, subtract the union, run the remainder; the `named, absorbed into <entry>` report for a file that is both | the subtraction has to land before the splice, or the fragment's blocks run twice and the population doubles — the failure the whole step exists to prevent |
| 3 | **leg B's SPLICE**: after the entry's own body, each fragment's blocks appended in include order, depth first | |
| 4 | **leg C's same two** through its own `discover` (`verify_rxt.py:715`) | its head-bearing refusal (`:407-417`) is UNCHANGED and untouched |
| 5 | **the CLOSURE TALLY and the FOURTH FAILURE CLASS**: `entry files: N`, `fragments spliced: M`, and RESOLUTION failures reported separately and scored as a pattern-compile failure for the block | the summary lines are what make a silently-unspliced set VISIBLE rather than merely smaller (K35, §2.11 rule 2) |
| 6 | **the three fixtures** (`include_basic`, `include_nested`, `include_dup_path` + their `.rxtfrag` files), **W23-S7**, and **S247** | |
| 7 | **the census pin block gains its second number** (§1.10.3): files discovered vs files that are entries, with the derivation beside it |
| 8 | **SW20** — the harness-evaluation spec hunk, which is W1-era row S3 and has never landed | D80, and §4.1 now says so |

**Acceptance**

- **The CORPUS control, and it is the one that matters**: over the
  shipped corpus at this pin, `fragments spliced` is **0** and
  `entry files` equals `CENSUS_FILES` = **210**. A subtraction bug that
  removed real files would otherwise surface only as a quieter suite.
- **The pinned census does not move**: 210 / 3,936 / 28,943 and leg B's
  209 / 3,933 / 28,932. The fixtures are `.rxtin`/`.rxtfrag` and
  therefore not corpus; **if the census moves, a fixture has leaked**
  (`utf8k53_report.md` §5's own finding).
- **W23-S7 green on all three fixtures**, with all four conjuncts
  asserted separately: equal counts across three legs, the entry's
  count EXCEEDING its own file's, `fragments spliced` equalling the
  number the fixture declares, and the fragment NOT appearing as an
  entry.
- `include_nested` agrees across three legs on the ORDER, not only the
  set.
- `include_dup_path` refuses in all three legs, class
  `schema-constraint`, **naming BOTH sites** — a refusal naming one is
  a RED, because §2.5's rule is about a collision and a collision has
  two ends.
- **S247 turns W23-S7 red on the FIXTURE arm and leaves the corpus arm
  green**, both asserted — a plant whose only evidence is "something
  went red" does not prove it went red for its reason.
- `make test` green; `make strict` clean.

**Must not touch**: `rxt_source.c`'s grammar (W23.3 landed the
production); the dump's SHAPE beyond item 1's column; any other leg
behaviour.

**The risk worth naming**: **this step edits the file-discovery loop
that every other section of `make test` inherits.** `run.sh:293-307` is
not `include`'s code, it is the harness's own population, and a
subtraction with an off-by-one in its path comparison silently drops
corpus files — which reads as a FASTER, GREENER suite. That is why the
corpus control above is an acceptance line rather than a side effect,
and why this is a separate merge: its diff should be readable as
"discovery changed" and nothing else.

### 6.4 [DD-13b.W23.4] — `--list-source`'s sections, and the survey

**Build order**

| # | build | why here |
|---|---|---|
| 1 | **RE-RUN the format-reader survey** (§1.5) at this step's own pin, and record its output in the commit | the table in §1.5 is stale by construction: three steps of checks have landed since. `w1_impl.md` §8.7's rule — **the command is the contract, not the list** |
| 2 | **the appended COLUMNS** on pattern rows (`tags`, `oracle`, `esc`) and the new head ROW kinds (`vocabulary`, `include`, `oracle`, `tag`, `use`), and the MANIFEST re-pinned | the MANIFEST check (`run_rxtsource_tests.sh:464-477`) fails loudly and correctly, with its own instruction — that is the gate working |
| 3 | **REPAIR *BOTH* SECTION-BLIND ASSERTIONS, R5 AND R6, BEFORE EMITTING ANY SECTION** — R5's field count (`:479-494`) with its failure message (`:487-492`), and **R6's head-declaration counters (`:499-505`)** | **R5 asserts one uniform column shape for every non-`#` row** and its message names a TAB as the only possible cause; **R6 counts every non-comment row whose kind is NOT `pattern` and asserts ZERO**, so every `#section cases` row is counted as a head declaration in a corpus that has none. Emitting a section first means delivering two red checks that are right to fire, under diagnostics pointing at the escape function and at a head-detection bug. The repair is the same shape for both: **the main table's rows are identified by the section boundary the stream DECLARES**, with the unknown-section arm HARD-FAILING rather than defaulting. R6 was marked safe at revision 1 — see §1.5 |
| 3b | **A SYNTHETIC STREAM EXERCISING BOTH REPAIRED ARMS, IN THE REPAIR'S OWN COMMIT** | **r59-A-M3**, and it is the only enforcement of item 3's "before emitting" ordering that exists. At the repair's commit NO section is emitted yet, so both new arms have population ZERO and the repair lands unexercised — a check nobody can distinguish from a check that was not written. The commit therefore carries a hand-written `--list-source`-shaped stream through the repaired awk. **The positive control's section must have a width that DIFFERS from the main table's 16** (**MEASURED**, `rxt_columns[]` at `rxt_source.c:2074-2082`), **and `#section cases` is ALSO 16** — counted off §2.24's own list: `line`, `block_line`, `block_name`, `kind`, `under`, `startpos`, `subject_form`, `subject`, `subject_id`, `sha256`, `start`, `end`, `count`, `giveup`, `slot`, `route`. A width-blind repair would pass a `cases`-only control by coincidence. **`#section aux` at EIGHT** (`line`, `block_line`, `block_name`, `consumer`, `depth`, `key`, `value`, `parent_line`) is the width to use. Note also that this check reads `DUMP_A_RAW`, which carries a leading FILENAME field — hence today's `NF != ncols + 1` — so every per-section expectation is *declared width + 1* and the `+ 1` belongs in one place, not per section |
| 4 | **the four `#section` blocks**: `provenance`, `variants`, `cases`, `aux` — emitted unconditionally when non-empty, **after the main table, never interleaved** | |
| 5 | **W23-S4** (no section row's field 1 equals a main-table kind token) and **W23-S6** (the aux value-identity check) | §1.5's invariant and §2.27.3 clause 5 |
| 6 | **RE-RUN S200-S203 AGAINST THE REPAIRED ASSERTIONS** and confirm each still fails for ITS OWN reason | **r59-A-M4.** R4/R5/R6 ARE those four rows' detectors (§1.5's R9 row), so item 3 changes the detector under four existing plants — the [MECH-REACH] shape, arriving through a repair rather than through a rename. **And three of the four carry a STALE COUNT in their `SAB_DESC` today**, which is the same class one layer over: S200 says *"16 fields where the header declares 15"* (the header declares 16), S202 says *"14 columns … 15 fields"* (15 and 16), S203 says *"all 179 corpus files"* (210). The re-run re-states all three |
| 7 | **S-R4a (S242), S-R4b (S243)** | they detect `opens_group` through `#section cases`'s `block_line` and the block count |
| 8 | **SW11, SW19, SW18's section half, SW14's section half** | |

**Acceptance**

- C1 green over the full corpus with the repaired field-count
  assertion; **the census does not move** (sections add rows to a dump,
  not lines to a corpus).
- **An existing corpus file's dump GROWS a `cases` section** and the
  `tests/rxtsource` pinned fixtures move with it — the normal re-pinning
  ritual, traced to the exact PASS/own-oracle split rather than copied
  from a log (`landing_report.md`'s lesson).
- **A file using no W23 production emits NO `#section` line**, and its
  stream differs from today's ONLY in the header row's appended
  columns. That is `table_contract.md`'s compatible evolution and it is
  bench check D5.
- **W23-S6 is green**: editing an aux body changes `#section aux`'s rows
  and **nothing else, byte for byte** — the dump with that section
  elided, `--list-schema`, every compiled artifact, every diagnostic.
- S242 and S243 turn their named detectors red, **and they are
  different detectors** — S242's symptom is a moved `block_line`,
  S243's is a changed block count.
- **S200-S203 each still fail, and each still fails for its own
  reason**, re-run against the repaired R5/R6 — asserted per row, not
  as an aggregate "mech is still green". Their three stale `SAB_DESC`
  counts are re-stated in the same commit.
- **The synthetic-stream control (item 3b) exercises BOTH repaired arms
  at a section width that is not 16**, and it is in the repair's own
  commit rather than in the section-emitting one.

**Must not touch**: any production, any refusal.

**The risk worth naming**: **the survey's own completeness.** §1.5
found R5 by grepping for four shapes (`NF`, `cut -f`, `IFS=$'\t'`,
`awk -F'\t'`). A reader that consumes the dump through a fifth
shape — a python `split('\t')`, a `read -a` array, a `sed` field
count — is outside those four patterns. The re-run at item 1 widens the
pattern set and, more usefully, **greps for `--list-source` itself and
reads every hit**, which is the one pass that cannot miss a consumer by
spelling. That is r58 B1's own method note applied one document over:
*read every grep HIT against every claim that names it.*

### 6.5 [DD-13b.W23.5] — fixtures, population, spec, and the acceptance pass

**Build order**

| # | build |
|---|---|
| 1 | every fixture in §3.2 not yet landed, and the **`all-readers` POPULATION check** (§3.3) — which can only run once every row exists |
| 2 | **promote `validated_by: pcrec` rows to `all-readers`** where their fixture now exists, one row at a time, each with its fixture named in the same commit |
| 3 | the SW rows not yet carried, and the §4.3 absence grep as a committed check rather than a manual step |
| 4 | **the bench acceptance DRY RUN** (§5) — **scoped to the RUNNABLE subset, and the split is named in the brief rather than discovered by the lane** (r59-B-M6). Roughly **25 of the 41** checks are executable here: groups A, B, C, D, F1/F2 and G are probes over `pcrec` and a fixture file, and we can write the fixtures from their own stated setups. **Group E's six and F3/F4 are NOT** — they invoke `pcrecbench` (`python3 -m pcrecbench run --subbench capability`), `make check-harness`, `Subbench.content_hash()` and their own `check` gate, none of which exists in this checkout. The acceptance bullet is scoped to the runnable set; the rest are marked NOT-RUN-HERE with the tool that is missing, never marked passed |
| 4b | **the CORRECTION LIST, read out of `format_design.md` §9 and Appendix A — NEVER re-derived from §5** (r59-B1). §5's own paragraph is a pointer for exactly this reason: the delivery-time list is whatever §9 holds at the delivered pin, plus anything the dry run finds |
| 5 | the D78 outbox message (Appendix A's body) — **the MANAGER sends it**, not the lane |

**Acceptance**

- **No `all-readers` row without a RECEIPT** — W23-S5 reads the
  three-leg helper's own invocation receipts, never a declared fixture
  name (§3.3 property 2), and the assertion is the check's, not a
  reading's.
- **The 41-check dry run reports three populations, not one**: passed,
  failed (each with its correction), and NOT-RUN-HERE with the missing
  tool named. A run that reports "25 passed" without its denominator is
  the shape this delivery has already corrected twice.
- The §4.3 grep returns 0 over `docs/spec/`, `src/`, `tests/`, `cli/`.
- The full battery: `make test`, `make strict`, `make test-axes`,
  `make san`, `make lint`, `make mech`. **All OWED to the merging
  session** — this note plans no runs.
- **G3's thirteen MEASURED facts re-run**: M1 MUST change, M10 changes
  by design, M5 changes; **M2-M4, M6-M9 and M11-M13 must be UNCHANGED,
  and any other movement is a FINDING** rather than a fix.

**The risk worth naming**: **step 4 is a discovery, not a
verification.** Running someone else's 41-check acceptance bar against
our own pin, for the first time, will either be clean or reveal a
reading of the design we and they do not share. That is the point of
running it before they do — and the correct response to a divergence is
a correction list for the manager, not a fix inside W23.5.
`w1_impl.md` §7.4's item 6 is the precedent, one wave over.

---

## 7. Risks, open questions, and what this note could not settle

### 7.1 The standing risks

1. **THE RESIDUE CLASS IS DISPOSITION TEXT, and this note is made of
   it.** r58's method note: *a forward grep finds SPELLINGS, an inverse
   walk finds MECHANISMS, and neither reads a sentence that describes a
   withdrawn production as current.* §4.3's grep catches a re-introduced
   spelling. Nothing here catches a paragraph in a later step's commit
   message, lane report or spec hunk that says `config … testee` is how
   a roster is declared. **The only instrument is the third pass: read
   every grep hit against every claim that names it**, and each step's
   checklist carries it as a line.
2. **Leg A's dispatch rewrite (W23.1) is the largest single risk in the
   delivery**, and §6.1's mitigation is an ORDER rather than a
   discipline.
3. **`ext` being built too well** (§6.3). The graduation rule is broken
   by accretion, not by decision.
4. **The step boundaries are only real if the diffs respect them.**
   §2.2 is written as a negative for that reason, and `git diff --stat`
   at each merge is the check.
5. **W23.3a EDITS THE HARNESS'S OWN FILE DISCOVERY** (§1.10, §6.3a),
   which every section of `make test` inherits. A subtraction bug there
   does not fail — it makes the suite quieter. The corpus control
   (`fragments spliced: 0`, `entry files == CENSUS_FILES`) is an
   acceptance line for that reason.
6. **A CITATION CARRIED FROM A RULED DOCUMENT IS STILL A CLAIM ABOUT
   THE TREE.** Revision 1 inherited SW12's two comment ranges from
   `format_design.md` and both were wrong; it inherited
   `run.sh:184-216` for the harness's per-file loop from §2.11 and that
   is wrong too; and it booked spec row S3 as landed on the strength of
   its wave LABEL. **A wave label says when a row was scheduled, never
   whether it shipped**, and every `file:line` in a design document is
   a measurement with a date on it. Re-read; do not carry.

### 7.2 The DECIDED points, collected

| # | decision | where | the alternative, and why it lost |
|---|---|---|---|
| 1 | `rxt_schema.def` is an X-macro with HOME DISPATCH | §1.4 | a generated table; `limits.def`'s precedent is in the tree and its Makefile lesson is already paid for |
| 2 | ONE exhaustive `default:`-less switch over the constraint enum | §1.4 | a dispatch table; a compile error at the one site that must handle a new kind is the house rule (`src/opt/mrl.c:18-24`) |
| 3 | `under`'s key tuple is PARSER CODE, and the schema SAYS SO | §1.4 | a declarative field extractor, which is §2.25.4's deferred item with a trigger (a SECOND `qualified-line` production) that has not fired |
| 4 | **no `#section` row's field 1 may equal a main-table `kind` token**, asserted | §1.5 | leaving three readers safe by luck. The invariant holds today and nothing states it |
| 5 | **sections FOLLOW the main table, never interleaved** | §1.5 | free today, impossible to recover once a consumer has seen the other order |
| 6 | leg B DETECTS a NUL rather than carrying one | §1.8 | rewriting the arm chain to carry bytes bash cannot hold, for a population of zero |
| **7** | **the NUL rule has ONE scope in all three legs: the whole file, before the line split** | §1.8 item 3 | a decoder-scoped test in leg C, which revision 1 specified — it never sees a NUL in a comment line, and two scopes for one rule cannot be differentiated |
| **8** | **`dup_head_description.rxtin` stays SINGLE-LEG, with its reason stated** | §1.8 item 5 | re-aiming it to `check_refusal_all3`, which goes green today for the wrong reason and RED the moment W23-S2 compares class |
| **9** | **`include`'s resolved real path is a DUMP COLUMN, and legs B/C read it rather than parsing `include`** | §1.10.2 rule 2 | a fourth head parser in each harness leg — which the seam ruling forbids — or `--list-source --resolved`, which stays unbuilt |
| **10** | **W23.3a is its OWN merge** | §1.10, §2.1 | folding it into W23.3, where a discovery change would land inside a diff about eight productions |
| **11** | **SW21 (the diagnostic class) lands in `cli.md`, not as an extension of SW2** | §4.1 | SW2 is `rxt_format.md`'s lexical rules — the FORMAT's grammar; a machine-parseable stderr tag is the CLI's output contract, and folding it into SW2 leaves `cli.md` silent about a channel callers parse |
| **12** | **W23-S3's denominator is a COMPILE-TIME total from the `.def`, printed by the dump** | §3.1 | a pinned count (a number in a second place) or an un-denominated iteration (a check whose population is defined by the thing it checks) |

### 7.3 The four open questions — RULED at r59 (R1-R4)

**All four were ruled by the manager at r59 and none returns to
Frank** (critic B's classification — all four manager-ruleable —
confirmed). The questions are kept with their answers because a
reader who meets the implementation wants to know what was chosen and
what was rejected, not only what shipped.

- **Q-W23.1 — does the diagnostic CLASS tag surface to a USER, or only
  to the differential? RULED R1: ACCEPT the implemented default.** The
  tag is **emitted on stderr in a stable, machine-parseable position,
  one channel** — the differential needs it and a second channel would
  be a second mechanism. **AND IT GAINS A SPEC HUNK THAT REVISION 1 DID
  NOT PLAN**: a machine-readable diagnostic structure is a
  caller-observable CLI surface, so D80 applies. **That hunk is SW21
  (§4.1) and it lands in `docs/spec/cli.md`, not in SW2.** The choice
  between a new row and an extension of SW2 is DECIDED (11): SW2's hunk
  is `rxt_format.md`'s LEXICAL RULES, which is the format's grammar,
  while the tag is the CLI's output contract — an extension of SW2
  would put a CLI surface in the format spec and leave `cli.md` silent
  about a channel callers parse. D26 is untouched either way: the hunk
  fixes the tag's POSITION and its closed SET, and says in terms that
  the sentence beside it is not a contract.
- **Q-W23.2 — where does `#section cases` put a `route`? RULED R2:
  ACCEPT.** The `route` is DENORMALISED onto each case row — the
  block's route, repeated — because §2.24's own gloss is *"the
  positional `frames-buffer=` state the case runs under"*, which is
  per-case by meaning even though the directive is block-scoped. The
  alternative (an empty column except where a route line precedes the
  case) is more faithful to the source and harder to use, and the
  consumer that reads this column is reading per case.
- **Q-W23.3 — does `--list-schema` print the `surface` rows in the same
  stream or behind a flag? RULED R3: ACCEPT the same stream**, as a
  `#section surface` block. §2.24 calls them *"a named sibling surface
  row in `--list-schema`'s output"*, and **a flag would hide exactly
  the absence the mechanism exists to surface**: declared non-coverage
  behind an opt-in is something a consumer has to already suspect
  before they can ask about it.
- **Q-W23.4 — is K57 fixed in this delivery? RULED R4: NO**, and the
  recommendation is accepted as written. K57 has its own
  `known_issues.md` entry, its corpus population is ZERO, and two
  independent reds must not share a step — fixing it inside a step
  whose acceptance is the structure layer would put two unrelated
  causes behind one failure.
  **R4 ALSO SETTLES WHAT REVISION 1 LEFT VAGUE: `prose_dedent.rxtin`'s
  WAITING STATE.** Revision 1 called it *"carried `known_fail`-style"*,
  which is not a thing `tests/rxtsource/` has — **there is no
  known-fail mechanism in that suite at all**; its fixtures either
  assert an acceptance or assert a refusal. So the fixture **asserts
  the CURRENT, WRONG decoded value** — the dedent strip's byte-count
  truncation, three legs agreeing on the truncated string — **with a
  comment naming K57 and saying in one line that this assertion is a
  RECORD OF A DEFECT, not a promise.** Its expiry event is therefore
  built in: **the day K57 is fixed, this fixture goes RED**, and the
  red is the signal to invert it to the three-way agreement on the
  CORRECT value. That is the cheapest available form of a pinned bug in
  a suite with no known-fail bucket: the pin cannot outlive the defect
  silently, because the fix breaks it.

### 7.4 What this revision could not settle

Nothing new. Revision 1's four questions are ruled above; the r59 panel
raised no fifth, and revision 1.1 adds no question to the Frank queue —
the W23 queue stays EMPTY.

### 7.5 What a fresh agent needs to know

- The note is `docs/design/dd13_format/w23_impl.md` on branch
  `lane/w23implfix` (revision 1 was written on `lane/w23impl`, which
  this branches from). It is DOCS-ONLY: nothing under `src/`, `tests/`
  or `docs/spec/` moved, no `make` was run.
- The design it implements is `format_design.md` **3.4.1**. On any
  disagreement the design note wins and this one is the bug.
- **Revision 1 was panelled at r59**; §0.5 is the finding-by-finding
  record. **The next step is the W23.1 charter** — the delivery is
  **SIX** merges (W23.1, .2, .3, .3a, .4, .5), not five.
- Nothing is owed by this lane. Every number in §6's acceptance
  sections is a target for its step, not a measurement this lane took;
  every `file:line` in this revision was re-read against the tree at
  this branch's merge base rather than carried from revision 1.

---

## 8. The one-page checklist a step lane types into its brief

Every W23 step's brief carries these **nine** lines. They are the rules
this delivery has already paid for once each — the last two added at
revision 1.1, each for a defect r59 found in revision 1.

1. **Spec hunk in the same change** (D80) — or an explicit "this step
   has no hunk", because "none" and "forgot" look identical in a diff.
2. **Sabotage row in the same commit as the code it detects**, numbered
   after re-checking the highest id **on main**.
3. **`validated_by: pcrec` until the fixture exists**, never
   `all-readers` on the strength of one leg.
4. **Diagnostic CLASS, never exit code**, in every three-leg assertion.
5. **Re-pin every manifest, census and count the change moves**, in the
   same delivery — post-merge manager cleanup of a lane's pins is a
   delivery failure.
6. **The withdrawals' absence check passes on its THREE arms** — the
   data arm and the parser arm as greps, the spec arm as a READ (§4.3).
   Not "a grep returns 0": that version was unsatisfiable on the
   untouched tree and its token list was missing two of the four
   withdrawn spellings.
7. **No abi bump.** If the step believes it needs one, it STOPS and
   escalates (§1.9).
8. **RE-READ EVERY `file:line` THE STEP RELIES ON, from the tree, at
   the step's own pin** — including ones this note and
   `format_design.md` supply. Revision 1 carried eight wrong ranges out
   of two ruled documents (§7.1 item 6).
9. **Every three-leg assertion names its CLASS**, and a helper that can
   be called without one does not exist after W23.2 (§6.2 item 1).
