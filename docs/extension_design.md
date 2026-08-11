# pcrec's extension mechanism — design

**Status: PART I PROPOSED AND PARTLY REFUTED (R13); PART II (§11-§18) is the
redesign that answers R13's holes, written 2026-08-11 fourth session after
Frank's rulings (D34), then itself reviewed the same session by the R14 panel
— which refuted its two central factual claims. Corrections are inline,
marked R14; §18 is the post-R14 state and Frank's open decisions. Not built.
Not adopted.**

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
>
> **PART II (§11-§18, fourth session) is the redesign that answers the holes
> above, written after Frank ruled on §10 (D34) — read it after this Part, not
> instead of it. It was itself reviewed the same session (R14), partly
> refuted, and corrected inline; read ITS panel-outcome block too.**

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
> **NEGATIVE RESULT, AND IT IS WRONG — see the correction below.**
> C2 measured `PCRE2_UTF` (bit `0x80000`, established behaviourally) as changing
> **0 of 120,099** verdicts, apparently reproducing R10.
>
> ### CORRECTED AGAIN (R13 — C5/F14, verified by the author): UTF DOES flip a verdict
>
>     \N{U+0041}     opt=0  err 193    opt=UTF  COMPILES
>     [\N{U+0041}]   opt=0  err 193    opt=UTF  COMPILES
>
> **Both sweeps are correct.** C2's probe space was strings of length 1..3,
> which cannot contain a ten-character construct; C5 swept the registry's own
> `syntax` strings, which can. *Counting a population by a generator that cannot
> produce it counts the generator* — and this is the second time in one session
> that a measurement was taken on a space that could not falsify the claim.
>
> C5's full sweep, 376 + 198 generated patterns over all 32 single bits, found
> **8 verdict-changing bits**, not two: `ALLOW_EMPTY_CLASS`, `ALT_BSUX`,
> `NO_AUTO_CAPTURE` (11 flips), `UTF`, `NEVER_BACKSLASH_C`, `LITERAL` (143),
> `MATCH_INVALID_UTF`, `ALT_EXTENDED_CLASS`.
>
> **And this breaks §7's framing, not just its list.** `\x` is mode-dependent
> under ALT_BSUX and is BASE grammar — pcrec implements `\x41` in `parse.c`, not
> in the table — so `\x` must NOT get a row. **The bound mode is therefore not
> expressible as a set of row statuses or a set of names**, which is what §7 is
> built on.

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

> **Revised again after Frank's rulings (D34, fourth session): items 1, 3, 6,
> 7, 8, 9, 10/10a, 11 and 13 are answered in PART II (§11-§17), pending the
> R14 panel. Items 2 (the bound-mode sweep), 4 (mask width — ruled: stay at
> 32 with a loud ceiling check), 5 (ruled: CLI-only `--without=NAME`) and 12
> (ruled: §8 rebuilt by a D27 author) are dispositioned in §11. The texts
> below stand as the record of the questions as asked.**

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
10a. **[OPEN, NEW — the panel's own proposed repair, NOT adopted]** C1's
    re-cut of `ask` into two independent axes: `want` (CLAIM / VERDICT / RESULT)
    and `may` (a capability SET — ALLOCATE / RECURSE / DIAGNOSE), with the
    cursor never moving below WANT_RESULT. The diagnosis behind it is
    unarguable: `(?(` needs the LEAST information and the MOST effects, so no
    total order can contain it. Distinguished from D32 §8's refuted trial mode
    because allocation is permitted rather than trapped, and the arena is the
    real one. Recorded rather than adopted, because adopting an unreviewed
    design at the desk is what this panel caught. See R13 addendum 2.
13. **[OPEN, NEW] The THIRD axis — what pcrec will EVER do.** (K14) Not a fact
    about PCRE2, so the status column cannot hold it; not a fact about one
    compile, so the enabled set cannot hold it. §7.2's `RS_NOT_OFFERED` and its
    [OPEN]'s permanently-disabled name are BOTH category errors, which retires
    open question 1 as posed rather than answering it. pcrec ships this defect
    today for the backtracking verbs.
12. **[OPEN, NEW] §8 wants rebuilding by someone denied this document.** The
    density of scope-inheritance defects across ten checks is the signature of
    one author writing both the mechanism and its controls, which is what D27
    exists to break.

---
---

# PART II — THE REDESIGN (2026-08-11, fourth session; PROPOSED — R14 has RUN)

> ## R14 PANEL OUTCOME — READ BEFORE ANY PART II SECTION
>
> A three-lens panel (R14, `docs/reviews/2026-08-11-r14-part2.md`, ~5,400
> probes) ran against Part II the session it was written. **Its two central
> factual claims were refuted** — §16.2's "exactly ONE deviating cell" (a
> second cell was printed in §16.1's own table and read as confirmation) and
> §14.2's digit rule (every multi-digit escape beginning 8 or 9) — and §12.2's
> "backrefs can land alone" is withdrawn. Corrections are applied inline below,
> marked **R14**; what they leave genuinely undecided is in §18. The panel's
> method note is R13's, recurring: *in each refuted section the falsifying
> bucket was one probe away, and the probe set used was one the claim could
> not fail on.*
>
> **What R14 corroborated, with counts:** per-port recognition (every cell,
> including class-side digits and fallback tails); the endpoint CORE rule at
> the escape doorway (every constructible cell beyond the curated 33); the
> LEXICAL set being exactly {`\Q…\E`, `\E`, `(?#…)`} (27 candidates, no
> fourth); the tokenizer reading AT atom/class-item positions (34 probes);
> the ten NULL class-port rows being mode-invariant; and invariant 6 (the
> cursor rule) as "the best of the nine — both sides computed by the harness,
> total, one-line live sabotage".

Frank reviewed Part I and ruled on its open questions (D34). This part is the
single design pass those rulings called for, covering §10's items 6, 7, 8, 9,
10/10a and 11 **together**, because R13's refutations cluster on one cause:
Part I assumed one recogniser, one shape, and one total order per row, and
PCRE2's grammar has position-dependent construct *identity* (`\12`), doorway-
and side-dependent error *precedence* (`[0-\p{Foo}]` vs `[[.a.]-z]`), and
constructs that are not atoms at all (`\Q...\E`). Every section below pushes
the missing distinction into per-port or per-doorway **data** rather than a
global invariant.

Every measurement in Part II was taken 2026-08-11 (fourth session) against
libpcre2 10.46 through `tests/fuzz/pcre2_abi.h`, or against `build/pcrec` at
`37a2401`, and is quoted with its probe. Two probe programs produced them
(`probe_qe.c`, `probe_atom.c`, session scratchpad — the outputs are quoted here
in full where load-bearing, because the scratchpad is ephemeral).

**What Part II does NOT cover, deliberately:** §7's bound-mode list (its
framing broke — the mode-dependent set reaches base grammar — so it gets its
own document after the option sweep, OQ 2); and §8's checks (ruled to be
rebuilt by an author denied this document, OQ 12 — §17.3 hands that author the
invariant list). Part I's text is left as the record; §17 maps which sections
it supersedes.

---

## 11. The rulings (Frank, 2026-08-11 — recorded as D34)

