# [M5.0] UTF-8 — design

**STATUS: PROPOSED. Nothing in this document is built.** No file under `src/`
or `tests/` is touched by the lane that wrote it. A D6 adversarial panel
reviews it before any [M5.0] implementation wave opens, and §12 is this
document's own list of where to attack, written before the panel rather than
after.

The charter is `docs/dev/plan.md`'s `[M5.0]` row, its `CROSS-NOTE`, and the
`[DD-12]` and `[DD-1]` rows it names. The architecture being instantiated is
`APPROACH.md` §4 and §10.3; the seam being consumed is `[M5-SEAM]`/D58, which
already shipped.

---

## 0. How to read this

### 0.1 Claim marking

Every claim below carries one of four marks, and the mark is load-bearing —
a panel's first job is to attack the ones that are not `MEASURED`.

| mark | means |
|---|---|
| **MEASURED** | a probe ran and its verbatim output is archived under `utf8_measurements/out/`. The cell names the file. |
| **STRUCTURAL** | true by the shape of code quoted in this document, verifiable by reading `src/` — not a measurement, but not a judgement either. |
| **ARGUED** | a derivation from measured facts. The premises are marked; the step is mine. |
| **ASSERTED** | a design choice or an unverified belief. If it is load-bearing it is also in §12. |

**Every MEASURED-against-libpcre2 claim in this document was measured against
libpcre2 10.46 on the OLD BOX**, which is the project's reference oracle. It
was NOT measured against this Mac's library. §0.4 explains why that mattered
more than it usually does.

### 0.2 The design in one paragraph

The parser stops producing a 256-bit byte bitmap and starts producing a
**sorted list of code-point intervals**; the encoding becomes a **lowering
instance** that turns that list into byte-level NFA fragments, and the byte
backend's instance is the identity map it already is. Everything downstream —
subset construction, minimisation, both emitters, every prefilter — stays
byte-wise and never learns that UTF-8 exists. `\p{...}` is a producer of
intervals and is therefore **not gated on the encoding at all**; case folding
is a **closure over the interval set** applied in the one constructor that
already applies it (D23), before negation, exactly as today. The seam gains no
new interface: its four residual entries get UTF-8 bodies under their existing
signatures, and the one place the design has to change something outside the
backend is an **analysis**, not a mechanism — the lookbehind width rule is
measured to be in CHARACTERS where pcrec computes BYTES, and under the byte
encoding nothing can tell those apart.

### 0.3 Measurements this lane produced

Seven probes, each archived with a provenance header naming the host, the
libpcre2, the python and the options word that produced it.

| file | what it settles | oracle |
|---|---|---|
| `out/premises.txt` | what pcrec refuses today; the code this design argues against, quoted | pcrec on HEAD |
| `out/invalid_utf.txt` | charter (i)'s invalid-UTF decision, three modes | libpcre2 10.46 |
| `out/uprops.txt` | charter (ii): which `\p` spellings 10.46 accepts; the UTF-gating question; the interval census | libpcre2 10.46 |
| `out/caseless.txt` | charter (iii): simple vs full folding, the closure, fold-before-negate | libpcre2 10.46 |
| `out/width.txt` | charter (iv): the lookbehind width UNIT, and the seam's other entries | libpcre2 10.46 |
| `out/sizing.txt` | charter (v): byte-automaton state counts against pcrec's caps | pure construction |
| `out/divergence.txt` | charter (vi): the D27 goal-facts list, 28 rows four ways | libpcre2 10.46 + python |
| `out/divergence_local_py311.txt` | the same 28 rows on the OTHER python this project uses | libpcre2 + python 3.11 |

### 0.4 THE ORACLE PROBLEM THIS LANE HAD, and why it is worth a section

Every earlier design gate in this house ran its probes on the machine that had
the reference libpcre2. This one could not: **the reference is 10.46 and it is
on the old box**, while the lane runs on a Mac whose library is a different
version. PC-3 measured the two diverging on the same day this lane opened.

So every oracle probe here executes REMOTELY, and the mechanism is worth
stating because a panel should attack it before it attacks any number that
came through it:

- `probes/bundle.py` embeds the borrowed oracle chain — `pcre2_ctypes.py` →
  `br_oracle.py` → this lane's `u8_oracle.py` — **verbatim**, as the `repr()`
  of each file's source, and shims `importlib` so the same import chain runs
  on the far end against the same bytes. **The binding is borrowed, not
  copied**, which is the rule `br_oracle.py`'s own header states and
  `la_oracle.py` repeats: *a lane that re-implements the binding it is
  checking cannot detect that the original moved*. Edit `pcre2_ctypes.py`
  tomorrow and the next bundle carries the edit.
- The payload arrives on **stdin**. Nothing is written on the old box — no
  temp file, no checkout — which is also what keeps the scope mandate clean
  on a machine this lane does not own.
- `probes/archive.sh` is the ONLY writer of `out/` (R30 M7's rule) and its
  header names the **oracle host** as well as the usual commit/version block,
  because for this lane an archived number is meaningless without it.

**Three instrument defects came out of this, and each is recorded at its own
site rather than only here** (the full list is `out/CLAUDE.md`):

1. **A transcript that printed a pattern nobody ran.** `probe_caseless.py`
   rendered its patterns with `.decode("latin-1")`, so the two UTF-8 bytes of
   U+00DF appeared as `Ã` plus a control. A reader cannot be expected to
   notice that the *pattern* column is lying. Cured by `u8_oracle.pshow()`, a
   function rather than a habit.
2. **A vacuity guard whose pass condition could not be met.**
   `probe_invalid.py`'s F3 asked `not isinstance(utf_result, tuple)` to mean
   "UTF did not answer" — but an error row IS a tuple, so the guard was
   unsatisfiable and reported `0 of 9` against a column that plainly differs.
   It announced itself only because it was written in the failing direction.
3. **`-o /dev/null`, reproduced verbatim.** pcrec writes `OUT.c` *and*
   `OUT.h`, so a `/dev/null` sink tries to create `/dev/null.h` and every
   COMPILING cell reads "Operation not permitted" — i.e. as a refusal.
   `docs/design/subroutines_measurements/CLAUDE.md` had already recorded this
   exact defect; this lane hit it anyway, on its first run, which is the R30
   M6 shape (*a defect reproduced verbatim by someone who had read the entry
   naming it*).

And one finding about the LOCAL side, which matters for anyone re-running
these probes here: `ctypes.util.find_library("pcre2-8")` on this Mac resolves
to **miniconda's** libpcre2, version **10.37** — not Homebrew's 10.48 and not
the reference 10.46. A "local comparison" run silently measures a *third*
version. The archiver prints `libpcre2:` from the library that actually
answered, which is what caught it.

---

## 1. Premises, re-verified on HEAD rather than inherited

`out/premises.txt`. This section exists because a design built on what a plan
row *says* the code does is a design built on a document, and the documents in
this tree have been wrong before. Two of the three claims below were wrong.

### 1.1 What ships today

**MEASURED** (`out/premises.txt` §1, §2, §6):

- `-e utf8` is refused **by the registry row's own name**:
  `encoding 'utf8' arrives with milestone M5 (an engine axis, not a module: no
  --features name enables it)`. `-e utf16` and `-e UTF8` are refused as
  unknown, with the menu rendered from the table. The seam's third-encoding
  recipe is real and this lane is its first test.
- `\x{...}`, `\p`, `\P`, `\N{U+...}` all refuse with **`requires module
  'unicode-props'`** — including inside a class, and including under `(?i)`.
  `\X` and `\R` refuse with `requires module 'misc'`, a **different module**,
  which §9 takes as a scope boundary rather than a detail.
- `\x41` (bare two-digit hex) **compiles**: only the braced form is gated.
- The registry's `\p`/`\P` rows read `built = unbuilt` (D65's derived column),
  `engines = dfa|vm`, `module = unicode-props`.
- The seam ships four residual entries (`next_pos`, `bref_match`,
  `bref_match_caseless`, `back_step`) behind a per-artifact mask.

### 1.2 THREE CLAIMS IN THIS LANE'S OWN CHARTER, CHECKED

**(a) `[DD-12]` assigns the CharSet widening to MOD-0.6. That is STALE, and
this milestone owns it.** The row says *"the CharSet widening is MOD-0.6's
(D33 §7)"*. D33 §7 itself carries an amendment dated the same session MOD-0.6
ran:

> **AMENDED 2026-08-12 (Frank, thirteenth session).** Widening DEFERS to the
> first milestone that PRODUCES a wide set (M5-era `\p` matching). MOD-0.6 as
> scoped in plan.md is recogniser-only — no producer lands, so a widened
> structure built there would itself be the unexercised structure this section
> warns about. Ownership split: MOD-0.6 owns the `\p`/`\P`/`\N{U+` REFUSAL
> surface; **the first wide producer owns the structure.**

**STRUCTURAL**, confirmed in the tree: `src/core/internal.h`'s `A_CLASS`
payload is still `struct { uint8_t bits[32]; } cls;` and `src/ir/nfa.c`'s
`A_CLASS` arm is still a `memcpy` of 32 bytes into one `N_CLASS` state. **This
milestone is the first wide producer, so §2.2 is this design's work and not an
inherited dependency.** The `[DD-12]` row should be corrected at merge.

**(b) The `[M5.0]` CROSS-NOTE's prescription for `pcrec_maxw` is REFUTED.**
The row says the `A_CLASS` arm *"must become the encoding's maximum code-unit
length"*. §5.6 shows, from a measurement, that doing exactly that would refuse
**every** lookbehind under UTF-8 including `(?<=a)`. The cross-note is right
that the arm is a hazard and right that the byte refusal is what makes it
exact today; its cure is wrong. This is the sharpest single finding in the
document.

