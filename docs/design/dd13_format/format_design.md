# [DD-13b] Design note — the grown `.rxt` format: grammar and semantics

**Status: DESIGN, for the [DD-13b.panel] D6 adversarial panel. NO PARSER IS
WRITTEN** (plan.md [DD-13]: "NO parser is written before (c) closes").

This note designs the grammar and semantics of the unified
pattern-source / test-carrier / bench-set file format, under the rulings
Frank gave on 2026-08-28 (`usecases_and_outline.md` §5 as amended by §6.1
through §6.5) and against the requirements [DD-13a] measured
(`requirements.md`: R-RXT-*, R-VE-*, R-VG-*, R-BENCH-*, R-GEN-*,
R-SUBST-*, R-COMPAT-1; tensions T-1..T-6; anti-requirements AR-1..AR-7;
OD-1..OD-6).

**The rulings are not reopened.** Where this note departs from the
position paper, it departs from the paper's *own* provisional choices,
never from a ruling, and says so at the point of departure with the
measurement that forced it. There are four such departures and they are
listed in §0.3.

## 0. How to read this

### 0.1 Claim marking

Every load-bearing claim in this note is one of three kinds, marked:

- **MEASURED** — a command was run in this worktree on 2026-08-29 and its
  output is quoted. Commands are given so the panel can re-run them
  (requirements.md §13 item 5 asks exactly this).
- **CITED** — quoted from a ruling, decision, or spec, with its id.
- **ARGUED** — reasoning from the above. An argued claim is the panel's
  natural target and is marked so it is not mistaken for either of the
  others.

### 0.2 The design in one paragraph

A `.rxt` file gains a **HEAD** (file-level declarations and `config` /
data blocks, everything before the first `pattern` line) above the
**BODY** it already has (pattern blocks, unchanged). Ten new line kinds
and three new block kinds live in the head or as block-scoped lines;
today's thirteen line kinds and their semantics are untouched, so all
179 files / 3,265 blocks / 26,691 expectation lines parse and mean
exactly what they mean now (MEASURED, §1.1). Composition is
**PCRE2's own `(?&name)`**, and the format's contribution is not a new
in-pattern syntax but a **definition-injection rule**: the referenced
definition closure is appended to the pattern text as a
`(?(DEFINE)…)` block **at the END**, which makes the composed pattern
plain PCRE2 the oracle can check directly, makes the primary's capture
numbering stable with the definitions appended at N+1.. — D39.2's
appended-numbering rule, obtained from PCRE2's own left-to-right
numbering rather than implemented (MEASURED, §2.3) — and makes a
name collision between a pattern's own group and a definition
**impossible by construction** rather than by a rule the format has to
enforce (§2.4). Build declarations are file-level `target <prefix> =
<name> [with <config>…]` triples (Frank §6.4); pattern blocks carry no
build marker at all. Everything a pcrec-bench sidecar carries today
becomes lines beside the pattern (§4.5, field by field against the live
`subbench.toml`).

### 0.3 Where this note departs from the position paper

| # | the paper said | this note says | forced by |
|---|---|---|---|
| D-a | "A pattern's OWN groups keep priority over libraries" (§2 wave 1) | there is no priority: a name declared by a named group in the pattern text is resolved **lexically and never looked up**, so it is never injected and the two never meet. A name that IS injected and IS also declared lexically cannot arise | MEASURED §2.4 — the composed form is REFUSED by pcrec ("two named subpatterns have the same name"), so "priority" was never available |
| D-b | `config` is wave 3 (§2) | a **minimal `config`** (pcrec option lines only) is **wave 1**, beside `target … with` | CITED: `docs/spec/limits.md` "Handling an oversized artifact" already tells users to put `--max-emit-bytes=N` "in the pattern-source file's `config` block"; a shipped spec has made the promise. Plus Frank §6.4's own words ("I want to specify the options for them") |
| D-c | OD-5's premise, inherited from requirements R-VE-8: "subroutine-call semantics are ATOMIC and shift capture numbering" | **BACKTRACKABLE, and capture-transparent**, on 10.46 | CITED, MEASURED by an earlier lane: `subroutines_design.md` §3.2 (four isolated cells + four atomic controls) and §3.1 (a live-ovector callout trace). OD-5's own tag is "measured, never read from docs" — this is that measurement, already taken |
| D-d | `include` "splices a file's blocks"; nothing said about a second include of the same file | a second `include` of the same resolved path in one closure is **REFUSED** | ARGUED from learnings §3 / K35: both alternatives (splice twice, silently ignore) change a population nobody counts |

