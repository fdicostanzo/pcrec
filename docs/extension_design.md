# pcrec's extension mechanism — design

**Status: PROPOSED AND PARTLY REFUTED, 2026-08-11. Not built. Not adopted.**

> ## PANEL OUTCOME — READ THIS BEFORE ANY SECTION BELOW
>
> A five-lens panel (R13, `docs/reviews/2026-08-11-r13-extension-design.md`) ran
> against the first draft of this document and refuted several of its
> load-bearing claims with measurements. The sections below have been corrected
> in place; the corrections are marked **REFUTED** or **CORRECTED** and carry
> the measurement that did it. **Where the refutation left a hole, the hole is
> marked [OPEN] rather than filled** — filling five holes at the desk, unreviewed,
> is precisely the mistake the panel just caught.
>
> **What survives intact:** one table with one row per construct (§2); names as
> the unit of enable/disable, and the measured fact that they are already
> half-built (§3); two ports per row (§4); the shared generic wrapper and
> data-driven class ports (§4.2); and the RECOGNISE-then-PRODUCE seam as an
> idea (§5).
>
> **What was refuted:**
> - **§2.3, position-independent selection — FALSE.** Four critics independently.
>   `(a)×12\12` is a backreference; `(a)×12[\12]` is still OCTAL. Selection
>   differs by position, so recognition must be PER-PORT.
> - **§6's "the SHAPE column decides" — FALSE.** The DOORWAY decides.
>   `[0-\p{Foo}]` is 147, not 150.
> - **§6 covers only the HIGH endpoint**, and the two sides are not symmetric:
>   `[0-[.ab.]]` is 150 but `[[.a.]-z]` is 113.
> - **§4.4's five outcomes are incomplete**, and one natural reading is a TIER-1
>   MISCOMPILE: `^\Qab\E*$` matches `abbb` and NOT `ababab`.
> - **§4.1's "a NULL class port means exactly one thing" — FALSE.** It has at
>   least three meanings, and `[\k]` compiles as the literal `k`.
> - **§5.2's TERMINAL level is incoherent at `(?(`**, whose correct answer needs
>   a top-level branch count, which is parsing.
> - **§5.4's invariant holds VACUOUSLY**, by single-pass termination rather than
>   by design — and §10.6's pre-scan breaks it for real.
> - **§8's checks 3, 4 and 6 are vacuous or mis-scoped**, checks 4 and 6 in the
>   K10 shape this document cites as its template.
>
> **And the panel found a live shipped bug the design would have frozen: K13.**
> Twelve rows answer the class position with the wrong module.

This document describes, from scratch, how a regex feature is added to pcrec.
It draws on D24, D26, D28, D30, D32 and D33 and on the R10/R11/R12 panels, but
it is not an amendment to any of them: where it disagrees with an existing
decision, this document is the newer thinking and the older entry is the record
of how we got here. Nothing here is implemented. Open questions are marked
**[OPEN]** and are for Frank.

Every measurement in this document was taken on 2026-08-11 against libpcre2
10.46 (through `tests/fuzz/pcre2_abi.h`, because this box has the runtime and
not the `-dev` package) or against `build/pcrec` at `5173a82`, and is quoted
with the probe that produced it.

---

## 1. What an extension is, and what problem this solves

pcrec compiles a PCRE2 pattern to C. It implements a base grammar — literals,
concatenation, alternation, classes, quantifiers, groups — and **everything
else is an extension**: lookaround, backreferences, recursion, Unicode
properties, inline modifiers, backtracking verbs, callouts, conditionals.

Three obligations shape the mechanism, and they pull in different directions.

**A. Never miscompile.** An unimplemented construct must produce a clean
diagnostic, never a matcher for a different language. This is the project
charter, and it has been violated four times (K5, K6, K8, and SPEC-FA's
`[0-[:digit:]]`), each time by a construct that pcrec silently read as
something else.

**B. Answer exactly, even for what we do not implement.** Under D26, *what a
pattern matches* and *whether a construct is real, and which module owns it*
are TIER 2 and exact. The wording of a diagnostic is tier 3. So pcrec must know
the full PCRE2 construct space, including the parts it will never implement,
and must attribute each part correctly — before any of it is built.

**C. Add a feature in one place.** D24's rule: adding a construct should mean
adding a row, and nothing else. Every time the project has had a fact about a
construct in two places, they have drifted (`\v`, K3, K4, K10).

The mechanism below is a single table of constructs, where each row carries a
**name**, up to two **handler functions** (one per syntactic position), and the
data needed to answer for the construct whether or not those handlers exist.

---

## 2. The table

**One row per construct. One table.** Not one table per position, and not one
table per module.

The alternative — a table for class-context constructs and a table for
atom-context constructs — was considered and rejected. Their overlap is exactly
the escape doorway's class-shaped rows, and **that overlap is where K10 lives**:
K10 is one construct (`\N{U+hhhh}`) whose class-position facet
(`RF_CLASS_INVALID`) contradicts its own atom-position `note`. Split across two
independently-keyed tables, that self-contradiction becomes two rows with
nothing forcing them to agree — the same failure one level up, and harder to
check, because there is no longer a single object to compare with itself.
Related data stays together.

### 2.1 Buckets

