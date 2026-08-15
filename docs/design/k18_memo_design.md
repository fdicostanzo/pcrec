# K18 — a path-sensitive epsilon-closure memo

**STATUS: AMENDED PER R23 (2026-08-15)** —
`docs/dev/reviews/2026-08-15-r23-k18-memo.md`, raw evidence in
`2026-08-15-r23-appendix-critic-findings.md`. The panel affirmed the DESIGN
(A2) and refuted the note's PROTOTYPE: `clo_visit` restored the open-loop
stack's depth but not its ENTRIES, and that one omission was simultaneously
the refutation of §2a's `nonstacktop == 0` cell and the ENTIRE cost residual
§6 asked a ruling about. The prototype is fixed and every cost number below
has been re-taken on the fixed prototype. **§6 ruling 1 is WITHDRAWN**; no
Frank rulings remain open from this note. What else changed: §1's ingredient
re-characterised (the PREFERRED arm, not laziness), §3's comparative claim
withdrawn, §4.4 back-annotated RESOLVED, `gen_adversarial.py`'s two invalid
families fixed and re-run, and §5 grown by nine items. Sections carry
**[R23]** markers where the panel's finding is what changed them.

**One NEW defect came out of the re-measurement itself, and it refutes a
STRUCTURAL claim this note made that R23 did not catch either.** §2a said "the
tail recursion does not deepen"; that is true of the number of recursion SITES
and false of the DEPTH. **MEASURED: `clo_visit` recurses Θ(d²) — 31,377 frames
at the parser's 250-paren cap, against the shipped closure's 253.** The
consequence is that the design needs ~7 MB of the default 8 MB stack at that
cap on the PLAIN build (shipped: 192 KB, 42x headroom), and overflows outright
under AddressSanitizer at depth **210**. It is not the stack fix — the unfixed
prototype measures identical recursion depths — and the suite would not catch
it, since corpus loop-nesting depth tops out at 4. §2a measures it, §5 item 12
turns it into a decision the rewrite lane owes. Also withdrawn as unmeasurable: the corpus-aggregate wall-clock figure,
whose signal sits under process-spawn noise — the counters answer that
question and the note now says so.

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

**Read the trace for the mechanism, not for the `?` in `b*?`.** What matters
above is that the arm whose exit edge lands on the already-seen state is the
one the walk PREFERS. Laziness is one way to arrange that and it is not the
only one — see §1.5, which the panel had to find because this section did not
say so.

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
to reach. **MEASURED [R23 S5]**, and it was cheap: the note left this BELIEVED
and asked for a ruling on whether to measure it (§6 ruling 2), and the panel
simply built both halves. Change (2) alone (`proto_half2.py`, the open-loop
stack and the open-path redirect trigger, memo context forced to 0)
reproduces the shipped compiler's wrong answers **cell for cell** — 8 cells on
2 patterns, the same 8 the shipped compiler gets wrong, against A2's 0.
Change (1) alone (`proto_half1.py`, context-keyed memo with the shipped
redirect trigger) does not merely fail — **it does not terminate**, SIGABRT on
the 15-character `(?:(?:a|b*?)?)*` and SIGSEGV even with the open-loop stack
sized 20,000x. That second result is stronger than the claim it was built to
check, and §3 now carries it: the open-set test is what BOUNDS THE STACK.

### 1.5 A fourth sub-case: the ingredient is the PREFERRED arm, not laziness [R23 S8]

Everything above characterises the defect with a lazy quantifier in it, and
that characterisation is too narrow. **What the defect needs is that the arm
whose EXIT edge lands on the already-seen epsilon state is the PREFERRED
one.** A lazy quantifier achieves that by preferring its exit. A GREEDY
nullable arm achieves exactly the same thing by being written FIRST in the
alternation. So does an empty arm, and so does a concatenation of two nullable
alternations — none of which contains a lazy quantifier at all.

Four witnesses, oracle-confirmed by python3 `re` and libpcre2 with zero
disagreements between them, all fixed by A2:

| pattern | subject | shipped | A2 and both oracles | what it refutes |
|---|---|---|---|---|
| `(?:(?:b*\|a)?)*` | `ba` | [0,2) | [0,1) | the "greedy inner" control, arms swapped |
| `(?:(?:b?\|a)?)*` | `ba` | [0,2) | [0,1) | its sibling, same way |
| `(?:(?:(?:b\|)\|a)?)*` | `ba` | [0,2) | [0,1) | "an empty alternative instead of a lazy quantifier" |
| `(?:(?:b?\|a)(?:b?\|d))*` | `ba` | [0,2) | [0,1) | "concatenation, not alternation" |

**MEASURED**, re-run by this lane rather than copied: over those four plus the
five controls the K18 entry lists as non-diverging plus the original witness,
15 subjects each, **the shipped compiler disagrees with the oracle on 19 cells
across 5 patterns and A2 on 0**. The five controls, with their arms in the
order the entry writes them, do not diverge — which is the point: the entry's
parenthesised CAUSES are wrong even though its rows are right. Every one of
those entries is corrected in `docs/dev/known_issues.md` in the same change as
this note.

**Why this matters even though A2 fixes all three.** The dense shape sweep
does generate the swapped order (`gen_shapes.py` emits `"%s|%s"` both ways),
so §4.3's 226/226 already covers the sub-case and A2 has no hole here. The
damage is to the PROSE and to the acceptance corpus, and it has already been
done once: all 15 patterns in
`tests/known_fail/k18_empty_exit_through_seen_eps.rxt` carry the lazy shape,
its only two non-lazy entries are there as CONTROLS, and none of the three
witnesses above is in the file. §4.1's headline — "all 7 over-reach controls
emit byte-identical C" — therefore proves less than it reads: at least one of
those controls is non-diverging for an ARM-ORDER reason rather than a
structural one, and its mirror image is a live miscompile. **A control that is
one character away from a witness is not an over-reach control**, and §5 item
1 now specifies the arm-order axis that would have caught it.

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

**Which of "set" and "stack" is the invariant. [R23 S13.]** This section's
heading says the memo is keyed on (state, open-loop-SET) and the prototype
interns an ordered CHAIN — `lctx_intern(ctxs, parent_ctx, loop)`, so two paths
holding the same loops in a different ORDER get different context ids. They
are not the same thing and the note owes a statement of which is which:

* **The SET is the invariant.** Correctness asks one question — "is this loop
  entry open on the path that reached it?" — and that is set membership. Every
  claim in §1 and §3 is a claim about the set.
* **The ordered chain is the implementation**, chosen because the redirect must
  truncate the stack to the re-arrived loop's POSITION (which needs an order)
  and because interning a chain is one hash probe per push where interning a
  set is not.
* **They coincide exactly while loop nesting is proper**, which it is today.
  If a future construct ever broke proper nesting, the chain would
  over-distinguish contexts (a cost bug: more contexts than the set needs) and
  the truncate-to-index would land in the wrong place (a correctness bug). The
  `nonstacktop` counter below is the standing check on the coincidence, and it
  is the only thing that would notice.