### 0.4 What this note does not design

- The **template's internal grammar** (`$1`, `${name}`) — R-SUBST-1 says
  do not, and this note does not. §4.6 states the slot only.
- **Diagnostic wording** — D26. This note says what must be refused and
  what a refusal must name (the file, the line, the construct), never how
  the sentence reads.
- **[DD-11]'s definition table** — §4.2 states what this format needs
  from it as an interface. D85 rules its shape; the design is [DD-11]'s.
- **The bench record's schema** — the bench owns it (D78). §4.5 states
  what the format must be able to say so the record can key on it.

---

## 1. Grammar

### 1.1 The base, restated as a testable invariant

**R-COMPAT-1 (existing files valid, unmodified, semantically unchanged)
is the first-class invariant of this design.** It is stated here as
something a check can fail:

> **INV-COMPAT.** For every `.rxt` file in `tests/`, the grown parser
> produces exactly the block sequence, directive values and expectation
> list that today's `tests/harness/run.sh` parser produces, and
> `tests/harness/verify_rxt.py` re-verifies the same 26,691 expectations
> to the same answers.

**How it is tested (three checks, not one, because one would share a
source with what it controls — learnings §3):**

1. **Re-parse differential.** A dump mode on each parser emits a
   canonical, order-preserving serialisation of what it parsed (block
   index, `file:line`, pattern text, every directive with its value,
   every expectation with its fields). The two dumps must be
   **byte-identical** over all 179 files. This is the check that catches
   a silently changed value.
2. **Answer re-run.** `run.sh` over the whole corpus under the grown
   parser must report the same pass/fail/pending counts, the same
   `pattern-compile failures (distinct)`, and the same
   `group cases pending-vm` (three numbers `run.sh` already prints —
   `tests/harness/run.sh:1030-1051`). This is the check that catches a
   parse that is faithful but routed differently.
3. **Oracle re-run.** `verify_rxt.py` over the corpus must report the
   same verified count and the same skip count. This is the check that
   catches a change in what a subject's bytes decode to.

**The counted denominator is asserted in all three** (the [DD-13c] lesson:
"without them the value comparison would have been vacuously true"): each
check fails if it saw fewer than 179 files, 3,265 blocks or 26,691
expectations. A check that runs on an empty corpus must be red.

**Sabotage rows for INV-COMPAT** (each must turn the corresponding check
red, and the check that must catch it is named — a row no check catches is
a finding about the check set):

| row | plant | must be caught by |
|---|---|---|
| S-C1 | drop the last `g` line of one block | (1) dump differential, (2) count |
| S-C2 | decode `\x41` as the two characters `x41` | (1) dump differential, (3) oracle |
| S-C3 | let `flags` carry forward to the next block | (1) dump differential |
| S-C4 | treat `# pcre2-only` as an ordinary comment | (3) oracle skip count |
| S-C5 | make `frames-buffer=` block-scoped rather than positional | (1) dump differential |
| S-C6 | accept an unknown `features` name silently | (2) — a `perr` block flips |

**MEASURED — the base vocabulary is closed and small.** The complete set
of first tokens over all 179 corpus files, with counts:

```
$ find tests -name '*.rxt' | wc -l                      -> 179
$ (python3 census, first token of every non-blank non-# line)
m 10552  n 6780  g 3942  pattern 3265  ns 3167  features 2146
ms 1603  perr 384  gp 240  flags 36  gu 23  engine 5  budget 3
frames-buffer=<6 distinct values> 8
blank lines 3820   whole-line comments 10585
blocks 3265   expectation lines (m+n+ms+ns+g+gp+perr+gu) 26691
```

Thirteen line kinds, one of which (`frames-buffer=`) is spelled
`key=value` rather than `keyword args` and is **positional within a
block, not block-scoped** (`docs/spec/rxt_format.md`). That wart is
inherited unchanged; the new grammar does not add a second `key=value`
line kind, so `frames-buffer=` stays the sole exception rather than
becoming a precedent.

**MEASURED — every proposed new keyword is unused as a first token.** All
21 candidates, over all 179 files, count **0**:

```
$ for w in name target lib include config use variant oracle tag mc \
           freq gap def with from testee option repl s sg serr unsupported; do
      echo "$w $(grep -rh "^$w\b" tests --include='*.rxt' | wc -l)"; done
  -> every one 0
```

This retires the requirements-note appendix bullet "keyword-collision risk
between reserved directive words and named definitions is unexamined
(R27 F10)": examined, and the answer is that the risk cannot arise from
*names* at all, because a definition's name never appears in first-token
position (it is the argument of `name`, of `target … = <name>`, or the
body of a `(?&name)` inside a pattern), and it cannot arise from the new
*keywords* because none of them occurs today.

### 1.2 The file shape

```ebnf
file        = head , body ;
head        = { head-item } ;
body        = { pattern-block } ;

head-item   = file-decl | config-block | data-block ;
pattern-block = pattern-line , { block-line } ;
```

**The head ends at the first `pattern` line, and nothing file-level may
appear after it.** This is AR-4 discharged mechanically: a D27-blinded
author reading any block needs to look in exactly one other place — the
top of the file — and that place is bounded. It is also what makes a
one-block file with no head behave exactly like `pcrec 'pattern'`
(AR-2/AR-7).

Lexical rules, unchanged from today and binding on every new line kind:

- Whole-line `#` comments only (R-RXT-2). A `#` anywhere but column 1 is
  data. The one comment with meaning — `# pcre2-only` immediately before
  a `pattern` line — keeps it, and is defined in §2.9 as an alias.
