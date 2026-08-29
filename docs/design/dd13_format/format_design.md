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
- **Four lexical CONTEXTS, each with a closed vocabulary.** The format
  already has two — the file's own directives and a pattern block's
  case vocabulary (`m`/`n`/`g`/…). This design adds two more (`config`
  body, data-block body). A first token unknown *in its context* is a
  hard error that names the context ("`testee` is not a pattern-block
  directive"). Nothing is a keyword everywhere.
- **IN THE HEAD, INDENTATION MEANS CONTINUATION.** A line indented by
  one or more spaces continues the head declaration or block above it: a
  `config` body, a data-block body, a `description` attached to a
  `target` or a `lib`, and a block-scalar value's own lines are all the
  same rule. A head construct therefore ends at the first non-indented
  line, and a typo inside a `config` body is a hard error naming the
  block rather than a silent block-ending.
  **MEASURED, and this is what makes it free:** **0** lines in the
  179-file corpus begin with whitespace
  (`grep -rhcE '^[[:space:]]+[^[:space:]]'` → 0; independently reproduced
  by r44-grammar's own recognizer run, G1), so no existing line's meaning
  can change. This REPLACES the first version's "leading whitespace is
  permitted and ignored"; Frank's `description` block scalar (r44, 15:1x)
  needs continuation to mean something, and one rule serving every head
  construct is better than a second mechanism beside it.
- **A PATTERN BLOCK keeps today's shape: case lines are NOT indented**,
  and a block ends at the next `pattern` line or end of file. This
  asymmetry between head and body is deliberate and is the only one: the
  body's shape is forced by R-COMPAT-1 (3,265 blocks depend on it) and
  the head is new territory where indentation costs nothing. A generator
  writing an included fragment writes pattern blocks only (§2.5), so it
  never has to indent anything.
- **One line, one value — with exactly ONE exception: the BLOCK SCALAR.**
  A line kind whose value is prose may write `<kind> |` and continue on
  indented lines, YAML's `|` form; newlines are preserved and the value
  ends at the first non-indented line. The one-line form
  `<kind> <text>` stays. **Only `description` uses it today**, and the
  exception is stated as a property of the VALUE production rather than
  of `description`, so a second prose field would inherit it rather than
  invent it. Nothing else in the format spans a line.

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
tag-item    = tag-label | tag-pair ;                              (* U1 *)
tag-label   = ? a bare label: no whitespace, no '=' ? ;
tag-pair    = tag-key , "=" , tag-value ;   (* tag-value: no whitespace, no '=' *)
prose-value = rest-of-line                        (* one-line form *)
            | "|" , eol , { INDENT , rest-of-line , eol } ;  (* block scalar *)
INDENT      = ? one or more spaces at the start of the line ? ;

(* ---------- file ---------- *)
file          = head , body ;
head          = { file-decl | config-block | data-block } ;
body          = { pattern-block } ;

(* ---------- head: file-level declarations ---------- *)
file-decl   = decl-line , { INDENT , decl-attr , eol } ;   (* indented attrs *)
decl-line =
      "lib"        , ws , path-ref                                 (* W1 *)
    | "include"    , ws , path-ref                                 (* W2 *)
    | "target"     , ws , ident , ws , "=" , ws , ident ,
                     [ ws , "with" , ws , config-list ]            (* W1 *)
    | "use"        , ws , config-list                              (* W3 *)
    | "oracle"     , ws , oracle-spec                              (* W3 *)
    | "tag"        , ws , tag-item , { ws , tag-item }             (* W2 *)
    | "description", ws , prose-value ;                            (* W1 *)

decl-attr   = "description" , ws , prose-value ;   (* attaches to decl-line *)

oracle-spec = "python" | "pcre2" | "none" , ws , rest-of-line ;    (* W3 *)

(* ---------- head: config block ---------- *)
config-block = "config" , ws , ident , [ ws , "from" , ws , config-list ] , eol ,
               { INDENT , config-line , eol } ;   (* `from` is W1 — G3 *)
config-line =
      "pcrec"    , ws , rest-of-line          (* raw pcrec flags        W1 *)
    | "flags"    , ws , letters               (* as a pattern block's   W1 *)
    | "features" , ws , module-list           (* as a pattern block's   W1 *)
    | "encoding" , ws , ident                 (* D58's per-pattern axis M16 *)
    | "engine"   , ws , ( "vm" | "dfa" )      (* as a pattern block's   W1 *)
    | "budget"   , ws , budget-item           (* as a pattern block's   W1 *)
    | "analysis" , ws , data-kind , ws , ident  (* select a data block  W2 *)
    | "testee"   , ws , engine-ref            (* a non-pcrec engine     W3 *)
    | "option"   , ws , tag-pair ;            (* that engine's options  W3 *)

engine-ref = ident , [ "/" , version-chars ] ;      (* e.g. pcre2/10.42 *)

(* ---------- head: data block (the analysis FAMILY, §2.10) ---------- *)
data-block = data-kind , ws , ident , eol , { INDENT , data-line , eol } ;
data-kind  = "freq" ;                    (* the family's only member    W2 *)
data-line =
      "description" , ws , prose-value   (* the summarizing script's field *)
    | "question" , ws , rest-of-line     (* what this answers, required *)
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
    | "features" , [ ws , "only" ] , ws , module-list  (* `only` is new: M14 *)
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
    | "name"        , ws , ident                                   (* W1 *)
    | "description" , ws , prose-value                             (* W1 *)
    | "encoding"    , ws , ident        (* D58's per-pattern axis    W1 M16 *)
    | "tag"         , ws , tag-item , { ws , tag-item }            (* W2 *)
    | "mc"          , ws , subject , ws , int                      (* W2 *)
    | "oracle"  , ws , oracle-spec                                 (* W3 *)
    | "variant" , ws , ident , ws , variant-body ;                 (* W3 *)

variant-body = "unsupported" , ws , rest-of-line          (* a declared refusal *)
             | rest-of-line , [ eol , "groups" , ws , group-map ] ;
group-map    = ident , "=" , int , { "," , ident , "=" , int } ;
```

**That is the whole grammar: seven file-level declarations, two head
block kinds, seven new block-scoped lines** (`name`, `description`,
`tag`, `mc`, `oracle`, `variant`, plus `encoding`; `features` gains an
optional `only`). Sixteen additions against thirteen existing line
kinds, plus §1.5's three pattern-level extensions — the format roughly
doubles, once, and each addition answers a named consumer in
`requirements.md` or a ruling.

**`description` is a FIELD, not a comment** (Frank, r44 15:0x): *"we may
want to summarize via script what a library or other rxt file has:
therefore a description may be helpful outside of comments, which should
be operational."* So it is machine-readable, it exists at file level,
per definition block, per target and per data block, and `#` comments go
back to being operational notes only. This **overturns §7 Q1's
recommendation in the first version** — `NOTES.md` is no longer where a
library's or a sub-bench's prose lives.

### 1.4 Which production earns which wave, and who is waiting

| wave | productions | the consumer that earns it | blocked row |
|---|---|---|---|
| **W1** | `name`, `description` (both forms), `lib`, `target … [with]`, `encoding`, `features only`, `config` with `pcrec`/`flags`/`features`/`encoding`/`engine`/`budget` **and `from`** (G3); AST composition (§2.3) with §1.5's three pattern-level extensions and `--emit-composed`; `rx_info.name`; **H11's target build path** (M9) | a file carrying several patterns that reference each other; a shipped library a user `lib`s and builds three targets from | **[LIB]** (all three parts), [DD-14]'s multi-pattern files |
| **W2** | `include`, `@file:` subjects, `mc`, `tag`, the `freq` data block and `config`'s `analysis` line | a generated 1,364-row expectation set; a 1 MB subject; an exemplar findings file | **[ENG-PGO]** (the findings file — its plan row says "blocks on [DD-13b] wave 2/3"), the first in-format sub-bench |
| **W3** | `use`, `oracle`, `variant`, `config`'s `testee`/`option` | a second engine in one file | **pcrec-bench** sub-benches with a non-pcrec testee |

**W1 is a departure from the position paper's wave assignment for
`config`, and the reason is a shipped promise** (D-b in §0.3):
`docs/spec/limits.md`, "Handling an oversized artifact", already
instructs callers to "put the override in the pattern-source file's
`config` block rather than on the command line". A spec that ships an
instruction owes the mechanism. `config`'s wave-3 half (`testee`,
`option`) stays wave 3 — it has no consumer until a second engine does.

**`from` is W1** (r44-grammar G3): it was in the W1 production and
unassigned in this table. It is unexercised (0 uses), but it is the only
cascade the format has and `config … from` is how a build variant is
spelled, so splitting it out of W1 would leave `config` half-built.

**H11 is part of W1, not an afterthought** (r44-sem M9): the first
version's H1-H10 never compiled or ran a `target … with <config>`, so
the central new build declaration would have shipped with no test path.
`target` and the thing that builds it land together (§3.2).

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
| **scope-path segment** | a delivering call `(?&<site>=<name>)` (§1.5 B3) | `(?&<site>.<group>)` in a pattern; `r.<site>.<group>` in C (§2.13) | PCRE2 group name |

**A fifth: SCOPE PATHS, and they are what makes "lexical scope wins" a
rule rather than a wall.** A delivering call names a scope; `^` names the
caller's (§1.5 B2). Within one path, names resolve lexically — a
caller's own group beats an injected definition of the same name (D87
rule 2) — and either can still be reached explicitly by its path. Two
paths never merge, so a caller's `w` and a library's `w` coexist without
either being renamed in the source the author wrote.

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
- scope-path segments: the pattern that writes the call. Two delivering
  calls in one pattern with the same site name are a duplicate and are
  refused; the same site name in two different patterns is two different
  scopes and is fine.

**The one namespace this rule does NOT govern is group NUMBERS**, and
they have their own (D87 rule 7(c), §2.3.1): a number assigned twice by
any mix of explicit and implicit assignment is a compile error naming
both sites. Same discipline — refuse, never silently renumber — reached
from the other direction.

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
| `features` | **UNION** — a config's modules are ADDED to the block's — **unless the block writes `features only <list>`**, which pins its own set against any config | enabling a module cannot change what an already-compiling pattern matches; it can only change what is refused (r44-sem probed 8 shapes: every difference was refuse→compile, never match→different-match). Union is what a testee needs: pcrec-bench's `subbench.toml` records that `--features all` "is a build/run flag of the TESTEE, not a variant of the pattern, and the pattern text handed to pcrec is byte-identical either way". **`only` exists because union alone makes NARROWING unspellable** (r44-sem M14: a block writing `features none` beside a config's `all` would silently get `all`) — a deliberate narrowing should be sayable, and spelled |
| `flags` | **more specific wins** (block over config over default) | `flags i` changes what the pattern *matches*; a block that states it has stated the test's meaning |
| `encoding` | **more specific wins**, block scope allowed | D58 makes encoding a PER-PATTERN scalar, so a block must be able to state it; the first version had no row and no block spelling (r44-sem M16) |
| `engine`, `budget` | more specific wins | as above |
| `pcrec <raw>` | config only; accumulated along the chain, later wins per flag | a block has no spelling for these, so there is nothing to conflict with |
| size-limit overrides (`--max-emit-bytes=N`, `--max-emit-code-bytes=N`) | **MAX WINS** across every scope that names one | CITED, `docs/spec/limits.md`: "raise-only (a value below the default is refused, so these can never be used to make a build fail that would have succeeded)". The first version said "raise-only at every scope, a chain that tries to lower is refused" — which made `with c1, c2` **ORDER-SENSITIVE** (r44-sem M15), since `c1` raising then `c2` lowering refuses while the reverse order does not. Max-wins is order-insensitive and the raise-only law then follows automatically rather than being enforced by a refusal |

**A `perr` block is evaluated in exactly ONE cell** — its own options
composed with the file's default — and is **never re-run under a `use`
or `target` config. ARGUED, and it is load-bearing**: `perr` asserts a
refusal *under a stated option set* (R-RXT-6: "a dropped flag would
compile a different automaton and the block's expectations would then be
verified against something nobody asked for"), so re-running it under a
testee's `--features all` would assert something nobody wrote — and
MEASURED, it would silently change the meaning of **384** blocks. Under a
non-pcrec testee a `perr` is meaningless in any case.

**The counter-case r44 put beside this** (U12 on §7 Q2): more-specific-
wins would let a block test under FEWER modules than the file intends,
which is a real way to weaken a suite silently. `features only` is the
answer to it — the narrowing exists, and it is a thing an author wrote
rather than a thing precedence did.

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
  so.** MEASURED, and the first version overstated it: **177** of the 179
  files have several blocks and would build nothing;
  **two have exactly one block** — `tests/mrl/11_motivating_shape_small.rxt`
  and `tests/base/d27_nested_min_boundary.rxt` — and would therefore
  BUILD as `target rx` under `--source` (r44-sem M11). That is harmless
  and intended: it is exactly `pcrec '<that pattern>'`, one artifact, and
  the harness already compiles both blocks as test artifacts today. No
  file declares a target, so `pcrec --source tests/base/quantifiers.rxt`
  emits **nothing** rather than 90 artifacts. Test compilation is
  untouched; target-ness and testability are independent bits
  (T-1/OD-4, §5).
- **One `.c` per target, and N targets need a DIRECTORY** (Frank's
  ruling 6; the naming rule is r44-sem M10, which found the first version
  had none). `-o` names one file and pcrec also writes its `.h`, so with
  more than one target that is not expressible:

  | invocation | result |
  |---|---|
  | `--target <prefix> -o out.c` | that one target, to `out.c` + `out.h` |
  | `-o <dir>` with N ≥ 1 targets | `<dir>/<prefix>.c` + `<dir>/<prefix>.h` per target |
  | `-o out.c` with N > 1 targets | **refused**, naming the targets and the two ways to proceed |

  A single multi-pattern **unit** stays [V-E]'s question (§4.4). Added to
  S11.
- **`rx_info` gains `const char *name`** (Frank §6.3): the block's
  `name`, or the prefix when the block is unnamed, so no artifact ever
  carries a NULL name. This is a scaffolding change and therefore **an
  `abi` bump under D76's ritual, in the same change**, at all four sites
  CLAUDE.md names: `src/gen/emit_dfa.c`'s `.abi` (currently **11**,
  MEASURED at `src/gen/emit_dfa.c:1310`), `tests/codegen/run_codegen_tests.sh`'s
  [DD-14.FB] §10.4 expectation, `docs/spec/match_api.md` §6, and the
  identity gate's (B) pin. It rides W1's first landing, not a separate
  event (memory `pcrec-abi-changes-pre-release`).
- **`ngroups` and `nnames` stay the PRIMARY's own** (D61; r44-sem
  M4/M5). A composed artifact's `ngroups` counts the target pattern's own
  groups, not the closure's; the definitions' delivered slots sit above
  it (§2.3.1 rule (i), §2.13). This is why `--source` and plain `-p` are
  not interchangeable on a composed pattern — plain `-p` is handed text
  and counts every group in it — and §3.4's S9 hunk states the difference
  where a caller can see it.

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
   stops being spliced is visible instead of merely smaller (K35).

   **A file both NAMED on the command line and included by another entry
   in the same run is counted ONCE, under the includer's closure**, and
   the summary says so: `named, absorbed into <entry>`. The first version
   said "a file named explicitly is always an entry, because the user
   asked for it", which **double-counts** it — the K35 shape this section
   cites for its other rules, caught by r44-consumers U6 in the note's
   own text. Counting once and REPORTING the absorption is better than
   refusing the run: the user gets what they asked for (that file's cases
   run), the population is right, and the line tells them why the file
   does not appear as an entry of its own.
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
| H2 | **PCREC's composer** (D87 rule 1): file reference detection, definition lookup on D85's table, the visited-set closure, name qualification, number assignment and re-basing, and the **span map** (§2.12). This is PCREC code, not harness code — the first version put it in the harness | W1 | `src/`, reached by `--source` / `--lib-path` |
| H2b | **The harness's textual EXPAND, as the ORACLE CONTROL** (§2.3.4): the DEFINE-append form, plus the VALIDITY TEST that decides whether the control may run at all — no absolute numeric reference in any body, no name collision between caller and closure. Outside that population the control is a counted, named skip, never a silent pass | W1 | `tests/harness/` |
| H2c | **`--emit-composed` and its round trip**: pcrec writes the composed pattern with explicit numbers (§1.5), and the `A == B` control recompiles it and compares against the `--source` build | W1 | `src/`, `tests/harness/` |
| H3 | **Cells**: run a block once per resolved config; report cells in the summary; the `perr` one-cell rule | W1 | `run.sh` summary + dispatch |
| H4 | **`verify_rxt.py` reads H2b's EXPANDED text**, not the source block. python `re` has **no** subroutine call at all (CITED, `subroutines_design.md` §10.1: "not different semantics, an ABSENCE"), so **any composed block is `oracle pcre2` whether or not it says so** — a python oracle cannot check a composed pattern, and pretending otherwise would be a silent pass | W1 | `verify_rxt.py` |
| H5 | **Include resolution + entry-set subtraction + closure accounting** (§2.11) | W2 | `run.sh` discovery |
| H6 | **`@file:` subjects — and the DRIVER PROTOCOL CHANGE they force.** Today a subject travels as `argv[1]` (`t <subject> [startpos] [route]`), which can carry neither an embedded NUL nor a megabyte. The driver needs a form that names a path and reads it byte-exactly — the natural spelling is a leading sentinel on the existing argument (`t @<path> …`), which is additive and leaves every existing invocation untouched | W2 | `tests/harness/driver.c`, `run.sh` |
| H7 | **`mc` find-all counting** against `match_api.md` §3.1's restart semantics | W2 | `driver.c` |
| H8 | **`tag` well-formedness only** — the harness validates the *shape*, never the vocabulary | W2 | `run.sh` |
| H9 | **Data-block parse + `--exemplar`-shaped hand-off to pcrec** (D83's flag takes the findings file, never the raw text) | W2 | `run.sh`, pcrec CLI |
| H10 | **`use` / `variant` / `oracle` / testee configs** | W3 | `run.sh` + a non-pcrec adapter, which is pcrec-bench's, not pcrec's |
| **H11** | **THE TARGET BUILD PATH — W1 ships with it, not without it** (r44-sem M9). Nothing in H1-H10 compiled or ran a `target … with <config>`: `driver.c` hard-codes the prefix `rx` and `run.sh` passes `-p rx`, so the central new build declaration would have had no test path at all. The harness must BUILD every declared target and assert two things per target — the emitted symbols carry its **prefix**, and `rx_info.name` is the definition's `name` — with the driver taking the prefix (a `-D` prefix macro or a generated shim). It is also the only path that exercises §2.7's output naming and §2.13's struct | W1 | `tests/harness/run.sh`, `tests/harness/driver.c` |

**H4 deserves its own line in a brief**, because it is the one place a
plausible implementation is silently wrong: handing python `re` the
*unexpanded* text would make it compile the primary alone (the `(?&n)`
raises `re.error`, so it would be skipped rather than mis-verified —
but a *skip* that nobody counted is AR-3's failure mode exactly).

**H2 and H2b are SEQUENTIAL, not one derivation** (r44-consumers U9).
Two resolutions run, in order, and confusing them is how a control ends
up sharing a source with its subject:

1. the FORMAT's cross-file resolution — which definitions are bound into
   this pattern, with what numbers and what name qualification (H2, in
   pcrec);
2. pcrec's own intra-pattern `(?&name)` binding in `recursion`'s AST,
   which runs on the resulting pattern exactly as it runs on any other.

H2b's textual expansion is a THIRD, independent path to the same
intended answer, written for the oracle. Its value is precisely that it
does not share step 1's implementation — which is also why it must
declare the population where it is valid rather than silently agreeing
everywhere.

### 3.3 What `--list-*` surfaces are affected

- **`--list-syntax` GAINS ROWS, and this is a change from the first
  version.** That version said "this design adds no construct", which was
  true of textual composition and is false of D87: §1.5's numbered group,
  scope prefix and delivering call are three new PATTERN constructs, and
  the registry is where a construct's existence, its owning module and
  its `built` status are stated (D65). They are DIALECT rows — spellings
  PCRE2 refuses (measured, §1.5) — which is the same shape
  `pcre2_compliance.md` already handles for pcrec-only forms. The
  constructs composition RIDES are unchanged and already `built`:
  `(?&name)`, `(?(DEFINE)…)` and the named-group spellings (MEASURED,
  §2.3.3).
- **`--list-definitions` gains a second reason to exist.** Beyond D85's
  option-scoped replacements, a user of a library wants to see what
  `lib <rfc5322>` brought into scope. Same table, same surface (§4.2).
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
  landing. Frank's `description` ruling sharpens what it would print: a
  file's summarizing script reads `description` fields, so the surface is
  "what this file declares, with each declaration's description", not a
  bare list of names.

### 3.4 The spec delta (D80: the contract changes in the same change)

`docs/spec/rxt_format.md` is the contract, and a parser landing without
its spec hunk is rejected on sight (D80; CLAUDE.md's situation index).
The hunks, named so a reviewer can check them off:

| # | hunk | wave |
|---|---|---|
| S1 | "The `.rxt` format" gains **HEAD and BODY**: the head's six declarations, the two head block kinds, and the rule that the head ends at the first `pattern` line | W1 |
| S2 | A new section, **"Composition"**: the AST-level model, D87 rule 7's assignment rules (a)-(j), lexical-scope-wins with internal name qualification, the visited-set closure, the five namespaces, and the statement that a composed block's oracle is necessarily `pcre2` | W1 |
| S2b | `docs/spec/` gains the **pattern-language extensions** (§1.5): the numbered group, the scope prefix, the delivering call — each with the "no legal PCRE2 pattern changes meaning" constraint and the measurement that admits it. These are DIALECT constructs, so `--list-syntax`'s registry gains their rows (§3.3) | W1 |
| S2c | A **"Delivered results"** section: the inline struct, path = member path, first-set-wins for duplicate names in one path, the two non-deliverable shapes and their refusals, and the one sentence about two call sites being distinct C types needing `__typeof__` (§2.13) | W1 |
| S3 | "How the harness evaluates a block" gains the **cell** notion and the `perr` one-cell rule; the summary's reported quantities grow (entry files, fragments, cells, resolution failures) | W1 |
| S4 | The **subject** subsection gains `@file:"path"`, and states the escape asymmetry (quoted subjects decode escapes, file subjects do not) | W2 |
| S5 | "The driver protocol" gains the `@<path>` argument form and its byte-exactness guarantee | W2 |
| S6 | A new section, **"Data blocks"**: the family, the membership rule (`question`/`reader` required), `freq`'s body, and the provenance fields with the reason they are required | W2 |
| S7 | The `oracle` line and `# pcre2-only`'s status as its alias | W3 |
| S8 | `variant` and the declared-`unsupported` outcome | W3 |
| S9 | `docs/spec/match_api.md` §6: **`rx_info.name`**, and the `abi` bump sentence — one of D76's four sites, all four in the same change | W1 |
| S9b | `docs/spec/match_api.md` §2/§5: **D61 made concrete by its first producer.** `ngroups`/`nnames` are the PRIMARY's own on a composed artifact; the composition's delivered slots occupy `ngroups+1 ..`; `RX_NCAPS` is an artifact constant a caller sizes from the header and **may move across library versions** while every index in `1..ngroups` holds still (r44-sem M4/M5). Also the difference between `--source` composition and handing a composed TEXT to plain `-p`, which counts every group | W1 |
| S10 | `docs/spec/limits.md` "Handling an oversized artifact" item 1 already promises the `config` block; when W1 lands, that sentence stops being a forward reference and gains a pointer to S1 | W1 |
| S11 | `docs/spec/cli.md`: `--source`, `--target <prefix>`, `--lib-path DIR`, **`--emit-composed`**, and §2.7's **output-naming rule** (`-o <dir>` per target; `-o <file>` with N > 1 refused) | W1 |

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
declares definitions with `name`, carries their own tests as ordinary
cases, and carries a `description` per definition so a store index can be
generated rather than written (Frank's r44 ruling — "summarize via script
what a library has"). It declares **no targets**, and its tests **do not
run** in a file that `lib`s it (they run when the library file is itself
under test — which is what makes the store's "each entry oracle-verified"
discipline mean something).

**A library is self-contained, and after r44 that is a mechanism rather
than an assertion.** The first version said "a user cannot accidentally
satisfy a library's reference from their own file"; r44-sem M2 MEASURED
that FALSE under the textual model — a caller's `(?J)` plus a colliding
name handed the library's private helper to the caller's group, inverting
the library's answer. It is true under D87: a library's internal
references bind in the library's own lexical scope, and the composer
qualifies injected names internally, so the caller cannot name them at
all (§2.3.2, §2.3.3 M2). The caller can still reach them deliberately —
that is what the scope prefix is for — which is the difference between
"self-contained" and "sealed".

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

1. **A lookup**: `resolve(name, option-scope) -> a definition, or
   not-found`. The result must be able to be a **BUILDER** — an AST, or
   something that produces one — not only text (r44-consumers M12): D87
   makes composition an AST operation, so a text-only interface would
   force the composer to re-parse and would put a second parser where
   learnings §3 says not to. That is the whole surface; the format's
   resolver (§2.3.2 step 2) calls it and does not walk the table itself.
2. **Determinism and orderability**: the table's answer for a given
   (name, option scope) must be stable across a compile, and when two
   rows could apply the table's own first-applicable-wins rule decides —
   the format never breaks a tie.
3. **A duplicate report WITH ORIGIN**: the format must be able to ask
   whether a name is defined by more than one *file* in its scope,
   because that is refused by name (§2.2) and the refusal must say which
   two files. D85 frames a library definition as a row with a predicate,
   so "two libraries define `email`" is two rows with the same key — but
   a predicate tag carries no file identity (r44-consumers M12), so the
   **origin is a COLUMN on the [LIB] store entry**, not a parameter of
   the tag. The table reports both rows and their origins; the format
   refuses and names them.
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
  file with no head has no references to bind, so the AST the compiler
  gets is the one it gets today and the output is byte-for-byte today's.
  **The format cannot add dispatch, because in that case it adds nothing
  at all.**
- **R-VE-3** (content-addressed shared-data dedup, and at what
  granularity) — **DEFERRED under D77, explicitly rather than by
  silence** (r44-consumers U8). The requirement is on the format's
  INFORMATION CONTENT: the format must expose enough per named pattern
  for a content hash to be taken at the right granularity. It does — a
  definition is a named, separately identified AST with its own assigned
  numbers — but *which* granularity is right is a codegen question with
  no consumer until multi-pattern units exist. **The trigger is [V-E]
  opening**, and the interface it will find is §4.4's own list, not a new
  one.
- **R-VE-5 / D39.2** (appended numbering) is now **D87 rule 7(i)**, and
  it is stronger than the first version claimed. That version said the
  rule "falls out of appending the DEFINE block" — true of PCRE2's
  positional numbering, and therefore true only of the textual control.
  Under D87 the composer ASSIGNS: a definition's groups are re-based
  above the caller's `ngroups`, local order and gaps preserved, the
  caller's numbers untouched. R-VE-5's actual requirement — "re-ordering
  an unrelated part of the file must not silently renumber an unrelated
  pattern's captures" — is met by the assignment being derived from
  reference structure, and D61 makes it a shipped promise rather than a
  property of where the block was written.
- **R-VE-4** (source-level vs link-level composition kept distinct) —
  the format expresses the **source-level** tier only, and expresses it
  as a PCRE2 subroutine call. Link-level composition
  ([M4-CALLOUTS]'s aligned ABI, non-regex predicates) has no spelling
  here and must not acquire one that looks the same; §7 Q4 records that
  as the open item it is.
- **R-VE-6 / D39's labelled references** (`"a:reg1"`, path composition
  `"c:a"`) — **the format DOES have the label, and D87 named it**: it is
  the delivering call's site name, and D39's "composed into a path for
  nested insertions" is §2.13's scope path exactly (`from.local`). A
  definition still appears **once** in the closure however many times it
  is called (§2.3.2's dedup); what a second call site adds is a second
  *delivery*, which is where the label was always needed. The first
  version said "the format needs no label", which was right about the
  closure and wrong about delivery.
- **R-VE-12** (a per-pattern encoding field) is an `encoding` line at
  block or config scope, more-specific-wins (§2.6) — D58 makes it a
  per-pattern scalar, so a block must be able to state it (r44-sem M16);
  the first version had only the `config` spelling.
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
| `objective`, `description` (prose) | **`description \|` block scalars** — file-level for the sub-bench, per block for a member (Frank's r44 ruling; §1.2). The first version sent this prose to `NOTES.md`; it is a FIELD, so a summarizing script can read a sub-bench's objective without a second file |
| `regimes = [...]` | `tag regime=search_short throughput` (file-level; bare labels and pairs both allowed, U1), refined per block (below) |
| `[[patterns]].name` | `name <ident>` (block-scoped) |
| `[[patterns]].file` | the `pattern` line itself — the `.rx` file disappears |
| `.feature_tier` | `features <list>` (a real directive) plus `tag tier=base` for the bench's own vocabulary |
| `.hazard_class`, `.size_class`, `.convention`, `.role` | `tag hazard=… size=… convention=… role=…` |
| **`.tags` (the free LIST — up to 6 bare labels per pattern)** | `tag` accepts **bare labels beside pairs on one line**, and repeated `tag` lines accumulate: `tag logs identifier control` then `tag regime=search_short` (r44-consumers U1; the first version's `tag-pair` required an `=` and dropped the list) |
| `[subjects].generator`, `.manifest`, **`.throughput_generator`, `.throughput_manifest`** | the directory convention — a generator beside its output, exactly as `tests/recursion/gen_corpus.py` already is. All four, not the two the first version listed (r44-consumers U5) |
| `[subjects].short_search_max_bytes` | `tag short-search-max-bytes=4096` |
| `[expectations].file` | `include "gen/expectations.rxt"` |
| `[expectations].default_method` | **TWO fields, not one** (r44-consumers U3): `oracle pcre2` names the ENGINE that checks, and `tag method=libpcre2-differential` names the VERIFICATION METHOD. R-BENCH-1's methods include non-oracle ones — "derived-law-plus-induction" is a real, already-used method (the K23 closed form) with no engine behind it — so folding method into the oracle enum would make those unspellable and would put a pcrec-shaped enum where AR-6 requires engine-neutrality. The first version conflated them |
| `[testees.pcre2].options` | `config pcre2` with `testee pcre2/10.46` + `option k=v` lines |
| `[testees.pcrec].options` | `config pcrec` with `pcrec --features all` |
| `patterns[].variant = null` | the **absence** of a `variant` line |
| an `expectations.tsv` row | `m @file:"subjects/s-000.bin" 234 258` / `n @file:"…"` / `mc @file:"…" <n>` |

**The four bench requirements that needed a decision, decided:**

1. **OUTCOME (§4.4), all twelve values accounted for** — the first
   version mapped 5 of 7 per-subject and 3 of 5 per-testee and was
   silent about the rest (r44-consumers U2). Per subject:
   `matched-as-expected` / `did-not-match-as-expected` /
   `wrong-span-or-captures` are what `m`/`n`/`g` already score;
   `gave-up` is `gu` (MEASURED live, 23 uses, §2.11); `crashed` /
   `timed-out` are the harness's own (exit ≥ 124 / ≥ 126, already
   distinguished by `run.sh`) and are never expectations.
   **`truncated-subject` is NOT REPRESENTABLE in this format, and that is
   deliberate**: it means the engine consumed fewer bytes than offered,
   which is a property of an ADAPTER's call, not of a pattern's answer —
   the bench records `consumed_length` where the API exposes it, and no
   `.rxt` line kind could produce that number for a foreign engine. It
   stays **bench-side**, and this note names the gap rather than leaving
   the reader to find it. Per testee: `did-not-compile` is `perr`;
   `unsupported-by-declaration` is `variant <testee> unsupported
   <reason>` — one line kind for both halves of the variant axis;
   `crashed` / `timed-out` are the harness's; **`compiled` is the
   ABSENCE of the other four**, a record-side default with nothing for
   the format to say. Two of twelve are bench-side by nature; ten map.
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
   `tag regime=search_short` (the bench's own spelling, underscored —
   r44-consumers U4 caught the first version writing `search-short`) and
   its own subject set. **MEASURED, the wrapper is
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
identification, or does T-3 overstate it?"** (This, and attack 2's
concession, are the two residuals r44-consumers U11 asked be kept named
rather than argued away; they are.) **MEASURED, the tension is
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
time has passed."** **RE-RUN, and independently REPRODUCED.** 2026-08-17:
54 files / 1,100 blocks / 9,977 expectation lines. 2026-08-29: **179 /
3,265 / 26,691** — 3.3× in twelve days — and r44-grammar, running its own
recognizer transcribed from `run.sh`'s 13 dispatch regexes rather than
from this note, "reproduced [them] to the digit" (G1), along with 0 head
lines, 0/32 keyword collisions and 636 `# pcre2-only` marks. **AR-1's
cost of getting compatibility wrong has tripled since AR-1 was written**,
which is an argument for the design's caution, not against it.

The 26,691 is a **three-way partition**, not one of the three numbers
`run.sh` prints (r44-grammar G2 corrected the first version's wording):
**22,125** subject cases (`m`/`n`/`ms`/`ns`/`gu`) + **4,182** group-slot
lines (`g`/`gp`) + **384** `perr` blocks. A `perr` block and a live `g`
line each record independently, so the harness's `cases passed` +
`cases failed` + `group cases pending-vm` is a different partition of
the same population.

**And two attacks the panel added.** r44-grammar tried four ambiguity
attacks on §1's grammar and **all four failed** (G5): a `pattern` line
inside a data block (the head-ender closes the block first); a
`#pattern` comment (column-1 `#` is tested before dispatch); a config
line whose value is a keyword (`rest-of-line` is never re-tokenized);
and a keyword colliding with a VALUE, which is impossible by
construction because dispatch is on the first token and values never
occupy it. **That run is what makes §2.10's `analysis freq <name>`
argument a demonstration rather than an assertion** (r44-consumers U11):
the ambiguity it avoids was checked, not asserted. r44-grammar also
confirmed (G6) that today's harness already hard-errors on any
non-comment line before the first `pattern`, so a head changes which NEW
files parse and never the meaning of the 179.

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
| **AR-2** no dispatch in the common case | a pattern with no file references binds nothing, so the AST is the one the compiler builds today. §2.7's default: one unnamed block, no head → `target rx`, byte-for-byte today's output. The format cannot add dispatch because in that case it adds nothing. **D87 strengthens this**: an UNDECLARED call stays capture-transparent at zero cost (rule 5), so even a composing file pays only for the deliveries it declares |
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
| **OD-6** the data block's spelling and namespace | **inline values, own namespace** (§2.10). This is OD-6, named — the first version presented it as departure "D-e" without citing the open decision it disposes of (r44-consumers U10) |
| **OD-3** config syntax unifying testees and build variants | **one block kind.** A build variant is a `config` with `pcrec` lines; a bench testee is a `config` with `testee` + `option` lines. R-BENCH-9's "one concept, two uses" is literal here — the same `config` grammar, differing only in which of its line kinds appear |
| **OD-4** interface/reference-only marking; a test-only surface | **no marking, no surface** — T-1 |
| **OD-5** PCRE2 desugar vs own spelling | **PCRE2's `(?&name)` — and, after D87, a deliberate, minimal DIALECT around it.** The spelling stays PCRE2's; what is pcrec's own is the number ASSIGNMENT (rule 7), the scope prefix and the delivering declaration (§1.5), each measured to be a spelling PCRE2 refuses. OD-5's two feared consequences are corrected: subroutine calls are **backtrackable**, not atomic, on 10.46 (§2.3.5), and the numbering is now an assigned property, not a positional accident. The item's own tag — "measured, never read from docs" — is honoured twice over: §2.3.3's semantics and §1.5's free-ness are both runs, on both oracles |


---

## 6. Worked files, in the final grammar

Every example below parses under §1.3 by the hand-trace beside it, and
every composed pattern in §6.1 was **compiled by `build/pcrec` and run
through `tests/harness/driver.c`** — the cells are measured, not
asserted.

### 6.0 The PIECE RULE — five ways a definition can depend on its site

A library definition is a **piece**, and a piece can be written so that
its meaning depends on where it is called. r44-sem enumerated the class
and the first version had only one member of it. **There are five**, and
they do not all have the same fix:

| # | class | witness | fate |
|---|---|---|---|
| (i) | **absolute subject tests** — `^`, `$`, `\A`, `\z`, `\Z`, `\G` | the position paper's own §3a: `email` = `^(?&local)@(?&domain)$` called from `From: (?&email)` → **nomatch**. Controls: `x(?&e)…(?<e>a$)` on `"xa"` matches, `x(?&e)y…` on `"xay"` does not | **REFUSED at the [LIB] store by a scan** — a piece carries no subject anchor |
| (ii) | **EDGE assertions reading the caller's text** — `\b`, `\B`, a lookbehind `(?<!…)` | `(?<e>\ba)` is nomatch on `xa` and match on `-a`: the callee reads the byte before the call site | **DOCUMENTED, not refused.** A piece may legitimately be edge-sensitive — "a word-boundary-anchored token" is a piece somebody means to write. The store records it; the caller sees it in the `description` |
| (iii) | **match-span writers** — `\K` | `^x(?&g)$` with `g` = `a\Kb` on `xab` reports **(2,3)**: `\K` ESCAPES the callee and rewrites the CALLER's reported start | **REFUSED by the store scan.** A piece may not move its caller's span |
| (iv) | **width-constrained CALL SITES** — a lookbehind caller | a definition legal everywhere else is a compile error from inside a lookbehind (libpcre2 err 125, "unbounded") | **A SITE RULE, not an authoring rule** — it is the caller's lookbehind that constrains, so it cannot be checked at the store; it is a refusal at the call site with the reason |
| (v) | **absolute numeric references** — `\1`, `\g{1}`, `(?1)`, `(?(1)…)` | §2.3.3 M1: `(\d)\1` composed naively inverts | **DROPPED from the refusal list by D87.** Rule 7(i) RE-BASES them, measured to restore the piece's own meaning. The manager's recommendation to the panel was to refuse; Frank ruled the mechanism instead, and the rule is now that a piece's absolute references are LOCAL to the piece wherever it lands |

**So the [LIB] store's entry scan covers (i) and (iii) mechanically** —
both are a lexical property of the definition's own text, checkable
without knowing any caller. (ii) is documented rather than refused
because refusing it would refuse patterns people mean. (iv) belongs to
the call site. (v) needs nothing at all any more, and that is the
clearest single consequence of D87 for [LIB]: the refusal list is
**two** members long, not five, and the two that remain are the ones a
piece has no business doing.

**Whole-string matching is not what the anchors are for.** A caller who
wants the whole subject writes their own `^…$`, or better uses the
artifact's own anchored entry `<prefix>_match`
(`docs/spec/match_api.md` §3.2), which exists precisely so a pattern
need not be re-spelled to be matched whole.

**The format cannot check (i)-(iii) statically for an arbitrary
pattern** — a `$` inside a callee is legal when the callee is the whole
target — so what it does is make the failure loud in the ordinary way:
the composing block's own `m` case goes red. The store scan is the
place the rule becomes mechanical, and that is [LIB]'s to build.

### 6.1 A library and a user of it ([LIB], U4/U5, W1)

`lib/rfc5322.rxt` — definitions are pieces, no anchors, no targets:

```
# Operational note: regenerate the tests with tools/gen_rfc5322.py.
description |
  RFC 5322 address pieces. Definitions only; this file declares no
  targets, so `pcrec --source` on it emits nothing.
  Every definition here is a PIECE: no subject anchors (§6.0 (i)).
tag objective=subroutines

pattern [A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*
name local
description The dot-atom local part, unquoted forms only.
m "john.doe" 0 8
n ".john"

pattern (?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}
name domain
description A dotted host name with a 2+ letter TLD. No IP literals.
m "example.com" 0 11

pattern (?&local)@(?&domain)
name email
description An addr-spec: local part, @, domain. Unanchored.
m "john.doe@example.com" 0 20
n "john.doe@"
```

`mail.rxt`, a user of it:

```
lib "lib/rfc5322.rxt"
target mail = from_line
  description The From:-line matcher the mail daemon links.

pattern From: (?&from=email)
name from_line
m "From: a@b.co" 0 12
```

**Hand-trace.** *`lib/rfc5322.rxt`*: head = a `description` block scalar
(three indented lines, ending at the non-indented `tag`) and one `tag`;
body = three blocks, each with its own one-line `description`. Blocks 1
and 2 declare no group and reference nothing, so composition binds
nothing and they compile exactly as written. Block 3 references `local`
and `domain`, both resolved in this file; the closure is those two, each
bound with its groups re-based above `email`'s own `ngroups` (which is
0). Being composed, the block's oracle is necessarily `pcre2` (H4). No
`target` line and more than one block, so **`pcrec --source
lib/rfc5322.rxt` emits nothing** — a library ships nothing by itself
(Frank §6.4).

*`mail.rxt`*: head = `lib`, then `target` with an indented `description`
attached to it (§1.2). `target mail = from_line` forward-references a
definition in the body — normal: the head precedes the body and
resolution is a whole-file pass. The block writes a **delivering call**,
`(?&from=email)` (§1.5 B3), so the caller gets
`struct { rx_span local, domain; } from;` and can read `r.from.domain`;
an ordinary `(?&email)` would have been capture-transparent and free.
`email` is not defined in this file, so it resolves in the `lib` chain;
its own references are then resolved in *rfc5322's* scope — the caller
could not satisfy them even by declaring `local` itself (§2.3.2).
**The library's own five cases do not run here.** `pcrec --source
mail.rxt -o mail.c` emits one artifact under prefix `mail`, with
`rx_info.name == "from_line"`, `ngroups` **0** (the primary declares no
group of its own — D61) and the three delivered slots above it.

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

Two things to read off the last two rows. `RX_NCAPS` is 1 + three
definition slots — but under D87/D61 those three sit **above `ngroups`**,
which stays at the primary's own count, so the numbers a caller indexes
by do not move (§2.3.1 rule (i)). And these cells are measured through
the TEXTUAL control (`(?(DEFINE)…)` appended), which is legitimate here
because this file is inside the control's valid population: no absolute
numeric reference anywhere in it, and no name collision between caller
and closure (§2.3.4). That is the control doing its job — agreeing with
the composer on the population where both are defined.

### 6.2 A bench sub-bench as one file (U7/U8, W2+W3)

The live `bench/loglines/` sub-bench, in the format. The **objective is
a field now**, not a `NOTES.md` paragraph (Frank's r44 ruling); the
generator still stays beside its output; the directory stays a directory
and no tool reads it as a schema.

```
# Operational: regenerate subjects with gen_subjects.py before editing.
description |
  Log-line search over mostly-FAILING text: what an engine pays to
  establish that a chunk of log lines does NOT contain the shape an
  operator is grepping for, at the sizes a log shipper hands a matcher
  (256 B - 4 KB) and across a size sweep to 1 MB.
  The set contains both cases the answer turns on: patterns whose match
  requires a literal byte, and patterns built only from classes, which
  no required-byte precheck can help.
tag id=loglines version=0.1 objective=realworld
tag short-search-max-bytes=4096
oracle pcre2
tag method=libpcre2-differential

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
description ISO-8601 timestamp with optional fraction and zone.
tag logs timestamp iso8601 tier-base
tag regime=search_short tier=base hazard=none size=medium
tag convention=perl-leftmost-first role=member
variant re2 unsupported no per-engine spelling preserves the objective
m @file:"../subjects/s-000.bin" 234 258
n @file:"../subjects/s-001.bin"
m @file:"../subjects/s-002.bin" 0 24
… 109 more

pattern :
name floor
description The floor control: one literal byte, structural in every log format here.
tag floor control one-literal
tag regime=search_short role=floor hazard=none size=tiny
m @file:"../subjects/s-000.bin" 24 25
… 111 more
```

**Hand-trace.** The entry file's head carries a `description` block
scalar (six indented lines, ending at the non-indented `tag`),
file-level `tag`s, an `oracle` naming the ENGINE and a separate
`tag method=…` naming the VERIFICATION METHOD (§4.5, r44-consumers U3),
three `config` blocks (one with a `pcrec` line, two with `testee`
lines), a `use` naming all three, and two `include`s. The fragments
carry pattern blocks only; their `@file:` paths are relative **to the
fragment** (§2.8), hence `../subjects/`. Each member block carries a
`tag` line of **bare labels** — the sidecar's free `tags` list (U1) —
beside a `tag` line of pairs, both accumulating. Each block runs as
three cells (`use` enumerates, §2.6); the `variant … unsupported` line
makes `re2`'s cell for `iso_ts` a declared, counted non-result rather
than a wrong answer (bench §4.4). The tally is reported under
`loglines.rxt` with `entry files: 1  fragments spliced: 2` (§2.11), and
each failure still prints the fragment's own `file:line`.

**Note what this file does NOT do: it composes nothing.** No block
references a definition, so §2.3's machinery never runs and the textual
control is not needed. A bench sub-bench is a flat corpus with a rich
head — which is why it earns W2/W3 and not W1.

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
  description Byte histogram of one month of production nginx access logs.
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

**Hand-trace.** The findings file's head is one data block, its body
lines indented under it (§1.2); the file's body is empty — a legal file
with zero pattern blocks, which the grammar admits
(`body = { pattern-block }`, possibly none) and which is the point: this
is data, not tests. `question` and `reader` are required, which is
§2.10's membership rule made structural; `description` is the field a
summarizing script reads. The user's file `lib`s a library by its
**store** spelling (`<rfc5322>` — searched on the library path, never
relative), `include`s the findings file by its **local** spelling,
selects the table in a config, and builds one target against it. **The
same pattern built against a second exemplar is a second `target` line,
not a second file** — which is what made the target-as-declaration shape
right.

**The `row` arity is a SEMANTIC check, not a grammatical one**
(r44-grammar G4). The production admits any `row` of one offset plus one
or more counts; that 16 rows of 16 counts make exactly 256, that the
offsets are 0, 16, … 240, and that every count is non-negative are
checked **when the data block is parsed** (H9), with the refusal naming
the row. The first version's prose read as if the grammar guaranteed
it — a grammar cannot count to 256.

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
non-blank line is a `pattern` line, true of all 179 corpus files
(MEASURED §5.1, independently reproduced by r44-grammar G1). Body: four
blocks. No block declares a group or references a definition, so
composition binds nothing and the compiler input is byte-for-byte
today's. No `target` line and more than one block, so the file builds
nothing. The `perr` block is evaluated in exactly one cell (§2.6).
`\x41` and `\n` decode as they do today. Every line is unindented, so
the head/continuation rule (§1.2) never engages. **Nothing in this file
is new, nothing in it means anything different, and nothing in it needed
to change.**

---

## 7. Open questions for Frank

### 7.0 What is no longer open

Six of the first version's questions and residuals are settled, and this
list is here so nobody re-answers them:

- **Q1 (where prose lives) is ANSWERED — the other way.** Frank, r44
  15:0x: *"we may want to summarize via script what a library or other
  rxt file has: therefore a description may be helpful outside of
  comments, which should be operational."* `description` is a machine-
  readable FIELD at file, definition, target and data-block level, with a
  YAML-style `|` block scalar for multi-line prose (15:1x). The note's
  recommendation — prose in `#` comments and `NOTES.md` — is **overturned**
  and gone from §1.2, §4.5 and §6.
- **Who composes, the numbering, and the collision rule** are D87 rules
  1, 2 and 7. §2.3 is rewritten around them.
- **"May a scope prefix reference CALLED groups?"** — which the first
  version could not answer — is settled by D87 rule 5: **yes, exactly
  where the call is declared as DELIVERING** (§1.5 B3, §2.13). A
  delivering call creates the scope; an undeclared one has no groups to
  name and stays capture-transparent.
- **The three spellings** (numbered group, scope prefix, delivering
  declaration) and the `.rxt`-level syntax calls are the manager's under
  Frank's 14:5x ruling, and are settled in §1.5 and §1.3 rather than
  asked here. One of them was settled by MEASUREMENT against the brief's
  own leading candidate — see the note in §7.1.
- **`analysis freq <name>`** (OD-6) is the manager's, accepted at the
  panel, and r44-grammar G5's run demonstrated the ambiguity it avoids.

### 7.1 One thing the manager should see before settling B3

The leading shape offered for the delivering-call declaration,
`(?<from>&email)`, is **DISQUALIFIED by measurement**: it is an ordinary
legal PCRE2 pattern today — a named group `from` whose body is the
literal `&email` — and it matches the subject `&email` at (0,6) on
libpcre2 10.46 AND on pcrec (§1.5). Adopting it would change the meaning
of patterns that already exist, which is the one constraint every
candidate must satisfy. §1.5 recommends `(?&from=email)` /
`(?&=email)` instead, with all candidates' free-ness measured.

### 7.2 The questions that remain

**Q2 — `features` composes by UNION, with `features only` for a
deliberate narrowing.** RECOMMENDED, and r44-sem could not refute the
union rationale (8 probes: every difference was refuse→compile, never
match→different-match). r44's counter-case (U12): more-specific-wins
would let a block test under FEWER modules than the file intends.
`features only` is the answer — the narrowing exists and is a thing an
author wrote (M14). The `perr` one-cell carve-out stands and is what
protects **384** blocks.

**Q3 — the PIECE RULE is a [LIB] store scan, and it is now a
five-member class with two mechanical members.** r44-sem found the first
version had one member of five (M6, §6.0). After D87 the store scan
refuses exactly two — subject anchors and `\K` — because absolute
numeric references are now RE-BASED rather than refused, and edge
assertions (`\b`, a lookbehind) are a legitimate thing to write and are
DOCUMENTED. r44's counter-case (U12): a static top-level `^`/`$` check
catches the bug once. Agreed, and that is what the scan is.

**Q4 — the link-level tier still has no spelling, and should not
acquire one by accident.** RECOMMENDED: confirm that [M4-CALLOUTS]'s
aligned-ABI tier gets its own construct and that `(?&name)` never means
"link to a separately compiled part". r44's counter-case (U12): reserve
a distinct sigil NOW rather than later. **This note declines to reserve
one** — D77, no consumer — but records that §1.5's constraint is what
makes reservation unnecessary: any future construct must also be a
spelling PCRE2 refuses, and that space is large.

**Q5 — W2's include-closure accounting is designed against a population
that does not exist.** No cross-file generator exists in either repo.
RECOMMENDED: ship W2 when the bench's 1,364-row expectation fragment
needs it, and treat that set as the validating measurement. r44's
counter-case (U12): build §2.11 now, because the bench row is already
blocked on it. **Both are right about different things** — the bench is
blocked on the FORMAT, not on the accounting rules, so W1's landing
unblocks the authoring and W2's landing carries the accounting with its
first real population.

**Q6 — a bench sub-bench references its canonical pattern per regime
rather than repeating it.** RECOMMENDED: reference now — MEASURED,
`expectations.tsv` has no capture columns at all, so the wrapper is
span-identical — and revisit when bench adds capture checking (its
OD-B9). r44's counter-case (U12): writing the pattern text directly
avoids a corpus-wide rewrite later. The trigger is named either way;
the choice is whether to pay now or on a known signal.

**Q7 — NEW, and it is the residual D87 creates: the oracle control no
longer covers the whole population.** Under the textual model the
control was total. Under D87 it is valid only where the append form
means what the composer means — **no absolute numeric reference in any
body, no name collision between caller and closure** (§2.3.4) — and
those are exactly the two shapes D87 added mechanism for. So the format
gains two capabilities whose answers no independent oracle checks.
**RECOMMENDED: accept it for W1 and name the trigger rather than build
a second oracle now.** Three reasons: the shapes are individually
verifiable by hand today (§2.3.3's M1 and M2 cells are that, on both
oracles); `--emit-composed`'s round trip is a real, if weaker, control
(pcrec must agree with itself across a serialization boundary); and a
second oracle means a second composer, which is the drift hazard
learnings §3 exists to name. **The trigger to revisit: the first
library entry that legitimately needs an absolute reference or a
colliding name.** If that never happens, the uncovered population is
empty and the residual costs nothing — which is itself worth measuring
at the [LIB] store's first ten entries.