**The stack invariant, stated explicitly, and measured on the fixed
prototype.** *Every redirect must find the re-arrived loop at the TOP of the
open-loop stack* — `at == depth - 1` at every redirect. The prototype counts
violations rather than assuming none.

| corpus | patterns | `nonstacktop > 0` on |
|---|---|---|
| 8 corpora: the note's 622 + 70 adversarial + 6 independently-generated families | 2,475 | **0** |
| random-grammar corpus, seed 20260815 | 4,000 | **0** |
| **the same 2,475 against the UNFIXED prototype (non-vacuity control)** | 2,475 | **30** |
| the note's OWN corpora only, against the UNFIXED prototype | 691 | **0** |

**MEASURED: 0 over 6,475 patterns**, at open depths to 251 and 93 million
redirects, with 0 compile timeouts at 180 s. The rewrite should keep that
counter as an assertion — **and this note previously told it to do so on
evidence that could not have failed.**

That last row is the finding. The original cell read "MEASURED: 0, over 555
corpus patterns and 52 adversarial patterns", and the panel reproduced that 0
exactly — then fired the same counter 358 times over 4,369 patterns of its own
(S10), because this lane's generator tops out at two loop levels and the
failure needs three under a `{0,2}`. A rewrite following §2a and §5 literally
would have shipped an assertion that aborts the compiler on a 28-character
regex. The reason it fires is the stack-entry bug above (S3): a clobbered
entry makes the scan find its loop at the wrong index, or miss it entirely.
With the entries restored the invariant is sound and the cell is true as
written — but it is true now because the prototype was fixed, not because the
original measurement was right. **A cell measured on a corpus that cannot
reach the failure is not a measurement of the design; it is a measurement of
the corpus.**

Two further disclosures the original numbers owed:

* **The "52 adversarial patterns" were 52 of 70. [R23 M-B1.]** The `altnest`
  and `k18nest` families — the two named after K18's own shape, the ones most
  on-point for "does the open-loop invariant survive K18-shaped nesting" —
  appended the outer `*` to a body already ending in `?`, so all 18 of their
  patterns were `?*` and every engine rejected them. They contributed ZERO
  patterns to this cell and to every other adversarial figure in the note.
  Nothing disclosed it: `k18_stats.py` printed `refused=18` on stderr exactly
  to prevent this, and the number never reached the prose. The generator is
  fixed, all **70 of 70** now compile (`refused=0`), and the table above is
  measured on all of them.
* **`nonstacktop` is necessarily self-instrumented** — the counter lives
  inside the prototype whose invariant it checks, because there is no external
  oracle for "was the open loop ever not the stack top". The panel flagged
  that as the one place independence is structurally impossible (M-O2), and
  S10 then demonstrated exactly the risk the flag named. The mitigation is not
  independence, which is unavailable, but the non-vacuity control in the table
  above: a corpus on which the counter is known to FIRE, run against the
  binary that is supposed to make it stop.

**And the assertion is not sufficient on its own.** `nonstacktop` measured 0
on the corrupted stack for a mechanical reason (S9, recorded in §3): the slot
the clobber overwrites is the slot of the loop whose redirect is then missed,
so the scan still finds its match at the top. §3's termination proof rests on
a DIFFERENT invariant — the stack holds no repeats — and §5 item 6 therefore
requires both assertions.

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

