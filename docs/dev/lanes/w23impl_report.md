# w23impl — [DD-13b.W23] the IMPLEMENTATION NOTE

Lane `w23impl`, opus, 2026-09-13, branch `lane/w23impl` in
`worktrees/w23impl`. Charter: write `docs/design/dd13_format/w23_impl.md`,
the implementation note that opens the W23 build, in `w1_impl.md`'s shape.

**DOCS ONLY. Nothing under `src/`, `tests/` or `docs/spec/` moved. No
`make`, no compile, no suite, no battery — none was needed and none was
run.** Delivered COMPLETE: the deliverable is a plan, the only checkable
artifacts are its own tables and citations, and both were checked (§3).

Files changed: `docs/design/dd13_format/w23_impl.md` (new, 1,240 lines),
`docs/design/dd13_format/CLAUDE.md`, and this report.

## 1. What I planned, in one paragraph

W23 lands as **five merges**: W23.1 the schema table
(`src/parse/rxt_schema.def`), its reader, `--list-schema`, and leg A's
dispatch converted from three keyword tables into a walk over it;
W23.2 the attachment arm and the diagnostic CLASS tag in legs B and C
(plus the STEP 0 parity fix, below); W23.3 the fourteen productions plus
§2.22's derived-identifier repair; W23.4 `--list-source`'s appended
columns and four `#section` blocks; W23.5 the population check, the
remaining fixtures and spec hunks, and a dry run of the bench's own
41-check acceptance bar. Nineteen fixtures, six sabotage rows
(**S239-S245**, highest on main measured at S238), nineteen SW spec
hunks distributed per step rather than collected at the end, and six
new checks W23-S1..W23-S6.

§0.10 of the design note is the finding-by-finding r58 record and this
report does not repeat it. What follows is what WRITING the plan
revealed.

## 2. Five things the plan surfaced that the brief did not anticipate

### 2.1 The `NF != 15` defect is ALIVE in this repo, and I found it by running the survey rather than by inheriting the lesson

This is the lane's result. §2.24 of the design note carries a
**format-reader survey obligation** — sweep the tree BY GREP for every
site that parses `--list-source`'s SHAPE, not only its content, because
`registry_built_status_memo.md`'s own CORRECTION records the `built`
column's landing missing two readers hard-coding `NF != 15` and the
union battery catching them instead.

I ran it. `tests/rxtsource/run_rxtsource_tests.sh:479-494` asserts:

```awk
awk -F'\t' -v want="$ncols" '
    $2 ~ /^#/ { next }
    NF != want + 1 { print FILENAME ": " $0; n++ }
    END { print "COUNT " n+0 }'
```

