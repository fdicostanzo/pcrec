# K18 — a path-sensitive epsilon-closure memo

Design note for the repair of K18 (docs/dev/known_issues.md), written
DESIGN-FIRST and panel-eyed before any rewrite lane opens, per the scheduling
ruled at R21 close. **This note is not the fix.** It carries the defect
analysis, three candidate repairs with head-to-head measurements, a
termination argument, a blast-radius prediction and the validation plan the
rewrite lane should execute.

Every claim below is marked **STRUCTURAL** (follows from the code's own
construction, and the note says which construction), **MEASURED** (a number
this lane produced, with the script that produced it), or **BELIEVED** (an
argument I find convincing but did not reduce to either of the other two).
R21's lesson is that panels break what is BELIEVED, so the marks are set
honestly to point the panel at the soft places rather than to make the note
look strong.

Measurement scripts and prototypes: `docs/design/k18_measurements/`. Every
prototype is built into a SCRATCH COPY of the tree by
`prototypes/mkproto.sh`, so no measurement in this lane ever entered
`src/`, `build/`, or the known-fail ratchet's line of sight.

---

## 1. The defect, precisely

### 1.1 What the closure is supposed to do

`clo_visit` (src/ir/dfa.c) walks epsilon edges from a pre-set in preference
order, emitting the `N_CLASS` states it reaches as a priority-ordered thread
list and stopping at `ACCEPT` when `prune` is on. Its one non-obvious rule is
PCRE's empty-iteration rule, added by K1 and widened by K17: reaching a loop
entry again by epsilon means the iteration in progress consumed nothing, which
ENDS the loop, so the walk follows the loop's EXIT edge at that priority
position — ahead of the body's lower-priority consuming alternatives.

Today that rule fires on the test `cl->seen[s] == cl->gen && st->loop`:
"this state has been visited somewhere in this closure, and it is a loop
entry". **STRUCTURAL:** `seen` is a per-closure memo keyed on the NFA state
alone, stamped once per closure by `marks_next`.

### 1.2 Why a global memo cannot express the rule

The empty-iteration rule is a property of the WALK'S OWN PATH: it asks whether
the loop we just arrived at is one whose body this particular path is
currently inside. `seen` answers a different question — whether any path
explored so far in this closure has touched the state. Those two questions
coincide only when the closure's walk is a single path. It is not; it is a
DFS over a branching epsilon graph.

K17 fixed the sub-case where the conflated state is ITSELF a loop entry, by
making the redirect fire on every re-arrival rather than once. That repair
reaches only arrivals that LAND on a loop entry. K18 is the sub-case where the
walk has to pass THROUGH an already-seen ordinary epsilon state to get to the
loop entry — and the memo kills it one hop short, so no rule stated at loop
entries can see it.

### 1.3 A worked minimal example, traced

Both traces below are printed by an instrumented compiler
(`prototypes/proto_dump.py` and `proto_dumpA.py`), not reconstructed by hand.
Pattern `^(?:(?:a|b*?)?)*`, the anchored member of the diverging family, whose
NFA is small enough to read in full:

    NFA start=0 n=8                          (PCREC_K18_DUMP=1)
       0 SPLIT  t1=6  t2=7  loop=1 exit_is_t2=1   outer `*` entry; exit -> ACCEPT
       1 EPS    t1=0                              the outer star's LOOP-BACK edge
       2 CLASS  t1=1              cls=a
       3 SPLIT  t1=1  t2=4  loop=1 exit_is_t2=0   `b*?` entry; LAZY, so t1 is the exit
       4 CLASS  t1=3              cls=b
       5 SPLIT  t1=2  t2=3                        the alternation `a | b*?`
       6 SPLIT  t1=5  t2=0                        the `?` wrapper
       7 ACCEPT

(The compiler numbers these 2,1,3,4,5,6,7,8 in the anchored machine; the
mapping is 1:1 and the trace below uses the compiler's own numbers, where
state 2 is the loop-back EPS and state 1 is the outer star entry.)

