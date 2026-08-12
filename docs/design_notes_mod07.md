# MOD-0.7a design note — the `--explain` rewrite — PHASE 1 (design + measurement, no implementation)

Written by the MOD-0.7a design lane, in the git worktree on branch `mod07`,
HEAD `26b9660` (mech completion trailer). Every number below was produced in
that worktree against a `make`-built `build/pcrec` at that commit, and each is
quoted with the command that produced it. Nothing in `src/`, `tests/` or `cli/`
is modified by this phase; the one source edit taken (§0's sabotage) was
applied, measured and reverted with `git checkout`, and the tree is clean.
Baseline recorded after the revert: `make test` on the clean worktree is fully
green (exit 0, zero `FAIL` lines), so every red result quoted below is the
sabotage's and not the branch's.

**Disclosure** (per brief): the only context beyond the brief and this
repository is the standard spawn-time injection — the session-root `CLAUDE.md`
(the repository-scope mandate, restated in the brief) and the memory index
(`pcrec process preferences` / `pcrec project status` / `pcrec check-design
lessons`). The third of those — *"every check this project has built has failed
the same way: a control sharing a source with what it controls"* — is the
sentence §0 below is an instance of, and it is why §0 was measured before
anything else was designed. No other file, review or conversation outside the
brief and the repository influenced this note.

---

## 0. The headline finding, first, because the plan row's own cure has this defect

**The cross-source agreement check the [MOD-0.7] plan row specifies cannot
catch a module-attribution swap. Measured, both directions, at this HEAD.**

The plan row's instruction is: *"print the ROW's declared attribution AND the
recogniser's answer, and assert they agree per row."* Applied literally, the
"recogniser's answer" for a row is a live doorway call, and the doorway renders
its module promise with `snprintf(..., r->module)` from **the same row**
`--explain` would print (`src/parse/ext.c:246`, `:341`). Two hats, one source.

Measured. R10/C4-1's exact sabotage — swap the module strings of two rows in
the `(?<` bucket, `(?<=...)` (lookaround) and `(?<name>a)` (named-groups),
`src/parse/registry.c:475,479` — then re-run the full declared-vs-live census
over all 100 registry rows (`--probe-ask verdict` on each row's own `syntax`,
scraping `module 'X'` out of the live answer and comparing it against the
row's `module` column):

    correct table   93 SAME   6 SILENT   1 NOROUTE
    swapped table   93 SAME   6 SILENT   1 NOROUTE        (census diff: 2 lines,
                                                           both still "SAME")

The live text follows the swap exactly, so agreement stays green on both
sabotaged rows. **A design that stops at "the row and the recogniser agree"
ships R10's disease under R10's own name.**

What the suite ACTUALLY catches, measured on the same sabotaged build (each
suite run individually, because `make test` halts at the first failing one):

| suite | checks run | failures under the swap | what caught it |
|---|---|---|---|
| `tests/cli` case10 | 120 cases | **1** | the `--count-groups '(?<n>a)'` pin — **not** any `--explain` assertion |
| `tests/reject` | 470 | **2** | hand-written pins `reject '(?<=a)' … 'lookaround'` / `reject '(?<n>a)' … 'named-groups'` (`run_reject_tests.sh:604,607`) |
| `tests/registry` `registry_check` + `pcre2_check` | 168 + 154 | **0** | — |
| `tests/registry` doc-index check | — | **1** | the committed generated index in `docs/pcre2_compliance.md` no longer matches `--list-syntax` |

All **eight** of case10's `--explain` CONTENT assertions PASS under the swap
(`--explain exits 0`, `names the owning module`, `carries the PCRE2 semantics`,
`reports (?< as lookaround`, `reports (?< as named-groups`, `reports all four
rows`, `on base syntax exits 1`, `on base syntax says why`), as do its three
`--explain` plumbing assertions. R10's C4-1 reproduces at this HEAD,
independently.

**The design consequence, and it shapes every section below.** The live
invocation is worth building, but for what it actually delivers:

- it delivers **reachability and election** — *which row won for this text*, a
  fact no table read can produce, and one that 13 rows cannot express in text
  at all (§5.3);
- it delivers **promise consistency** — *does the live answer promise a module
  at all*, which is decided by branches in `ext.c` that the row's `module`
  column knows nothing about (`ROADMAP_NEVER`, `RF_CLASS_INVALID`, the option-
  run rejection, unknown POSIX names, the verb name tables). §1 below is a
  LIVE tier-2 defect found by exactly this comparison;
- it does **not** deliver module-name truth. Only a hand-written pin does.
  `tests/reject` is that pin's home and already carries 470 of them; the new
  `tests/cli` case carries a small named subset so that the swap fails there
  too, which is the brief's measured-demonstration requirement, and the note
  says out loud that this is a second home and why (§9.2).

---

## 1. A live defect this comparison finds on the first row it is applied to

    $ build/pcrec --explain '(?C1)'
    (?C1)
      doorway   after '(?'
      status    known, unimplemented — requires module 'callouts'
      …
    $ build/pcrec -o - '(?C1)'
    pcrec: (?C...) is outside pcrec's scope and no module will implement it
           (see docs/pcre2_compliance.md) (pattern offset 0)

`--explain` promises a module for a construct pcrec has decided never to
implement. That is K14's over-promise, which D34 ruling 1 fixed by adding the
`roadmap` axis and which `ext.c:339` honours — and `syntax_dump.c` never reads
`roadmap`, so the query surface still makes the promise the compiler withdrew.
D26 tier 2, in D26's own words: *"Naming a module that will never implement a
construct is a defect."*

Population, measured (`--list-syntax` where `status == module && roadmap ==
never`): **exactly one row today**, `(?C1)`. Small, but it is the defect class
this milestone exists to make visible, it was found by the first application of
the design, and `registry_check`'s K14 branch is explicitly written to cover a
second such row *"the day it exists"* while `--explain` is not.

**Not fixed this phase** (phase 1 writes no code). It becomes the new test
case's first field-level assertion and an open question for the manager (§11.1)
— specifically whether it wants a `K` number, since it is live on `main`.

---

## 2. What `--explain` is today, and the reframe

Today it is a **mutual-prefix match against the `syntax` column** and nothing
else (`syntax_dump.c:266-315`; no `ext_`, `registry_find` or `arbitrate`
reference exists in the function). R10/C4-2 reproduces:

    $ build/pcrec --explain '(?i-m:'
    pcrec: no construct matches '(?i-m:' — it is either base syntax or not a
           construct pcrec knows                                      (exit 1)

while the doorway, asked the same text, has a perfectly good answer:

    $ build/pcrec --probe-ask verdict -- '(?i-m:'
    group  verdict  verdict  1  1  refusal  0  0  0  (?i...) requires module 'modifiers'

**The reframe: a query is TEXT AT A DOORWAY, not a key into a column.** That
one sentence is the whole rewrite. It gives the query a live answer, it makes
D29's worked example run, and it makes `--explain` show the same mechanism the
compiler used rather than a table join that resembles it.

It also has a boundary that must be stated before anything is built: **a query
is not required to be a pattern**. `(?<` is a legal query and an illegal
pattern. The router below is bytewise and never parses, which is what lets a
truncated query still reach a doorway — and it is also why some queries cannot
be answered at all (§3.4), which the design REFUSES rather than fabricates.

---

## 3. The query → doorway mapping

### 3.1 There is already a router, and it must stay the only one

`pcrec_probe_ask` (`syntax_dump.c:348-438`, MOD-0.1 slice 8) already maps a
construct string to exactly one doorway call: a bytewise scan for the first
doorway opener, positions reported in FULL-TEXT coordinates, each branch
placing the cursor exactly where `parse.c` has it at that call site, `(?:`
excluded exactly as `parse.c` excludes it. It is a fifth CALLER of the four
doorways and recognises nothing itself.

**The design reuses it verbatim rather than writing a second one.** Concretely:
extract the scan into a file-static helper in `syntax_dump.c`

    typedef struct { RegKind kind; int sel; size_t at; size_t cursor;
                     bool at_class_open, at_content_start; size_t from; } Doorway;
    static bool doorway_route(const char *text, size_t len, Doorway *d);
    static ExtResult doorway_call(Ctx *cx, const Doorway *d, ExtWant want);

with `pcrec_probe_ask` and `pcrec_syntax_explain` as its two callers. Writing a
second router is the D24 two-homes failure with a new coat: the two would drift,
and the drift would be invisible because each surface would be self-consistent.

**The regression net for that extraction is already built and must be cited in
the phase-2 commit message**: `--probe-ask`'s 10 TSV fields are read by
`tests/spec_mod0/check06` and by case10, which pins one cell byte-exact
(`escape verdict verdict 2 2 refusal 0 0 0 \d requires module 'classes'`), the
field count at 10, both gate cells, and an in-repo cursor sweep over every row
at claim+verdict with the population FLOORED at 198 probes. If `--probe-ask`'s
output moves by a byte, phase 2 broke the router.

### 3.2 The router's fidelity, measured

The question the reuse raises is whether an answer obtained through the probe
router is the answer the COMPILER gives. Measured two ways at this HEAD:

- **every registry row's own `syntax`** (100 rows): compare `--probe-ask
  verdict`'s `(msg, at)` against `pcrec -o - <syntax>`'s `(msg, offset)`.
  **99 identical, 1 no-route** — the no-route is `(?:...)`, which has no
  doorway call at all and compiles. Zero text differences, zero offset
  differences.
- **the hand-listed query set of §3.3** (11 queries, including truncated and
  malformed ones): **11 identical**.

So "live" in `--explain`'s output means the same thing the compiler would say,
for everything measured. The BOUNDARY: this is measured for canonical row
syntaxes and one hand-listed query set. It is not measured — and cannot be in
general — over arbitrary query text, because a query need not be a compilable
pattern and there is then nothing to compare against. §9.4 lists this as one of
the instrument's stopping points.

### 3.3 Which rows a query selects

Two rules are in play and they answer different questions:

- **PREFIX** (today's): rows whose `syntax` and the query are a mutual prefix.
  Answers *"which rows look like what I typed"* — a catalogue.
- **BUCKET** (new): the rows the live arbitration actually considered — every
  row with `kind == route.kind && sel == route.sel`, which is precisely
  `pcrec_registry_arbitrate`'s candidate loop (`registry.c:899-918`), plus the
  kind's `REG_SEL_ANY` row as a last-resort fallback *only when the arbitration
  actually elected it* (arbitrate returns `any` only when no sel-matching row
  answered).

Measured over a hand-listed query set (`|prefix|`, `|bucket candidates|`, and
the union, computed from `--list-syntax`'s own `kind`/`selector` columns and
the router's doorway choice):

| query | prefix | candidates | union | what the difference is |
|---|---|---|---|---|
| `\v` | 1 | 1 | 1 | agree |
| `\d` | 1 | 1 | 1 | agree |
| `(?<` | 4 | 4 | 4 | agree (the catch-all is NOT elected: the bare `<` row answers) |
| `(?P` | 4 | 4 | 4 | agree |
| `[[:alpha:]]` | 1 | 1 | 1 | agree |
| `(?i-m:` | **0** | 1 | 1 | D29's worked example: prefix finds nothing, the bucket finds `(?i)` |
| `(?iZ)` | **0** | 1 | 1 | same shape; the live answer is the catch-all's text (§4.2) |
| `[[:foo:]]` | **0** | 1 | 1 | prefix says "no construct matches" for text the doorway has an opinion about |
| `\p{Foo}` | **0** | 1 | 1 | same |
| `(*NOTAVERB)` | **0** | 0 | 1 | no candidate; the verb row is the elected fallback |
| `\N{U+0041}` | 2 | **3** | 3 | prefix misses `\N{name}` — R10/C1-1's "the bucket has THREE rows" |
| `(?-1)` | 0 | **11** | 11 | the ten `(?-N)` rows plus `(?-i)`, all genuinely arbitrated |
| `(?` | **45** | 0 | 45 | prefix is a catalogue of everything starting `(?` |
| `(?:` | 1 | 0 | 1 | the base grammar answers it; no doorway call exists (§3.4) |
| `a` | 0 | 0 | 0 | not doorway territory; exit 1, today's message (§3.4) |

**Decision: SELECTION = PREFIX ∪ CANDIDATES, and every row carries a `select`
field saying which rule put it there** (`candidate` = in the query's bucket,
`listed` = prefix match only). Reasons, in order:

1. Dropping PREFIX is an unforced behaviour regression: `--explain '(?'` as a
   catalogue is a real use and case10's `(?<` count assertion depends on the
   prefix set. There is no forcing function to remove it.
2. Dropping BUCKET is R10/C4-2 unfixed.
3. Keeping both without a tag would hide the interesting cell:
   `\N{U+0041}`'s third row is a CANDIDATE the prefix rule cannot see, and
   `(?`'s 45 rows are LISTED rows that competed for nothing. The tag is a
   field, it has a reader, and it can dissent (§6).

`(?` printing 45 rows is a wart the union INHERITS and does not create. Left
alone deliberately; narrowing it is a separate behaviour change with its own
argument to make.

### 3.4 What cannot be answered, and is refused rather than fabricated

| query shape | what happens | what `--explain` prints | exit |
|---|---|---|---|
| no doorway opener (`a`, `abc`) | router returns false | today's message verbatim: *"no construct matches '…' — it is either base syntax or not a construct pcrec knows"* | 1 |
| `(?:` | router excludes it exactly as `parse.c` does | the row block (prefix-selected), and a `route` line reading `none — the base grammar answers `(?:` before any doorway is consulted`. **No live block**: there is no call to report, and inventing one would be the dump lying. | 0 |
| a doorway opener but an empty selection (impossible today; every routed query yields at least the elected row) | — | the live block alone, with `rows 0` | 0 |
| **escape at CLASS position** (`[\p{L}]`, `[\d]`) | the router's first opener is `[`, so it lands on doorway 4 and the class-bracket row lookup DECLINES (there is no `RK_CLASSBRACKET` row for `\`) | the honest class-bracket decline. **This is a known non-answer, OUT OF SCOPE for MOD-0.7** — see §10 and §11.3 | 0 |

The class-position gap deserves its own sentence, because it is the one place
where the honest answer is also an unhelpful one. Extending the router with an
in-class escape case would change `--probe-ask`'s routing, and `--probe-ask` is
`check06`'s measurement channel with a floored 198-probe sweep over it. That is
a MOD-0.8 change with its own measurement, not a side effect of a display
rewrite. Until then `--explain` prints the row's declared `class_expect` column
(a libpcre2-measured fact already on the row) and labels it DECLARED.

---

## 4. Per-doorway analysis

For each doorway: the entry point, what its answer contains, what a second
source is (if any), and what agreement MEANS there.

### 4.1 ESC — `pcrec_ext_escape(cx, want, c, in_class=false, at)`

- **Answers.** Arbitration over bucket `(RK_ESC, c)`; 41 rows, no
  `REG_SEL_ANY` row (an unknown escape is `ext.c:156`'s `if (!r)` refusal, not
  a catch-all row). The answer carries: `what` (refusal today for every row at
  the default enabled set; `node`/`members` for module `classes` with the gate
  open), `at` (the blame offset), `msg`, `answered_at`, and — for `\p`/`\P` —
  `mod_uprops`'s refined malformed-vs-unknown-name split with a load-bearing
  offset.
- **Second source.** None for most rows: the message is rendered from the row.
  `\p`/`\P` are the exception — the text and offset come from
  `mod_uprops.c`'s body scanner via the `pcrec_registry_uprops_recognise`
  pointer-identity marker, so the OFFSET is a fact the row does not contain
  (§8).
- **Agreement means.** The row's own `syntax` elects the row itself, and the
  answer promises exactly the row's module iff the row is `RS_MODULE` +
  `PLANNED`. Measured: 41/41 rows SAME except `\N{name}` (`RS_REJECTED`, no
  module declared, no module promised — a SILENT cell, agreeing).
- **`--explain` probes ATOM position only.** `in_class` is false for every
  call. The class-position half is DECLARED-only, from `class_expect` (§3.4).

### 4.2 GROUP — `pcrec_ext_group(cx, want, c2, at)`

- **Answers.** Arbitration over `(RK_GROUP, c2)`; 55 rows, one
  `REG_SEL_ANY` catch-all (`(?q)`, `registry.c:638`). Additional branches that
  answer WITHOUT using the elected row's module: `c2 < 0` ("missing closing )
  for group", the R17 fix), the option-run rejection, and `ROADMAP_NEVER`.
- **Second source, and it is real.** `pcrec_registry_option_run_ok`
  (`mod_modifiers.c`) is a MEASURED GRAMMAR that lives outside the table. For
  `(?iZ)` the elected row is the `i` GROUP_OPT row and the MESSAGE is the
  catch-all row's text — measured:

      $ build/pcrec --probe-ask verdict -- '(?iZ)'
      group  verdict  verdict  1  1  refusal  0  0  0  unrecognized character after (? or (?-

  **This is the cell that defines what `elected` means in the output.**
  `elected` is *the row the doorway chose to dispatch on*, NOT *the row that
  wrote the message*. The two differ here, they are both true, and the display
  must not conflate them — which is why the output carries `elected` and
  `names` (does the answer promise a module, and whose) as two separate fields
  rather than one "attribution" field (§6).
- **Agreement means.** As for ESC, plus: a `ROADMAP_NEVER` row must NOT promise
  its module. That predicate is what §1's defect fails.

### 4.3 VERB — `pcrec_ext_verb(cx, want, at)` (in `mod_verbs.c` since MOD-0.4)

- **Answers.** **No arbitration at all.** One row (`RK_VERB`, `REG_SEL_ANY`,
  syntax `(*ACCEPT)`), and the decision is by NAME through the two `VerbName`
  tables — chosen by the CASE of the first name byte — with four possible
  answers (D25): the module promise, the per-table "not recognized" text,
  `(*MARK)`'s "must have an argument", and the empty-name quantifier error.
- **Second source, and it is the strongest one available.** The `VerbName`
  tables are a genuinely separate schema whose every bit is re-measured against
  libpcre2 by PC-3 on every run, and they carry a PER-NAME `roadmap` the RegRow
  does not. Measured contrast:

      $ build/pcrec --probe-ask verdict -- '(*NOTAVERB)'
      verb  …  refusal  0  …  (*VERB) not recognized or malformed

  The single row DECLARES module `verbs`; the query's live answer promises
  nothing. **That is not a dissent** — it is the name table doing its job, and
  it is exactly why per-row agreement is asserted on the ROW'S OWN SYNTAX and
  never on the query (§5.1).
- **Agreement means.** For the one row: `(*ACCEPT)` elects it and promises
  `verbs`. **Plus a genuine cross-source pair**: when the query's name is in a
  table, `--explain` prints a `verb` sub-block (table, name, forms, unknown-msg,
  roadmap, quantifiable) and asserts `row.roadmap` against `name.roadmap`. This
  is the one doorway where the RegRow alone is a fiction, and the sub-block is
  the same data `--list-verbs` already prints, joined to the query.
  **Slice-able**: if the manager wants MOD-0.7 smaller, the verb sub-block is
  the piece to cut (§11.4); the row-level agreement stands without it.

### 4.4 CLASSBRACKET — `pcrec_ext_class_bracket(cx, want, c2, at, from, at_class_open, at_content_start)`

- **Answers.** `pcrec_registry_find` on `(RK_CLASSBRACKET, c2)`; 3 rows, and
  deliberately **no catch-all** (`registry_check` requires its absence — a
  catch-all would make every unmatched byte in a class a construct). This is the
  only doorway that DECLINES. Answers additionally depend on the K4 extent scan,
  `at_class_open` (which selects `open_msg`), `at_content_start`, and the POSIX
  name table.
- **Second source.** `posix_names[]` — existence AND per-name module
  attribution, PC-3-measured. Measured:

      $ build/pcrec --probe-ask verdict -- '[[:<:]]'
      class-bracket … [[:<:]] is a word-boundary assertion and requires module 'assertions'

  The `:` row declares module `classes`; the live answer names `assertions`.
  **Again not a dissent** — per-name attribution (MOD-0.3a) — and again the
  reason agreement is a row-canonical predicate.
- **Agreement means.** `[[:alpha:]]` elects the `:` row and promises `classes`;
  the two collating rows are `RS_REJECTED` and promise nothing (SILENT cells).
  The `at_class_open` variant is a separate live cell the router reaches for a
  query written `[:alpha:]`; `--explain` reports which variant it probed.

### 4.5 Rows with no callable recogniser

There are none, and the phrase needs retiring rather than answering. `NULL` in
`RegRow.recognise` does not mean "no recogniser": it means
`pcrec_recognise_tail_default` with the row's `tail` as its parameter, which is
total and always callable (`internal.h:798-810`). The genuinely special rows,
and what `--explain` prints for each:

| row kind | example | what `--explain` prints |
|---|---|---|
| tail-less fallback (`recognise` NULL, `tail` NULL, rank 0) | `\d`, `(?<name>a)` | ordinary candidate; it answers "always" and that is CORRECT (D32 §2), so its live block is ordinary |
| MARKER recogniser (`option_run`, `uprops`) | `(?i)`, `\p{L}` | ordinary candidate. The marker always answers true and the real check runs in `ext.c`/the module — so the elected row is the marker's row and the message may come from elsewhere (§4.2). The output's `names` field is what shows this, and the note for these rows says the marker is a marker |
| `REG_SEL_ANY` catch-all (2 exist: `(?q)`, `(*ACCEPT)`) | `--explain '(?'` | printed as `fallback`, and **only when the arbitration actually elected it** — printing it always would assert reachability the arbitration denies (for `(?<`, the bare `<` row always answers, so the catch-all is unreachable there) |
| `RS_BASE` (`(?:...)`) | `--explain '(?:'` | the row block with `status base`, and `route none` with the base-grammar sentence. No live block; §3.4 |

---

## 5. The agreement predicate, and what it can and cannot say

### 5.1 It is evaluated on the ROW'S OWN SYNTAX, never on the query

`--explain` makes **two kinds of live call** and only one of them is an
assertion:

- **LIVE-ON-QUERY** — one call, on the text the user typed. It is DATA. It is
  never compared to anything, because a query legitimately gets an answer its
  bucket's rows do not declare: `(?iZ)`, `(*NOTAVERB)`, `[[:foo:]]`, `[[:<:]]`
  and `\p{Foo}` are five measured cells where that is CORRECT behaviour (§4).
  Asserting agreement there would fire on a correct registry, which is the
  exact shape R10/C1-1 refuted in D29.
- **LIVE-ON-ROW-SYNTAX** — one call per DISPLAYED row, on that row's own
  `syntax` (which `registry.c` already guarantees is a valid probe reaching
  that row's doorway: *"`syntax` must be a pattern that really reaches that
  doorway"*). This one IS the assertion.

### 5.2 The predicate, and the census that establishes it

For a displayed row R, with `L = live answer on R.syntax`:

1. **ELECTION** — `L.row == R`. The row wins its own canonical form.
2. **PROMISE** — `L.msg` names a module **iff** `R.status == RS_MODULE && R.roadmap == PLANNED`.
3. **ATTRIBUTION** — when it names one, the name equals `R.module`.

Measured over all 100 rows at this HEAD (`--probe-ask verdict` on each row's
own `syntax`; the module name scraped from the answer with `module '([^']*)'`):

    SAME     93   live names exactly the declared module
    SILENT    6   live names no module
    NOROUTE   1   no doorway call exists

and the 6 SILENT rows partition exactly along clause 2, with nothing left over:

    \N{name}      esc             rejected  —      "PCRE2 does not support \F, \L, \l, \N{name}, \U, or \u"
    (?PX)         group           rejected  —      "unrecognized character after (?P"
    (?q)          group           rejected  —      "unrecognized character after (? or (?-"
    [[.a.]]       class-bracket   rejected  —      "POSIX collating elements are not supported"
    [[=a=]]       class-bracket   rejected  —      "POSIX collating elements are not supported"
    (?C1)         group           module    never  "(?C...) is outside pcrec's scope and no module will implement it"

Five `RS_REJECTED` rows (no module declared, none promised) and one
`ROADMAP_NEVER` row. **`NOROUTE` is `(?:...)`, the single `RS_BASE` row**, and
it is exempt from all three clauses by construction.

So the predicate is TOTAL over the table, holds 100/100 today, and its
`ROADMAP_NEVER` clause is precisely what §1's display defect violates — the
predicate would print `DISSENT` for `(?C1)` on the CURRENT `--explain`, which
is the "false the day before" property (D33 §9.3) satisfied honestly.

### 5.3 What it can dissent on, and what it cannot

**Can**, with the mechanism named for each:

- a row that no longer wins its own canonical form (recogniser narrowed, tail
  corrupted, rank inverted, row shadowed by a sibling) — clause 1;
- an `RS_MODULE`+`PLANNED` row whose live answer promises nothing (a new
  `ROADMAP_NEVER`, an `RF_CLASS_INVALID`-shaped branch, a name table
  overruling, an option-run rejection swallowing the row) — clause 2;
- an `RS_REJECTED` row that started promising a module — clause 2, other
  direction;
- the `(?C1)` defect of §1 — clause 2, today.

**Cannot**, measured:

- **a module-name swap** (§0). Clause 3 reads `r->module` through `ext.c`'s
  `snprintf` and compares it with `r->module`.
- **anything about whether the module name is the RIGHT name.** libpcre2 can
  say a construct exists; it has no opinion about pcrec calling it
  `recursion`. `tests/reject`'s hand pins are the only source for that, as
  `src/parse/CLAUDE.md` already states.

**Why clause 1 is nonetheless worth its cost, quantified.** Election is not
observable from the message text, because messages are not unique within a
bucket. Measured over the 5 multi-row buckets:

    bucket group sel '-'   11 rows   10 share one rendered message:
                                     "(?-...) requires module 'recursion'"
    bucket group sel '<'    4 rows    3 share one rendered message:
                                     "(?<...) requires module 'lookaround'"
    == 13 rows share a rendered atom diagnostic with a bucket sibling

`registry_check`'s `check_table_to_parser` compares TEXT (it builds `want` from
the row and compiles the row's `syntax`), so for those 13 rows it cannot tell
which row answered. `elected` can. That is the one thing the live call adds
that no existing check has.

### 5.4 `--explain` is not the check, and this section is why (R10 ruling 6)

R10 disposition 6 is explicit: *"Drop `--explain` and module-shipped probes as
controls. Both may exist; neither may be the check."* This design obeys it, and
the obedience is structural rather than promised:

- `registry_check`'s `check_table_to_parser` (row's own syntax → real compile →
  diagnostic matches the row) already owns clauses 2 and 3 as an INVARIANT over
  all 100 rows, in `make test`, with no CLI in the loop. Nothing here retires
  it or duplicates its coverage claim.
- `tests/reject` owns module-name truth (470 hand pins).
- `check_required_rows` owns row EXISTENCE — the hand-written manifest, because
  everything that iterates the table is blind to a deletion.
- What `--explain` adds is a HUMAN SURFACE that shows both sources side by
  side and cannot silently print a fabrication, plus `elected`, which no check
  reads today. Its test case is a surface pin, not the project's guard.

---

## 6. Output format, field by field, with each field's reader

Format grammar (a strict one, so the test can assert per field rather than per
blob):

    <query header>            unindented `key value` lines
    <blank>
    <row block>               first line = the row's `syntax`, unindented;
                              then `  <key><pad><value>` lines, keys from a
                              CLOSED vocabulary; no tabs, no newlines in a value
    <blank>
    <row block> …

Keeping row-block keys indented and header keys unindented is load-bearing:
case10 counts `^  doorway` lines to count rows, and the header must not add
one.

### 6.1 Query header

| field | source | reader, and can it dissent |
|---|---|---|
| `query` | echoed input | new cli case: asserts the echo for a shell-quoted query. Dissents on mangling |
| `route` | live router | new cli case: asserts `after '(?' selector 'i'` for `(?i-m:` and `none — the base grammar…` for `(?:`. Dissents on a routing change |
| `live` | LIVE-ON-QUERY `msg` | new cli case: asserts the exact text for 5 pinned queries (§9.1). Dissents on any wording/branch change |
| `live at` | LIVE-ON-QUERY `at` | new cli case: asserts `7` for `\p{Foo}` and `1` for `[[:foo:]]`. **Offsets are load-bearing** (D26's tension paragraph; the S27 lesson) |
| `live elected` | LIVE-ON-QUERY `ExtResult.row` | new cli case: asserts `(?i)` for `(?i-m:` and `(?<name>a)` for `(?<`. Dissents on an arbitration change the text cannot show |
| `live answered` | `ExtResult.answered_at` | new cli case: asserts `verdict` by default and `result` under `--features classes` for `\d`. The gate, observable — the same cell case10 already pins for `--probe-ask` |
| `rows` | count of displayed rows | new cli case: asserts `4` for `(?<`, `3` for `\N{U+0041}`. Dissents on a selection-rule change |
| `dissents` | count of clause failures | new cli case: asserts `0` on the correct table and `≥1` under each sabotage (§9.2) |

### 6.2 Per row block

| field | source | reader, and can it dissent |
|---|---|---|
| `syntax` (block head) | `RegRow.syntax` | join key; the case addresses rows by it |
| `select` | derived: `candidate` / `listed` / `fallback` | new cli case: asserts `\N{name}` is `candidate` for query `\N{U+0041}` (the row today's prefix rule misses) and that `(?`'s 45 rows are `listed`. Dissents on a selection regression |
| `doorway` | `RegRow.kind` | case10's row COUNTER (`grep -c '^  doorway'`), preserved; new case asserts the value |
| `status` | `RegRow.status` | new cli case: field-level per named row |
| `module` | `RegRow.module` | **new cli case: field-level, hand-pinned for 5 named rows.** This is the C4-1 net (§9.2) — and the pin, not the agreement clause, is what dissents |
| `roadmap` | `RegRow.roadmap` | new cli case: asserts `never` for `(?C1)`. **Not printed today at all**, which is §1 |
| `flavours` | `RegRow.flavours` | new cli case (one row); also the `--flavour` filter's subject, already in case10 |
| `engines` | `RegRow.engines` | printed with its existing "design intent, unconsumed until SR-8" caveat. Reader: case10's existing text assertion only. **Kept for compatibility, flagged as the weakest field here** |
| `note` | `RegRow.note` | case10 asserts `vertical whitespace` for `\v`; new case keeps one such |
| `class` | `RegRow.class_expect` | new cli case: asserts `set 10` for `\d`. Labelled DECLARED — the class-position live probe is out of scope (§3.4) |
| `own` | LIVE-ON-ROW-SYNTAX `msg` | new cli case: exact text for 5 named rows. Dissents on any diagnostic change |
| `own at` | LIVE-ON-ROW-SYNTAX `at` | new cli case: a number for 2 named rows |
| `own elected` | LIVE `ExtResult.row` vs this row | new cli case: `self` for every displayed row across the whole hand-listed query set, counted with a FLOOR. This is clause 1 |
| `names` | derived: which module the live text promises, or `—` | new cli case: `—` for `(?C1)` and `[[.a.]]`, `assertions` for the `[[:<:]]` query cell. This is clause 2's observable |
| `agree` | clauses 1-3 | new cli case: `ok` for every row on the correct table (counted, floored), `DISSENT: …` under sabotage |

### 6.3 Fields deliberately NOT printed, and why

R10 §7's rule is *"not 'is there a reader' but 'can the reader dissent'"*. Three
fields were considered and rejected for having no dissenting reader here:

- **`rank`** — `registry_check`'s `check_row_ranks` owns it, and D32's own
  comment forbids a second global rank sweep (*"R11/M3 measured one redundant
  with the per-row syntax check in all 5,632 probes"*). Printing it would be a
  column whose only reader is the human.
- **`feature`** (the `FEAT_*` mask) — `check_feature_module_bijection` owns the
  feature↔module pairing; the hex mask means nothing to a reader of one row.
- **`tail`** — after MOD-0.2 it is only the parameter of a default recogniser;
  `elected` reports the OUTCOME of the recognition it feeds, which is the fact
  worth showing.

`engines` is printed only because it already is; it is named above as the
weakest field in the output and is the first candidate if the format is ever
trimmed.

### 6.4 Why not TSV

`--list-syntax`, `--list-verbs` and `--probe-ask` are all TSV with an
appended-never-reordered rule, which would make field extraction trivial. It is
rejected here for one reason: those three are DUMPS with format consumers
(SR-4 generates a doc section from one; `check06` parses another), and
`--explain` is a HUMAN answer about one construct with no generated-doc
consumer. The strict `key value` grammar above buys per-field assertion without
turning a readable answer into a spreadsheet. The cost is that the new test
needs a small `explain_field <out> <row> <key>` awk helper, which §9.1
specifies.

---

## 7. The dissent contract and exit codes

**A dissent is a defect surfaced, not a query error.** They get different exit
codes because a script must be able to tell "you asked a bad question" from
"pcrec is inconsistent with itself":

| exit | meaning | stdout | stderr |
|---|---|---|---|
| **0** | the query was answered and every displayed row agrees | the full answer | — |
| **1** | the query could not be answered — no rows selected AND no doorway route; or a CLI misuse (unchanged) | — | today's message, verbatim |
| **3** | the query was answered and at least one displayed row DISSENTS | **the full answer**, with `agree  DISSENT: <clause>: <detail>` on each failing row and `dissents N` in the header | one summary line naming the count and the first failing row |

Rationale for 3 rather than 2: this CLI's usage errors are all exit 1 today,
and 2 is conventionally a usage code in enough tools that reusing it would
invite exactly the confusion this split exists to remove. The value is pinned
by the new case in both directions.

**The dissent text is a diagnostic for a pcrec developer, not a compile
diagnostic**, so D26's tiering applies at tier 3 and the wording is free. What
is NOT free is the CLAUSE identity — a reader must be able to tell election
from promise from attribution — so the three clause names are part of the
format:

    agree     DISSENT: election: '(?-3)' elected '(?-i)' for its own syntax
    agree     DISSENT: promise: declared module 'callouts' (planned) but the live
                       answer promises none
    agree     DISSENT: attribution: declared 'lookaround', live names 'named-groups'

---

## 8. `\p`/`\P` and K16 — exactly what `--explain` claims

K16 (RULED acceptable-until-producer, D26 tier 2) records that 164 of 256
possible `\p{...}` body bytes are libpcre2 ERR 146 AT THE BAD BYTE, where
pcrec's scanner reads past them and answers its own unknown-name/generic
category at the scan-completion offset. **This design neither fixes nor works
around it**, per the brief. What it does is state the claim precisely:

- **`--explain` reports PCREC'S OWN behaviour.** The `live` and `own` text and
  the `live at`/`own at` offsets are what pcrec's `\p`/`\P` scanner answers
  today. They are STABILITY pins, not oracle-agreement pins — the same status
  `tests/reject`'s `\p{!}`/`\p{9}`/`\p{=}`/`\p{Script=Latin}` pins already
  carry. Measured cell the new case pins:

      $ build/pcrec --probe-ask verdict -- '\p{Foo}'
      escape … refusal  at=7 … \p requires module 'unicode-props'

  (and `--explain`'s `live at 7` must equal it). A future K16 fix will move
  this offset for malformed bodies; when it does, this pin moves WITH the fix,
  and the note recording that is here so the next reader does not read it as an
  oracle claim.
- **Module attribution is unaffected by K16** and stays exact: every `\p`/`\P`
  cell names `unicode-props` either way (K16's own text says so). So clauses
  1-3 hold for the `\p`/`\P` rows regardless of the divergence, which is why
  §5's census shows them as ordinary SAME cells.
- **The normalised name is NOT printed. This is a change from the plan row's
  wording and it needs the manager's ruling (§11.2).** Three reasons: there is
  no accessor — `ExtResult` has no name field and `mod_uprops`'s buffer is
  local to the scan; there is no producer, so `aport`/`cport` stay `NO_PORT`
  and the name has no other consumer; and K16 means the accumulated buffer is
  wrong-by-construction for 164 body bytes, so a printed name would be a field
  whose value is a known divergence and whose only reader is the case that
  prints it — R10 §7's eighth column, newly created by the milestone that was
  supposed to close it. Recommendation: defer the field to the first
  `unicode-props` producer, which is where K16's fix already lands.

---

## 9. Test design

### 9.1 A new case, `tests/cli` case11, and case10 gives up the `--explain` content

**Split.** case10 keeps the flag PLUMBING assertions for `--explain`
(`--list-syntax --explain` exits 1, missing value exits 1, `--explain` with `-o`
exits 1) because those belong with the other flag-conflict pins. Every CONTENT
assertion moves to case11 and is rewritten field-level. The reason for moving
rather than adding: leaving case10's eight blob assertions in place beside a
field-level case would leave R10's demonstrated-useless assertions in the suite
as if they were coverage, and the swap demonstration would have two homes with
different answers.

**The helper, because the rule needs enforcing mechanically:**

    # explain_field <output> <row-syntax|@header> <key>  -> the value, or ""
    explain_field() { … awk over the block grammar of §6 … }

and the case's own discipline, stated in its header comment: **no
`assert_contains` against a whole `--explain` output in case11.** Every
assertion names a row and a key. That sentence is the case's reason to exist.

**The hand-pinned row set** (small on purpose, chosen as the rows R10's C4-1
and C4-1b actually used plus the three doorways' representatives):

| row | pinned fields |
|---|---|
| `(?<=...)` | `module lookaround`, `own` text, `own elected self`, `agree ok` |
| `(?<name>a)` | `module named-groups`, `own` text, `agree ok` |
| `\N{U+0041}` | `module unicode-props`, `select candidate` for query `\N{U+0041}`, `agree ok` |
| `\N` | `module classes`, `agree ok` |
| `(?C1)` | `roadmap never`, `names —`, and `agree` — **the §1 assertion** |
| `[[:alpha:]]` | `module classes`, `own at`, `class set …` |

**The pinned query cells** (LIVE-ON-QUERY, exact text + offset): `(?i-m:`
(D29's worked example — the case's headline), `\p{Foo}` (offset 7, §8),
`(*NOTAVERB)` (names nothing), `[[:foo:]]` (names nothing), `[[:<:]]` (names
`assertions`, a module different from the row's — pinned as CORRECT so a future
reader does not "fix" it).

**The floored sweeps** (populations asserted, because an empty sweep prints the
same silence as a passing one — case10's own rule):

- every row's `own elected` is `self`, over the union of every query in the
  hand list: floor on the number of row blocks examined;
- every row's `agree` is `ok`: same floor;
- `dissents 0` in every header.

### 9.2 Failing-direction validation, planned as MEASUREMENTS at landing

Each of these is run at landing and the RESULT recorded in the phase-2 commit
message (not asserted here — this is a plan). Each satisfies D33 §9.3's "false
the day before" honestly, and the first one is stated with its EXPECTED result
because §0 already measured it:

| # | sabotage | must fail | expected, from §0's measurement |
|---|---|---|---|
| **V1** | **C4-1's swap**: exchange `module` between `(?<=...)` and `(?<name>a)` (`registry.c:475,479`) | case11's `module` field pins on both rows | 2 failures. **The `agree` field will NOT fire** — measured in §0, and case11 must be seen to fail on the PINS. If a future reader reports V1 as "caught by agreement", the measurement was misread |
| **V2** | C4-1b's swap: exchange `module` between the `\N` and `\N{U+0041}` rows | case11's `module` pins on both | 2 failures, same mechanism |
| **V3** | delete `roadmap` from the `(?C1)` row's rendering (i.e. restore today's behaviour after §1 is fixed) | case11's `(?C1)` `names`/`agree` assertions | the §1 defect, re-introduced. **False the day before**: it is TRUE on `main` today |
| **V4** | narrow a recogniser so a row loses its own syntax — set the `\N{U+` row's `tail` to `{U+X` | clause 1 (`own elected` ≠ self) on that row, and the floored `self` sweep | election dissent; `check_table_to_parser` may ALSO fire (text changes here), which is fine and is worth recording as an overlap |
| **V5** | invert the `\N{U+`/`\N{` rank pair (D30's measured n=1 sabotage) | clause 1 on one row | D30 measured this as observable on **1 input in 176,544** in a generated sweep; the per-row canonical probe should see it directly. **If it does not, say so** — that is a finding about the instrument, not a nuisance |
| **V6** | make the option-run grammar reject everything (`pcrec_registry_option_run_ok` returns false) | the `(?i-m:` query cell's `live` text | the query-level pin, which no row-level clause covers |
| **V7** | change `--probe-ask`'s routing (the shared router) | case10's byte-exact `--probe-ask` cell AND case11's `route` line | the one-home guarantee of §3.1, in the failing direction |

**V1's expected result is the one to watch.** A phase-2 lane that runs V1, sees
2 red assertions, and writes "the cross-source check caught the swap" will have
recorded the opposite of what happened.

### 9.3 A `mech` `cli` suite type — recommended NOT built this phase

`tests/mech/run_sabotage_matrix.sh` has four suite types (`codegen`, `trie`,
`reject`, `harness`) and no `cli`. Adding one is genuinely small — one `case`
arm in `run_one` invoking `bash tests/cli/run_cli_tests.sh` in the scratch tree
and counting `^FAIL` lines, the same shape the `reject` arm already has. But
V1-V7 above are `registry.c`/`syntax_dump.c` edits whose relevant suite would
be `cli`, so a `cli` arm is exactly what would let them live as S-numbers
rather than as a paragraph in a commit message.

Recommendation: **record it as a MOD-0.8 candidate, and run V1-V7 by hand at
MOD-0.7 landing.** Reasoning: the mech driver builds a fresh tree per sabotage
and `run_cli_tests.sh` compiles generated C in several cases (it is the
slowest non-harness suite), so a `cli` arm has a real runtime cost that should
be measured before seven rows are added to a matrix that runs in `make mech`.
That measurement is not phase-1 work. The brief asked whether this is "genuinely
trivial": the CODE is; the runtime budget is unmeasured, and this project's
rule is not to assert a cost.

### 9.4 What this instrument CANNOT reach — named, because the sweep-template lesson has recurred four times

Stated as boundaries of case11 and of the design, not as future work:

1. **The query set is HAND-LISTED.** Every query in §9.1 was chosen by the
   author of the design. `wake §7`'s rule is generate, never list — and the
   generated query space (all 256 bytes after each doorway opener, times a
   suffix depth) is NOT swept by case11. It is swept by `pcre2_check`'s
   existing doorway sweeps for VERDICTS; nothing sweeps it for `--explain`'s
   SELECTION or `elected`. **A routing or selection bug that affects only a
   byte outside my list is invisible here.** This is K15/K16's shape — the
   instrument stops at the boundary its author was thinking about — and it is
   the most likely place for the fifth recurrence.
2. **The row set comes from `--list-syntax`** — the same table `--explain`
   prints. A DELETED row disappears from both, and case11 cannot see it. Row
   existence is `check_required_rows`'s hand-written manifest and stays there.
3. **Clause 3 cannot dissent** (§0, measured). Module-name truth is
   `tests/reject`'s 470 hand pins and case11's 6-row subset. **94 of 100 rows
   have no module pin in case11**, by design; a swap on any of them fails only
   in `tests/reject`, if `tests/reject` happens to pin that row.
4. **Router fidelity is measured for canonical row syntaxes and one query
   list** (§3.2: 99/99 and 11/11), not for arbitrary text, and not in
   principle — a query need not be a compilable pattern.
5. **Both `--probe-ask` and `--explain` read the SAME router**, so a router bug
   is self-consistent across both surfaces and invisible to any check that
   reads only their output. The independent control is `tests/reject` and the
   `.rxt` corpus, which reach the doorways through `parse.c`'s real call sites
   — a different caller. V7 exists for this reason and is the weakest of the
   seven, because it validates the pins rather than the router.
6. **Class-position answers are DECLARED, never live** (§3.4). `class_expect`
   is libpcre2-measured and `check04` re-verifies it, but `--explain` is
   reporting a column, not an observation, and says so.

---

## 10. Non-goals, stated

- **No K16 fix, no workaround** (§8). The `\p`/`\P` cells pin pcrec's own
  behaviour; the fix lands with the first `unicode-props` producer.
- **No new recogniser behaviour.** No row's `recognise`, `rank`, `tail`,
  `module`, `status` or `roadmap` value changes. `--explain` gains a live
  invocation; the parse front gains at most the `ExtResult.row` field (§6.1)
  and nothing that alters an answer. **Byte-identity of every rendered
  diagnostic is a landing requirement**, evidenced by `tests/reject` (470),
  the `.rxt` corpus and case10's byte-exact `--probe-ask` cell.
- **No fifth doorway, no new router.** One router, two callers (§3.1).
- **No in-class routing** (§3.4) — MOD-0.8 candidate.
- **No `mech` `cli` arm** (§9.3) — MOD-0.8 candidate.
- **D26 tier discipline on all wording.** The row-facing texts are the ones
  `ext.c` already renders and they do not change. The new text — the dissent
  lines, the `route` line, the header keys — is tier 3: a developer-facing
  diagnostic about pcrec's own consistency, with no PCRE2 counterpart to match.
  *"Requires module 'X'" discharges the obligation in full*, and nothing here
  gold-plates it.
- **`--explain` does not become a check** (§5.4, R10 ruling 6).

---

## 11. Open questions for the manager

1. **§1's live defect: does `--explain '(?C1)'` promising module `callouts`
   get a K number?** It is live on `main`, it is D26 tier 2 by D26's own
   wording, and the population is one row. Options: (a) open a K, fix it in
   MOD-0.7 phase 2 as the first row of the rewrite (my recommendation — the
   rewrite reads `roadmap` anyway, so the fix is the design landing rather
   than a separate change); (b) open a K and defer, keeping V3 as the
   false-the-day-before demonstration; (c) treat it as folded into MOD-0.7's
   scope with no K, recorded in the journal only. Note that (a) costs V3 its
   "false the day before" status unless the pin is written and watched failing
   first (the FIX-3 pattern), which is what I would do.
2. **The normalised name (§8).** The plan row lists it as one of the four
   things `--explain` reads from the port; this note recommends deferring it to
   the first producer, with reasons. Confirm the deferral, or rule that phase 2
   should add an accessor and print it with an explicit "pcrec's own,
   K16-divergent for malformed bodies" label.
3. **Class-position queries (§3.4).** Confirm that `--explain '[\p{L}]'`
   answering with the class-bracket doorway's honest DECLINE plus the
   `class_expect` column is acceptable for MOD-0.7, with in-class routing as a
   MOD-0.8 item. The alternative — extending the shared router now — touches
   `check06`'s channel and its floored sweep, which I do not think a display
   milestone should do.
4. **The verb sub-block (§4.3).** It is the only genuinely independent
   cross-source pair available at any doorway (RegRow vs the PC-3-measured
   `VerbName` tables, including a per-name `roadmap` the row does not carry),
   and it is also the most cuttable slice if MOD-0.7 should be smaller. Keep
   or cut.
5. **`--explain '(?'` printing 45 rows (§3.3).** Inherited, not created. Leave
   as is, or narrow the prefix rule to require the query to be at least as long
   as some minimum? I recommend leaving it — narrowing is a behaviour change
   with no forcing function, and the `select listed` tag now makes the 45
   honest about having competed for nothing.
6. **Exit code 3 (§7).** Confirm the value, or say if a dissent should exit 1
   like every other failure and be distinguished by text alone. I recommend 3;
   the distinction is the point of the surface.

---

## 12. Slice plan for phase 2 (AUTHORIZED and BUILT — see §14 and the branch's slice commits)

1. **Router extraction** — `doorway_route`/`doorway_call` as file-statics;
   `pcrec_probe_ask` rewritten onto them with its 10 TSV fields byte-identical.
   Evidence: case10's `--probe-ask` cells and `check06` unchanged and green.
2. **`ExtResult.row`** — the elected row, set at the four doorways' dispatch
   points. Nothing on the compile path reads it. Evidence: byte-identity across
   `tests/reject` + the `.rxt` corpus.
3. **The rewrite** — `pcrec_syntax_explain(query, flavours, &ndissent)`:
   selection (§3.3), the query header (§6.1), row blocks with the row-canonical
   live call (§6.2), the three clauses (§5.2), exit codes (§7). §1's `roadmap`
   fix lands here.
4. **case11** — field-level, with the helper, the pins, the floored sweeps
   (§9.1); case10 loses its `--explain` content assertions.
5. **V1-V7 measured**, results in the commit message; §9.2's warning about V1's
   expected result restated there.
6. **Docs** — `src/parse/CLAUDE.md`'s `syntax_dump.c` entry, `cli/CLAUDE.md`,
   `tests/cli/CLAUDE.md`, `docs/plan.md` STATE flips, and a journal entry.

Optional, manager's call: the verb sub-block (§4.3, OQ 4).

---

## 13. MANAGER RULINGS (2026-08-12) — the note is accepted and phase 2 is authorized

The manager reviewed this note at `f3fc90a` and independently reproduced §1
(the `(?C1)` over-promise against the compiler's no-promise wall) and §2
(`(?i-m:`'s prefix miss against the doorway's live answer) on a main-tree
build, both byte-exact. §0's swap-blindness measurement is accepted as
reshaping the milestone. Recorded here so this note is self-contained for the
R panel.

1. **OQ 1 — the `(?C1)` defect: option (a), fixed in this milestone, NO `K`
   number**, with the FIX-3 pattern made explicit: the case11 pins for
   `roadmap never` / `names —` are written FIRST and run against the
   pre-fix rewrite, and that failure is RECORDED — that is what preserves the
   false-the-day-before evidence, since fixing inside the same milestone that
   found the defect otherwise destroys it. Only then does the roadmap-aware
   rendering land. V3 stays as the re-introduction sabotage at landing. The
   defect is recorded in the journal and will appear in the R-panel close file
   rather than in `docs/known_issues.md`.
2. **OQ 2 — the normalised name is DEFERRED to the first `unicode-props`
   producer.** This SUPERSEDES the [MOD-0.7] plan row's original wording (the
   main-tree plan row is annotated accordingly). K16's linked-pair logic
   applies: the buffer gains its accessor when it gains a real consumer AND
   the K16 fix, together. **Do not add the accessor.**
3. **OQ 3 — class-position queries are DECLARED-only**, answered with the
   honest class-bracket decline plus the `class_expect` column. In-class
   routing is a MOD-0.8 candidate. **The router's routing behaviour must not
   change**; V7 guards that in the failing direction.
4. **OQ 4 — the verb sub-block is KEPT.** It is the only genuinely independent
   cross-source pair in the design and the milestone budget accommodates it.
   If phase 2 runs long, tell the manager before cutting anything rather than
   cutting silently.
5. **OQ 5 — `--explain '(?'`'s 45-row catalogue stays as-is**, with the
   `select listed` tag.
6. **OQ 6 — exit code 3 is CONFIRMED**, pinned in both directions: `0` on
   agreement in case11, and `3` under a sabotaged table measured at landing as
   part of V1-V7 — case11 itself must never ship asserting against a sabotaged
   tree.

**Landing-bar additions** (manager, same review): slice 1's byte-identity
evidence goes in its commit message with NUMBERS, not "green"; slice 2 states
the measured evidence that nothing on the compile path changed; the final
commit carries V1-V7 as a table (sabotage, suite that fired, count) with
§9.2's V1 caveat restated verbatim; and the docs slice records case11's
no-blob-assertions rule, the `explain_field` helper, and §9.4's boundaries in
`tests/cli/CLAUDE.md` — the hand-listed query set named as the instrument's
stopping boundary, so the fifth sweep-template recurrence has a signpost.

---

## 14. V1-V7, MEASURED at landing (phase 2, 2026-08-12)

Each sabotage applied to a FRESH tree from `git archive HEAD` at `9516863` —
never a copy of the working tree, never a reused/reverted one (tests/mech's
[MECH-2] lesson) — built there, with `tests/cli`, `tests/reject` and
`tests/registry` run against it. Failure counts are `^FAIL` lines per suite.

| # | sabotage | cli | reject | registry | which case11 assertions fired |
|---|---|---|---|---|---|
| **V1** | C4-1's module swap, `(?<=...)` lookaround → named-groups | **2** | 1 | 1 | `(?<=...) is module lookaround`; `...and its live answer promises its own module` |
| **V2** | C4-1b's swap, the `\N{U+` row unicode-props → classes | **1** | 7 | 1 | `\N{U+0041} is module unicode-props` |
| **V3** | K14 on the query surface, re-introduced | **1** | **0** | **0** | `(?C1)'s status does NOT promise a module` |
| **V4** | recogniser narrowed: the `\N{U+` row's tail → `{U+X` | **2** | 8 | 4 | `agreement sweep`; `no query dissents (exit 3 count)` |
| **V5** | rank inversion on the `\N{U+` / `\N{` pair | **2** | 8 | 3 | `agreement sweep`; `no query dissents (exit 3 count)` |
| **V6** | the option-run grammar rejects every run | **6** | 27 | 58 | the four `(?i-m:` query-cell pins |
| **V7** | the SHARED router: group cursor `i+1` → `i+2` | **6** | **0** | **0** | `(?<=...) wins its own syntax`; `...promises its own module`; `(?<=...) agrees`; `agreement sweep`; `no query dissents` — **plus case10's byte-exact `--probe-ask` cursor cell** |

**Every one of the seven is caught, and four readings matter more than the
counts.**

**V1 IS THE ONE TO READ CAREFULLY, and §9.2 said so in advance.** Its two
failures are `case11: (?<=...) is module lookaround` (a hand-written pin on the
DECLARED column) and `case11: ...and its live answer promises its own module`
(a hand-written pin on the LIVE text). **The `agree` field did not fire**, and
could not: both of its sides read `r->module`. A reader who reports V1 as "the
cross-source check caught the swap" has recorded the opposite of what happened.
The pins are the net; the clause is not.

**V3 is the sharpest result in the table: 1 / 0 / 0.** The K14 query-surface
over-promise is invisible to `tests/reject` and to all 322 registry checks,
because it is a defect in a DISPLAY that no other suite reads. case11 is its
only net — which is the argument for the case existing, made in the failing
direction rather than asserted.

**V5 answers the open question §9.2 recorded.** D30 measured the `\N{U+`/`\N{`
rank inversion as observable on exactly ONE input in 176,544 in a generated
sweep. The per-row canonical probe sees it directly (clause 1, plus the exit-3
count), so the note's "if it does not, say so" does not need to be exercised.

**V7 confirms the one-home guarantee in the failing direction, and its 6/0/0
shape confirms §9.4's point 5 in the same breath.** Moving the SHARED router's
cursor breaks case10's byte-exact `--probe-ask` cell AND case11's row-level
assertions, so the extraction cannot drift unnoticed. It also touches nothing
in `tests/reject` or `tests/registry` — both of those reach the doorways
through `parse.c`'s real call sites, so the router genuinely has no
independent control outside the CLI surfaces. That is the boundary §9.4 named,
now with a number on it.
