# Design proposal — string selectors for the construct registry (SR-9)

**Status: REVIEWED AND SUPERSEDED (R6, 2026-08-10). Do not build §2.** Build the
`byte + tail` design in §7 instead. Nothing is built yet either way; §7 needs
Frank's approval and PC-3 before it.

---

## 0. R6 verdict — three design critics, all against §2 as written

The diagnosis in §1 is right. The mechanism in §2 is not, and two of its load
-bearing claims were refuted by measurement rather than argument.

**Killed the "one uniform rule" premise:**

- **The deciding information is not always at the doorway. Twice.** `(?(R)` is a
  recursion condition or a named-group condition depending on whether the
  pattern declares a group named `R` — *possibly later in the pattern*. And
  `\12` is octal or a backreference depending on the running capture count. No
  lookahead resolves either. The bound this forces is worth stating plainly and
  is now the honest limit of the whole table: **the registry can identify a
  DOORWAY and name a MODULE; it cannot always identify the CONSTRUCT.**
- **`RF_WORD` would ship wrong.** §2.3 needs the verb terminator set to be
  global. It is per-verb: `(*ACCEPT:x)` compiles, `(*CR:x)` does not;
  `(*LIMIT_DEPTH=1)` compiles, `(*LIMIT_DEPTH:1)` does not.
- **`(*` is TWO name tables**, selected by the case of the first byte, with two
  different "not recognised" diagnostics.
- **`(?C1` vs `(?C{x}` is not a distinction at all** — both compile as callouts.
  One of the three cases §2 cites to motivate itself does not exist.

**Killed the cost argument:**

- **"The base tier performs zero lookups" is FALSE, today, before any of this.**
  Measured with an instrumented build and confirmed independently: `abc` and
  `(?:ab)+` cost 0, but `[abc]` costs 1 and `[a-z]+@[a-z]+\.[a-z]{2,4}` costs 3,
  because the class-bracket doorway is on the base-tier path. `(?:` costs zero,
  not "one, once". The claim stood in six places and **SR-5 was scheduled to
  encode it**. Corrected everywhere; SR-5's assertion rewritten as a bound.
- Under §2 that same path would go from 3 int compares to ~31 `strncmp` calls
  per character class, on the one doorway the base tier actually reaches.

**Killed the advertised structural win:** moving the catch-all row to first
position leaves dispatch unchanged, so the "catch-all must be LAST" invariant
§2.2 deletes was already vacuous — while the duplicate-selector check would be
weakened and the 255-byte sweep would silently narrow. Net movement in
checkable invariants: negative.

**What survives, and is kept:** §1's diagnosis; §2.4's `^`-in-the-name idea
(sound, and correctly caveated); §2.5's one-generator-two-spellings argument
(which does not require 28 rows to get); and §3, which the cost critic asked be
kept verbatim as the specification module `classes` will need.

---

The registry (D24, `src/parse/registry.c`) keys every non-base construct on a
single byte. This proposes keying on a STRING instead, with longest-match
lookup and an optional word-boundary requirement. Byte-keyed rows become
length-1 selectors and do not change.

---

## 1. The problem, as measured rather than argued

R5's tests critic put it best: **one byte of lookahead is all any sweep in this
repo has.** Two sabotages went undetected by all seven suites:

- a branch on `(*NO_S…`, four bytes into a verb name;
- a branch distinguishing `(?P=` from `(?P<`.

Both are real PCRE2 distinctions that pcrec's table cannot express, so nothing
can check them. `registry.c`'s header already records ONE instance of this —
`\N{U+hhhh}` sharing the `N` selector with bare `\N`, called a "known
outstanding second home". It is not one instance. It is the shape of every
doorway that is keyed by a byte while PCRE2 keys by a string.

Sorted by what actually discriminates (all measured against libpcre2 10.46):