The closure that matters is the one for the position after `a`, whose pre-set
is exactly that loop-back EPS. **MEASURED**, on the shipped compiler:

    closure pre-set {2} bot=0 eol=0 prune=1
      visit  2 EPS    t1=1   loop=0
      visit  1 SPLIT  t1=7   t2=8   loop=1
      visit  7 SPLIT  t1=6   t2=1   loop=0
      visit  6 SPLIT  t1=3   t2=4   loop=0
      visit  3 CLASS  t1=2   loop=0
          EMIT thread 3                       <- the `a` thread, correct
      visit  4 SPLIT  t1=2   t2=5   loop=1    <- `b*?`; lazy, so t1 (its EXIT) is preferred
      visit  2 EPS    t1=1   loop=0 <-- ALREADY SEEN
          DEAD: seen, not a loop entry -- the walk stops one hop short
      visit  5 CLASS  t1=4   loop=0
          EMIT thread 5                       <- the `b` thread, WRONG, and ahead of ACCEPT
      visit  1 SPLIT  t1=7   t2=8   loop=1 <-- ALREADY SEEN
      visit  8 ACCEPT
          ACCEPT

State 2 was marked seen at the very first step, because it IS the pre-set. The
lazy `b*?` then prefers its exit, and that exit edge points straight back at
state 2 — the one state the closure could not re-enter. One hop further on sits
state 1, the outer star entry, whose redirect is the ACCEPT. The walk never
gets there. Thread 5 (`b`) is emitted ahead of the ACCEPT that is finally
reached by a different route, and on subject "ab" the DFA consumes the `b`:
span [0,2) against both oracles' [0,1).

**Nothing K17 could have done reaches this.** K17's repair is a property of
ARRIVALS AT LOOP ENTRIES; the arrival that is lost here is at state 2, which is
not a loop entry and never becomes one. **STRUCTURAL.**

### 1.4 The same closure, repaired

Prototype A (§2a) keys the memo on (state, open-loop-set). **MEASURED:**

    closure pre-set {2} bot=0 eol=0 prune=1
      visit  2 EPS    loop=0  open={} ctx=0
      visit  1 SPLIT  loop=1  open={} ctx=0
      visit  7 SPLIT  loop=0  open={1} ctx=1     <- loop 1 pushed for its BODY edge
      visit  6 SPLIT  loop=0  open={1} ctx=1
      visit  3 CLASS  loop=0  open={1} ctx=1
          EMIT thread 3
      visit  4 SPLIT  loop=1  open={1} ctx=1
      visit  2 EPS    loop=0  open={1} ctx=1     <- SAME STATE, DIFFERENT CONTEXT: not deduped
      visit  1 SPLIT  loop=1  open={1} ctx=1
          REDIRECT: loop 1 is OPEN on this path -> empty iteration ends the loop
      visit  8 ACCEPT
          ACCEPT

The thread list goes from `[3, 5]`+accept to `[3]`+accept. The `b` thread is
never emitted, because the ACCEPT is now reached before it, at the priority
position the empty iteration earns.

Two things changed, and it is worth separating them:

1. the memo key gained the open-loop set, so the second arrival at state 2 is
   a different key and survives;
2. the redirect's trigger changed from "seen and a loop entry" to "a loop
   entry that is OPEN on this path", which is the rule's actual statement.

(2) alone would not fix K18 — the walk still dies at state 2 before reaching
any loop entry. (1) alone would not either — without (2) there is no redirect
to reach. **BELIEVED**, from reading the two changes; I did not build the two
half-prototypes to confirm it, and a panel that wants it MEASURED should say
so, since it is cheap.

---

## 2. The candidate designs

All three were built and measured. Shared measurement apparatus:

* **the existing corpus** — every `pattern` line in `tests/**/*.rxt`, 622
  patterns, of which 555 compile on the base tier today
  (`harvest_patterns.py`);
* **the K18 acceptance corpus** — `tests/known_fail/k18_empty_exit_through_seen_eps.rxt`,
  165 cases, 8 diverging shapes and 7 over-reach controls. Baseline: **26 of
  165 fail** on the shipped compiler;
* **a dense shape-space sweep** — 18,858 patterns built only from the
  ingredients K17 and K18 are made of (`gen_shapes.py`). The K17 entry records
  that the general fuzzer hits this class at ~1e-4, which is far too sparse to
  tell two candidate repairs apart;
* **adversarial and stress families** — nested nullable stars, sibling nullable
  loops, bounded repeats, wide nullable alternations (`gen_adversarial.py`);
