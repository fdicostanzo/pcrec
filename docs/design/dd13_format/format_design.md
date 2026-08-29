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

### 2.5 The include model

`include <path-ref>` splices the referenced file's **blocks** as if they
had been written at that point.

- **Path spelling** (Frank §6.1, C's model): `include "rel/path.rxt"` is
  resolved relative to **the directory of the file that names it** —
  including when that file is itself a fragment; `include <name>` is
  searched on the library path (pcrec's shipped store, then each
  `--lib-path DIR` in order), with `.rxt` implied, and is **never**
  relative to the including file.
- **What an included file may contain: pattern blocks and `include`
  lines. Nothing else.** No `lib`, `target`, `config`, `use`, `oracle`,
  file-level `tag`, no data block. ARGUED from AR-4: a fragment that can
  redefine file scope makes a block's meaning depend on which file
  spliced it, which is exactly the cross-file context a D27 author must
  not need. Nested `include` is allowed because a splice of a splice is
  still only blocks.
- **A second `include` of the same resolved real path in one closure is
  REFUSED**, naming both sites (§0.3 D-d). The two alternatives —
  splice twice, or silently ignore — respectively double a population
  and hide one, and learnings §3 is a catalogue of exactly that failure.
  `lib`, by contrast, **is** idempotent: it declares, it does not splice,
  and the same file reached by two paths is one contribution.
- **Cycles are refused**, naming the cycle (R-VE-7's requirement, one
  level up: the *file* graph as well as the *reference* graph must be
  statically analysable).
- **A fragment is not an entry file.** §2.11 states the rule and why it
  has to be a rule rather than a directory convention.

### 2.6 Config scoping and precedence

A **cell** is the unit that gets compiled and run: a (block, option-set)
pair. Today every block is exactly one cell. Configs multiply cells.

- **`with c1, c2` on a `target` COMPOSES**: one artifact, one option set,
  `c1` then `c2`, later wins.
- **`use c1, c2` ENUMERATES**: one cell per named config. ARGUED: `with`
  builds a single artifact and so needs a single option set, while `use`
  says "run these cases under each of these", which is plural by nature
  — and `use`'s consumer is the bench, where the point is that pcrec and
  pcre2-jit are *different testees*, not a composition.
- **`config c from a, b`** expands to `a`'s lines, then `b`'s, then `c`'s
  own. Cycles in `from` are refused.

**Composition is per option kind, not one blanket rule**, because the
kinds are not alike:

| option | how a config and a block compose | why |
|---|---|---|
| `features` | **UNION** — a config's modules are ADDED to the block's | enabling a module cannot change what an already-compiling pattern matches; it can only change what is refused. This is what a testee needs: pcrec-bench's `subbench.toml` records that `--features all` "is a build/run flag of the TESTEE, not a variant of the pattern, and the pattern text handed to pcrec is byte-identical either way" |
| `flags` | **more specific wins** (block over config over default) | `flags i` changes what the pattern *matches*; a block that states it has stated the test's meaning |
| `engine`, `budget` | more specific wins | as above |
| `pcrec <raw>` | config only; accumulated along the chain, later wins per flag | a block has no spelling for these, so there is nothing to conflict with |
| size-limit overrides (`--max-emit-bytes=N`, `--max-emit-code-bytes=N`) | **raise-only at every scope** (D84) | CITED, `docs/spec/limits.md`: "raise-only (a value below the default is refused, so these can never be used to make a build fail that would have succeeded)". Precedence may therefore never *lower* an effective cap; a chain that tries is refused, not silently ignored |

**A `perr` block is evaluated in exactly ONE cell** — its own options
composed with the file's default — and is **never re-run under a `use`
or `target` config. ARGUED, and it is load-bearing**: `perr` asserts a
refusal *under a stated option set* (R-RXT-6: "a dropped flag would
compile a different automaton and the block's expectations would then be
verified against something nobody asked for"), so re-running it under a
testee's `--features all` would assert something nobody wrote — and
MEASURED, it would silently change the meaning of **384** blocks. Under a
non-pcrec testee a `perr` is meaningless in any case.

### 2.7 Targets, `rx_info.name`, and how many `.c` files come out

A **target** is a file-level declaration, never a block marker (Frank
§6.4, which supersedes the paper's §2/§6.2/§6.3 block-scoped `target`):

```
target <prefix> = <name> [with <config>[,<config>…]]
```

- `<name>` is any definition in scope — this file's or a `lib`'d one. A
  library declares no targets; a user file declares the targets it wants
  from the library, under the user's own configs. This is Frank's own
  case ("there is a set of lib patterns I want to include in my compiled
  file but I want to specify the options for them").
- `<name>` may be declared **after** the `target` line (the head precedes
  the body); resolution is a whole-file pass, so forward reference is
  normal, not an exception.
- **Several targets may name one definition**: `target email_avx2 = email
  with avx2` and `target email_base = email with baseline` are two
  artifacts, two prefixes, one pattern, and `rx_info.name == "email"` in
  both. A duplicate **prefix** in the include closure is refused.
- **Compatibility default** (Frank §6.4): a file with no `target` line
  and exactly one **unnamed** block is `target rx = <that block>` —
  today's `pcrec 'pattern'`, and the CLI's `-p` still overrides the
  prefix for that case. **Every other file builds nothing unless it says
  so.** MEASURED, this is the right default for the corpus: all 179 files
  have several unnamed blocks and none declares a target, so
  `pcrec --source tests/base/quantifiers.rxt` emits **nothing** rather
  than 90 artifacts. Test compilation is untouched — the harness compiles
  every block with cases, as it does today; target-ness and testability
  are independent bits (T-1/OD-4, §5).
- **One `.c` per target** (Frank's ruling 6). `pcrec --source f.rxt
  --target <prefix> -o out.c` selects one; with no `--target`, every
  declared target is built, one file each. A single multi-pattern
  **unit** stays [V-E]'s question (§4.4).
- **`rx_info` gains `const char *name`** (Frank §6.3): the block's
  `name`, or the prefix when the block is unnamed, so no artifact ever
  carries a NULL name. This is a scaffolding change and therefore **an
  `abi` bump under D76's ritual, in the same change**, at all four sites
  CLAUDE.md names: `src/gen/emit_dfa.c`'s `.abi` (currently **11**,
  MEASURED at `src/gen/emit_dfa.c:1310`), `tests/codegen/run_codegen_tests.sh`'s
  [DD-14.FB] §10.4 expectation, `docs/spec/match_api.md` §6, and the
  identity gate's (B) pin. It rides W1's first landing, not a separate
  event (memory `pcrec-abi-changes-pre-release`).

### 2.8 Exemplar-file addressing (`@file:`)

`@file:"path"` is a subject, usable wherever a quoted subject is —
`m`, `n`, `ms`, `ns`, `mc`.

- **Local spelling only** (Frank §6.1: "`@file:` subjects are always
  local (quoted spelling only — a subject is data, never a library)").
  There is no `<>` form.
- **Relative to the file that names the subject**, so a spliced
  fragment's paths are relative to the fragment, not to the entry file.
- **The file's bytes ARE the subject.** No escape decoding, no newline or
  encoding transformation, NUL-safe — T-5's requirement, and the same
  discipline `tests/harness/driver.c` already keeps for inline subjects
  ("the decoded bytes may include `\0`, so it never uses `strlen`",
  `docs/spec/rxt_format.md`). The asymmetry is deliberate and must be
  stated in the spec: a *quoted* subject's escapes are processed, a
  *file* subject's bytes are not.
- **The format imposes no size limit.** §3 records the driver-protocol
  change this forces — today a subject travels as an `argv` string, which
  can carry neither a NUL nor a megabyte.
- **No content hash on a subject reference.** ARGUED, and it is the
  principle §2.10 turns on: **provenance is required exactly where the
  source is not committed.** A subject file sits in the repo beside the
  `.rxt` and is covered by the same review and the same history; an
  exemplar deliberately is not.

### 2.9 The oracle declaration

`oracle python` (the default) | `oracle pcre2` | `oracle none <reason>`,
file-level or block-scoped, block wins.

- **`# pcre2-only` immediately before a `pattern` line stays valid and
  means `oracle pcre2` for that block.** MEASURED: **636** occurrences
  across the corpus; not one of them changes.
- `oracle none <reason>` is a **counted, printed** skip — AR-3, and the
  same shape as `# pcre2-only`'s counted skip and PC-3's loud `SKIP:`
  lines. R-RXT-7's obligation is unchanged: an exclusion still owes a
  `docs/dev/upstream_issues.md` entry.
- **An absent oracle degrades to a labelled skip, never a silent pass and
  never a hard failure** (R-VG-3, the PC-3 discipline) — a stranger's
  clone without libpcre2 must still exit 0 with its skips named.
- **`oracle` never selects what pcrec compiles.** It selects what the
  expectation is checked against. The distinction matters for `variant`
  (§4.5): a testee's variant is checked against the *canonical*
  expectations, which the *canonical* oracle produced.

### 2.10 The data-block family, and its membership rule

Frank ruled the exemplar-analysis findings file **is** an `.rxt`, and
that the analysis block is a **family with a membership rule**: an
analysis is included only when it answers a **specific question a named
selection point asks**, with its value **measured first** (D77) — never
on plausibility.

**The rule is made structural, not editorial.** A data block's
`question` and `reader` lines are **required**; a block without them is
refused. `question` states what it answers; `reader` names the selection
point that consumes it. "A block nobody reads is not emitted" is then a
parse-time fact rather than a review convention.

**`freq <name>` is the family's only member today**, and it is earned:
it answers "which byte is rarest", which the rarest-byte candidate-scan
selection ([OPT-A]/D21) asks, and D83 already rules that analysis runs
outside pcrec and arrives as a findings file. Its body is
**16 `row` lines of 16 counts each**, offset-labelled — 256 counts.

**OD-6 is disposed of** (§5): inline values, not `@file:`; and a
**namespace of its own**, not `config`'s (§2.2). Inline, because the
findings file is the **committed artifact and the exemplar is not**
(Frank) — a table that referred out to a second file would reintroduce
exactly the uncommitted dependency the ruling removes, and 256 counts is
~2 KB of text a person can read. Its own namespace, because a `config`
block's `freq <name>` line names a data block and nothing else, so there
is no ambiguity to resolve and no reason to make `config prod` and
`freq prod` collide.

**Provenance is required** — `exemplar`, `bytes`, `sha256`, `analyzer`,
`date` — because the exemplar is absent by design (proprietary, secret,
or too large). The table can then be re-derived when the exemplar is at
hand and **reads honestly when it is not**. A byte histogram is 256
counts and effectively non-reversible, so committing it leaks
essentially nothing; committing it *without* provenance would be the
population-nobody-counted hazard one file over.

**`gap` — the illustrated second member — is NOT specified here.** Frank
named it as an illustration ("I'm just illustrating that there may be
more than frequency, not saying what"), its question is real (how far a
`memchr` for a byte skips, and how bursty its occurrences are — which
frequency cannot answer: equal means, different shapes), and its
**value has not been measured**. D77 says wait. The family's grammar
admits it as one new `data-kind` with its own body when it is earned;
this note adds no production for it.

### 2.11 Population accounting: the summary unit once includes and cells exist

T-6 is the tension the requirements note flagged and no requirement
anticipated: today the accounting unit is the FILE, because
`tests/harness/run.sh` runs one worker per file
(`tests/harness/run.sh:184-216`) and each worker prints its own summary.
Includes break that, and configs break it a second way.

**Three rules, each stated so a check can fail:**

1. **The accounting unit is the INCLUDE CLOSURE, reported under the ENTRY
   file's name.** A failure always prints its own `file:line` — the
   fragment's, not the entry's — so a person can find it; the *tally* is
   the entry's, so a run's totals do not depend on how a set is split
   across files.
2. **An entry file is a discovered file that is not included by any entry
   in the run.** Discovery already excludes by directory
   (`find … -not -path "*/known_fail/*"`), but a *directory* rule for
   fragments would be exactly the role-by-filename convention the
   position paper's §4 rejected for the sidecar. So: resolve includes
   first, subtract the included set, and **report both numbers** —
   `entry files: N` and `fragments spliced: M` — so a set that silently
   stops being spliced is visible instead of merely smaller (K35). A file
   named explicitly on the command line is always an entry, because the
   user asked for it.
3. **A cell is (block, config), and cells are counted.** Today
   cells == blocks. Once `use` and `with` exist, a summary that counts
   only cases hides its own denominator — the [DD-13c] lesson in one
   line ("the [agreement] denominators were arithmetic over bucket sizes
   … they are COUNTED at the comparison sites now").

**The failure taxonomy grows from three to four.** R-RXT-9's three
(pattern-compile failure, harness-level failure, ordinary case failure)
gain **RESOLUTION failure**: an unresolved name, a duplicate name, a
reference or include cycle, a duplicate target prefix, a config `from`
cycle, an unreadable `@file:` path.

- It is **reported separately** in the summary, so R-RXT-9's
  separate-attributability obligation holds at the new boundary.
- It is **scored as a pattern-compile failure for the block** — which is
  what preserves the four `sr_refusals.rxt` `perr` blocks (§2.4): "this
  pattern does not compile" is true whether the resolver or pcrec said
  so, and a `perr` block must not care which.

**Two accounting facts from today's format that the requirements note
recorded as gaps, and that are already closed** (both worth stating so
[DD-13b]'s design is not built on a stale premise):

- **R-RXT-8's "expected give-up" gap is closed.** `gu <code>
  "<subject>"` exists, is specified (`docs/spec/rxt_format.md`), and is
  MEASURED at **23** uses; `engine vm` (5) and `budget` (3) are the
  directives that reach the path. `subroutines_design.md` §10.3's "THE
  HARNESS GAP: there is no way to EXPECT a give-up" is likewise closed.
  pcrec-bench's `gave-up` outcome (its §4.4) therefore maps onto an
  existing directive, not a new one.
- **`gp`'s pending-VM bucket is the model R-RXT-5 asks a successor to
  keep**, and this design keeps it untouched: `g` out of range is a hard
  failure, `gp` out of range is a counted third state, `gp`
  self-activates when the artifact grows. Nothing in W1..W3 touches it.

### 2.12 Diagnostics: the offset must come home

pcrec reports pattern offsets into the text it was given. Once the format
expands, that text is not the text the user wrote. MEASURED, the
collision refusal in §2.4 reads:

```
pcrec: two named subpatterns have the same name … (pattern offset 27)
```

— offset 27 of a 45-byte expanded pattern the user wrote as a `pattern`
line and a `name` line in two different places, possibly in two different
files.

**The obligation** (not the wording — D26 keeps that out of scope): the
expander keeps a **span map** from byte ranges of the expanded text to
the (file, line, offset-within-that-line's-text) they came from, and
every diagnostic carrying an offset is rewritten through it. A refusal
that lands inside an injected definition must name **that definition's
own `file:line`**, not the referencing block's.

This is small — the expansion is a concatenation, so the map is one
interval per participating text — and it is the difference between a
composable format and one whose errors are unreadable. It is also the
one piece of machinery the format layer owes that has no analogue in
today's harness, and §3 lists it as such.

---

## 3. Migration

### 3.1 The existing corpus: nothing changes

**No existing line changes meaning, and no existing file changes at
all.** §1.1 states this as INV-COMPAT with three independent checks and
six sabotage rows; §2.4 shows the only construct that could have
interacted — the 143 blocks carrying a by-name subroutine reference —
is untouched, because 139 of them resolve lexically (so R = ∅ and the
expansion is the identity) and the other four are `perr` blocks in a
file with no definitions.

The corpus is **179 files / 3,265 blocks / 26,691 expectation lines**
(MEASURED 2026-08-29). The [DD-13a] census read 54 / 1,100 / 9,977 on
2026-08-17; the corpus has grown 3.3× in twelve days, which is exactly
why requirements.md §13 item 5 told the panel to re-run it rather than
trust it. **AR-1's cost of getting this wrong has tripled since the
requirement was written.**

### 3.2 What the harness must gain

In dependency order. Each item is a *change to the harness*, not to the
format, and each is named so a lane brief can be written from it.

| # | change | wave | touches |
|---|---|---|---|
| H1 | **A head parser**: parse file-level declarations and `config`/data blocks above the first `pattern`; hard-error on an unknown first token per context | W1 | `tests/harness/run.sh` |
| H2 | **The resolver and expander**: L/R computation over a pattern's text, definition lookup, transitive closure, DEFINE-append, and the **span map** (§2.12) | W1 | new; shared by the harness and, later, `pcrec --source` |
| H3 | **Cells**: run a block once per resolved config; report cells in the summary; the `perr` one-cell rule | W1 | `run.sh` summary + dispatch |
| H4 | **`verify_rxt.py` reads the EXPANDED text.** The oracle must see what pcrec sees, which is what makes the expansion the splice-vs-linkage control by construction ([LIB]). python `re` has **no** subroutine call at all (CITED, `subroutines_design.md` §10.1: "not different semantics, an ABSENCE"), so **any block with R ≠ ∅ is `oracle pcre2` whether or not it says so** — a python oracle cannot check a composed pattern, and pretending otherwise would be a silent pass | W1 | `verify_rxt.py` |
| H5 | **Include resolution + entry-set subtraction + closure accounting** (§2.11) | W2 | `run.sh` discovery |
| H6 | **`@file:` subjects — and the DRIVER PROTOCOL CHANGE they force.** Today a subject travels as `argv[1]` (`t <subject> [startpos] [route]`), which can carry neither an embedded NUL nor a megabyte. The driver needs a form that names a path and reads it byte-exactly — the natural spelling is a leading sentinel on the existing argument (`t @<path> …`), which is additive and leaves every existing invocation untouched | W2 | `tests/harness/driver.c`, `run.sh` |
| H7 | **`mc` find-all counting** against `match_api.md` §3.1's restart semantics | W2 | `driver.c` |
| H8 | **`tag` well-formedness only** — the harness validates the *shape*, never the vocabulary | W2 | `run.sh` |
| H9 | **Data-block parse + `--exemplar`-shaped hand-off to pcrec** (D83's flag takes the findings file, never the raw text) | W2 | `run.sh`, pcrec CLI |
| H10 | **`use` / `variant` / `oracle` / testee configs** | W3 | `run.sh` + a non-pcrec adapter, which is pcrec-bench's, not pcrec's |

**H4 deserves its own line in a brief**, because it is the one place a
plausible implementation is silently wrong: handing python `re` the
*unexpanded* text would make it compile the primary alone (the `(?&n)`
raises `re.error`, so it would be skipped rather than mis-verified —
but a *skip* that nobody counted is AR-3's failure mode exactly).

### 3.3 What `--list-*` surfaces are affected

- **No existing surface changes.** `--list-syntax`, `--list-axes` and
  the other registry surfaces describe *constructs and axes*, and this
  design adds no construct: `(?&name)`, `(?(DEFINE)…)` and the named-group
  spellings are already registry rows, already `built` (MEASURED,
  §2.3).
- **`--list-definitions` is [DD-11]'s fifth registry surface** (D85), and
  the format is one of its two readers, not its author. §4.2 states the
  interface.
- **New, and owed by this row when W1 lands**: a way to ask a *file* what
  it declares — the targets, their prefixes, their configs and their
  definitions — because a build system needs it and because a person
  needs to check that a target list says what they think. It reads the
  parsed file, so it has **one derivation and two readers** (learnings
  §3): the same resolver the harness runs. It is named in §7 Q3 rather
  than specified, because its consumer ([V-E]'s build integration) is not
  real yet and D77 applies.

### 3.4 The spec delta (D80: the contract changes in the same change)

`docs/spec/rxt_format.md` is the contract, and a parser landing without
its spec hunk is rejected on sight (D80; CLAUDE.md's situation index).
The hunks, named so a reviewer can check them off:

| # | hunk | wave |
|---|---|---|
| S1 | "The `.rxt` format" gains **HEAD and BODY**: the head's six declarations, the two head block kinds, and the rule that the head ends at the first `pattern` line | W1 |
| S2 | A new section, **"Composition"**: EXPAND's six steps, the DEFINE-append rule with the numbering consequence, the four namespaces and the refuse-never-shadow rule, and the statement that a composed block's oracle is necessarily `pcre2` | W1 |
| S3 | "How the harness evaluates a block" gains the **cell** notion and the `perr` one-cell rule; the summary's reported quantities grow (entry files, fragments, cells, resolution failures) | W1 |
| S4 | The **subject** subsection gains `@file:"path"`, and states the escape asymmetry (quoted subjects decode escapes, file subjects do not) | W2 |
| S5 | "The driver protocol" gains the `@<path>` argument form and its byte-exactness guarantee | W2 |
| S6 | A new section, **"Data blocks"**: the family, the membership rule (`question`/`reader` required), `freq`'s body, and the provenance fields with the reason they are required | W2 |
| S7 | The `oracle` line and `# pcre2-only`'s status as its alias | W3 |
| S8 | `variant` and the declared-`unsupported` outcome | W3 |
| S9 | `docs/spec/match_api.md` §6: **`rx_info.name`**, and the `abi` bump sentence — one of D76's four sites, all four in the same change | W1 |
| S10 | `docs/spec/limits.md` "Handling an oversized artifact" item 1 already promises the `config` block; when W1 lands, that sentence stops being a forward reference and gains a pointer to S1 | W1 |
| S11 | `docs/spec/cli.md`: `--source`, `--target <prefix>`, `--lib-path DIR` | W1 |

`docs/guide/` is the human tier and points at these; it never restates
them (D80).

---

## 4. The seams

Each seam is stated as an **interface** — what this format needs from the
other row, or what the other row may rely on — never as that row's
implementation.

### 4.1 [LIB] — subpattern libraries

**[LIB] is what W1 exists for**, and it is `STATE:not-started` blocking
on this note ("depends on rxt format" — the row BLOCKS on [DD-13b]).
All three of its parts are covered by W1: (1) a file carrying several
patterns that reference each other is `name` + `(?&name)`; (2) a user
including a library and calling its subpatterns by name is
`lib "path"` / `lib <name>` + `(?&name)`; (3) a shipped **library store**
is the `<>` spelling's search path — pcrec's shipped store first, then
each `--lib-path DIR` in declaration order.

**What [LIB] may rely on:** a library file is an ordinary `.rxt`; it
declares definitions with `name` and carries their own tests as ordinary
cases; it declares **no targets**, and its tests **do not run** in a file
that `lib`s it (they run when the library file is itself under test —
which is what makes the store's "each entry oracle-verified" discipline
mean something). The library's internal references resolve in the
library's own scope (§2.3 step 4), so a library is self-contained and a
user cannot accidentally satisfy a library's reference from their own
file.

**What [LIB] must decide, not this note:** the store's location and
versioning ([DD-3]), whether `pcrec_options` gains a definitions input
and what `--lib FILE` means at the library API level, and the store's
authoring discipline (a D27-blinded author per entry). The format's
answer to "where do definitions come from" is a file; whether the C API
accepts them another way is [LIB]'s.

### 4.2 [DD-11] / D85 — the definition table

D85 rules that the replacement model is a **predicate-scanned table** on
[ENG-FORM]'s shape, and names this format as one of its readers:
"[DD-13b]'s `name`/`lib` resolution and the [LIB] store read the same
table (a library definition is a row whose predicate is the library's
presence)."

**What this format needs from [DD-11]** — the interface, stated as this
side of the seam:

1. **A lookup**: `resolve(name, option-scope) -> definition text in core
   syntax, or not-found`. That is the whole surface. The format's
   resolver (§2.3 step 3) calls it; it does not walk the table itself.
2. **Determinism and orderability**: the table's answer for a given
   (name, option scope) must be stable across a compile, and when two
   rows could apply the table's own first-applicable-wins rule decides —
   the format never breaks a tie.
3. **A duplicate report**: the format must be able to ask whether a name
   is defined by more than one *file* in its scope, because that is
   refused by name (§2.2). D85 already frames a library definition as a
   row with a predicate, so "two libraries define `email`" is two rows
   with the same key — the table must say so rather than silently
   ordering them.
4. **Nothing about the option-scoped rows.** `$` under `(?m)`, D66's
   assertion expansions, the possessive desugaring: the format neither
   sees nor spells those. They are the table's other customers.

**The reverse direction**, worth stating because D85's revisit-when
raises it: *"[DD-13b]'s wave 1 needs `name` resolution before [DD-11]
exists (then the table's first rows are library definitions and the
option-scoped rows follow)."* This note's recommendation is the
opposite order where it is free: W1's resolver is ~50 lines of name
lookup over parsed blocks, and building it *as* the table's first
consumer costs nothing extra — but if [DD-11] has not opened when W1
lands, W1 ships its own lookup behind interface (1) above, and [DD-11]
replaces the implementation without touching the format. That is
implement-then-replace, which memory
`pcrec-general-mechanisms-not-special-cases` permits explicitly, and it
keeps [LIB] from waiting on a second design.

### 4.3 [ENG-PGO] / D83 — the findings file

D83 rules the analysis runs **outside** pcrec, once per exemplar file,
delivering a **findings file pcrec accepts**, and that the file-general
and pattern-specific analyses are two files and two builds. Frank then
ruled the findings file **is** an `.rxt`.

**The interface**: the findings file is an `.rxt` whose head carries one
or more data blocks and whose body is empty. A user's file brings it in
with `include "…freq.rxt"` (or `lib`, if the same file also carries
definitions), a `config` selects a table by name (`freq loglines`), and a
`target … with <config>` builds a pattern against it. **The same pattern
built against two exemplars is two `target` lines** — which is the
property that made the target-as-declaration shape right (Frank §6.4).

**What [ENG-PGO] may rely on**: the block's shape and its required
provenance (§2.10); that the harness never interprets the table beyond
well-formedness; that the **analyzer is the only writer** of a findings
file (the R30 lesson: an archiver is the only writer of its output, and a
hand edit there is a red line — provenance imitation is worse than
absent provenance).

**What [ENG-PGO] owns**: the analyzer, D83's `--exemplar FILE`-shaped
flag, the built-in static fallback table when no findings file is given,
and — under D77 — whether any *second* family member is ever earned.
Its plan row says it blocks on "wave 2/3"; on this design it blocks on
**W2** alone.

### 4.4 [V-E] — the manifest, the finder, and compilation units

[V-E]'s manifest **is** the target list. Frank §6.4: "the target list IS
the manifest — one line per artifact, all at the top of the file."

- **R-VE-1** ("N named patterns → one emitted unit, perhaps several") is
  answered at the format layer by **one `.c` per target** (Frank's ruling
  6) and left open at the codegen layer: a single multi-pattern *unit* is
  [V-E]'s charter, and the format does not prejudge it — several targets
  in one file are several artifacts *by default*, which a later
  unit-emitting mode can group without any change to the declarations.
- **R-VE-2 / AR-2** (no dispatch for the statically-known single-pattern
  call) is preserved by §2.7's compatibility default: a one-unnamed-block
  file with no head is `target rx`, its expansion is the identity
  (§2.3 step 6), and the compiler input is byte-for-byte today's. **The
  format cannot add dispatch, because in that case it adds nothing at
  all.**
- **R-VE-5 / D39.2** (appended numbering) is not implemented by the
  format; it *falls out* of appending the DEFINE block (§2.3, MEASURED).
  That is the strongest form of the requirement being met — there is no
  second numbering mechanism to keep in agreement with PCRE2's.
- **R-VE-4** (source-level vs link-level composition kept distinct) —
  the format expresses the **source-level** tier only, and expresses it
  as a PCRE2 subroutine call. Link-level composition
  ([M4-CALLOUTS]'s aligned ABI, non-regex predicates) has no spelling
  here and must not acquire one that looks the same; §7 Q4 records that
  as the open item it is.
- **R-VE-6 / D39's labelled references** (`"a:reg1"`, path composition
  `"c:a"`) — **the format needs no label**, because a definition is
  referenced by name and appears **once** in the DEFINE block however
  many times it is called. The label problem is the *inlining* tier's
  ("the same regex inserted twice"), which this format does not spell.
  If [V-E] later adds an insert-at-this-point tier, the label lives on
  *its* construct, not on `(?&name)`.
- **R-VE-12** (a per-pattern encoding field) is a `config` line — the
  encoding selector is a pcrec option and `pcrec --encoding=…` inside a
  config reaches it today with no new grammar.
- **R-VE-9** (CLI args and a manifest file must not need contradictory
  semantics): they do not — the CLI's single pattern is the
  `target rx` default, and `--target <prefix>` selects from a file.

### 4.5 pcrec-bench — regime, variant, outcome, objective, and the sidecar

The bench's inputs (its `docs/design/requirements.md` §3, §4.4, §4.5, §5)
were written against a **directory + sidecar** model that Frank's ruling
supersedes: the sidecar is dropped and its fields become lines beside the
pattern. The bench's *needs* are absorbed; its *shape* is not.

**MEASURED — the absorption, field by field, against the live sidecar**
(`/home/duxevents/pcrec-bench/bench/loglines/subbench.toml`, 11 patterns,
112 subjects, a 1,364-row `expectations.tsv`):

| `subbench.toml` field | becomes |
|---|---|
| `id`, `version` | `tag id=loglines` / `tag version=0.1` (file-level) |
| `objective_kind` | `tag objective=realworld` (file-level) |
| `objective`, `description` (prose) | `#` comments and `NOTES.md` — **the two things §4 of the position paper already said are not lines in a pattern file** |
| `regimes = [...]` | `tag regime=search-short,throughput` (file-level), refined per block (below) |
| `[[patterns]].name` | `name <ident>` (block-scoped) |
| `[[patterns]].file` | the `pattern` line itself — the `.rx` file disappears |
| `.feature_tier` | `features <list>` (a real directive) plus `tag tier=base` for the bench's own vocabulary |
| `.hazard_class`, `.size_class`, `.convention`, `.tags`, `.role` | `tag hazard=… size=… convention=… role=…` |
| `[subjects].generator`, `.manifest` | the directory convention — a generator beside its output, exactly as `tests/recursion/gen_corpus.py` already is |
| `[subjects].short_search_max_bytes` | `tag short-search-max-bytes=4096` |
| `[expectations].file` | `include "gen/expectations.rxt"` |
| `[expectations].default_method` | `oracle pcre2` (file-level) |
| `[testees.pcre2].options` | `config pcre2` with `testee pcre2/10.46` + `option k=v` lines |
| `[testees.pcrec].options` | `config pcrec` with `pcrec --features all` |
| `patterns[].variant = null` | the **absence** of a `variant` line |
| an `expectations.tsv` row | `m @file:"subjects/s-000.bin" 234 258` / `n @file:"…"` / `mc @file:"…" <n>` |

**The four bench requirements that needed a decision, decided:**

1. **OUTCOME (§4.4).** `did-not-compile` is `perr`; `gave-up` is `gu`
   (MEASURED live, 23 uses, §2.11); `matched-as-expected` /
   `did-not-match-as-expected` / `wrong-span-or-captures` are what
   `m`/`n`/`g` already score; **`unsupported-by-declaration`** is
   `variant <testee> unsupported <reason>` — one line kind for both
   halves of the variant axis, not two. `crashed` / `timed-out` are the
   harness's own (exit ≥ 124 / ≥ 126, already distinguished by
   `run.sh`), never expectations.
2. **VARIANT (§4.5), constraint 1** — "the results must be the same" —
   is **mechanical**: a `variant` is checked against the block's own
   expectations, and a difference invalidates the cell. Nothing new is
   needed; the variant simply supplies different pattern text for one
   testee's cell.
3. **VARIANT, constraint 2** — "the sub-bench's objective must be
   preserved" — is **a review obligation the format records and does not
   check**, and it must say so. The format's contribution is visibility
   (T-2/AR-5: a variant is beside the pattern or it is a fork), not
   verification. A `tag variant-note=…` carries the reviewer's statement.
4. **REGIME (§3)** is a property of the **subject set**, not of a case,
   and there is no case scope (Frank's ruling 4). So a sub-bench writes
   the canonical pattern **once** as a `name`d definition and one block
   per (pattern, regime), each `pattern (?&<name>)` with its own
   `tag regime=…` and its own subject set. **MEASURED, the wrapper is
   free here**: `expectations.tsv`'s columns are
   `pattern subject regime expected start end nmatches method oracle` —
   **no capture columns at all** — and a subroutine wrapper is
   span-identical, differing only in capture visibility (§2.3). When
   bench adds capture checking (its OD-B9, [DD-13a] T-3), the wrapper
   stops being free and those blocks must carry the pattern text
   directly; §7 Q2 records that trigger.

**What the bench must still own** (D78 — this is a durable interface
statement, not a ruling into their repo): the record and its keys, the
adapters, the reporter, and the decision of *when* to move a sub-bench
into the format. This note's contribution is that when they do, the
sidecar has somewhere to go.

### 4.6 [M4-SUBST] — the template slot only

R-SUBST-1 says the format must have somewhere for a replacement template
to live per named pattern, and R-SUBST-3 records the unpaneled prior art
(`subst_template_design.md` §8.1's `repl`/`s`/`sg`/`serr`). **This note
adds no template production**, per R-SUBST-1's own instruction ("Do not
design the template's internal syntax here") and D77.

What it does do is leave the slot obviously shaped: `repl` is a
block-scoped line in the prior art and would be a block-scoped line here,
`s`/`sg` are case lines exactly like `m` with a second quoted field, and
`serr` is `perr`'s shape one construct over. None of the four collides
with anything in §1.3 (MEASURED, §1.1: all four are 0 in the corpus).
The one thing this note asserts is that when they land they should be
**block-scoped and non-carrying**, like everything else in a pattern
block — which is what the prior art already chose independently.
