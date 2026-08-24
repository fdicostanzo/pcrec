# la_d27_extract.md — the [M6.6.3] blinded author's design extract

Extracted verbatim from docs/design/lookaround_design.md (sections 2, 7,
10.1) by the manager at the module's build completion (main 1844a1c).
The blinded author sees THIS FILE and never the full design: sections 3-6,
8-9 and 11-14 describe the implementation and its checks, which D27 denies.

## 2. The construct table (charter (i))

### 2.1 Every spelling, and whether pcrec ships it

MEASURED, `out/spellings.txt` axis A1/A2, 10.46 and python 3.14.4. The
`is it what it claims` column is the DISCRIMINATOR rule taken from
`backrefs_design.md` §2 and from `registry.c:692`'s own record: a construct
that merely compiles proves nothing about what it is.

| spelling | libpcre2 10.46 | is it what it claims? | python `re` | **this module** |
|---|---|---|---|---|
| `(?=X)` | ok | atomic positive lookahead — `(?=(a\|ab))\1$` is NOMATCH on `"abab"` | ok | **SHIPS** |
| `(?!X)` | ok | negative lookahead | ok | **SHIPS** |
| `(?<=X)` | ok | atomic positive lookbehind | ok, fixed-width only | **SHIPS**, fixed-per-branch (§2.5) |
| `(?<!X)` | ok | negative lookbehind | ok, fixed-width only | **SHIPS**, fixed-per-branch |
| `(?*X)` | ok | **NON-atomic** positive lookahead — `(?*(a\|ab))\1$` is **(2,4)** on the same subject | err | **SHIPS** (§3.6: the atomic shape MINUS the cut) |
| `(?<*X)` | ok | non-atomic positive lookbehind — `(?<*(a\|ba))c` is (2,3) g=(0,2) | err | **SHIPS** |
| `(*pla:X)` `(*positive_lookahead:X)` | ok | atomic — `(*pla:(a\|ab))\1$` NOMATCH, same as `(?=)` | err | **SHIPS** (§8.2) |
| `(*nla:X)` `(*negative_lookahead:X)` | ok | negative lookahead | err | **SHIPS** |
| `(*plb:X)` `(*positive_lookbehind:X)` | ok | positive lookbehind | err | **SHIPS** |
| `(*nlb:X)` `(*negative_lookbehind:X)` | ok | negative lookbehind — `(*nlb:a)\w` is (0,1) on `"ba"` | err | **SHIPS** |
| `(*napla:X)` `(*non_atomic_positive_lookahead:X)` | ok | non-atomic — **(2,4)**, the same answer as `(?*`, which is the proof they are one construct | err | **SHIPS** |
| `(*naplb:X)` `(*non_atomic_positive_lookbehind:X)` | ok | non-atomic positive lookbehind | err | **SHIPS** |
| `(*nanla:X)` `(*nanlb:X)` | **err 195** ("(*alpha_assertion) not recognized") | — **there is no non-atomic NEGATIVE form** | err | refuse — the row's own control |
| `(?<!*X)` | **err 109** | — the `*` is read as a quantifier | err | refuse |
| `(?=)` `(?!)` `(?<=)` `(?<!)` | ok, all four | zero-width with an empty body: `a(?=)b` is (0,2), `a(?!)b` is NOMATCH | ok | **SHIPS** (§2.6) |

**THE FAMILY THIS TABLE'S CONSTRUCTS ARE ALREADY IN.** Every member of the
assertion family module `assertions` ships — `\b` `\B` `(?m)^` `(?m)$` `\Z`
`$` `^` — HAS a definition in terms of these spellings, verified equivalent at
972 cells / 0 disagreements (§6.1). So the constructs below are not a new
surface bolted beside the assertions module; they are the vocabulary it is
already written in, and §6 uses that three ways.

