# utf8_d27_extract.md — the [M5.0] blinded author's design extract

Extracted verbatim (per its own §8.3.2's include/exclude ruling) from
`docs/design/utf8_design.md` at commit `30de9e3a` by the manager, for the
D27-blinded author denied `src/` and `tests/`. The blinded author sees THIS
FILE and never the full design.

**Included** (per the source document's own §8.3.2, which sets this list):
§1.3 (the construct table); §2.6(a)-(e) and §2.6.1/§2.6.1.1 (the invalid-UTF-8
ruling and the per-entry `startpos` promise, plus the measurement the
`startpos` cells are written from); §2.7.3 (the two-cell refusal rule);
§3.1 and §3.4 (the measured `\p` acceptance surface and its ship/refuse
staging); §4.1-§4.3 (simple-folding-only, the closure, fold-before-negate);
§5.6's measured population table ONLY, not its resolution (§5.6.1-§5.6.5);
§7.1 and §7.1.1 (the verdict tally and the oracle predicate); §8.3's
population-sizing table and §8.3.1's subject-witness paragraph.

**Excluded**: §§2.1-2.5, §2.7.1-§2.7.2, §5.1-§5.5 and §5.6's resolution, §6,
§8.1, §8.2, §8.4, §8.5, §9, §12, §13, §14 — pcrec's internal representation
and compilation mechanism, its engine/selection consequences, the validation
plan, staging, predictions, the implementation brief, and Frank's rulings.
Where an included section named one of these by number or by an
internal mechanism's name, the reference below is replaced with a
behavioural description (see the cutter's notes at the end).

**Regenerate only by re-cutting this file from its source; never edit it
independently of `docs/design/utf8_design.md`.**

---

## 1.3 The construct table

For every construct in this milestone's neighbourhood: whether it SHIPS,
whether it REFUSES, and which module owns it.

| construct | 10.46 | owner | refuses today as | lands |
|---|---|---|---|---|
| `--encoding=utf8` | n/a (an option there) | **encoding**, not a module | `encoding 'utf8' arrives with milestone M5 (an engine axis, not a module)` | **stage 2** |
| `\x{HH...}` ≤ 0xFF | compiles at any options | base grammar | `\x{...} requires module 'unicode-props'` | **stage 1** |
| `\x{HH...}` > 0xFF | UTF only (err 134 otherwise) | base grammar, encoding-sensitive | same | **stage 2** (refuses under `byte`, as 10.46 does) |
| `\xHH` (bare, 2 digits) | compiles | base grammar | already ships | — |
| `\p{X}` / `\P{X}`, general categories | compiles at ANY options | `unicode-props` | `\p requires module 'unicode-props'` | **stage 3** |
| `\p{X}`, `Xan Xps Xsp Xuc Xwd L& Any Assigned` | compiles | `unicode-props` | same | **stage 3** (derived, no new data) |
| `\p{Greek}`, `\p{Script=…}`, `\p{sc=…}` | compiles | `unicode-props` | same | **stage 5** |
| `\p{scx=…}`, `\p{Script_Extensions=…}` | compiles | `unicode-props` | same | **stage 5** |
| `\p{Alphabetic}` and the boolean family | compiles | `unicode-props` | same | **REFUSES** at first landing |
| `\p{bc=…}`, `\p{Bidi_Class=…}` | compiles | `unicode-props` | same | **REFUSES** at first landing |
| `\p{InGreek}`, `\p{blk=…}` — **blocks** | **err 147** | `unicode-props` | same | **REFUSES PERMANENTLY** — reproducing 10.46's own refusal |
| `\p{^L}` (caret inside braces) | compiles | `unicode-props` | same | **stage 3**, with its family |
| `\N{U+HHHH}` | compiles under UTF | `unicode-props` | `\N requires module 'unicode-props'` | **stage 2** (it is `\x{}` by another spelling) |
| `(?i)` over non-ASCII | simple fold only | the one class constructor — **not a module** | n/a (the fold ships; its non-ASCII half does not exist yet) | **stage 4** |
| `\w \d \s \b` under UCP semantics | needs `PCRE2_UCP` | — | pcrec has **no UCP axis** | out of scope for this design |
| `\X` (grapheme cluster) | compiles under UTF | **`misc`** — a different module | `\X requires module 'misc'` | out of scope |
| `\R` | compiles | **`misc`** | `\R requires module 'misc'` | out of scope |
| UTF-16 / UTF-32 | PCRE2 has separate libraries | — | `unknown encoding 'utf16' (want byte, utf8)` | never |

Two rows worth reading twice: **`\p` is owned by a module and gated on
nothing else** — it works without `PCRE2_UTF`, which is what lets stage 3
be independent of stage 2. And **`\X`/`\R` belong to `misc`**, not to
`unicode-props` — so "everything Unicode" is not this tree's module
boundary.

---

## 2.6 Invalid UTF-8: the decision, taken deliberately

MEASURED:

**(a) The PATTERN is validated at COMPILE time**, with nine distinct error
codes naming the specific clause violated — `-22` isolated continuation
byte, `-23` illegal 0xFE/0xFF, `-8`/`-9` truncation, `-17` overlong, `-16`
surrogate, `-15` above U+10FFFF, `-13` five-byte form. This costs the
emitted artifact nothing and pcrec's compiler owes it.

**(b) Under `PCRE2_UTF` alone, an ill-formed SUBJECT is a whole-subject
precondition, checked before matching.** The discriminating cell: pattern
`a` on subject `61 FF 61` returns `ERRM -23`, **not** a match at offset 0 —
even though a valid `a` sits before the bad byte. So `PCRE2_UTF` pays an
O(n) validation pass on every match call.

**(c) `PCRE2_MATCH_INVALID_UTF` differs on all nine ill-formed subjects**,
and what it does is make ill-formed bytes a **barrier**: matches on either
side are found (`a` on `61 FF` gives `(0,1)`; on `FF 63` gives `(1,2)`),
matches *through* them are not (`a.c` on `61 FF 63` → no match; `\w+` on
`61 62 FF 63 64` → `(0,2)`, stopping at the barrier).

**(d)** Under `options=0` — pcrec's actual byte encoding — `a.c` on
`61 FF 63` **matches `(0,3)`**: a byte engine is delighted to consume 0xFF
as a character. So `MATCH_INVALID_UTF` is *not* the byte-wise semantics.
It is the semantics of a **byte-wise UTF-8 automaton**, which has no path
for an ill-formed sequence and therefore cannot match through one.

**THE RULING THIS DESIGN PROPOSES:**

> Under `--encoding=utf8`, pcrec's artifact **treats an ill-formed byte
> sequence as matching nothing**. There is no validation pass, no error
> return, and no error code for bad input. This is
> `PCRE2_MATCH_INVALID_UTF`'s answer on every cell measured, and pcrec gets
> it **for free from the automaton's structure** rather than from a check.

The cost is a stated divergence from PCRE2's DEFAULT UTF mode: a caller who
wants "tell me the subject is broken" gets "no match" instead.

**(e) The mid-character cursor.** A `startoffset` inside a character is
`ERRM -36 "bad offset into UTF string"` under `PCRE2_UTF`, and under
`MATCH_INVALID_UTF` it silently advances to the next character boundary
(start=1 on `αβ` returns `(2,4)`). pcrec's own answer falls out of the same
rule as (d) — a cursor mid-character has no path — which is exactly what
`next_pos` exists to make unreachable for the one caller who could hit it.

### 2.6.1 "No path" INVERTS for a negative assertion

"A cursor mid-character has no path" is a SAFE answer for a positive
match — no path means no match, which is a miss and never a false hit.
**For a negative assertion it is the opposite.** `(?!X)` succeeds exactly
when `X` has no path, so at a mid-character position `(?!α)` **SUCCEEDS**,
where a validating engine skips the position (`MATCH_INVALID_UTF`,
measured: start=1 on `αβ` returns `(2,4)`) or refuses it (`PCRE2_UTF`,
`ERRM -36`).

**§2.6(e)'s cure covers only ONE of three ways a cursor gets to a
mid-character position:**

| how the cursor gets there | protected? | the artifact's promise under `utf8` |
|---|---|---|
| the **find-all loop's own advance** | **YES** — the loop advances by `<prefix>_next_pos`, which walks to a character boundary | boundary by construction |
| a **caller-supplied `startpos`** to `<prefix>_search` | **NO** | the automaton's answer, which for a negative assertion differs from both PCRE2 UTF modes |
| `<prefix>_match`'s **anchored** entry at a caller-supplied position | **NO** | same |

**THE DESIGN'S POSITION:**

> **`startpos` must be a character boundary of the artifact's encoding.**
> A caller who passes a non-boundary gets a DEFINED answer — the
> automaton's — which is not PCRE2's answer in either UTF mode, and which
> for a leading negative assertion differs in the SUCCEEDING direction.
> `next_pos` is the supported way to produce a valid `startpos`, and the
> find-all loop already uses it.

This is a contract sentence, not an implementation note: a corpus must
cover it. **What makes this cheap to get wrong**: every instrument a
corpus author naturally writes starts at `startpos = 0`, which is a
boundary on every subject. A correct corpus needs an explicit **non-zero
mid-character `startpos`** cell on a leading `(?!` and a leading `(?<!` —
the two shapes where the answer inverts — rather than leaving the axis to
be covered by find-all cells that structurally cannot reach it.

#### 2.6.1.1 MEASURED — and there are THREE answers, not two

A ruling from Frank directed leaving pcrec's own unanchored start-search
loop alone, with the addendum "validate against oracles" — so this became
a measurement rather than an argument. Subject `αβ` (`CE B1 CE B2`,
boundaries at 0/2/4), every cell in all three option words:

| pattern | start | `PCRE2_UTF` | `MATCH_INVALID_UTF` | `options=0` (byte) | **pcrec/utf8 (ARGUED)** |
|---|---|---|---|---|---|
| `(?<!.)` | 0 bnd | `(0,0)` | `(0,0)` | `(0,0)` | `(0,0)` |
| **`(?<!.)`** | **1 MID** | **`ERRM -36`** | **`(2,2)`** | **no match** | **`(1,1)`** |
| `(?<!.)` | 2 bnd | no match | no match | no match | no match |
| `(?!.)` | 1 MID | `ERRM -36` | `(4,4)` | `(4,4)` | `(1,1)` |

**THREE DIFFERENT ANSWERS ON ONE CELL, and pcrec's is a fourth.**

- **`PCRE2_UTF` REFUSES** — `ERRM -36`, and **uniformly**: every
  mid-character start is `-36` regardless of pattern. It never answers at
  all.
- **`MATCH_INVALID_UTF` ADVANCES to the next boundary and then answers** —
  and it does **not** give the same answer as starting at that boundary.
  At start=1 it reports `(2,2)` where a start of 2 reports **no match**.
  The mid-character entry point acts as a **barrier** the lookbehind
  cannot cross, applying `MATCH_INVALID_UTF`'s own ill-formed-bytes rule to
  a truncated leading character. A reader who assumed "it just rounds the
  offset up" would have got this wrong.
- **`options=0`** has no notion of a boundary, so every offset is one.
- **pcrec under `--encoding=utf8`** answers `(1,1)`: at `pos=1, k=1` its
  mechanism walks back to 0, finds a lead byte declaring 2 bytes against a
  run of 1, and finds no valid step back — so the lookbehind body cannot
  run, the negative assertion succeeds, and the match is the empty one at 1.

**THE VACUITY GUARD, in the failing direction**: a mid-character start
differs from the boundary below it on **8 of 8** negative-assertion cells
under `PCRE2_UTF`. A 0 would have meant the table could not see the
phenomenon it exists for.

---

## 2.7.3 The explicit-`\x{>FF}` refusal stays DISTINCT

The rule is on the parser's LITERAL INPUT, never on a derived set:

| what | under `byte` | under `utf8` | why |
|---|---|---|---|
| `\x{3b1}`, or a range endpoint, WRITTEN above `MAXCP(enc)` | **compile error** | compiles | 10.46's own answer: err 134 *"character code point value in \x{} or \o{} is too large"* at `options=0`, accepted under `PCRE2_UTF` |
| a class reaching the encoding's maximum code point because a COMPLEMENT put it there | compiles | compiles | the user wrote `[^a]`; nothing above `0xFF` was named, and there is nothing to refuse |

One test, one place, applying a range check to the escape's own parse
site, where the written value is in hand. A derived set never passes
through it, because by then there is no written value to check. The two
cells above are the discriminating pair a stage-2 corpus owes: `\x{3b1}`
under `byte` refuses, `[^a]` under `byte` compiles.

---

## 3.1 What 10.46 actually accepts

MEASURED: 114 spellings tried, **83 compile, 30 are error 147 (unknown
property), 1 is error 146 (malformed)**.

| axis | verdict |
|---|---|
| one-letter general categories `C L M N P S Z` | **compile** |
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
| `\p{grEEk}`, `\p{l a t i n}` | **compile** — case and separators insignificant |

The property surface is much larger than a plain reading of the charter
would suggest: booleans and `Bidi_Class` are two whole axes beyond the
obvious general-category/script list. §3.4 (below) is where that gets
staged rather than shipped.

## 3.4 What ships, what refuses

ASSERTED staging:

| family | first landing | why |
|---|---|---|
| one- and two-letter general categories, `L&`, `Any`, `Assigned` | **SHIP** | ~5,000 code-point ranges of Unicode data total; one UCD file; the family every `\p` user reaches for first |
| `Xan Xps Xsp Xuc Xwd` | **SHIP** | PCRE2-specific, defined in terms of the categories above — derived, no new data |
| script names, `Script=`/`sc=` | **stage 5** | one more UCD file, ~160 names; nothing structural, purely table weight |
| `Script_Extensions=`/`scx=` | **stage 5, with scripts** | same file family |
| boolean properties (`Alphabetic`, `Math`, `Emoji`, …) | **REFUSE at first landing** | a third data family; no measured demand |
| `Bidi_Class=`/`bc=` | **REFUSE** | a fourth; no measured demand |
| **blocks** (`InGreek`, `blk=`) | **REFUSE PERMANENTLY** | 10.46 refuses them too (error 147). Reproducing a refusal is free and correct. |

A refused-but-well-formed body must refuse as `unicode-props` not
implementing it, never as unknown.

---

## 4.1 10.46 does SIMPLE folding only — so there are no one-to-many foldings

MEASURED. Eleven one-to-many cells — ß/SS, ß/ss, SS/ß, ss/ß, U+FB01/fi,
fi/U+FB01, U+FB03/ffi, U+0149, U+01F0, U+1E96, U+0390 — under
`PCRE2_UTF|PCRE2_CASELESS` and under `…|PCRE2_UCP`:

> **1:n cells that matched under some caseless option: 0 of 11**

And from the other side, `[ß]` caseless does not match `"ss"` or `"SS"`,
and `[s]` does not match `ß`.

**This result matters because of what it removes.** A 1:n fold cannot
live in a set — it is a *sequence*, so it would force a caseless literal
to become an alternation and a caseless class to hold something a class
cannot hold. There is no PCRE2 behaviour requiring pcrec to build that.

Pcrec's fold applies to the SET, computed once, at parse time. Only the
set is now code points instead of bytes.

### 4.1.1 The 0-of-11 becomes a standing check

Frank's ruling: the eleven one-to-many candidates become a permanent check
riding the existing PCRE2-differential machinery, firing the day the
oracle's own folding behaviour changes — because the absence of 1:n
folding is what lets a caseless class stay a class; that is a structural
dependency, not a tuning choice, and the failure mode if it silently
changed underneath pcrec would be that a future PCRE2 with full folding
starts matching cells pcrec answers "no" to, with nothing noticing. The
check asserts every one of the 11 named cells (under both
`PCRE2_UTF|PCRE2_CASELESS` and `…|PCRE2_UCP`, 22 assertions total) does
**not** match; a cell that starts matching is a hard failure, not a skip.
This becomes a permanent check in pcrec's validation suite, landing ahead
of the fold code itself, because it is a check on the ORACLE's behaviour
and not on pcrec's — so it can and should run before any of this module
is built.

## 4.2 It is a CLOSURE, not a pairing — and it reaches outside the range

MEASURED. Three findings that constrain the implementation:

**(a) Equivalence classes have more than two members.** `k` ↔ `K` ↔
U+212A (KELVIN) all match each other; so do `s` ↔ `S` ↔ U+017F (LONG S). A
constructor that "adds the other case" from a single case-mapping table
gets these wrong. It must compute the **closure** of the set under the
fold relation.

**(b) The partner is often in a different block.** Measured matching
pairs: KELVIN U+212A ↔ k, ANGSTROM U+212B ↔ å, OHM U+2126 ↔ ω, MICRO
U+00B5 ↔ μ, LONG S U+017F ↔ s, final sigma U+03C2 ↔ σ ↔ Σ. And two that
**do not** fold: U+0130 (dotted capital I) and U+0131 (dotless i) match
neither `i` nor `I` — Unicode's default simple case folding, and a naive
`toupper`/`tolower` table would get both wrong in opposite directions.

**(c) THE CLOSURE ADDS CODE POINTS FAR FROM THE WRITTEN ONES.** The
sharpest cell: **`[a-z]` under caseless matches U+212A** (3 bytes) and
**U+017F** (2 bytes). So the fold cannot be a post-pass over byte ranges —
by the time the set is byte ranges, U+212A is not adjacent to anything in
`[a-z]`. **The fold must happen while the set is still code points.**

**(d) A consequence for literals.** Because folding is 1:1 but the
partners have different encoded lengths, **a caseless single-character
match consumes a variable number of bytes**: `(?i)k` against U+212A
matches `(0,3)`. Under UTF-8, a caseless literal is a code-point class
whose members encode to different byte counts.

## 4.3 Fold before negate, over UTF

MEASURED. The rule that the caseless fold is applied to a set BEFORE
negation holds under UTF, including across blocks:

| cell | result |
|---|---|
| `[^k]` caseless on `K` | no match |
| `[^k]` caseless on **U+212A** | **no match** ← the whole test |
| `[^K]` caseless on `k`, on U+212A | no match |
| `[^s]` caseless on U+017F | no match |
| `[^a-z]` caseless on `A` | no match |
| `[^\p{Ll}]` caseless on `A` | no match |

The negation is over the **closed** set. The fold closure is applied while
the class is still a set of code points, and negation complements the
closed result — the observable order is fold, then negate — exactly as it
is today for the byte tier.

---

## 5.6 The measured population of variable-byte-width fixed-lookbehind bodies

MEASURED: PCRE2 measures lookbehind length in **CHARACTERS**.

| pattern | compiles under UTF | `PCRE2_INFO_MAXLOOKBEHIND` |
|---|---|---|
| `(?<=a)x` | yes | 1 |
| `(?<=\x{3b1})x` | yes | **1** ← 2 bytes, reported as 1 |
| `(?<=[a\x{3b1}])x` | **yes** | **1** ← 1-or-2 bytes, ONE branch |
| `(?<=.)x` | yes | 1 |
| `(?<=a\x{3b1})x` | yes | 2 |
| `(?<=a*)x` | **err 125** | — |

The discriminating cell is row 3: **one branch, fixed at one character,
variable at one-or-two bytes, and 10.46 compiles it.**

**THE POPULATION THAT MAKES THIS CONCRETE.** MEASURED — every body below
is accepted by 10.46 as fixed-width (`MAXLOOKBEHIND` 1) and has more than
one observed byte width:

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

**6 of 6** plain bodies are variable-byte-width, and the two caseless rows
are the same phenomenon arriving through the fold closure (§4.2(c)). A
correct implementation must compile every one of these bodies as a
lookbehind; a corpus must contain all eight of them.

---

## 7.1 The D27 goal-facts list

MEASURED: 28 cells, each in four columns — libpcre2 at `PCRE2_UTF`, at
`PCRE2_UTF|PCRE2_UCP`, python `re` over `str`, and python `re` over
`bytes`.

**The four-column structure is itself the finding.** python has one
engine per subject type and PCRE2 has two UTF modes, so "python vs PCRE2"
is not one comparison. `\w` over a Greek letter is FALSE in python-bytes,
FALSE in PCRE2/UTF, and TRUE in both python-str and PCRE2/UTF|UCP. **A
corpus author told only "python disagrees" would mark the wrong cells.**

Verdict tally over the 28 rows: **10 PCRE2-ONLY, 8 UCP-SPLIT, 5
PY-STR-ONLY, 5 ALL-AGREE.**

| verdict | count | what the author does |
|---|---|---|
| `PCRE2-ONLY` | 10 | mark `# pcre2-only`; libpcre2 rules the cell. These are `\p{...}`, `\x{...}`, `\X`, `\R`, class ranges over non-ASCII, quantified multi-byte characters, an ill-formed subject — **python `re` cannot express the syntax at all**, which is a stronger reason than "disagrees" |
| `UCP-SPLIT` | 8 | `\w \d \s \b \W` over non-ASCII. **pcrec has no UCP axis**, so the corpus must state which semantics it expects — pcrec's answer is the non-UCP column, and **python `re` over BYTES is the arbitrating oracle; see §7.1.1** |
| `PY-STR-ONLY` | 5 | `.`, `.{2}`, `[^a]` over multi-byte characters, caseless LONG S. python's `str` engine is the right oracle; the corpus's `bytes`-comparison tier is not |
| `ALL-AGREE` | 5 | write the cell, python verifies it |

**The `PY-STR-ONLY` row changes what oracle a corpus must use**: comparing
against python's bytes engine is correct for the byte tier and wrong for
the UTF tier on 5 of 28 measured cells.

### 7.1.1 The UCP-SPLIT rows' ARBITRATING ORACLE

**THE ORACLE IS PYTHON `re` OVER `bytes` ON SEVEN OF THE EIGHT ROWS, AND
THE EIGHTH IS THE INTERESTING ONE.**

Every `UCP-SPLIT` row, `py/bytes` against `pcre2/UTF` — the non-UCP
column, which is pcrec's semantics:

| cell | `pcre2/UTF` = pcrec | `py/bytes` | |
|---|---|---|---|
| `\w` over a Greek letter | no | no | ✓ |
| `\w` over an Arabic-Indic digit | no | no | ✓ |
| `\d` over an Arabic-Indic digit | no | no | ✓ |
| `\s` over NBSP U+00A0 | no | no | ✓ |
| `\s` over U+2028 line sep | no | no | ✓ |
| `\b` before a Greek letter | no | no | ✓ |
| **`\b` between ASCII and Greek** | **MATCH(0,3)** | **MATCH(0,3)** | ✓ |
| **`\W` over a Greek letter** | **MATCH(0,2)** | **no** | **✗** |

**7 of 8.**

**THE SEVENTH ROW IS WHY THE SEVEN ARE A RESULT AND NOT A COINCIDENCE.**
Six of the agreeing cells are `no` on both sides, and an oracle that
simply refused everything non-ASCII would score six. `\b` between ASCII
and Greek is the **discriminating** one: the non-UCP answer is MATCH and
the UCP answer is `no` — the opposite direction from every other row —
and `py/bytes` gives MATCH. So it is tracking the non-UCP SEMANTICS, not
exhibiting a bias that happens to agree. **That row is the control**, and
a corpus that drops it loses the evidence for this ruling.

**THE EIGHTH ROW FAILS FOR A UNIT REASON, AND THE UNIT REASON IS THE WHOLE
POINT OF THIS MILESTONE.** `\W` over `α` (`CE B1`):

- **PCRE2/UTF** — and pcrec under `--encoding=utf8` — asks "is this
  CHARACTER a non-word character", answers yes, and **consumes both
  bytes**: `MATCH(0, 2)`.
- **python-bytes** asks "is this BYTE a non-word byte", answers yes for
  `0xCE`, and consumes **one** byte; against an anchored `^\W$` that
  leaves `0xB1` unmatched, so the cell reads `no`.

The two agree perfectly on the PREDICATE (α is not a word character) and
disagree on the UNIT. **python-bytes has no character notion at all**, so
it can verify a UCP-SPLIT cell exactly when the cell's answer does not
depend on one class consuming a multi-byte character.

**AND `py/str` DOES NOT RESCUE IT** — the same row reads `no` there too,
for the opposite reason: python's `str` engine gives `\w` Unicode
semantics, so α IS a word character and `\W` does not match at all.
**Neither python engine gives pcrec's answer on this cell.**

**SO THE RULE THE BLINDED AUTHOR GETS IS A PREDICATE, NOT A VERDICT
LABEL:**

> A `UCP-SPLIT` cell is **python-verifiable through the `bytes` engine** —
> and must NOT be marked `# pcre2-only` — **unless the expected answer is
> a MATCH that consumes a multi-byte character.** Those cells are
> `# pcre2-only`: `\W`, `\D`, `\S` and `[^…]` over non-ASCII. The
> complemented forms, in other words, and only when they match.

**THE VERDICT COLUMN AND THE ORACLE COLUMN ARE DIFFERENT PARTITIONS.**
`VERDICT` answers *"which engines' semantics diverge here"*. `ORACLE`
answers *"who can check pcrec's expected answer"* — and it depends on the
UNIT each candidate oracle counts in, which no verdict label carries. The
`\W`-over-Greek cell is `UCP-SPLIT` by verdict and `PCRE2-ONLY` by oracle.
The `PY-STR-ONLY` row above already contains the same phenomenon — `[^a]`
over multi-byte characters is `\W`'s cell one spelling over.

**THE ONE THING THIS DOES NOT SETTLE**: the oracle confirms pcrec's
answer is *self-consistent with the non-UCP definition*. It does not make
the non-UCP answer the RIGHT one for a user who wanted UCP — that question
is open and no oracle here decides it.

---

## 8.3 Population sizing for the blinded corpus

**THE UNIT.** This design sizes in **BLOCKS**. A `.rxt` **block** is one
`pattern` plus its directives; a **case** is one `m`/`n`/`g` line.

> **Subjects per block: 4** — for a UTF-8 axis the discriminating subjects
> are a member, a non-member, a member at a different encoded length, and
> a boundary or ill-formed neighbour. That is the smallest set that
> distinguishes "the class is right" from "the class is right for
> one-byte members".

| axis | derivation | blocks | cases (×4) |
|---|---|---|---|
| encoded-length coverage | 4 lengths × 4 contexts (literal / class / quantified / negated) × 4 shapes (bare, in a class, in a range, after a quantifier) | **64** | 256 |
| the 1-byte↔multi-byte class boundary (`[a\x{3b1}]`) | 6 boundary shapes × 4 spellings (explicit `\x{}`, literal UTF-8, range endpoint, `\p`) | **24** | 96 |
| invalid UTF-8 | 9 measured ill-formed kinds × 3 positions (before / after / through the bad bytes) | **27** | 108 |
| `\p{…}` general categories | 30 two-letter + 7 one-letter = **37** accepted spellings × 2 polarities (`\p`/`\P`) × 2 (in-member, out-member) = 148, rounded | **150** | 600 |
| `\p` refusals | 30 measured error-147 bodies + 4 block spellings (`InGreek`, `Block=Greek`, `blk=Greek`, `IsGreek`) | **34** | 34 (a refusal has one case) |
| caseless: pairs, cross-block folds, closure, fold-before-negate | 6 measured cross-block pairs + 2 measured non-folds + 4 closure shapes (`k`/`K`/U+212A three ways) + 3 fold-before-negate shapes × 4 spellings ≈ 60 | **60** | 240 |
| caseless 1:n NON-matching | the 11 measured cells of §4.1, one block each | **11** | 22 (match + reverse direction) |
| lookbehind over variable-byte-width bodies | the 8 measured bodies of §5.6 × 3 (positive, negative, call-bearing) | **24** | 96 |
| `next_pos` / find-all over multi-byte subjects | 4 subject shapes × 4 patterns (empty, nullable, anchored, unanchored) + **4 mid-character-`startpos` cells on leading `(?!`/`(?<!`** (§2.6.1) | **20** | 80 |
| **the surrogate SUBJECT witness** | **3 surrogate encodings (`ED A0 80` low, `ED BF BF` high, a CESU-8 pair) × 3 patterns (`.`, `[^a]`, `\p{L}`)** | **9** | 27 |
| the byte-encoding control arm | every block above re-run under `-e byte`, expecting refusal-or-identity | mirror | mirror |
| **TOTAL** | | **423 blocks** | **≈ 1,559 cases** |

### The surrogate subject needs a witness, not a compile-time check

The promise being tested is that *the surrogate range is excluded from
every lowered set*. The ~27 invalid-UTF-8 cells elsewhere in this corpus
are **COMPILE-TIME refusals** — patterns PCRE2 rejects before matching —
and they cannot exercise this promise, because it is not about what
compiles; it is about what a compiled automaton **accepts**.

> The witness is a **SUBJECT**: `ED A0 80` … `ED BF BF` (the UTF-8-shaped
> encoding of a surrogate scalar, which is not valid UTF-8 and has no
> path) fed to a compiled `-e utf8 '^.$'`, `'^[^a]$'` and `'^\p{L}$'`. A
> correct artifact **rejects** every one of these subjects.

That is the 9-block row in the population table above (the surrogate
SUBJECT witness).

---

## Cutter's notes

Edits made to included sections while producing this extract (all
mechanical — no content judgment beyond what the source's own §8.3.2
ruling already made):

1. §2.6(e): dropped the internal cross-reference "§5.1 shows this is..."
   and stated the promise ("exactly what `next_pos` exists to make
   unreachable...") directly, since §5.1 itself is excluded.
2. §2.6.1.1: dropped the internal engine-name reference ("`ENG_ATTEMPT`'s
   start loop") in favor of "pcrec's own unanchored start-search loop".
3. §2.6.1.1: omitted one paragraph of the source ("AND THIS CELL IS A
   SECOND, INDEPENDENT WITNESS...") that analyzed an internal repair by
   naming an excluded mechanism and two internal error-handling symbols;
   it was corroborating evidence for the same measured table already
   included here, not an additional promise.
4. §2.6.1.1: rewrote the "pcrec's mechanism" sentence ("at `pos=1, k=1`
   its mechanism walks back to 0...") to describe the observable behaviour
   without naming the internal function the source names.
5. §2.7.3: dropped a cross-reference to the general §2.7 discussion,
   restating the range-check rule in place.
6. §4.1.1: dropped the sabotage-row id and its associated internal
   check-naming convention, replacing the sentence with "This becomes a
   permanent check in pcrec's validation suite."
7. §4.3: replaced a named internal constructor function with "pcrec's
   single class-construction step."
8. §5.6: cut the section immediately after the population table and its
   one-sentence conclusion, per the source's own instruction to include
   the table only and not its resolution (§5.6.1-§5.6.5); also dropped
   the source's framing paragraphs that quoted the `[M5.0]` cross-note's
   internal function/field names, keeping only the measured PCRE2 facts.
9. §7.1.1 / §8.3.1: dropped a sabotage-row id and its associated internal
   assertion-macro name from the surrogate-witness paragraph, restating
   the same corpus obligation without naming either.
10. §8.3's population table: retitled the surrogate-witness sub-heading to
    drop the sabotage-row id it originally carried.

## Sentences I was unsure about (flagging rather than deciding silently)

- §2.6.1.1's omitted paragraph (see cutter's note 3) contained the
  strongest available justification for *why* the mid-character
  `startpos` population must include the specific pair "a well-formed
  subject with a caller-supplied `startpos`" rather than only ill-formed
  subjects. I judged that justification to be implementation reasoning
  (it walks through what an unrepaired internal mechanism would do) and
  cut it, but the corpus requirement itself ("mid-character `startpos`
  cells, not just the nine ill-formed kinds") is real and I was not fully
  sure it survived clearly enough in what I kept. I did NOT add it back
  explicitly to avoid re-introducing the mechanism discussion — flagging
  it here instead.
- The source's §7.1.1 closing paragraph ties the oracle predicate to "a
  future `.rxt` oracle value" not yet implemented. I dropped that forward
  reference as it named an excluded section (§7.4) and an excluded ASK
  number; I'm not fully sure whether the blinded author should be told
  that no such third oracle value exists yet in `.rxt` syntax today, since
  that could affect how they'd try to encode the `# pcre2-only` vs
  python-verifiable distinction in their corpus. Left unstated here.

**Manager's post-cut edits (2026-09-05, review pass):** four residual
vocabulary leaks fixed — the §2.7.3 complement cell, the §3.4 staging
table's data-size note, §4.3's closure heading and its closing paragraph
each named the class representation or the pass that consumes it; all four
restated behaviourally (the observable fold-then-negate order and the
promise cells are unchanged).