* **a counter-instrumented build of the SHIPPED closure**
  (`prototypes/proto_basestats.py`), so every "prototype A expands N states"
  has a denominator. That build emits byte-identical C to the shipped
  compiler on all 555 corpus patterns — **MEASURED**, which is the check that
  the instrumentation is inert.

### 2a. The recorded direction: memo keyed on (state, open-loop-set)

**The design.** Maintain the open-loop stack along the walk's own path. Push a
loop entry when the walk takes its BODY edge; drop it when the frame that
pushed it returns, or when a redirect truncates the stack. Intern each stack to
a small integer context id, so the memo key is two ints. Then:

* the redirect fires on "this loop entry is in the open set", not on "seen";
* the memo suppresses a re-arrival only at the same (state, context);
* `N_CLASS` emission and `ACCEPT` keep a separate GLOBAL per-state dedup, so a
  context-split walk cannot put the same thread in a DFA state's list twice.
  **STRUCTURAL:** a thread's future depends only on its NFA state, so the
  first (highest-priority) occurrence is the only one that can matter.

**The stack is a stack, not a set.** The open loops on any path are properly
nested, so the loop re-arrived at is always the TOP of the stack. That is an
assumption the prototype could have hidden, so it is instrumented instead: the
prototype counts every redirect where the open loop was NOT the stack top.
**MEASURED: 0, over 555 corpus patterns and 52 adversarial patterns**, including
every nesting family up to 60 levels deep. The rewrite should keep that counter
as an assertion rather than delete it.

**The tail recursion does not deepen.** The push for a loop's body has to be
undone when the walk leaves the loop, and the obvious way to arrange that is to
make the body edge a recursive call — which would make C-stack depth grow with
the number of nullable loops in a CHAIN, not just nesting, and `limits.h`
explicitly records that clo_visit's tail edges were made iterative to stop
exactly that. It is not needed: the redirect TRUNCATES the stack to the
re-arrived loop's index, and a frame restores the saved depth on return, so the
push made on an iterative tail edge is always unwound by one of those two.
The preferred-branch recursion is the only recursion, exactly as today.
**STRUCTURAL**, from the prototype's control flow.

#### Cost: what the open-loop set actually costs

The open set's cardinality is the loop-NESTING depth. **MEASURED**, over the
555 compiling corpus patterns (`summarise.py`):

| max open-set size | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| patterns | 353 | 176 | 17 | 7 | 1 | 1 |

So the brief's question — "is real nesting depth ever >3?" — answers **twice in
555**, and those two are `(b*?(a*|b*)*)*` and `(?:b*?(?:(?:a*)*)*)*`, both of
which are K17's own guard-test patterns rather than anything a user wrote.
Distinct contexts per pattern: 353 patterns need exactly 1 (the empty one), and
the maximum over the whole corpus is **19**.

The memo's inflation over the shipped walk, same patterns, same counters
(`inflation.py`):

| | aggregate | p50 | p90 | p99 | max | unchanged |
|---|---|---|---|---|---|---|
| states expanded | **x1.006** | 1.00 | 1.00 | 1.29 | 1.76 | 527 / 554 |
| states visited | **x1.001** | 1.00 | 1.00 | 1.05 | 1.65 | 482 / 554 |

**The worst case is NOT exponential in nesting depth.** Nested nullable stars,
`(?:(?:...(?:a*)*...)*)*`, measured at depths 20 to 60:

| nesting depth d | 20 | 30 | 40 | 60 | 97 | 220 |
|---|---|---|---|---|---|---|
| distinct contexts | 1,507 | 4,907 | 11,407 | 37,707 | 151,911 | 1,798,507 |
| states expanded | 3,454 | 10,764 | 24,474 | 79,094 | 313,154 | 3,645,654 |
| redirects | — | — | — | — | 6,966,548 | 193,628,274 |

Contexts fit **d³/6** closely (d=40: predicted 10,667, measured 11,407; d=60:
36,000 vs 37,707), and the redirect count — which is where the time goes —
fits **d⁴**: the measured ratios 3.16, 2.45, 2.08 across d = 49→65→81→97
against predicted 3.10, 2.41, 2.06. **MEASURED. The cost law is Θ(d⁴) in loop
nesting depth, and it is polynomial, not exponential.**

