# [CLS-TREE] — THE STUDY: a per-section class-matcher kit, measured

Lane `clstudy`, branch `lane/clstudy`, worktree `worktrees/clstudy`, on `main`
at `13b56a12`. **Study only** — nothing under `src/`, `tests/` or
`docs/spec/`; no design note, no panel, no build. The prototypes live in
`studies/cls_tree_study/` and are never the compiler.

Every number here comes from that directory's own harness, on this box (Mac
M1, darwin 25.6.0, `gcc-16`, `-O2 -std=gnu11`). Sizes are `.text + .rodata`
of a `.o`. Correctness is **exhaustive**: every matcher this study built was
compared against an independently constructed reference on all 1,114,112 code
points, not on a sample.

---

## 0. What the study was asked, and what it answers

The brief asks four things. In one line each, before the evidence:

1. **Which representation per set-structure class?** There is no per-class
   answer, because the winning matcher is never one representation — the
   populations want 17 to 36 sections of four or five different forms in one
   matcher. The kit, not a pick from it, is the answer (§4).
2. **The sectioning rule, as measured output?** Minimize
   `rodata + text + λ·probe-ops` over contiguous partitions by dynamic
   program; λ IS the dial. What that search picks, described rather than
   prescribed, is §5.
3. **Discovery compile-time, and the D77 verdict on the cache?** 26.4 ms on
   the worst real set, in C, single-threaded. **The cache is NOT triggered**
   (§6).
4. **The property-testing exploit of provenance-blindness?** Composition
   identities as a free oracle, on arbitrary unreachable sets: 438 cells,
   1,114,112 code points each, zero mismatches (§7).

And the headline the brief did not ask for: **all 312 property sets cost
3,977,754 object bytes today and 85,613 as kit matchers — 46.5×**, with
`\p{L}` alone going 227,409 → 4,359 (§3).

---

## 1. Populations

Read out of the tree's own generated data, never re-derived from the UCD.
`studies/form_char_twins` set that rule and the reason survives here: a set
re-derived from source data can disagree with the set the compiler actually
builds, and then the study measures its own parser.

| population | what | size |
|---|---|---|
| `uprops` | the DISTINCT sets behind module `unicode-props`' 717 name rows, parsed from `src/parse/uprops_tables.inc` | **312 sets, 10,961 intervals** |
| `k53` | the six sets K53 named, each with its complement | **12 sets**, 677–931 intervals |
| `byteclasses` | 256-bit membership words parsed off EMITTED artifacts over the shipped corpus | **41 distinct sets** from 3,452 compiled pattern blocks |

Two facts about the populations are already findings.

**The worst real set is 931 intervals, not thousands.** `Xwd`'s complement
tops the list; `\p{L}` is 677. Every compile-time bound in §6 is against
these, not against a hypothetical.

**The shipped corpus contains only 41 distinct byte classes, and every one
has between 2 and 4 intervals** (27 have two, 10 have three, 4 have four).
There is no degenerate many-interval byte class in pcrec's corpus at all.
That is a direct answer to the plan row's "a degenerate `[...]` that today
gets a flat 32-byte bitmap": the shape exists in the row's imagination and
not in this tree's corpus, and [UTF-RW]'s real-world harvest is the row that
would change that — the byte tier's win here is a different one (§4.3).

---

## 2. The shape, and why the seed is a special case of it

An emitted matcher is three things:

```
1. one global bound test         cp outside [lo_0, hi_last] -> 0
2. a balanced binary DISPATCH TREE over the section boundaries
3. at each leaf, that section's own chosen TEST
```

A **section** is a contiguous run of the interval list. Because the intervals
are sorted, disjoint and non-adjacent, the sections partition the code-point
axis in order, and the dispatch tree establishes `base[s] <= cp <= top[s]`
before a leaf runs — so **a leaf never needs a bound test of its own**, only
a test that distinguishes members from the gaps inside its span.

[CLS-TREE]'s seed — "a class implementation that is a binary tree of ranges"
— is this shape with every section holding one interval and every leaf the
trivial test. That is worth stating plainly: **the seed is not an alternative
to the kit, it is one of the kit's settings**, and the study reaches it as
the `λ→∞`-on-a-sparse-set corner rather than as a separate candidate. Frank's
reframing ("composed per-section from a small kit, statically selected") is
strictly more general and costs nothing to be more general, which is the
general-mechanisms rule paying off before any code ships.