| doorway | discriminator | evidence |
|---|---|---|
| `(*` | **whole word** | `(*ACCEPT)` compiles; `(*ACC)` → "(*VERB) not recognized"; `(*MARKx)` → not recognized, `(*MARK:x)` compiles |
| `[:…:]` | **whole name** | 14 POSIX names; `[[:foo:]]` → "unknown POSIX class name" |
| `(?` | **mixed** | `=` `!` `>` `#` are byte-decided; `(?P<` `(?P=` `(?P>` are three constructs on one byte, as are `(?<=` `(?<!` `(?<name>` and `(?C1` `(?C{x}` |
| `\` | **mostly byte** | genuine exception measured: `\N`, `\N{U+0041}` and `\N{}` produce three different PCRE2 outcomes |

The `\N` family, verbatim from the oracle:

    \N            -> compiles (any char except newline)
    \N{U+0041}    -> "\N{U+dddd} is supported only in Unicode (UTF) mode"
    \N{}          -> "PCRE2 does not support \N{name}"
    [\N]          -> "\N is not supported in a class"

Three constructs, one selector byte. Today's table can describe one of them.

## 2. Proposal

### 2.1 The selector becomes a string

    const char *sel;    /* was: int sel */

A byte-keyed row is a length-1 selector and reads identically (`"d"` for `\d`).
`REG_SEL_ANY` becomes the **empty string**, which falls out of the lookup rule
below rather than needing its own case.

### 2.2 Lookup is longest-match over the text at the doorway

    const RegRow *pcrec_registry_find(RegKind k, const char *at, size_t avail);

Scan the rows; among those whose selector is a prefix of the remaining pattern
text, take the LONGEST. This subsumes three mechanisms that are currently
separate or absent:

- byte selectors — length 1, unchanged;
- sub-construct splits — `N{U+` (4) beats `N{` (2) beats `N` (1);
- the catch-all — the empty selector matches everything at length 0, so it is
  automatically the shortest match and every real row outranks it.

**This deletes an invariant rather than adding one.** `registry_check.c`
currently enforces "the catch-all row must be LAST, or it shadows rows after
it" — an ORDERING constraint, i.e. a property of how the array is written.
Longest-match replaces it with a total order on match length, which is a
property of the data. Ordering bugs stop being possible instead of being
checked for.

### 2.3 A row may require the match to end at a delimiter

    unsigned flags;   /* + RF_WORD */

`RF_WORD` means: the match counts only if the next byte is one of the
construct's terminators. This is what makes verbs work, and it is measured, not
assumed — `(*MARK:x)` compiles while `(*MARKx)` is "(*VERB) not recognized", so
`MARK` must be followed by a delimiter. Verb terminators are `)`, `:` and `=`
(`(*ACCEPT)`, `(*MARK:x)`, `(*LIMIT_DEPTH=1)`, all measured).

Without `RF_WORD`, longest-match alone would let a row for `MARK` swallow
`MARKx`. With it, one rule — longest match, optionally word-bounded — covers all
four doorways.

### 2.4 POSIX class names become rows, and `^` is part of the name

**This is Frank's idea.** pcre2syntax.html lists the negated form as its own
notation, alongside the positive one:

    [[:xxx:]]    positive POSIX named set
    [[:^xxx:]]   negative POSIX named set

and gives 14 names: `alnum alpha ascii blank cntrl digit graph lower print
punct space upper word xdigit`. So PCRE2's own documentation models `^` as part
of the SYNTAX. Frank's proposal is to model it as part of the NAME instead, so
that `^alpha` is simply a name and negation needs no handling anywhere.

**Be precise about what the measurement does and does not establish.**
`[[:^^alpha:]]` gives "unknown POSIX class name" rather than a syntax error —
but that outcome is consistent with BOTH models (name `^^alpha` unknown, or
strip one `^` and find `^alpha` unknown). The probe does not distinguish them,
and I should not claim it does. What it does establish is that the
name-as-written model is not CONTRADICTED, and the argument for it is design
economy rather than fidelity.

The economy is real, and the precedent is already in the table: pcrec gives `\d`
and `\D` separate rows rather than one row plus a negate flag. `alpha` and
`^alpha` are the same relationship, so 14 names become 28 rows and no negation
logic exists anywhere.

Names are case-sensitive (`[[:AlPhA:]]` → unknown POSIX class name), and
"recognize only ASCII characters by default, but some of them use Unicode
properties if PCRE2_UCP is set" — a per-name option dependence that the
`engines`/module columns will eventually need to carry, and that DD-1/M5 owns.

### 2.5 The payoff: one bitmap mechanism, two spellings

`[[:digit:]]` and `\d` denote the SAME 256-bit membership set. Today they would
be two code paths in module `classes` that can disagree — which is the `\v`
failure mode (a declarative table and an imperative switch disagreeing ten lines
apart) at a larger scale, with 14 more chances to make it.

With name-keyed rows both spellings are rows pointing at ONE name→bitmap
generator. `\D` and `[[:^digit:]]` likewise. **This is the first real customer
for the handler field**, which D24 has now deferred twice for want of one.

## 3. What the measurements REFUTED

The strawman included gating recognition on an approved character set, so that
a name outside the set would fall through to ordinary class members. **PCRE2
does not do this.** Measured:

    [[:a b:]]    -> unknown POSIX class name     (space is in the "name")
    [[:a-b:]]    -> unknown POSIX class name
    [[:al_pha:]] -> unknown POSIX class name
    [[:2:]]      -> unknown POSIX class name
    [[::]]       -> unknown POSIX class name     (the EMPTY name is a name)
    [[:]]        -> compiles as literals         (no terminator: `]` aborts the scan)

Recognition is purely STRUCTURAL — `[:` … `:]`, with the scan aborting at an
unescaped `]` or a nested `[:` — and the name is validated afterwards. A
charset gate would make `[[:a b:]]` compile as literals, which is a divergence
we would be introducing on purpose.

**Consequence for the design:** the class-bracket doorway needs an outcome the
registry vocabulary does not currently have — *recognised structurally, but the
name is unknown* → "unknown POSIX class name". That is distinct from "no row
matched" (not a construct at all) and from `RS_MODULE` (known, unimplemented).
Same for `(*NOTAVERB)` → "(*VERB) not recognized".

This is a schema addition, and it is the part of the proposal I am least sure
of. See open question Q1.

## 4. What this does and does not fix

**Fixes:**

- K3 and K4 dissolve rather than being patched. You cannot RECOGNISE `[:alpha:]`
  without scanning for `:]`, so the terminator condition stops being an
  `RF_CLASS_DELIM` flag and becomes intrinsic to the lookup. The flag-based fix
  sketched in K3/K4 would be thrown away by this work, so **it should not be
  written first.**
- The two invisible sabotages of R5's F-12 become expressible, therefore
  testable.
- The `\N`/`\N{U+` second home closes.
- The catch-all ordering invariant disappears.

**Does not fix:**

- The circularity R5 measured. A row with a plausible-but-wrong module name is
  still caught by nothing except a hand-written entry. **More rows means more
  unverified claims** — 28 POSIX names and several dozen verb names, each with
  a semantics note written by someone. SR-1 declined per-verb rows for exactly
  this reason ("naming forty verbs that nothing distinguishes and no test
  exercises would be fiction"). That objection is not answered by this design;
  it is answered by PC-3, and **PC-3 should land first.**

## 5. Cost

- **Lookup**: `strncmp` per row instead of an int compare, over more rows
  (67 → ~130 with POSIX names and verbs). Measured baseline: a full 39-row miss
  is 33.6 ns against a 90 µs floor for the cheapest compile pcrec can do.
  Frank's standing steer is not to optimise this. SR-6 remains the forcing
  function — doorway hits go from once-per-compile to once-per-construct then.
- **The base tier still performs zero lookups.** Nothing here touches that; the
  base switch runs first and returns. SR-5 still guards it.
- **`registry_check.c`** loses the ordering check, keeps everything else, and
  gains sweeps that can vary more than one byte.
- **Signature change** to `pcrec_registry_find`. SR-7 already needs one (for the
  flavour argument it cannot express today). Doing both at once is cheaper than
  doing them separately.

## 6. Open questions for the critic round

- **Q1.** Is "recognised but unknown name" a new `RegStatus`, a new `RegDiag`,
  or a per-kind fallback row? A fallback row is tempting (it is what
  `REG_SEL_ANY` does today) but the diagnostic differs per doorway and the
  outcome is not "requires module X".
- **Q2.** Does longest-match introduce an ambiguity the byte scheme did not
  have? Two rows with the same selector is already an error. A row whose
  selector is a PREFIX of another is now meaningful rather than an error, so
  the duplicate check must be refined rather than kept.
- **Q3.** Should `(?` sub-constructs (`P<`, `P=`, `P>`, `<=`, `<!`) become rows
  NOW, or with their modules? They are the highest-value rows for `--explain`
  and the compliance doc, and the lowest-value for the parser, which rejects
  them all identically today.
- **Q4.** Is the verb terminator set exactly `)`, `:`, `=`? Measured for four
  verbs. PCRE2's full verb list is unexamined (R5 spec critic's own
  not-covered list). **And pcre2syntax.html lists `(*:NAME)` as a synonym for
  `(*MARK:NAME)` — a verb whose NAME IS EMPTY.** Under `RF_WORD` that is an
  empty selector requiring a `:` terminator, which collides with the empty
  selector's other proposed meaning (the catch-all, §2.2). Two different things
  would both be `""`. This needs resolving before the scheme is coherent, and I
  do not have a clean answer.
- **Q5.** Does this make the class-open vs class-inner distinction (the fifth
  doorway kind, `RK_CLASSOPEN`) unnecessary, or does it still need one? PCRE2
  still uses a different message per position.
- **Q6.** Sequencing. Proposed: PC-3 → K5/K6 → this. Is there a reason to take
  K3/K4 before it, given the flag fix would be discarded?

---

## 7. THE ADOPTED DESIGN — keep the byte key, add an optional `tail`

Proposed by R6's cost critic, **built and measured as a working prototype**
(~60 lines across three files, in a scratchpad copy; the repo was not touched).
This is §1's diagnosis taken at its measured size.

`RegRow` gains ONE field:

    int         sel;    /* unchanged: the deciding byte, or REG_SEL_ANY */
    const char *tail;   /* NULL, or the bytes that must FOLLOW sel */

and lookup becomes longest-tail-wins *within the selector byte's bucket*:

    const RegRow *pcrec_registry_find(RegKind k, const char *at, size_t avail);

Five new rows. Sixty-seven existing rows unchanged apart from a `NULL` the
macros supply. It fixes every divergence the byte key cannot express today:

    (?P<n>a)      (?P...) requires module 'named-groups'    unchanged
    (?P=n)        (?P...) requires module 'backrefs'        FIXED
    (?P>n)        (?P...) requires module 'recursion'       FIXED
    \N            \N requires module 'classes'              unchanged
    \N{U+0041}    \N requires module 'unicode-props'        FIXED
    \N{}          \N{name} is not supported                 FIXED (RS_REJECTED)

Every other diagnostic in the table is byte-identical.

### Why it beats §2 on every axis that was measured

| | §2 as proposed | byte + tail |
|---|---|---|
| rows | 67 → ~130 | 67 → 72 |
| new hand-written unverifiable notes | ~68 | 5 |
| `parse.c` call sites changed | 6 | **0** |
| schema fields added | 5 | 1 |
| base-tier class lookup | 3 rows → ~31 | **3 rows, unchanged** |
| duplicate-selector check | weakened to strings | `(sel, tail)` pair — **stronger than today** |
| 255-byte sweep | silently narrows | **provably identical** (verified: 0 divergences over 4 kinds × 255 bytes) |
| Q4 (`(*:NAME)`) | "no clean answer" | never arises |

### What it deliberately does NOT do, stated rather than papered over

- **No POSIX name rows and no verb name rows.** Under D18 they have not earned
  an axis: no code distinguishes them and no test exercises them. They arrive
  with modules `classes` and `verbs` — which is what SR-1 decided, and R5's F-12
  does not overturn it.
- **No `RF_WORD`.** The terminator set is per-verb, so the flag would be wrong
  on arrival. It needs a per-row terminator set designed against a full measured
  survey of PCRE2's verb list.
- **It does not close R5's F-12 verb sabotage gap.** `(?P=` vs `(?P<` becomes
  catchable; `(*NO_S…` does not. That is the honest cost of the cheaper design.

### Sequencing, corrected by the critics

§4 said K3/K4 should wait because the flag fix "would be thrown away". **That
premise is wrong** — K4 is untouched by the selector scheme, and its structural
scan has to exist under any design. Both other critics argued the reverse, and
the testability one gave the better reason: K3/K4-fixed gives this change a
correctness target at the doorway it changes most. Deferring means correctness
there is attested only by four pinned lines changing colour, and a colour change
says something moved, not that it moved somewhere right.

**Adopted order: K5/K6 (miscompiles) → PC-3 against the CURRENT 67-row table →
K3/K4 → this.** PC-3 first is what makes the 67-row baseline externally
verified, so this becomes a change against a known-good reference rather than
against 67 rows nobody has checked.

## 8. Independent actions this review produced, already done

1. **Corrected "the base tier performs zero lookups" in six places** and rewrote
   SR-5's assertion as a measured bound. This was the review's highest-priority
   item: a documented invariant that is false, which a scheduled step was about
   to encode.
2. **Corrected PC-3's check (b), which had the polarity backwards** and as
   written would have passed every fabricated row it exists to catch. An
   `RS_MODULE` row's `syntax` must COMPILE under libpcre2 — a row naming a
   construct PCRE2 does not have fails there. Check (a) strengthened to require
   a matching error identity.
3. **Corrected `registry_check.c`'s catch-all justification** — the row does not
   shadow rows after it; the invariant is readability, not correctness.
4. **Added the cheap pins**, all valid whether or not §7 is ever built:
   `[[:foo:]]`, `[[::]]`, `[[:AlPhA:]]`, `(*MARKx)`, `(*NOTAVERB)`; the last
   coverage floor made exact; and `pinned()` given an expected-message argument,
   since a verdict-only pin says something moved, not that it moved rightly.
5. **Found one new divergence while doing (4):** `[[:]]` — PCRE2 accepts it (no
   `:]` terminator, so `[` and `:` are ordinary members) and pcrec rejects it.
   Same family as K3/K4, previously unrecorded, now pinned.

## 9. T-12 — the payoff neither §2 nor §7 claims, and it is not about selectors

The testability critic found the strongest argument in this whole review, and
the proposal does not make it.

Every finding in R4, R5 and R6 runs into one wall: **a check that iterates what
EXISTS cannot see what is MISSING.** The hand-written manifest is the only
answer the project has, and it covers 8 rows.

For the two NAME-keyed doorways that wall comes down, automatically:

    for each candidate name s, from a source OUTSIDE pcrec
        (pcre2syntax.html, generated, or fuzzed — never the registry):
      pcre2_ok = libpcre2 compiles "(*" + s + ")"
      assert  pcre2_ok  =>  pcrec says "requires module"
      assert !pcre2_ok  =>  pcrec says "not recognized"

Delete the `ACCEPT` row: detected. Misspell it `ACCPET`: detected. Shadow it
with a longer row: detected. Add a row for a verb PCRE2 does not have:
detected. **None of those is detectable by anything in this repo today, at any
effort.** It is the first mechanism the project has had that scales coverage
without scaling human transcription.

**But read what it actually depends on.** Not string selectors — Q1. The check
above collapses the moment the catch-all answers for every name, because then
pcrec says "requires module 'verbs'" for `(*NOTAVERB)` too, which is exactly the
over-promise R6 measured (F22) and exactly what happens today. What unlocks it
is a distinct *recognised-but-not-a-known-name* outcome. That is Q1, and the
cost critic's own comparison table lists Q1 as **orthogonal to both designs.**

**Consequence for sequencing, and it strengthens the adopted order rather than
changing it:** Q1 + PC-3 are the load-bearing pair, and both are buildable
against today's 67-row table. The selector shape is secondary and can follow.
Anyone tempted to reach for §7 first because it is the interesting change should
read this section again.