**SHIP/REFUSE SPLIT: EIGHTEEN spellings ship and THREE refuse** — `(*nanla:`
and `(*nanlb:`, which PCRE2 does not have (err 195), and `(?<!*X)`, which
PCRE2 reads as a quantifier and rejects (err 109). **There is no spelling in
this module's territory that PCRE2 HAS and pcrec declines.** Every decline
this module makes is about a BODY (§2.5), not a spelling, and that is the
distinction D26 tier 1/2 cares about: which constructs are REAL and who owns
them is exact here, and the capability limits are stated separately.

### 2.2 The atomicity discriminator, because it is the whole difference

MEASURED, `out/spellings.txt` A2, on `"abab"`:

```
(?=(a|ab))\1$        NOMATCH    the lookahead keeps its FIRST success ("a"),
                                so \1 is "a" and "a" does not end the subject
(?*(a|ab))\1$        (2,4)      the non-atomic form RETRIES, finds "ab",
(*napla:(a|ab))\1$   (2,4)      and \1 = "ab" ends the subject
(*pla:(a|ab))\1$     NOMATCH    the verb spelling of (?=) — atomic
```

That table is four rows and it fixes four things at once: `(?=` is atomic,
`(?*` is not, `(*napla:` is `(?*`, and `(*pla:` is `(?=`. §3 emits the first
and third with a cut and the second and fourth without one, and there is
nothing else to the distinction.

### 2.3 The lookbehind length rule, cell by cell on 10.46

MEASURED, `out/lookbehind_length.txt` B1. The `err` numbers are the fact;
their wording is D26 tier 3.

| body | maxlb | libpcre2 10.46 | python `re` |
|---|---|---|---|
| `(?<=a)x` `(?<=abc)x` `(?<=\w)x` `(?<=[abc][def])x` | 1/3/1/2 | ok | ok |
| `(?<=a{3})x` `(?<=(?:ab){2})x` | 3/4 | ok — an EXACT count is fixed | ok |
| `(?<=ab\|cd)x` | 2 | ok — same length | ok |
| **`(?<=a\|bc)x`** | **2** | **ok — DIFFERENT fixed lengths per branch** | **ERROR** ("look-behind requires fixed-width pattern") |
| `(?<=(a\|bc))x` | 2 | ok — but this is ONE branch of VARIABLE width | ERROR |
| `(?<=a\|bc\|def)x` | 3 | ok | ERROR |
| `(?<=(?:a)(?:b))x` `(?<=(a)(b))x` | 2 | ok | ok |
| `(?<=(?:a\|bc)d)x` `(?<=((a\|bc)d))x` | 3 | ok | ERROR |
| `(?<=a{2,3})x` `(?<=a{0,3})x` `(?<=a?)x` | 3/3/1 | ok — BOUNDED variable | ERROR |
| `(?<=a*)x` `(?<=a+)x` `(?<=a{2,})x` `(?<=a*?)x` `(?<=a*+)x` `(?<=(?>a*))x` | — | **err 125** "length of lookbehind assertion is not limited" | ERROR |
| `(a)(?<=\1)x` | 1 | ok — a backref to a FIXED-width group | ok |
| **`(a\|bc)(?<=\1)x`** | **2** | **ok — a backref to a VARIABLE-width group** | ERROR |
| `(?<=(?=a)a)x` `(?<=(?<=a)b)x` `(?<=a(?!b))x` `(?=(?<=a)b)x` | 1 | ok — lookaround nests both ways | ok |
| `(?=(?<=a*)b)x` | — | err 125 — the inner rule applies through the outer | ERROR |
| `(?<=\Ka)x` `(?=a\K)x` `(?!a\K)x` `(?<!\Ka)x` | — | **err 199** "`\K` is not allowed in lookarounds" | ERROR (`\K` absent) |
| `a\Kb` (control) | 0 | ok | ERROR |
| `(?<!a\|bc)x` `(?<*a\|bc)x` | 2 | ok — the rule is polarity- and atomicity-blind | ERROR |
| `(?<!a*)x` `(?<*a*)x` | — | err 125 | ERROR |

**THE CAPS ARE TWO DIFFERENT NUMBERS AND ONE OF THEM IS NOT A PROPERTY OF THE
CONSTRUCT.** MEASURED, B3:

- The **variable** back-step is capped by the COMPILE CONTEXT's
  `max_varlookbehind`, whose **default bisects to 255** (`(?<=a{1,255})x` is
  ok; `(?<=a{1,256})x` is **err 200** "branch too long in variable-length
  lookbehind assertion"). Under an explicit cap of 4, `(?<=a{1,4})x` compiles
  and under 3 it does not — so the number is contextual, not intrinsic, and
  quoting 255 as "PCRE2's lookbehind limit" would be wrong.
- A **fixed** lookbehind is **not subject to that cap at all** (a 10-character
  literal body compiles under a cap of 1). Its own ceiling bisects to
  **32759**, past which it is **err 120** "regular expression is too large" —
  i.e. the pattern-size limit, not a lookbehind limit.

**`PCRE2_INFO_MAXLOOKBEHIND` for composite bodies**, MEASURED B4, because §3
and §5 both need this quantity: `(?<=a)(?<=bc)x` → 2 (the max, not the sum);
`(?<=a)x|(?<=bcd)y` → 3; `(?<=(a|aa)(b|bb))x` → 4 (the sum of the maxima);
`\babc` → **1**; `(?m)^abc` → **0**; `a\Kb` → 0. The `\b` row is the one §6
uses.

### 2.4 THE PREFERENCE ORDER — two levels that disagree

**This is the sharpest measurement in the module and the design's capture
semantics rest on it.** MEASURED, `out/lookbehind_length.txt` B2.

**Level 1 — top-level BRANCHES are tried in WRITTEN ORDER:**

```
(?<=(a)|(aa))c        on "aac"   ->  (2,3)  g1=(1,2)   branch 1 wins (shorter)
(?<=(aa)|(a))c        on "aac"   ->  (2,3)  g1=(0,2)   branch 1 wins (longer)
(?<=(a)|(aa)|(aaa))c  on "aaac"  ->  (3,4)  g1=(2,3)   branch 1 wins
(?<=(aaa)|(aa)|(a))c  on "aaac"  ->  (3,4)  g1=(0,3)   branch 1 wins
```

**Level 2 — within ONE branch the STEP-BACK LENGTH is tried LONGEST FIRST,
and the alternation's own written order does not decide it:**

```
(?<=(a|aa|aaa))c   on "aaac"  ->  g1=(0,3)   longest (3) wins, written LAST
(?<=(aaa|aa|a))c   on "aaac"  ->  g1=(0,3)   longest (3) wins, written first
(?<=(a|aa))c       on "aac"   ->  g1=(0,2)   longest (2) wins, written last
(?<=(x|aa|a))c     on "aac"   ->  g1=(0,2)   longest VIABLE wins
(?<=(a|ba))c       on "bac"   ->  g1=(0,2)   longest (2) wins, written last
(?<=(a|ba))c       on "xac"   ->  g1=(1,2)   only length 1 is viable there
(?<=(a{1,3}))c     on "aaac"  ->  g1=(0,3)   a bounded quantifier: longest first
```

For comparison, the LOOKAHEAD has ordinary leftmost-first alternation, because
it has no length to choose: `(?=(a|ab))ab` gives g1=(0,1) and `(?=(ab|a))ab`
gives g1=(0,2).

**WHY THIS MATTERS TO THE DESIGN, in one sentence:** an implementation that
lowered a lookbehind as "try each alternative in written order, stepping back
its own width" would be **exactly right at level 1 and exactly wrong at level
2** — and it would be exactly right at level 2 too *for the fixed-per-branch
subset this module ships*, because a branch of fixed width has one length and
the loop that would order them has one iteration. **That is the whole argument
for the subset boundary this design draws**, and §2.5 draws it there for that
reason rather than for effort.

### 2.5 THE RULE THIS MODULE SHIPS

> **A lookbehind body's every TOP-LEVEL BRANCH must have a fixed width:**
> `minw(branch) == maxw(branch)`, both finite. Widths may DIFFER between
> branches. A body with any variable-width branch is REFUSED with pcrec's own
> reason.

Consequences, each checkable against §2.3's table:

- `(?<=a)x`, `(?<=abc)x`, `(?<=[ab][cd])x`, `(?<=a{3})x` — **ship**.
- `(?<=a|bc)x`, `(?<=a|bc|def)x` — **ship**. Two branches, each fixed, widths
  1 and 2. This is the charter's "fixed-length alternatives of DIFFERENT
  lengths" cell and the answer is yes.
- `(?<=(a|bc))x` — **REFUSED**. One branch, width 1..2. It looks like the row
  above and is a different shape, and the difference is exactly the level-1 /
  level-2 split §2.4 measured. **This asymmetry is the single most likely
  thing in this document to be called a defect, and §12 P-3 says how to refute
  it.**
- `(?<=a{2,3})x`, `(?<=a?)x` — **REFUSED** (bounded variable).
- `(?<=a*)x` and family — **REFUSED**, and here pcrec AGREES WITH PCRE2, which
  is err 125.
- `(a)(?<=\1)x` — **REFUSED** in [M6.6.2]. A backreference's width is decided
  at MATCH time by which alternative the referenced group took. For a
  fixed-width referenced group it is computable and this refusal is
  conservative; §11's follow-on row carries the refinement.
- `(?<=(?=a)b)x`, `(?<=(?<=a)b)x`, `(?<=a(?!b))x` — **ship**: a nested
  lookaround is zero-width, so it contributes 0 to both `minw` and `maxw`.

**THE RULE IS EXACTLY BIG ENOUGH FOR THE ASSERTION FAMILY, and that is
measured rather than arranged.** Every one of the nine [DD-11]/D66 expansions
(§6.1) compiles under this rule: their lookbehind bodies are `(?<=\w)`,
`(?<!\w)` and `(?<=\n)` — one class or one literal, fixed width 1 — and the
only variable-width body in the whole family, `\n?\z`, sits inside a
lookAHEAD (`\Z` ≡ `(?=\n?\z)`) where there is no width rule at all. **The
same body one direction over would be refused**, and `out/expansions.txt` E2
prints that discriminating row: `(?<=\n?\z)x`, `(?<=\n?)x` and `(?<=\w?)x`
all compile in PCRE2 with `maxlb 1` and all have `minw 0, maxw 1`, so pcrec
refuses all three as lookbehinds. §12 P-12 is how to refute the coincidence.

**`pcrec_maxw` DOES NOT EXIST (P11) and this module writes it**, beside
`pcrec_minw` in `src/opt/mrl.c`, with that file's `default:`-less exhaustive
switch so a node kind added later is a build failure there (R26 V7, the rule
`mrl.c:18-24` states and `altcls.c:405` cites). It returns a saturating
`PCREC_W_UNBOUNDED` for `A_REP` with `rmax < 0`, and — per the bullet above —
for `A_BREF`. **Writing `maxw` is the module's one piece of genuinely new
analysis and §12 P-4 is how to attack it.**

**WHY REFUSE VARIABLE-LENGTH RATHER THAN SHIP IT.** The machine is not large —
a loop over `k` from `maxw` down to `minw`, the same back-step entry, the same
end-check, which at that point stops being redundant (§3.4). Three reasons to
charter it instead of shipping it:

1. **The loop runs in the OPPOSITE direction to everything else the emitter
   does.** Every other ordered choice in `emit_vm.c` is preference-first, and
   §2.4 measures this one as longest-first over a range whose ends come from a
   NEW analysis (`maxw`). Shipping a reversed loop over an unvalidated
   analysis in the same wave is how the [M4.6d] counter-rung defect happened
   (a compile-time follow-min that topped out at `K + residue`, found by a
   D27-blinded author).
2. **The cost is per-position and unbounded by the pattern.** A body of width
   1..255 runs the body up to 255 times per candidate start, and D42 item 6's
   two bounds (steps and frames) do not see a frameless re-run — the same gap
   [ENG-BREP counter-K] settlement 4 opened `RX_ERR_WORK` for.
3. **The refusal is honest and PCRE2-shaped.** PCRE2 itself refuses the
   unbounded case with err 125 and caps the bounded case at a
   context-dependent 255; a pcrec that ships fixed and names the limit is one
   step, not a different kind of thing.

**The refusal's WORDING is D26 tier 3 and its EXISTENCE is not.** The
construct is real and the module is enabled, so this is not "requires module
'lookaround'" — it is the capability limit P14 already has a diagnostic shape
for. Proposed text, for the panel to attack on content and not on prose:
*"variable-length lookbehind is not implemented: every alternative of a
lookbehind must have a fixed length (this one can match N..M characters)"*.

### 2.6 The degenerate bodies, quantifiers, and the empty-iteration rule

MEASURED, `out/spellings.txt` A3/A4 and `out/captures.txt` C4.

- **`(?=)` `(?!)` `(?<=)` `(?<!)` all compile in BOTH oracles.** `a(?=)b` is
  (0,2), `a(?!)b` is NOMATCH, `a(?<=)b` is (0,2), `a(?<!)b` is NOMATCH — i.e.
  the empty body always succeeds, so the positive forms are no-ops and the
  negative forms are `(*FAIL)`. `(?:(?!))|a` is (0,1). **They ship**, and they
  fall out of §3's shapes with no special case: an empty body is `A_EMPTY`.
- **Quantified lookaround compiles in BOTH oracles** — all fourteen forms
  tried, including `(?=a)*+`. **This refutes the charter's expectation** that
  python lacks it (§1).
- **The empty-iteration cells terminate**, MEASURED with a clock because "it
  did not hang" is the measurement: `^(?=a)*a$`, `^(?:(?=a))*a$`,
  `^(?:(?=a)|b)*a$`, `^(?:(?!x))*a$`, `^(?:(?=(a)))*a$` all answer in 0.0000 s
  and all agree with python.
- **A quantified lookaround's captures behave like one iteration**:
  `^(?=(a))*a$` → g1=(0,1); `^(?=(a))*b$` → g1 unset; `^(?!(a))*b$` → g1
  unset.

**The design consequence is one line and getting it wrong HANGS the emitted
matcher.** `vm_nullable` (`emit_vm.c:875-899`) must answer **true** for the
new node, exactly as it answers true for `A_ATOMIC` and for the same reason
(`emit_vm.c:877-881`: the cut removes MATCHES, never BYTES). A lookaround
consumes nothing on every path, so a `*` above it must get the
empty-iteration guard. §9's sabotage row S-LA9 removes the arm.

### 2.7 `\K` inside a lookaround

MEASURED, `out/lookbehind_length.txt` B1 and `out/captures.txt` C5. **PCRE2
10.46 REFUSES `\K` in every lookaround, all four polarities, err 199**, whose
own text names `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`. That option **exists and is
bit 0x40 on this build** (derived by sweep after the documentation-order guess
0x8000 measured nothing); with it set, `(?=a\K)x` and `(?<=\Ka)x` compile,
while an unrelated lookbehind error (err 125) survives and plain `a\Kb` stays
legal — the two controls that separate "this bit enables `\K` in lookarounds"
from "this bit disables checking".

**RULING: pcrec REFUSES `\K` inside a lookaround**, matching PCRE2's default,
and does not implement the extra option (D38's option survey territory, not
this module's). The refusal is a parse-time check in the module's hook: while
parsing a lookaround body, an `A_KRESET` node is an error.

**THE SCOPE IS RECURSIVE, AND R33 C1-7 is right that "while parsing a
lookaround body" has two readings.** The check must descend through nested
groups AND nested lookarounds, and must NOT fire after the assertion closes.
MEASURED both directions (`out/follow_scoping.txt` F5):

**REFUSED (err 199), eleven cells** — `(?=(a\K))x`, `(?=a(?:\K))x`,
`(?=(?:(?=\K)))x`, `(?*a\K)x`, `(?<*\Ka)x`, `(*pla:a\K)x`, `(*nlb:\Ka)x`,
`(?<=\Ka)x`, `(?=a\K)x`, `(?!a\K)x`, `(?<!\Ka)x`. The first three are the
ones a check testing only IMMEDIATE children would miss.

**COMPILES, four cells** — `(?=a)\Kb`, `a(?=b)\Kc`, `(?<=a)\Kb`, `a\Kb`.
These are what a check that latched on "a lookaround was seen" would wrongly
break. **S-LA10's prediction names both sets**, so the row cannot go green by
being too broad. **The check is
NEEDED rather than free** — `\K` is module `assertions`, already shipped, so
without it `(?=a\K)b` would compile today's `\K` inside tomorrow's lookaround
and quietly change the reported match start. §9's S-LA10.

---

**AMENDMENT (2026-08-23, post-approval, manager + Frank): the OLD semantics
behind the flag, measured.** Frank recalled `\K` inside a lookbehind moving
the reported match START before the attempt point. MEASURED on this box's
10.46: with `PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK` (0x40, the bit §2.7's sweep
derived), `(?<=\Kfoo)bar` on `"baxfoobarbaz"` matches **(3,9) = "foobar"**
— the start moves back INTO the lookbehind; `(?<=foo\K)bar` gives (6,9);
`(?=\Kfoo)foobar` gives (3,9). This is Perl's pre-deprecation `\K`
heritage; PCRE2 made it err 199 by default in 10.38. pcrec's refusal is the
right D26 tier (the oracle is pinned at options=0; adopting any `EXTRA_*`
bit is a D38 ruling event, docs/pcre2_options.md). If ever adopted, the
design consequence is one deliberate exception to §3's rule: `\K` writes
the match-start slot, and inside a lookbehind body that write must SURVIVE
the position restore that discards the body's other effects. **RULED
(Frank, 2026-08-23, same conversation): NOT WANTED — "it's considered bad
mojo and weird; I don't want to goof with our set-up." The refusal is
permanent unless a future Frank ruling reopens it; do not propose the
EXTRA bit's adoption from this paragraph.**

## 7. The D27 goal-facts list (charter (vi))

For the [M6.6.3] blinded author, who is denied `src/` and `tests/` and writes
the corpus from PCRE2 semantics and this document's §2. **Every row is a
divergence between python3 `re` and libpcre2 10.46, MEASURED, with the one
probe line that shows it.** Rows the charter expected and that are NOT
divergences are listed too, because a goal-facts list that omits a refuted
expectation invites the author to write it in anyway.

### 7.1 REAL divergences — libpcre2 rules these cells; mark them `# pcre2-only`

| # | divergence | probe line |
|---|---|---|
| G1 | **A lookbehind whose branches have DIFFERENT fixed lengths is legal in PCRE2 and an ERROR in python.** | `(?<=a\|bc)x` — pcre2 ok, python "look-behind requires fixed-width pattern" |
| G2 | **Any variable-width lookbehind body is legal in PCRE2 up to `max_varlookbehind` and an error in python** — `(?<=(a\|bc))x`, `(?<=a{2,3})x`, `(?<=a?)x`, `(?<=(?:a\|bc)d)x`. **pcrec REFUSES these too** (§2.5), so a cell here is a `perr` cell for pcrec and an `ok` cell for PCRE2, and the author must not write a match expectation for it | `(?<=a{2,3})x` — pcre2 ok, python error, pcrec `perr` |
| G3 | **A backreference to a VARIABLE-width group inside a lookbehind is legal in PCRE2, error in python** — and pcrec refuses it (§2.5) | `(a\|bc)(?<=\1)x` — pcre2 ok (maxlb 2), python error |
| G4 | **The alpha spellings do not exist in python at all.** All twelve produce "nothing to repeat at position 1", because python reads `(*` as a quantified `(` | `(*pla:a)b` |
| G5 | **The non-atomic forms do not exist in python.** `(?*` and `(?<*` are "unknown extension" | `(?*a)b`, `(?<*a)b` |
| G6 | **`\K` does not exist in python**, so every `\K` cell in this module (all of which are pcre2 COMPILE ERRORS, err 199) is a compile error in python for a **different reason** — "bad escape \K". The author must not treat the agreement as agreement | `(?=a\K)x` |
| G7a | **THE ASSERTION-FAMILY EXPANSIONS ARE ALL PYTHON-COMPATIBLE, and this refutes the charter's own warning.** Every one of the nine (§6.1) compiles in python: `(?<=\w)`, `(?<!\w)`, `(?<=\n)` are fixed-width-1 lookbehinds, and `\Z`/`$`'s optional body sits in a lookAHEAD (`(?=\n?\z)`) where python has no width rule. **So the expanded corpus stays python-verifiable and `# pcre2-only` must NOT be put on it** | `(?=\n?\z)x` — python ok; `(?<=\n?\z)x` — python "look-behind requires fixed-width pattern". The DIRECTION is the whole difference |
| G7 | **`\A`/`\Z`/`\z` differ between the oracles** (inherited from `assertions_design.md`, not this module's, and it bites here because lookaround bodies contain them): python's `\Z` is PCRE2's `\z` | `(?<=a)b\Z` vs `(?<=a)b\z` |

### 7.2 NOT divergences — the charter expected these and they are refuted

| # | the expectation | what was measured |
|---|---|---|
| G8 | *"python lacks quantified lookaround"* | **FALSE.** python compiles all fourteen forms tried (`(?=a)*`, `(?=a)+`, `(?=a){2}`, `(?!a)?`, `(?=a)*+`, `(?=(a))*`, …) and **agrees with libpcre2 on all nine behavioural cells** (`out/spellings.txt` A4). `# pcre2-only` on a quantified-lookaround cell would throw away a working oracle — which is R32 C3's finding (two corpus files marked python-verifiable in the direction that LOSES the oracle), in the other direction |
| G9 | *"python's handling of captures in negative lookahead"* differs | **FALSE.** The two oracles agree on **all 27 capture cells** in `out/captures.txt` — C1 (positive, retained), C2 (negative, discarded), C3 (positive that fails after capturing, unset), C4 (under a quantifier). python is a usable oracle for the whole capture axis |
| G9a | *"python `re` cannot take several expansions"* (the 2026-08-23 charter addition) | **FALSE for every expansion in the family.** MEASURED, `out/expansions.txt` E3: all nine compile in python. The variable-width lookbehind python rejects — `(?<=\n?\z)` — appears in NO expansion, because `\Z`'s definition is a lookAHEAD. The warning is real about the CONSTRUCT and wrong about the SET |
| G10 | *"python's same-width lookbehind rule"* is one rule | **It is narrower than "same width".** python accepts `(?<=ab\|cd)x` (two branches, same length) and rejects `(?<=a\|bc)x`. So the divergence is about **differing** widths, not about alternation |

### 7.3 What the blinded author should be told about pcrec, and nothing more

- The construct table §2.1 (which spellings exist and what each one IS).
- The rule §2.5 (which lookbehind bodies pcrec compiles), stated as a promise,
  not as an implementation.
- That captures inside a positive lookaround are retained, inside a negative
  one are discarded, and are unset when a positive one fails (§2.4/§2.6's
  cells, stated as behaviour).
- That `\K` inside a lookaround is refused.
- That a lookbehind reads subject bytes before `startpos` (§3.8) — so the
  corpus should contain `ms`/`ns` cells, which is the axis a startpos-blind
  corpus would miss entirely.
- That the ASSERTION FAMILY has lookaround definitions (§6.1's table), because
  the author's corpus should contain the expansions as ordinary patterns — they
  are the most heavily-exercised real lookarounds this module will ever see and
  they are the [M6.6.3] author's cheapest source of non-invented cells.
- **Nothing about the cut, the seam entry, the slots, the prefilter, the
  substitution driver, or `[ENG-LOOK]`.** The driver is a TEST-side generator
  built from the same table; an author who knew about it would be writing the
  driver's corpus a second time instead of an independent one.

---

### 10.1 The construct population for the blinded corpus

Counting **spellings × contexts**, which is what the [M6.6.3] author sizes
against:

| axis | count | what it is |
|---|---|---|
| spellings | **18** | 4 `(?` forms + 2 non-atomic `(?` forms + 6 short alpha + 6 long alpha (§2.1) |
| distinct CONSTRUCTS behind them | **6** | pos/neg × ahead/behind, plus non-atomic pos ahead/behind |
| body shapes per construct | **9** | empty; a literal; a class; a fixed multi-character; same-length alternatives; different-length alternatives (lookbehind only); a capture; a nested lookaround; a backreference |
| contexts | **7** | pattern start; pattern end; mid-pattern; inside an alternation branch; under `*`, `+`, `{n,m}`; inside a capture; inside an atomic group |
| refusal cells | **8** | unbounded body; bounded-variable body; single-branch variable body; backref to a variable group; `\K` in each of the four polarities |
| oracle axis | **2** | python-verifiable vs `# pcre2-only` (§7) |

**Corpus size: ≈ 6 × 9 × 7 ≈ 380 behavioural cells plus ≈ 40 refusal cells**,
before subjects. At 4-6 subjects per block that is **1,500-2,300 match
expectations** — the same order as `tests/backrefs/` and `tests/atomic_groups/`.

**THREE POPULATION REQUIREMENTS THAT ARE NOT SIZE**, each because a sabotage
row above is otherwise unfalsifiable:

1. **The corpus MUST contain at least one of §5.5's 16 qualifying shapes** —
   a lookaround inside an alternation with a bounded-repeat, mandatory-tail
   follow — or **S-LA12 cannot go red** and §5.6's ruling has no test.
   `((?:a(?!q)|aq)(?:xy){0,4}q)` on `"aqq"` is the measured witness and
   belongs in `tests/lookaround/prefilter.rxt` by name.
2. **The corpus MUST contain `ms`/`ns` startpos cells over a lookbehind**, or
   **S-LA8** cannot go red and §3.8's contract claim is untested.
3. **The corpus MUST contain a LONG-SUBJECT LEADING multi-branch lookbehind**
   (R33 C1-6), or §3.7's `n·Σk_i` work-charge shape is reasoned about and
   never measured — and it is the one shape that can reach `PCREC_ERR_WORK`
   where PCRE2 matches.
4. **The corpus MUST contain an EMPTY capture inside a lookaround and a
   re-entered group across one**, because those are where the trail discipline
   §3.2(3) and §3.3 rely on is discriminating rather than incidental — S105's
   own lesson one construct over.

### 10.1a THE SECOND POPULATION: the expanded assertions corpus

§10.1's ~380 blocks are the module's OWN corpus, written by the [M6.6.3]
blinded author. **§6.3's substitution driver contributes a second population
an order of magnitude larger and costs nothing to author**: 624 generated
patterns over **8,260 libpcre2-verified behavioural cells**, every expectation
inherited from a module that already ships.

The two populations are complementary rather than redundant, and the
difference is worth stating because a reader could take the larger one as a
reason to shrink the smaller:

| | the module corpus (§10.1) | the expanded corpus (§6.3) |
|---|---|---|
| authored by | a D27-blinded author, from §2 and §7 | nobody — generated from a shipped corpus |
| covers | every SPELLING, every body shape, the refusals, the alpha forms, `ms` startpos, the prefilter witness | **one body shape**: the assertion family's, which is one class or one literal |
| its oracle | python where §7 allows, libpcre2 otherwise | the two-comparison self-oracle, plus libpcre2 |
| what it would MISS alone | — | every construct §2 ships that no expansion uses: variable bodies, captures inside a lookaround, the non-atomic forms, quantified lookaround, nesting, the alpha spellings |

**So the expanded corpus is a DEPTH instrument on one shape and the module
corpus is a BREADTH instrument**, and §11's landing bar asks for both.