### The kit

`x` is `cp - base`; `k` is the section's interval count; `W` its span.

| member | applies | test | rodata |
|---|---|---|---|
| `ALL` | k = 1 | `1` | 0 |
| `RANGES` | k ≤ 8 | OR of `(unsigned)(x-a) <= b-a` | 0 |
| `CUBES` | W ≤ 256 | OR of `(x & care) == val` | 0 |
| `MASK64` | W ≤ 64 | `(mask >> x) & 1` — **no load** | 0 |
| `BITMAP` | any | `(t[x>>3] >> (x&7)) & 1` | ⌈W/8⌉ |
| `PAGE64` | W ≥ 128 | `(leaf[idx[cp>>6 - pb]] >> (cp&63)) & 1` | pages + 8·distinct leaves |
| `BSEARCH` | k ≥ 8 | binary search over the section's intervals | 8k |

`PAGE64` is PCRE2's own property-lookup shape (plane → page index → bitmap
leaf) with the leaves deduplicated. Pages are **absolute** (`cp >> 6`), not
base-relative, which is what makes the page decomposition a property of the
SET rather than of the sectioning — and that is what lets §6's search price
the form in O(k) without building it.

---

## 3. THE HEADLINE: what this costs today, and what it costs as data

`baseline.py` compiles one `\p` spelling of each of the 312 sets with the
worktree's own `build/pcrec` under `--features unicode-props -e utf8` and
sizes the resulting `.o`. **`-e utf8` is not optional**: under `byte` every
one of these sets is clamped to Latin-1 and tiny, which is exactly the trap
[K53-SELRETRY] §4 recorded.

The comparison is OBJECT bytes on both sides. Comparing the kit's object
against pcrec's 772,418 bytes of emitted *source* for `\p{L}` would flatter
the kit by whatever the comments weigh.

| set | intervals | **today** (obj) | **kit, `mid`** | ratio |
|---|---:|---:|---:|---:|
| `\p{Xwd}` | 930 | 294,153 | 5,326 | **55.2×** |
| `\p{Xan}` | 770 | 267,541 | 4,959 | **53.9×** |
| `\p{C}` | 736 | 228,957 | 4,667 | **49.1×** |
| `\p{L}` | 677 | **227,409** | **4,359** | **52.2×** |
| `\p{Unknown}` | 729 | 215,055 | 4,684 | **45.9×** |
| `\p{Ll}` | 662 | 70,529 | 1,635 | **43.1×** |
| `\p{Lu}` | 651 | 63,024 | 1,508 | **41.8×** |
| **all 312 sets** | **10,961** | **3,977,754** | **85,613** | **46.5×** |

**`obj_text` is a constant 788 or 672 bytes across every row of the
baseline.** Today's cost for a code-point class is not code at all — it is
automaton TABLE bytes, entirely. That confirms K53's own diagnosis
("intervals decomposed into byte-sequence states") as a measured property of
all 312 sets rather than of the six the entry examined, and it is why any
class-as-DATA layout collapses them: there is nothing else in the artifact to
collapse.

---

## 4. Deliverable (1): which representation, per set-structure class

**The question as posed has no answer, and that is the finding.** No single
representation wins any of the real code-point sets. The winning matcher for
`\p{L}` at the middle policy is 27 sections: 16 `ALL`, 7 `BITMAP`, 3
`PAGE64`, 1 `BSEARCH`. At the pure-size end it is 19 sections of five
different forms. A per-class dial setting ("big sets get the tree") would be
choosing among matchers none of which the search ever proposes.

What the populations DO support is a ranking of members by whether they earn
their place at all:

### 4.1 What the 312 sets actually choose

Section shares across the whole property population, by policy:

| policy | `ALL` | `MASK64` | `PAGE64` | `BITMAP` | `RANGES` | `BSEARCH` | `CUBES` | sections |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| size | 18.8% | **33.3%** | **24.0%** | 0% | 20.7% | 2.7% | 0.5% | 812 |
| mid | **71.6%** | 10.4% | 5.5% | 8.6% | 0% | 2.6% | 1.3% | 1,168 |
| speed | **78.7%** | 4.1% | 3.8% | **12.7%** | 0% | 0% | 0.7% | 1,161 |

Four things are legible in that table and none of them were assumed:

1. **`ALL` dominates once speed is priced at all** (72–79%). Most sections of
   a real property set are a single wide interval, and the dispatch tree has
   already bounded it — so most of the matcher is a binary search that
   returns without testing anything. That is [CLS-TREE]'s seed shape winning
   at the level of the *dispatch*, while losing as a *leaf* form (§4.2).
2. **At the size end the biggest single form is `MASK64`** (33.3%) — a dense
   span of ≤ 64 code points as a 64-bit immediate, **no memory reference at
   all**. This is the plan row's own reframing hypothesis ("a dense ≤64-code-
   point span → a single uint64 mask test (NO memory load)") confirmed as the
   single most-chosen leaf form when bytes are what matters.
3. **The two table forms swap ends.** `PAGE64` is 24.0% at the size end and
   3.8% at the speed end; `BITMAP` is **absent entirely** at the size end and
   12.7% at the speed end. They are not competitors at a crossover — they are
   the size answer and the speed answer to the same question, and the dial
   picks between them.
4. **`RANGES` exists only at the size end** (20.7%, zero elsewhere), which is
   the measured `.text` cost of §5.2 doing its job: 12 bytes an interval is
   cheap in `.rodata` terms and is the first thing a speed-weighted objective
   discards.

### 4.2 `BSEARCH` — the seed — is a marginal member

[CLS-TREE]'s own seed representation — a binary search over a section's
interval table — is **2.7% of sections at the size policy, 2.6% at the
middle, and ZERO at the speed policy** across all 312 property sets; on the
12 K53 sets it is chosen 12 times in 72 cells, always exactly once per
matcher. It earns a place in the kit and it is nobody's main story.

This is worth separating carefully, because the seed's name is doing two
jobs. **As a DISPATCH, binary search over ranges is the whole architecture**
— every matcher here is one (§2), and `ALL`'s 72–79% share at the middle and
speed policies is that dispatch answering without any leaf test at all. **As
a LEAF FORM it is the least-used member in the kit.** A design that built
"a binary tree of ranges" and stopped would have got the important half
right by accident and the measured-least-valuable half on purpose.

### 4.3 `CUBES` — where CONSTITUTIONAL CONSTRAINT 1 is discharged as a measurement

The kit's cube member takes a section and asks one O(k) question: **do the
members agree on every bit but a free set?** If they do, the section is one
don't-care cube and the test is `(x & care) == val` — one AND, one compare,
no table. It is never told what the set is for.

Constraint 1 named two customers for that question in advance. Both are
confirmed, in the real data, and a third turned up.