Wall-clock, against the shipped compiler:

| d | 16 | 32 | 48 | 64 | 96 | 100 | 200 | 250 (the cap) |
|---|---|---|---|---|---|---|---|---|
| shipped | 0.12 s | 0.12 s | 0.12 s | 0.12 s | 0.12 s | 0.12 s | 0.12 s | 0.12 s |
| prototype A | 0.12 s | 0.12 s | 0.22 s | 0.32 s | 1.41 s | 1.62 s | **20.5 s** | ~40 s (extrapolated) |

(0.12 s is this box's process-startup floor; everything at that figure is doing
no measurable closure work.) **The depth is bounded**: `src/parse/parse.c:549`
refuses at 250 nested parentheses, and loop nesting requires parentheses, so
d ≤ 250 — **STRUCTURAL** on the parser's cap, **MEASURED** at the boundary
(nest249 compiles, nest255 refuses). The 250-deep worst case is the
extrapolation in that table and is the one number here I did not run to
completion; the d⁴ fit is good enough that I would defend ~40 s, but it is
**BELIEVED**, not MEASURED.

#### The regression the fuzzer found, and the fast path that removes it

Prototype A was run through the repo's own differential fuzzer. At seed 99 it
did not diverge — it **timed out**, on

    (1{0,30}?[^]abc][^abc]){28,30}0+|a

which the shipped compiler processes in 0.61 s and prototype A in **13.33 s**.
This is not a contrived pattern; the general fuzzer produced it within 129
draws, which is the same standard of "reachable by accident" the K18 entry
applies to the bug itself.

The counters explain it, and they say something the wall clock does not.
**MEASURED**, on the `{8,8}` shrink of that pattern, shipped build vs
prototype A: closures 332,476 vs 332,476; states visited 15,743,238 vs
15,743,238; states expanded 11,714,704 vs 11,714,704; maxdepth 1; contexts 2.
**The two builds do exactly the same work.** The entire 7x was the per-probe
constant: prototype A had replaced one generation-stamped array access with a
hash probe, 15.7 million times.

So the design gets an **empty-context fast path** (prototype A2): when the open
stack is empty, (state, 0) and `state` are the same key, and the shipped
compiler's own per-state stamp array is an exact and much cheaper
representation of the memo. The hash is used only for contexts that actually
need distinguishing. **STRUCTURAL** that this changes no answers; **MEASURED**
that it does not: A and A2 emit **byte-identical C on all 18,858 shape-space
patterns and all 555 corpus patterns**.

| | shipped | A | **A2** |
|---|---|---|---|
| `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` | 0.61 s | 13.33 s | **0.82 s** |
| same, `{8,8}` | 0.21 s | 1.52 s | **0.22 s** |
| corpus aggregate compile time | 0.671 s | 0.662 s | (A2 ≡ A) |
| nest100 / nest200 | 0.12 s | 1.62 / 20.4 s | 1.62 / 20.5 s |

The fast path removes the constant-factor regression and leaves the Θ(d⁴)
deep-nesting cost untouched, which is correct — that cost is real work, not
overhead.

**A recommended cheap mitigation for the residual.** 353 of 555 corpus
patterns never open a loop at all and the corpus maximum is 5, while the
compile-time risk begins somewhere past depth 64. A depth threshold — full
path-sensitivity at nesting depth ≤ D, falling back to today's global memo
beyond it — bounds the worst case at whatever D buys while leaving every
realistic pattern exact. **MEASURED:** D=32 bounds it at 0.12 s, D=48 at
0.22 s, D=64 at 0.32 s. I recommend **D=64**, on the grounds that it is 12x the
deepest pattern in the corpus and holds the worst case to a third of a second.
The honest cost of the threshold is that beyond D the compiler is K18-buggy
again — but no worse than it is today, and the fallback is a documented,
testable boundary rather than a silent one. This is a RULING I am asking for,
not a decision I have taken: see §6.

### 2b. The cheap alternative: transparent epsilon states

**The design.** Keep the memo global and keyed on state alone, exactly as
today. Change only what an already-seen state does: an already-seen `N_EPS` is
walked THROUGH rather than killing the walk. Two lines
(`prototypes/proto_b.py`), no new data structure, no new state.