1. **Two axes for what a row is** (was OQ 1 + 13): a `status` column holds
   facts about PCRE2; a new `disposition` column holds facts about pcrec's
   roadmap (PLANNED / NEVER). "Requires module 'X'" is only ever emitted for
   PLANNED. Fixes K14. §17.2.
2. **Bound-mode list**: separate document, after the sweep (OQ 2 stays open).
3. **Mask width** (OQ 4): stay at 32 bits with a loud check at the ceiling.
4. **Toggles** (OQ 5): CLI-only `--without=NAME`, test-facing, not public API.
5. **Recognition is never gated; only production is** (OQ 6): §12.
6. **Per-port recognition, one rank per row** (OQ 7): §14.
7. **Explicit literal-fallback class ports** (OQ 8): §14.3.
8. **`\Q`/`\E`/`(?#...)` are lexical-mode, owned by the lexer** (OQ 9): §13.
   The sixth-outcome repair is rejected.
9. **Adopt C1's `want`×`may` re-cut of the ASK contract** (OQ 10/10a) as the
   basis, subject to R14: §15.
10. **The endpoint rule is measured, not derived** (OQ 11): §16.
11. **§8 is rebuilt under D27** (OQ 12): by an author denied this document.

## 12. Recognisers are ALWAYS LIVE; only producers gate (answers OQ 6)

**The rule.** Every port's RECOGNISE phase — and the extent computation §12.2
adds — is permanently-live code with no path from the enabled set into it. The
gate applies to PRODUCE only. §5.4's invariant ("recognition never depends on
what is enabled") stops being a vacuous consequence of single-pass termination
and becomes a structural property: it holds because the code that could break
it does not exist. Single-pass termination remains as a second wall, no longer
the only one.

This also dissolves §3.1's apparent contradiction. "The enabled set instead of
the absence of code" was always about producers; recognisers were never absent
— `sel` + `tail` data exists for every row today. §12.2 extends that to
extents, and nothing more.

### 12.1 What C2/F3 measured, re-verified

All five cells reproduce exactly (probe_atom.c, fw-1..fw-5):

    \1(a)         COMPILES        \1\Q(a)\E     ERR 115
    \1(?#()       ERR 115         \1(?|(a))     COMPILES
    (?n)(a)x12\12 COMPILES (octal)

`\1`'s verdict at offset 0 depends on group-count effects of constructs owned
by `quoting`, `comments`, `modifiers` and `branch-reset` appearing LATER. So
backref recognition needs a whole-pattern group count, and the count-scan needs
correct extents for exactly: `\Q...\E` runs, classes, `(?#...)`, `(?x)`-mode
comment/whitespace, `(?n)`, and `(?|`.

### 12.2 The count-scan is the LEXER in count mode, not a second parser

Under §13, `\Q`/`\E`/`(?#...)`/`(?x)`-whitespace are lexer-owned; classes are
base grammar; `(?n)` and `(?|` are *recognised* (not produced) by their rows.
So every extent the count-scan needs comes from machinery that is always live
by this section's rule. There is no duplicate branch scanner (the thing OQ 6
feared), and **`backrefs` can land alone**: the `quoting`/`comments`/
`modifiers`/`branch-reset` rows contribute their recognisers and extents from
day one while their producers stay gated.

Worked example, `quoting` disabled, `backrefs` enabled:

- `\1\Q(a)\E` — count-scan (always live) sees the quote extent, counts 0
  groups; the parser reaches `\1`, the backref row claims (a single digit is
  always a backreference, §14.2), produces, and fails "reference to
  non-existent subpattern" at offset 0 — the same verdict PCRE2 gives (115).
  The compile never reaches the disabled `\Q`.
- `\1(a)\Q\E` — count 1, `\1` produces a valid backref, the parser reaches
  `\Q` and terminates with "requires module 'quoting'". PCRE2 compiles it;
  pcrec's refusal names the exact unimplemented construct. Correct under D26.

**The guard is no longer the unimplemented-ness** — the count is computed by
live code in every configuration, which is what OQ 6 demanded and the pre-scan
as designed could not deliver.