**(a) The `\p{Lu}` parity block — the constraint's own named non-caseless
customer** ("`\p{Lu}` over adjacent-pair blocks (Latin Ext-A) = range +
parity (m=0x01 fold)"). Measured, at the middle policy:

| set | section | intervals | members | the one cube |
|---|---|---:|---:|---|
| `\p{Lu}` | U+1E00..U+1E7E | **64** | 64 | `(cp - 0x1E00) & 1 == 0` |
| `\p{Lu}` | U+04D0..U+052E | 48 | 48 | `(cp - 0x04D0) & 1 == 0` |
| `\p{Ll}` | U+1E01..U+1E7F | **64** | 64 | `(cp - 0x1E01) & 1 == 0` |
| `\p{Ll}` | U+048B..U+04BF | 27 | 27 | `(cp - 0x048B) & 1 == 0` |
| `\p{Lt}` | U+1F88..U+1FAF | 3 | 24 | `(cp - 0x1F88) & 8 == 0` — five free bits |

Latin Extended Additional alternates upper and lower case code point by code
point, so `\p{Lu}` there is **64 separate single-code-point intervals** — and
it collapses to two instructions with no memory reference. The alternative in
the kit is a 16-byte `BITMAP` plus a load, or a 64-term compare chain. The
cube is found in O(k) from the endpoints, without enumerating a member.

**(b) The ASCII case fold, rediscovered at the byte tier.** `bc011` is the
corpus byte class `{0x53, 0x73}` — `{'S','s'}`. Given nothing but the set,
`cube_of` returns `care = 0x1F, val = 0` over `x = cp - 0x53`, i.e. **bit 5 is
free** — which written absolutely is `(c | 0x20) == 's'`. That is
[FORM-CHAR]'s shipped `ascii-fold` object, byte for byte. The whole emitted
matcher is:

```c
int cls_kit(unsigned cp)
{
    if ((unsigned)(cp - 83u) > 32u) return 0;
    return (int)((((cp - 83u) & 0x1Fu) == 0x0u));
}
```

Today pcrec reaches the same code through `vm_cls_shape`, a classifier that
asks *"are these two bytes a case-fold pair"*. The kit asks *"do the members
agree on every bit but one"*. **The second question is strictly more general
and no more expensive.**

**(c) And the general form covers TWICE the population the special case
does.** `CUBES` is chosen for 8 of the 41 corpus byte classes, and only four
of those eight are case-fold pairs:

| set | members | the one cube, absolutely | today's `cls-fold` classifier |
|---|---|---|---|
| `bc017` | `{A,a}` | `(c \| 0x20) == 'a'` | **sees it** — `(lo^hi)==0x20`, both letters |
| `bc011` | `{S,s}` | `(c \| 0x20) == 's'` | **sees it** |
| `bc033` | `{Z,z}` | `(c \| 0x20) == 'z'` | **sees it** |
| `bc035` | `{B,b}` | `(c \| 0x20) == 'b'` | **sees it** |
| `bc018` | `{a,c}` | `(c & ~0x02) == 'a'` | **blind** — xor is 0x02, not 0x20 |
| `bc032` | `{g,k}` | `(c & ~0x04) == 'g'` | **blind** — xor is 0x04 |
| `bc019` | `{A,B,a,b}` | `(c & ~0x21) == 'A'` | **blind** — not a pair at all; two free bits |
| `bc024` | (2 sections) | `ALL` + one cube | **blind** |

The four "blind" rows are emitted today as 32-byte bitmap tables plus a
load-shift-and. **The shipped special case covers half of its own general
form's population in this tree's own corpus**, which is the
general-mechanisms rule (memory
`pcrec-general-mechanisms-not-special-cases`) stated as a count rather than
as a principle.

Across the 312 property sets, `CUBES` is chosen **27 times in 19 cells over
11 distinct sets** (`Lu`, `Ll`, `Lt`, `Z`, `Zs`, `Cyrl`, `Syrc`, `Glag`,
`Hung`, `Tfng`, `Tutg`). It is a narrow member. It is also the one that
turns a 64-interval section into two instructions, and the one whose
existence is an argument about mechanism rather than about bytes.

### 4.4 `MASK64`, and the byte tier's tables going to zero

`bc000` is `\w` (4 intervals, 63 members, span 75): the kit emits **two
sections, 56 bytes of `.text`, zero `.rodata`**, against the 32-byte bitmap
table plus load that pcrec emits for a bitmap-class site today.

**Across the whole byte-class population the tables disappear.** At the
middle policy the 41 sets compile to **1,584 bytes of `.text` and exactly
ZERO bytes of `.rodata`**, 16–68 bytes per class, in 82 sections total (69
`ALL`, 8 `CUBES`, 5 `MASK64`). The corpus carries **319 byte-class sites**
across those 41 distinct sets; every one of them is a 32-byte table today.
246 of 246 byte-class cells verify exhaustively.

---

## 5. Deliverable (2): the sectioning rule, as measured output

### 5.1 The search

`section.py` / `discover.c` run the same exact dynamic program over
contiguous partitions:

```
best[j] = min over i of  best[i] + rodata(i..j) + text(i..j) + λ·ops(i..j)
```

It is exact over contiguous partitions because a section is a contiguous run
and the sections are ordered, so where section j ends is independent of
everything before it given where it starts. λ prices one probe op against one
byte, and **sweeping λ traces the size/speed Pareto frontier** — which is the
shape [OPT-DIAL]'s five-setting dial needs, arrived at from the algorithm
rather than fitted to the dial afterwards.

### 5.2 The cost model is MEASURED, and the first version of it was wrong

The first cost model priced a section by its `.rodata` alone. The first full
Pareto sweep refuted it on sight: `\p{L}` at the pure-size policy came out at
**9,672 bytes and 1,302 probe ops** against the middle policy's **4,311 and
111** — smaller and faster at once. A frontier point dominated on both axes
is not a trade-off, it is a modelling error.

The cause: `RANGES` chains are free in `.rodata` and expensive in `.text`,
and the model could not see the bill. `.text` was then measured two
independent ways —

* `calibrate.py`: OLS of measured `.text` on per-form section counts over 72
  real sweep rows. **R² = 0.9996**, worst residual 211 bytes.
* `calibrate_direct.py`: a slope between synthetic 8-section and 32-section
  single-form matchers.

— and **the two routes disagree, which is itself reported rather than
averaged away**: the OLS reads `RANGES` at 117 bytes/section against the
direct route's 52, and `MASK64` at 86 against 24. The synthetic route's
sections are structurally identical so gcc shares code between them; the OLS
sees real heterogeneous sections. The direct slopes were adopted because only
they can price a form the population never chooses (`CUBES` is an
unidentified column in the OLS — zero sections) and only they expose the one
form whose cost is **linear in k**: `RANGES` measures 12 bytes per interval,
`BSEARCH` is flat at 104 (a call to the one shared helper).

With `.text` in the objective, `\p{L}`'s frontier becomes monotone:

| policy (λ) | sections | text | rodata | total | ops | forms |
|---|---:|---:|---:|---:|---:|---|
| size (0) | 19 | 1,392 | 2,926 | 4,318 | 206 | ALL 1, RANGES 3, MASK64 2, PAGE64 12, BSEARCH 1 |
| (4) | 17 | 1,168 | 3,028 | **4,196** | 175 | ALL 3, RANGES 2, BITMAP 1, PAGE64 10, BSEARCH 1 |
| mid (16) | 27 | 1,184 | 3,175 | 4,359 | 108 | ALL 16, BITMAP 7, PAGE64 3, BSEARCH 1 |
| (64) | 25 | 1,076 | 4,283 | 5,359 | 78 | ALL 14, BITMAP 9, PAGE64 2 |
| speed (256) | 25 | 1,072 | 4,778 | 5,850 | 72 | ALL 14, BITMAP 10, PAGE64 1 |
| maxspeed (∞) | 11 | 688 | 24,308 | 24,996 | 66 | BITMAP 11 |

**A residual inversion is left in and named**: λ=0 (4,318 bytes / 206 ops) is
still slightly dominated by λ=4 (4,196 / 175). The model's byte term is
accurate to about 3%, and at the extreme size end 3% is enough for two
adjacent policies to invert. It does not affect any conclusion here, and it
is the honest statement of how good a `.text` model built this way gets.

### 5.3 What the search picks — the rule, described

Over the real populations the answer has a stable shape, and this is the
sectioning rule stated as an observation rather than as a prescription:

1. **Sections break where DENSITY breaks, not where intervals are.** On the
   K53 sets, section counts of 17–36 sit an order of magnitude below interval
   counts of 677–931; population-wide the 312 sets' 10,961 intervals resolve
   into 1,168 sections at the middle policy, a **9.4× collapse**. The search
   is finding runs of similar local density and giving each one the form that
   suits it — which is why no per-class representation answers §4.
2. **`ALL` absorbs the wide blocks and its share grows with λ** (1 section at
   λ=0, 16 at λ=16, 14 at λ=256 for `\p{L}`). A wide contiguous block is free
   once the dispatch has bounded it, so speed buys `ALL` sections by
   splitting sections that a byte-table would otherwise have covered.
3. **`PAGE64` is the size end's workhorse and `BITMAP` is the speed end's**,
   population-wide (§4.1's table: 24.0% → 3.8% and 0% → 12.7%) and on single
   sets (`\p{L}` goes from 12 `PAGE64` / 0 `BITMAP` at λ=0 to 1 / 10 at
   λ=256). The dial's real content at the code-point tier is *how many
   dependent loads will you pay to shrink the tables* — `PAGE64`'s second
   load is the whole trade.
4. **The extreme speed end collapses to few, huge `BITMAP` sections** —
   `\p{L}` at λ=∞ is 11 sections and 24,308 bytes, a 5.6× size blow-up for
   the last 6 probe ops. That is a bad cell, and naming it is useful: the
   dial's speed notches should stop before it.
5. **The byte tier never reaches any of this.** Every corpus byte class
   resolves in one or two sections of `MASK64`/`CUBES`/`ALL` with no table at
   any policy.

---

## 6. Deliverable (3): discovery compile-time, and the D77 verdict

**The measurement.** `discover.c` is the same DP in C, timed over 10–20
repetitions. Over the **60 largest property sets** (every set with ≥ 46
intervals), C discovery at the middle policy is **mean 4.19 ms, max 25.86
ms**. The individual worst cases:

| set | intervals | discovery, C | discovery, Python |
|---|---:|---:|---:|
| `^Xwd` | 931 | **26.7 ms** | ~1.6 s |
| `Xwd` | 930 | **26.4 ms** | ~1.6 s |
| `\p{L}` | 677 | **22.7 ms** | 1.55 s |

(The Python DP is the same algorithm producing the same answers — §8 — at a
measured **mean 141×, max 472×** slower. It is an implementation cost, not a
different algorithm, which is exactly why the compile-time question had to be
answered in C and not in the prototype language.)

Two properties of the algorithm, not of the data, are what make this hold:

* **Cost is evaluated without materializing tables.** Every kit member's cost
  is O(1) or O(k) from the interval endpoints — `PAGE64`'s distinct-leaf
  count included, because absolute page alignment means only the pages an
  interval *starts or ends in* can be partial. Tables are built only for the
  sections the answer keeps.
* **Sections are capped at 64 intervals**, so the DP is O(n·64), not O(n²).

**THE D77 VERDICT: CONSTITUTIONAL CONSTRAINT 2'S CACHE IS NOT TRIGGERED.**
26.4 ms on the worst real set, single-threaded, is not a cost that justifies
a committed pre-analysis store, a content-hash key, an analyzer-version
stamp, a standing sample-equality check and a `third_party/`-shaped
generation step. For scale: this study's own `baseline.py` measured
`build/pcrec` taking 144 ms to compile `\p{Xwd}` today — **discovery for the
worst set in the tree costs less than one fifth of what that one pattern
already costs the compiler.** The constraint's own gate ("build only on the
study's cost measurement") therefore closes it.

Two qualifications that keep the verdict honest:

* It is a per-SET cost. A pattern with many distinct `\p` sections pays it
  per set, and the measurement is per set. Nothing here bounds a pathological
  pattern with hundreds of distinct large classes; that would be a fresh
  measurement, and the cache's design would then be re-openable on it.
* The 26.4 ms figure is for the **tier-1** kit (§6.1). It is the
  configuration this study recommends, and the verdict is stated for it.

### 6.1 The expensive half of discovery buys 0.36% and is dropped

`CUBES` was implemented in two tiers: tier 1 is `cube_of`, an O(k)
closed-form test for whether the section is EXACTLY ONE cube; tier 2 is a
full Quine–McCluskey two-level minimization, exact at these widths, for
multi-cube covers in the band `64 < W ≤ 256`.

Measured over 126 cells (42 sets × 3 policies):

| | discovery total | rodata total | probe-ops total | sectionings changed |
|---|---:|---:|---:|---:|
| tier 1 + tier 2 | **571.7 s** | 244,928 | 36,659.4 | — |
| tier 1 only | **116.3 s** | 244,894 | 36,792.4 | 10 of 126 |

Tier 2 costs **4.9× the discovery time** to change 10 of 126 sectionings, for
**0.36% fewer probe ops** at 34 more bytes. It is dropped, and `discover.c`
never implemented it. The cheap tier is the one that finds the case fold.

This is the study's clearest instance of a general point: **the algebraically
impressive half of the analysis was the half that did not pay.** An exact
two-level minimizer over an 8-bit boolean function is the textbook answer to
"byte class = boolean fn over 8 bits → exact minimization feasible" from
CONSTITUTIONAL CONSTRAINT 1's own framing, and it is feasible, and it is not
worth running.

---

## 7. Deliverable (4): the property-testing exploit of provenance-blindness

CONSTITUTIONAL CONSTRAINT 1 is usually argued as a design virtue. It is also
a **testing lever**, and a sharp one. If the matcher is a function of the set
and of nothing else, then two things follow that a provenance-tagged design
could not claim:

**The test population need not be reachable from any pattern.** Arbitrary
sets are legitimate inputs, so the generator can produce structures no regex
would ever build — and those are the ones that break a form's preconditions.
`proptest.py` ships eight generators, each an attack on one member:
`sparse`, `dense`, `comb` (the parity cube), `fold` (`{x, x^bit}`), `orbit`
(complete orbits under 2–3 free bits), `boundary` (intervals pinned to the
64/256/0x10000 seams), `random`, and `pathologic` — one member every 65 code
points, so every page is distinct and non-empty and `PAGE64`'s leaf dedup
buys exactly nothing.

**Every composition of sets is an oracle for free.** Membership commutes with
union, intersection, difference and complement, so for any A and B:

```
kit(A ∪ B)(cp)  ==  kit(A)(cp) || kit(B)(cp)      for every cp
```

where the left side ran discovery ONCE on a merged set and the right ran it
TWICE on unmerged ones — different sectionings, different form choices,
different emitted code. **No external oracle is consulted**, and a bug cannot
hide, because it would have to corrupt both sides identically through two
different sectionings.

This check is only *available* because the form is provenance-blind. Had the
dial read a "this came from `\p`" or "this came from caseless expansion" tag,
`A ∪ B` and `kit(A) || kit(B)` would be entitled to differ and the identity
would not be a law to test against. Constraint 1 buys the test.

**Result: 438 cells, every one comparing all 1,114,112 code points — 488
million compared answers — with ZERO mismatches**, across 4 operators × 3
policies × 40 generated pairs (the shortfall from 480 is compositions that
came out empty, which are skipped rather than counted).

Two caveats stated rather than buried: the composed set `C` is normalized to
pcrec's own sorted/disjoint/non-adjacent invariant before discovery (the kit
is entitled to assume it), so this tests the kit and not a normalizer; and
`proptest.py` is seeded and therefore reproducible but not exhaustive over
structures — it is a property test, not a proof.

---

## 8. The checks that caught this study's own bugs

Three defects were found by instruments inside the harness, and each is worth
more than the bug.

**A cost model that prices without building is only safe if something builds
and checks.** `PAGE64` is priced in O(k) without materializing its tables —
that is what makes §6's verdict possible. The first version double-counted a
64-wide page shared by two consecutive intervals, which suppressed the
all-empty leaf and under-priced the form by 8 bytes on one section of
`\p{L}`. It was found by comparing *the price the DP paid* against *the table
the emitter actually wrote*, a comparison `make k53` now runs on every cell.

**Two implementations of one algorithm find what one cannot.** `discover.c`
was written from the cost model rather than translated from the Python, and
`crosscheck.py` compares section boundaries and form choices over a whole
population. It found an integer floor `log2` in the C against `math.log2` in
the Python (moving `\p{L}` at the middle policy from 28 sections to 27), and
later a duplicated fixed term in the Python's `RANGES` text cost that made
the two disagree on **12 of 36 cells, every one at the pure-size policy**
where `RANGES` is the form under contention. Both implementations were
self-consistent throughout. Only the comparison could see either.

**A frontier point dominated on both axes is a modelling error, not a
result.** §5.2. The Pareto sweep was built to characterize a trade-off and
its first output was a refutation of the cost model that generated it.

---

## 9. What this study does NOT settle

Named, not hidden.

* **ns/char is measured only on the K53 twelve** (§10), and only as a
  membership loop over a code-point array — not inside either engine. The
  interaction with the VM's per-position loop and with the DFA's byte-wise
  walk is [CLS-TREE]'s design-pass question, not this study's, and the plan
  row's own item (2) (the DFA/hybrid seam — "a byte-wise DFA cannot search
  mid-state") is untouched here. Nothing in this memo licenses a claim about
  end-to-end matcher throughput.
* **The dispatch tree is balanced by section count, not by frequency.** A
  frequency-weighted tree (common sections shallower) is an obvious next
  variant and is unmeasured; it needs a code-point frequency model, which
  needs [UTF-RW]'s real-world harvest.
* **The byte tier's population is 41 sets from this tree's own corpus**, all
  2–4 intervals. [UTF-RW]'s harvest is the row that would say whether real
  non-English patterns produce the many-interval byte classes the plan row
  imagines; if they do, `CUBES`' tier-2 verdict (§6.1) is re-openable on a
  population that has structure for it to find.
* **`MAXK = 64`** (intervals per section) is a search bound chosen to make the
  DP O(n·64) and never swept. A larger cap can only lower cost; nobody
  measured by how much.
* **The Linux arm is unexercised.** `sweep.obj_sizes` carries an ELF `size -A`
  path but every number here is Mach-O `size -m` on the Mac.
* **No `src/` consequence is proposed.** Per the brief: the design note picks
  the kit and the sectioning rule from these numbers; this memo does not.

---

## 10. Verification totals

Every matcher this study built was compared against an independently
constructed reference on **all 1,114,112 code points**. Not a sample.

| arm | cells | result |
|---|---:|---|
| `uprops` — 312 sets × 3 policies | 936 | **936 PASS, 0 FAIL** |
| `k53` — 12 sets × 6 policies | 72 | **72 PASS, 0 FAIL** |
| `byteclasses` — 41 sets × 6 policies | 246 | **246 PASS, 0 FAIL** |
| composition property test (§7) | 438 | **438 PASS, 0 FAIL** |
| C-vs-Python DP cross-check (K53 ×3 policies, 60 largest uprops ×1) | 96 | **96 AGREE, 0 DIFFER** |

**1,692 verification cells × 1,114,112 code points = 1.885 billion compared
answers, zero mismatches**, plus 96 cross-implementation sectioning
comparisons, zero disagreements.

## 11. Timing — OWED, and deliberately not forced

`bench.py` is written, committed and runnable: five arms per set (the flat
`BSEARCH` reference — [CLS-TREE]'s seed; one whole-span `BITMAP`; and the kit
at each policy), four subject regimes (`member` / `mixed` / `ascii` / `full`),
11 rounds with **arms interleaved round by round**, every round's answer
checksummed against the reference arm, and the 1-minute load average gated
below 0.5 — the protocol `docs/dev/lanes/isl1_report.md` §12 established and
`studies/form_char_twins` §8 reused, copied rather than re-invented so the
numbers are comparable across studies.

**It refused.** The box did not fall below the gate inside this lane's
window — the sizing, verification, property-test and cross-check arms are
this box's compute today, and other lanes are live. The harness does not
caveat a noisy measurement, by construction; relaxing its own gate to
produce a number would be the exact failure `studies/scan_edge_ladder`'s
README already records as a refusal worth making.

**No conclusion in this memo rests on a timing number**, and that is a
property of what was asked rather than good luck: deliverable (1) is a form
census, (2) is a search output, (3) is compile time, and (4) is answer
identity. §9's first entry already states that nothing here licenses an
end-to-end throughput claim, and the ns/char question it names — how these
matchers behave *inside* the VM's per-position loop and the DFA's byte-wise
walk — is the design pass's, not a rerun of this harness.

To run it: `make bench` in `studies/cls_tree_study/` on a quiet box. Results
land at `results/bench_k53.tsv`.

---

## 12. Disclosure

Nothing from injected context shaped a decision beyond the brief. The two
constitutional constraints were supplied verbatim in the brief and are
answered as written: Constraint 1 in §4.3 and §7, Constraint 2 in §6. The
brief's suggestion that a tag "may be a search HINT — accelerates, never
decides" was **not needed and not used**: `cube_of` is O(k) and no search
needed accelerating, so the kit takes no hint argument at all and the
provenance-blindness of §7 is total rather than nearly total. The choice of
kit members, of the DP formulation, of λ as the dial parameter, of the eight
property-test generators and of the two calibration routes were this lane's.
`pcrec-bench` was not read or written.
