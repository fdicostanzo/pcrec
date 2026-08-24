# sr_d27_extract.md — the [DD-14] blinded author's design extract

Extracted verbatim from `docs/design/subroutines_design.md` (sections 2, 3,
10.1) plus the post-approval rulings that touch this module
(`docs/dev/decisions.md` D71 items 1/4/5, D73, and the [DD-14.LB] amendment
in §3.4(d)) by the manager ahead of the [DD-14] blinded corpus. The blinded
author sees THIS FILE and never the full design: §§1, 4-9, 11-14 describe the
implementation, the linkage, the call graph, `W`, the gate and the sabotage
rows, which D27 denies.

## 2. The construct table (charter — CONSTRUCTS)

### 2.1 The one cell that separates a call from a reference

`(a|b)\1` and `(a|b)(?1)` both compile, both look like "group 1 again", and
they are different constructs. The discriminator is one cell:

| pattern | on `"ab"` | verdict |
|---|---|---|
| `(a\|b)\1` | **nomatch** | a REFERENCE — it wants the same TEXT |
| `(a\|b)(?1)` | **(0,2)** | a CALL — it re-RUNS the alternation |

MEASURED, `out/spellings.txt` A1/A2. The same table against `"aa"` — where
both a call and a reference match — is printed beside it precisely because a
compile-status column would have told a reader nothing.

### 2.2 Every spelling, and whether pcrec ships it

MEASURED on libpcre2 10.46 and python 3.14 `re`, `out/spellings.txt`
A1/A2/A7.

| spelling | 10.46 | python | kind | pcrec |
|---|---|---|---|---|
| `(?1)` … `(?9)` | call | ERR | call | **SHIPS** (`features recursion`) |
| `(?10)`, `(?12)` … | call | ERR | call | **SHIPS** |
| `(?-1)` … `(?-9)`, `(?-01)` | call, relative left | ERR *(read as a flag group)* | call | **SHIPS** |
| `(?-10)` and beyond | call | ERR | call | **SHIPS** |
| `(?+1)` … `(?+9)` and beyond | call, relative right | ERR | call | **SHIPS** |
| `(?&name)` | call | ERR | call | **SHIPS** (`features recursion,named-groups`) |
| `(?P>name)` | call | ERR | call | **SHIPS** (`features recursion,named-groups`) |
| `\g<1>`, `\g<name>`, `\g<-1>`, `\g<+1>` | call | ERR *(bad escape)* | call | **SHIPS** |
| `\g'1'`, `\g'name'`, `\g'-1'` | call | ERR | call | **SHIPS** |
| `(?R)`, `(?0)` | whole-pattern call | ERR | call | **SHIPS** |
| **`\g<0>`, `\g'0'`** | **whole-pattern call** | ERR | call | **SHIPS** |
| **`(?01)`, `(?001)`, `(?0001)` …** | **group 1** | ERR | call | **SHIPS** |
| **`(?00)`, `\g<00>`, `\g'00'`** | **the ROOT** | ERR | call | **SHIPS** |
| **`(?-01)`, `\g<-02>`** | relative, leading zero | ERR | call | **SHIPS** |
| `\1`, `\g1`, `\g{1}`, `\g{-1}` | reference | `\1` only | reference | already ships — module `backrefs` (`features backrefs`), NOT this module |
| `\k<n>`, `\k'n'`, `\k{n}`, `(?P=n)`, `\g{n}` | reference | `(?P=n)` only | reference | already ships — module `backrefs`, NOT this module |
| `(?(DEFINE)…)` | a never-executed container | ERR | the DEFINE idiom | **SHIPS as this module** (§2.5) |
| **`(?:(…)){0}` — a callee parked under `{0}`** | a never-executed definition | ERR | the pre-DEFINE idiom | **SHIPS** (a repeat + a group, both already shipped) |

**EVERY SPELLING SHIPS.** There is no refusal in this module's own territory
comparable to `lookaround`'s variable-length lookbehind. Every refusal you
can find belongs to another module or another construct — see §5 below
("refusals that exist") for the actual list; do not go looking for a
recursion-specific decline that does not exist.

**RULING (D71 item 4, 2026-08-23):** `(?(DEFINE)…)` joins module `recursion`
as of this ruling. Before it, `(?(DEFINE)` was refused as module
`conditionals`'; now it SHIPS as this module's own construct, lowered as
exactly the `{0}`-callee shape the row above already covers. **The `(?:X){0}`
idiom and `(?(DEFINE)(?<name>X))` are stated by this ruling to be the SAME
PROGRAM** — no corpus block should treat them as merely equivalent behaviour;
they are one lowering with two spellings, and a corpus that only ever
exercises one of the two spellings has not covered the other.

### 2.3 The relative and forward forms, and what they resolve to

MEASURED, `out/spellings.txt` A3, with subjects chosen so the WRONG target
gives a different answer rather than merely a different capture:

| pattern | subject | 10.46 | what it proves |
|---|---|---|---|
| `^(a)(b)(?-1)$` | `"abb"` | (0,3) | `(?-1)` is the NEAREST group to the left — group **2** |
| `^(a)(b)(?-2)$` | `"aba"` | (0,3) | `(?-2)` is group **1** |
| `^(?+1)(a)$` | `"aa"` | (0,2), g1=(1,2) | `(?+1)` is a **forward** call — group 1's pattern runs BEFORE group 1 does |
| `^(?+2)(a)(b)$` | `"bab"` | (0,3) | `(?+2)` counts forward past one group |
| `^(a)(?-01)$` | `"aa"` | (0,2) | a leading zero is accepted |
| `^\g<+1>(a)$` | `"aa"` | (0,2) | `\g<±N>` obeys the same relative rule |

**THE FORWARD CALL IS THE SHAPE THAT MAKES A CALL UNLIKE A REFERENCE**, and it
is one cell: `^(?+1)(a|b)$` on `"ab"` matches, while the forward *reference*
`^\2(a|b)(c)$` on `"abc"` does not — a forward reference can only ever read an
unset group, a forward call runs the group's pattern.

Relative resolution is **at the call site's own group count** (the number of
`(` seen so far), stored as a computed absolute number.

### 2.4 `(?R)`, `(?0)`, `\g<0>` — "the whole pattern" INCLUDES the anchors

MEASURED, `out/spellings.txt` A4/A7a. One cell settles what "the whole
pattern" means:

| pattern | `"aabb"` | |
|---|---|---|
| `^(a(?1)?b)$` | **(0,4)** | `(?1)` calls GROUP 1 — the anchors are outside it |
| `^(a(?R)?b)$` | **nomatch** | `(?R)` re-runs `^(a(?R)?b)$`, **`^` and `$` included**, so the inner `^` fails at offset 1 |
| `^(a(?0)?b)$` | **nomatch** | `(?0)` is `(?R)` |
| `^(a\g<0>?b)$` | **nomatch** | and so is `\g<0>` |
| `(a(?R)?b)` unanchored | (0,4) | with the anchors gone, `(?R)` reaches depth 2 |

**This is the single most counter-intuitive fact in this module, and the one
an implementer is most likely to get wrong in the same direction a promise-
first author might.** `\g<0>` and `\g'0'` behave exactly as `(?R)` on all four
cells above; they are call spellings, not "call group 0", because there is no
group 0 body — the target is the AST root.

#### 2.4a Leading zeros

MEASURED, `out/wrapped_target.txt` axis Z, on the **anchored** discriminator
above (`(?R)` answers nomatch on `"aabb"`; a call to group 1 answers (0,4)):

| pattern | `"aabb"` | target |
|---|---|---|
| `^(a(?1)?b)$` | (0,4) | group 1 |
| **`^(a(?01)?b)$`**, `^(a(?001)?b)$`, `^(a(?0001)?b)$` | **(0,4)** | **group 1** |
| `^(a(?R)?b)$`, `^(a(?0)?b)$` | nomatch | the root |
| **`^(a(?00)?b)$`** | **nomatch** | **the root** |
| `^(a\g<1>?b)$`, **`^(a\g<01>?b)$`**, **`^(a\g'01'?b)$`** | (0,4) | group 1 |
| `^(a\g<0>?b)$`, **`^(a\g<00>?b)$`**, **`^(a\g'00'?b)$`** | nomatch | the root |

and the relative forms take a leading zero too — `^(a)(b)\g<-01>$` and
`^(a)(b)(?-01)$` match `"abb"`, `^(a)(b)\g<-02>$` matches `"aba"` — while a
**relative value of zero** stays **error 126** in every spelling (`(?-00)`,
`(?+00)`, `(?-0)`, `\g<-0>`).

> **THE RULE, uniform across the `(?` and `\g` doorways: parse the WHOLE DIGIT
> RUN as decimal; the value 0 is the ROOT; a RELATIVE value of 0 is error
> 126.** `(?0…)` is a one-digit-prefix trap: `(?0` alone is not enough to know
> the target, the whole run matters.

### 2.5 The `(?(DEFINE)…)` idiom and its exact substitutes

MEASURED, `out/spellings.txt` A5/A7b and `out/premises.txt` axis A/B.
`(?(DEFINE)(?<w>X))` is a conditional group whose condition is never true, so
its body never runs lexically and exists only to be called. Per D71 item 4
(above) it now SHIPS as this module's own construct.

Three DEFINE-less spellings of the same intent, against the DEFINE form over
11 subjects (`out/spellings.txt` A7b) — useful population material even
though DEFINE itself now ships:

| spelling | agrees with DEFINE | why |
|---|---|---|
| `^(?!)(?<w>X)\|^BODY$` | **11 / 11** | the `(?!)` kills the declaring branch, the name is still declared, the call still resolves — an exact substitute |
| `^(?:(?<w>X))?BODY$` | **9 / 11** | the optional group RUNS, so it eats input and leaves a capture: on `"foo-bar"` the DEFINE form gives g1 **unset** and this gives g1 **(0,2)** |
| `^(?<w>X)?+BODY$` | **fails outright** | the possessive optional consumes and will not give back |

The `(?!)`-guarded-branch spelling and the plain `(?:X){0}` idiom (§2.2) are
both exact substitutes on every measured cell.

### 2.6 Quantified calls, and the empty-body guard

MEASURED, `out/atomicity.txt` T5:

| pattern | subject | 10.46 |
|---|---|---|
| `(?&g){2}`, `(?&g)+`, `(?&g)*` | as written | ordinary bounded/unbounded repeats of a call |
| `(?(DEFINE)(?<g>a?))(?&g)*` | `"aaa"` | (0,3) — a NULLABLE callee under `*` terminates |
| `(?(DEFINE)(?<g>))(?&g)*` | `""` | (0,0) — an EMPTY callee under `*` terminates |
| `^(a?)(?1)*$` | `"aaa"` | (0,3) |
| `^(?R)*$` | `""` | **`rc -52`** — the give-up, not a match |

So a call is a repeatable item, and quantified calls compile and behave
sensibly in general — but see §5 below: `^(?R)*$` and its kin are a
DEPTH-CAPACITY give-up cell, worth putting directly in a corpus as a `gu`
case rather than as a match/nomatch guess.

## 3. The semantics, measured on libpcre2 10.46

### 3.1 Captures: the callee WRITES and the RETURN restores (H-RESTORE)

**MEASURED, `out/captures.txt` C2 — via a live callout INSIDE the called
body, not an after-the-fact inference:**

```
^((a)(?C1))(?1)$   on "aa"  ->  (0,2)  g1=(0,1) g2=(0,1)
    C1 at pos 1  caps=[None, (0,1)]     <- the LEXICAL run
    C1 at pos 2  caps=[(0,1), (1,2)]    <- INSIDE the call: g2 is (1,2) here
```

At the second firing g2 is (1,2) — the callee wrote it — and the final
answer is g2 = (0,1). **The write happened and the return undid it.** This
is the depth-3 cell shape to test with: an outer capture, an inner capture
written and read live during the call (via callout or, for a blinded corpus
without callout access, by constructing subjects/patterns where the
DURING-call value would leak into the final answer if it were not restored —
e.g. what happens to a group referenced again after the call returns), and
the value AFTER return.

**THE CALLEE INHERITS THE CALLER'S CAPTURES.** MEASURED, C5:

| pattern | subject | 10.46 | |
|---|---|---|---|
| `^(a)(b\1)(?2)$` | `"ababa"` | **(0,5)** g1=(0,1) g2=(1,3) | group 2's body is `b\1`; the call re-ran it and **`\1` was still `"a"`** |
| `^(a)(b\1)(?2)$` | `"abab"` | nomatch | control: an unset-and-empty `\1` would have matched this |

A call is not a fresh capture environment — it runs inside the caller's live
capture state.

**PER LEVEL, AND THE OUTERMOST LEVEL'S VALUES ARE THE FINAL ANSWER.**
MEASURED, C3: `^((a)(?1)?(b)(?C1))$` on `"aabb"` gives (0,4) g1=(0,4)
g2=(0,1) g3=(3,4) — during the call the inner level's own g2/g3 are visible,
then restored, then the outer's own written last. `^((a|b)(?1)?\2)$` matches
`"abba"` and not `"abab"` — each level's `\2` refers to that level's capture.

**AFTER A FAILED CALL, NOTHING SURVIVES.** MEASURED, C4:
`^(?:((a)(?C1))(?1)x|(?1)y)$` on `"ay"` is (0,2) with g1 AND g2 both unset —
the first branch's call ran (and its body wrote g2) and then died; the
second branch's call ran and succeeded; neither left a trace.

**THE ONE-SENTENCE RULE: a subroutine call is CAPTURE-TRANSPARENT — the
capture state after the call is exactly the state before it, whatever the
call did while it ran.**

### 3.2 Atomicity: BACKTRACKABLE on 10.46

PCRE2 was atomic here before 10.30; on 10.46 it is not. **The obvious test
cell does not isolate this** — `^(a|ab)(?1)c$` on `"ababc"` matches under
both hypotheses because the LEXICAL group can retry too. The isolated cell
puts the retriable body somewhere ONLY the call can reach it:

| pattern | subject | 10.46 | |
|---|---|---|---|
| `^(?(DEFINE)(?<g>a\|ab))(?&g)c$` | `"abc"` | **(0,3)** | **BACKTRACKABLE.** Atomic would be nomatch |
| `^(?!)(?<g>a\|ab)\|^(?&g)c$` | `"abc"` | (0,3) | the same without DEFINE, in case DEFINE is special |
| `^(?(DEFINE)(?<g>a+))(?&g)ab$` | `"aaab"` | (0,4) | a QUANTIFIER, not an alternation, as the callee's choice point |
| `^(?(DEFINE)(?<g>a{1,3}))(?&g)aa$` | `"aaa"` | (0,3) | and a bounded repeat |

**FOUR ATOMIC CONTROLS, all nomatch:** an atomic callee body `(?>a|ab)`; an
atomic wrapper on the call site `(?>(?&g))`; a possessive quantifier on the
call `(?&g)++`; and an atomic wrapper around a giving-back callee. A corpus
that only tests the four positive rows above (backtrackable) without their
atomic controls (which must all give the OPPOSITE, nomatch, answer) has not
established atomicity at all — it is the CONTRAST that is the fact.

**AND IT RETRIES ACROSS A RETURN, AT DEPTH:**
`^(?(DEFINE)(?<g>a(?&g)?b|x|xy))(?&g)$` matches `"axyb"` — the retreat has to
re-enter the INNER call after the outer one has already returned.

### 3.3 Left recursion: no compile-time refusal; the give-up is at match time