**But it DOES deepen, and this note did not notice. [Found by the R23
revision lane's own re-measurement; the panel did not catch it either.]** The
sentence above is true about the number of recursion SITES and was silently
read as a claim about recursion DEPTH. Those are different, and the depth
changes asymptotically. **MEASURED**, a counter around `clo_visit`'s entry and
exit, nested nullable stars:

| nesting depth d | 50 | 100 | 200 | 250 (the cap) |
|---|---|---|---|---|
| shipped, max recursion depth | 53 | 103 | 203 | **253** |
| A2, max recursion depth | 1,277 | 5,052 | 20,102 | **31,377** |

The shipped closure recurses **d+3** deep — linear, which is what `limits.h`
was protecting when it made the tail edges iterative. A2 recurses **≈ d²/2**,
because the same state is descended into once per CONTEXT rather than once,
and the context count is itself ≈ d²/2 (31,627 at d=250, the same curve). The
recursion site did not multiply; the recursion depth acquired a power of d.

**What that costs, on the PLAIN build, at the parser's own cap.** Minimum
stack at which nest250 still compiles, bisected with `ulimit -s`:

| | shipped | A2 |
|---|---|---|
| minimum stack for nest250 | **192 KB** | **7,168 KB** |
| headroom against the default 8 MB | 42x | **1.15x** |

A2 segfaults at `ulimit -s 4096`. It is not frame bloat — A2 averages ~228
bytes per frame against the shipped closure's ~780; there are simply 124x more
frames. And it is **not the stack-entry fix**: the unfixed prototype measures
an identical 1,277 / 5,052 / 20,102, so this belongs to prototype A's design,
not to the repair of it.

This is the one place where the design as prototyped is close to a hard edge,
and the note reached its recommendation without measuring it. §5 item 12 now
carries it, and the honest framing for the rewrite lane is that a Θ(d²) C
recursion on a fixed 8 MB stack is a design question — shrink the recursion,
bound the depth explicitly, or size the stack deliberately — not a tuning
detail.

**A frame must restore the stack's ENTRIES, not only its depth — and the
sentence above is where this note got that wrong. [R23 S3/S16.]** "A frame
restores the saved depth on return" is true and was not enough. A redirect
sets the depth to the re-arrived loop's index `at`, and `at` can be BELOW the
current frame's saved depth, because the re-arrived loop was pushed by an
ANCESTOR frame — which is reachable, and is precisely the K18 shape: the only
epsilon exit from a loop body runs through the loop's own entry split, so a
walk inside loop L can redirect at L and then immediately redirect at an
enclosing loop O. The continuation then PUSHES over `open[at .. save_depth)`.
Restoring only the depth hands the caller a stack whose entries name the wrong
loops, and the caller's redirect scan reads them.

The consequence is a MISSED empty-iteration redirect — verbatim the defect
this note exists to repair, reintroduced by the repair. It was measured
reaching the redirect decision on 552 of 1,001 patterns, overwhelmingly on the
reverse machine, and every divergence was a miss rather than a spurious fire.
It changed no answers (0 emitted-C differ against a variant that restores the
entries, on 1,001 + 1,728 patterns), which is why nothing in this lane's own
apparatus caught it — but it did three other things, and §2a's cost numbers,
§2a's `nonstacktop == 0` cell and §6's ruling request were all downstream of
it. The prototype now saves and restores the entries (`proto_a.py`'s
`clo_visit`, a deliberately naive `malloc`+`memcpy` per frame so that no
number below can be accused of hiding the fix's own cost), and every cost
figure in this section has been re-taken on it.

#### Cost: what the open-loop set actually costs

The open set's cardinality is the loop-NESTING depth. **MEASURED** on the
FIXED prototype, over the 555 compiling corpus patterns (`summarise.py`):

| max open-set size | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| patterns | 353 | 176 | 17 | 8 | 1 |

So the brief's question — "is real nesting depth ever >3?" — answers **once in
555**, on `(?:b*?(?:(?:a*)*)*)*`, which is one of K17's own guard-test patterns
rather than anything a user wrote. Distinct contexts per pattern: 353 patterns
need exactly 1 (the empty one), and the maximum over the whole corpus is
**13**. (The unfixed prototype reported one pattern at depth 5 and a corpus
maximum of 19 contexts; the extra depth and the extra contexts were the
corruption, on the corpus as much as on the deep-nesting families.)

The memo's inflation over the shipped walk, same patterns, same counters
(`inflation.py`, 554 patterns compared, 0 dropped as one-sided):

| | aggregate | p50 | p90 | p99 | max | unchanged |
|---|---|---|---|---|---|---|
| states expanded | **x1.004** | 1.00 | 1.00 | 1.29 | 1.40 | 527 / 554 |
| states visited | **x0.996** | 1.00 | 1.00 | 1.05 | 1.22 | 482 / 554 |

Visits now come in slightly UNDER the shipped compiler in aggregate (127,197
against 127,766), which is not a rounding artifact and is worth one sentence:
the path-sensitive redirect ENDS walks the global memo lets continue, so on the
patterns where the two differ the exact rule sometimes does strictly less work.
The worst per-pattern case is 1.40x expansions on `(?:b*?(?:(?:a*)*)*)*`. This
is the figure quoted as the reason the design is affordable, so it is the one
the panel asked to see re-taken; it improved.

#### The deep-nesting worst case, re-measured [R23 S16, M-m1]

Nested nullable stars, `(?:(?:...(?:a*)*...)*)*`, at the depths that matter,
with the parser's own cap as the last column. Times are min-of-3 wall clock
from a python harness whose per-invocation floor is **0.92 ms** on this box,
measured against the pattern `a` at every run — not the 0.12 s this note
originally printed, which was its shell harness's own overhead and made every
cheap compile look identical. (M-m1 also found the old table's d=97 row off
3–6% on all three counters against bit-exact neighbours; the re-measurement
below replaces it rather than patching it.)

| nesting depth d | 16 | 32 | 48 | 64 | 96 | 100 | 200 | 250 (the cap) |
|---|---|---|---|---|---|---|---|---|
| shipped | 0.0009 s | 0.0010 | 0.0011 | 0.0013 | 0.0027 | 0.0027 | 0.0018 | **0.0044 s** |
| A2, stack UNFIXED | 0.0026 s | 0.0321 | 0.1136 | 0.2800 | 1.3367 | 1.5947 | 20.4461 | **37.02 s** |
| **A2, as designed** | **0.0011 s** | 0.0026 | 0.0081 | 0.0175 | 0.0512 | 0.0450 | 0.2221 | **0.3501 s** |

The middle row is the prototype this note originally measured, and it
reproduces the old table (37.0 s against the old 39.25 s, box noise). The
bottom row is the same binary with the stack entries restored. **The worst
case a user can reach through the parser is 0.35 s**, not 39 s.

The counters say why, and they are more informative than the clock
(`PCREC_K18_STATS=1`, dominant machine):

| d | 16 | 32 | 48 | 64 | 96 | 100 | 200 | 250 |
|---|---|---|---|---|---|---|---|---|
| contexts | 154 | 562 | 1,226 | 2,146 | 4,754 | 5,152 | 20,302 | 31,627 |
| states expanded | 418 | 1,330 | 2,754 | 4,690 | 10,098 | 10,918 | 41,818 | 64,768 |
| redirects | 2,176 | 14,080 | 43,904 | 99,840 | 322,816 | 363,600 | 2,787,200 | 5,396,500 |
| nonstacktop | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Against the unfixed prototype at the same depths — same pattern, same binary,
one changed function:

| d | 64 | 100 | 200 |
|---|---|---|---|
| contexts, unfixed / fixed | 45,639 / 2,146 | 171,507 / 5,152 | 1,353,007 / 20,302 |
| redirects, unfixed / fixed | 1,370,468 / 99,840 | 8,205,854 / 363,600 | 132,156,704 / 2,787,200 |
| visits, unfixed / fixed | — | — | 137,570,342 / 2,870,018 |

**67x fewer contexts and 48x fewer visits at d=200, for byte-identical
emitted C.** The mechanism is compounding: a missed redirect does not merely
lose a rule, it makes the walk EXPAND a loop it should have exited, which
pushes that loop, which mints a fresh context, which defeats the memo for the
entire subtree below it. The context explosion IS the missed redirects
accumulating.

**The "cost law" was a law about the bug.** On the fixed prototype the same
family fits contexts ≈ **d²/2** (d=250: 31,250 predicted against 31,627
measured; d=200: 20,000 against 20,302) and redirects ≈ **d³/3** (5,208,333
against 5,396,500; 2,666,667 against 2,787,200). The unfixed prototype fitted
d³/6 and Θ(d⁴) — the numbers this note published — so **the stack fix removes
one whole factor of d from both counters.** Marked as what it is: a FIT TO ONE
FAMILY, on a generator of pure nesting with no bounded repeats, not a law of
the design. The next subsection is a different family that this fit does not
predict at all.

**The depth is bounded**: `src/parse/parse.c:549` refuses when parentheses
nest too deeply, and a loop can only nest inside another loop through a group,
so d is capped by that refusal — **STRUCTURAL** that loop nesting requires
parentheses (`frag_star` is reached only through a quantified group),
**MEASURED** at the boundary: 250 nested `(?:...)*` wrappers compile, 251 are
refused (`PCREC_MAX_GROUP_DEPTH = 250`, `src/core/limits.h:125`). That makes
nest250 the true worst case a user can reach on this family, and it is
measured, not extrapolated — see the table's last column.

**A NEW limit, found by measuring the sanitizer axis this note had never
measured. [R23 V1 asked for this; it did not find what it expected.]** Under
AddressSanitizer the prototype's `clo_visit` **overflows the 8 MB stack at
nesting depth 210**, where the shipped compiler compiles the same pattern
fine to 250:

| nesting depth | 200 | 210 | 220 | 230 | 240 | 250 |
|---|---|---|---|---|---|---|
| shipped, asan | ok | ok | ok | ok | ok | ok |
| **A2, asan** | ok | **stack-overflow** | overflow | overflow | overflow | overflow |
| shipped / A2, ubsan | ok | ok | ok | ok | ok | ok |

**The cause is recursion DEPTH, not frame size, and not the fix** — it is the
Θ(d²) recursion measured under "The tail recursion does not deepen" above.
A2 recurses ≈ d²/2 frames deep where the shipped closure recurses d+3, so at
the parser's cap it already needs ~7 MB of the default 8 MB stack on the PLAIN
build; ASan's redzones then push the same walk over at depth 210. A2's frames
are in fact SMALLER than the shipped closure's (~228 bytes against ~780) —
there are just 124x more of them. The unfixed prototype overflows at the
identical depth and measures identical recursion depths, so the stack-entry
repair is not implicated.

Three things follow, and none of them is "ignore it". `make asan` is in the
merge/close battery, so this is a real failure mode for the rewrite — and the
plain build is at 1.15x headroom, so it is not an asan-only story either. The
suite would NOT currently catch it: corpus loop-nesting depth
is 4, so no test goes near 210. And the honest cost figure for the sanitizer
axis is not a timeout at all — timing was what V1 predicted would be tight,
and timing is fine (A2 at nest250 is 0.85 s under ubsan against 0.36 s plain,
and asan is faster still where it survives). §5 item 12 carries the
obligation.

#### The family the depth model does not predict [R23 S14]

A depth fit is the wrong instrument, and the panel found the family that shows
it: bounded repeats crossed with a nullable loop. `A_REP` lowers `{0,k}` into
nested COPIES of the body (`src/ir/nfa.c`), so the machine's NFA grows with k
while the nesting a reader counts in the pattern does not move at all — 405
NFA states at k=2, 1,485 at k=8, from a pattern whose visible nesting is
constant.

    ((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,k}(){2,3}){1,2}){2,3}

| k | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| shipped | 0.0022 s | 0.0062 | 0.0040 | 0.0039 | 0.0043 | 0.0054 | 0.0123 |
| A2, stack UNFIXED | 0.2192 s | 2.2503 | 17.1465 | 50.6882 | — | — | — |
| **A2, as designed** | **0.0029 s** | 0.0039 | 0.0049 | 0.0064 | 0.0072 | 0.0078 | **0.0087 s** |
| contexts (fixed) | 13 | 19 | 25 | 31 | 37 | 43 | 49 |
| max open depth (fixed) | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

**On the fixed prototype this family is LINEAR in k, at open-loop depth 1.**
On the unfixed prototype it was 231x over k=2..5 and did not finish beyond
that, with contexts 450 → 2,834 → 11,770 → 40,422 and **max depth pinned at
11**. (The k=3 and k=4 counters were re-measured here and reproduce S14's
bit for bit — 2,834 and 11,770 contexts, 274,312 and 1,056,992 redirects,
83,904 and 272,576 nonstacktop; k=2 and k=5 are S14's own.)

That last number deserves care, because the panel drew a conclusion from it
that this re-measurement narrows. S14 read depth-11-at-visible-nesting-3 as
`A_REP`'s copies MULTIPLYING the depth the open-loop machinery sees, and
called the mechanism prototype-independent. It is not: with the entries
restored the same patterns measure **max depth 1**, because the copies sit in
SEQUENCE rather than one inside another — a walk is inside at most one of them
at a time. The depth of 11 was the corrupted stack failing to pop loops whose
redirects were missed. (`docs/dev/plan.md`'s ENG-BREP third amendment is
corrected accordingly; its other two consequences stand.)

**What survives, and it is the part that matters for §5:** the cost driver is
the number of distinct open-loop CONTEXTS, not the nesting depth a reader
counts — contexts are what the memo keys on and what the interner holds, and
they grow with the unrolled copy count. Any budget or gate posed on
"nesting depth" is posed on a quantity the compiler does not use. §5 item 6
gains this family as a gate row for exactly that reason.

**The four patterns that did not finish.** Over 3,993 randomly generated
patterns with no knowledge of K18, four exceeded a 60 s compile budget under
the unfixed prototype and none under the shipped compiler (one was still
running at 900 s). On the fixed prototype:

| | shipped | A2 unfixed | **A2 as designed** |
|---|---|---|---|
| `((?:(?:(?:[^a]{1,2}\|[^a]??\|.{0,2}?)+){0,3}((?:[^a]*?\|){1,2}?){2,3}...` | 0.0038 s | >900 s | **0.0103 s** |
| `(?:(?:(?:.{0,3}\|[^a]?)+(?:b?){0,2}(.*?))*[a-c]{2,3}...` | refused | >60 s | **refused** |
| `(?:(?:.{0,3}d+a*?){0,3}(?:a{0,4}?\|\|d{2,3})+(?:.*?.*.??){0,4}?){0,4}?` | 0.3872 s | >60 s | **1.2199 s** |
| `(?:[^a]{0,3}\|c{0,3}\|(?:(?:(?:a??c??)*?(.{1,2})*)*\|...){0,4}?\|d{1,2}){2,3}` | 0.7879 s | >60 s | **2.8504 s** |

The second is refused by the existing DFA state cap (>32,000 states) under the
shipped compiler and A2 alike — a clean, attributable error, which is what D22
says that case should get. **The worst residual on this set is 3.6x the
shipped compiler on a pattern the shipped compiler already spends 0.79 s on.**
That is an ordinary optimisation-pass cost. It is not a reason to make the
compiler deliberately inexact, which is why §6 ruling 1 is withdrawn rather
than answered.

#### The regression the fuzzer found, and the fast path that removes it

Prototype A was run through the repo's own differential fuzzer. At seed 99 it
did not diverge — it **timed out**, on

    (1{0,30}?[^]abc][^abc]){28,30}0+|a

which the shipped compiler processes in 0.62 s and prototype A in **13.53 s**.
This is not a contrived pattern; the general fuzzer produced it within 129
draws, which is the same standard of "reachable by accident" the K18 entry
applies to the bug itself.

**[R23] One correction to what that number is.** This pattern does not
compile: every binary — the shipped compiler, A, A2, and the repo's own
committed `build/pcrec` — REFUSES it with `pattern too complex for the DFA
engine (>32,000 states; VM engine arrives in M4)`, exit 1. The times above and
below are therefore **time-to-refusal**: the work of building 32,000 DFA states
before the cap fires. That is still real closure work and still the right
measurement for a constant-factor comparison, but the note called it
"processes" and it is not a compile. (The panel's measurement critic found the
pattern in the state-cap bucket and read it as staleness; it is not — `src/` is
byte-identical to the note's own base commit. The number was always
time-to-refusal.)

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

All re-taken on the fixed prototypes, min-of-N, 0.9 ms floor:

| | shipped | A | **A2** | A2, stack unfixed |
|---|---|---|---|---|
| `(1{0,30}?[^]abc][^abc]){28,30}0+\|a` (to refusal) | 0.621 s | 13.530 s | **0.820 s** | 0.817 s |
| same, `{8,8}` (compiles) | 0.159 s | 1.428 s | **0.192 s** | — |
| nest100 / nest200 / nest250 | 0.003 / 0.002 / 0.004 s | — | **0.045 / 0.222 / 0.350 s** | 1.59 / 20.4 / 37.0 s |

**The fast path is still needed, and the stack fix does not substitute for
it.** [R23 S16 addendum.] The two mitigations are orthogonal and the last
column proves it: on this pattern the stack fix changes nothing (0.820 against
0.817 — it is a maxdepth-1, 2-context walk, so there is no stack to corrupt),
while the fast path is the whole of the 13.5 s → 0.82 s. Symmetrically, on the
deep-nesting family the fast path does nothing and the stack fix is the whole
of the 37 s → 0.35 s. Both are required; neither is the other's substitute.

**The corpus aggregate is WITHDRAWN as a wall-clock figure, because it cannot
be measured that way on this box.** The old row read "corpus aggregate compile
time: 0.671 s shipped, 0.662 s A" and invited the reading that A costs 1.4%
less. It cannot support that reading in either direction: 622 process spawns
at ~0.9 ms are essentially the whole of the ~0.6 s measured, and the ~0.1 ms
of per-pattern closure work sits under the spawn's own variance. Subtracting a
measured floor does not rescue it — three repeated trials of exactly that
measurement, each against a matched null corpus of 555 compiles of `a`, gave
nets of 0.089 / 0.121 / **−0.053** s for the shipped compiler and 0.138 /
**−0.266** / 0.341 s for A2. A quantity whose measurement changes sign
between trials is not a measurement.

**The counters are the instrument for this question**, and they already
answer it exactly, with a denominator and no clock: **x1.004 expansions,
x0.996 visits** over the same 554 patterns (the inflation table above). This
is also why §5 item 6's cost gates name specific expensive patterns rather
than a corpus total — a gate on a floor-dominated aggregate would pass
whatever the compiler did.

The fast path removes the constant-factor regression and leaves the
deep-nesting cost untouched, which is correct — that cost is real work, not
overhead.

**The threshold this section used to recommend is withdrawn. [R23 S16.]** It
read: full path-sensitivity at nesting depth ≤ D, falling back to today's
global memo beyond it, D=64 recommended, "MEASURED: D=32 bounds it at 0.12 s,
D=48 at 0.22 s, D=64 at 0.32 s". Every one of those numbers was a measurement
of the stack bug. With the entries restored the *entire* depth range up to the
parser's own cap costs 0.35 s, so a threshold at any D buys nothing and pays
for it in exactness. It is also posed on the wrong variable: the family that
actually blew up (§2a, S14) runs at open-loop depth 1, so D=64 would never
have fired on it at all. See §6, where the ruling request is withdrawn rather
than answered.

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

**It is cheap and it works — on the acceptance corpus.** **MEASURED:** 165/165
on the K18 corpus, 1704/1704 on the full `.rxt` suite, and compile time
indistinguishable from the shipped build on every family measured. Re-taken on
the 0.9 ms-floor harness against the FIXED A2, nested nullable stars:

| nesting depth | 100 | 200 | 250 (the cap) |
|---|---|---|---|
| shipped | 0.0011 s | 0.0017 | 0.0025 |
| B | 0.0011 s | 0.0019 | 0.0020 |
| A2, as designed | 0.0450 s | 0.2157 | 0.3541 |

**On cost, B still beats A2**, and that is worth stating plainly rather than
burying: if exactness were not the deciding axis, B would be the
recommendation. But the stakes changed with the stack fix and the note should
not keep quoting the old ones. This section originally set B's 0.11 s against
"the recommended design costs 1.6 s and 20.5 s"; the real comparison is 2 ms
against a third of a second, at the deepest pattern the parser will accept. B
wins a race in which both candidates finish before a human notices.

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

**MEASURED**, on `(?:a*|b*){n}`, the family the K18 entry names — re-taken on
the fixed prototypes with the 0.9 ms-floor harness [R23 S16 item 3]:

| n | 14 | 16 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|
| shipped | 0.0010 s | 0.0014 | 0.0026 | 0.0017 | 0.0028 | 0.0027 | 0.0015 |
| A2, as designed | 0.0012 s | 0.0016 | 0.0017 | 0.0015 | 0.0035 | 0.0016 | 0.0018 |
| C (no memo) | 0.0942 s | 0.3940 | 1.6337 | 3.3561 | 6.8409 | 14.0510 | **budget** |

A clean doubling per unit of n — **Θ(2ⁿ)**, measured ratios 2.05, 2.04, 2.05
across n = 19→20→21→22 — running out of the 3x10⁸-visit budget at n=22 (exit
97, `K18BUDGET exceeded`). This CONFIRMS the K18 entry's own sketch ("the
naive path-local version was exponential on `(?:a*|b*){20}`-class shapes") as
a measurement rather than a recollection, and it settles the shape of the
answer: the expensive thing is dropping the dedup, not making the rule
path-sensitive. A is exponentially cheaper than C, and on this family it is
indistinguishable from the shipped compiler.

**And the premise the pricing rests on is now measured too. [R23 S6.]** This
section asserted that "A and C give the same answers, so the difference
between them is the memo's contribution and nothing else" — an assertion, not
a measurement, and the whole argument-from-cost depends on it. The panel built
a third binary (`proto_ref.py`: no memo at all, plus the per-frame stack-entry
restore, i.e. the most conservative reading of the design's own rule) and
diffed emitted C three ways against A2 and C over 1,001 patterns: **0 differ,
all three.** The memo suppresses nothing that matters.

### 2d. Recommendation

**Prototype A2 — (state, open-loop-context) memo with an empty-context fast
path. No threshold, no fallback, exact everywhere. [R23]**

B is rejected on exactness (98-0 against the oracle), not on cost — on cost it
still wins, though by far less than this note originally reported. C is
rejected on cost (2ⁿ), not on exactness. A2 is the only candidate acceptable
on both.

The recommendation used to carry "with a nesting-depth threshold at D=64
pending the ruling in §6", on the strength of a residual that no longer
exists: the 39 s worst case was the prototype's stack bug, and with it fixed
the deepest pattern the parser will accept compiles in **0.35 s** (§2a). What
survives as a genuine residual is smaller and differently shaped — a
constant-factor cost that tracks the number of distinct open-loop CONTEXTS a
pattern creates, worst measured case 3.6x the shipped compiler on a pattern
the shipped compiler already spends ~0.8 s on. That is an ordinary
optimisation-pass cost, not a ruling-grade one, and §5 item 6 gates it rather
than trading exactness away to bound it.

---

## 3. Termination

In the style the K17 fix's comment carries, for A/A2 as recommended.

**Claim.** Every `clo_visit` walk terminates.

**Setup.** (i) **STRUCTURAL:** a (state, context) pair is EXPANDED — reaches
the switch — at most once per closure, because expansion is guarded by an
insert into the memo that fails on the second attempt. (ii) **AN OBLIGATION,
NOT A FACT** — see below: the set of contexts is finite, because a context is
an open-loop stack, the stack contains no repeats (a re-arrival at an open
loop redirects instead of pushing), and there are finitely many loop states.
(iii) **STRUCTURAL:** `frag_star` at src/ir/nfa.c:115-131 is the only
construction that creates a back edge, and its target always carries
`loop=1`, so every cycle in the epsilon graph passes through a loop-entry
split.

**[R23] Setup (ii) is the load-bearing premise, and it is promoted here from
a parenthesis to an obligation the rewrite must ASSERT** (§5 item 6). It is
not a property of the NFA; it is a property of the walk, and it holds only if
the redirect fires on EVERY re-arrival at an open loop — which in turn holds
only if the redirect's scan reads an accurate stack. R23 measured that scan
missing open loops on 358 of 4,369 patterns on the prototype as first built,
for exactly the reason §2a now records (S3/S10). Two independent measurements
say how thin the margin is:

* **Removing the open-set test loses termination outright.** [R23 S5.] A
  half-prototype with the context-keyed memo but the SHIPPED redirect trigger
  (`proto_half1.py`) does not merely fail to fix K18 — it SIGABRTs on the
  15-character `(?:(?:a|b*?)?)*`, and with the `openst` array oversized
  20,000x (`proto_half1b.py`) it still SIGSEGVs on the same pattern: without
  the open-set test a loop entry is pushed again at every fresh context, and
  every fresh context makes a fresh memo key. So the open-set test is not
  only what makes the redirect fire, **it is the only thing bounding the
  stack** against `openst`'s `nfa->n + 2` sizing.
* **The no-repeat invariant survived the corrupted stack by coincidence, not
  by design.** [R23 S9.] `proto_a2_dup.py` scans `open[0..depth)` for the
  state before every push: 0 duplicates on 1,001 patterns even on the
  UNFIXED prototype — because the slot the corruption overwrites is exactly
  the slot of the loop whose redirect is then missed, so a missed redirect
  pushes a loop that is by then genuinely absent. That is a mechanism
  coincidence, and it is why §5 item 6 keeps BOTH assertions: `nonstacktop`
  does not cover the no-repeat push, and the no-repeat push does not cover
  `nonstacktop`.

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

The decreasing-measure argument above is **STRUCTURAL** from the prototype's
code, and that mark stands.

**[R23] What does NOT hold is the comparative claim this section used to
make.** It said the argument was "strictly stronger than K17's and subsumes
it", on the grounds that a measure on the walk's own state survives changes to
the NFA's shape that K17's exit-points-outward argument would have to
re-check. That was marked BELIEVED and the panel broke it (S12), twice over:

* **It trades one premise for another, and the new one is the fragile one.**
  K17's argument needs no finite-context premise; this one needs setup (ii),
  which is a claim about the accuracy of the redirect scan and was measured
  FALSE on the prototype. "Holds regardless of what the NFA looks like" is
  true, but it holds only as long as something else — now an assertion —
  holds instead.
* **It proves a weaker property.** Termination is not correctness. A future
  construct whose loop exit pointed back INTO the loop would keep the measure
  decreasing (depth still drops at every redirect) while putting the
  empty-iteration redirect in the wrong place. K17's shape-based argument
  catches that; a decreasing measure cannot. Whatever "stronger" means, it is
  not this.

The two arguments are therefore kept as siblings, not as a replacement: the
decreasing measure for termination, K17's shape argument for where the
redirect lands. A new construction owes both.

**What could still break it.** If a future change let the redirect truncate to
a depth that is not strictly less than the current one — for instance, a
redirect that popped nothing when the loop was already the top — the measure
would stop decreasing. The rewrite should carry the "open loop is the stack
top" assertion (§2a) and an explicit `at < cl->depth` assertion, because the
termination proof is exactly what those two guard.

---

## 4. Blast radius, predicted

**[R23] Every number in this section survives the prototype fix, and it was
checked rather than argued.** The fix changes cost, not answers. Emitted-C
identity, fixed prototype against unfixed:

| corpus | patterns | differ |
|---|---|---|
| the dense shape space (`gen_shapes.py`) | 18,858 | **0** |
| the existing corpus (`harvest_patterns.py`) | 622 | **0** |
| two independent R23 generators | 1,001 + 523 | **0** |
| nesting ladder, depths 1–250, greedy and lazy | 38 | **0** |
| the bounded-repeat family of §2a | 3 | **0** |
| *non-vacuity control: base vs A2, same harness* | 1,001 | *405* |

And every blast-radius figure below re-derives on the FIXED prototype, exactly:
**249** of 18,858 shape-space patterns differ base-vs-A (§4.3), **83** differ
A-vs-B (§2b), **8** of 622 corpus patterns differ base-vs-A and they are
precisely the 8 named in §4.2, and A and A2 remain byte-identical on all
18,858. Separately, the panel's measurement critic rebuilt every prototype
from scratch and re-derived §4.1, §4.2 and §4.3 digit for digit, including the
1704/1704 suite run against A2 with the real harness.

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

> **RESOLVED 2026-08-15 — and the BELIEVED attribution above was WRONG.**
> [R23 M-M1/V5.] A concurrent lane root-caused and fixed this 32 minutes
> after this note's last commit (`fuzzfix`, merged at 7e27c19). The cause was
> **not** the M4.5 VM path and not any emitted matcher: `tests/fuzz/fuzz_driver.c`
> declared `ptrdiff_t caps[RX_NCAPS][2]` as a stack array sized by a
> preprocessor macro baked in when the SHARED driver was compiled against a
> throwaway pattern, then reused that driver unmodified against every later
> pattern whose real `rx_info.ncaps` was larger — a test-infrastructure
> stack smash, 274 of them, now 0. The fuzzer is green on both seeds at HEAD
> (R23 re-ran seeds 99 and 5: `content divergences: 0`), and the pattern this
> section names as the timing trigger now lands in the DFA state-cap refusal
> bucket instead.
>
> Two things are worth keeping rather than deleting. The hedge was
> well-calibrated — the attribution was wrong *precisely* because "I did not
> open a repro bundle", and opening it was cheap. And none of the three
> dispositions this section offered ("K19/K20 fallout, a known-and-excluded
> fuzz category, or a new K-entry") named the answer: a bug in the harness
> itself. A defect list that cannot spell "the instrument is broken" is §7's
> lesson wearing different clothes.

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
  must**, because M4.5's VM consumes the DFA's span. *[R23: still open as a
  capture differential. The lead attached to it is NOT — S15 found three
  short capture-bearing patterns whose generated matchers print uninitialised
  memory as spans under BOTH the shipped compiler and A2, the panel filed it
  as PROBE 1, and it is now **RESOLVED 2026-08-15 as K21** (fixed on main,
  merge 6eeedbb): `--emit-main`'s convenience `main()` read
  `<prefix>_search`'s three-valued return as a boolean, so a VM step- or
  frame-budget exhaustion (`RX_ERR_STEPS`/`RX_ERR_FRAMES`, negative and
  therefore C-truthy) printed as a successful match with uninitialised capture
  spans. A reporting bug in the emitted `main()`, not a matcher defect and not
  A2's — and the fourth instance in two days of a defect living in the
  INSTRUMENT rather than the thing measured, which is §7's subject.]*
* **The reverse machine (D7) in isolation.** It is exercised throughout (the
  counters aggregate both machines) but never singled out. `prune` is off
  there, so the closure keeps every thread alive — a different code path
  through the same walk. *[R23 S11: CLOSED for spans, and it mattered. Every
  pattern in the K18 family is fully nullable, so it matches at offset 0 and
  the reverse machine's job is trivially answered — which every corpus in
  this note inherited. A corpus of 240 shapes with a MANDATORY leading atom
  forces a computed match start: 81,840 cells, the shipped compiler wrong on
  1,980, A2 wrong on **0**. This is also where the stack corruption lived —
  S10's missed redirects are overwhelmingly on the reverse machine — so the
  axis this section flagged as unmeasured is exactly the axis the defect was
  hiding on.]*
* **libpcre2 as a second oracle** on the A-vs-B and base-vs-A cells. python3
  `re` alone was used. The K17/K18 entries record zero disagreements between
  the two oracles across this whole space, so I judged one oracle sufficient
  for a design screen — but D44's three-way rule means the rewrite lane owes
  the second oracle. *[R23 S15: the judgement is now MEASURED rather than
  believed — 998,535 oracle-vs-oracle cells across this note's own 18,858
  shapes plus three independent corpora, **0 disagreements**. D44 still binds
  the rewrite lane's expectations.]*
* **[R23 V7] Thread safety of the two new tables.** This section listed three
  gaps and this was a fourth. Concurrent `pcrec_compile()` is in the STANDING
  `make test` battery (TS-3), and a design that adds heap tables to the
  DFA-construction path owes an answer about where they live. **STRUCTURAL,
  and clean:** in the prototype both are per-compile automatic locals of
  `pcrec_build_dfa` (`prototypes/proto_a.py:370-371`) and the open-loop stack
  comes from the compile's own arena (`:373`); the only file-scope state is
  the measurement counters at `:68-69`, which do not ship. Nothing is shared,
  so nothing can race. §5 item 11 carries the obligation to keep it that way.

---

## 5. Validation plan for the rewrite lane

The K17 methodology, with the additions this lane's own findings demand.

1. **Oracle-verified family tests.** A live `.rxt` guard corpus, on **three**
   axes rather than the current one:
   * the 8 diverging shapes and the 7 controls already on file;
   * **the `{0,2}`-bodied family from §2b** — the 83 patterns where B and A
     disagree are a ready-made, independently-derived extension of the class,
     and they are not in the current 165;
   * **[R23 S8] an ARM-ORDER axis: every diverging shape in BOTH alternation
     orders, with greedy as well as lazy nullable arms.** §1.5 is why. The
     current 165 are lazy-only, and the two non-lazy entries in the file are
     there as CONTROLS — so the corpus contains no member of the sub-case
     whose witnesses are `(?:(?:b*|a)?)*`, `(?:(?:(?:b|)|a)?)*` and
     `(?:(?:b?|a)(?:b?|d))*`. A corpus derived from the bug as FOUND inherits
     the finder's alphabet; this axis is the cheapest known correction.

   Every expectation from python3 `re` AND libpcre2, both oracles agreeing,
   per D44.
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
   * **BOTH invariant assertions, not one.** [R23 S3/S9/S10.] The
     `nonstacktop` assertion (no redirect at a non-top position) AND the
     **no-repeat push scan** (`for i < depth: open[i].loop != s` before every
     push). Neither covers the other: on the unfixed prototype `nonstacktop`
     fired 358 times in 4,369 patterns while the no-repeat scan stayed at 0,
     and §3's termination proof rests on the one that stayed silent. An
     assertion that cannot fail on the bug it is named for is a sentence.
   * timing on the fuzz-found `(1{0,30}?[^]abc][^abc]){28,30}0+|a` and on
     nested-star depths 16/64/100/200/250 as explicit gates — that pattern is
     the one that caught the constant-factor regression and it should not be
     allowed to regress silently;
   * **[R23 S14] a BOUNDED-REPEAT-times-NULLABLE-LOOP row**, e.g.
     `((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,k}(){2,3}){1,2}){2,3}` swept in
     k. Neither of the two families above has this shape, and it is the one
     that showed cost tracking CONTEXT COUNT rather than nesting depth (§2a).
     The honest gate is a context-count or expansion budget, not a depth one.
   * at least two fuzzer seeds run to completion, **each with a per-pattern
     COMPILE-TIME budget reported as a count.** [R23 S14.] §4.4's fuzz result
     could not have seen the cost defect, because a compile that never
     finishes is not a divergence — it is invisible to a differential that
     compares answers. A budget turns it into a number.
7. **`make ubsan` and `make asan`, both axes.** The design adds two heap
   tables with growth and rehash paths — the first version of the prototype
   had a table that deadlocked when full (§7) — and neither the corpus nor the
   fuzzer exercises the grow path deliberately. A test that drives a closure
   past the initial capacity should be written on purpose.
8. **[R23 S7] `tests/codegen/run_trie_identity.sh` as an explicit gate.** A2
   creates this obligation and the note did not name it: the gate requires the
   shipped compiler and a `-DPCREC_NO_TRIE` build to emit byte-identical C, on
   the argument that subset construction plus minimization erases what the
   M2.8 trie does to the NFA — and that argument was written for a
   path-INSENSITIVE closure. A2 makes the closure path-sensitive over the
   epsilon graph and the trie CHANGES that graph, so the erasure does not
   automatically carry. It HOLDS under A2 on the panel's 180-pattern crossing
   of flat alternations with nullable-quantified branches under a nullable
   loop (0 differ, both directions) — but that is not the gate's own 500
   random patterns plus its `-i` sweep, which is what the rewrite lane owes.
9. **[R23 V6] `make strict`, and one serial `PROCS=1` pass.** Both are in
   K17's own close record ("full `make test` + `strict` green"), so §5's
   framing as "the K17 methodology plus additions" already implied them and
   the checklist omitted them. They are cheap and they are aimed at exactly
   what this design adds: new hash-table code with growth paths (`-Wall
   -Wextra`), and a result that must not depend on the harness fan-out.
10. **[R23 V4] The known-fail ratchet move, in the SAME COMMIT as the fix.**
    §4.5 measures the ratchet going red with `NOW PASSING:
    tests/known_fail/k18_empty_exit_through_seen_eps.rxt`, which is the
    ratchet working as designed. The landing must move that file into a live
    corpus directory (folded into item 1's re-scoped corpus) and close the
    `docs/dev/known_issues.md` K18 entry in the same commit, or `make test`
    stays red. Stated here as its own checklist line because a requirement
    stated three sections away from the checklist is a requirement someone
    executes the checklist without.
11. **[R23 V7] Thread scoping — a STRUCTURAL claim to re-check, or TS-3 to
    run.** Concurrent `pcrec_compile()` is in the STANDING `make test`
    battery (TS-3, `tests/thread/`, sabotage-validated with planted races),
    and this design adds two heap tables to the DFA-construction path.
    **STRUCTURAL, in the prototype:** both are per-compile automatic locals
    of `pcrec_build_dfa` (`prototypes/proto_a.py:370-371` — `PMemo memo;
    LCtxTab ctxs = {...}`) and the open-loop stack comes from the compile's
    own arena (`:373`, `arena_alloc(&cx->arena, ...)`); the only file-scope
    state in the prototype is the measurement counters at `:68-69`, which do
    not ship. So there is nothing shared to race, BY CONSTRUCTION. The
    obligation on the rewrite is to keep it that way and to say so at the
    declaration — and if any part of the real implementation becomes shared
    (a cache across compiles is the obvious temptation), TS-3 runs before it
    lands rather than after.
12. **[R23 V1] The harness's own pcrec budget, and the sanitizer axis.**
    `tests/harness/run.sh:256` wraps pcrec's OWN invocation in a bare,
    hardcoded `timeout 60`. That predates D45 and is outside its mechanism:
    `tests/lib/gen_timeout.sh` derives the budget from `-fsanitize=` in the
    flags of a GENERATED-CODE compile, and pcrec's own invocation passes no
    such flags — so the one compile this design can actually slow down has
    the one budget that does not scale with the axis, and blowing it is
    scored `HARNESS FAILURE`, not a graceful skip. With the stack fixed the
    margin is no longer an emergency (worst measured residual 0.35 s at the
    parser's cap, §2a), but the gap is real. The rewrite lane either folds
    that timeout into the `gen_timeout.sh` mechanism so it becomes
    axis-aware, or documents in `docs/testing.md` why pcrec's own invocation
    is exempt — with reasons, not silence.

    **The instrumented measurement this item asked for is DONE, and it found a
    failure the timing worry did not predict** (§2a): the design's `clo_visit`
    recursion is **Θ(d²)** where the shipped closure's is Θ(d) — 31,377 frames
    at the parser's 250-paren cap against 253 — so it needs ~7 MB of the
    default 8 MB stack on the PLAIN build (shipped: 192 KB) and overflows
    outright under asan at depth 210. Not the stack fix: the unfixed prototype
    measures identical recursion depths. Timing on the instrumented axes is
    comfortable by comparison (nest250: 0.85 s ubsan, 0.36 s plain), so the
    axis-aware-timeout question this item started as is the smaller half of it.

    The rewrite lane owes a DECISION here, not a tweak: bound the recursion
    (make the context-split descent iterative, as `limits.h` already did for
    the tail edges), or refuse above a measured depth, or size the stack
    deliberately and say so — **plus a deep-nesting case in the suite, since
    the corpus tops out at depth 4 and would never have found this.** Note the
    interaction with item 11: `pcrec_compile()` on a non-main thread gets
    whatever stack that thread was created with, which is frequently less than
    8 MB, and TS-3 is in the standing battery.
13. **[R23 S4] A comment obligation on the `marks_next` 2^32 wrap.** The
    empty-context fast path threads a SECOND `Marks` whose generation is
    advanced in lockstep with the first, so a wrap is safe only because both
    advance together. The panel attacked the fast path on key aliasing and
    generation desync and could not break it (0 of 1,001 and 0 of 523 emitted
    C differ; 44,455 span cells, A2 = oracle on all) — but nothing reaches
    2^32 closures, so the wrap itself is safe BY INSPECTION and will stay
    that way. The rewrite writes that down at the second `marks_next` call
    rather than leaving it implicit.

---

## 6. Rulings requested

**NONE remain open. [R23]** Both of the note's original rulings are
discharged, and the third ask is a scheduling detail the rewrite lane owns.

1. **The nesting-depth threshold — WITHDRAWN, not answered.** This note
   asked Frank to choose a depth D past which the compiler would fall back to
   today's global memo and be deliberately K18-buggy again, recommending
   D=64 on the strength of a MEASURED 39.25 s compile at the parser's own
   nesting cap. **That 39 s was a prototype bug, not a property of the
   design.** With the open-loop stack's entries restored per frame — a change
   that only ADDS per-frame work — the same worst case is 0.41 s (§2a), and
   the four randomly-generated patterns that did not finish under the unfixed
   prototype compile in 0.01–2.9 s (three of them; the fourth is cleanly
   refused by the existing DFA state cap, under the shipped compiler too).
   There is nothing left for a threshold to
   mitigate, so asking for one would be asking Frank to authorise a
   deliberately inexact compiler to work around a defect this note has since
   fixed. The recommendation is **NO THRESHOLD**.

   Recorded for whoever proposes one later, because the panel found the note
   had engaged neither ruling (V2/V3): a threshold proposal must answer
   **D22** (adversarial patterns are out of scope, and its own prescription
   for a legitimate-but-extreme pattern is a clean REFUSAL with a diagnostic,
   never silent degradation — so silent fallback is the shape that needs the
   extra justification, not refusal) and **D46** (every strategy-selection
   point must be OBSERVABLE and FORCEABLE — a silent per-closure fallback is
   exactly the selection point D46 governs, and without a stamp a sabotage
   test written for the exact path would silently exercise the buggy one).
2. **Whether §2a's "(1) and (2) are each necessary" claim needs measuring —
   DISCHARGED.** R23 built both half-prototypes (S5). Change (2) alone
   reproduces the shipped compiler's wrong answers cell for cell; change (1)
   alone does not terminate. §1.4 is re-marked MEASURED and §3 now carries
   the stronger fact that came out of it.
3. **Whether the 83 `{0,2}` patterns from §2b become a live guard corpus in
   this lane or the rewrite lane.** The rewrite lane, as one input to the
   re-scoped corpus §5 item 1 now specifies — which also owes the arm-order
   axis §1.5 found. No ruling needed; the second oracle is D44's standing
   requirement either way.

---

## 7. A note on this lane's own instrumentation

Two prototype defects were found and fixed during the measurements, and both
are recorded because both produced numbers that would have gone into this note
as findings.

**A fixed-capacity memo does not slow down when it fills — it hangs.** The
first prototype's open-addressed table never grew. Every slot carried the
current generation and none matched the key, so the probe loop never found a
free slot. It presented as `(?:...(?:a*)*...)*` at 17 nesting levels running
forever while 16 finished instantly — a cliff so sharp that I nearly wrote it
up as an algorithmic explosion. It was a full hash table. After adding growth,
depth 40 compiles in single-digit milliseconds. (This paragraph originally
quoted both of those as "0.12 s", which was this lane's shell harness's own
overhead rather than any measurement of pcrec — see §2a.)

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

**A third defect, and the defence above is exactly what could not see it.
[R23 S3/S16.]** `clo_visit` restored the open-loop stack's depth per frame and
not its entries, so a redirect crossing a frame boundary handed the caller a
stack naming the wrong loops. Every consequence of that bug was in the COST,
never in the ANSWERS: the corrupted scan misses a redirect, the walk then
expands a loop it should have exited, the expansion pushes that loop, the push
mints a fresh context, and the fresh context defeats the memo for the whole
subtree beneath it. Missed redirects compounding IS the context explosion —
100x of compile time, 48x the visits, 67x the contexts, and byte-identical
emitted C at the end of it.

So the byte-identity defence was not merely insufficient here, it was
STRUCTURALLY blind: **byte-identical output cannot see a cost bug.** The note
built its cost numbers against a correct-output oracle and was measuring a
defect the whole time, while §2a's own `nonstacktop` counter — the one thing
positioned to notice — read 0 because the corpus behind it could not reach a
three-loop-deep shape under a `{0,2}` (§2a). Two independent instruments, one
blind by construction and one blind by corpus.

The correction that found it is worth more than the fix: the panel refused to
take a STRUCTURAL mark on trust and read the prototype's control flow against
the sentence claiming it. Every marked-STRUCTURAL claim in this note is a
claim about code someone can read, which means every one of them is falsifiable
by reading — and the one that was false was the one nobody had read.