It is aimed directly at §1.3: the state that kills K18's walk is an `N_EPS`,
it has one out-edge and no priority of its own, and passing through it cannot
reorder anything.

**Termination.** A non-terminating walk needs infinitely many already-seen
hops, since a state is expanded at most once. The already-seen hops are the
loop redirect (outward, acyclic, per K17's argument) and this new
pass-through, which follows a single edge. A cycle built from those would be a
cycle in the epsilon graph that avoids every expansion — and **every cycle in
the epsilon graph runs through a `loop=1` SPLIT**, because `frag_star`
(src/ir/nfa.c:115-131) is the only construction in the file that creates a back
edge and its target is always such a split. **STRUCTURAL**, verified by
grepping every `.loop` assignment: there is exactly one, at nfa.c:122, and the
`A_REP` bounded-repeat path builds nested optionals with no back edge at all.

**It is cheap and it works — on the acceptance corpus.** **MEASURED:** 165/165,
full corpus 1704/1704, compile time indistinguishable from the shipped build on
every family measured, including the fuzz-found pattern (0.62 s vs the shipped
0.61 s) and nest200.

**And it is not exact, which is why it is rejected.** A and B were compared by
emitted source over the 18,858-pattern shape space: **18,775 byte-identical,
83 differing**. Every one of the 83 has a `{0,2}`-quantified body — the
conflation happening at a nested optional SPLIT rather than at an `N_EPS`,
which is precisely the case B's two lines cannot reach. Running those 83
against python3 `re`:

> **98 pattern/subject cells where A and B disagree. A agrees with the oracle
> on 98. B agrees on 0. Neither agrees on 0.** (`oracle_cmp.py`)

Examples, all `[0,1)` from the oracle, `[0,2)` from B:
`(?:(?:b*|a){0,2})*` on "ba", `(?:(?:a|b*?){0,2})*` on "ab",
`(?:(?:b?|a){0,2})*` on "ba".

So B passes the entire K18 acceptance corpus while leaving a live tier-1
miscompile class of the same shape and severity. **That is the most important
single result in this note**, and it is a direct instance of this project's
recurring lesson: the 165 cases were derived from K18's own witnesses, so they
share an alphabet with the bug as found rather than with the defect as it
exists. A candidate that passes them is not thereby correct. The rewrite lane
must not treat 165/165 as its acceptance criterion.

### 2c. The naive baseline: no memo at all

**The design.** Prototype A with the memo deleted (`prototypes/proto_c.py`).
Same empty-iteration rule, same open-loop stack (which is what breaks cycles,
so it still terminates), same output dedup — it simply never suppresses a
re-arrival. Its only job is to PRICE the memo: A and C give the same answers,
so the difference between them is the memo's contribution and nothing else.
Without it, "the memo is what makes the exact rule affordable" would be an
assertion.

**MEASURED**, on `(?:a*|b*){n}`, the family the K18 entry names:

| n | 14 | 16 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|
| shipped | 0.11 s | 0.11 s | 0.11 s | 0.11 s | 0.12 s | 0.11 s | 0.12 s |
| A | 0.11 s | 0.11 s | 0.11 s | 0.11 s | 0.11 s | 0.11 s | 0.11 s |
| C (no memo) | 0.11 s | 0.41 s | 1.51 s | 3.11 s | 6.31 s | 12.63 s | budget |

A clean doubling per unit of n — **Θ(2ⁿ)** — running out of a 3x10⁸-visit
budget at n=22. This CONFIRMS the K18 entry's own sketch ("the naive
path-local version was exponential on `(?:a*|b*){20}`-class shapes") as a
measurement rather than a recollection, and it settles the shape of the answer:
the expensive thing is dropping the dedup, not making the rule path-sensitive.
A is exponentially cheaper than C and, per §2a, within 0.6% of the shipped
compiler on real patterns.

### 2d. Recommendation

**Prototype A2 — (state, open-loop-context) memo with an empty-context fast
path — with a nesting-depth threshold at D=64 pending the ruling in §6.**

B is rejected on exactness (98-0 against the oracle), not on cost. C is
rejected on cost (2ⁿ), not on exactness. A2 is the only candidate that is both,
and its residual — Θ(d⁴) beyond nesting depth ~64, bounded at ~40 s by the
parser's own 250-paren cap — is addressable by a threshold whose worst case is
measured.

---

## 3. Termination

In the style the K17 fix's comment carries, for A/A2 as recommended.

**Claim.** Every `clo_visit` walk terminates.

**Setup, all STRUCTURAL.** (i) A (state, context) pair is EXPANDED — reaches
the switch — at most once per closure, because expansion is guarded by an
insert into the memo that fails on the second attempt. (ii) The set of
contexts is finite: a context is an open-loop stack, the stack contains no
repeats (a re-arrival at an open loop redirects instead of pushing), and there
are finitely many loop states. (iii) `frag_star` at src/ir/nfa.c:115-131 is the
only construction that creates a back edge, and its target always carries
`loop=1`, so every cycle in the epsilon graph passes through a loop-entry
split.

**Argument.** Suppose a walk does not terminate. By (i) and (ii) it performs
finitely many expansions, so it must perform infinitely many NON-expanding
hops. There are exactly two:

* a **memo hit**, which returns immediately and cannot continue a walk;
* a **redirect**, which follows a loop's exit edge.

So an infinite walk is an infinite suffix of redirects. Each redirect
truncates the open stack to strictly below the redirected loop's position —
`cl->depth = at` where `at` is that loop's index — so the open stack's depth
strictly decreases at every redirect. Depth is a non-negative integer. There
can be at most `depth` consecutive redirects, and depth is bounded by the loop
nesting depth. Contradiction.

**This is stronger than K17's argument and subsumes it.** K17's comment argues
that the redirect graph is acyclic because loop exits point outward past the
loop — a statement about the NFA's shape that has to be re-checked whenever a
construction is added. The version above is a decreasing measure on the walk's
own state, so it holds regardless of what the NFA looks like, and in
particular it would survive a future construct that made loop exits point
somewhere surprising. **BELIEVED** that this is strictly stronger; the
decreasing-measure part is STRUCTURAL from the prototype's code.

**What could still break it.** If a future change let the redirect truncate to
a depth that is not strictly less than the current one — for instance, a
redirect that popped nothing when the loop was already the top — the measure
would stop decreasing. The rewrite should carry the "open loop is the stack
top" assertion (§2a) and an explicit `at < cl->depth` assertion, because the
termination proof is exactly what those two guard.

---

## 4. Blast radius, predicted

### 4.1 The 165 acceptance cases

**Prediction: all 165 pass; 26 change from fail to pass, 139 are untouched.**
**MEASURED** on both A and A2: 165/165, from a baseline of 139 passing.

Stronger than the pass count, and the form the rewrite lane should report:
of the 15 patterns in that file, **exactly 8 change their emitted C, and they
are exactly the 8 diverging shapes. All 7 over-reach controls emit
byte-identical C** — not merely "still pass", which a subject sample could
have reported without noticing a changed automaton.

### 4.2 The existing corpus: predicted ZERO changed cells, and why

**Prediction: zero.** Not from an argument — from the emitted source.
Compiling all 622 harvested corpus patterns with the shipped compiler and with
A (`emitdiff.py`): **555 accepted by both, 547 byte-identical, 8 differing, 0
accepted by only one.** The 8 are:

    (?:(?:a|b*?)?)*     ((?:a|b*?)?)*      (?:(?:a+|b*?)?)*   (?:(?:a|b??)?)*
    (?:(?:a?|b*?)?)*    (?:(?:a|b*?)?)+    (?:(?:[a]|[b]*?)?)*  ^(?:(?:a|b*?)?)*

which are the K18 known-fail shapes and nothing else. **So the fix's reach on
the corpus is precisely the shape it is aimed at, with no collateral at all**,
and the predicted change to live corpus cells is zero because no live corpus
pattern's emitted bytes move. **MEASURED.** Corroborated independently: the
full `.rxt` suite is **1704/1704 under A, 1704/1704 under A2, and 1704/1704
under the shipped compiler** — the same number three ways, which is what "zero
changed cells" has to look like.

### 4.3 Direction, where things do change

Every cell where the shipped compiler and A differ, over the dense shape space
(`oracle_cmp.py` on the 249 patterns whose emitted C differs):

> **226 differing pattern/subject cells. A agrees with the oracle on 226. The
> shipped compiler agrees on 0. Both wrong on 0.** Unanimously old-wrong →
> new-right, which is the direction K17's own isolation sweep reported and the
> only direction that is acceptable.

Note the denominator honestly: the shape space is a DENSE sample of the defect
class, deliberately so. 249 of 18,858 differing is **not** a "1 in 76 patterns"
figure for real inputs; §4.2's 8 of 555 is the realistic figure.

### 4.4 The differential fuzzer, and a finding that is not mine

Two seeds, 400 patterns x 16 subjects each, shipped compiler vs A2:

| | seed 99 | seed 5 |
|---|---|---|
| content divergences, shipped | 347 | 442 |
| content divergences, A2 | 343 | 446 |
| distinct diverging patterns, shipped | 8 | 8 |
| distinct diverging patterns, A2 | 8 | 8 |
| **patterns diverging under A2 but not the shipped compiler** | **0** | **0** |
| patterns diverging under the shipped compiler but not A2 | 0 | 0 |

The diverging-pattern SETS are identical, element for element, on both seeds.
The cell counts wobble by ~4 in ~2,000 because some cells are runaway matchers
whose outcome is `TIMEOUT` on one execution and `CRASH` on another:
CRASH+TIMEOUT totals are **39 vs 39** at seed 99 and **40 vs 40** at seed 5.
**MEASURED. A2 introduces no divergence and removes none.**

**Reporting the part that is not about K18:** the differential fuzzer is
already RED on the current tree. The shipped compiler produces 347 and 442
content divergences on these seeds, across 8 patterns each, and 23 and 12 of
those cells are generated matchers ABORTING with `*** stack smashing detected
***`. Every one of the 8 patterns per seed carries a `{28,30}`-class bounded
repeat over a capture-bearing body — the [M4.5] VM path, not the DFA closure.
This is not K18, it is not caused by anything in this note, and it is outside
this lane's brief; it is recorded here because the lane ran into it and M4.5
closed green, so someone should decide whether it is K19/K20 fallout, a
known-and-excluded fuzz category, or a new K-entry. **The measurement is
MEASURED; the attribution to the VM path is BELIEVED**, from the shape of the
patterns, since I did not open a repro bundle.

### 4.5 `make test`

**MEASURED**, full `make test` in a scratch tree with A applied: every leg
passes except the known-fail ratchet, which fails with EXIT=2 and the message
`NOW PASSING: tests/known_fail/k18_empty_exit_through_seen_eps.rxt`. That is
the ratchet working as designed. The rewrite lane's landing must move that file
into a live corpus directory and close the K18 entry in the same commit, or
`make test` stays red.

### 4.6 What I did NOT measure, and where the risk sits

* **Captures.** Every measurement here is spans-only. K18's entry marks the
  defect capture-independent, and the corpus run includes the capture suites,
  but I did not do a capture-offset differential of my own. **The rewrite lane
  must**, because M4.5's VM consumes the DFA's span.
* **The reverse machine (D7) in isolation.** It is exercised throughout (the
  counters aggregate both machines) but never singled out. `prune` is off
  there, so the closure keeps every thread alive — a different code path
  through the same walk.
* **The 250-deep worst case**, run to completion (§2a).
* **libpcre2 as a second oracle** on the A-vs-B and base-vs-A cells. python3
  `re` alone was used. The K17/K18 entries record zero disagreements between
  the two oracles across this whole space, so I judged one oracle sufficient
  for a design screen — but D44's three-way rule means the rewrite lane owes
  the second oracle.

---

## 5. Validation plan for the rewrite lane

The K17 methodology, with the additions this lane's own findings demand.

1. **Oracle-verified family tests.** A live `.rxt` guard corpus: the 8
   diverging shapes, the 7 controls, **plus the `{0,2}`-bodied family from
   §2b** — the 83 patterns where B and A disagree are a ready-made,
   independently-derived extension of the class, and they are not in the
   current 165. Every expectation from python3 `re` AND libpcre2, both oracles
   agreeing, per D44.
2. **Isolation sweep with changed-cell accounting**, old-binary vs new-binary,
   reporting old-wrong→new-right / regressed / both-wrong. §4.3's 226-0-0 is
   the shape; the lane should reproduce it at a larger scale with injected
   positive controls, and must state the injection count separately so the
   total is not inflated by controls the way K17's 294 was.
3. **Emitted-source blast radius**, shipped vs new, over both the realistic
   corpus and a generated sweep. §4.2's "547 identical, 8 differing, all 8 the
   target shapes" is the result to reproduce and beat.
4. **Sabotage-validated traps.** The fuzz trap templates K17 landed cover
   K17's shape. The lane owes rows for K18's — including a `{0,2}`-bodied row,
   since §2b proves that sub-shape is separately reachable — exhaustively
   expanded and measured against the PRE-fix compiler to show a nonzero
   divergence count, then against the post-fix compiler to show zero.
5. **A non-vacuous control for every check.** K17's lane discarded a "0
   changed over 36,000 cells" isolation sweep whose generator could not produce
   a K17 shape at all. Concretely, for this lane: any sweep must report how
   many of its generated patterns have loop nesting depth ≥ 2 and at least one
   lazy nullable quantifier, and a sweep reporting zero of those is a control
   that could not have failed. **My own §4.2 corpus sweep passes this test
   only because the corpus already contains K17's and K18's guard patterns —
   a generated sweep would not, and the lane should not reuse my generator
   without checking it.**
6. **Cost regression gates**, which K17's methodology did not need and this one
   does:
   * the counter-instrumented base build (`proto_basestats.py`) kept, so
     inflation is reported with a denominator;
   * the `nonstacktop` counter kept as an assertion;
   * timing on the fuzz-found `(1{0,30}?[^]abc][^abc]){28,30}0+|a` and on
     nested-star depths 16/64/100/200 as explicit gates — that pattern is the
     one that caught the constant-factor regression and it should not be
     allowed to regress silently;
   * at least two fuzzer seeds run to completion, since seed 99 found the cost
     defect that no corpus run did.
7. **`make ubsan` and `make asan`, both axes.** The design adds two heap
   tables with growth and rehash paths — the first version of the prototype
   had a table that deadlocked when full (§7) — and neither the corpus nor the
   fuzzer exercises the grow path deliberately. A test that drives a closure
   past the initial capacity should be written on purpose.

---

## 6. Rulings requested

1. **The nesting-depth threshold.** Take D=64 (worst case ~0.32 s, exact for
   everything within 12x of the corpus maximum), take a different D, or take
   none and accept ~40 s at the parser's 250-paren cap. I recommend D=64. If a
   threshold is taken, it needs a decisions.md entry, because it makes the
   compiler deliberately inexact in a bounded region and that must not become
   folklore.
2. **Whether §2a's "(1) and (2) are each necessary" claim needs measuring**
   before the rewrite. It is cheap (two half-prototypes) and it is currently
   BELIEVED.
3. **Whether the 83 `{0,2}` patterns from §2b become a live guard corpus in
   this lane or the rewrite lane.** They are oracle-verified against python3
   `re` today but not yet against libpcre2.

---

## 7. A note on this lane's own instrumentation

Two prototype defects were found and fixed during the measurements, and both
are recorded because both produced numbers that would have gone into this note
as findings.

**A fixed-capacity memo does not slow down when it fills — it hangs.** The
first prototype's open-addressed table never grew. Every slot carried the
current generation and none matched the key, so the probe loop never found a
free slot. It presented as `(?:...(?:a*)*...)*` at 17 nesting levels running
forever while 16 finished in 0.12 s — a cliff so sharp that I nearly wrote it
up as an algorithmic explosion. It was a full hash table. After adding growth,
depth 40 compiles in 0.12 s.

**A linear-scan interner prices the prototype, not the design.** Context
interning was a linear scan over all contexts. At the depths where contexts run
to six figures that scan, not the memo, would have been the measured cost.
Replaced with a hash before any cost number in this note was taken.

Both are instances of the lesson `pcrec-check-design-lessons` records in a
different form: an instrument that shares a failure mode with the thing it
measures reports the instrument. The general defence used here was to keep the
UNMODIFIED closure instrumented with the identical counters and to check that
the instrumented build emits byte-identical C — which is what turned the
13.33 s fuzz timeout from "the design is too slow" into "the design does
identical work and my probe is slow", and produced the fast path in §2a.
