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