A row belongs to a **bucket**, the syntactic doorway at which its construct can
appear. Four exist (`RegKind`, `internal.h:208-213`):

    RK_ESC           after `\`
    RK_GROUP         after `(?`
    RK_VERB          after `(*`
    RK_CLASSBRACKET  after `[` inside a class

Buckets are a property of PCRE2's grammar, not of pcrec, and this design does
not change them.

### 2.2 Selection within a bucket

Unchanged from D32, which resolved it after three panels:

- **`sel`** — the selector byte — is a **checkable pre-test**, not a key: "do
  not call me unless the first byte matches". The handler is the truth.
- A row's recogniser is **positive and local**: it recognises its own proper
  form and knows nothing about its siblings. `\N{U+` asks only "does the text
  start with `{U+`"; bare `\N` answering "always" is CORRECT.
- **Multiple rows answering is normal.** `rank` is a **local tiebreak**,
  meaningful only between clashing rows — measured, four buckets and 22 rows;
  the other 78 are alone in their bucket and carry no meaningful rank.
- **Two answering rows at EQUAL rank is a defect**, reported as an internal
  error. Measured not to fire on the correct table: 0 collisions over 3,507
  generated probes across all four buckets.
- Declaration ORDER is NOT the rule. Refuted on the shipped table with no edit:
  the tail-less `\N` is declared first, so first-match hands it `\N{U+0041}`
  (16 of 17 boundary probes wrong); pin the fallback last and `"{"` still
  precedes `"{U+"` (7 of 17). Blast radius decides it — 4 of 96 adjacent swaps
  are load-bearing, but 520 of 2,308 arbitrary swaps, because moving an
  unrelated row across a bucket's span corrupts that bucket as a side effect of
  where it lands. Rank travels with the row; order is a property of the file.

### 2.3 Selection is POSITION-INDEPENDENT

**The same row must be selected regardless of syntactic position.** Position
selects which *port* is consulted (§4), never which *row* wins.

Measured on the `\N` bucket, the only prefix-related tail pair in the table:

    [\N]        err 171   bare row wins,  class port NULL     -> refuse
    [\N{name}]  err 137   {name} row wins, class port present -> same answer as outside a class
    [\N{U+41}]  err 193   {U+}   row wins, class port present -> same answer as outside a class

So it is **not** "filter to rows that have a class port, then rank". It is
**arbitrate exactly as today, then consult the winner's port**; a NULL port is
a refusal, never a reason to select a different row. The other reading silently
re-ranks the bucket at class position and would make `[\N]` answer
`\N{name}`'s error.

This makes a new invariant checkable: *for every row, the row selected at class
position equals the row selected at atom position.*

> ### REFUTED (R13 — C1/F1, C3/F5+F9, C4/F19, C5/F2 — four critics independently)
>
> **Selection is NOT position-independent.** Verified by the author against
> libpcre2 10.46:
>
>     (a)x12 \12     matches "a"x12 + "a"     -> BACKREFERENCE 12
>     (a)x12 [\12]   matches "a"x12 + "\n"    -> STILL OCTAL 012
>
> Same capture count, same bytes, two different constructs — so the row that
> should win differs by position. C3 widened it: **114 of 168 (digit-run,
> capture-count) cells select a different row at class position, and the split
> starts at k = 0.**
>
> The §2.3 evidence above cannot decide this, and that is the methodological
> point worth keeping: all three `\N` probes are REFUSALS at class position, so
> "same row, then the port refuses" and "a different row wins" are
> indistinguishable on that data. `[\12]` is the first case where the two
> readings give different VERDICTS. **The measurement was taken on the only
> bucket that could not answer the question.**
>
> **Consequence: RECOGNITION is per-port, not just production.** Each port has
> its own recogniser; the `backrefs` row's class-side recogniser must decline so
> the octal row can claim. A row with no class PRODUCER still recognises and
> then refuses — which is how `[\N]` keeps its 171.
>
> **[OPEN] The replacement is stated, not designed.** Per-port recognition
> reopens everything §2.3 was holding shut: whether `rank` is per-port, what
> §8 check 3 pins instead, and whether two ports of one row can now disagree
> about whether a construct is present at all. Not resolved here.

---

## 3. Names

**Every row carries a NAME.** Rows sharing a name form a feature — the unit in
which pcrec talks about, tests, and enables functionality.

**This already exists and is half-built.** `internal.h:219-234` defines
`FEAT_*` as a **bitmask** (16 features, bits 0-15 of a 32-bit `unsigned`),
`RegRow` carries `unsigned feature`, and `registry.c:129-144` pairs each with a
string:

    #define M_recursion  FEAT_RECURSION, "recursion"

So the "logical grouping of rows" this design needs is present in the table
today; what does not exist is anything that *uses* it beyond printing a module
name in a diagnostic.

**A name is genuinely orthogonal to a bucket, and that is measured, not
asserted.** Counting the shipped table through `build/pcrec --list-syntax`
(100 rows, 16 features, 6 rows carrying no feature — five `rejected` and `(?:`,
which is `base`):

    classes    11 esc  +  1 group  +  1 class-bracket   = 3 buckets
    backrefs   12 esc  +  1 group                       = 2 buckets
    recursion  24 group                                 = 1 bucket
    the other 13 features                               = 1 bucket each

Two of sixteen span buckets today. That is a modest number and it is the whole
justification for names being their own axis: a grouping that could be
expressed as "a contiguous run of one bucket" would not need to exist. It also
sets the honest expectation — most features are bucket-local, and the mechanism
should not be designed as though cross-bucket were the common case.

### 3.1 A name is the unit of ENABLE/DISABLE

A compile carries an **enabled set** — a mask of feature names. A row whose
name is not in the set does not produce; it diagnoses.

This is not a new behaviour. It is the *existing* behaviour, generalised: today
every extension is permanently disabled, and the diagnostic is "requires module
'X'". This design makes the enabled set data instead of the absence of code.

**What that buys, in rough order of value:**

1. **Sabotage becomes a first-class instrument.** This project's recurring
   failure is a check whose sabotage is not live — recorded in K3 (a branch no
   test could see), K4 (a rule whose deletion changed no verdict), R11/C4-1 (a
   check whose pass condition held before the feature existed). With named
   features, every feature has a built-in sabotage: turn it off, assert the
   construct is refused; turn it on, assert it compiles. The instrument ships
   with the mechanism rather than being bolted on afterwards.
2. **The bound compile mode (D30 §4) becomes writable.** See §7.
3. **The migration is data.** As each module lands, one name flips. The
   refactor that introduces the mechanism can be byte-identical (§9).
4. **`--explain` and `--list-syntax` get a grouping** that is the same object
   the dispatcher uses, rather than a second description of it.

### 3.2 One name per row

`feature` is a MASK, so a row *can* carry several. It should not. The compound
module name was deliberately removed — `registry.c:146-155`:

> **THERE IS NO COMPOUND MODULE MACRO ANY MORE.** `M_lookaround_named`
> ("lookaround/named-groups") lived here for `(?<`, one byte meaning two
> constructs, and SR-9's `tail` retired it: a compound name is a true sentence
> and an inexact answer, and D26 puts module attribution in tier 2, where the
> standard is exact.

**The type therefore permits exactly what the decision forbids.** This design
requires: *every row's `feature` has exactly one bit set, or is zero for base
and rejected rows* — and says so as a check, because a mask that is allowed to
hold two bits is an open invitation to reintroduce the compound the moment
somebody meets a byte with two meanings.

Measured on the shipped table: **every one of the 100 rows carries exactly one
bit or zero**, and all 16 bits are in use. So the check passes today and its
sabotage is live — OR two `M_*` macros together and it fails. This is the
cheapest check in §8 and it guards a decision that was already made and then
left unenforced.

### 3.3 Scope of a toggle

- **Base grammar is not toggleable.** It is not in the table and carries
  `feature == 0`. Turning off literals is not a feature request.
- **Toggles are internal and test-facing**, exposed through the CLI
  (`--without=NAME` or similar) so the sabotage instrument is reachable. They
  are **not** in the public API. Adding them there is a public-contract change
  and belongs with DD-3 and K9, which are already bundled for that reason.
- **[OPEN] Dependencies between names.** `unicode-props` produces class sets;
  `classes` consumes the same machinery. Is `--without=classes` with
  `unicode-props` enabled a coherent state, an error, or a silent implication?
  Nothing measured. The safe default is to make it an internal error at
  startup rather than discover it at parse time, but the dependency graph has
  not been derived.
- **[OPEN] Header room.** 16 of 32 bits are used. §7 adds at least one more
  category and finer names would add more. A `uint64_t`, or an index rather
  than a mask, may be wanted before this is built. Deferred deliberately: it
  is a mechanical change and choosing now is speculative.

---

## 4. Two ports per row

A row carries up to **two handler functions**, one per syntactic position:

    class port   parses the construct INSIDE `[...]`   -> a set, or a scalar
    AST   port   parses it OUTSIDE a class             -> an Ast *

Position selects the port. There is no `in_class` parameter.

### 4.1 A NULL class port means exactly one thing — and `\b` is what makes that true

Measured:

    [\A] [\Z] [\K] [\R] [\X]  err 107  escape sequence is invalid in character class
    [\N]                      err 171  \N is not supported in a class
    [\b]                      COMPILES — backspace 0x08

Today two different mechanisms both amount to "the class doorway is not taken",
for **opposite reasons**: `ESC_CLASS_BASE` (exactly one row, `\b`,
`registry.c:261`) because the base grammar answers first at `parse.c:152`, and
`ESC_CLASS_INVALID` (10 rows) because PCRE2 forbids the construct permanently.
A NULL port cannot say both.

**Resolution: `\b`'s class port returns the scalar `0x08`.** A NULL class port
then means exactly one thing — *no module, permanently invalid here* — and this
deletes `parse.c:152`'s special case, `RF_CLASS_BASE` and `RF_CLASS_INVALID`
together.

**K10 becomes structurally unrepresentable.** K10 is a row whose flag says
"permanently invalid in a class" while its own `note` says the opposite; the
check that would have caught it exempts `RF_CLASS_INVALID` rows by design
(`registry_check.c:875`), so *the flag exempted the row from the only check
that contradicted it*. With no flag, the presence of the function is the
answer, and it is the same object the dispatcher uses — there is nothing left
to disagree with.

`\N`'s wording differing from the other nine (171 vs 107) is tier 3 under D26
and is deliberately not modelled.

> ### REFUTED (R13 — C5/F4, C3/F6) — a NULL class port has at least THREE meanings
>
> Verified by the author against libpcre2 10.46:
>
>     [\A] [\Z] [\K] [\R] [\X]   err 107   permanently invalid in a class
>     [\N]                        err 171   permanently invalid, own wording
>     [\b]                        COMPILES  base grammar: backspace 0x08
>     [\k] [\g]                   COMPILES  THE LITERAL LETTER — matches "k","g"
>     [0-\k]                      COMPILES  a legal range, 0x30..0x6b
>
> `\g` and `\k` inside a class are neither a construct nor an error: libpcre2
> falls back to **the literal letter**. So "no class producer" means at least
> three things — *permanently invalid*, *base grammar*, and *falls back to a
> literal* — and §4.1 collapses them into one silence.
>
> §4.1's claim that this makes K10 "structurally unrepresentable" is therefore
> too strong: it removes one flag whose absence then asserts a tier-2 fact by
> SILENCE, which is the same defect wearing different clothes.
>
> **CORRECTED, and the author found this half independently before the panel:**
> **the feature name is a property of the PORT, not of the row.** `\b`'s AST port
> is `assertions`; its class port is base and is never gated. Without that,
> §5.4's gate demotes `[\b]` to TERMINAL and answers *"requires module
> 'assertions'"* for a pattern pcrec compiles correctly today.
>
> **C5 found the worse half, which the author had not seen:** §4.2's shared
> generic wrapper, applied to `\b` as written, gives `\b`'s AST port =
> wrap(0x08), so `a\bb` compiles to a matcher for `a\x08b` — **a tier-1
> miscompile**, invisible to the byte-identity run because `a\bb` is refused
> today. Every check in §8 passes on it, and check 8 *certifies* it.
>
> **[OPEN] What a missing producer asserts.** Per-port features fix `\b`. The
> literal-fallback case (`\k`, `\g`) has no home in this vocabulary at all.

### 4.2 The AST port of a class-shaped construct is a SHARED GENERIC WRAPPER

Not one function per construct per position, and for most rows not a function
at all.

`char_node` (`parse.c:76-82`) already normalises a literal to a **singleton
`A_CLASS` node**; `internal.h:42` records that literals ARE singleton classes;
and codegen emits membership tests from `cls[32]`. So "the code to check
whether the input belongs" is not something an AST-port function writes — it is
what the backend already does with a bitmap.

Therefore:

- the AST port of every class-shaped row is **one shared wrapper** that calls
  the class port and wraps the result in an `A_CLASS` node;
- for the ten character-type escapes (`\d \D \w \W \s \S \h \H \v \V`) the
  class port is **data** — a bitmap plus a negate flag — read by one shared
  handler.

Not two functions per class. Not even one function per class.

### 4.3 The two ports have DIFFERENT interfaces

They are not one signature with a mode flag. The class port needs position
context the AST port has no use for, and forcing a union of both into one
signature is how D29's `head_len` hand-off came to be wrong before anything was
built.

    ExtWhat class_port(Ctx *cx, const ClassReq *req, ClassResult *out);
    ExtWhat ast_port  (Ctx *cx, const AstReq   *req, Ast **out);

    ClassReq  { ExtAsk ask; bool at_class_open, at_content_start;
                size_t at; const RegRow *row; }
    AstReq    { ExtAsk ask; size_t at; const RegRow *row; }

`at_class_open` distinguishes `[.a.]` (an error at offset 0) from `[[.a.]]`;
`at_content_start` is R9/C3-4's `[[:<:]]` rule. Both are class-only facts and
neither belongs in the AST port's signature.

**There is deliberately no `at_range_endpoint`.** It was in the first draft of
this document and removed: under §6 the endpoint caller decides the verdict
itself from the claim and the row's shape, so no handler needs to know it is
being asked at an endpoint. A field with no consumer is the defect D32 §1 cited
against `span_at`/`span_len` and that D24/SR-2 records as this project's larger
loss — *"lost more to unexercised structure than to missing structure"*. If a
construct is ever found whose RECOGNITION differs at an endpoint, this is where
it goes back.

### 4.4 Outcomes

    EXT_NOT_MINE   the row's recogniser declines
    EXT_SCALAR     a code point — THE ONLY SHAPE LEGAL AS A RANGE ENDPOINT
    EXT_MEMBERS    an A_CLASS node whose cls[] the caller ORs into its own
    EXT_NODE       a subtree the caller splices in
    EXT_TERMINATED the construct is real and this compile will not proceed

The three producing shapes are not arbitrary: they are the three things the
surrounding grammar can splice. `EXT_SCALAR` and `EXT_MEMBERS` collapse at atom
position (both wrap to `A_CLASS`), which is why §4.2's wrapper is generic.

**The SHAPE column describes what the CLASS port produces, and only that.** A
row with no class port has no shape, because the only consumer of shape is the
range-endpoint rule (§6) and a group or verb construct can never appear at a
class range endpoint. Stating it the other way round — "every row declares a
shape" — invents a value for 60-odd rows that nothing reads, and the first
person to read one of those values will be reading a guess.

> ### REFUTED (R13 — C1/F3, C3/F2+F3, C2/F5, C5/F3)
>
> **(a) The five outcomes are incomplete.** `\Q...\E` and `\E` and `(?#...)` are
> none of them. Verified by the author:
>
>     [0-\Q\Ea]   COMPILES   the quote is TRANSPARENT; the endpoint is `a`
>     [0-\E]      COMPILES   \E contributes nothing; `-` reverts to a literal
>     [0-\Qz\E]   COMPILES   the endpoint is the FIRST quoted byte
>     [0-\Q-\E9]  err 108    confirms the endpoint was `-`
>
> A quoted run contributes one endpoint AND further members — a byte run that
> re-enters the enclosing class loop. §4.4's supporting sentence ("the three
> things the surrounding grammar can splice") asked whether the three fit the
> grammar and never asked whether every construct fits the three.
>
> **(b) The natural `EXT_NODE` reading of a quoted run is a TIER-1 MISCOMPILE.**
> Verified by the author:
>
>     ^\Qab\E*$  vs "abbb"    MATCHES
>     ^\Qab\E*$  vs "ababab"  does NOT match
>     ^a\Q\E*$   vs "aaa"     MATCHES
>     ^\Q\E*$                 err 109
>
> A quantifier binds the LAST character of a quoted run, not the run. If the
> `\Q` row's AST port returns a node and `try_quant` quantifies it, `\Qab\E*`
> compiles to `(ab)*`. §5.6 — which requires a producing claim to be RETURNED to
> a caller whose next act is `try_quant` — is what makes this reachable.
>
> **(c) "`EXT_SCALAR` is THE ONLY SHAPE LEGAL AS A RANGE ENDPOINT" is FALSE**, by
> the same measurements.
>
> **(d) Rows with no class port ARE reachable at an endpoint** — ten escape rows
> are (`[0-\A]` is 107), so §4.4's "a group or verb construct can never appear at
> a class range endpoint" enumerates two buckets and stops. The rule is not total
> over its own input domain, and §4.4's own sentence applies to §6's caller:
> *the first person to read one of those values will be reading a guess.*
>
> **[OPEN] A sixth outcome is needed** — transparent/lexical-mode: consumed
> input, contributed nothing, is not a quantifier target, does not terminate a
> range. Its interaction with §6 (a third endpoint answer, "the endpoint is not
> here, keep looking") is not designed.

---

## 5. The seam: RECOGNISE, then PRODUCE

This is the centre of the design. Everything else hangs off it.

Every handler has two phases:

    RECOGNISE   is this construct here, and what SHAPE is it?
                   — pure: no allocation, no diagnostic, no cursor commitment
    PRODUCE     parse the body and build the result
                   — may allocate, may diagnose, may recurse into the parser

### 5.1 What "pure" means here, precisely

**Purity constrains EFFECTS, not INPUTS.** A recogniser may read anything the
parser has already established — the pattern text, the cursor, the current
option state, the running capture count. What it may not do is allocate,
diagnose, or move the cursor.

This is not a technicality; it decides a case the design would otherwise get
wrong. `\12` is octal or a backreference **according to how many capture groups
the parser has seen so far** — measured: `\12` alone COMPILES as octal 012,
`(a)\12` COMPILES as octal, and with twelve preceding groups it is
backreference 12. Under "purity = reads nothing", the two rows would both have
to claim `\12` and be separated by `rank`, which cannot work: rank is static
and that answer is dynamic. Under "purity = no effects", each recogniser
consults the count and **exactly one claims**, so the clash never reaches
arbitration and rank is not involved at all.

The same reading is what D32 §5 relied on when it dropped D30 §6's digit
exception, and it is consistent with R12/P1's measurement, which instrumented
ALLOCATION and not reads.

### 5.2 Three ASK levels

**A caller may ask for less than the whole thing**, through the `ask` field.
There are THREE levels, nested — each does everything the one above it does:

    EXT_ASK_SHAPE      recognise only. Return the claim and its shape. Do not
                       inspect the body, diagnose, allocate, or move the cursor.
    EXT_ASK_TERMINAL   recognise, and inspect the body far enough to choose the
                       RIGHT terminal answer. May diagnose. Must not produce.
    EXT_ASK_FULL       recognise and produce.

**The middle level is not optional, and leaving it out is a bug this document
had for its first draft.** The obvious design — "when a feature is disabled,
confirm the claim with SHAPE and emit the row's static message" — is wrong,
because a single row's terminal answer is not static. Measured, `build/pcrec`
at `5173a82`, all from the ONE class `:` row:

    [[:alpha:]]        POSIX class [:...:] requires module 'classes'
    [:alpha:]          POSIX class [:...:] is only valid inside a character class
    [[:foo:]]          unknown POSIX class name
    [x[:<:]]           unknown POSIX class name        <- valid ONLY at content start
    [[:<:]]            POSIX class [:...:] requires module 'classes'

Four terminal SHAPES and three distinct messages, chosen by reading the NAME
and the POSITION. (D32 §6 called these four shapes; three of them share two
messages, and `[x[:<:]]` reuses the bad-name text rather than having a wording
of its own.) The verb row is the same story with D25's four `(*` answers:
`(*FAIL)` names a module, `(*NOSUCH)` and `(*LIMIT_X=3)` are
"(*VERB) not recognized or malformed", and `(*)` is not a verb at all.

Emitting "requires module 'classes'" for `[[:foo:]]` is precisely the
over-promise FIX-2 removed. A design that reaches the terminal answer without
reading the body reintroduces it for three of that row's four shapes.

> ### REFUTED (R13 — C1/F2, C1/F6) — TERMINAL is incoherent at `(?(`
>
> `(?(` has one registry row. Its correct terminal answer is at least six
> different things, two of which PCRE2 will NEVER accept:
>
>     (a)(?(1)x|y)     ok            (a)(?(1)x|y|z)   E127 more than two branches
>     (?(DEFINE)a|b|c) E154          (a)(?(1)x|y|z    E114 termination beats 127
>     (?(1)x|y)        E115          (a)(?()x|y)      E162
>
> E127 and E154 are permanent — module `conditionals` will implement
> `(?(1)x|y)` and can never implement `(?(1)x|y|z)`. So by §5.2's own standard
> that is the FIX-2 over-promise, and TERMINAL owes the fix.
>
> **TERMINAL cannot pay it.** Deciding E127 means counting TOP-LEVEL `|`, and
> C1 measured that this is not a bounded prefix scan and not a lexical count:
> `|` is hidden by `\Q...\E`, by a class, by a comment and by an escape, and
> group nesting is unbounded. That scan IS the parser. The three ways out are
> to call `pcrec_parse_body` (which allocates and recurses — PRODUCE by §5's own
> definition), to write a second non-allocating branch scanner (the duplicate
> §10.6 condemns), or to over-promise (refuted by §5.2 itself).
>
> **The defence measured the easy case and generalised to the hard one.** §5.3's
> instrumented-arena evidence is about the class `:` row, whose body inspection
> is a bounded delimiter scan plus a 16-name lookup. `(?(`'s is a parse.
>
> **C1/F6 adds a case no ASK level covers at all:** the right terminal answer
> sometimes depends on the text AFTER the construct, which is neither head nor
> body.
>
> **[OPEN]** Either TERMINAL may allocate — i.e. the real rule is "must not
> COMMIT the cursor / must not return a producing outcome" rather than "must not
> produce" — or the document must name the exempt rows and accept the
> over-promise for them in writing. Not decided.

This is NOT the two-port decide/build split D32 §1 dropped. That split was two
*functions* with a hand-off contract (`head_len`, `span_at`/`span_len`) that
was already wrong before anything was built — `head_len` assumed every
recogniser's `at` sits after the selector byte, and `RF_OPTION_RUN` rows start
AT it — and whose "the semantic port begins where the head ended, ASSERTED"
named no mechanism (`src/` contains zero `assert()` calls). Here there is one
function and no hand-off: it answers its own question and returns.

It is also NOT the TRIAL MODE refuted in D32 §8 by building it. Trial mode was
*implicit* — a `Ctx` copy plus a flag tripping `arena_alloc`/`ctx_fail` — so
any construct with a body tripped it, aborting every CORRECT implementation,
and it leaked ~76-80 bytes per byte scanned (76.4 MB at N = 1,000,000). Here
the instruction is *explicit* and the handler is written to honour it.

### 5.3 Most rows do not write a handler at all

Three ask levels across 100 rows would be an unreasonable contract if every row
implemented them. It does not: **a shared default handler implements all three
levels out of the row's own data** — `sel` plus `tail` for recognition, the
row's shape column, and `RD_MODULE`/`RD_FIXED`/`open_msg` for the terminal
answer. That is exactly what `ext.c` does today for the rows that have no body.

Only rows with a BODY override it, and D28 counted them: **ten construct
families need body parsing** — verb names, the `LIMIT_*` magnitude rule, the
class-bracket delimiter scan (all three already in `ext.c`), plus `\p{...}`'s
loose normalisation, `(?[...])`'s nested set algebra, the named-group forms,
and the rest. So the per-handler contract is owed by roughly ten handlers, not
a hundred, and for the other ninety the levels are a property of the shared
code rather than something a row author can get wrong.

> ### CORRECTED (R13 — C1/F4) — "ten" is a count of FAMILIES reported as a count of HANDLERS
>
> D28's ten is ten construct FAMILIES. Measured against the real table it is
> **at least 22 handlers, and structurally at least 12 in the `(?` bucket
> alone**. The reassurance in this section is therefore roughly half the size it
> claims, and it was obtained by quoting a number that counts something else —
> the same error as `17 tailed rows` (which was 18, and the missed row was the
> one the argument was about).

**That the contract is per-handler and unenforced is the price**, and it is
paid with a mechanical check: R12/P1's instrumented arena over the real
`pcrec_compile` measured a declining delimiter scan allocating **18 calls / 318
bytes identically at N = 1,000 / 100,000 / 2,000,000** — zero growth with scan
length. The same instrument asserts, for every row, that `EXT_ASK_SHAPE`
allocates nothing and diagnoses nothing.

### 5.4 THE GATE SITS AT THE SEAM

A disabled feature stops at exactly the point `EXT_ASK_SHAPE` stops at:

    arbitrate the bucket  ->  row
      ask == SHAPE                  -> call the port with SHAPE, whatever is enabled
      ask == FULL, name ENABLED     -> call the port with FULL
      ask == FULL, name DISABLED    -> call the port with TERMINAL

The gate DEMOTES the request by one level. It does not replace the handler with
a canned message, and it does not skip the handler: the handler is the only
thing that knows whether this instance is `[[:alpha:]]` or `[[:foo:]]`.

**Recognition never depends on what is enabled.** This is the load-bearing
invariant of the whole design, and it is tier 2 under D26: whether a construct
is REAL is a fact about PCRE2, not about how much of pcrec is finished. If
disabling `classes` made `[0-[:digit:]]` stop being an invalid range, pcrec
would be answering a question about itself and calling it a question about
PCRE2.

It is also what makes the disabled path *be* the shape path plus the row's
existing diagnostic vocabulary — which is why today's entire behaviour is one
branch of the mechanism rather than a thing the mechanism has to reproduce.

> ### CORRECTED (R13 — C2/F2, C2/F3, C4/F3) — the invariant holds VACUOUSLY
>
> **It is true for all 16 features, and not because it was engineered.** pcrec
> is single-pass and `EXT_TERMINATED` leaves by longjmp, so a disabled
> state-setting feature stops the compile AT the setter and no later construct
> is ever recognised:
>
>     (?x)[a- ]   -> (?x...) requires module 'modifiers'   (stops here)
>     [a- ](?x)   -> range out of order in character class
>
> C2 measured which features could otherwise break it — 87,164 generated probes
> as prefixes, 8,716,400 compile pairs, with a control-choice error caught and
> corrected mid-flight (`(?:)` conflates quantifiability; `(?i)` does not).
> Exactly three are real state-setters: `modifiers` (via `(?x)`/`(?n)` only —
> the other eleven modifier rows are provably inert), `quoting` (via `\Q`, not
> `\E`), and the capture-count movers.
>
> **An invariant whose enforcement mechanism is undocumented is one refactor
> away from being lost**, and §10.6's pre-scan is that refactor. This section
> must say that the invariant rests on single-pass termination.
>
> **The cross-construct case is real and check 6 cannot reach it:**
>
>     (a)x12\12       -> \12 is BACKREFERENCE 12
>     (?n)(a)x12\12   -> \12 is OCTAL 012
>
> `(?n)` is a `modifiers` row that changes which CONSTRUCT `\12` is. So a
> `backrefs` recogniser reads state produced by a `modifiers` producer: §5.1
> presents the capture count as parser state, and it is **a feature's output**.
>
> **A result in the design's favour, recorded as such:** §3.3's worry pair
> (`unicode-props` / `classes`) measures at **exactly zero** — `\p{L}`, `\d`,
> `[[:alpha:]]` change no downstream verdict. §3.3 and §10.3 were asking about
> the wrong pair.

### 5.5 The terminal answer is the ROW'S EXISTING VOCABULARY

A uniform three-outcome protocol (NOT_MINE / PARSED / UNIMPLEMENTED→render the
module name) was proposed and refuted (R12/P3). It holds at one doorway of
four:

- **it resurrects a bug FIX-2 removed.** The class `:` row has four live
  terminal shapes, measured in §5.2 above. Rendering "requires module
  'classes'" mechanically is the exact over-promise FIX-2 removed, for three of
  those four;
- module-shaped outcomes are a minority even at the escape doorway — ~18 of 41
  rows;
- `NOT_MINE` is structurally unreachable at VERB (one row, one unconditional
  call site, nothing to hand back to), and `(*)` fits none of the three.

So `EXT_TERMINATED`'s message comes from the row's existing `RD_MODULE` /
`RD_FIXED` / `open_msg` fields and D25's four `(*` answers.

### 5.6 A PRODUCING claim is RETURNED

`EXT_TERMINATED` may still leave by `ctx_fail`'s longjmp — no change to the 23
`ctx_fail` sites in `ext.c`. But a claim that **produces** must return its
result to the caller.

This is not stylistic. Today every doorway is `noreturn` except
`pcrec_ext_class_bracket`, and the moment one returns:

- `pcrec_ext_escape`'s two call sites (`parse.c:139`, `:154`) are **undefined
  behaviour** — both invoke it as the last statement of a value-returning
  function with no `return` in front, legal only because `noreturn` makes
  falling off the end unreachable. Reproduced (K11): with the declaration
  changed and one sentinel selector byte returning a stub, `a\qb` compiles and
  launders the discarded pointer out of `%rax` (5/5 runs), while `[a\qb]`
  **SIGSEGVs `build/pcrec` itself** (3/3 runs). gcc emits `-Wreturn-type` at
  both sites and the build still exits 0, because `-Werror` is not the default.
- `pcrec_ext_group`'s returned node is **silently discarded** and control falls
  through into the body parse: `(?%x)b)` compiles to byte-identical C to the
  bare pattern `b` — the module's node AND the pattern's own unmatched trailing
  `)` both vanish (`parse.c:253-262`).

One returning contract, one epilogue. The two doorway epilogues that "do not
exist as code" (GROUP, VERB) cannot be missing when there is one.

---

## 6. The range-endpoint rule falls out of the seam

PCRE2 refuses a range whose endpoint is a set-valued construct. This is the
rule SPEC-FA implemented for the bracket shape — where pcrec had been reading
`[` as an ordinary literal upper bound and **emitting a matcher**, a tier-1
miscompile, 546 instances in a 1,530-pattern sweep.

**The naive implementation is wrong**, and knowing why is what makes the rule
correct. At an endpoint, PCRE2's "invalid range" **beats the construct's own
diagnostic**:

    [0-[:foo:]]  err 150 invalid range    vs   [[:foo:]]  err 130 unknown POSIX class name
    [0-[.ab.]]   err 150 invalid range    vs   [[.ab.]]   err 113 collating not supported
    [0-[=x=]]    err 150 invalid range    vs   [[=x=]]    err 113
    [0-[:<:]]    err 150 invalid range

So a caller cannot simply parse the endpoint and complain if the result is
set-shaped: parsing `[:foo:]` raises 130 long before anyone can say 150. That
observation is what motivated `pcrec_ext_class_pair_opens`, a bespoke pure
predicate for one doorway (`ext.c:354`).

**`EXT_ASK_SHAPE` generalises it correctly, and the predicate is deleted.** The
endpoint asks two questions: *did anything claim* (call the port with SHAPE)
and *is the row's shape set-valued* (a static column). Verified against every
case measured:

    [0-[:digit:]]                    claims, SET        -> 150      PCRE2 150
    [0-[:foo:]]                      claims, SET        -> 150      PCRE2 150
    [0-[.ab.]] [0-[=x=]] [0-[:<:]]   claims, SET        -> 150      PCRE2 150
    [0-[a] [0-[:] [0-[:digit] [0-[.] declines           -> literal  PCRE2 COMPILES
    [0-\d] [0-\p{L}]                 claims, SET        -> 150      PCRE2 150
    [0-\N{U+41}]                     claims, SCALAR     -> its 193  PCRE2 193
    [0-\q]                           no row, no claim   -> its 103  PCRE2 103
    [\x41-z]                         claims, SCALAR     -> a range   PCRE2 COMPILES
    [a-\x41] [a-\n]                  claims, SCALAR     -> err 108   PCRE2 108

The shape must be a **static column**, not a parse outcome: `[:foo:]` is
set-shaped-but-invalid and still yields 150, while `\N{U+41}` is scalar-shaped
and its own mode error stands.

> ### REFUTED (R13 — C3/F1, C3/F4, C3/F7) — the DOORWAY decides, not the shape
>
> The contrast this paragraph rests on varies TWO things at once — shape and
> doorway — and credits the wrong one. Hold shape fixed at SET and vary only the
> doorway (verified by the author):
>
>     [0-[:foo:]]   150  invalid range        SET, class-bracket doorway
>     [0-\p{Foo}]   147  unknown property     SET, escape doorway
>     [0-\p]        146  malformed \P or \p   SET, escape doorway
>     [0-\p{L}]     150                       SET, escape doorway, VALID body
>
> §6's rule predicts 150 for all four; libpcre2 says 150 for two. **The real
> rule:** at the ESCAPE doorway the escape is decoded IN FULL first and any
> decoding error wins; only a successfully decoded, class-valued escape gives
> 150. At the CLASS-BRACKET doorway only the syntactic pair is recognised and
> the name is never validated, so 150 beats 130. The column called SHAPE was
> doing the work of *which doorway is this, and did the body parse*.
>
> **The rule also covers only the HIGH endpoint** — `parse.c:209-211` runs only
> after the `-`. libpcre2 rejects on either side, and **the two sides are not
> symmetric**, which kills any "apply the same rule twice" repair:
>
>     [\d-z]      150     [\p{L}-z]  150     [[:alpha:]-z]  150
>     [0-[.ab.]]  150  <- HIGH: position beats the construct
>     [[.a.]-z]   113  <- LOW:  the construct's error wins
>
> This is SPEC-FA repeating one position to the left: §6 widened the narrow fix
> to all doorways and stopped at the same edge. **"Fixing the narrowest instance
> and calling it the class" applies to §6 itself.**
>
> **The endpoint is not even a fixed text position** — `\E`, `\Q\E` and `(?xx)`
> move it, and one of them dissolves the range entirely.
>
> **NEGATIVE RESULT, recorded because it bounds the damage:** at the
> class-bracket doorway alone the rule is EXACTLY right — 21,396 generated
> patterns, zero disagreements (C3/F8). The defect is the generalisation to the
> escape doorway, not the original SPEC-FA rule.
>
> **[OPEN]** The corrected rule is per-doorway and per-side, and is not designed
> here.

Two consequences worth stating:

- **The endpoint verdict is independent of what is enabled**, because the shape
  is data. `[0-\d]` is an invalid range whether or not `classes` is on — which
  is what PCRE2 does.
- **This closes K12.** `[0-\d]` is answered today with "requires module
  'classes'" where PCRE2 says the range is permanently invalid. pcrec is
  correct today only because `\d` is refused before `parse.c:213`'s range code
  (`int hi = esc_class_value(cx)`, then `lo > hi`, then
  `for (i = lo; i <= hi; i++)`) can see it. **The guard is the
  unimplemented-ness, and MOD-0.2 removes it** — the same shape `plan.md:577`
  already records for `(?xx)[a- ]`, one construct over.

---

## 7. The bound compile mode is a set of names

D30 §4 decided that pcrec writes down the option semantics it compiles for, and
quantifies its verdicts over that: `\U` is REFUSE **because pcrec will not
offer `PCRE2_ALT_BSUX`**, which is a decision pcrec can defend, rather than a
false claim about PCRE2. **The decision was taken; the LIST was never written.**

Under §3 the list is a set of names, and writing it exposes a distinction the
current table cannot express. Measured:

    \U      opt=0         err 137      \U      opt=ALT_BSUX   COMPILES
    \u0041  opt=0         err 137      \u0041  opt=ALT_BSUX   COMPILES
    \u{41}  opt=0         err 137      \u{41}  opt=ALT_BSUX   COMPILES
    [\U]    opt=0         err 137      [\U]    opt=ALT_BSUX   COMPILES
    \F \L \l \N{name}     err 137      ... under ALT_BSUX     STILL err 137

PCRE2 emits **one message for six constructs**, of which only two are
mode-dependent. So there are two categories behind one string:

- **`\U`, `\u`** — real constructs, legal in a mode pcrec declines to offer.
- **`\F`, `\L`, `\l`, `\N{name}`** — not legal in any PCRE2 mode.

### 7.1 This is the same hole as three other open issues

Measured against `build/pcrec` at `5173a82`:

    \U   ->  pcrec: unknown escape \U (pattern offset 0)
    \F   ->  pcrec: unknown escape \F
    \L   ->  pcrec: unknown escape \L
    \l   ->  pcrec: unknown escape \l
    \N{name} -> pcrec: PCRE2 does not support \F, \L, \l, \N{name}, \U, or \u

**`\U`, `\u`, `\F`, `\L`, `\l` have no registry row at all.** They fall through
to `ext.c:84-85`'s generic `"unknown escape \%c"`. That single fall-through is
simultaneously:

- **the project's only completely unguarded diagnostic surface** — nothing in
  the repo would notice its wording changing (R11 disposition 14);
- **D32 §9.4's missing fourth residue category** — 46 of the 93 reachability
  counterexamples (49%) come from neither a registry row nor D25, and they are
  exactly these escapes plus unknown POSIX names;
- **the reason D30 §4's list could not be written** — there was nowhere to put
  "real construct, mode not offered".

All three close by giving these constructs **rows**, with a status that says
which of the two categories they are in.

### 7.2 The status vocabulary

    RS_BASE        the base grammar implements it; no row needed
    RS_MODULE      real; a named feature owns it; enabled or not
    RS_REJECTED    real in no PCRE2 mode — agreement IS compliance
    RS_NOT_OFFERED (new) real under a PCRE2 option pcrec does not implement

`RS_NOT_OFFERED` carries the option that would make it legal, so the diagnostic
can say what it depends on and D26's upgrade rule has something to bite on: a
future PCRE2 option does not retroactively make pcrec's diagnostics lies,
because they were never quantified over every possible PCRE2 mode.

**[OPEN] Is `RS_NOT_OFFERED` a status or a name?** It could equally be a
feature name that is permanently disabled (`alt-bsux`), which would make "the
bound compile mode" literally the set of names not enabled, with no new status.
That is more uniform and it is one fewer concept — but it makes "we will never
implement this" and "we have not implemented this yet" the same state, and D26
tier 2 distinguishes them. Not decided.

**[OPEN] What is the full bound-mode list?** Only `ALT_BSUX` and
`EXTRA_BAD_ESCAPE_IS_LITERAL` have been measured as verdict-changing. R10
measured that `UTF`, `UCP`, `CASELESS`, `MULTILINE`, `DOTALL`, `UNGREEDY`,
`AUTO_CALLOUT` and every `EXTRA_ASCII_*` flip NO construct verdict. The
remaining options have not been swept. Writing the list needs that sweep.

> ### CORRECTED (R13 — C2/F4) — there are THREE categories, and the [OPEN] is not neutral
>
> C2 established the ALT_BSUX bit behaviourally rather than looking it up —
> swept all 32 single-bit compile options, exactly two make `\u0041` compile,
> and the other (`0x02000000`) also makes `a+` literal, so it is `PCRE2_LITERAL`
> and `0x2` is ALT_BSUX. Then, over **120,099 generated probes**, opt=0 vs
> opt=0x2 changed **274**, and they are three escapes, not two:
>
>     \u  \U   err 137 -> COMPILES     (the two this section has)
>     \x       err 178 -> COMPILES     <- NEW: base grammar, digits missing after \x
>
> **`\x` is a BASE-GRAMMAR escape pcrec already implements, and ALT_BSUX changes
> what it recognises.** So the mode-dependent set reaches into the base grammar,
> which §3.3 declares not toggleable, and there is a third category with no home
> in the `RS_*` vocabulary: *base construct whose meaning the mode changes*.
>
> **This decides §7.2's [OPEN] toward STATUS, not name.** If `alt-bsux` were a
> feature NAME in the enabled set, then by §5.4's own words recognition must not
> depend on it — and these 274 probes are exactly recognition depending on it.
> The uniformity argument costs the invariant §5.4 calls load-bearing, and that
> cost is not in the tradeoff as written.
>
> **NEGATIVE RESULT:** `PCRE2_UTF` (bit `0x80000`, also established
> behaviourally) changes **0 of 120,099** verdicts, independently reproducing
> R10 with a different generator.

---

## 8. Checks the mechanism makes possible

Each of these is stated with the sabotage that must break it, because a check
whose pass condition already held before the feature existed cannot detect the
feature (R11/C4-1: PARSE-1's own proposed primary check asserted something true
of the tree the day before, so "ship it by doing nothing" passed).

**But that rule has been applied too widely, and the distinction matters here.**
There are two kinds of check in this list and they answer to different
standards:

- a **feature detector** must FAIL before the thing it certifies is built. If
  it passes on the tree as it stands, it certifies nothing. R11/C4-1 is about
  these.
- an **invariant guard** is *supposed* to pass today. Its job is to fail when a
  future change breaks a property currently held by construction. Demanding it
  fail first is incoherent.

Below, checks 1, 5, 8 and 9 are feature detectors; 2, 3, 4, 6, 7 and 10 are
invariant guards. Check 3 is the clearest case: the same row is selected at
both positions **today, by construction**, because `esc_atom` and
`esc_class_value` call `pcrec_registry_find` with identical arguments. There is
no sabotage that makes it fail on the current tree, and that is not a weakness
— it is the point. Labelling every check a detector is how a guard gets
rejected for passing.

1. **Per-row `syntax`.** A row's own `syntax` string, fed through the REAL
   dispatch, must be claimed by THAT row. Total over 22 clashing rows,
   terminating, no generated space, no oracle. *Primary.* Sabotage: give bare
   `\N` a rank above `\N{U+` and `\N{U+0041}` is claimed by the wrong row.

   **`syntax` must therefore be a COMPLETE probe, not a fragment**, for any row
   whose recogniser reads parse state (§5.1). The ten digit rows are the live
   instance: their `syntax` is bare `\0`..`\9` today, so a backreference row
   probed with bare `\1` is probed in a state where no backreference can be
   valid. Splitting octal from backrefs (§10.7) makes those probes
   `(a)(b)...\12` and `\012`. **And it exposes a shipped tier-2 misattribution
   on the way past:** `\0` currently carries module `backrefs`, and `\0` can
   never be a backreference — there is no group 0.
2. **Equal-rank collision.** Two answering rows at equal rank is an internal
   error. Sabotage: set two clashing rows' ranks equal.
3. **Same row at both positions** (§2.3). Sabotage: make arbitration skip rows
   without a class port and `[\N]` answers `\N{name}`'s error.
4. **`sel` redundancy.** For every row with non-null `sel`, its recogniser
   returns exactly `EXT_NOT_MINE` for every input whose first byte differs.
   Worded that way deliberately: "does not return PARSED" passes vacuously
   while every row is a stub (R12/P4).
5. **`EXT_ASK_SHAPE` is pure**, by instrumented arena, per row: zero
   allocations, zero diagnostics, and no growth with scan length. Sabotage:
   have one handler parse its body under SHAPE.
6. **Recognition is enablement-independent** (§5.4) — the same construct is
   recognised, with the same shape, with its feature on and off. Sabotage: gate
   the recogniser instead of the producer, and `[0-[:digit:]]` stops being an
   invalid range when `classes` is off.
7. **Exactly one feature bit per row** (§3.2). Sabotage: OR two `M_*` macros.
8. **Every feature toggles**: for each name, a pattern that compiles with it on
   and is refused with it off. This is the built-in sabotage of §3.1, and it is
   the check that has no analogue today.
9. **The reachability differential** — pcrec must have an answer wherever
   libpcre2 recognises a construct, with residue in exactly one of the
   categories in §7.2. D30 §2's wording *"pcrec must promise a module wherever
   libpcre2 DISPATCHES"* is FALSE and is not adopted: 93 counterexamples in
   1,672 probes, all of them pcrec being correct, confirmed by three
   independent harnesses. Baseline to beat, measured: **2 of 4 buckets have any
   live external coverage, 0 of 4 have complete coverage of the malformed-body
   class, `\N` has none.** The classifier must name every doorway's
   no-construct code, including **103** at the escape doorway.
10. **`check_tail_precedence`'s liveness obligation** must have a committed
    successor before it is retired — R11/M3 located it, a "did any generated
    probe have more than one matching row" counter, baseline nonzero per bucket
    (111 / 333 / 333 / 2730).

### 8.0a REFUTED AND CORRECTED (R13 — C4, 26 findings; C5/F8, C5/F10)

C4 took the K10 template to all ten checks. The list above stands as written
only where it is not contradicted below.

- **Check 4 is vacuous for ~90 of 100 rows (CRITICAL).** §5.3 says most rows'
  recogniser IS "compare the first byte against `row->sel`". Check 4 then asks
  that function whether it returns NOT_MINE when the first byte differs from
  `row->sel`. **That is the function's own definition, evaluated ninety times**,
  and it cannot fail for any value of `sel`, right or wrong. Real population:
  about ten. Printed population: about ninety. Fixing the stub vacuity (R12/P4)
  did not touch this one.
- **Check 4's SCOPE is the field it validates (MAJOR).** "For every row with
  non-null `sel`" — so a row escapes by declaring `REG_SEL_ANY`, a one-token
  edit. **`RK_VERB` has exactly one row and it IS a `REG_SEL_ANY` row**
  (`registry.c:522`), so that bucket's coverage is permanently zero — at the
  doorway §5.5 singles out as the one it cannot reason about. This is K10's
  shape exactly.
- **Check 6 varies only the row's OWN feature bit (CRITICAL)**, while §5.1
  licenses a recogniser to read any other one. And **its input set is EMPTY
  today and stays empty at landing**, because §9's acceptance bar is
  byte-identity with every name disabled. It is the only check of the invariant
  §5.4 calls load-bearing. Remedy: vary the WHOLE enabled set (all on / all off
  / this row's name inverted), and print an exact per-name coverage count with a
  ratcheting floor — a PASS line that does not say how many pairs it compared is
  indistinguishable from a green empty loop, which is this repository's
  most-repeated finding.
- **Check 3 is unfalsifiable as justified, and the invariant is false anyway**
  (§2.3's refutation above). It would pin the wrong thing.
- **Check 1 declares "no oracle" as a virtue and is labelled *Primary***, and it
  samples ONE point of a construct's form space, written by the same hand as the
  thing it checks.
- **Check 5 asserts two of purity's three clauses** and omits the cursor —
  the one arbitration depends on and the one that corrupts output.
- **§6 creates a SECOND HOME for "is this construct set-valued?"** and nothing
  makes it agree with the class port that also knows.
- **Check 7's "or zero" exemption is keyed on the same field** it validates.
- **Nothing checks that the GATE demotes rather than replaces**, and nothing
  checks the RETURNING epilogue §5.6 introduces — **K11 is the live proof that
  the epilogue is where the bodies are.**

**[OPEN] §8 needs rebuilding, not patching.** Ten checks with this many
scope-inheritance defects is a symptom of the same author writing the mechanism
and its controls, which is the failure D27 exists to break. The next version of
§8 should be written by someone denied this document's reasoning.

### 8.1 What the mechanism does NOT guard

Stated rather than implied, because §8's length invites the opposite reading.

- **Module swap between two rows, and row deletion.** `tests/reject/`'s
  hand-written manifest is their only net. Neither this design nor any
  alternative considered improves it. Adding a REAL construct with a WRONG name
  passes everything if you follow the three exact-count tripwires' printed
  remedies: libpcre2 can say a construct exists, never what pcrec should call
  its feature.
- **`note` is a factual claim about PCRE2 that nothing checks**, and K10 is
  exactly a row whose `note` contradicts its own flags. §4.1 removes those
  particular flags; it does not make `note` checkable.
- **Semantics under UTF.** R10 closed the recognition half — `PCRE2_UTF` flips
  no construct verdict — but **9 rows' SEMANTICS change under UTF and nothing
  tests those.**

---

## 9. What this replaces

    pcrec_ext_class_pair_opens      (ext.c:354)     — §6
    RF_CLASS_BASE, RF_CLASS_INVALID                 — §4.1
    parse.c:152's `\b` special case                 — §4.1
    the `in_class` parameter                        — §4
    registry_check.c:875's skip_flag                — went with RF_CLASS_INVALID;
                                                      K10's fourth blind net
    two missing doorway epilogues                   — one epilogue (§5.6)
    esc_class_value's bare `int`                    — a tagged result (§4.4);
                                                      K11's UB shape
    "requires module 'X'" as the absence of code    — an enabled set (§3.1)

**A property worth designing for:** with every name disabled, the mechanism's
output should be **byte-identical** to today's across the corpus — the SR-2
acceptance bar — because §5.4 makes today's behaviour one branch of it. The
deliberate exceptions are the behaviour changes this document argues for (K12's
endpoint rule, and §7.1's new rows), each of which should land as its own
change with its own pins rather than riding along inside the refactor. Byte
identity has an honest limit, recorded at K4: **it cannot see a bug that both
sides share.**

> ### REFUTED (R13 — C5/F11, C5/F9) — byte identity is NOT achievable as written
>
> Four divergences, three of them unlisted here, two of them necessary
> consequences of §3.1 rather than accidents:
>
> 1. **`[\b]`** — §4.1 gives `\b` a class port and §5.4's gate demotes it,
>    because `assertions` is disabled. `tests/base/escapes.rxt:96-98` pins `[\b]`
>    with a comment explaining exactly this rule, so the corpus WOULD catch it —
>    but the design does not expect it, so it is a defect rather than a planned
>    exception.
> 2. **K10's fix** (`[\N{U+41}]`), which the author had already missed from the
>    list.
> 3. **K12's endpoint rule** and **§7.1's new rows** — the two that were listed.
>
> **And C5/F9 reverses §4.1's conclusion about K10:** §9's deletion audit is
> wrong about what `registry_check.c` actually holds up, so removing
> `RF_CLASS_INVALID` does not subsume it. §4.1's "K10 becomes structurally
> unrepresentable" does not survive that.
>
> **C4/F5 states the same thing as a process failure:** §4.1 + §9 do exactly
> what K10's own entry forbids — *"Do not fix the flag without the sweep, or the
> next reader has the same four blind nets"* — and none of §8's ten checks
> covers the class position with a TAIL, which is the sweep K10 demands.

---

## 10. Open questions, collected

**Revised after R13.** Items marked RESOLVED were closed by the panel's
measurements; items marked WIDENED got worse under review. Everything here is
for Frank.

1. **RESOLVED toward STATUS — `RS_NOT_OFFERED` is a status, not a name.**
   (§7.2) C2 measured 274 ALT_BSUX-dependent verdicts over 120,099 probes. If
   `alt-bsux` were a name in the enabled set, recognition would depend on the
   enabled set, which §5.4 forbids. The uniformity argument costs the
   load-bearing invariant. **And there is a THIRD category** with no home yet:
   `\x` is base grammar whose meaning ALT_BSUX changes.
2. **[OPEN] The full bound-mode list.** (§7.2) Still needs the option sweep;
   `ALT_BSUX` is now established behaviourally (bit `0x2`) rather than assumed,
   and `PCRE2_UTF` (`0x80000`) is confirmed to change 0 of 120,099.
3. **RESOLVED, and the question was aimed at the wrong pair.** (§3.3)
   `unicode-props` / `classes` measures at exactly ZERO coupling. The real
   dependency edges are the three C2 measured into the capture count, and
   C2/F6 derives the graph.
4. **[OPEN] Feature-mask width.** (§3.3) Unchanged: 16 of 32 bits used.
5. **[OPEN] Where toggles are exposed.** (§3.3) Unchanged. Note C4/F4: with no
   switch at all, check 6 has an empty input set, so this is not only an API
   question.
6. **WIDENED to CRITICAL — the whole-pattern pre-scan breaks the invariant.**
   (§10.6 as it was) C2/F3 measured that `\1`'s validity at offset 0 depends on
   constructs owned by `modifiers`, `comments`, `quoting` and `branch-reset`
   appearing LATER:

       \1(a)        OK        \1(?n)(a)    err 115     \1(?#()   err 115
       \1\Q(a)\E    err 115   \1(?|(a))    OK

   So the pre-scan needs live lexer code for features that are DISABLED — which
   contradicts §3.1's "the enabled set instead of the absence of code" and its
   migration story, because `backrefs` cannot land alone. **And the defence this
   document offered — "pcrec never says 'reference to non-existent subpattern'
   because it refuses `\1..\9` with a module name first" — is the third
   instance of the guard-is-the-unimplemented-ness shape that this same document
   diagnoses twice elsewhere (§6 on K12, and `plan.md:577` on `(?xx)[a- ]`).**
   Being able to name a failure mode twice and then commit it in the same
   document is the most useful thing the panel found.
7. **REOPENED — backrefs and octals.** The split is still right, but the
   resolution claimed here was wrong. §5.1's "each recogniser reads the count
   and exactly one claims" does not survive §2.3's refutation: `\12` is a
   backreference at atom position and octal in a class at the SAME count, so the
   deciding input is position as well as count, and per-port recognition is
   required. See §2.3's [OPEN].
8. **[OPEN, NEW] What a missing producer asserts.** (§4.1) At least three
   meanings, and the literal-fallback case (`[\k]`, `[\g]` compile as literal
   letters) has no home in the vocabulary.
9. **[OPEN, NEW] The sixth outcome.** (§4.4) Transparent/lexical-mode
   constructs — `\Q...\E`, `\E`, `(?#...)` — are none of the five, and §6 needs
   a third endpoint answer ("not here, keep looking").
10. **[OPEN, NEW] Can TERMINAL allocate?** (§5.2) `(?(`'s correct answer needs a
    parse. Either the rule becomes "must not COMMIT" rather than "must not
    produce", or the exempt rows are named and their over-promise accepted in
    writing.
11. **[OPEN, NEW] The corrected endpoint rule.** (§6) Per-doorway and per-side.
    The class-bracket doorway is exactly right over 21,396 patterns; the escape
    doorway is not; the low side is asymmetric with the high side.
12. **[OPEN, NEW] §8 wants rebuilding by someone denied this document.** The
    density of scope-inheritance defects across ten checks is the signature of
    one author writing both the mechanism and its controls, which is what D27
    exists to break.