**Every non-comment row, unconditionally of kind, must have exactly
`ncols+1` fields.** Four `#section` blocks whose rows are narrower
(`#section aux` is eight columns against the main table's sixteen)
violate that on every row of every section. The check is not wrong about
today's stream; it is unaware the stream can have more than one shape —
which is the same sentence the memo's correction had to write about the
`built` column, one document over and two years of process later.

**Two things make it worse than a red check, and both are in the plan
as W23.4's item 3 rather than left to whoever meets it.** First, the
`fail` message at `:484-492` names exactly one possible cause (*"A field
contained a TAB, which is what the rxt-escape on columns 4, 5 and 15
exists to prevent"*) and helpfully lists the three corpus blocks that
carry a literal tab — so a lane meeting the red after emitting a section
goes and reads the escape function. The message was true when written,
because a field count could only go wrong one way. Second, the check's
own sabotage row (`S202_rxt_manifest_column_dropped.sh`) plants a
dropped manifest column, so the row and the check both live entirely
inside the one-shape assumption.

**The generalisation, since it is the third instance this house has
recorded**: a check that asserts a SHAPE goes stale when the shape gains
a variant, and its FAILURE MESSAGE goes stale with it — the message is
a second, undeclared claim about the space of causes. Repairing the
assertion without repairing the message leaves a check that fires
correctly and diagnoses wrongly, which is worse than one that does not
fire at all.

### 2.2 Three of the four other dump readers are safe BY LUCK, and the invariant that saves them is written nowhere

`run.sh:1651` (`awk '$1 == "pattern"'`), `run.sh:1671` (`IFS=$'\t' read`
keyed on `_k = "target"`) and `run_rxtsource_tests.sh:499` (kind-keyed
counts) all survive four new sections — because every section's first
column is `line`, an integer, which can never equal a main-table `kind`
token. Nothing states that. A fifth section whose first column happened
to be a name would break three readers silently, and `run.sh:1671`'s
failure mode is the silent one: a section data row survives the
`grep -v '^#'` filter, reaches the loop, fails the key test and is
skipped with no signal.

So the note makes it check **W23-S4** — *no `#section` row's field 1 may
equal any main-table `kind` token*, walked off the dump's own header
lines rather than a hand-written list of section names, which would go
stale the day a fifth section lands and be the `NF != 15` shape one
level up. And it adds the ordering rule the readers also rest on
(**sections FOLLOW the main table, never interleaved**, since
`run.sh:1651` takes the FIRST `pattern` row), free today and impossible
to recover once a consumer has seen the other order.

### 2.3 The STEP 0 parity fix belongs in the CLASSIFICATION step, and the reason is structural rather than scheduling

The brief asked me to schedule legs B/C parity for `rxtnul`'s two
refusals. The obvious home is "some harness step"; the right home is
W23.2 specifically, and the argument is one sentence: **that step is
already teaching both legs to attach a CLASS to a refusal, and a
refusal neither leg can currently produce is exactly a refusal with no
class.** Landing the parity fix in the step that builds the
classification machinery means the two new refusals get their class from
the mechanism rather than from a special case.

It also forced a DECIDED point the brief did not contain: **leg B
DETECTS a NUL rather than carrying one.** Bash cannot hold a NUL in a
variable at all, so "leg B stops losing NULs" is either a detection pass
ahead of the per-line loop or a rewrite of a seventeen-arm chain to
carry bytes bash cannot hold, for a population of zero. Detection
restores three-leg agreement, which is the only property the
differential asks for.

And one bookkeeping item that is really a staleness item: the three
fixtures move from `check_refusal` to `check_refusal_all3` **and
`tests/rxtsource/CLAUDE.md`'s leg-A-only scope note is deleted in the
same commit.** A scope note that outlives its scope is the shape this
tree keeps catching; the re-aim and the note's deletion are one edit or
they are two edits and the second never happens.

### 2.4 `pcrec_rxt_source_ncols()` has zero callers, and the check that should use it derives its own

`src/parse/rxt_source.c:2085` exports the column count; the
field-manifest check derives `ncols` from its own hand-pinned `MANIFEST`
string instead. That is CORRECT and deliberate — a check reading the
count from the code it checks would share a source with what it controls
— but it means the exported accessor is dead, and the comment above the
column table still says **"THE 15 COLUMNS"** where the array has
sixteen entries (`export` was appended at W1.3). Neither is a defect
this note fixes; both are named in the file-by-file table so the lane
that opens `rxt_source.c:2074` at W23.4 meets them with an explanation
rather than a puzzle.

### 2.5 The graduation rule's fifth clause is checkable in exactly one direction, and that direction is cheap

§2.27.3 clause 5 is stated over VALUES: *nothing in pcrec may take a
value that changes when an aux body changes, except `#section aux`'s own
faithful rows.* Writing the check plan made clear why that phrasing is
worth more than the four reader-clauses above it: **a code review catches
the patch that reads an aux value; it does not catch the two routes
clause 5 was added for** (an opener-row cardinality; a derived count
pinned in CI), because neither reads an aux body at all. A byte-identity
check over OUTPUTS catches all three, because all three move a value.

So W23-S6 is: edit an aux body, and require every pcrec output except
that section's rows to be byte-identical — the dump with the section
elided, `--list-schema`, every compiled artifact, every diagnostic. Its
own limit is stated rather than tidied: it proves the property for the
EDITS it makes, so the fixture's edit has to move line count, depth, key
spellings AND block count at once, which is the difference between a
check with a population and a check with an example.

**And §3.5 says honestly why that check gets NO sabotage row.** The
plant would be *"make some pcrec output depend on an aux body"*, which
is not a corruption of shipped code — it is the arrival of a feature.
A `mech` row is a planted defect; clause 5's violation is a patch
somebody writes on purpose. The check is the detector and the review is
the gate, and writing that down is better than a row that plants an
arbitrary dependency nobody would have written.

## 3. The self-check sweep

The r58 residue class is DISPOSITION TEXT, and this note is 1,240 lines
of it, so I swept my own file for the three things a reader of an
earlier revision must not carry a memory of.

| grep | hits | verdict |
|---|---|---|
| `configs describe` / `configs build` / `provides` / `capable` / `cross-scope` / `tag-prose` | 9 | **0 live.** Every hit is a WITHDRAWN/REMOVED marker, the "never enters SW13's derived list" statement, the SEVEN-kinds sentence naming `cross-scope`'s absence, §4.3's absence-grep landing condition, or the verbatim bench-facing correction that D1 *"types neither `capable` nor `config`"* |
| `eight kind` / `eight-kind` / `five kinds` / "two parameters" | **0** | the note says SEVEN kinds and THREE parameters throughout |
| `parameter 2` / `parameter 3` / `three parameter` | 9 | all read three-or-parameter-3 correctly; the one `parameter 2` mention outside its own pair rule is §1.6's record of what the reversed decision WOULD have made it return |
| prose near `aux`/`ext` | 3 | all three state the NO answer (§0.4 item 3, the `aux_literal_pipe` row, SW18) |
| table rendering (every table run outside fenced blocks: constant indent + header separator) | — | **0 issues** |

**Citations spot-checked against the tree, not trusted from the survey**:
`run_rxtsource_tests.sh:464` (`MANIFEST`, sixteen names), `:479-494`
(the `NF != want + 1` assertion and its `$2 ~ /^#/` skip), `:484-492`
(the TAB-only failure message), `run.sh:1651-1652` and `:1671-1675`
(the two positional readers), `rxt_source.c:2068` (the stale "THE 15
COLUMNS" comment), `:2074-2082` (sixteen entries) and `:2085`
(`pcrec_rxt_source_ncols`, zero callers). All eight verify exactly as
cited.

## 4. The standing constraints, each discharged explicitly

- **abi is 24 and W23 carries NO abi event.** §1.9 CONFIRMS that from
  the file-by-file plan rather than restating the design's claim: no
  step opens a file under `src/gen/`, `src/ir/`, `src/opt/` or
  `lib/pcrec.h`, and the two files that look like they might are
  `cli/main.c` (dispatches dumps, emits no scaffolding) and
  `tests/harness/driver.c` (links against a matcher, is not part of
  one — `w1_impl.md`'s own F13 treats it the same way). **No
  unavoidable abi event was discovered, so nothing is flagged to the
  manager under that clause.** §8's checklist makes "if a step believes
  it needs one, it STOPS and escalates" a line every step brief carries.
- **D26**: the note specifies diagnostic CLASS (a machine-read tag)
  and never a sentence; §7.3's Q-W23.1 is where the class's own
  user-visibility is left open, and D26 governs wording rather than
  structure either way.
- **The withdrawn mechanisms have no implementation in any step**, and
  §4.3 makes that a *checkable* landing condition on SW19's own model
  (the grep returns 0 over `docs/spec/`, `src/`, `tests/`, `cli/` at
  every step) rather than a promise. §7.1 then says plainly what that
  grep does NOT catch — a sentence describing a withdrawn production as
  current — and names the third pass (read every grep hit against every
  claim that names it) as the only instrument for it.
- **`timeout`**: no command of uncertain length was run. Every command
  this lane issued was a read, a grep or a line count.

## 5. What is owed, and what a fresh agent resumes from

**Nothing is owed by this lane.** Every number in §6's acceptance
sections is a TARGET for its step, not a measurement taken here, and
the note says so in §7.4.

For the manager:

1. **The D6 panel on the note is the next step** (the brief says so).
   §7.1 lists the standing risks and §5.2a of the design note is the
   model — the note is written to be attacked section by section, and
   §1.5 and §3.4 are the two places it makes claims no document handed
   it.
2. **Four questions §7.3 could not settle from the documents**, each
   implemented-with-an-alternative-named rather than left open: whether
   the diagnostic class is user-visible or differential-only; where
   `#section cases` puts a `route` (a block-scoped directive on a
   per-case row — implemented as a denormalisation, and the alternative
   is more faithful and harder to use); whether `--list-schema`'s
   `surface` rows are in-stream or behind a flag; and **whether K57 is
   fixed in this delivery** — recommended NOT, because it is a shipped
   defect with its own entry and fixing it inside a step whose
   acceptance is the structure layer would put two independent reds in
   one step. `prose_dedent.rxtin` ships as a `known_fail`-style cell
   either way.
3. **Three bench-facing corrections** go out over D78 at delivery, and
   §5 carries them with their reasons: **A2's fixture needs two lines
   deleted** (it types `config … testee`/`option`), **B6's premise is
   dissolved** (both pattern spellings are S2 openers, so a second
   opener starts the next block and the refusal has an empty
   population), and **F2's premise is dissolved with the D93-unchanged
   note** (a set file with no configs has no construction for it, and
   F2's literal pass condition still fails for every config-BEARING
   file). A rename the bench never has to make is not a correction and
   is not on the list.
4. **The survey in §1.5 must be RE-RUN at W23.4's own pin**, and the
   note states that as the step's landing condition rather than as
   advice: three steps of checks land between this note and that step,
   and a check added in this very delivery is exactly the kind of reader
   a survey written before it cannot contain. `w1_impl.md` §8.7's
   discipline, applied to a shape instead of to a number — the command
   is the contract, not the list.

Commits on `lane/w23impl`: `f9e523ce` (the note), the CLAUDE.md entry,
and the §1.5 misdirection finding, plus this report.