**(c) `[DD-12] (3)`'s characterisation of `PCRE2_MATCH_INVALID_UTF` is
REFUTED as worded.** The row says that mode *"is essentially the byte-wise
semantics"*. §2.6 measures it and it is not — it is essentially the byte-wise
**UTF-8 automaton's** semantics, which is a different thing and happens to be
the one pcrec wants. The row's conclusion (*measure against THAT mode and pick
deliberately*) survives; its reason does not.

---

## 2. THE LOWERING (charter (i))

### 2.1 Where code points live, and where they stop

`[DD-12] (1)` and `(2)` fix this and the measurements do not disturb it, so
this section states the shape and moves on:

```
pattern bytes ─► [parser] ─► AST with CODE-POINT INTERVAL sets
                                     │
                                     │  ◄── the ONE place code points exist
                                     ▼
                             [encoding lowering]      one instance per backend
                                     │
                                     ▼
                       IR: byte-class NFA states, exactly as today
                                     │
                    subset construction, minimisation, both emitters,
                    every prefilter, the artifact  —  ALL BYTE-WISE
```

**Code points exist only between the parser and lowering.** That is where the
"convert everything to UTF-32" instinct belongs and it is the whole of its
territory: the subject is never converted, offsets are permanently bytes
(`[DD-12]`'s stated invariant, and `docs/spec/match_api.md` already promises
it), and the hot loop never decodes.

**The lowering is a per-backend instance, not a conditional.** DD-12 (7)
forbids `if (enc == UTF8)` anywhere. The byte backend's instance is
"code point *c* ≤ 0xFF becomes the one-byte sequence *c*, and an interval
touching anything above 0xFF is a compile error"; the utf8 backend's instance
is §2.3. Both live in `src/gen/enc/`, which is where §9 puts them.

### 2.2 The class structure widens HERE

The `Ast` `A_CLASS` payload becomes an interval list. **ASSERTED** shape,
offered for the panel to improve:

```c
/* A_CLASS: a set of CODE POINTS as sorted, disjoint, non-adjacent
 * intervals. The invariant is what makes every consumer simple:
 * lo[i] <= hi[i] < lo[i+1] - 1. */
struct {
    PcrecCpRange *iv;    /* arena-allocated */
    int           n;
} cls;
```

Three notes, each of which is a decision rather than a detail:

- **Why intervals and not a bitset.** A bitset over 0x110000 code points is
  136 KB per class node. The measured interval counts (§3.3) are 44 to 770.
- **Why not keep the 32-byte bitmap for sub-0x100 sets.** Two
  representations means two code paths in every consumer and a predicate
  deciding which — the special-case shape this project has a standing rule
  against. The byte backend's lowering reads intervals and emits a bitmap;
  the bitmap survives where it belongs, in the IR.
- **What this deletes.** `cls_set`/`cls_has` and the `pcrec_cls_*[32]`
  tables (`pcrec_cls_word_esc` and its eighteen siblings) are the byte-tier
  producers' output format. They become interval literals. §8.1 makes the
  no-op-ness of that conversion a gate rather than a claim.

**The parser is otherwise unchanged**, and that is `[DD-12] (1)`'s point:
there is no encoding parameter in the grammar. The parser changes only where
UTF changes the LANGUAGE (§2.7).

### 2.3 CharSet → byte-sequence fragments: the construction

The classic range-to-byte-sequence decomposition, used by RE2 and generated by
Ragel; cited as [Cox07] and [Ragel] in `REFERENCES.md` (entries added in this
change, per the citation rule that file's own header states). In one
paragraph:

Split each code-point interval at the UTF-8 length boundaries (0x7F, 0x7FF,
0xFFFF), and split out the surrogate range U+D800–U+DFFF, which has no UTF-8
encoding. Within one length class, an interval becomes a small set of
**byte-range sequences**: a chain of `N_CLASS` states whose bitmaps are
contiguous byte ranges. `U+0800–U+FFFF` minus surrogates is the canonical
four-row table

```
E0     A0-BF  80-BF
E1-EC  80-BF  80-BF
ED     80-9F  80-BF
EE-EF  80-BF  80-BF
```

and the whole construction is that table generalised. **Suffix sharing** — a
trie built from the END, so alternatives with common trailing byte-range
chains share states — is what keeps a `\p{L}`-sized set near-linear.

**THIS IS ALL EXISTING IR VOCABULARY.** A byte-range is a 256-bit bitmap with
a contiguous run set; a sequence is an `A_CAT` of them; a set of sequences is
an `A_ALT`. The lowering emits nodes `src/ir/nfa.c` already knows how to
compile, which is why §6 finds no downstream consequences: **there is nothing
downstream to change.**

Ill-formed input needs no handling because it has no path: an overlong
encoding, a truncated sequence, a surrogate encoding and a byte above 0xF4 are
all simply absent from the automaton. §2.6 turns that into a promise.

### 2.4 The sizing measurement: there is no blowup

**MEASURED** (`out/sizing.txt`), and this is the result that most changes the
shape of the milestone, because the charter asks about "state-count blowup"
and the honest answer is that there is none.

| class | intervals | byte-seq alternatives | NFA (shared) | DFA | min-DFA | lead bytes |
|---|---|---|---|---|---|---|
| `[a-z]` | 1 | 1 | 4 | 2 | 2 | 26 |
| `[\x{80}-\x{7FF}]` | 1 | 1 | 5 | 3 | 3 | 30 |
| `[α-ω]` | 1 | 2 | 7 | 4 | 4 | 2 |
| `[\x{100}-\x{10FFFF}]` | 2 | 8 | 18 | 9 | 9 | 49 |
| `.` (UTF, no DOTALL) | 3 | 10 | 20 | 9 | 9 | 178 |
| `[^a]` (UTF) | 3 | 10 | 20 | 9 | 9 | 178 |
| `\p{L}` | 648 | 786 | 2,205 | 283 | 283 | 97 |
| `\p{Lu}` | 646 | 659 | 1,246 | 74 | 74 | 47 |
| `\w` (UCP, approximated) | 883 | 1,056 | 2,958 | 332 | 332 | 110 |

Against pcrec's caps — `PCREC_MAX_NFA_STATES` 131,072,
`PCREC_MAX_DFA_STATES_GOTO` 10,000, `PCREC_MAX_DFA_STATES_TABLE` 32,000
(`out/premises.txt` §7) — **every row clears every cap by more than an order
of magnitude.** The largest minimised DFA in the table is 332 states.

And quantified, which is the sharper question because a class never appears
alone:

| form | DFA | min-DFA |
|---|---|---|
| `\p{L}` | 283 | 283 |
| `\p{L}*` | 283 | **282** |
| `\p{L}{1,3}` | 952 | 847 |
| `.*` (UTF) | 9 | 9 |

`\p{L}*` is **smaller** than `\p{L}`, which is not a typo and is worth
understanding rather than just recording: the star's back-edge merges the
accept state into the start state, and a DFA over a self-similar byte
structure has almost nothing left to distinguish. **A UTF-8 `.*` does not
blow the DFA cap; it is nine states.**

**The self-check is what makes these numbers usable.** 10,916 sample points —
every interval endpoint and its neighbours, interior points, out-of-class
points, hand-built surrogate encodings, truncations of every multi-byte
sample, and deliberate overlong re-encodings at every extra length — checked
for accept/reject against the built automaton: **0 mismatches**. It was not 0
on the first run. The construction had a real bug (the shared start state
consumed each alternative's first byte twice, so `[a-z]` could not match
`'a'`), found by the self-check at 5,460 mismatches and fixed. A sizing number
from a wrong construction is worse than no number, and this is the instrument
that separated the two.

**TWO CAVEATS, both stated rather than buried.**

1. **This is not pcrec's lowering, because pcrec has no UTF-8 lowering.** It
   is an independent from-scratch construction. It bounds what a correct
   implementation of the standard construction costs; it does not predict what
   pcrec's own will cost. §12 P-3 makes that falsifiable.
2. **The `\p{L}` row is Unicode 14.0.0 and PCRE2 10.46 is Unicode 16.0.0.**
   `out/sizing.txt` ran under this Mac's python 3.11 (`unicodedata` 14.0.0);
   `out/uprops.txt` §0 derives PCRE2's own version as **16.0.0**. The
   oracle-swept interval census (§3.3) gives `L` = **677** intervals against
   this table's 648 — a real 4.5% drift, quantified rather than hand-waved.
   It does not move any conclusion here (283 states versus a 10,000 cap), and
   §3.3's numbers are the ones §9 sizes tables from.

### 2.5 What happens to the byte-tier class machinery

Four consumers were named in the charter. **STRUCTURAL** in each case:

- **The 256-entry class bitmap machinery** is *below* the lowering and is
  untouched. `NState.cls[32]`, the DFA's `eqclasses` partition and its
  `d->rep[c]` representative-byte trick all operate on the byte alphabet, and
  after lowering the byte alphabet is all there is.
- **The class-axis views** (`upc_of_class`, `Dfa.s1w`, the `\b` context bit)
  ask "is the byte this class selects a word byte / a newline byte". Under
  UTF-8 the classes reaching them are byte-RANGE classes, and the question
  still has a well-defined answer — but *the answer is no longer the one the
  assertion needs*, because word-ness is a property of a CHARACTER. This is
  §5.4, and it is the one genuinely open engine question in the milestone.
- **`[OPT-CLSPACK]`'s forms** are helped rather than hurt. Its STEP 0 measured
  (`docs/dev/form_char_step0.md`) that range compares win on size and the
  shared-atom table wins at N≥16. A UTF-8 lowering produces byte-RANGE classes
  almost exclusively — the decomposition's output *is* contiguous ranges — so
  the form `[OPT-CLSPACK]` found cheapest is the form this lowering naturally
  emits. **ARGUED**; the measurement that would confirm it is a form census
  over a UTF-8 corpus, which cannot run until stage 2 lands.
- **`[FORM-CHAR]`'s object list loses one member.** §4.1 measures that 10.46
  does simple folding only, so object (5) `utf8-full-fold` has no PCRE2
  behaviour to reproduce.

### 2.6 Invalid UTF-8: the decision, taken deliberately

`[DD-12] (3)` leaves this open and asks for a measurement against
`PCRE2_MATCH_INVALID_UTF`. **MEASURED** (`out/invalid_utf.txt`):

**(a) The PATTERN is validated at COMPILE time**, with nine distinct error
codes naming the specific clause violated — `-22` isolated continuation byte,
`-23` illegal 0xFE/0xFF, `-8`/`-9` truncation, `-17` overlong, `-16`
surrogate, `-15` above U+10FFFF, `-13` five-byte form. **This costs the
emitted artifact nothing** and pcrec's compiler owes it. (D26 tier: pcrec owes
the *refusal*, not the wording.)