- Blank lines ignored.
- A line kind is its first whitespace-delimited token. An unknown first
  token is a **hard error** (R-RXT-6's discipline generalised): never a
  silent no-op, never a comment.
- No line continuation. No multi-line string. **No value in this format
  spans a line** — §7 Q1 records why, and what prose does instead.
- **Four lexical CONTEXTS, each with a closed vocabulary.** The format
  already has two — the file's own directives and a pattern block's
  case vocabulary (`m`/`n`/`g`/…). This design adds two more (`config`
  body, data-block body). A first token unknown *in its context* is a
  hard error that names the context ("`testee` is not a pattern-block
  directive"). Nothing is a keyword everywhere.
- **Leading whitespace on a line inside a `config` or data block is
  permitted and ignored** — a readability convention only, never
  significant. MEASURED: **0** lines in the 179-file corpus begin with
  whitespace (`grep -rhcE '^[[:space:]]+[^[:space:]]'` → 0), so this
  cannot change the meaning of any existing line.

### 1.3 The productions

Each production carries its wave: **W1** composition, **W2** large and
generated sets, **W3** per-engine / per-config application. A parser may
ship W1 alone and reject W2/W3 keywords with "not in this build"; the
grammar is designed so that is a *subset*, never a *dialect of a
dialect*.

```ebnf
(* ---------- terminals ---------- *)
ident       = ( "A".."Z" | "a".."z" | "_" ) , { "A".."Z" | "a".."z" | "0".."9" | "_" } ;
                              (* a PCRE2 group name AND a C identifier *)
int         = "0".."9" , { "0".."9" } ;
rest-of-line = ? every byte to the end of the line, verbatim ? ;
subject     = quoted-subject | file-subject ;
quoted-subject = '"' , { subject-char | escape } , '"' ;    (* today's, unchanged *)
escape      = '\"' | "\\" | "\n" | "\t" | "\r" | "\f" | "\v" | "\x" , hex , hex ;
file-subject = '@file:"' , path-chars , '"' ;                              (* W2 *)
path-ref    = '"' , path-chars , '"'                    (* local, C's "" *)
            | "<" , store-name , ">" ;                  (* library path, C's <> *)
config-list = ident , { "," , [ ws ] , ident } ;
tag-pair    = tag-key , "=" , tag-value ;   (* tag-value: no whitespace, no '=' *)

(* ---------- file ---------- *)
file          = head , body ;
head          = { file-decl | config-block | data-block } ;
body          = { pattern-block } ;

(* ---------- head: file-level declarations ---------- *)
file-decl =
      "lib"     , ws , path-ref                                    (* W1 *)
    | "include" , ws , path-ref                                    (* W2 *)
    | "target"  , ws , ident , ws , "=" , ws , ident ,
                  [ ws , "with" , ws , config-list ]               (* W1 *)
    | "use"     , ws , config-list                                 (* W3 *)
    | "oracle"  , ws , oracle-spec                                 (* W3 *)
    | "tag"     , ws , tag-pair , { ws , tag-pair } ;              (* W2 *)

oracle-spec = "python" | "pcre2" | "none" , ws , rest-of-line ;    (* W3 *)

(* ---------- head: config block ---------- *)
config-block = "config" , ws , ident , [ ws , "from" , ws , config-list ] , eol ,
               { config-line } ;
config-line =
      "pcrec"    , ws , rest-of-line          (* raw pcrec flags        W1 *)
    | "flags"    , ws , letters               (* as a pattern block's   W1 *)
    | "features" , ws , module-list           (* as a pattern block's   W1 *)
    | "engine"   , ws , ( "vm" | "dfa" )      (* as a pattern block's   W1 *)
    | "budget"   , ws , budget-item           (* as a pattern block's   W1 *)
    | "freq"     , ws , ident                 (* select a data block    W2 *)
    | "testee"   , ws , engine-ref            (* a non-pcrec engine     W3 *)
    | "option"   , ws , tag-pair ;            (* that engine's options  W3 *)

engine-ref = ident , [ "/" , version-chars ] ;      (* e.g. pcre2/10.42 *)

(* ---------- head: data block (the analysis FAMILY, §2.10) ---------- *)
data-block = data-kind , ws , ident , eol , { data-line } ;
data-kind  = "freq" ;                    (* the family's only member    W2 *)
data-line =
      "question" , ws , rest-of-line     (* what this answers, required *)
    | "reader"   , ws , rest-of-line     (* the selection point, required *)
    | "exemplar" , ws , rest-of-line     (* provenance, required *)
    | "bytes"    , ws , int              (* provenance, required *)
    | "sha256"   , ws , hex64            (* provenance, required *)
    | "analyzer" , ws , rest-of-line     (* provenance, required *)
    | "date"     , ws , iso-date         (* provenance, required *)
    | "row"      , ws , int , ws , int , { ws , int } ;  (* offset, then 16 counts *)

(* ---------- body: a pattern block ---------- *)
pattern-block = "pattern" , ws , rest-of-line , eol , { block-line } ;
block-line =
    (* --- today's, unchanged --- *)
      "flags"    , ws , letters
    | "features" , ws , module-list
    | "engine"   , ws , "vm"
    | "budget"   , ws , budget-item
    | "frames-buffer=" , route
    | "perr"
    | "m"  , ws , subject , ws , int , ws , int
    | "n"  , ws , subject
    | "ms" , ws , int , ws , subject , ws , int , ws , int
    | "ns" , ws , int , ws , subject
    | "g"  , ws , slot , ws , span
    | "gp" , ws , slot , ws , span
    | "gu" , ws , giveup-code , ws , subject
    (* --- new --- *)
    | "name"    , ws , ident                                       (* W1 *)
    | "tag"     , ws , tag-pair , { ws , tag-pair }                (* W2 *)
    | "mc"      , ws , subject , ws , int                          (* W2 *)
    | "oracle"  , ws , oracle-spec                                 (* W3 *)
    | "variant" , ws , ident , ws , variant-body ;                 (* W3 *)

variant-body = "unsupported" , ws , rest-of-line          (* a declared refusal *)
             | rest-of-line , [ eol , "groups" , ws , group-map ] ;
group-map    = ident , "=" , int , { "," , ident , "=" , int } ;
```

**That is the whole grammar: six file-level declarations, two head block
kinds, five new block-scoped lines.** Thirteen additions against
thirteen existing line kinds — the format roughly doubles, once, and
each addition answers a named consumer in `requirements.md`.

### 1.4 Which production earns which wave, and who is waiting

| wave | productions | the consumer that earns it | blocked row |
|---|---|---|---|
| **W1** | `name`, `lib`, `target … [with]`, `config` with `pcrec`/`flags`/`features`/`engine`/`budget`; `(?&name)` file-scope resolution; `rx_info.name` | a file carrying several patterns that reference each other; a shipped library a user `lib`s and builds three targets from | **[LIB]** (all three parts), [DD-14]'s multi-pattern files |
| **W2** | `include`, `@file:` subjects, `mc`, `tag`, the `freq` data block and `config`'s `freq` line | a generated 1,364-row expectation set; a 1 MB subject; an exemplar findings file | **[ENG-PGO]** (the findings file — its plan row says "blocks on [DD-13b] wave 2/3"), the first in-format sub-bench |
| **W3** | `use`, `oracle`, `variant`, `config`'s `testee`/`option` | a second engine in one file | **pcrec-bench** sub-benches with a non-pcrec testee |

**W1 is a departure from the position paper's wave assignment for
`config`, and the reason is a shipped promise** (D-b in §0.3):
`docs/spec/limits.md`, "Handling an oversized artifact", already
instructs callers to "put the override in the pattern-source file's
`config` block rather than on the command line". A spec that ships an
instruction owes the mechanism. `config`'s wave-3 half (`testee`,
`option`) stays wave 3 — it has no consumer until a second engine does.

D77 is honoured at the wave granularity, not the production granularity:
each wave ships when its named consumer is real, and nothing in W2 or W3
is built to be ready.

---

## 2. Semantics

### 2.1 Scope: two levels, and exactly one cascading thing

Frank's ruling 4: two scopes only (file-top, block); cascade only inside
`config … from`; `include` is pure splice. Concretely:

- **File scope** is the head. Its declarations apply to the whole file
  and to everything spliced into it by `include`.
- **Block scope** is a pattern block. Block-scoped lines **reset at each
  `pattern` line** — R-RXT-1, unchanged, and it now covers `name`,
  `tag`, `oracle` and `variant` too. `frames-buffer=` keeps its
  positional-within-the-block exception.
- **There is no section scope and no case scope.** OD-1 asked where
  options may be declared; the answer is file and block, and `include` +
  `with` supply what a section scope would have (§2.6).
- **The one cascade is `config <name> from <a>, <b>`**: `a`'s lines,
  then `b`'s, then `<name>`'s own; later wins per option. T-4 is resolved
  by construction — the resetting default and the accumulating cascade
  are *different constructs*, so neither has to become the other, and no
  existing file opts into the second (MEASURED: `config` appears 0 times
  in the corpus).

### 2.2 Names: four namespaces, and one rule for all of them

The format declares four kinds of name. Each is declared by exactly one
construct and referenced from exactly one kind of site, so a reference is
never ambiguous about which namespace it is in:

| namespace | declared by | referenced from | shape |
|---|---|---|---|
| **definition name** | `name <ident>` in a pattern block | `(?&n)` / `(?P>n)` / `\g<n>` / `\g'n'` inside a pattern; `target … = <n>` | PCRE2 group name |
| **config name** | `config <ident>` | `with <list>`, `use <list>`, `from <list>` | ident |
| **data name** | `freq <ident>` (the family, §2.10) | a `config` block's `freq <ident>` line | ident |
| **target prefix** | `target <ident> = …` | `pcrec --target <ident>`; the emitted C symbols | C identifier |

**One rule governs all four: a duplicate declaration within the
resolution scope is REFUSED BY NAME, never shadowed.** (Frank's §2 wave 1
ruling for definitions; extended to the other three because the reasons
are the same and a parallel mechanism would be exactly what memory
`pcrec-general-mechanisms-not-special-cases` forbids.) The resolution
scope is:

- definition names: the file's own blocks, then its `lib`s in declaration
  order, transitively. Two *different files* defining one name is a
  refusal; the *same file* reached twice by two paths that resolve to one
  real path is one contribution, not a duplicate.
- config, data, target: the **include closure** (§2.5), which is one
  flat space — an included fragment cannot declare any of them (§2.5), so
  in practice this is the entry file plus its `lib` chain for definitions
  and the entry file alone for the other three.

**Two identities, deliberately kept apart** (Frank §6.3): the **prefix**
is the link-time identity (`<prefix>_search`, unique per translation
unit); `rx_info.name` is the **runtime identity** — the block's `name`,
or the prefix when the block is unnamed. They are equal by default and
differ exactly where they must: one definition built under two configs is
two artifacts with two prefixes and one `rx_info.name` (§2.7).

### 2.3 Reference resolution and the expansion — the heart of the design

**The format adds no in-pattern syntax** (Frank's ruling 2). What it adds
is a rule for turning a block plus the file's definitions into **one
plain PCRE2 pattern**. That pattern is what the oracle checks, what pcrec
compiles, and what `A == B` splice-vs-linkage controls compare — the
harness's expansion is the control by construction ([LIB] plan row).

**EXPAND(block B) is defined as:**

1. **L** = the names declared by named groups in B's pattern text
   (`(?<n>`, `(?'n'`, `(?P<n>`).
2. **R** = the names referenced by a *by-name* subroutine call in B's
   pattern text — `(?&n)`, `(?P>n)`, `\g<n>`, `\g'n'` — with **n ∉ L**.
   *Numeric, relative and whole-pattern call forms* (`(?1)`, `(?-1)`,
   `(?+1)`, `(?R)`, `(?0)`, `\g<0>`, and their leading-zero spellings)
   are **never** file references: they are lexical by definition and are
   left alone.
3. Each n ∈ R resolves against §2.2's definition scope. Not found → a
   refusal (§2.11 says how it is scored). Found twice → refused by name.
4. Close transitively: a resolved definition's own text is scanned the
   same way, its lexical names are its own, and its unresolved references
   resolve **in the scope of the file that defines it** (a library's
   internal references are the library's business — this is what makes a
   library self-contained).
5. **Emit `B ++ "(?(DEFINE)" ++ (?<d>…) for each d in closure order ++ ")"`.**
   Closure order is **first-reference order over a depth-first pre-order
   traversal**, starting from B's pattern text left to right. This is
   what makes R-VE-5's requirement hold — "re-ordering an unrelated part
   of the file must not silently renumber an unrelated pattern's
   captures" — because the order is derived from *reference positions*,
   not from file order.
6. **If R is empty, EXPAND(B) is B's pattern text, byte for byte.**

**MEASURED — why the DEFINE block goes at the END.** Four spellings of
one composition, compiled by `build/pcrec -p rx --features all` and run
through `tests/harness/driver.c` (script in the session scratchpad;
`RX_NCAPS` read from the artifact's own `gen.h`, never assumed):

| # | pattern | subject | `RX_NCAPS` | result |
|---|---|---|---|---|
| E | `^(\d+)-([a-z]+)$` (hand-inlined control) | `12-abc` | 3 | `match 0 6  0 2  3 6` |
| **F** | `^(\d+)-(?&w)$(?(DEFINE)(?<w>[a-z]+))` | `12-abc` | 3 | `match 0 6  0 2  -1 -1` |
| G | `(?(DEFINE)(?<w>[a-z]+))^(\d+)-(?&w)$` | `12-abc` | 3 | `match 0 6  -1 -1  0 2` |
| H | `^(\d+)-(?&w)$(?:(?<w>[a-z]+)){0}` | `12-abc` | 3 | `match 0 6  0 2  -1 -1` |

**F is the design. G is why the prefix spelling is wrong**: with the
DEFINE block in front, the definition takes group 1 and the primary's own
`(\d+)` **shifts to 2**. Every `g <slot>` line in a file would change
meaning the day the file gained a definition. With the block appended,
the primary keeps 1..N and the definitions append at N+1.. — **which is
exactly D39.2's appended-numbering rule, obtained from PCRE2's own
left-to-right numbering rather than implemented.** H shows the
`(?:…){0}` spelling is an exact alternate; F is chosen because
`(?(DEFINE)…)` is what a reader recognises and because it is
`recursion`'s own registry row, `built` (MEASURED,
`build/pcrec --list-syntax`: `group ( (?(DEFINE)(?<w>a)) recursion …
built`, described there as "the same thing `(?:BODY){0}` means").

**MEASURED — the composed answer is capture-transparent, and that is a
real difference from inlining.** Same script, a definition whose body
itself captures:

| # | pattern | subject | `RX_NCAPS` | result |
|---|---|---|---|---|
| I | `^(\d+)-(([a-z])+)$` (inlined control) | `12-abc` | 4 | `match 0 6  0 2  3 6  5 6` |
| J | `^(\d+)-(?&w)$(?(DEFINE)(?<w>([a-z])+))` | `12-abc` | 4 | `match 0 6  0 2  -1 -1  -1 -1` |

The definition's groups exist as slots and read **unset**, because a
subroutine call is capture-transparent — CITED and MEASURED by an
earlier lane on libpcre2 10.46 (`subroutines_design.md` §3.1: a
`pcre2_set_callout` live-ovector trace showing the callee's write and the
return's restore; "the capture state after the call is exactly the state
before it, whatever the call did"). **This is the one place composition
is not the same as textual substitution**, and it is PCRE2's semantics,
not pcrec's invention: a user who hand-writes the same DEFINE form in
PCRE2 gets the same answer.

**And a subroutine call is BACKTRACKABLE, not atomic** — CITED,
`subroutines_design.md` §3.2, four isolated cells against four atomic
controls on 10.46 ("PCRE2 was atomic here before 10.30"). This
**retires OD-5's premise as stated in R-VE-8** ("subroutine-call
semantics are ATOMIC and shift capture numbering"): of the two claimed
consequences, atomicity is false on the current PCRE2, and the numbering
shift is an artefact of where the DEFINE block is written — appended, it
*is* D39.2's rule. OD-5's own instruction was "measured, never read from
docs"; §0.3 D-c records that the measurement exists and this note is
built on it.

**So the answer to "when is the format's reference a PCRE2 subroutine
call, and when is it substitution": it is ALWAYS a PCRE2 subroutine
call, and never substitution.** The format never rewrites pattern text
except by appending a DEFINE block. Three consequences worth stating
because they are what the panel should attack:

1. **Match semantics are preserved because they are PCRE2's.** The
   expanded text is a legal PCRE2 pattern; the oracle can be handed it
   unchanged; nothing about pcrec is assumed.
2. **The cost is PCRE2's too.** A call-linked search does ~2× the
   backtracks of the same language inlined (CITED, `subroutines_design.md`
   §3.2 T7, monotone over 1..8 call sites, measured with PCRE2's own
   `match_limit`). Whether pcrec pays that is a *lowering* question, not
   a format question: `src/opt/callgraph.c`'s `cg_eligibility` already
   splices an acyclic callee under a node budget (CITED,
   `subroutines_design.md` §6.3a), and a splice preserves
   capture-transparency through its own `SLOT_SPLICE_SAVE` family. The
   format pins the *answer*; the compiler chooses the *linkage*.
3. **The expansion is the contract, and dead-capture elision lives below
   it.** MEASURED, the [DD-14.G] bar is **not met by expansion alone
   today**: `^[a-z]+@[a-z.]+$` emits 11,262 bytes with `RX_NCAPS 1`,
   while `^(?&local)@(?&domain)$(?(DEFINE)(?<local>[a-z]+)(?<domain>[a-z.]+))`
   emits 11,922 bytes with `RX_NCAPS 3` — 40 diff lines apart. That gap
   is [DD-14.G]/[V-E]'s to close (splice + dead-capture elision), and
   this note states the constraint it must close it under: **elision may
   change the emitted code; it may not change `RX_NCAPS` or any slot's
   value**, because those are the expansion's observable contract and a
   caller reads them.

### 2.4 Collisions: the format does not need a shadowing rule

**MEASURED.** A definition and a lexical group with the same name, in the
composed text, is refused by pcrec — in both orders:

```
$ build/pcrec ... '^(?<w>x)(?&w)$(?(DEFINE)(?<w>[a-z]+))'
pcrec: two named subpatterns have the same name
       (write (?J) before this declaration to allow duplicates) (pattern offset 27)
$ build/pcrec ... '(?(DEFINE)(?<w>[a-z]+))^(?<w>x)(?&w)$'
   (the same refusal)
```

So "a pattern's own groups keep priority over libraries" (the position
paper's §2) was never an available semantics — there is no priority,
there is a refusal (§0.3 D-a). **The design avoids the situation instead
of ruling on it**: step 2 of EXPAND excludes names in **L**, so a name
the pattern declares itself is *never looked up and never injected*, and
the collision cannot arise.

**MEASURED — this is exactly what the existing corpus needs.** Across all
179 files, **143 blocks** carry a by-name subroutine reference, and
**exactly 4** reference a name their own pattern does not declare:

```
tests/recursion/d27/sr_refusals.rxt:153  ^(?<w>a)(?&nope)$     perr
tests/recursion/d27/sr_refusals.rxt:158  ^(?<w>a)(?P>nope)$    perr
tests/recursion/d27/sr_refusals.rxt:163  ^(?<w>a)\g<nope>$     perr
tests/recursion/d27/sr_refusals.rxt:168  ^(?<w>a)\g'nope'$     perr
```

All four are `perr` blocks whose whole purpose is the refusal of an
undefined name, in a file that declares no `name` and no `lib` — so the
file scope is empty, `nope` stays unresolved, and the refusal is
preserved. **The other 139 have R = ∅ and expand to themselves, byte for
byte.** That is not a survey result that might have gone otherwise: a
block whose by-name reference did not resolve lexically would refuse
today, and the corpus is green, so R = ∅ is *forced* for every
non-`perr` block in it.

**The one hazard, and why it is self-detecting.** If
`sr_refusals.rxt` ever gained `name nope`, those four blocks would
resolve, compile, and their `perr` assertion would go **red** — loudly,
at the block that changed meaning. No new check is owed; the existing
assertion is the check. (This is the K35 shape — a population whose
meaning depends on something elsewhere in the file — and it is worth
stating that it landed on the loud side by construction, not by luck: a
`perr` block's expectation is *falsified* by resolution succeeding.)
