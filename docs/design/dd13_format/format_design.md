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
measurement that forced it. There are five such departures and they are
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
**BODY** it already has (pattern blocks, unchanged). Thirteen additions —
six file-level declarations, two head block kinds and five block-scoped
lines — live there;
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
| D-e | a `config` line `freq <name>` selects a data block (§6.5) | the selector is **`analysis freq <name>`** | ARGUED, a grammar ambiguity: `freq` would then be both a config-body line kind and a head block starter, so `freq x` after a `config` body could not be told from a new data block without a lookahead rule. OD-6 left the data block's naming open, so this is inside the design's mandate |

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
**32** candidates — the six file-level declarations, the two block
starters, the five new block-scoped lines, `config`'s and the data
block's own body vocabularies, and R-SUBST-3's four prior-art
spellings — over all 179 files, count **0**:

```
$ for w in name target lib include config use variant oracle tag mc freq gap \
           def with from testee option repl s sg serr unsupported analysis \
           question reader exemplar bytes sha256 analyzer date row groups; do
      c=$(grep -rh "^$w\b" tests --include='*.rxt' | wc -l)
      [ "$c" != 0 ] && echo "COLLISION $w $c"; done
  -> nothing printed: all 32 are 0
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
- **A head block ends at the first line whose first token starts a new
  head item or a pattern block** — one of `lib`, `include`, `target`,
  `use`, `oracle`, `tag`, `config`, `freq`, `pattern`. Any *other* token
  a block's own vocabulary does not define is a hard error naming the
  block, so a typo inside a `config` body is loud rather than silently
  ending it.
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
    | "analysis" , ws , data-kind , ws , ident  (* select a data block  W2 *)
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
| **W2** | `include`, `@file:` subjects, `mc`, `tag`, the `freq` data block and `config`'s `analysis` line | a generated 1,364-row expectation set; a 1 MB subject; an exemplar findings file | **[ENG-PGO]** (the findings file — its plan row says "blocks on [DD-13b] wave 2/3"), the first in-format sub-bench |
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

### 1.5 The PATTERN-level extensions, and the one constraint they all obey

D87 adds three things to the pattern language itself, not to the `.rxt`
line grammar: a **numbered group**, a **scope prefix** on a subroutine
call, and a **delivering-call declaration**. Frank ruled the semantics
and left the spellings to the manager (r44, 14:5x). This section
recommends one spelling each, names the alternatives, and gives the
measurement that admits or rejects each candidate.

**THE CONSTRAINT, and it is testable: no legal PCRE2 pattern may change
meaning.** Every candidate is therefore checked by compiling it on
libpcre2 10.46 — a candidate PCRE2 already accepts is disqualified, not
merely disfavoured, because adopting it would silently re-interpret
patterns that exist in the world.

**MEASURED** (`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`,
libpcre2 10.46; every row cross-checked on `build/pcrec --features all`,
which agreed):

| candidate | libpcre2 10.46 | verdict |
|---|---|---|
| `(?<3>a)` | refused — "subpattern name must start with a non-digit" | **free** |
| `(?<name=3>a)` | refused — "syntax error in subpattern name" | **free** |
| `(?3:a)` | refused — "missing closing parenthesis" | **free** |
| `(?<3,name>a)` | refused | **free** |
| `(?&^.w)` | refused — "subpattern name expected" | **free** |
| `(?&caller.w)` | refused — "syntax error in subpattern name" | **free** |
| `(?&from=email)` | refused — "syntax error in subpattern name" | **free** |
| `(?&=email)` | refused — "subpattern name expected" | **free** |
| `(?&&email)` | refused — "subpattern name expected" | **free** |
| **`(?<from>&email)`** | **COMPILES — matches the literal `&email`** | **DISQUALIFIED** |

The last row matters: `(?<from>&email)` was the leading shape for the
delivering declaration, and it is an ordinary PCRE2 named group whose
body is the two-character literal `&email`. On both oracles it matches
the subject `&email` at (0,6). **Adopting it would change the meaning of
a legal pattern**, which is the one thing the constraint forbids, so it
is rejected on a measurement rather than on taste.

#### B1 — the numbered group: **`(?<3>…)`, and `(?<name=3>…)` for both**

RECOMMENDED. Names and numbers are two halves of one thing — a group's
IDENTITY — so they belong in one bracket with one dispatch point, and the
named-and-numbered form then falls out instead of needing a second
syntax. A parser dispatches on the character after `(?<`: `=` or `!` is a
lookbehind (unchanged), a digit is a number, a name character is a name
followed by an optional `=<digits>`.

- Alternative **`(?3:…)`** — closest to Frank's own shorthand `(3:abc)`,
  and it reads as `(?:` with a number. Rejected only because it has no
  natural named-and-numbered form, which would then need a third
  spelling.
- Alternative **`(?<3,name>…)`** — same bracket, comma separator.
  Rejected because `=` reads as assignment and a comma reads as a list.

#### B2 — the scope prefix: **`(?&^.name)`**, a PATH

RECOMMENDED, with `^` as the reserved segment meaning "one scope up".
D87 rule 3 asks for "a reserved scope word for the caller"; a WORD would
occupy the name space and could collide with a call-site name, whereas
**`^` is not a name character at all, so it can never collide**. It also
makes the prefix a genuine path — `^.^.name` is two scopes up by
construction, and downward paths are the delivering call's member names
(`from.local`, §2.13), so one grammar serves both directions:

```
(?&name)          this scope's definition            (PCRE2's, unchanged)
(?&^.name)        the CALLER's group `name`
(?&from.local)    the delivered group `local` of the call site `from`
```

- Alternative **`(?&caller.name)`** — readable, and D87's own leading
  shape. Rejected because `caller` is a legal call-site name, so a file
  that names a delivering call `caller` would make the prefix ambiguous.
- Only ONE level up has a named consumer today; `^.^.` is admitted by the
  grammar rather than built for (D77).
- The objection worth recording: `^` reads as an anchor everywhere else
  in a pattern. It is unambiguous here (inside `(?&…)` there is no
  anchor position) but a reader meets it in an unfamiliar role.

#### B3 — the delivering call: **`(?&site=name)`, and `(?&=name)` for the default**

RECOMMENDED. **One rule: an `=` in the call makes it delivering; the name
to the left of it is the member, and an empty left side means the
definition's own name.**

```
(?&email)          plain call, capture-transparent   (PCRE2's, unchanged)
(?&=email)         delivering; member `email`
(?&from=email)     delivering; member `from`
```

The assignment order (`member = source`) matches C, matches the path
(`r.from.local`), and puts the site name where the struct member name
goes. Both extended forms are refused by PCRE2 today (measured above).

- Alternative **`(?<from>&email)`** — **DISQUALIFIED by measurement**: a
  legal PCRE2 pattern today (above).
- Alternative **`(?&&email)`** — free, and visually distinct, but it
  needs a second form for the named case and "a reference to a
  reference" means nothing.
- The weak point, stated: `(?&=email)` reads slightly oddly for the
  common case. The alternative — making the DEFAULT the bare `(?&email)`
  and delivering implicit — was rejected because D87 rule 5 requires an
  undeclared call to stay capture-transparent at zero cost, so delivery
  must be something a site opts into visibly.

#### The serialization: **`--emit-composed`**

RECOMMENDED name, kept from D87's own placeholder. It writes the composed
pattern with every group's number spelled explicitly in B1's form, and
pcrec accepts what it writes (D87 rule 4, §2.3.4). Alternatives
considered and not taken: `--emit-pattern` (says nothing about
composition), `--emit-flat` (suggests inlining, which this is not — the
call structure is preserved and only the numbers are made explicit).

**Wave: all four are W1**, because composition is W1 and none of them is
optional to it — B1 is what `--emit-composed` prints and what rule (c)'s
collision error is about, B2 and B3 are how a definition reaches outside
itself and how a caller reaches inside. B2's multi-level `^.^.` and B3's
refusal cases are the parts with no consumer yet, and they are grammar,
not machinery.

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
| **data name** | `freq <ident>` (the family, §2.10) | a `config` block's `analysis freq <ident>` line | ident |
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

### 2.3 Composition — an AST-level operation inside pcrec (D87)

**This section was rewritten after the r44 panel and D87.** The first
version made composition a TEXTUAL operation: append the referenced
definitions as a `(?(DEFINE)…)` block and hand the text to pcrec.
r44-sem measured, on libpcre2 10.46 AND pcrec, that appending can
silently INVERT a library's meaning (M1, M2 below). Frank ruled the
mechanism rather than the refusal: **composition is an AST-level
operation inside pcrec, over ASSIGNED group numbers** (D87 rules 1-7).
The textual expansion survives as the ORACLE CONTROL, not as the
producer.

#### 2.3.1 What a group number is

**CITED, D87 rule 1: a group's number is an ASSIGNED property.** It
defaults to the group's position in its own pattern, and a rewrite such
as composition may assign otherwise. So an absolute reference `\1`
inside a library piece keeps meaning *"this piece's own group 1"*
wherever the piece lands — the composer RENUMBERS rather than refusing.

The assignment rules (D87 rule 7, restated here as the format's
contract because they are what `--emit-composed`, `RX_NCAPS` and the
struct view all read):

| | rule |
|---|---|
| (a) | `0` is the whole match; `(?<0>…)` is an error |
| (b) | an implicit counter `c` starts at 1; an unnumbered group takes `c` then `c += 1`; a numbered group takes its number **and restarts the counter** at `N+1` |
| (c) | a number assigned twice, by any mix of explicit and implicit assignment, is a **compile error naming both sites** — never a silent renumber |
| (d) | `ngroups` = the highest assigned number; `RX_NCAPS = ngroups+1`; numbers in `1..ngroups` held by no group are **real slots that are never set** (`-1,-1`), so a caller's `caps[N]` is always in range |
| (e) | branch reset `(?\|…)` is unchanged: the rules apply within one alternative, the same number across alternatives is the feature, explicit numbers behave like implicit ones there |
| (f) | `\N`, `\g{N}`, `(?N)`, `(?(N)…)` bind to the ASSIGNED number; a backreference or condition on an unassigned number behaves as an unset group (PCRE2's rule); a **call** to an unassigned number is an error — there is no body to call |
| (g) | relative forms `(?-1)`, `\g{-1}` keep PCRE2's textual-position meaning and survive relocation unchanged |
| (h) | names are orthogonal to numbers (§2.13) |
| (i) | **composition assigns a definition's groups a base above the caller's `ngroups`**, preserving local order and gaps; explicit local numbers are RE-BASED, never copied; **the caller's numbers are never touched** |
| (j) | `--emit-composed` prints every group in explicit form, and the serialization round-trips under (a)-(d) unchanged |

Frank's own worked examples: `(3:abc)(1:xxx)(yyy)` assigns 3, 1, 2 —
the numbered group restarts the counter, so `(yyy)` takes 2;
`(3:abc)(1:xxx)(yyy)(fff)` is an **error**, because `(fff)` would take 3
and 3 is already assigned.

Rule (i) is what makes D61 hold. **CITED, D61:** `caps[k]` is the
PRIMARY pattern's own group `k` for `1 <= k <= ngroups`, and slots above
`ngroups` are RESERVED for composition producers, which APPEND their
delivered slots and never renumber `1..ngroups`. D61's revisit-when is
"the first ref-bearing producer is designed" — **this is it**, and the
constraint is inherited as a requirement rather than chosen: `ngroups`
and `nnames` stay the PRIMARY's own (r44-sem M4/M5), the definitions'
delivered slots sit above, and a library's private internal edit can
move `RX_NCAPS` without touching any number a caller indexes by.

#### 2.3.2 Binding: lexical scope wins in both directions

**CITED, D87 rule 2.** A caller's own `(?<w>…)` overrides an injected
definition named `w` — the position paper's "own groups win", restored
as a rule rather than as an avoidance. And a library's internal `(?&w)`
binds to **the library's own** `w`, the lexical scope of the file that
defines it. The composer therefore **name-qualifies injected definitions
internally**, so a caller's `(?J)` cannot reach them.

Resolution, restated for the AST model:

1. For each pattern the compiler is given, the by-name subroutine calls
   (`(?&n)`, `(?P>n)`, `\g<n>`, `\g'n'`) whose target is not a named
   group **of that same pattern** are FILE references.
2. A file reference resolves against §2.2's definition scope: the file's
   own `name`d blocks, then its `lib`s in declaration order,
   transitively. Not found → a refusal. Found in two different files →
   refused by name (§2.2).
3. The closure is a **visited-set fixpoint with dedup** (r44-sem M8): a
   definition already in the closure is not added twice, so a definition
   used at two call sites, a self-recursive definition and a pair of
   mutually recursive definitions each contribute their body **once**.
   Cycles are ALLOWED — r44-sem verified that self- and mutual recursion
   compile and match on both oracles — so the fixpoint terminates on the
   visited set, not on an acyclicity test.
4. **A block's own `name` joins the set of names that pattern declares**
   (r44-sem M8): a block named `x` whose pattern calls `(?&x)` is calling
   itself, not requesting an injection of itself. A `name` line is not a
   named group in the pattern text, so the first version emitted such a
   body twice.
5. Each definition in the closure is bound into the caller's AST with
   its groups re-based per rule (i) and its own name scope qualified.

#### 2.3.3 MEASURED: the two defects, and the two rules that fix them

Every cell below was run on **both oracles** — libpcre2 10.46 through
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py`, and
`build/pcrec -p rx --features all` through `tests/harness/driver.c`.
**They agreed on every cell**, so the findings are the format's, not
pcrec's.

**M1 — an absolute numeric reference inside a relocated body, and
re-basing.** The library piece `dd` = `(\d)\1` ("a digit repeated"):

| pattern | `77` | `75` | |
|---|---|---|---|
| `(\d)\1` — the piece alone | match (0,2) | nomatch | the library's meaning |

composed into the caller `^(\d)-(?&dd)$`, whose own `(\d)` is group 1:

| composed form | `5-77` | `5-75` | |
|---|---|---|---|
| `…(?(DEFINE)(?<dd>(\d)\1))` — NAIVE append | **nomatch** | **match (0,4)** | **INVERTED**: `\1` re-targeted into the caller's capture space |
| `…(?(DEFINE)(?<dd>(\d)\3))` — RE-BASED per rule (i) | match (0,4) | nomatch | **the library's meaning, restored** |

The caller has `ngroups` 1, so `dd` is assigned 2 and `dd`'s own group 1
is assigned 3; its `\1` re-bases to `\3`. That is rule (i) executed by
hand, and it produces the piece's own semantics at the composed site.
**Relative forms need no re-basing** — r44-sem verified `(?-1)` and
`\g{-1}` safe across relocation (rule (g)), because their meaning is
textual position and relocation preserves the body's internal order.

**M2 — a caller name colliding with an injected definition, and
qualification.** Library: `outer` = `(?&w)`, `w` = `[a-z]+`. The
library alone answers `^(?&outer)$`: match on `abc`, nomatch on `Q`.
A caller writes `(?J)^(?<w>Q)(?&outer)$`:

| composed form | `Qabc` | `QQ` | |
|---|---|---|---|
| NAIVE append | **nomatch** | **match (0,2)** | `(?J)` makes the duplicate legal and the by-name call binds the FIRST declaration — the CALLER's `w`. The library's helper is silently replaced |
| injected definitions NAME-QUALIFIED (rule 2) | match (0,4) | nomatch | the library's own `w`, restored — and equal to the library-alone answer |

`(?J)` is not the disease, it is the symptom: without it the duplicate
is a loud refusal, with it the duplicate compiles and binds the wrong
declaration. Qualification removes the duplicate entirely, so the
behaviour is the same whether the caller writes `(?J)` or not.

**And the numbering fact that started the design still holds** — cells
E-J of the first version, re-stated here for what they now measure:
appending the `(?(DEFINE)…)` block at the END keeps the primary's
captures at `1..N` and appends the definitions at `N+1..`, while
PREFIXING shifts the primary's own numbers:

| # | pattern | subject | `RX_NCAPS` | result |
|---|---|---|---|---|
| E | `^(\d)-([a-z]+)$` (hand-inlined control) | `12-abc` | 3 | `match 0 6  0 2  3 6` |
| **F** | `^(\d)-(?&w)$(?(DEFINE)(?<w>[a-z]+))` | `12-abc` | 3 | `match 0 6  0 2  -1 -1` |
| G | `(?(DEFINE)(?<w>[a-z]+))^(\d)-(?&w)$` | `12-abc` | 3 | `match 0 6  -1 -1  0 2` |
| H | `^(\d)-(?&w)$(?:(?<w>[a-z]+)){0}` | `12-abc` | 3 | `match 0 6  0 2  -1 -1` |
| I | `^(\d)-(([a-z])+)$` (inlined control) | `12-abc` | 4 | `match 0 6  0 2  3 6  5 6` |
| J | `^(\d)-(?&w)$(?(DEFINE)(?<w>([a-z])+))` | `12-abc` | 4 | `match 0 6  0 2  -1 -1  -1 -1` |

These are no longer evidence about how pcrec composes — pcrec composes
over the AST. **They are evidence that the ORACLE CONTROL is exact**:
on the population where the textual expansion is valid, PCRE2's own
left-to-right numbering of the append form produces the same assignment
rule (i) specifies, so the control's answer and the composer's answer are
comparable slot for slot. F is the control's shape; G is why it is
appended and not prefixed.

#### 2.3.4 Who composes, and what the harness's EXPAND is for

**CITED, D87 rules 1 and 4. PCREC COMPOSES.** `--source` / `--lib-path`
read the file, resolve names on [DD-11]'s table (D85), bind definitions
into the AST, assign numbers and emit. This is not a preference: PCRE2
numbers groups by position and has no way to say otherwise, so an
assigned-number model cannot be expressed as text PCRE2 will read — the
operation has to live where the AST is.

Three things follow, and they are the shape of the whole design:

1. **The harness's textual EXPAND is the ORACLE CONTROL, not the
   producer.** It is valid on the population where the append form means
   what the composer means — **no absolute numeric references in any
   body, and no name collisions between caller and closure** — which is
   exactly the population python `re` and libpcre2 can check. Outside it
   the control does not run and says so (a counted, named skip, AR-3),
   because a control that quietly disagrees with its subject on a shape
   neither can express is worse than no control (learnings §3).
2. **`--emit-composed` is a serialization, not a mechanism** (D87 rule
   4). It writes the composed pattern with every group's number spelled
   out explicitly (§1.5), and pcrec ACCEPTS what it emits, so the
   `A == B` control recompiles it and compares. Frank considered and
   rejected composing OUTSIDE pcrec through this spelling: a textual
   renumberer would need a second PCRE2 parser covering every reference
   form (learnings §3's drift hazard), the oracle could not read the
   extended text, and the assigned-number concept has to exist inside
   pcrec regardless. It is the interchange format if a different front
   end ever needs composition.
3. **The composed pattern is not the same object as its serialization.**
   A composed text handed to plain `-p` is ordinary PCRE2 and counts
   every group, so `ngroups` there is the composed total; the same
   composition performed by `--source` keeps `ngroups` at the primary's
   own and puts the delivered slots above. §3.4's S9 hunk states that
   difference in `match_api.md`, because a caller can observe it.

#### 2.3.5 What composition costs, and what it is not

**A subroutine call is BACKTRACKABLE, not atomic, and
capture-transparent** — CITED and MEASURED by an earlier lane on
libpcre2 10.46 (`subroutines_design.md` §3.2, four isolated cells
against four atomic controls; §3.1, a live-ovector callout trace showing
the callee's write and the return's restore). This retires OD-5's
premise as R-VE-8 stated it ("subroutine-call semantics are ATOMIC and
shift capture numbering"): atomicity is false on the current PCRE2, and
the numbering is now an assigned property rather than a positional
accident.

**A call is not textual substitution, and there are TWO places the
difference shows** (r44-sem M13 corrected the first version's "the one
place"):

1. **Captures.** A call restores the callee's capture state on return;
   inlining leaves it set. This is the difference pcrec can reach, and
   it is what the delivering declaration (§2.13) exists to make
   available where a caller wants the callee's groups.
2. **Backtracking control verbs.** `(*PRUNE)` and its family behave
   differently inside a callee than inlined, on libpcre2. pcrec refuses
   verbs (module `verbs`, unbuilt), so this one bites only the
   `oracle pcre2` path and pcrec-bench — but it is a real second member
   and the note no longer claims there is one.

**The cost is PCRE2's, and the linkage is the compiler's.** A
call-linked search does ~2x the backtracks of the same language inlined
(CITED, `subroutines_design.md` §3.2 T7, monotone over 1..8 call sites,
measured with PCRE2's own `match_limit`). `src/opt/callgraph.c`'s
`cg_eligibility` already splices an acyclic callee under a node budget
(§6.3a), and a splice preserves capture-transparency through its own
`SLOT_SPLICE_SAVE` family. **The format pins the answer; the compiler
chooses the linkage.**

**The [DD-14.G] bar, restated** (r44-sem M3, RULED by D87's supersede
clause). The first version said "elision may change the emitted code; it
may not change `RX_NCAPS`", which contradicts plan.md:591's
"byte-identical to the hand-inlined pattern". Under D61 the two are
reconciled: **the bar is the emitted CODE byte-identical and slots
`1..ngroups` identical; the composition's delivered slots live above
`ngroups`.** r44-consumers U7 confirmed [DD-14.G]'s own archived ruling
already matches this (dead call-only groups are elided from engine
SELECTION only; the name table and unset-fill are untouched).

### 2.4 Collisions and the piece rule

**The format has a shadowing rule, and it is "lexical scope wins"**
(D87 rule 2, §2.3.2) — not the first version's "the situation cannot
arise". Three consequences, each with the measurement behind it:

1. **A caller's own named group wins over an injected definition of the
   same name**, and the injected one remains reachable to the library's
   own internal references because it is qualified. MEASURED as M2
   above: naive injection inverts the library's answer under `(?J)`;
   qualification restores it and makes `(?J)` irrelevant.
2. **A definition found in two different files is refused by name**
   (§2.2), unchanged. This is the collision the format still refuses,
   because there is no scope that could break the tie.
3. **A caller may reference a definition's groups explicitly** through
   the scope prefix (§1.5), which is what makes "lexical scope wins" a
   rule rather than a wall: the outer name wins by default, and the
   inner one is still spellable.

**MEASURED — the corpus needs none of this, and that is the point.**
Across all 179 files, **143** blocks in 23 files carry a by-name
subroutine reference, and exactly **4** reference a name their own
pattern does not declare:

```
tests/recursion/d27/sr_refusals.rxt:153  ^(?<w>a)(?&nope)$     perr
tests/recursion/d27/sr_refusals.rxt:158  ^(?<w>a)(?P>nope)$    perr
tests/recursion/d27/sr_refusals.rxt:163  ^(?<w>a)\g<nope>$     perr
tests/recursion/d27/sr_refusals.rxt:168  ^(?<w>a)\g'nope'$     perr
```

All four are `perr` blocks whose purpose is the refusal of an undefined
name, in a file that declares no `name` and no `lib` — so the file scope
is empty, `nope` stays unresolved, and the refusal is preserved. The
other 139 have no file reference and compose to themselves. That is not
a survey that might have gone otherwise: a block whose by-name reference
did not resolve within its own pattern would refuse today, and the
corpus is green.

**The one hazard is self-detecting.** If `sr_refusals.rxt` ever gained
`name nope`, those four blocks would resolve, compile, and their `perr`
assertion would go **red** at the block that changed meaning. No new
check is owed; the existing assertion is the check, and it falsifies in
the loud direction.

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
block's `analysis freq <name>` line names a data block and nothing else,
so there is no ambiguity to resolve and no reason to make `config prod`
and `freq prod` collide.

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

### 2.13 The struct view: context naming IS struct naming (D87 rules 5, 6)

**CITED, D87 rule 5.** With the feature that loads a match's results into
a generated struct — one field per named group — **a scope prefix is a
path and a struct is a path**, so the two are one mechanism seen from two
sides. This subsection states the format's half; the feature's own row is
**[V-I]** (plan.md:737, NAMED-RESULTS COPY HELPER — "an emitted
`struct <prefix>_groups` with one span member per named group, plus a
copier from the caps array"), which already cites D61 and
`rx_group_entry.slot` as its substrate.

**A delivering call gets an inline, in-place struct member named by the
CALL SITE.**

```c
struct { rx_span local, domain; } from;    /* declared in place */
```

- **No named type per definition.** The member is declared inline at its
  position, so the artifact stays self-contained and two libraries'
  `email` cannot collide in a type namespace that does not exist.
- **The reference prefix spells the member path**: `r.from.local` in C is
  `(?&from.local)` in the pattern (§1.5 B2). One vocabulary.
- **Per CALL SITE, not per definition.** A definition called twice needs
  two site names — defaulting to the definition's own name, given
  explicitly when that would repeat.
- **Undeclared calls stay capture-transparent** (PCRE2's default, zero
  cost). Delivery is opt-in per site; a file that declares none emits
  exactly what it emits today.
- **Delivered slots live ABOVE `ngroups`** — D61's reserved region,
  §2.3.1 rule (i). `ngroups` and `nnames` remain the primary's own.

**What is not deliverable, and its refusal.** A struct member is a
finite, fixed-shape object, so what cannot be one cannot be delivered:

| shape | why | outcome |
|---|---|---|
| a **recursive** definition (self- or mutually) | the nesting depth is a runtime fact; the member type would be infinite | a delivering declaration on it is a **refusal naming the recursion** |
| a call **under a repeat** | one member, many activations; which one is delivered has no answer the format may pick | a **refusal naming the quantifier** |

Iterated capture — "give me every iteration's value" — is a separate
question and explicitly **out of this row** (D87 rule 5). The refusals
above are not a policy against it; they are the honest answer while no
mechanism for it exists.

**Duplicate names within one scope path are ONE field, populated by the
FIRST SET group of that name in number order** (D87 rule 6) — PCRE2's own
`pcre2_substring_get_byname` rule, made structural rather than
re-invented. The intended use is alternation branches populating one
field:

```
(?<num>\d+)|0x(?<num>[0-9a-f]+)        ->  one member `num`
```

Two things this does NOT do, stated because both are natural misreadings:

- **It does not merge across scope paths.** A caller's `w` and a
  library's `w` are different paths, so they are different fields — which
  is §2.3.2's lexical rule seen through the struct.
- **It does not collapse the slot table.** Every duplicate keeps its own
  assigned number and its own slot; numbering never merges. Only the
  STRUCT VIEW merges, and it is a view.

**Two call sites of one definition are DISTINCT C types.** Each member is
declared inline at its own position, so `from` and `to` over the same
`email` definition have no common type name; assigning one to the other
needs `__typeof__`. That is acceptable because the target is
gcc-dialect C by construction (CLAUDE.md: "generated code uses computed
goto and other GNU C extensions") and it is **one sentence the spec
owes**. A named typedef per definition is a later opt-in, not this row's.

**Field order is assigned-number order.** The struct is the slot table
seen through names, so there is **one derivation feeding three readers** —
`RX_NCAPS`, the struct, and `--emit-composed` — which is learnings §3's
rule applied where it matters most: three surfaces that must agree can
disagree only if they are computed twice.

**A library adding a delivered group changes the user's struct TYPE.**
This is r44-sem's M5 ("a library's private edit moves the user's
`RX_NCAPS`") in its honest, visible form: under D61 the caller's own
`1..ngroups` are untouched, and the thing that moves is a type the
compiler checks, not an index the caller computed. A recompile sees it.

**What [DD-13b] hands [V-I]**, stated as the interface so that row does
not have to re-derive it:

1. the assigned-number table for the composed pattern (§2.3.1), from
   which field order follows;
2. a scope PATH per delivered group (call-site name, then the
   definition's own name), from which the nesting follows;
3. the first-set-wins merge rule for duplicate names within a path
   (D87 rule 6);
4. the two non-deliverable shapes and their refusals;
5. the guarantee that delivered slots never intrude on `1..ngroups`.

What [V-I] still owns: the C-keyword MANGLING rule its own row already
flags (`(?<int>…)`, `(?<return>…)` are valid group names and invalid
member names), the copier's signature, and whether the struct is an
optional emission unit ([EMIT-SET] names it as one).

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
  §3): the same resolver the harness runs. It is **named here and not
  specified**, because its consumer ([V-E]'s build integration) is not
  real yet and D77 applies — the trigger is [V-E] opening, not W1
  landing.

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
definitions), a `config` selects a table by name (`analysis freq
loglines`), and a
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
   directly; §7 Q6 records that trigger.

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

---

## 5. The attack list, the tensions, the anti-requirements, the OD ledger

### 5.1 requirements.md §13 — the five claims it told the panel to attack

**Attack 1 — "the DIALECT answer is absence-of-counterexample from a note
that surveyed no generator that has tried."** The residual, in §13's own
words: *"a panel with more time could try to construct a HYPOTHETICAL
include/reference pattern and check whether it is even representable as
'existing files unchanged, new top-level constructs added'."*

**ANSWERED, and the premise has expired.** Two measurements:

1. **The corpus now exercises cross-references.** MEASURED: **143**
   blocks across 23 files carry a by-name subroutine reference, and 99
   lines use `(?(DEFINE)`. The `recursion` module landed *after* the
   requirements note was written; `(?&name)`, `(?P>name)`,
   `\g<name>`, `\g'name'` and `(?(DEFINE)…)` are all registry rows and
   all `built`. The generator that wrote them
   (`tests/recursion/gen_corpus.py`, 33 files) needed **no format
   extension** — because in-pattern composition rides `pattern`'s
   verbatim-to-end-of-line text, and only *cross-file* composition needs
   grammar. That is the actual mechanism behind R-GEN-1's finding, and it
   is why the finding generalises rather than merely not having been
   contradicted yet.
2. **The head is virgin territory.** MEASURED: across all 179 files there
   are **0** non-blank, non-comment lines before the first `pattern`
   line. So "new top-level constructs added above the first `pattern`
   line" is not merely compatible with the corpus — **it occupies space
   the corpus has never used, in any file.** R-COMPAT-1 holds
   *structurally*, not only by keyword absence (§1.1's second
   measurement).

The honest residual is narrower and is stated in §7 Q5: no *cross-file*
generator exists yet, so the include-closure accounting rules (§2.11) are
designed against a hypothetical population.

**Attack 2 — "R-GEN-1's n=5 is flat: none of the five exercised
cross-references, config sections or includes."** **PARTLY CONCEDED, and
n is now 6 with the flatness broken on one axis.** The sixth is the
`recursion` corpus above: cross-references, yes; config sections and
includes, still no. **The concession matters and is not argued away**:
`include` and `config` have no generator behind them anywhere in either
repo, which is exactly why they are W2/W3 and why §7 Q5 names the
measurement that would trigger them.

**Attack 3 — "does bench actually need engine-neutral group
identification, or does T-3 overstate it?"** **MEASURED, the tension is
not live today**: the live `expectations.tsv` columns are
`pattern subject regime expected start end nmatches method oracle` —
**no capture columns at all**, over all 1,364 rows. And T-3's premise is
weaker than stated for a second reason: the appended numbering is
**PCRE2's own** for the same text (§2.3 MEASURED), not a pcrec
convention, so an engine fed the same expanded pattern numbers it the
same way. The mechanism for the case where it *does* bite —
`variant … groups <name>=<n>` — exists in the grammar and is unexercised;
§7 Q6 names its trigger rather than pretending it is proven.

**Attack 4 — "check whether `--replace`'s CLI-only existence has already
created an informal convention a manifest template field would be awkward
to match."** **CHECKED DIRECTLY, and the premise is false: there is no
`--replace`.** MEASURED — `grep -rn replace cli/ lib/pcrec.h
docs/spec/cli.md` returns nothing, and `build/pcrec --help` names no
replace or subst flag. So R-SUBST-1 is the free, unconstrained field the
requirements note hoped it was, and §4.6 leaves it free.

**Attack 5 — "re-run the census rather than trust it verbatim if material
time has passed."** **RE-RUN.** 2026-08-17: 54 files / 1,100 blocks /
9,977 expectation lines. 2026-08-29: **179 / 3,265 / 26,691** — 3.3×
in twelve days. The note's own figures are updated throughout; **AR-1's
cost of getting compatibility wrong has tripled since AR-1 was written**,
which is an argument for the design's caution, not against it.

### 5.2 The tensions

| | resolution |
|---|---|
| **T-1** interface-vs-reference-only vs every-part-testable | **No new concept.** Target-ness and testability are **independent bits**: the harness compiles every block that has cases, as a **test** artifact, exactly as today; `target` is a file-level, build-only declaration that no pattern block carries. A reference-only definition with cases is therefore fully testable and ships nothing. No test-only surface is invented, so AR-2's no-dispatch rule is not even reached |
| **T-2** canonical pattern vs declared per-library tweak | `variant <testee> <text>` is block-scoped, sits **beside** the pattern, and is checked against **the block's own expectations**. Structurally it cannot become a second pattern: a variant has no `name`, so it cannot be referenced and cannot be a target. Constraint 1 is mechanical; constraint 2 is a recorded review obligation the format does not pretend to check (§4.5) |
| **T-3** appended numbering vs engine-neutral expectations | see Attack 3. Not live (measured); the numbering is PCRE2's own; `groups <name>=<n>` is the mechanism when it becomes live |
| **T-4** non-carrying block state vs cascading options | **Two different constructs, so neither has to become the other.** Block reset is the default and is untouched; the cascade exists only inside `config … from`. MEASURED: `config` occurs 0 times in the corpus, so no existing file opts in |
| **T-5** byte-exact subjects by reference | §2.8: bytes are the subject, no decoding, NUL-safe, local paths only. It forces a **driver-protocol change** (H6/S5) rather than being free, and this note says so rather than assuming `argv` will carry a megabyte with a NUL in it |
| **T-6** per-file accounting vs includes | §2.11's three rules: closure is the unit, entry-set subtraction with **both counts reported**, cells counted. Plus a fourth failure taxonomy (resolution) that is *reported* separately but *scored* as a compile failure, which is what preserves the 384 `perr` blocks |

### 5.3 The anti-requirements

| | how it is honoured |
|---|---|
| **AR-1** no re-verification of the corpus | INV-COMPAT (§1.1) with three independent checks, six sabotage rows and asserted denominators. MEASURED: 0 keyword collisions over 32 candidates, 0 head lines in 179 files, R = ∅ for every non-`perr` block |
| **AR-2** no dispatch in the common case | §2.3 step 6: with no references the expansion **is** the pattern text. §2.7's default: one unnamed block, no head → `target rx`, byte-for-byte today's compiler input. The format cannot add dispatch because in that case it adds nothing |
| **AR-3** declared inapplicability ≠ failure ≠ silent pass | four separate, counted, printed states: `oracle none <reason>`, `variant … unsupported <reason>`, `gp`'s pending-vm bucket, and the resolution-failure taxonomy — each reported on its own line in the summary (§2.11) |
| **AR-4** must not make D27 harder | the head is **bounded and above the first `pattern` line**, so a blinded author reading a block looks in exactly one other place; a fragment **may not declare file scope**, so a spliced block's meaning never depends on which file spliced it; and the one genuine cross-block dependency — a name a pattern references — is visible at the top of the file by construction |
| **AR-5** no silent semantic fork | T-2 |
| **AR-6** no pcrec-specific data in bench expectations | expectations stay spans and counts (`m`/`n`/`ms`/`ns`/`mc`); the verification method is a declared `oracle`, not an engine; group correspondence, when needed, is **by name** |
| **AR-7** no structural violation via the format | a file declaring no targets emits nothing; a file declaring one target emits what `pcrec 'pattern'` emits; nothing routes a single pattern through multi-pattern machinery. The generator/finder split is untouched because the format never names a finder |

### 5.4 The open-decision ledger

| | disposition |
|---|---|
| **OD-1** where per-engine options live, and composition across includes | **file and block scope only** (Frank's ruling 4). Composition is the **per-option-kind** table in §2.6 — `features` unions, everything else is more-specific-wins, size caps are raise-only at every scope. The cascade Frank asked for lives in `config … from`, ordered, last wins; `include` stays pure splice, because making an include's *position* change a later block's meaning is the cross-file context AR-4 forbids |
| **OD-2** the declared-tweak mechanism | `variant <testee> <text>` / `variant <testee> unsupported <reason>`, block-scoped (§4.5) |
| **OD-3** config syntax unifying testees and build variants | **one block kind.** A build variant is a `config` with `pcrec` lines; a bench testee is a `config` with `testee` + `option` lines. R-BENCH-9's "one concept, two uses" is literal here — the same `config` grammar, differing only in which of its line kinds appear |
| **OD-4** interface/reference-only marking; a test-only surface | **no marking, no surface** — T-1 |
| **OD-5** PCRE2 desugar vs own spelling | **PCRE2's `(?&name)`** (Frank's ruling 2). Its two feared consequences are corrected by measurement: subroutine calls are **backtrackable**, not atomic, on 10.46, and the numbering shift is a function of *where the DEFINE block goes* — appended, it **is** D39.2's rule (§2.3, §0.3 D-c) |
| **OD-6** the data block's spelling and namespace | **inline values, own namespace** (§2.10) |

---

## 6. Worked files, in the final grammar

Every example below parses under §1.3 by the hand-trace beside it, and
every composed pattern in §6.1 was **compiled by `build/pcrec` and run
through `tests/harness/driver.c`** — the cells are measured, not
asserted.

### 6.0 A correction the position paper's §3a needs, and why it matters

**MEASURED: the position paper's §3a does not match.** Its library
defines `email` as `^(?&local)@(?&domain)$` — *anchored* — and its user
file writes `pattern From: (?&email)`. Composed:

```
From: (?&email)(?(DEFINE)(?<email>^(?&local)@(?&domain)$)(?<local>…)(?<domain>…))
  on "From: a@b.co"  ->  nomatch
```

**A subroutine call is not a wrapper: `^` and `$` inside a called body
anchor to the SUBJECT, not to the call site.** Two controls:

```
x(?&e)(?(DEFINE)(?<e>a$))   on "xa"   -> match 0 2
x(?&e)y(?(DEFINE)(?<e>a$))  on "xay"  -> nomatch
```

This is PCRE2's semantics, not a pcrec artefact, and it is the same fact
`subroutines_design.md` §2.4 records for `(?R)`/`(?0)` ("'the whole
pattern' INCLUDES the anchors"). **The design consequence is an
authoring rule for [LIB], not a format mechanism:** a library definition
is a **piece** and carries no subject anchors; whole-string matching is
the caller's `^…$`, or better, the artifact's own anchored entry
`<prefix>_match` (`docs/spec/match_api.md` §3.2), which exists precisely
so a pattern need not be re-spelled to be matched whole. The format does
not and cannot check this statically; what it does is make the failure
loud in the ordinary way — the composing block's own `m` case goes red.

§6.1 is the corrected file.

### 6.1 A library and a user of it ([LIB], U4/U5, W1)

`lib/rfc5322.rxt` — definitions are pieces, no anchors, no targets:

```
# RFC 5322 address pieces. Definitions only; this file declares no targets.
# Every definition is a PIECE: no subject anchors (§6.0).
tag objective=subroutines

pattern [A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*
name local
m "john.doe" 0 8
n ".john"

pattern (?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}
name domain
m "example.com" 0 11

pattern (?&local)@(?&domain)
name email
m "john.doe@example.com" 0 20
n "john.doe@"
```

`mail.rxt`, a user of it:

```
lib "lib/rfc5322.rxt"
target mail = from_line

pattern From: (?&email)
name from_line
m "From: a@b.co" 0 12
```

**Hand-trace.** *`lib/rfc5322.rxt`*: head = one `tag`; body = three
blocks. Blocks 1 and 2 have L = ∅, R = ∅, so EXPAND is the identity and
they compile exactly as written. Block 3 has L = ∅ and
R = {`local`, `domain`}; both resolve in this file; closure order is
first-reference order — `local`, then `domain`; the emitted text is
`(?&local)@(?&domain)` ++ the DEFINE block. R ≠ ∅ makes the block
`oracle pcre2` (H4). No `target` line and more than one block, so
**`pcrec --source lib/rfc5322.rxt` emits nothing** — a library ships
nothing by itself (Frank §6.4).

*`mail.rxt`*: head = `lib` + `target`; body = one block. `target mail =
from_line` forward-references a definition in the body — normal, the head
precedes the body and resolution is a whole-file pass. The block has
L = ∅, R = {`email`}; `email` is not defined in this file, so it resolves
in the `lib` chain; its own text is then scanned in *rfc5322's* scope and
adds `local`, `domain`. Closure order: `email`, `local`, `domain`.
**The library's own five cases do not run here.** `pcrec --source
mail.rxt -o mail.c` emits one artifact under prefix `mail`, with
`rx_info.name == "from_line"`.

**MEASURED — all six cells**, `build/pcrec -p rx --features all` +
`driver.c`:

| cell | expanded pattern (abbreviated) | subject | result |
|---|---|---|---|
| `local` m | `[A-Za-z0-9!#$…]+(?:\.[…]+)*` | `john.doe` | `match 0 8`, `RX_NCAPS 1` |
| `domain` m | `(?:[A-Za-z0-9](?:…)?\.)+[A-Za-z]{2,}` | `example.com` | `match 0 11`, `RX_NCAPS 1` |
| `email` m | `(?&local)@(?&domain)(?(DEFINE)…)` | `john.doe@example.com` | `match 0 20`, `RX_NCAPS 3` |
| `email` n | (same) | `john.doe@` | `nomatch` |
| `from_line` m | `From: (?&email)(?(DEFINE)(?<email>…)(?<local>…)(?<domain>…))` | `From: a@b.co` | `match 0 12`, `RX_NCAPS 4` |
| (a user's anchored form) | `^(?&email)$(?(DEFINE)…)` | `a@b.co` | `match 0 6`, `RX_NCAPS 4` |

Note `RX_NCAPS` in the last two: 1 + three definition slots, all unset
(§2.3). That is the observable cost of composition today, and §2.3 point
3 states the constraint under which [DD-14.G]'s elision may reduce it.

### 6.2 A bench sub-bench as one file (U7/U8, W2+W3)

The live `bench/loglines/` sub-bench, in the format. Prose stays in
`NOTES.md`; the generator stays beside its output; the directory stays a
directory and no tool reads it as a schema.

```
# bench/loglines/loglines.rxt — the log-line-search sub-bench.
# Objective, description and the required-literal column: NOTES.md.
tag id=loglines version=0.1 objective=realworld
tag short-search-max-bytes=4096
oracle pcre2

config pcrec
  pcrec --features all
config pcre2
  testee pcre2/10.46

config re2
  testee re2/2024-07-02
use pcrec, pcre2, re2

include "gen/cases_search_short.rxt"    # 11 patterns x 112 subjects, generated
include "gen/cases_throughput.rxt"      # the 16 KB - 1 MB sweep
```

and a fragment `gen/cases_search_short.rxt`, machine-written — **blocks
only, no head** (§2.5):

```
pattern \d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?
name iso_ts
tag regime=search-short tier=base hazard=none size=medium
tag convention=perl-leftmost-first role=member
variant re2 unsupported no per-engine spelling preserves the objective
m @file:"../subjects/s-000.bin" 234 258
n @file:"../subjects/s-001.bin"
m @file:"../subjects/s-002.bin" 0 24
… 109 more

pattern :
name floor
tag regime=search-short role=floor hazard=none size=tiny
m @file:"../subjects/s-000.bin" 24 25
… 111 more
```

**Hand-trace.** The entry file's head carries file-level `tag`s, an
`oracle`, three `config` blocks (one with a `pcrec` line, two with
`testee` lines), a `use` naming all three, and two `include`s. The
fragments carry pattern blocks only; their `@file:` paths are relative
**to the fragment** (§2.8), hence `../subjects/`. Each block is run as
three cells (`use` enumerates, §2.6); the `variant … unsupported` line
makes `re2`'s cell for `iso_ts` a declared, counted non-result rather
than a wrong answer (bench §4.4). The tally is reported under
`loglines.rxt` with `entry files: 1  fragments spliced: 2` (§2.11), and
each failure still prints the fragment's own `file:line`.

**What this replaces**: `subbench.toml` (183 lines),
`expectations.tsv` (1,364 rows), and eleven `patterns/*.rx` files —
three file kinds and two grammars become one file kind and one grammar,
with the case's identity being `file:line` in one file rather than a
`(pattern, subject, regime)` key joined across two (§4's
"identity of a case" row).

### 6.3 Two build configurations from one source ([V-E], U6, W1)

```
config baseline
  pcrec --no-captures
config avx2 from baseline
  pcrec --simd=avx2
config big from baseline
  pcrec --max-emit-bytes=4000000

target log_base = level_filter with baseline
target log_avx2 = level_filter with avx2
target log_big  = level_filter with big

pattern (?i)error|warn|fatal
name level_filter
m "an ERROR here" 3 8
```

**Hand-trace.** Head: three `config` blocks (`avx2` and `big` each
inherit `baseline`'s `--no-captures` through `from`, then add their own),
three `target` lines naming one definition three times. Body: one block.
`pcrec --source log.rxt` emits **three** `.c` files;
`--target log_avx2` emits one. All three carry
`rx_info.name == "level_filter"` and three distinct prefixes (§2.7).
`big` is the D84 addendum-3 case, and it is exactly the shape
`docs/spec/limits.md` already tells callers to use. The harness runs the
block's one case in each of the three targets' configs, and identity
between them is a free control.

### 6.4 An exemplar-analysis findings file (`freq`, W2)

Written by the analyzer, committed; the exemplar is not (D83, Frank).

```
# exemplars/loglines.freq.rxt — WRITTEN BY THE ANALYZER. Do not hand-edit.
freq loglines
  question which byte is rarest in this exemplar
  reader OPT-A rarest-byte candidate-scan selection
  exemplar prod-web-01 nginx access log, 2026-08 (not committed)
  bytes 4187336614
  sha256 9f2c0b1e7a4d38c5be6109f7d2a4c83b5e0d7f61a9c2b48e35d7061fa8c3b92d
  analyzer scripts/exemplar_freq.py 0.1
  date 2026-08-29
  row 0    412 0 0 0 0 0 0 0 0 118344 4192011 0 0 91 0 0
  row 16   0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
  row 32   681240119 3341 24 88190 4412 33 991 62204 41180 41180 8823 6 2201947 774310 2119883 1884420
  … 13 more rows
```

and a user of it:

```
lib <rfc5322>
include "exemplars/loglines.freq.rxt"

config prod
  analysis freq loglines
  pcrec --features all

target email_prod = email with prod
```

**Hand-trace.** The findings file's head is one data block; its body is
empty — a legal file with zero pattern blocks, which the grammar admits
(`body = { pattern-block }`, possibly none) and which is the point: this
is data, not tests. `question` and `reader` are required, which is
§2.10's membership rule made structural. The user's file `lib`s a
library by its **store** spelling (`<rfc5322>` — searched on the library
path, never relative), `include`s the findings file by its **local**
spelling, selects the table in a config, and builds one target against
it. **The same pattern built against a second exemplar is a second
`target` line, not a second file** — which is what made the
target-as-declaration shape right.

### 6.5 A today's-`.rxt` file, unchanged (U1, all waves)

Verbatim from `docs/spec/rxt_format.md`'s own example, which is what
one of the 179 files looks like:

```
# Literal matching and basic quantifiers.

pattern abc
m "abc" 0 3
m "xxabcxx" 2 5
n "ab"

pattern a+
m "aaa" 0 3
n "b"

# An invalid pattern: unbalanced group.
pattern (bad
perr

pattern colou?r
m "The color and colour are spelled differently." 4 9
m "colour" 0 6
m "byte \x41 then newline\n" 5 6
```

**Hand-trace.** Head: **empty** — the file's first non-comment,
non-blank line is a `pattern` line, which is true of all 179 corpus files
(MEASURED, §5.1). Body: four blocks. Every block has L = ∅ and R = ∅, so
EXPAND is the identity and the compiler input is byte-for-byte today's.
No `target` line and more than one block, so the file builds nothing. The
`perr` block is evaluated in exactly one cell (§2.6). `\x41` and `\n`
decode as they do today. **Nothing in this file is new, nothing in it
means anything different, and nothing in it needed to change.**

---

## 7. Open questions for Frank

Only what the rulings do not settle. Each carries a recommendation, so
"agree" is a complete answer.

**Q1 — prose has no home in the file, and the bench declares an
OBJECTIVE field.** The format has no multi-line value (§1.2), by
design: every value is one line. But pcrec-bench's live sidecar carries
an `objective` and a `description` that are paragraphs, and its §4.5
calls the objective "a declared field of the sub-bench". **Recommend:
the machine-readable field is a single token (`tag objective=realworld`)
and the paragraph lives in `#` comments and `NOTES.md`.** The reason is
the position paper's own verdict — prose and generators are the two
things that are files beside a pattern file, not lines in one — and the
reason it is safe is that constraint 2 ("the objective is preserved") is
a review obligation the format was never going to check anyway (§4.5).
*The alternative, a multi-line block value, buys one field and costs the
line-oriented property every other rule in the format rests on.*

**Q2 — `features` composes by UNION, which is the one composition rule
that is not "more specific wins."** §2.6. A config's modules are added
to a block's, so a testee's `--features all` reaches a block that says
`features classes`. **Recommend: union, together with the rule that a
`perr` block is evaluated in exactly one cell and never re-run under a
config.** Union is what a testee needs (pcrec-bench's own note: "a
build/run flag of the TESTEE, not a variant of the pattern"), and it is
safe because enabling a module cannot change what an
already-compiling pattern matches — only what is refused. The `perr`
carve-out is what stops it from silently changing the meaning of the
**384** `perr` blocks in the corpus.

**Q3 — a library definition must not carry subject anchors, and that is
an authoring rule the format cannot enforce.** MEASURED (§6.0): the
position paper's own §3a worked file returns `nomatch`, because `^`/`$`
inside a called body anchor to the subject, not to the call site.
**Recommend: [LIB]'s store discipline makes "a definition is a piece,
and pieces carry no subject anchors" a store-entry rule with a trivial
scan behind it, and whole-string matching is the caller's `^…$` or the
artifact's own `<prefix>_match` entry.** The format's contribution stays
loudness — the composing block's `m` case goes red — because a static
rule ("a definition containing `$` may not be called from a non-final
position") is not decidable in general and would refuse legitimate
patterns.

**Q4 — the link-level composition tier still has no spelling, and should
not accidentally acquire one.** R-VE-4 requires source-level and
link-level composition to be representable but never to look alike. This
design spells the **source-level** tier only, as a PCRE2 subroutine call.
**Recommend: confirm that when [M4-CALLOUTS]'s aligned-ABI tier arrives
it gets its own construct, and that `(?&name)` never means "link to a
separately compiled part".** The costs differ by orders of magnitude and
a reader must be able to see which one they wrote.

**Q5 — W2's include-closure accounting is designed against a population
that does not exist yet.** No cross-file generator exists in either repo;
every one of the six known generators writes a flat, self-contained file
(§5.1, attack 2 — conceded, not argued away). **Recommend: ship W2 when
the first real generated set needs it — the bench's 1,364-row expectation
fragment is the natural first — and treat that set as the measurement
that validates §2.11's rules rather than claiming they are validated
now.** D77's shape: the trigger is named, the build waits for it.

**Q6 — a bench sub-bench references its canonical pattern per regime
rather than repeating it, and that is free only while bench checks no
captures.** §4.5 item 4: regime is a property of the subject set, there
is no case scope, so a sub-bench writes the pattern once as a `name`d
definition and one block per (pattern, regime) spelled `pattern (?&n)`.
**Recommend: reference now** — MEASURED, `expectations.tsv` has **no
capture columns at all**, and a subroutine wrapper is span-identical,
differing only in capture visibility (§2.3) — **and revisit when bench
adds capture checking** (its OD-B9 / [DD-13a] T-3), at which point those
blocks must carry the pattern text directly. The trigger is named so the
change is a scheduled one rather than a surprise.