**(b) Under `PCRE2_UTF` alone, an ill-formed SUBJECT is a whole-subject
precondition, checked before matching.** The discriminating cell: pattern `a`
on subject `61 FF 61` returns `ERRM -23`, **not** a match at offset 0 — even
though a valid `a` sits before the bad byte. So `PCRE2_UTF` pays an O(n)
validation pass on every match call.

**(c) `PCRE2_MATCH_INVALID_UTF` differs on all nine ill-formed subjects**, and
what it does is make ill-formed bytes a **barrier**: matches on either side
are found (`a` on `61 FF` gives `(0,1)`; on `FF 63` gives `(1,2)`), matches
*through* them are not (`a.c` on `61 FF 63` → no match; `\w+` on
`61 62 FF 63 64` → `(0,2)`, stopping at the barrier).

**(d) `[DD-12] (3)`'s wording is refuted and its instinct is right.** Under
`options=0` — pcrec's actual byte encoding — `a.c` on `61 FF 63` **matches
`(0,3)`**: a byte engine is delighted to consume `0xFF` as a character. So
`MATCH_INVALID_UTF` is *not* the byte-wise semantics. It is the semantics of a
**byte-wise UTF-8 automaton**, which has no path for an ill-formed sequence
and therefore cannot match through one — precisely what §2.3 builds.

**THE RULING THIS DESIGN PROPOSES** (and §14 ASK 1 puts to Frank, because it
is a user-visible semantic and not an implementation detail):

> Under `--encoding=utf8`, pcrec's artifact **treats an ill-formed byte
> sequence as matching nothing**. There is no validation pass, no error
> return, and no `RX_ERR_*` code for bad input. This is
> `PCRE2_MATCH_INVALID_UTF`'s answer on every cell measured, and pcrec gets it
> **for free from the automaton's structure** rather than from a check.

Three reasons, in order of weight. It is what the construction does anyway, so
the alternative costs *more* code, not less. It preserves the streaming
promise (M3): a whole-subject precondition cannot be checked on a chunk. And
it keeps DD-12 (7) — a validation pass would be encoding-conditional code on
the hot path, which is the thing the seam exists to forbid.

**The cost is a stated divergence from PCRE2's DEFAULT UTF mode**, and the
design does not hide it: a caller who wants "tell me the subject is broken"
gets "no match" instead. §14 ASK 1 asks whether that is acceptable or whether
an opt-in validation entry point is owed.

**(e) The mid-character cursor.** `out/invalid_utf.txt` §E: a `startoffset`
inside a character is `ERRM -36 "bad offset into UTF string"` under
`PCRE2_UTF`, and under `MATCH_INVALID_UTF` it silently advances to the next
character boundary (start=1 on `αβ` returns `(2,4)`). pcrec's own answer falls
out of the same rule as (d) — a cursor mid-character has no path — but §5.1
shows this is exactly what `next_pos` exists to make unreachable for the one
caller who could hit it.

### 2.7 The parser changes, and only where UTF changes the language

`[DD-12] (1)`'s rule. **MEASURED** boundaries from `out/premises.txt` §2 and
`out/width.txt` §1:

- **`\x{...}` becomes meaningful above 0xFF.** Today it refuses with
  `unicode-props`; 10.46 gives error 134 (*"character code point value in
  \x{} or \o{} is too large"*) for `\x{3b1}` at `options=0` and accepts it
  under `PCRE2_UTF`. So `\x{...}` is **encoding-sensitive at the parser**:
  the same spelling is legal or not depending on a per-compile scalar. That is
  the one place this design puts an encoding question into the parser, and it
  is a RANGE CHECK on a value, not a conditional on behaviour.
- **A multi-byte atom quantifies as one unit.** Free: `\x{3b1}{2}` parses as a
  quantified atom and the atom lowers to a fragment. Nothing in `p_rep` cares
  how many bytes a fragment consumes.
- **`.` and `[^...]` change what they mean**, but only through the interval
  set — `.` becomes `[\x{0}-\x{10FFFF}]` minus newline, negation complements
  within the code-point space rather than within 0..255. This is the interval
  representation doing its job, not a parser change.

---

## 3. `\p{...}` / `\P{...}` — module `unicode-props` (charter (ii))

### 3.1 What 10.46 actually accepts

**MEASURED** (`out/uprops.txt` §1): 114 spellings tried, **83 compile, 30 are
error 147 (unknown property), 1 is error 146 (malformed)**. The 146/147 split
is the refusal surface `src/parse/mod_uprops.c` already ships, so this
extends a measurement the tree already depends on.

| axis | verdict |
|---|---|
| one-letter general categories `C L M N P S Z` | **compile** (the 7 pcrec's table already knows) |
| the other 19 letters | error 147 |
| two-letter categories (`Lu Ll Lt Lm Lo Mn Mc Me Nd Nl No Pc Pd Ps Pe Pi Pf Po Sm Sc Sk So Zs Zl Zp Cc Cf Cs Co Cn`) | **all 30 compile** |
| `L&`, `Any`, `Xan`, `Xps`, `Xsp`, `Xuc`, `Xwd`, `Assigned` | **compile** |
| bare script names (`Greek Latin Cyrillic Han Arabic Hebrew Hiragana Katakana Common Inherited Unknown Thai Deseret`) | **all compile** |
| `Script=`, `sc=`, `Script:`, `sc:` | **compile** |
| `Script_Extensions=`, `scx=`, `scx:`, `Script_Extensions:` | **compile** |
| boolean properties (`Alphabetic Uppercase Lowercase White_Space Bidi_Control Math Emoji ASCII_Hex_Digit Alpha Upper`) | **all compile** |
| `Bidi_Class=`, `bc=`, `bc:` | **compile** |
| **BLOCKS** (`InGreek`, `Block=Greek`, `blk=Greek`, `IsGreek`) | **error 147 — the one axis 10.46 does not have** |
| `\p{^L}` (caret negation inside braces) | **compiles** |
| `\p{grEEk}`, `\p{l a t i n}` | **compile** — case and separators insignificant, exactly the normalisation `mod_uprops.c` already implements |

The property surface is therefore **much larger than the charter's list**
(`\p{L}`, `\p{Lu}`, script names, `\p{scx:...}`): booleans and `Bidi_Class`
are two whole axes the charter did not name. §3.4 is where that gets staged
rather than shipped.

### 3.2 THE FINDING: `\p` does not require `PCRE2_UTF`

**MEASURED** (`out/uprops.txt` §2), and it changes the module's staging:

| options | compile `\p{L}` | `'a'` | U+00E9 as UTF-8 | U+00E9 as ONE BYTE | U+03B1 as UTF-8 |
|---|---|---|---|---|---|
| `options=0` | yes | MATCH | MATCH | **MATCH** | MATCH |
| `PCRE2_UCP` | yes | MATCH | MATCH | **MATCH** | MATCH |
| `PCRE2_UTF` | yes | MATCH | MATCH | ERRM −4 | MATCH |
| `PCRE2_UTF\|PCRE2_UCP` | yes | MATCH | MATCH | ERRM −4 | MATCH |

In an 8-bit non-UTF build, `\p{L}` matches the **single byte** 0xE9 — PCRE2
treats bytes 0–255 as code points 0–255, which is exactly what pcrec's `byte`
encoding is ("every byte is a character, 8-bit clean", D58's rename
rationale).

**Consequence: `unicode-props` is not an encoding-gated module.** Under
`--encoding=byte` a `\p{L}` is a 256-bit bitmap over the Latin-1 letters — an
ordinary bitmap producer exactly like `\d`, needing **no** structural
widening, **no** byte-sequence lowering, and no UTF-8 backend. This is what
lets §9 land `unicode-props` *before* the utf8 backend, on a stage whose
acceptance is entirely within today's machinery.

**A second, sharper consequence.** `[DD-11]`/D85's ruled-in class-escape
family (`\d \D \s \S \w \W \h \H \v \V \N \R` + POSIX classes) carries
*"predicate `always` today with UTF/UCP as the chartered second row"*. The
measurement above says the second predicate is **UCP, not UTF** — they are
independent bits and it is UCP that redefines `\w`/`\d`/`\s`/`\b`
(`out/uprops.txt` §2's second table, and every `UCP-SPLIT` row in
`out/divergence.txt`). A `[DD-11]` row keyed on the encoding would be keyed on
the wrong axis.

### 3.3 The table-size problem

The charter asks for a sizing estimate per property family "against the
artifact-size log's sensibilities". **MEASURED** by sweeping all 1,114,112
code points against a compiled `^\p{X}$` on the oracle itself
(`out/uprops.txt` §3) — so these are 10.46's own membership under Unicode
16.0.0, immune to the version caveat of §2.4:

| property | intervals | code points | sweep |
|---|---|---|---|
| `L` | **677** | 141,028 | 4.1 s |
| `Lu` | **651** | 1,858 | 3.8 s |
| `Nd` | **71** | 760 | 3.8 s |
| `Greek` | **44** | 531 | 3.8 s |
| `Han` | **42** | 99,338 | 4.0 s |
| `Xan` | **770** | 142,939 | 4.1 s |

The unit that matters is **intervals**, not code points: `Han` has 99,338 code
points in 42 intervals, and it is the 42 that the lowering and any table pay
for.

**What an artifact actually carries.** Not the interval table — that is
*compile-time* data inside pcrec. The artifact carries the **lowered
automaton**, and §2.4 measures it: `\p{L}` is 283 DFA states. Against
`[ART-SIZE]`/D84's caps (code-bytes 500,000, total-bytes 1,000,000) a
283-state DFA is unremarkable; the corpus already contains larger machines.
**So the "table-size problem" the charter names is, for the DFA route,
measured not to be a problem.**

It IS a problem in one place, and the design should say which: **pcrec's own
binary** must contain the property data for every property it can compile.
`\p{L}` at 677 intervals × 8 bytes is ~5.4 KB; the full general-category set
is roughly 5,000 intervals (~40 KB); adding all ~160 scripts and the boolean
properties would be several hundred KB of static tables in `libpcrec.a`. That
is a real cost and it is the reason §3.4 stages rather than ships everything.

**WHERE THE DATA COMES FROM IS THE HARD QUESTION, and it is an ASK.** There
are three sources and two of them are disqualified:

- **Generate from python's `unicodedata`** — disqualified by version drift,
  now quantified: python 3.11 says `L` has 648 intervals, 10.46 says 677
  (§2.4 caveat 2). And the two boxes this project uses carry *different*
  pythons (3.11/Unicode 14.0.0 here, 3.14/Unicode 16.0.0 there), so the
  generated table would depend on which machine ran the generator.
- **Generate by sweeping libpcre2** — disqualified by the rule
  `src/parse/mod_uprops.c`'s own header states, in the manager ruling that
  made its short-name table hand-written: *"a table generated from libpcre2
  and then checked by a differential against the SAME libpcre2 install is one
  source wearing two hats"*. PC-3 and PC-4 are the independent checks; making
  them check their own generator's output would delete them.
- **Vendor the UCD data files** (`UnicodeData.txt`, `Scripts.txt`,
  `ScriptExtensions.txt`, `PropList.txt`, `DerivedCoreProperties.txt`) at a
  **pinned Unicode version**, generate into a `.inc` at build time exactly as
  `cls_bits.inc` is generated today, and let PC-3/PC-4's libpcre2 differential
  remain the independent check. **This is the design's recommendation** and
  §14 ASK 2 puts it to Frank, because it is the first third-party data this
  repository would vendor and `third_party/` currently holds only PCRE2's
  BSD-licensed testdata.

The version pin is itself a decision: pinning to 16.0.0 matches 10.46 today
and will drift when the reference libpcre2 moves, which D26's addendum already
treats as a re-measurement event.

### 3.4 What ships, what refuses

**ASSERTED** staging, on the sizing above:

| family | first landing | why |
|---|---|---|
| one- and two-letter general categories, `L&`, `Any`, `Assigned` | **SHIP** | ~5,000 intervals total; one UCD file; the family every `\p` user reaches for first |
| `Xan Xps Xsp Xuc Xwd` | **SHIP** | PCRE2-specific, defined in terms of the categories above — derived, no new data |
| script names, `Script=`/`sc=` | **stage 5** | one more UCD file, ~160 names; nothing structural, purely table weight |
| `Script_Extensions=`/`scx=` | **stage 5, with scripts** | same file family; the charter names `scx:` explicitly |
| boolean properties (`Alphabetic`, `Math`, `Emoji`, …) | **REFUSE at first landing** | a third data family; no measured demand |
| `Bidi_Class=`/`bc=` | **REFUSE** | a fourth; no measured demand |
| **blocks** (`InGreek`, `blk=`) | **REFUSE PERMANENTLY** | 10.46 refuses them too (error 147). Reproducing a refusal is free and correct. |

A refused-but-well-formed body must refuse **as `unicode-props` not
implementing it**, never as unknown — the wording rule `mod_uprops.c`'s header
already states (pcrec may only claim "not recognised" where its own table is
exhaustive for the axis). The 146/147 distinction it ships is unchanged.

---

## 4. DD-1: caseless under UTF (charter (iii))

`[DD-1]`'s remaining half is *"multi-byte fold pairs, one-to-many foldings and
the fold-before-negate rule over byte-range trees rather than a 256-bit
bitmap"*. Three questions; the measurement answers all three and **deletes
one of them**.

### 4.1 10.46 does SIMPLE folding only — so there are no one-to-many foldings

**MEASURED** (`out/caseless.txt` §2). Eleven one-to-many cells — ß/SS, ß/ss,
SS/ß, ss/ß, U+FB01/fi, fi/U+FB01, U+FB03/ffi, U+0149, U+01F0, U+1E96, U+0390 —
under `PCRE2_UTF|PCRE2_CASELESS` and under `…|PCRE2_UCP`:

> **1:n cells that matched under some caseless option: 0 of 11**

And from the other side, `[ß]` caseless does not match `"ss"` or `"SS"`, and
`[s]` does not match `ß`.

**This is the section's most valuable result because of what it removes.** A
1:n fold cannot live in a set — it is a *sequence*, so it would force a
caseless literal to become an alternation and a caseless class to hold
something a class cannot hold. `[FORM-CHAR]`'s object (5) `utf8-full-fold`
(*"1:n folds (ß ↔ SS): a small NFA step"*) has **no PCRE2 behaviour to
reproduce** and should not be built. Object (4) `utf8-simple-fold` is the
whole job.

**D23's rule therefore survives verbatim**: the fold is applied to the SET, in
the one constructor, at parse time. Only the set is now code points.

### 4.2 It is a CLOSURE, not a pairing — and it reaches outside the range

**MEASURED** (`out/caseless.txt` §3, §3b, §5). Three findings that constrain
the implementation:

**(a) Equivalence classes have more than two members.** `k` ↔ `K` ↔ U+212A
(KELVIN) all match each other; so do `s` ↔ `S` ↔ U+017F (LONG S). A
constructor that "adds the other case" from a single case-mapping table gets
these wrong. It must compute the **closure** of the set under the fold
relation.

**(b) The partner is often in a different block.** Measured matching pairs:
KELVIN U+212A ↔ k, ANGSTROM U+212B ↔ å, OHM U+2126 ↔ ω, MICRO U+00B5 ↔ μ,
LONG S U+017F ↔ s, final sigma U+03C2 ↔ σ ↔ Σ. And two that **do not** fold:
U+0130 (dotted capital I) and U+0131 (dotless i) match neither `i` nor `I` —
which is Unicode's default simple case folding, and a naive
`toupper`/`tolower` table would get both wrong in opposite directions.

**(c) THE CLOSURE ADDS INTERVALS FAR FROM THE WRITTEN ONES.** The sharpest
cell in the section: **`[a-z]` under caseless matches U+212A** (3 bytes) and
**U+017F** (2 bytes). So the fold cannot be a post-pass over byte ranges — by
the time the set is byte ranges, U+212A is not adjacent to anything in
`[a-z]`. **The fold must happen while the set is still code points**, which is
`[DD-12] (5)`'s prediction confirmed and is the ordering constraint the
implementation must not get wrong.

**(d) A consequence for literals nobody had written down.** Because folding is
1:1 but the partners have different encoded lengths, **a caseless
single-character match consumes a variable number of bytes**: `(?i)k` against
U+212A matches `(0,3)`. Under UTF-8 a caseless literal is a code-point class
whose members encode to different byte counts — and §2.3's construction
handles that with no new machinery, because an alternation of byte-sequences
of differing length is exactly what it already builds. **No special case is
needed**; the fact is recorded because it is surprising and because §5.3 needs
it.

### 4.3 Fold before negate, over UTF

**MEASURED** (`out/caseless.txt` §4). OS-1/D23's ordering rule holds under
UTF, including across blocks:

| cell | result |
|---|---|
| `[^k]` caseless on `K` | no match |
| `[^k]` caseless on **U+212A** | **no match** ← the whole test |
| `[^K]` caseless on `k`, on U+212A | no match |
| `[^s]` caseless on U+017F | no match |
| `[^a-z]` caseless on `A` | no match |
| `[^\p{Ll}]` caseless on `A` | no match |

The negation is over the **closed** set. Since §4.2(c) puts the closure before
the byte lowering and the negation is a complement of the interval list, the
existing constructor's order — fold, then negate, then lower — is unchanged.
`pcrec_ast_class_node`'s single-constructor discipline is what carries this,
exactly as it does today.

### 4.4 The ruled subset for first landing

**ASSERTED**, and deliberately not a subset at all:

> **Full simple case folding ships**, because the measurement shows that IS
> the whole of PCRE2 10.46's behaviour. There is no 1:n tier to defer.

The boundary that *does* need stating is the **data**, and it is §3.3's
question one axis over: the fold closure needs `CaseFolding.txt` (the `C` and
`S` status lines — simple folding), a fifth UCD file, pinned to the same
version. Under `--encoding=byte` the closure is the ASCII one pcrec already
has (`src/core/fold.c`), unchanged and byte-identical.

### 4.5 The UCP wrinkle, and pcrec has no UCP axis

**MEASURED** (`out/caseless.txt` §7): without `PCRE2_UTF`,
`PCRE2_CASELESS` alone folds **only the 52 ASCII letters** (byte 0xE9 does not
match 0xC9), which is exactly `enc_byte.c`'s residual contract and exactly
`src/core/fold.c`. But `PCRE2_UCP|PCRE2_CASELESS` **does** fold them.

pcrec has no `UCP` axis today, so pcrec's `byte` encoding reproduces PCRE2 at
`CASELESS` and diverges at `UCP|CASELESS`. That is a **pre-existing, correct**
state of affairs — pcrec's byte semantics are `options=0`-family — and this
design does not change it. It is recorded because §7's corpus author will meet
it as eight `UCP-SPLIT` rows and needs to know pcrec has no lever there.
§14 ASK 4 asks whether a UCP axis is owed at all.

---

## 5. THE SEAM'S SECOND INSTANCE (charter (iv))

The seam is `src/gen/enc/enc.h`'s `PcrecEncEntry` table, four entries today.
**The headline of this section is that the seam needs no interface change** —
D58's revisit clause is honoured by having nothing to record — **and that the
one thing that does have to change is an ANALYSIS outside the backend, which
the seam was never going to catch.**

### 5.1 `next_pos` — the entry the seam was built for

**STRUCTURAL.** The contract is already encoding-neutral: *"the smallest
position strictly greater than `pos` that is a character boundary of this
artifact's encoding, counting every position ≥ n as a boundary"*. The UTF-8
body:

```c
size_t $_next_pos(const unsigned char *s, size_t n, size_t pos)
{
    size_t i = pos + 1;
    while (i < n && (s[i] & 0xC0) == 0x80) i++;
    return i;
}
```

Reads `s` only in `[pos, n)`, as the contract promises; `pos >= n` returns
`pos + 1` because the loop does not run. **No caller changes a character** —
`docs/spec/match_api.md` §3.1's find-all loop is already final.

**Why this is not merely cosmetic.** `out/width.txt` §4a runs PCRE2's own
find-all over `αβγ` advancing by `+1` past an empty match: the second
iteration lands mid-character and PCRE2 returns `ERRM -36`. The `+1` a caller
would have written before `[M5-SEAM]` is exactly the bug this entry deletes.

**It stays `engine_callable = false`.** Unanchoredness is the automaton's own
self-loop; there is no external advance for an engine to route through, and
`tests/codegen`'s `[M5-SEAM]` check keeps enforcing that.

### 5.2 `back_step`, and THE WIDTH FINDING

The contract already says the right thing — *"the position exactly `k`
CHARACTERS before `pos`"* — and `enc_byte.c`'s own comment explains that `s`
and `n` are parameters this backend ignores *because* "a UTF-8 backend walking
back over continuation bytes must reject a MALFORMED sequence". The body:

```c
size_t $_back_step(const unsigned char *s, size_t n, size_t pos, size_t k)
{
    (void)n;
    while (k--) {
        if (pos == 0) return $_BACK_STEP_NONE;
        do { pos--; } while (pos > 0 && (s[pos] & 0xC0) == 0x80);
        if ((s[pos] & 0xC0) == 0x80) return $_BACK_STEP_NONE;  /* ran off */
    }
    return pos;
}
```

**MEASURED** boundary cells (`out/width.txt` §4b): one character precedes →
succeeds; nothing precedes → clean fail; **a continuation byte precedes with
no lead byte** → PCRE2 answers `ERRM -22`, and this body answers
`BACK_STEP_NONE`, which under §2.6's ruling is the right pcrec answer (no
path, no match). Fewer than `k` characters precede → clean fail.

**AND NOW THE FINDING.** `k` is in CHARACTERS. Where does pcrec's `k` come
from? `src/parse/mod_lookaround.c`'s `la_widths`:

```c
long long lo = pcrec_minw(a->r), hi = pcrec_maxw(a->r);
if (lo != hi || hi >= PCREC_W_UNBOUNDED || hi > INT_MAX) { ... refuse ... }
out[i] = (int)hi;
```

and `pcrec_minw`/`pcrec_maxw` are documented, in their own headers, as
counting **BYTES**. Under the byte encoding the two units coincide and nothing
in the tree can tell them apart. Under UTF-8 they do not. §5.6 is the
resolution.

### 5.3 The backreference compares

`enc_byte.c`'s comment makes a specific prediction about why the entry returns
a LENGTH rather than a bool:

> `(?i)^(ss)\1$` on `"ss\xdf"` is the cell a UTF-8 build has to answer
> differently, with one captured character folding to two and the consumed
> length no longer equalling the captured one.

**MEASURED** (`out/caseless.txt` §6): that cell is **no match** under
`PCRE2_UTF|PCRE2_CASELESS`, exactly as it is in the 8-bit build. **The
prediction is refuted**, and it is refuted by §4.1 — there is no 1:n folding,
so the sharp-s family does not behave that way.

**But the design decision it justified is CORRECT, for a different reason this
lane measured.** Same section:

> `^(k)\1$` on `6B E2 84 AA` (`k` then U+212A) → **MATCH(0, 4)**

The captured group is **one byte** (`k`); the backreference consumed **three**
(U+212A). The compare is **not length-preserving**, because §4.2's 1:1
cross-block folds pair code points of different encoded lengths. So:

- The `ptrdiff_t` length return is vindicated. A `bool` could not express it,
  and the shared emitter "never computes a length, it only adds the one it is
  given" — DD-12 (7) working as designed.
- **`enc_byte.c`'s comment should be corrected at the [M5.0] merge**, not
  deleted: it names the right mechanism and the wrong witness. The design's
  §12 P-6 turns that into a check.
- The UTF-8 caseless compare walks CHARACTERS on both sides, folding each,
  and returns the SUBJECT bytes consumed. On failure it returns
  `-(prefix) - 1` where `prefix` is subject bytes compared equal — the
  protocol is unchanged.

The case-sensitive compare is a plain `memcmp` under any encoding (UTF-8 is
self-synchronising; equal bytes ⇔ equal code points), which is `[FORM-CHAR]`
object (3) `utf8-exact` and is worth stating because it means the
non-caseless entry's body is **literally unchanged** between backends.

### 5.4 `\b` and word classification — the entry that does not exist

**This is the milestone's one genuinely open engine question**, and the design
states it as such rather than resolving it cheaply.

`\b` is shipped (`[M6.2]` wave B) as a **class-axis context bit** in the DFA
state identity: `upc_of_class` asks whether a byte class is a word class by
testing its representative byte against `pcrec_cls_word_esc[32]`. That
mechanism is exact when one byte is one character. Under UTF-8 the classes
reaching it are byte-RANGE classes and word-ness is a property of the
**character**, so the representative-byte test is asking the wrong question.

**MEASURED** (`out/width.txt` §4c), the cells a UTF-8 build must answer:

| cell | `PCRE2_UTF` | `PCRE2_UTF\|PCRE2_UCP` |
|---|---|---|
| `\bx` on `αx` | `(2,3)` | no match |
| `\Bx` on `αx` | no match | `(2,3)` |
| `\b` on `αβ` | no match | `(0,0)` |

Note the two columns **disagree**, which is §4.5's UCP wrinkle arriving in the
engine: without UCP, `\w` is ASCII-only and α is a non-word character, so
there IS a boundary; with UCP there is not.

**THE DESIGN'S POSITION**, and it is deliberately the modest one:

> **Without `UCP`, `\b`'s alphabet is ASCII-only, and the shipped mechanism is
> already correct under UTF-8.** `\w` is `[A-Za-z0-9_]`, every member is a
> one-byte character, and every byte of a multi-byte character is a
> non-word byte — so the byte-level test and the character-level test agree
> on every input. **STRUCTURAL**, and §12 P-4 is the sweep that would refute
> it.

That is why this section proposes **no fifth seam entry** at first landing. A
seam entry for word classification becomes necessary exactly when a UCP axis
lands (§14 ASK 4), and building it now would be the unexercised structure
D24/SR-2 warns about. **The door is recorded as built, not walked through**:
the seam's entries table grows by one row, per `enc.h`'s own third-encoding
recipe, with no interface change — the property `[M6.6.2]` wave D already
demonstrated (prediction P-1).

### 5.5 `\G` and the other advances

**STRUCTURAL.** `\G` is `pos == startpos`, an absolute position test that
reads no byte (`assertions_design.md` §4.2, and `internal.h`'s `N_GSTART`
comment). It has no encoding-sensitive residue at all. The charter lists it;
the answer is that there is nothing to instantiate.

`ENG_ATTEMPT`'s `for (start = startpos; start <= start_max; start++)` is a
genuine external byte-arithmetic advance loop in shared emitter code —
`assertions_design.md` already flagged it as outside D58's "the hot path has no
external advance loop" rationale. Under UTF-8 it would try starts
mid-character. **Those starts have no path** (§2.6) so they cannot produce a
wrong answer; they are wasted attempts, at up to 3 per character.
**ASSERTED**: correct but not optimal, and the optimisation (step the loop by
`next_pos`'s rule) is deliberately NOT taken here, because routing that loop
through a residual entry is precisely what `engine_callable = false` and
sabotage row S68 forbid. §14 ASK 5 raises it; §11 puts it out of scope.

### 5.6 The cross-note answered — and its prescription refuted

The `[M5.0]` row says:

> `pcrec_maxw`'s A_CLASS arm answers 1 BYTE and is EXACT only because
> `src/core/compile.c` refuses `PCREC_ENC_UTF8` by name; the day a UTF-8
> backend lands that arm **must become the encoding's maximum code-unit
> length**, or the lookbehind fixed-width rule silently accepts
> variable-width branches.

**The hazard is real. The cure is wrong, and following it would break every
lookbehind under UTF-8.**

**MEASURED** (`out/width.txt` §1, §2): PCRE2 measures lookbehind length in
**CHARACTERS**.

| pattern | compiles under UTF | `PCRE2_INFO_MAXLOOKBEHIND` |
|---|---|---|
| `(?<=a)x` | yes | 1 |
| `(?<=\x{3b1})x` | yes | **1** ← 2 bytes, reported as 1 |
| `(?<=[a\x{3b1}])x` | **yes** | **1** ← 1-or-2 bytes, ONE branch |
| `(?<=.)x` | yes | 1 |
| `(?<=a\x{3b1})x` | yes | 2 |
| `(?<=a*)x` | **err 125** | — |

The discriminating cell is row 3: **one branch, fixed at one character,
variable at one-or-two bytes, and 10.46 compiles it.** The
`MAXLOOKBEHIND` index was re-verified in the same run against
`la_oracle.py`'s own three-cell guard (3 / 0 / 2 for `(?<=abc)x` / `abc` /
`(?<=ab)x`), which is what separates it from `MINLENGTH`.

**So the prescription fails in two directions at once.** Set the `A_CLASS` arm
of `pcrec_maxw` to 4 (UTF-8's maximum code-unit length) and:

- `la_widths` tests `pcrec_minw(branch) == pcrec_maxw(branch)`. `minw`'s
  identical-looking arm stays at 1 (it is an under-estimate, its safe side —
  the row says so). So **every** class branch reads `1 != 4` and refuses.
  `(?<=a)x` — a pure-ASCII lookbehind that works today — would stop
  compiling under `--encoding=utf8`.
- Nothing is gained even in principle, because `k` is handed to `back_step`
  as CHARACTERS. The number the analysis must produce was never a byte count.

**THE POPULATION THAT MAKES THIS CONCRETE.** **MEASURED**
(`out/width.txt` §3) — every body below is accepted by 10.46 as fixed-width
(MAXLOOKBEHIND 1) and has more than one observed byte width:

| body | maxlb | byte widths observed |
|---|---|---|
| `[a\x{3b1}]` | 1 | 1, 2 |
| `.` | 1 | 1, 2, 3, 4 |
| `[^a]` | 1 | 1, 2, 4 |
| `\w` | 1 | 1, 2 |
| `\p{L}` | 1 | 1, 2, 4 |
| `[\x{0}-\x{10FFFF}]` | 1 | 1, 2, 4 |
| `(?i)s` | 1 | 1, 2 |
| `(?i)[a-z]` | 1 | 1, 2 |

**6 of 6** plain bodies are variable-byte-width, and the two caseless rows are
the same phenomenon arriving through §4.2(c)'s fold closure.

**THE RESOLUTION.** Two quantities, because there are two consumers asking
different questions:

1. **`pcrec_minw` / `pcrec_maxw` stay in BYTES and become EXACT per class.**
   Their real consumer is `[M4.6d]`'s MRL pruning ("how many subject bytes
   must any accepting continuation still consume"), which genuinely wants
   bytes. Under UTF-8, `minw(A_CLASS)` = the minimum encoded length over the
   class's intervals; `maxw(A_CLASS)` = the maximum. Both are **exact**, both
   are computable from the interval list at the lowering, and both are a
   strict improvement over today's constant `1` — the MRL bound gets *tighter*
   for a non-ASCII class, not looser. Each arm keeps its own safe direction.
2. **`la_widths` moves to a CHARACTER-width analysis.** A new
   `pcrec_cwmin`/`pcrec_cwmax` over the same AST, identical in shape to
   `mrl.c`'s pair (same saturating arithmetic, same `default:`-less exhaustive
   switch, same opposite-direction obligation), whose `A_CLASS` arm answers
   **exactly 1 in every encoding** — because a class is one character by
   definition. That is what makes the whole table above compile.

**Why this is not two sources for one fact.** They are two different facts.
Under `--encoding=byte` they are numerically equal, and §8.1's identity gate is
what proves the byte-encoding answers did not move. A panel should attack
whether one parameterised function (`pcrec_width(a, UNIT_BYTES|UNIT_CHARS)`)
is better than two; the argument for two is `mrl.c`'s own — an exhaustive
switch per analysis is the alarm that fires when a node kind is added, and a
unit parameter threaded through every arm makes each arm answer two questions
where today it answers one.

**A consequence worth pricing before the panel does.** Making `maxw` exact
means `maxw(A_CLASS)` under UTF-8 can be 4, so a lookbehind's *byte* width
becomes variable — but no consumer of `maxw` asks for a lookbehind's byte
width any more, because §5.6(2) moved that consumer. The `end-check` the
emitter emits on both arms (`[M6.6.2]` wave D, ASK 2's ruling) keeps working
and gets *more* valuable: it is the runtime evidence that the character
analysis agrees with what the emitter did, and under UTF-8 it stops being
redundant, which `emit_vm.c`'s own comment predicts in those words.

---

## 6. Engine and selection consequences (charter (v))

### 6.1 State counts — answered in §2.4

No blowup. Largest measured minimised DFA is 332 states (`\w` under UCP)
against a 10,000-state computed-goto cap and a 32,000-state table cap.
`.*` under UTF is 9 states.

### 6.2 UTF-8 artifacts are DFA-eligible on day one

**ARGUED** from §2.3 and §2.4, and the argument is short because the
construction makes it short: **the lowering emits nodes the IR already has.**
A byte-range class is an `N_CLASS`; a sequence is a concatenation; a set of
sequences is an alternation. Subset construction, Hopcroft minimisation, the
`eqclasses` partition, both emitters and every optimisation pass see exactly
what they see today.

So the answer to "DFA-eligible day one or VM-first" is **day one, and not as a
choice** — there is no mechanism by which an encoding could make a pattern
VM-only, because engine selection reads node kinds and registry rows and this
lowering introduces neither. The one thing that *would* force the VM is a
construct, not an encoding: `\X` (grapheme clusters) is module `misc` and out
of scope (§11).

### 6.3 The prefilter: is `memchr` on a lead byte still sound?

**The soundness argument is one line and does not mention UTF-8.** The
prefilter derives a set of bytes any match can START with, from the automaton
pcrec built. Under UTF-8 that automaton's start states are lead-byte ranges.
The derivation is unchanged and its output is correct **by construction**,
because it reads the machine rather than the pattern. There is no
"superset" step to justify: it is the same computation on a different machine.

What changes is the filter's **quality**, and that is measured
(`out/sizing.txt`, lead-byte column):

| class | lead bytes | consequence |
|---|---|---|
| `[α-ω]` | **2** (0xCE, 0xCF) | excellent filter; but `memchr` takes ONE byte, so the single-byte arm declines and the bitmap-skip arm takes it |
| `\p{Lu}` | 47 | a usable bitmap filter |
| `\p{L}` | 97 | weak |
| `.` | 178 | useless — but `.` is useless under the byte encoding too |

**The finding for the design is the first row**: a two-byte lead set is a
*strong* filter that the current `memchr` arm cannot use, because `memchr`
takes a single byte. The `byte-class` bitmap arm handles it (`RX_DFA_SCAN`'s
measured five values, D81), so nothing is broken — but a two-value scan is a
real optimisation opportunity that UTF-8 makes common where the byte tier made
it rare. **Recorded, not built** (D77): the measurement that would trigger it
is a throughput comparison of `memchr`-on-one-byte versus a two-value scan on
a UTF-8 corpus, and that corpus does not exist until stage 2.

**`[OPT-K]`'s offset-k skip gets better, and for free.** A 2-byte character's
second byte is a continuation byte in `80-BF`, so a UTF-8 pattern starting
with a specific non-ASCII character has an *exact* byte at offset 1 — the
richest possible input for that mechanism. **ASSERTED**; same trigger.

---

## 7. The oracle plan (charter (vi))

### 7.1 The D27 goal-facts list

**MEASURED** (`out/divergence.txt`): 28 cells, each in four columns —
libpcre2 at `PCRE2_UTF`, at `PCRE2_UTF|PCRE2_UCP`, python `re` over `str`, and
python `re` over `bytes`.

**The four-column structure is itself the finding.** python has one engine per
subject type and PCRE2 has two UTF modes, so "python vs PCRE2" is not one
comparison. `\w` over a Greek letter is FALSE in python-bytes, FALSE in
PCRE2/UTF, and TRUE in both python-str and PCRE2/UTF|UCP. **A corpus author
told only "python disagrees" would mark the wrong cells.**

Verdict tally over the 28 rows: **10 PCRE2-ONLY, 8 UCP-SPLIT, 5 PY-STR-ONLY,
5 ALL-AGREE.** Twenty-three of twenty-eight are not all-agree, against the
charter's "at least 10".

**The list the blinded author gets** (the design's §7 extract, cut at cell
level):

| verdict | count | what the author does |
|---|---|---|
| `PCRE2-ONLY` | 10 | mark `# pcre2-only`; libpcre2 rules the cell. These are `\p{...}`, `\x{...}`, `\X`, `\R`, class ranges over non-ASCII, quantified multi-byte characters, an ill-formed subject — **python `re` cannot express the syntax at all**, which is a stronger reason than "disagrees" |
| `UCP-SPLIT` | 8 | `\w \d \s \b \W` over non-ASCII. **pcrec has no UCP axis** (§4.5), so the corpus must state which semantics it expects — pcrec's answer is the non-UCP column |
| `PY-STR-ONLY` | 5 | `.`, `.{2}`, `[^a]` over multi-byte characters, caseless LONG S. python's `str` engine is the right oracle; **the suite's `bytes` engine is not** |
| `ALL-AGREE` | 5 | write the cell, python verifies it |

**The `PY-STR-ONLY` row is the one that changes test infrastructure**, and it
is why §7.4 exists: the suite's python oracle today compares bytes, which is
correct for the byte tier and wrong for the UTF tier on 5 of 28 measured
cells — silently, in the direction that loses the oracle (R32 C3's shape).

### 7.2 The python version is itself an axis

**MEASURED**, and it is a hazard nobody had named. The suite's oracle is
"python3 `re`" with no version pinned, and the two machines this project uses
do not carry the same one:

| box | python | `unicodedata` |
|---|---|---|
| old box (the reference oracle's home) | 3.14.4 | **16.0.0** |
| this Mac | 3.11.4 | **14.0.0** |

libpcre2 10.46 is Unicode **16.0.0** (`out/uprops.txt` §0, derived by sweeping
`pcre2_config_8` slots rather than guessed — the method
`pcre2_ctypes.py` used for `PCRE2_CONFIG_VERSION`, forced by this box having
no `pcre2.h`).

So on the old box the python oracle and the PCRE2 oracle share a Unicode
version, and **on this Mac they do not**.

**THE OBVIOUS ALARM WAS RUNG AND IT DID NOT SOUND, WHICH IS THE HONEST
RESULT.** The whole 28-row divergence table was re-run under python 3.11 /
Unicode 14.0.0 (`out/divergence_local_py311.txt`) and compared row by row
against the 3.14 / 16.0.0 run: **the two are identical, cell for cell, on all
28 rows.** So the version axis, real as it is, does **not** move any cell in
§7.1's list, and this section must not imply that it does. The rows were
chosen for engine-semantic divergence (`\w` under UCP, `.` over multi-byte,
syntax python lacks), and none of them sits near a code point whose properties
changed between Unicode 14 and 16.

**Where the version axis IS live is §3.3's tables**, and there it is
quantified rather than feared: `\p{L}` is **648** intervals under Unicode
14.0.0 and **677** under 16.0.0. That is a property-DATA question, which is
why ASK 2 pins a version for the vendored UCD files and why §3.3's census is
swept from the oracle rather than from python.

**The design's requirement is therefore narrower than it first appears**, and
§8 makes it a check rather than a note: any generator that derives `\p`
membership records the `unicodedata.unidata_version` it ran under and the
verifier **fails loudly** on a mismatch — the same skip-loudly convention PC-3
uses for a missing libpcre2. Generators that only exercise engine semantics
need no such pin, on this measurement.

### 7.3 The PC-4 oracle twin

`[DD-12] (4)` names it and carries R13/R14's warning verbatim: *a UTF sweep
needs generators that can PRODUCE multi-byte constructs, or it counts the
generator.* The design has nothing to add to that warning and repeats it
because it is the failure this lane's own sizing sub-lane nearly made in a
different form. Concretely, the UTF twin of PC-4 must generate: multi-byte
literals, classes with non-ASCII endpoints, classes spanning the 1-byte/2-byte
boundary (`[a\x{3b1}]` — the §5.6 shape), `\p{...}` bodies, caseless
non-ASCII, and subjects containing characters of all four encoded lengths. An
ASCII-only generator run under `--encoding=utf8` would report a clean sweep
over patterns whose UTF-8 lowering is the identity.

### 7.4 `.rxt` encoding directives — flagged, not written

The charter says to flag rather than write, and the flag has three parts:

1. **A per-block `encoding` directive** is needed, because the encoding is a
   per-compile scalar and a corpus must exercise both.
2. **The oracle-selection line needs a third value.** Today a block is
   python-verifiable or `# pcre2-only`. §7.1 measures a **third** state:
   python-verifiable *but only through the `str` engine*. `docs/spec/
   rxt_format.md` needs a design note for it, and getting it wrong is silent.
3. **Subject bytes**: a `.rxt` subject line must be able to carry arbitrary
   bytes including ill-formed sequences (§2.6's cells are exactly the tests
   worth writing). Whether today's escape vocabulary covers that is a
   question for the format's owner, not this lane.

`docs/spec/rxt_format.md` is not edited by this lane. §14 ASK 6 routes it.

---

## 8. The validation plan (charter (vii))

### 8.1 The identity gate

**The module's no-op proof**, on the `[M6.6.2]` wave-0 and `[M6.5]` precedent:
every artifact pcrec emits under `--encoding=byte` (the default) is
**byte-identical** to what the pinned pre-M5 binary emits, over the whole
corpus, on four axes: default, the standard second, `-fno-prefilter`, and
`--no-captures`.

**This gate is doing more work here than in any previous module**, and the
reason is §2.2: this milestone changes the **class representation**, which
every pattern in the corpus goes through. A lookaround module touches patterns
containing lookaround; this touches every pattern that contains a character.
The gate is therefore the primary instrument, not a formality.

**The positive control** — the half that can actually fail — is that the
pinned pre-module binary **refuses** every pattern the new corpus adds
(`-e utf8`, `\p{...}`, `\x{...}`), which `out/premises.txt` §1/§2 already
records as the current behaviour.

**A stated gap.** The gate cannot cover the `--encoding=utf8` artifacts,
because there is no prior binary to compare them against. Those are covered by
the corpus and the differential, not by identity. Saying so is the point:
`[M6.6.2]` wave E's identity gate caught a 37-byte generated-comment
regression precisely because its scope was known.

### 8.2 The sabotage rows

One per load-bearing claim, following D69's shape. **ASSERTED** list, with the
failing direction each needs:

| # | claim | sabotage | why only this instrument sees it |
|---|---|---|---|
| S-U1 | the fold is applied BEFORE negation (§4.3) | swap the order in the one constructor | both orders produce case-closed sets; only behaviour on `[^k]`/U+212A differs |
| S-U2 | the fold is a CLOSURE, not a pairing (§4.2a) | replace the closure with one round of "add the partner" | `k`↔`K` still works; only U+212A fails |
| S-U3 | the fold happens on CODE POINTS, before lowering (§4.2c) | move it after the byte lowering | `[a-z]` still folds to `[A-Z]`; only U+212A/U+017F are lost |
| S-U4 | `la_widths` uses CHARACTER width (§5.6) | point it back at `pcrec_maxw` | every ASCII lookbehind still compiles; only `(?<=[a\x{3b1}])` refuses |
| S-U5 | `back_step` walks characters (§5.2) | make it `pos - k` | identical under `byte`; under utf8 it lands mid-character |
| S-U6 | `next_pos` finds a boundary (§5.1) | make it `pos + 1` | only a find-all over an empty match on a multi-byte subject sees it |
| S-U7 | the surrogate range is excluded from every lowered set (§2.3) | include it | only a subject containing a CESU-8-shaped sequence sees it |
| S-U8 | `minw`/`maxw` are per-class exact (§5.6.1) | return the old constant 1 | answers unchanged (a looser bound is sound); only the MRL stamp moves |

**S-U8 is the one worth noticing**: it changes **no answer**, because a looser
MRL bound prunes less and can never delete a match. Only a structural or
stamp-reading check can see it — the S68 shape, and the reason the design
names it rather than assuming the corpus covers it.

### 8.3 Population sizing for the blinded corpus

**ASSERTED**, sized from the measured surfaces rather than guessed:

| axis | cells | source |
|---|---|---|
| encoded-length coverage (1/2/3/4-byte characters × literal/class/quantified/negated) | ~64 | §2.3 |
| the 1-byte↔multi-byte class boundary (`[a\x{3b1}]` shapes) | ~24 | §5.6's population |
| invalid UTF-8 (9 ill-formed kinds × before/after/through) | ~27 | `out/invalid_utf.txt` |
| `\p{...}` general categories (37 accepted spellings × 2 polarities × in/out members) | ~150 | `out/uprops.txt` §1 |
| `\p` refusals (30 measured error-147 bodies + blocks) | ~34 | `out/uprops.txt` §1 |
| caseless: 1:1 pairs, cross-block folds, the closure, fold-before-negate | ~60 | `out/caseless.txt` §1/§3/§4 |
| caseless 1:n NON-matching (the §4.1 result as tests) | ~11 | `out/caseless.txt` §2 |
| lookbehind over variable-byte-width bodies | ~24 | `out/width.txt` §3 |
| `next_pos` / find-all over multi-byte subjects | ~20 | §5.1 |
| the byte-encoding control arm (every above pattern under `-e byte`) | mirror | §8.1 |

**~420 cells**, comparable to `lookaround`'s 457 blocks / 1,819 cases. The
D27 author gets an extract of §2.6, §3.1, §4.1–4.3, §5.6 and §7.1 — the
construct table, the measured semantics and the oracle rules — and **not**
§2.3, §5, §8 or §9, which are the implementation.

### 8.4 The compatibility question the cross-note names

The `[M5.0]` row asks this design to own the `maxw` change. §5.6 owns it, and
the **compatibility** half is: under `--encoding=byte`, `pcrec_minw` and
`pcrec_maxw` must answer **exactly what they answer today** for every pattern
in the corpus. That is not an argument, it is §8.1's gate — the MRL bound is
baked into emitted literals (`RX_PRUNE_*`), so a changed bound is a changed
artifact and the byte-identity gate fails. **The gate is the check; no
separate instrument is needed.**

---

## 9. Module and staging (charter (viii))

### 9.1 What is a module and what is not

**MEASURED** (`out/premises.txt` §1): pcrec's own refusal already rules this —
`encoding 'utf8' arrives with milestone M5 (**an engine axis, not a module**:
no `--features` name enables it)`.

| thing | kind | registry / gate |
|---|---|---|
| the UTF-8 **encoding backend** | an **encoding**, not a module | one `enc_utf8.c` + one row in `enc.c`'s table. `--encoding=utf8`. No `--features` name. |
| `unicode-props` (`\p` `\P` `\N{U+}` `\x{}`) | a **module**, already registered, `built = unbuilt` today | `--features unicode-props`; rows exist |
| the **fold** | **neither** | it is inside the one class constructor (D23). A module for it would be a second home for one rule. |
| `\X`, `\R` | module **`misc`** | measured, different module, out of scope (§11) |

**The third-encoding recipe is this milestone's own test**, and it is a
falsifiable prediction rather than a compliment: adding `enc_utf8.c` and its
row should touch **nothing** in `src/core`, `src/gen`, `cli/` or `lib/`.
§12 P-1 states what happens if it does.

**But the recipe does not cover the lowering**, and the design should be
honest that this is where DD-12 (7)'s "derailment signal" needs
interpretation. §2.1 puts the encoding lowering behind the same one-file-per-
backend rule; whether it lives in `src/gen/enc/` alongside the residual text
or in `src/ir/` behind a table of function pointers is an implementation
choice the panel should rule on. What is NOT negotiable is that no shared file
acquires an `if (enc == UTF8)`.

### 9.2 The staged landing order

Five stages, each with an acceptance that can be run before the next opens.

**STAGE 1 — the CharSet widening.** `A_CLASS` becomes intervals; every
producer (`\d`, `\w`, POSIX classes, ranges, literals) emits intervals; the
byte backend's lowering turns intervals back into the 32-byte bitmap.
`\x{...}` above 0xFF still refuses. **Nothing user-visible changes.**
*Acceptance:* §8.1's identity gate at 100% byte-identity on all four axes —
the whole corpus, since every pattern goes through this. This stage is a pure
refactor and its gate is total.

**STAGE 2 — the utf8 backend.** `enc_utf8.c` (four residual bodies), the
byte-sequence lowering, `\x{...}` above 0xFF under `--encoding=utf8`,
`-e utf8` starts compiling. §5.6's `pcrec_cwmin`/`pcrec_cwmax` land here
because lookbehind is already shipped and would otherwise be wrong the moment
utf8 compiles. *Acceptance:* the UTF `.rxt` corpus green; identity gate still
100% on `byte`; DD-12 (7)(a)'s **two M5-time structural checks** — hot-loop
shape identity ASCII-vs-UTF-8, and the second-backend validation of D58's
"revisit-when" names; S-U4/5/6/7 detected.

**STAGE 3 — `unicode-props`, general categories.** The UCD vendoring (§3.3),
the generated `.inc`, the category families of §3.4. **This stage does not
require stage 2** (§3.2) and could land in parallel; it is sequenced after it
only so that its corpus can test both encodings at once. *Acceptance:* PC-3's
name-axis sweep green; PC-4 differential over the category population; the
D65 `built` column flips for the `\p`/`\P` rows.

**STAGE 4 — DD-1, the fold closure.** `CaseFolding.txt`, the closure in the
one constructor, before negation. *Acceptance:* `out/caseless.txt`'s cells as
a corpus; S-U1/2/3 detected; the `byte` encoding's ASCII fold byte-identical.

**STAGE 5 — scripts and `Script_Extensions`.** Table weight only, no new
mechanism. *Acceptance:* PC-3/PC-4 over the script population.

**What is NOT staged, deliberately:** a UCP axis (§14 ASK 4), a word-class
seam entry (§5.4), `\X`/`\R` (module `misc`), UTF-16/32 (D18 earn-its-axis;
`[DD-12] (6)` already rules them out and no consumer asks).

---

## 10. What this design does NOT resolve

Stated plainly so the panel attacks the right things:

- **Whether `unicodedata`-free UCD vendoring is acceptable in this repo** —
  §3.3, ASK 2. Everything in §3.4 and §4.4 depends on the answer.
- **Whether pcrec may diverge from PCRE2's default UTF mode on ill-formed
  subjects** — §2.6, ASK 1. The design recommends yes and the recommendation
  is a user-visible semantic.
- **Where the encoding lowering lives** — §9.1. `src/gen/enc/` and `src/ir/`
  are both defensible; the panel should rule.
- **Whether one parameterised width function beats two** — §5.6.
- **The `.rxt` third oracle value** — §7.4, ASK 6, owned by the format.

---

## 11. Explicitly out of scope

`\X` (extended grapheme clusters) and `\R` — **MEASURED** as module `misc`,
not `unicode-props` (`out/premises.txt` §2). `\X` is the one construct in the
UTF neighbourhood that is genuinely not a class: a grapheme cluster is a
variable-length sequence with its own break algorithm, and it would be the
first construct whose width is unbounded at the character level. It belongs to
its own module and its own design gate.

UTF-16 and UTF-32 (`[DD-12] (6)`). PCRE2's `PCRE2_UCP` as a pcrec axis
(§14 ASK 4). Optimising `ENG_ATTEMPT`'s start loop for character boundaries
(§5.5). A two-value scan arm for the prefilter (§6.3) — measured as an
opportunity, declined under D77 until a UTF corpus exists to measure it on.

---

## 12. What would refute this — predictions for the panel

Written before the panel rather than after. Each is falsifiable.

- **P-1 — the third-encoding recipe holds.** Adding `enc_utf8.c` plus its
  registry row touches no file in `src/core`, `src/gen`, `cli/` or `lib/`.
  *Refuted by:* any shared file needing an edit. **If refuted, that is the
  design-stop signal DD-12 names, not a patch to write** — and the honest
  prediction is that the LOWERING (§9.1) is where it will bite, because the
  recipe was written for residual text and a lowering is not text.
- **P-2 — the identity gate is 100% at stage 1.** *Refuted by:* one
  non-identical artifact. The likeliest cause is an ordering difference in
  interval→bitmap conversion for a class whose producers overlap.
- **P-3 — pcrec's own lowering produces state counts within 2× of
  `out/sizing.txt`.** *Refuted by:* a `\p{L}` DFA over 566 states. The
  prototype shares no code with pcrec, so this is a real prediction.
- **P-4 — `\b` needs no seam entry without UCP** (§5.4). *Refuted by:* one
  subject where the byte-level word test and the character-level test disagree
  under `--encoding=utf8` at `\w = [A-Za-z0-9_]`. I believe no such subject
  exists; a sweep over multi-byte characters adjacent to word characters is
  the instrument.
- **P-5 — no corpus pattern's minimised DFA grows past a cap under utf8.**
  *Refuted by:* any corpus pattern that compiles under `byte` and hits
  `PCREC_MAX_DFA_STATES_TABLE` under `utf8`. §2.4 measures classes in
  isolation, **not** the products a real pattern builds — this is the
  measurement §2.4 does not make and the most likely place its comfort is
  misplaced.
- **P-6 — the `(?i)^(ss)\1$` witness in `enc_byte.c` is wrong and
  `^(k)\1$` is right** (§5.3). *Refuted by:* 10.46 matching the sharp-s cell
  under some options word this lane did not try.
- **P-7 — `\p{...}` under `--encoding=byte` needs no widening** (§3.2).
  *Refuted by:* a property whose sub-0x100 membership cannot be expressed as a
  256-bit bitmap, which is impossible, so the real refutation is a property
  whose *name* pcrec accepts and whose byte-tier answer diverges from 10.46's
  8-bit answer.
- **P-8 — 10.46 does simple folding only** (§4.1). *Refuted by:* any 1:n
  cell matching under any options word. This is the single result the most
  design depends on; §14 ASK 3 asks whether to make it a standing check rather
  than a one-time measurement, since a future PCRE2 could add full folding.

---

## 13. The implementation brief

Deliberately short: the stages in §9.2 are the brief, and each names its own
acceptance. Three cross-cutting obligations belong to every wave:

1. **D80** — anything a caller can observe updates `docs/spec/` in the SAME
   change. Stage 2 alone touches `match_api.md` §3.1.1 (the `next_pos`
   contract's "byte encoding" paragraph), §8.2 (`utf8` stops being refused),
   and `limits.md` if any cap moves.
2. **D76/D94** — any change to emitted scaffolding is an `abi` bump plus an
   identity-gate re-pin **in the same change**, with the site list found by
   grepping for the current abi number's readers, not hand-enumerated.
3. **Every wave states its own population.** The recurring defect in this
   house is a check whose population nobody counted (`learnings.md` §3); the
   sizing sub-lane in this very lane found a construction bug only because
   its self-check counted 10,916 samples rather than asserting correctness.

---

## 14. ASKs for Frank

Six. None is a ruling contradiction; each is a decision this lane deliberately
did not take.

**ASK 1 — invalid UTF-8 semantics (§2.6).** The design proposes that a
pcrec UTF-8 artifact treats an ill-formed sequence as **matching nothing**,
with no validation pass and no error return — which is what the automaton does
for free, what `PCRE2_MATCH_INVALID_UTF` does, and what M3 streaming requires.
It **diverges from PCRE2's default `PCRE2_UTF` mode**, which reports an error
for the whole subject. Accept the divergence? If not, an opt-in validation
entry point is owed and it is a new seam entry.

**ASK 2 — vendoring UCD data (§3.3).** `\p{...}` needs Unicode property
tables. Generating them from python is disqualified (version drift, measured);
generating them from libpcre2 is disqualified (one source wearing two hats —
`mod_uprops.c`'s own rule). The recommendation is to **vendor the UCD data
files at a pinned version** into `third_party/` and generate a `.inc` at build
time, as `cls_bits.inc` already is. This would be the first non-PCRE2
third-party data in the repository. Approve, and approve the pin (16.0.0,
matching libpcre2 10.46)?

**ASK 3 — should "simple folding only" become a standing check? (§4.1)** The
whole of §4 rests on a one-time measurement that 10.46 does no 1:n folding.
A future PCRE2 could add full folding, and the failure would be silent. Worth
a permanent cell in the PC-3/PC-4 differential, or accept it as a
re-measurement event on version bump (D26's addendum)?

**ASK 4 — is a UCP axis owed? (§4.5, §5.4, §7.1)** `PCRE2_UCP` re-defines
`\w \d \s \b` over the whole code-point space and accounts for **8 of 28**
measured divergence rows. pcrec has no such axis. Without one, pcrec's UTF-8
answers for those constructs are the non-UCP ones and the corpus must say so.
With one, §5.4's word-classification seam entry becomes necessary. The design
recommends **no UCP axis at M5** (D18 earn-its-axis; no consumer has asked)
and flags that it is the largest single divergence family.

**ASK 5 — `ENG_ATTEMPT`'s start loop (§5.5).** Under UTF-8 it tries
mid-character starts, which are harmless (no path) but wasted, up to 3 per
character. Fixing it means routing a shared emitter loop through a residual
entry, which S68 and `engine_callable = false` currently forbid. Leave it
(the design's recommendation, D77 — measure the loss first), or charter it?

**ASK 6 — the `.rxt` third oracle value (§7.4).** The format has
python-verifiable and `# pcre2-only`. UTF needs a third: python-verifiable
**through the `str` engine only** (5 of 28 measured cells). This lane did not
edit `docs/spec/rxt_format.md`. Route it to `[DD-13b]`, or charter a small
amendment now so stage 2's corpus has somewhere to live?