**PCRE2 10.46 REFUSES NO LEFT-RECURSIVE SHAPE AT COMPILE TIME.** Every one of
`((?1)a)`, `(a|(?1)a)`, `((?1)?a)`, `((?1)*a)`, `(?R)a`, and many more,
compiles. The guard is entirely at MATCH time: `rc -52`, "nested recursion at
the same subject position" (PCRE2's own message).

**THE OBVIOUS READING OF THAT MESSAGE IS REFUTED.** MEASURED,
`^(a|(?C1)(?1)a)$` with a callout immediately before the recursive call:

| subject | nested calls | entry offsets seen | result |
|---|---|---|---|
| `"a"×10` | 9 | `[0]` | (0,10) |
| `"a"×100` | 99 | `[0]` | (0,100) |
| **`"a"×200`** | **199** | **`[0]`** | **(0,200) — MATCHES** |
| `"a"×10 + "b"` | 12 | `[0]` | rc −52 |
| `"a"×40 + "b"` | 42 | `[0]` | rc −52 |

**199 nested recursions, every one entered at offset 0, and it matches.**
"Refuse a recursion at a position an ancestor already occupies" is the naive
reading of −52's own wording and it is WRONG: it would refuse this very
cell, where PCRE2 matches. `^(a|(?1)a)$` on `"a"×200` MUST MATCH — this is a
load-bearing corpus cell, not an edge case to skip.

pcrec's own behaviour for a left-recursive shape it cannot resolve is a
DEPTH-CAPACITY give-up, `PCREC_ERR_FRAMES` in the default artifact — see §5
below ("the depth ceiling") for the exact number and how to write a corpus
cell that expects it correctly (`gu frames "subject"`).

### 3.4 The interactions

#### (a) Backreferences to groups set inside a call

A reference reads live slot values, and the slots are always correct at the
instant it fires — nothing special here, this falls straight out of §3.1.

#### (b) `\K` is NOT restored by a return

MEASURED, `out/captures.txt` C7:

| pattern | subject | 10.46 |
|---|---|---|
| `^(a\Kb)(?1)$` | `"abab"` | **(3,4)** |
| `^(?(DEFINE)(?<g>a\Kb))(?&g)$` | `"ab"` | **(1,2)** |
| `^(a(?1)?\Kb)$` | `"aabb"` | **(3,4)** |

A `\K` inside a called body MOVES the reported match start, and the last one
executed on the successful path wins. **`\K` is a PATH fact, not capture
state, and it survives the return** — where every ordinary capture is
undone, `\K`'s effect on the reported start is not. This is a fact about
PCRE2's *measured behaviour*, verifiable purely from match spans (the
`(start,end)` of the whole match moves), with no implementation detail
attached: a corpus author should write cells like the three above and check
where the match START lands.

**A SEPARATE, LEXICAL rule governs whether `\K` is even ALLOWED inside a
lookaround, and it does NOT get relaxed by being reached through a call.**
This is measured PCRE2 behaviour, not an implementation claim: `\K` inside a
lookaround body is refused (err 199) whether the `\K` is written directly in
the lookaround or reached by a call FROM inside the lookaround into a body
containing `\K` — PCRE2's rule is about the LEXICAL nesting of the `\K` at
compile time, not about what runs at match time. A corpus testing "`\K`
inside a called body that is itself inside a lookaround" should expect
whatever PCRE2 itself does when you construct that pattern and hand it to
libpcre2 10.46 — measure it, do not assume the call "hides" the `\K` from
the lookaround's rule or "exposes" it in some new way.

#### (c) Duplicate names: a CALL and a REFERENCE resolve DIFFERENTLY

MEASURED, `out/captures.txt` C8 (all under `PCRE2_DUPNAMES`, i.e. write
patterns using `(?J)` or two same-named groups where pcrec's `modifiers`
module allows it):

| pattern (duplicate name `a`) | `"qyx"` | `"qyy"` |
|---|---|---|
| `^(?:(?<a>x)\|q)(?<a>y)(?&a)$` — a **CALL** | **(0,3)** | nomatch |
| `^(?:(?<a>x)\|q)(?<a>y)\k<a>$` — a **REFERENCE** | nomatch | **(0,3)** |

**A call by name to a duplicated name runs the FIRST DECLARATION's pattern,
statically, whether or not that group is set. A backreference by name reads
the first SET member of the run, dynamically.** They are two different
resolutions of one name — and this holds uniformly across ALL FOUR by-name
call spellings (`(?&a)`, `(?P>a)`, `\g<a>`, `\g'a'`): all four match `"qyx"`
and all four refuse `"qyy"` on the pattern above. A call also does NOT retry
into later same-named members: `^(?<a>x)(q)(?<a>y)(?&a)z$` matches `"xqyxz"`
and not `"xqyyz"`.

#### (d) A call inside a lookbehind needs a WIDTH — and the [DD-14.LB] amendment

MEASURED, `out/leftrec.txt` L7:

| pattern | 10.46 |
|---|---|
| `^(?(DEFINE)(?<g>ab))ab(?<=(?&g))$` | (0,2) — fixed width 2 |
| `^(?(DEFINE)(?<g>a\|ab))ab(?<=(?&g))$` | (0,2) — ONE branch, widths 1 and 2 mixed — the variable-length lookbehind PCRE2 10.43+ allows |
| `^(?(DEFINE)(?<g>a+))aa(?<=(?&g))$` | **ERR 125** "length of lookbehind assertion is not limited" |
| `^(?(DEFINE)(?<g>a{1,300}))aaaa(?<=(?&g))$` | **ERR 200** "branch too long in variable-length lookbehind" |
| `^(?(DEFINE)(?<g>a(?&g)?b))aabb(?<=(?&g))$` | **ERR 125** — a RECURSIVE callee has no bounded width |

PCRE2 computes the callee's width THROUGH the call. pcrec's own shipped
lookbehind subset is stricter than PCRE2's (module `lookaround`'s own §2.5:
every TOP-LEVEL branch of a lookbehind body must be individually fixed-width)
and this composes as follows, per the **[DD-14.LB] amendment** (2026-08-24),
which is a RULING, not merely a design intent — treat it as the authoritative
statement of what SHIPS:

- **An acyclic, fixed-per-branch callee composes and SHIPS.** A call inside
  a lookbehind to a callee whose own top-level branches are each individually
  fixed-width (row 1 above; also a two-hop acyclic call chain, or an
  alternation of calls written at the lookbehind body's own top level) is
  accepted.
- **A single call that is itself the lookbehind's one top-level branch, whose
  CALLEE has an alternation of DIFFERENT fixed widths (row 2 above,
  `(a|ab)`), is REFUSED by pcrec** — even though PCRE2 accepts it — because
  from the lookbehind body's own point of view this is ONE branch of
  variable width (1..2), which is exactly the `(?<=(a|bc))x` shape module
  `lookaround`'s §2.5 already refuses; being reached through a call does not
  change that. pcrec's refusal names the true bound ("this one can match 1..2
  characters"), not a false "unbounded".
- **A recursive callee inside a lookbehind is REFUSED on both sides** — row 5
  above is PCRE2's own err 125, and pcrec refuses it too, err 125 on both
  sides (the amendment's own words). A corpus cell testing this should
  expect a `perr` block on the pcrec side.

#### (e) A call inside a lookahead or an atomic group is ordinary

MEASURED, L8: `(?=(?&g))`, `(?!(?&g))`, `(?>(?&g))` all behave as the
construct they are wrapped in, including the atomic wrapper suppressing the
call's retries (consistent with §3.2's atomic controls).

#### (e2) `\G`, a non-zero startpos, `\A`/`\z` inside a callee

MEASURED, `out/wrapped_target.txt` axis G:

| pattern | subject | startpos | 10.46 |
|---|---|---|---|
| `(?(DEFINE)(?<g>\Ga))(?&g)` | `"xa"` | 0 | nomatch |
| `(?(DEFINE)(?<g>\Ga))(?&g)` | `"xa"` | **1** | **(1,2)** |
| `(?(DEFINE)(?<g>\Aa))x?(?&g)` | `"xa"` | 0 | nomatch |
| `(?(DEFINE)(?<g>a\z))x(?&g)` | `"xa"` | 0 | (0,2) |
| `(?(DEFINE)(?<g>a\z))x(?&g)b` | `"xab"` | 0 | nomatch |

`\G` is a test against `startpos`, `\A`/`\z` are tests against the subject's
absolute ends — a call changes neither the subject nor `startpos`, so these
mean exactly what they mean outside a call. **This is a strong signal that
your corpus should include `ms`/`ns` cells at non-zero startpos over
call-bearing patterns** — a span-only, startpos-0-only corpus cannot exercise
`\G`'s interaction with a call at all.

#### (f) `(?R)` under a quantifier, and the anchors again

MEASURED: `^(?R)*$`, `^(?R)?$`, `^(?R){0,2}$` all give `rc −52` (a give-up on
pcrec's side, per §5 below); `^a(?R)*b$` on `"ab"` matches; `(a(?R)*b)` on
`"aabb"` matches. `(?R)` under a quantifier is an ordinary repeatable item
and its interaction with `^`/`$` is exactly §2.4's, unaffected by the
quantifier.

### 3.5 A CALL'S TARGET MAY LIVE INSIDE A LOOKAROUND OR AN ATOMIC GROUP

MEASURED, `out/wrapped_target.txt` axis W. This is the mirror image of
§3.4(e): not a call written INSIDE a lookaround/atomic group, but a call TO a
group whose own lexical home happens to be inside one. This is one of the
sharpest and most implementer-hostile facts in the module — an obvious
implementation gets every cell of it wrong the same way.

| # | pattern | subject | 10.46 | what it proves |
|---|---|---|---|---|
| W1 | `^ab(?<=(ab))(?1)$` | `"abab"` | **(0,4)** g1=(0,2) | the call CONSUMES, though group 1's lexical home is a lookbehind (which is normally zero-width and rewinds) |
| | `^ab(?<=(ab))(?1)$` | `"ab"` | nomatch | control: the call must consume input |
| W2 | `^(?!(z\|zy))x(?1)c$` | `"xzyc"` | **(0,4)** | the call RETRIES into `zy`, though the group's home is a negative lookahead (normally cut on success and the whole region discarded) |
| | `^(?!(z\|zy))x(?1)c$` | `"xzc"` | (0,3) | control: the first alternative suffices |
| W3 | `^(?>(a\|ab))z(?1)c$` | `"azabc"` | **(0,5)** g1=(0,1) | the call CAN GIVE BACK `a` and take `ab` on retry, though the group's home is atomic (normally cuts retries) |
| | `^(?>(a\|ab))z(?:a\|ab)c$` | `"azabc"` | (0,5) | control: inline, atomic wrapper kept, same answer |
| Z0 | `^(?:(?<g>a\|ab)){0}(?&g)c$` | `"abc"` | **(0,3)** | the callee is defined inside `X{0}`, which pcrec emits NO code for lexically — the call still reaches it |
| | `^(x)?(?:(a(?2)?b)){0}(?2)$` | `"aabb"` | (0,4) | …and it can be RECURSIVE |
| | `^(?:((?>a\|ab))){0}(?1)z$` | `"az"` / `"abz"` | (0,2) / nomatch | …and atomic — here atomicity DOES travel with the callee, because the `(?>` is written INSIDE the group, unlike W3 where it wraps the group from outside |
| W5 | `^(?=(a\|ab))..(?1)$` | `"abab"` | (0,4) | positive lookahead, same idea |
| | `^((?=(b))\|a)+(?2)$` | `"ab"` | (0,2) | a lookahead nested in a quantified group |

**THE RULE THE ROWS FORCE:** a called group runs as its OWN region — forward,
consuming, cut-free, back-step-free — WHATEVER its lexical wrapper is. The
wrapper (lookbehind, negative lookahead, atomic group, `{0}`) is a property
of where the group happens to sit in the pattern text, not of the group
itself; a CALL reaches the group, not the lexical occurrence, and runs it
plain.

## 5. The refusals that exist (and how many there are)

Compiled here as a flat list because §2's table is spread across several
sub-sections. Every one of these is an EXISTENCE fact — none of their
diagnostic wording is fixed, and none of it matters for a blinded corpus:

- **`(?-0)`, `(?+00)`, `\g<-0>` and any spelling of a RELATIVE call at value
  zero** — error 126, refused on both PCRE2 and pcrec (§2.4a). Absolute zero
  (`(?0)`, `(?00)`, `\g<0>`, `\g<00>`) is NOT this — it is a valid call to the
  root or (for the double-zero forms) also the root, per §2.4a's table.
- **A call to a group number/name that does not exist** — a missing-target
  compile error, both sides.
- **A recursive callee reached through a lookbehind** — refused, err 125 on
  both sides (§3.4(d)).
- **A single-branch variable-width callee that is the lookbehind's whole
  top-level branch** — refused BY PCREC ONLY (PCRE2 accepts it); this is the
  §3.4(d) `(a|ab)`-through-a-call case, and pcrec's refusal is the true bound
  stated as a message, not "unbounded" (§3.4(d)).
- **`(?(DEFINE)…)` with TWO OR MORE branches** — PCRE2 itself refuses this
  (a DEFINE container is meant to hold exactly one alternative-free
  definition; giving it two live branches is a compile error on PCRE2's
  side already, independent of pcrec). A corpus testing this is testing
  PCRE2's own rule, which pcrec inherits by construction since the DEFINE
  lowering only ever sees what PCRE2 itself would have accepted as valid
  DEFINE syntax.

**THE DEPTH CEILING (D73, 2026-08-24): 2048 resume frames / 3072 trail
entries is the pcrec DEFAULT stamped capacity for a call-bearing pattern.**
This is not a refusal — it is a runtime give-up, and the exact number to
design cells against: `^(a(?1)?b)$` gives up (returns `PCREC_ERR_FRAMES`, the
default artifact's code for this — D71 item 1) at **n = 342**, i.e. an
**684-byte subject** (2×342 characters, since the pattern's body is `a...b`
around `n` nested calls). Below that depth the pattern MATCHES (per §3.3's
`^(a|(?1)a)$` cell, which reaches depth 199 and matches — well under the
ceiling); at or above it, pcrec gives up loudly rather than answering wrong.
**A deep-recursion corpus cell should therefore be written as a `gu frames
"subject"` directive for a subject ABOVE this ceiling, and as an ordinary `m`
match expectation for one BELOW it.** The `.rxt` directive vocabulary is
`gu <code> "<subject>"` with `<code>` one of `steps`/`frames`/`work`/
`recurse` — `recurse` (`PCREC_ERR_RECURSE`) exists as a reserved code but has
NO PRODUCER today, so no block can pass expecting it yet; do not write a `gu
recurse` cell expecting it to pass. `frames` is the one this module's give-up
actually produces in the default artifact.

## The oracle rules

1. **libpcre2 10.46 is the ONLY oracle for match cells.** For every other
   module built so far, python `re` has ruled some cells and PCRE2 the rest.
   **For this module python rules NOTHING.** MEASURED, all nine call
   spellings plus both zero spellings:

   | spelling | python 3.14 `re` |
   |---|---|
   | `(?1)`, `(?0)`, `(?R)` | `PatternError: unknown extension` |
   | `(?-1)` | `PatternError: missing flag at position 8` — python reads it as an INLINE-FLAG group, the error does not even mention a subpattern |
   | `(?&n)`, `(?<n>…)` | `PatternError: unknown extension ?<n` — python needs `(?P<n>…)`, so the DECLARATION fails first |
   | `(?P>n)` | `PatternError: unknown extension ?P>` |
   | `\g<1>`, `\g'1'`, `\g<0>`, `\g{1}` | `PatternError: bad escape \g` — `\g` is a REPLACEMENT-TEMPLATE escape in python, never a pattern one |
   | `\1`, `(?P=n)` | **compiles** — but these are the REFERENCE spellings, module `backrefs`', not this module's |

2. **The two reference spellings python DOES compile are a TRAP.** `\1` and
   `(?P=n)` compile in python and mean something DIFFERENT from `\g<1>` and
   `(?P>n)`. Checking "does python agree" on a cell containing `\1` tests
   `backrefs`, not `recursion`. §2.1's one-cell discriminator (`(a|b)X` on
   `"ab"`) is the tool for telling which one you are looking at, and it
   should be used liberally.
3. **Every spelling SHIPS.** There is no refusal list to test against the
   way every previous module had one (module `lookaround` had 8 refusal
   cells, module `backrefs` had its own set) — this module's refusals are
   the short, specific list in §5 above, and they are few.
4. **`(?R)` re-runs the whole pattern INCLUDING the anchors** (§2.4) — the
   single most counter-intuitive fact here.
5. **Nothing about the implementation.** Not the linkage, not the call
   graph, not the internal name `W`, not the depth capacity's storage
   representation (only its OBSERVABLE number, 342/684 bytes, matters to a
   corpus author, and that number is given in §5 above).

**THE SINGLE-ORACLE SITUATION IS A REAL WEAKENING — do not read this
document as claiming otherwise.** Both the corpus and the compiler answer to
libpcre2, which is D26's design (PCRE2 IS the source of truth) rather than a
failure mode, but it does mean this corpus has less independent triangulation
than most modules' did. The one thing that keeps this from being circular is
that the author of this corpus never sees `src/`, so the corpus cannot
inherit the implementation's own alphabet of mistakes.

### THE PERL ARM (D71 item 5) — a SECOND oracle, divergences RECORDED not resolved

**Perl 5.40.1 is installed on this box.** Subroutine calls are Perl's own
construct — `(?1)`, `(?R)`, `(?&name)`, and (measure which spellings Perl
itself accepts; do not assume) `(?(DEFINE)…)` and `\g<…>` are all part of
Perl's regex heritage, which PCRE2's own subroutine-call feature was modeled
on. Perl is therefore the construct's ORIGIN and a legitimate second oracle
— but **D26 rules that PCRE2 is the sole source of truth for what pcrec
matches.** So:

> **PERL IS A SECOND ORACLE WHOSE DIVERGENCES FROM PCRE2 10.46 ARE TO BE
> RECORDED, NOT RESOLVED.** Where Perl and PCRE2 disagree, PCRE2 rules pcrec's
> expected answer (per D26); note the Perl divergence in the corpus (e.g. a
> comment or a parallel non-oracle observation) rather than writing an
> expectation against Perl's answer.

**THE ONE DIVERGENCE THE DESIGN ALREADY KNOWS, so you do not have to
rediscover it from nothing:** PCRE2 ≥10.30's subroutine calls are
BACKTRACKABLE (§3.2 above); earlier PCRE, and (this is for you to MEASURE,
not assume) quite possibly Perl itself, may treat a call as ATOMIC. If Perl
disagrees with PCRE2 on any of §3.2's isolated backtracking cells, that is
the expected shape of the divergence, and the corpus should record it rather
than treat it as a surprise needing resolution.

**MEASURE WHICH SPELLINGS PERL ACCEPTS — do not guess from the PCRE2 table.**
The invocation shape, so you need not work it out yourself:

```sh
perl -e '
  my $pat = shift;
  my $subj = do { local $/; open(my $fh, "<", shift) or die $!; <$fh> };
  if ($subj =~ /$pat/) {
    print "match @- / @+\n";   # @- and @+ are the start/end offset arrays,
                                # index 0 = whole match, index k = group k
  } else {
    print "nomatch\n";
  }
' '<pattern>' subject_file.txt
```

(a subject read from a file, rather than passed on the command line, avoids
shell-escaping headaches for subjects containing regex metacharacters or
control bytes). Print `@-`/`@+` rather than `$&` so unset groups and byte
offsets are visible the same way PCRE2's ovector reports them.

## The population you are asked for

Target ADVERSARIALLY the specific ways a lowering of this module gets it
wrong — each of these is a plausible bug shape, not a hypothetical:

- **A lowering that forgot to restore captures after a call returns** (§3.1)
  — test at DEPTH (nested calls, not just one level) so a bug that only
  shows at depth ≥ 2 is reachable.
- **A lowering that restored the WRONG SET of slots** — e.g. restored too
  much (undoing `\K`, §3.4(b)) or too little (leaving a stale value from a
  call that should have been fully undone, §3.1's C4 "nothing survives"
  cell).
- **A lowering that popped the call frame ON RETURN** rather than leaving it
  live — this would show up as the call becoming falsely atomic; test with
  §3.2's isolated backtracking cells AND their atomic controls together,
  since a bug here makes the positive cells read like the controls.
- **A lowering that CUT at the return** — same failure mode as above, from a
  different mechanism; the retry-across-a-return cell (§3.2, the depth-nested
  DEFINE) is the sharpest test of this.
- **A lowering that mis-scoped the FOLLOW** after a call — e.g. treating what
  comes after `(?1)` as though it were part of the callee, or vice versa.
  Test with calls immediately followed by more pattern that must NOT run as
  part of the callee, and (§3.4(d)/§3.5) calls whose target sits inside a
  lookaround or atomic wrapper, where a mis-scoped follow is most likely to
  surface as either eating the wrapper's semantics or leaking past them.
- **A lowering that INLINED a recursive callee** (impossible in general —
  test that deep/unbounded recursion behaves as a call, not as however many
  copies got inlined, by using the depth-ceiling cells in §5 and the
  `^(a|(?1)a)$`×200 cell from §3.3).
- **A lowering that counted call-graph SLOTS LEXICALLY** rather than
  correctly handling the `{0}`-parked / DEFINE callee shapes of §2.2 and
  §3.5's Z0 row, where the callee has no lexical emission of its own at all.
  Test the Z0 family directly: a plain, a recursive, and an atomic callee
  each parked under `{0}` or DEFINE, each called successfully.
- **A lowering that resolved `\g<0>` (or `\g'0'`) as "group 0"** rather than
  as the AST root / `(?R)` synonym — test directly against §2.4's anchored
  discriminator cells.
- **A lowering that resolved a DUPLICATED NAME the same way for a call as for
  a reference** — test §3.4(c)'s pair directly: the call takes the FIRST
  DECLARATION regardless of which is set; the reference takes the first SET
  member. These two rows on the SAME pattern shape, expecting DIFFERENT
  answers, is the discriminating test — a corpus with only one of the two
  spellings cannot catch this bug.

**THE DEPTH CEILING, again, because it governs how you write deep cells:**
2048 frames / 3072 trail entries is the default stamped capacity; for
`^(a(?1)?b)$`-shaped patterns the give-up lands at **n = 342** (a 684-byte
subject). Write cells ABOVE this ceiling as `gu frames "<subject>"` and cells
BELOW it as ordinary `m` matches. Do not write a match expectation for a
subject you have not checked is under the ceiling for that specific pattern
shape — the ceiling is in resume frames and trail entries, not directly in
subject bytes, so different call-bearing pattern shapes cross it at
different subject lengths.

**`ms`/`ns` cells at non-zero startpos are required, not optional** — §3.4(e2)
is entirely about the interaction between `\G`/`\A`/`\z` and a non-zero
`startpos`, and a startpos-0-only corpus cannot exercise it at all.

**`g` lines (per-group capture-slot expectations) belong on EVERY relevant
`m`/`ms` case, not just some of them.** This whole module is about what a
call's return puts back into the capture slots — a span-only cell (checking
only the whole match's start/end) cannot see a restore bug at all. Use the
`.rxt` `g <slot> <start> <end>` / `gp <slot> <start> <end>` directives
(`docs/testing.md`) liberally, especially on the depth-nested and
duplicate-name cells above.

**THE RFC 5322 EMAIL SPECIMEN** is a real-pattern seed, not invented for this
corpus — a genuine RFC 5322 address-spec regex and a hand-factored version of
the SAME pattern using named DEFINE-style subgroups and calls to them,
matching the same language:

Original (`orig.rx`):
```
(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])
```

Factored (`factored.rx`), using `(?:(?<name>BODY)){0}` DEFINE-style callee
parking plus `(?&name)` calls:
```
(?:(?<atom>[a-z0-9!#$%&'*+/=?^_`{|}~-]+)){0}(?:(?<qchar>[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])){0}(?:(?<label>[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)){0}(?:(?<octet>25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){0}(?:(?&atom)(?:\.(?&atom))*|"(?:(?&qchar))*")@(?:(?:(?&label)\.)+(?&label)|\[(?:(?:(?&octet))\.){3}(?:(?&octet)|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])
```

Both are on this box at
`docs/design/subroutines_measurements/email_specimen/orig.rx` and
`factored.rx`. Include both forms in the corpus with a shared set of email
and non-email subjects (valid addresses, addresses with quoted local parts,
IP-literal domains, and deliberately invalid strings), checking that BOTH
patterns agree with each other AND with libpcre2 on every subject. This
specimen is valuable specifically because it is real-world-shaped: many
named callees, several called more than once, a mix of alternation and
bounded repeat inside callee bodies, and a callee (`octet`) called from
inside a `{3}`-bounded repeat — none of it invented to embarrass an
implementation, all of it naturally occurring in how people actually write
factored patterns.

## What is withheld

Nothing beyond §§2, 3, 5, and this file's oracle-rules/population sections is
disclosed. Specifically NOT disclosed, and not to be inferred or guessed at
by a blinded author: the lowering (how a call is emitted, frames, the second
indirect jump, the trail mechanics), the linkage between a call site and its
callee body, the call graph or its construction, anything named `W` (a slot
write-set analysis internal to the implementation), the identity/consistency
gate, the sabotage rows, any file name under `src/` or `tests/` (other than
the two email-specimen `.rx` files named above, which are DATA, not
implementation), and the wording of any diagnostic (only whether a
construct is real, which module owns it, and whether pcrec ships or refuses
it, per D26's tiering — never the phrasing of an error message).