> ### REFUTED IN PART (R14 — C1/F3, C3/F1, C3/F2, C2/F4; verified by the author)
>
> **§12.2's "exactly" list is short by at least four families, and "backrefs
> can land alone" is WITHDRAWN.** The count-scan must classify EVERY
> `(`-initiated form as capturing or not:
>
>     \1(?<n>a)  \1(?'n'a)  \1(?P<n>a)   COMPILE     (named groups CAPTURE)
>     \1(?=a) \1(?<=a) \1(?>a) \1(?i:a)  ERR 115     (these do not)
>     \2(*MARK:()(a)   \2(?C"(")(a)      ERR 115     (verb/callout bodies hide a `(`)
>     \2(?|(a)|(b)|(c))                  ERR 115     ((?| is a per-branch MAXIMUM)
>     ((?n))(a)\1  OK   vs   (?n)(a)\1  ERR 115      ((?n) is a SCOPED mode; (?-n) reverses)
>
> The `(?|` maximum needs a nesting-aware top-level `|` scan — `|` hidden by
> an escape, a class, a quote, a comment, and unbounded nesting, all measured
> — which is the scan R13 used to kill TERMINAL at `(?(`. So §12.2's "no
> duplicate branch scanner" is FALSE, and the always-live layer is honestly a
> **group-header sub-parser plus verb/callout body extents** — including code
> for two RD_NEVER families. Whether that changes the migration order is §18's
> first open question.
>
> **Corrections adopted:** a per-row `captures` fact (data, checked against
> libpcre2's capture count per row syntax — it must not be a hand-list, C3/F2);
> the §13.3 axis split into THREE — recognise / count-affecting semantics /
> produce-a-node — with the middle always live by name (`(?x)` `(?n)` `(?|`
> `\Q…\E` and every capturing form; C2/F4 measured `\2(?x)#(a)\n(b)` err 115
> vs `\2#(a)\n(b)` COMPILES); invariant 2 re-scoped to **libpcre2 as the
> oracle, over generated patterns compiling or not** — as written its scope
> excluded undercounts, the only failure direction the gaps produce (C3/F1);
> and §12's "the code does not exist" claim gets a MECHANISM — recognisers and
> extent scans live in translation units that do not link the enabled-set
> symbol, checked by `nm` in the build, sabotage = an added reference (C3/F7).

## 13. Lexical-mode constructs: `\Q`, `\E`, `(?#...)` (answers OQ 9)

### 13.1 The measurements

Everything below is probe_qe.c, sections A-D, quoted in full because this
section's conclusion rests on the *pattern* across them:

    A1  ^\Qab\E*$      "abbb" MATCH   "ababab" no      quantifier binds LAST char
    A4  ^(\Qab\E)*$    "ababab" MATCH "abbb" no        grouping restores the run
    A5  ^\Qab\E+$      "abbb" MATCH   "ab" MATCH
    A6  ^\Qab\E{2}$    "abb" MATCH    "abab" no
    A2  ^a\Q\E*$       "aaa" MATCH                     empty quote is TRANSPARENT to *
    A3  ^\Q\E*$        ERR 109                          ...and leaves no target
    B1  ^[\Qa-z\E]$    "-" MATCH   "b" no              `-` quoted: three literals, no range
    B2  ^[\Q]\E]$      "]" MATCH                        `]` quotable
    B4  ^[\Q^\Ea]$     "^" MATCH   "a" MATCH            `^` quoted
    B7  ^[\Q\\\E]$     "\" MATCH                        `\` quoted
    B3  ^[a\Q\E-z]$    "m" MATCH   "-" no              range FORMS THROUGH an empty quote
    B5  ^[0-\Q\Ea]$    "5" MATCH   "a" MATCH            endpoint reached through the quote
    B6  ^[0-\E9]$      "5" MATCH   "-" no              range forms through a bare \E
    C1  (?i)\Qa\E      "A" MATCH                        case-folding applies INSIDE the quote
    C2  (?x)\Q a\E     " a" MATCH  "a" no              (?x) whitespace-skipping suspends inside
    C8  ^\Qa\E\E b$ (EXTENDED)  "ab" MATCH  "a b" no   ...and resumes after \E
    C3  ^(a)\Q\1\E$    "a\1" MATCH "aa" no             \1 inside the quote is two literals
    C4  ^\Q\Q\E$       "\Q" MATCH                       no nesting: inner \Q is two literals
    C5  ^\Qab$         "ab$" MATCH "ab" no             unterminated quote absorbs $ to the end
    C6  ^a\Eb$         "ab" MATCH                       bare \E is a no-op
    C7  ^[a\E]$        "a" MATCH                        ...in a class too
    D1  ^a(?#x)*$      "aaa" MATCH "a" MATCH            * binds `a` THROUGH the comment
    D2  ^(?#x)*$       ERR 109                          comment leaves no target either
    D3  ^a(?#x)b$      "ab" MATCH
    D4  ^[0-(?#x)]$    ERR 108                          `(` is a literal inside a class

### 13.2 The conclusion: these are not constructs with outcomes; they are
tokenizer modes

Every row of §13.1 is consistent with ONE reading and inconsistent with every
atom-shaped reading: **`\Q...\E` is a lexer mode that turns raw bytes into
literal character tokens; `(?#...)` is a lexer discard; downstream machinery
(classes, ranges, quantifiers, case-folding, anchors) sees only the tokens.**
The quantifier binds the last character because the parser only ever saw
characters. The range forms through `\Q\E` and `\E` because the range logic
never saw them. Case-folding applies inside the quote because folding is a
semantic property of the character token, not a lexical one. `(?x)` suspends
inside `\Q` because both are modes of the same tokenizer.

A port-and-outcome reading cannot reproduce this. The natural `EXT_NODE`
reading is R13's tier-1 miscompile (`\Qab\E*` → `(ab)*`); a sixth
`EXT_TRANSPARENT` outcome would need every consumer of every outcome to learn
"not here, keep looking" — §4.4's own argument against unread values, applied
to every caller at once. **The sixth outcome is REJECTED. `\Q`, `\E` and
`(?#...)` leave the outcome vocabulary entirely; the five outcomes of §4.4
stay five, and are once again total over their domain — every construct that
IS an atom or class item fits them.**

### 13.3 Lexical, but NOT base grammar

Frank's question, answered with a distinction: **implementation locus and
gating are different axes.** `\Q...\E` is lexical in locus — when built, it is
built in the tokenizer, not as a row with ports. It is NOT base grammar:

- pcrec today refuses all three (`build/pcrec` at `37a2401`):

      \Q      ->  \Q requires module 'quoting'
      \E      ->  \E requires module 'quoting'
      (?#x)a  ->  (?#...) requires module 'comments'

  Base grammar is never refused; these must keep being refused until
  implemented, and byte-identity (§9) requires the exact strings.
- D26 tier 2 requires attributing the construct to its owner while it is
  unimplemented. A base construct carries no name to attribute.
- The sabotage instrument (§3.1) applies: `--without=quoting` must refuse
  `\Q` with today's message. Base grammar is not toggleable (§3.3), and
  quoting must be.

So the table keeps rows for `\Q`, `\E` and `(?#...)` — carrying name, syntax,
status, disposition, note — but of a new row kind, **LEXICAL: no class port,
no AST port.** The "producer" is the lexer-mode transition itself, and it
gates like any producer: disabled → terminal at the token, with the row's
existing vocabulary. Their recognisers and extent scans are always live
(§12.2). When `quoting` lands, bare `\E` becomes the measured no-op (C6/C7) —
a planned, pinned behaviour change, not a byte-identity accident.

`(?x)`'s whitespace/comment skipping is the same tokenizer machinery, owned by
`modifiers` — the lexer hosts mode state; producers set it. That is the
designed home for C2/F8's finding that `(?x)` is a state-setter, not a
violation of §12's rule: recognising `(?x)` never depends on the enabled set;
*acting* on it does.

> ### CORRECTED (R14 — C1/F6, C3/F4, C3/F6, C3/F16; verified by the author)
>
> **(a) Quote mode belongs to the ATOM/CLASS-ITEM tokenizer only.** It is not
> entered in group headers, subpattern names, quantifier bodies or braced
> escape bodies — `(?\Q:\Ea)` is err 111, `(*\QFAIL\E)` 160, `\p{\QL\E}` 147,
> and `a{\Q2\E}` matches the LITERAL "a{2}". The sharpest cell: **`(\Q?\E:a)`
> is a CAPTURING group** while `(?:a)` is not, so a lexer entering quote mode
> uniformly counts groups wrong — §13.2's "downstream machinery sees only the
> tokens" holds exactly where §13.1 measured it (34/34 probes at atom/class
> positions) and nowhere else. The count-scan (§12.2) must scope its modes the
> same way.
>
> **(b) The tokenizer's modes are also CLASS-SCOPED, differently per row.**
> `\Q`/`\E` are active inside a class (`[\Qa-z\E]` quotes the `-`);
> `(?#` is NOT a comment inside a class — `[a(?#x)]+` matches "(#x)", the
> bytes are ordinary members, because a class member never consults the GROUP
> bucket at all. §14.3's "a NULL class port means permanently invalid" is
> therefore SCOPED to port-bearing rows of the two buckets a class position
> consults (escape, class-bracket); the two lexical escape rows' class
> behaviour is lexer-owned, and `(?#`'s row needs no class story of any kind.
>
> **(c) QUANTIFIABILITY is a third axis this section missed, and it is R13's
> `\Qab\E*` mechanism on 22+ rows.** Measured: atom-position constructs
> partition into THREE quantifier classes — transparent (`(?#c)`, `\Qz\E`,
> `\E`), repeatable (`(?=x)`, `(?:x)`, `(?>x)`, `(?R)`…), and NON-repeatable,
> err 109: `\b \B \A \Z \z \G \K`, the modifier family `(?i)`, `(?C1)`,
> `(*FAIL)`, `(*MARK:z)`. No §4.4 outcome encodes "not a quantifier target";
> an EXT_NODE from a non-repeatable row lets `try_quant` compile `a\b*`,
> which PCRE2 rejects. Not derivable from any existing column — `(?=x)` is an
> assertion and repeatable; `\b` is an assertion and not. **Adopted: a
> per-row `quantifiable` fact, populated and checked by sweeping
> `a<syntax>*` over all 100 rows against libpcre2.** Where it lives (column
> vs outcome flag) is §18.
>
> **(d) §13.2's "cannot reproduce this" overstated what was measured** — the
> EXT_NODE reading measurably miscompiles; the sixth-outcome reading was
> rejected on an unmeasured cost. The conclusion stands on (a)-(c)'s evidence;
> the word "cannot" does not, and the LEXICAL set membership is guarded by the
> criterion itself as a check: *a row is LEXICAL iff `a<syntax>*` compiles
> and the quantifier binds the preceding atom, per libpcre2* — swept, so a
> fourth lexical construct is FOUND rather than assumed away (C3/F11: 27
> candidates probed, exactly three qualify today).

## 14. Per-port recognition (answers OQ 7 and OQ 8)

### 14.1 Each port recognises for itself; disagreement is the designed
behaviour

§2.3 is replaced. A row still appears once in the table with one name-pair
(per-port features, §4.1's correction), but each port carries its own
RECOGNISE, and the two ports of one row may disagree about whether the
construct is present. That disagreement is not a defect to check away — it is
PCRE2, measured:

    \12  at 12 groups, atom pos.:  backreference   (br-12:  matches "a"x12+"a")
    \12  at 12 groups, class pos.: octal 012       (br-12c: [\12] matches "\n")
    \8 \9 \k \g  atom pos.:        constructs      (ERR 115, 115, 169, 157)
    \8 \9 \k \g  class pos.:       literal letters ([\8] matches "8", etc.)

Arbitration runs per-bucket as today, over the recognisers of the ports at the
current position. The `backrefs` rows' class-side recognisers decline
unconditionally — backreferences do not exist inside classes, a permanent
PCRE2 fact — so the octal row claims `[\12]` and the literal rows claim
`[\8]`, at any group count.

### 14.2 The atom-side digit rule, corrected while we were here

Part I (§5.1, §10.7) had "octal or backreference according to the count" for
all digit escapes. Measured, the real atom-position rule is finer:

    ^\12$  0 groups   COMPILES, octal   (matches "\n")
    ^\8$   0 groups   ERR 115           single digit: ALWAYS a backreference
    ^\0$              COMPILES, octal   \0 is NEVER a backreference

**A single digit `\1`..`\9` at atom position is always a backreference** —
err 115 when the group is missing, never octal fallback. Multi-digit escapes
fall back to octal by count (`\12` at 0 groups is octal 012). `\0` is always
octal. This refines the §10.7 split and is why check 1's complete-probe rule
matters: a `\8` row probed as bare `\8` is probed at its ERROR, and its happy
path needs `(a)x8` in front (verified: 8 groups + `\8` compiles and matches).

> ### REFUTED IN PART (R14 — C1/F2 and C3/F13, independently; verified by the
> author)
>
> The paragraph above was derived from `\12`, `\8`, `\0` — a probe set with no
> multi-digit run beginning 8 or 9, i.e. one that could not falsify it. The
> same method failure this section exists to correct, and the missing clauses
> are three:
>
>     \81 \90 \88 \99 \80 \819 \8123   at 0 groups: ALL err 115
>
> **A decimal number beginning 8 or 9 is ALWAYS a backreference, at any
> length, regardless of count** (8 is not an octal digit; the prescribed
> fallback was not even well defined). Count still matters within that rule:
> `(a)x9 \98` is 115, `(a)x98 \98` compiles. And the octal fallback itself is
> not "the whole run": **up to three OCTAL digits are re-read and the rest are
> literals** (`\19` = `\x01` + "9"; `\0123` = `\x0a` + "3"), and overflow is
> its own error (`\400 \500 \777` err 151 in 8-bit non-UTF mode; `\3777` =
> `\377` + "7"). §17.3's invariant on this rule carries all three clauses —
> as written it certified an implementation that reads `\81` as octal.

### 14.3 The literal fallback is an EXPLICIT port, and NULL regains its one
meaning (answers OQ 8)

The full class-position sweep over `[\c]` for all 62 ASCII letters and digits
(probe_qe.c section E) partitions cleanly:

    literal fallback   \g \k \8 \9                      compile; MATCH the letter itself
    base scalar        \a \b \e \f \n \r \t \0..\7      compile; match the control/octal byte
    construct (set)    \d \D \w \W \s \S \h \H \v \V    compile; match members
    ERR 107/171        \A \B \C \G \K \R \X \Z \z \N    permanently invalid in a class
    ERR 103            \i \j \m \q \y \I \J \M \O \T \Y  not an escape anywhere
    own-body errors    \c(106) \o(155) \p \P(146) \x(178) \u \l \F \L \U(137)
    lexical            \Q \E                            §13

The four fallback rows get **explicit class ports producing `EXT_SCALAR` of
the letter** — data, like the char-type escapes, not functions. `[\k<name>]`,
`[\g{1}]`, `[\9]` (C1/F9's probes) follow with no further machinery: the
tailed `\k<`/`\g{` rows' class recognisers decline, the bare row claims one
letter, and `<name>` re-enters the class loop as ordinary literals.

With the fallback explicit, **a NULL class port means exactly one thing again
— permanently invalid at class position** — which §4.1 wanted and could not
have. The three meanings R13 counted are now three representations: base/
scalar data ports (`\b` → 0x08), literal-fallback data ports (`\g \k \8 \9`),
NULL (the ten ERR 107/171 rows). **This is the K13 fix**: the twelve rows'
class answer becomes the literal, produced and testable, instead of module
`backrefs` asserted by silence.

Per-port features make the C5 miscompile unrepresentable too: `\b`'s class
port is base (never gated) and its AST port is `assertions` (its own handler,
not the generic wrapper). The §4.2 wrapper applies only to rows whose two
ports share one feature and a set/scalar shape — the char-types — which is
what it was designed from.

### 14.4 Rank stays one per row

Per-port recognition reopened whether `rank` is per-port. Ruling: **one rank
per row, until a measured counterexample.** Rationale: rank only means
anything between clashing recognisers; the measured clashes (`\N` family, the
digit family) either arbitrate identically at both positions or are resolved
by a port's recogniser declining outright, so no measured case needs two
ranks. The revisit trigger is concrete: a bucket where two rows clash at BOTH
positions and the winner must differ. None exists in the current table.

The check-3 successor: every row states its expected class-position
disposition **as data** — claimed-by-me / claimed-by-row-R / invalid — and a
total check walks the table comparing each row's `syntax` at class position
against that column, through the real dispatch. The K13 shape (wrong answer at
the position the author didn't think about) becomes a per-row assertion
against libpcre2 instead of a silence. Detailed check design belongs to the
§8 rebuild (D27 author).

> ### CORRECTED (R14 — C2/F9, C2/F17, C3/F8, C3/F9, C1/F8)
>
> Four defects in the two paragraphs above, all applied:
>
> - **"Through the real dispatch" compared pcrec against pcrec** — K13
>   survives that check (the author who believes the wrong module writes the
>   column, the dispatch agrees). The check is COLUMN vs LIBPCRE2; the
>   dispatch comparison is a separate secondary line.
> - **The column's vocabulary was unobservable and a second home.**
>   `claimed-by-me`/`claimed-by-row-R` are facts libpcre2 cannot see, and
>   `claimed-by-row-R` stores row R's fact in someone else's row — the K10
>   two-homes shape. The column becomes TWO-VALUED and libpcre2-observable:
>   *what does `[<syntax>]` do — compile as WHAT, or error N.* Which pcrec row
>   claims is the dispatch's business, not data. Renamed **"class-position
>   expectation"** — "disposition" now means only the roadmap column (§17.2).
> - **Its real population is 44, not 100** — 41 esc + 3 class-bracket rows
>   can reach a class position; `(` is an ordinary member (`[a(?#x)]+`
>   matches "(#x)"), so 56 group/verb rows carry NO value rather than an
>   invented one (§4.4's own objection). Within the 44 the single `syntax`
>   probe samples one point — `[\cX]` never sees `[0-\c]` err 108 vs
>   `[\c-z]` COMPILES (`\c` eats the delimiter) — so endpoint-adjacent
>   probes are part of the row's probe SET, and the check prints real and
>   covered populations per bucket with a ratcheting floor.
> - **The partition is mode-dependent** (C1/F8): under
>   `EXTRA_BAD_ESCAPE_IS_LITERAL` 18 of the 62 class cells migrate into
>   literal-fallback (the set becomes 22 rows, not 4). Bound-mode document
>   material. The part that HOLDS, measured: the ten NULL rows are exactly
>   the rows that do not move under any swept option — "NULL means
>   permanently invalid" is mode-invariant, which is the claim this section
>   needs.

## 15. The ASK contract: `want` × `may` (answers OQ 10, adopts 10a)

C1's re-cut is adopted as the basis. The diagnosis stands unweakened: `(?(`'s
terminal answer needs the LEAST information (a branch count) and the MOST
effects (a real parse), so no total order of ask levels can contain it.

    want   WANT_CLAIM    is this yours, and what shape
           WANT_VERDICT  the right terminal answer, whatever it costs
           WANT_RESULT   the produced set/node

    may    capability SET: MAY_ALLOCATE | MAY_RECURSE | MAY_DIAGNOSE

    hard rule: cx->pos moves ONLY under WANT_RESULT.

The old levels map to points in the space — SHAPE = {CLAIM, ∅}, TERMINAL =
{VERDICT, ALLOCATE|RECURSE|DIAGNOSE}, FULL = {RESULT, all} — and the case no
level could express becomes ordinary: `(?(` at VERDICT parses its body with
the real parser into the real arena, reads the branch count, raises E127/E154
exactly, and discards the subtree (freed wholesale at compile exit, which is
what an arena is for). This is not D32 §8's trial mode: allocation is
permitted, not trapped, so nothing aborts and nothing leaks.

**The gate (§5.4 restated):** demotes `want` by one — RESULT → VERDICT — and
leaves `may` alone. A disabled `conditionals` still answers E127 for
`(a)(?(1)x|y|z)`: no over-promise, FIX-2's standard held at every doorway.

Check 5's successor is C1's: *no ask with `want` below WANT_RESULT moves
`cx->pos`* — one comparison, total over every row, live sabotage (make one
handler commit under VERDICT).

**[OPEN, narrowed] C1/F6's after-the-construct case** — a terminal answer
that depends on text AFTER the construct — is not covered by `want`×`may` and
is deliberately left open for R14 with its R13 citation, rather than patched
here. It is one finding wide; the contract above is not redesigned around an
unmeasured case.

> ### CORRECTED (R14 — C3/F3, C1/F7, C2/F14, C2/F15, C3/F17)
>
> **(a) "Parse the body with the real parser" over-promises in the shipping
> configuration** (C3/F3, verified): the real parser has GATED producers, so
> `(a)(?(1)\d|y|z)` — PCRE2 err 127, PERMANENT — dies first at the gated
> `\d` with "requires module 'classes'". The FIX-2 promise this section makes
> fails at its own motivating row, in the all-disabled state the refactor
> ships in. **Correction: the E127/E154 branch count comes from §12.2's
> always-live count-scan** (which already needs every extent this requires),
> not from a recursive parse. The measured half that survives: real body
> errors DO beat 127 (`(a)(?(1)x|y|[z)` → 106) — body-first precedence is
> right; only the gated-producer route to it was wrong.
> **Consequence, §18:** with `(?(` served by the scan, NOTHING currently
> motivates `MAY_ALLOCATE|MAY_RECURSE` at VERDICT. The `want`×`may` diagnosis
> stands; whether `may` still earns its keep is for Frank.
>
> **(b) "[OPEN, narrowed]... one finding wide" is WITHDRAWN** (C1/F7): 18 of
> 26 class items change their correct verdict when a range tail follows —
> after-the-construct dependence is §16's entire subject, one section later.
> The endpoint caller owns that dependence; the sentence claiming it was rare
> was false.
>
> **(c) Legality rules, previously unstated** (C2/F14): the gate FLOORS at
> VERDICT (never demotes to CLAIM — silence where a message is owed);
> `WANT_VERDICT` requires `MAY_DIAGNOSE`; `WANT_RESULT` carries all three
> capabilities. **(d)** CLAIM's consumer is ARBITRATION (`{WANT_CLAIM, ∅}`),
> not the endpoint rule — the annotation carried over from C1's R13 table was
> stale the moment §16 made the endpoint evaluate in full (C2/F15, C3/F17).

## 16. The endpoint rule, measured (answers OQ 11)

### 16.1 The measured table

probe_qe.c section F, complete:

    HIGH, escape doorway            LOW, escape doorway
    [0-\d]        150               [\d-z]        150
    [0-\p{L}]     150               [\p{L}-z]     150
    [0-\p{Foo}]   147               [\p{Foo}-z]   147
    [0-\p]        146               [\p-z]        146
    [0-\N{U+41}]  193               [\N{U+41}-z]  193
    [0-\x{110000}] 134
    [0-\A]        107               [\A-z]        107
    [0-\x41]      COMPILES (range)  [\x41-z]      COMPILES (range)
    [0-\k]        COMPILES (range)  [\k-z]        COMPILES (range)
    [0-\8]        COMPILES (range)  [\8-z]        COMPILES (range)

    HIGH, bracket doorway           LOW, bracket doorway
    [0-[:digit:]] 150               [[:alpha:]-z] 150
    [0-[:foo:]]   150               [[:foo:]-z]   130
    [0-[.ab.]]    150               [[.a.]-z]     113
    [0-[=x=]]     150               [[=a=]-z]     113
                                    [[:<:]-z]     130

    order/dissolution: [z-\x41] 108;  [0-\Q\Ea] COMPILES (endpoint a);
    [0-\Q-\E9] 108 (endpoint was `-`);  [0-\E] COMPILES (both literals);
    [0-\E9] COMPILES (range 0-9 forms through the \E)

### 16.2 The rule, and it is simpler than Part I feared

**Evaluate the item at class position exactly as it would be evaluated
anywhere in the class. Any error of its own wins. If evaluation succeeds and
the result is SET-shaped, the range is invalid: 150. There is exactly ONE
deviating cell: at the HIGH endpoint, the bracket doorway's syntactic
pair-open (`[:` `[.` `[=` after the `-`) short-circuits to 150 with no
evaluation at all.**

Every cell above follows. The escape doorway is symmetric across sides — six
error pairs and three range pairs, identical low and high. The bracket
doorway's asymmetry is exactly the one special cell: on the low side `[.a.]`
is evaluated as an ordinary class item (113 — nobody knows a range is coming),
on the high side the pair-open is refused before the name is read (150 beats
130/113). SPEC-FA's original fix was precisely this cell, which is why C3/F8
found it exactly right over 21,396 patterns — the defect was Part I
generalising the cell's law to the other doorway, where the opposite law
(evaluate first) holds.

`\E`/`\Q` transparency at endpoints needs no rule at all: under §13 the range
logic sees only character tokens, and B3/B5/B6/F-x2/F-x3 all follow.

### 16.3 Consequences for the mechanism

- **The SHAPE column loses its only static consumer.** Part I §4.4 justified
  a static shape column by the endpoint caller's need to say 150 without
  parsing (`[:foo:]` raises 130 first). Measured, that need exists only in the
  one deviating cell, and there it is met by a two-byte lexical test at one
  call site — not by a column. Everywhere else the caller evaluates first and
  inspects the RESULT's shape, which is a tag on a value that exists, never a
  guess about one that doesn't. §4.4's worry about 60 unread column values
  dissolves with the column. `pcrec_ext_class_pair_opens` still dies (§9),
  replaced by the one lexical test instead of by a column.
- **Composition with the gate keeps K12 closed.** `[0-\d]` with `classes`
  disabled: the endpoint caller's RESULT ask is demoted to VERDICT; a VERDICT
  for a real, successfully-recognised construct carries its shape; success +
  SET at an endpoint → 150. The verdict is 150 whether or not `classes` is
  enabled — PCRE2's answer, D26 tier 2, and the third "guard is the
  unimplemented-ness" instance (§10.6's defence) is retired the same way as
  the first two.
- **The build-time obligation is a generated differential sweep** of all four
  doorway×side cells (the C3/F8 generator extended to the low side and the
  escape doorway), sized in the tens of thousands through the shim. The 33
  curated cells above are the design evidence; the sweep is the check, and it
  belongs to the §8 rebuild.

> ### REFUTED IN PART (R14 — C1/F1, C1/F4, C1/F5, C2/F1, C2/F2, C2/F12,
> C3/F5, C3/F12; all verified by the author)
>
> **(a) "Exactly ONE deviating cell" is FALSE — there are TWO, and the second
> was printed in §16.1's own table and read as confirmation.** `[:<:]`/`[:>:]`
> are word-boundary assertions legal ONLY as a class's ENTIRE content
> (`pcre2_compliance.md:241` had it right; R9/C3-4 measured it): `[[:<:]]`
> compiles, `[[:<:]x]`, `[x[:<:]]` and `[[:<:]-z]` are all 130. "Evaluated as
> anywhere in the class" they are NOT an error, so the §16.2 rule predicts
> 150 for `[[:<:]-z]`; libpcre2 says 130. C1's generated differential — 71
> items², 5,041 (low, high) pairs, verdicts and shapes taken FROM libpcre2 so
> the predictor shares no source with the predicted — found 71 disagreements,
> every one with `[:<:]` low, and no others. The needed predicate is
> at-content-start AND at-class-end.
>
> **(b) The rule is silent on EVALUATION ORDER, and all 33 curated cells were
> blind to it** — every cell has a plain literal on the non-construct side.
> On the bucket that can see it: `[\d-\A]` is 107 and `[\d-\p{Foo}]` is 147 —
> the HIGH side's own error beats the LOW side's success+SET. The order
> fitting all 5,041 pairs is FIVE steps: low's own error → high's pair-open
> short-circuit → high's own error → either side SET → 150 → scalar
> ordering.
>
> **(c) The "two-byte lexical test" is WRONG and `pcrec_ext_class_pair_opens`
> SURVIVES** (three critics independently). `[0-[:]`, `[0-[:digit]`,
> `[0-[.a]`, `[0-[:alpha]]` all COMPILE — the real condition is the
> predicate's own three rules: two delimiter bytes, next byte not `]`, and a
> matching terminator before end of PATTERN (`ext.c:340-345` lists the exact
> forcing counterexamples). It is struck from §9's and §16.3's deletion
> lists; the deviating cell is implemented BY it. Its 21,396/0 record was the
> evidence; deleting the thing measured while keeping the measurement was
> this section's clearest error.
>
> **(d) The claimed side-symmetry overcounted** (C3/F12): `[0-\c]` is 108 but
> `[\c-z]` COMPILES (`\c` eats the `-`); `[0-\g{1}]` compiles but
> `[\g{1}-z]` is 108. Symmetry holds only for the pairs measured on both
> sides, and delimiter-eating rows break it by construction.
>
> **(e) §16.3's composition bullets contradicted each other** (C2/F1): the
> SHAPE column cannot both dissolve and be consulted for a producer that
> never ran. Correction: RECOGNISE returns `(claim, shape)` — the shape
> column RELOCATED into recogniser output, scoped to the 44 class-reachable
> rows (§14.4's population), which answers §4.4's unread-values objection by
> construction. The demoted VERDICT's payload is
> `(diagnostic, shape, would-PCRE2-accept-this-here)` — the third field is
> what lets the endpoint caller send `[[:alpha:]-z]` to 150 while
> `[[:foo:]-z]` keeps its 130 with `classes` disabled (C2/F12's low-side K12
> case, now the worked example the section lacked).
>
> **(f) The sweep obligation was sized, not designed** (C3/F12): it gains an
> alphabet (every row's syntax × both sides × both doorways, PLUS the
> delimiter-eaters, the lexical rows, and both-sides-construct pairs — the
> two families the cell-generator could not produce), a nonzero per-cell
> floor printed on the PASS line, and an owner (the §8 rebuild inherits
> C1's `probe3.c` method: predictor fed from libpcre2, never from the row).

## 17. Bookkeeping

### 17.1 What Part II supersedes in Part I

    §2.3  position-independent selection      -> §14.1
    §4.1  NULL-port meanings, \b resolution   -> §14.3 (per-port features kept)
    §4.4  the five outcomes' totality         -> §13.2 (five stay; \Q \E (?# leave)
    §5.2  three ASK levels                    -> §15
    §5.4  the gate demotes                    -> §15 (demotes `want`, keeps `may`)
    §6    shape-column endpoint rule          -> §16
    §10.6 the whole-pattern pre-scan          -> §12.2 (lexer in count mode)

§9's byte-identity divergence list is repaired by §14.3: with per-port
features, `[\b]`'s class port is base and never gated, so divergence 1 (the
`tests/base/escapes.rxt:96` regression the design didn't expect) disappears.
Remaining planned divergences: the K10 fix, the K12 endpoint rule, §7.1's new
rows, and bare `\E` becoming a no-op when `quoting` lands — each lands as its
own change with its own pins, never inside the refactor.

> ### CORRECTED (R14 — C2/F11, C3/F15, C2/F3)
>
> **The list above was missing its LARGEST entry, the second consecutive
> draft to miss one** (R13 caught K10's fix missing from the same list): the
> **K13 fix** — the literal-fallback class ports are base scalars, never
> gated, so `[\8]`, `[\12]`, `[\k]`, `[\g]`, `[0-\k]` go from refusal to
> compiling with every name disabled, the exact configuration byte-identity
> is measured in. It cannot be gated off during the refactor, so it must land
> FIRST, before the byte-identity bar is asserted, or be explicitly excluded
> from the corpus the bar runs on.
>
> **And the list itself is now guarded** (C3/F15): a planned divergence
> exists only with a named test that FAILS before the change and passes
> after, and the byte-identity run enumerates its exceptions by test id — an
> exception with no failing-then-passing pin cannot exist, so a fifth
> divergence cannot ride the refactor by being added to prose.
>
> **§5.6 is added to the superseded list** (C2/F3): its "EXT_TERMINATED may
> still leave by ctx_fail" carve-out pointed the wrong way once §16.3 needs
> the NON-producing verdict returned. The rule is now: every terminal answer
> is RETURNED under WANT_VERDICT; `ctx_fail` survives only under WANT_RESULT.
> D33 §5's blast radius carries forward: 23 `ctx_fail` sites in `ext.c` must
> yield a representable diagnostic.

### 17.2 Status and disposition (the D34 ruling on OQ 1 + 13)

    status       fact about PCRE2:   RS_BASE | RS_MODULE | RS_REJECTED |
                                     RS_NOT_OFFERED(option)
    disposition  fact about pcrec:   RD_PLANNED | RD_NEVER

"Requires module 'X'" renders only for RD_PLANNED. RD_NEVER rows (the
backtracking verbs, `(?C)` callouts, the `LIMIT_*` family — the constructs
`pcre2_compliance.md` already calls architecturally excluded) say so in the
diagnostic instead of promising a module. **This is the K14 fix**, and it puts
the fact in one home: the compliance survey's prose becomes a generated view
of the column, or the column is checked against it — either direction, but
one source. The exact diagnostic wording is tier 3; that it does not promise
is tier 2.

> ### CORRECTED (R14 — C2/F5, C2/F6, C2/F7, C2/F8)
>
> Four repairs, all applied:
>
> - **The enum is renamed `ROADMAP_PLANNED`/`ROADMAP_NEVER`** — `RD_*` is the
>   shipped diagnostic-disposition enum (`internal.h:263`) that §5.3/§5.5
>   still cite, and the verb row would have carried `RD_MODULE` (promises a
>   module) beside roadmap-NEVER (must not) with nothing arbitrating. The
>   diagnostic vocabulary gains the missing entry — *real, refused, names no
>   module* — so §5.5 stays total.
> - **Illegal cells are stated**: `RS_BASE` × either roadmap value, and
>   `RS_REJECTED × ROADMAP_PLANNED`, are table-check errors;
>   `RS_REJECTED × ROADMAP_NEVER` is the required pairing, not a choice.
> - **Disposition lives on `VerbName` too, with the row's value as default**
>   (C2/F5): `RK_VERB` is ONE row for fifty names spanning both dispositions
>   — `(*COMMIT)` is NEVER while `(*pla:…)`/`(*atomic:…)` are the
>   lookaround/atomic constructs in verb spelling. A per-row column cannot
>   separate K14's own repro set. And **ROADMAP_NEVER demotes `want`
>   INDEPENDENTLY of the enabled set** — when module `verbs` lands and is
>   enabled, that clause is the only thing standing between `(*COMMIT)` and
>   WANT_RESULT.
> - **`RS_NOT_OFFERED` is DEFERRED to the bound-mode document** (C2/F6): "real
>   under an option pcrec does not implement" packs a roadmap fact into the
>   PCRE2-facts column — the category error K14 names, inside K14's fix. The
>   likely split ("real under option X" as a status; "pcrec will not offer X"
>   as roadmap) is recorded for that document, not decided here.
> - **The one-source direction is CHOSEN: checked, not generated** (C2/F8).
>   Generating the survey's prose from the column would retire the
>   independent home that CAUGHT K14 — a control sharing a source with what
>   it controls. `compliance_section.py --names` grows a pass asserting
>   prose-OUT-OF-SCOPE ⇔ ROADMAP_NEVER, both directions.

### 17.3 Invariants handed to the §8 rebuild (D27 author; not checks, inputs)

**REBUILT AFTER R14** (C3's audit, F1/F7/F8/F9/F10/F11/F14: the first version
was "nine one-line invariants... six of which cannot fail in the direction
the design's own gaps produce"). Each entry now names its ORACLE, its
POPULATION, and its SABOTAGE — and per C3/F14, what the D27 author receives
is these entries plus the PROBES behind them, never this document's
reasoning. Where an entry says "libpcre2", the probe is external; where it
says "harness", both sides are computed outside the handler under test.

1. **Enabled-set isolation, mechanical.** Recognisers and extent scans live
   in translation units that do not link the enabled-set symbol; checked by
   `nm` in the build. Oracle: the linker. Sabotage: add one reference.
2. **The capture count, external.** The count-scan's group count equals
   LIBPCRE2's capture count over generated patterns — compiling AND
   non-compiling, because an undercount manifests as a spurious err-115
   refusal (the non-compiling side is the failure direction). Population
   printed per generator family; includes `(?<n>`/`(?<=` splits, verb and
   callout bodies, `(?|` branch maxima with hidden `|`, scoped `(?n)`, and
   quote-mode edges (`(\Q?\E:a)` captures).
3. **LEXICAL membership, behavioural.** A row is LEXICAL iff `a<syntax>*`
   compiles and the quantifier binds the preceding atom, per libpcre2 —
   swept over all 100 rows, so a fourth lexical construct is FOUND, not
   assumed away. (Today: exactly three.)
4. **Class-position expectation, external.** For the 44 class-reachable rows
   (41 esc + 3 class-bracket): the two-valued expectation column (compile-as-
   what / error N) matches libpcre2 on the row's class probe SET (including
   endpoint-adjacent probes for delimiter-eaters). Populations printed per
   bucket with a ratcheting floor; the 56 group/verb rows carry no value.
5. **The digit rules, all three clauses.** Single digits `\1..\9` never fall
   back to octal; runs beginning 8/9 are backreferences at any length and
   any count; octal fallback re-reads at most three octal digits and
   overflow is err 151. Oracle: libpcre2 over a generated digit-run × count
   grid.
6. **The cursor rule.** `cx->pos` moves only under WANT_RESULT — harness
   computes both sides, total over rows, sabotage is one line. (R14: "the
   best of the nine"; unchanged.)
7. **Gate equivalence, with a real population.** Disabled-feature verdicts
   equal enabled-feature verdicts, varied over the WHOLE enabled set (all
   on / all off / one inverted), with a per-name compared-pair count and a
   ratcheting floor printed on the PASS line — an empty population is
   indistinguishable from a pass otherwise, and at landing the population
   IS empty until the first module flips (C4/F4's remedy, carried this
   time). Membership ("whose validity PCRE2 decides") is computed by asking
   libpcre2, never hand-listed.
8. **The endpoint sweep, with an alphabet.** Every row's syntax × both sides
   × both doorways, PLUS delimiter-eaters, lexical rows, and both-sides-
   construct pairs; per-cell floors printed; predictor fed from libpcre2
   (C1's probe3.c method). The five-step order and both deviating cells are
   in scope by construction.
9. **Every feature toggles** (§3.1's check 8) — subsumed into 7's population
   machinery; kept named because it is the check with no analogue today.
10. **Quantifiability.** The per-row `quantifiable` fact matches libpcre2's
    `a<syntax>*` verdict, all 100 rows (new; §13's R14 block).


## 18. State after R14, and what is open for Frank

R14 ran the session Part II was written (three lenses, ~5,400 probes,
`docs/reviews/2026-08-11-r14-part2.md`), every load-bearing refutation was
re-verified by the author before being applied, and the corrections are inline
above. The honest summary:

**What now stands, corroborated rather than asserted:** one table; names;
per-port recognition (every cell tried, including fallback tails and
class-side digits at every count); explicit literal-fallback ports with the
ten NULL rows mode-invariant; the lexical-mode reading at atom/class-item
positions (34/34) with the set {`\Q…\E`, `\E`, `(?#…)`} behaviourally exact
(27 candidates, no fourth); the endpoint CORE rule at the escape doorway
(every constructible cell); `pair_opens` as the surviving deviating-cell
predicate; the cursor rule; the `want`×`may` DIAGNOSIS.

**What R14 corrected, now inline:** two deviating endpoint cells and a
five-step evaluation order (§16); the three-clause digit rule (§14.2); the
count-scan as a group-header sub-parser with a per-row `captures` fact, and
the withdrawal of "backrefs can land alone" (§12); quote-mode position
scoping and the quantifiability axis (§13); E127 from the scan, not the gated
parser, plus `want`×`may` legality rules (§15); the guarded divergence list
and §5.6's supersession (§17.1); `ROADMAP_*`, per-VerbName disposition, the
checked one-source direction, and `RS_NOT_OFFERED`'s deferral (§17.2); the
rebuilt invariant list (§17.3).

**Open for Frank — these are decisions, not desk-fillable holes:**

1. **The migration order.** The always-live layer is honestly a group-header
   sub-parser plus verb/callout body extents plus a nesting-aware branch
   scanner — code for two ROADMAP_NEVER families among it. That is
   effectively a LEXER/SCANNER milestone that must precede `backrefs`.
   Options: accept it as the first module-era milestone; or defer backref
   VALIDITY (keep refusing `\1..\9` until the scanner exists) and land
   simpler modules first. The second keeps the migration small at the cost
   of `backrefs` staying refused longer.

   > **RESOLVED (Frank, 2026-08-11 fifth session): NEITHER — there is no
   > scanner, because PCRE2's digit semantics do not need one.** Frank
   > challenged the scanner ("I recall you arguing against a scanner" — the
   > original argument was right), and eighteen targeted probes plus a
   > 2,931-probe generated sweep (predictor stated before running; backref-ness
   > read back via `PCRE2_INFO_BACKREFMAX`, zero disagreements) established
   > the model:
   >
   >     leading '0'                  octal, always
   >     single digit 1..9            backref, always; VALID iff TOTAL count >= d
   >     multi-digit, leading 1..7    backref iff RUNNING count >= n,
   >                                  else OCTAL — the total is IRRELEVANT
   >                                  (^\12(a)x12$ matches "\n"+12 a's: octal)
   >     multi-digit, leading 8..9    backref, always; VALID iff TOTAL >= n
   >                                  (\89 with 89 groups AFTER it compiles)
   >
   > The RUNNING count is ordinary parser state. The TOTAL count is needed
   > only for VALIDITY of already-decided backrefs — and PCRE2 reports every
   > structural error FIRST (`\1[` is 106, `\1(` 114, `\1a**` 109, `\1(?P<n`
   > 142, `\1\q` 103; 115 surfaces only when the rest parses cleanly), which
   > is exactly the behaviour of **DEFERRED RESOLUTION**: parse single-pass
   > with the real parser, record pending references (offset + number), check
   > them against the final count at end-of-parse. Structural errors longjmp
   > out before the end-check runs, so the precedence matches by
   > construction. `(?(n)` forward references measured to work the same way
   > (`(?(1)a|b)(x)` compiles; `(?(2)a|b)(x)` is 115).
   >
   > Constructs pcrec refuses terminate the compile, so their count
   > contribution never matters — the "always-live sub-parser including
   > ROADMAP_NEVER families" requirement evaporates, and **"backrefs can land
   > alone" is TRUE again** under this design (`\1(?<n>a)` with
   > `named-groups` disabled refuses at `(?<n>` with the right module name).
   > `plan.md`'s [MOD-STATE] note had already recorded the running/validity
   > split; Part II walked past it. §12.2's count-scan is WITHDRAWN in favour
   > of: running count in `Ctx` + a pending-references list + one end-of-parse
   > check. Consequence for §15: the `(?(` terminal-answer question REOPENS
   > (the scan was its designated answerer) — see decision 2.
   >
   > Probes: `probe_defer.c`, `probe_digit_sweep.c` (session scratchpad;
   > outputs quoted in R14's addendum). Pending: a quick adversarial pass on
   > this block before the plan builds on it — it is a same-day desk
   > conclusion, and this project has a fresh catalogue of what those are
   > worth.
2. **Does `may` survive?** — REOPENED IN A NEW FORM by decision 1's
   resolution: the count-scan that was to serve `(?(`'s exact E127/E154
   terminal answer no longer exists, so the question is now *what answers
   `(a)(?(1)x|y|z)` while `conditionals` is disabled*. Three options: (a)
   keep `may` — VERDICT parses the body with the real parser in a
   structure-only mode (gate-demotion propagating into sub-parses), which is
   real machinery in the trial-mode direction; (b) a bounded lexical
   top-level-`|` counter used only by `(?(`'s VERDICT (paren depth + the
   lexer's existing hidden-`|` awareness — much smaller than the dead
   scanner, but a second walker for one row); (c) LEFTMOST-REFUSAL POLICY:
   while `conditionals` is disabled, `(?(` answers "requires module
   'conditionals'" without reading the body — the `(*FAIL)*` precedent,
   already pinned in `tests/reject/` as a deliberate non-defect — and the
   exact E127 arrives for free from the real parse when the module lands.
   (c) is today's shipped behaviour, costs no machinery, never miscompiles,
   and makes `may` unnecessary; its price is that R13/C1-F2's E127
   over-promise stands as a DOCUMENTED POLICY until `conditionals` lands
   rather than being fixed by mechanism. If (c), collapse to three `want`
   levels + the cursor rule, with the revisit trigger recorded: a terminal
   answer REQUIRED to depend on a full sub-parse while its module is
   disabled reintroduces the axis.
3. **Where `quantifiable` and `captures` live** — row columns (two more
   hand-written facts, each with an external sweep behind it) is the working
   assumption; an alternative is deriving both from one machine-readable
   grammar classification of the `(?` header, which is more structure than
   the table has anywhere else.
4. **The K13-fix sequencing** (§17.1's R14 block): land it before the
   byte-identity bar, or exclude its twelve patterns from the bar's corpus.
   Landing first is cleaner and it is a shipped-bug fix Frank has already
   agreed with in substance.
5. **The bound-mode document** now owns: the full option sweep (OQ 2), the
   `RS_NOT_OFFERED` split, and the `EXTRA_BAD_ESCAPE_IS_LITERAL`
   mode-dependence of the fallback partition (18 cells move; the NULL ten do
   not).

**Process note, recorded because it is now a pattern with three instances:**
R13 refuted Part I's claims that were measured on buckets that could not
falsify them; Part II then did it twice more (§16.1's literal-sided cells,
§13.1's atom-only cells), and in one case the falsifying measurement was
already printed in the document's own table. The next design pass on this
project should REQUIRE, for every stated rule, one probe chosen because the
rule could fail on it — before the rule is written down. R14's generated
differential (predictor fed from the oracle, never from the row) is the
method that found what three curated tables missed.
