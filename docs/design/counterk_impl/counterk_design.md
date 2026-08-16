# COUNTER-K — the bounded-repeat counter rung, emitted shape and its debts

The [ENG-BREP] COUNTER-K lane's design note, written BEFORE the code on this
project's design-first precedent (K18's scheduling, the possessify and
rung-select lanes' own notes). Design of record: `../eng_brep_design.md` §4
(the K axis), `../engine_m4.md` §2.5 (the ladder) and §4 (the step budget and
DD-2's two bounds). Rulings consumed: D45 (+ its three addenda), D46
(observability + controllability), D47 (all six ENG-BREP rulings, D47.1's
ladder order and D47.2's K-as-a-named-constant most of all). Open issue:
K22.

Claims are marked STRUCTURAL / MEASURED / BELIEVED in the house style
(`../eng_brep_design.md` §0.1). Every MEASURED claim below was taken from the
committed tree at `673992a` with `build/pcrec` built from it; the reproduction
commands are in `probes/` (see this directory's CLAUDE.md).

---

## 0. What this rung is for, in one paragraph

On the frames rung a bounded repeat is FULL REPLICATION: `X{m,n}` is `m`
mandatory copies of the body plus `n−m` nested optional copies, O(N·body)
emitted C, and the D45 incident. Counter-K replaces the copies with ONE body
copy (or K, the unroll factor) plus an ITERATION COUNTER, so emitted size
stops depending on the count. It is the ladder's LAST rung and its universal
fallback: unlike possessification and rung-select it declines nothing, because
it is the general shape rather than an exactness condition. Its endgame cell is
a body that BOTH earlier rungs refuse at a count the replication cap refuses —
`((a)|ab){0,4000}c` — and its debts are the three the ladder accumulated on the
way down.

---

## 1. Where it sits, and the two arms it must cover

### 1.1 The ladder as it will be

Per `A_REP`, cheapest provable machinery first (D47.1):

| | condition | emitted |
|---|---|---|
| 1 | `vm_cursor_fits` | span-loop cursor |
| 2 | `a->revbody` | one body copy, reverse-deterministic |
| 3 | `a->rmax >= 0` (bounded) | **this rung: one body copy per K iterations + a counter** |
| 4 | — | frames: the unbounded star |

with **possessification as an orthogonal modifier at every rung**, exactly as
today. Rung 3 does not displace `VM_RUNG_FRAMES_BOUNDED`; it takes the shapes
that rung takes today, and the frames-bounded rung survives as what
`-fno-counter` falls back to. That is what keeps replication available as the
§5.1 ground truth, which is this rung's entire validation story.

### 1.2 There are TWO arms, and the possessive one is not optional

MEASURED, and it corrects an assumption the ladder's shape invites. A
possessified bounded repeat does NOT stop replicating today — `vm_poss_chain`
emits one copy per optional repetition and buys frames, not size:

| pattern | flags | emitted lines | `VM_STRATS` |
|---|---|---|---|
| `((a)\|b){0,64}c` | `-fno-revdet` | 1,939 | `0x1` possessive |
| `((a)\|b){0,64}c` | `-fno-revdet -fno-possessify` | 1,997 | `0x2` backtracking |
| `((a)\|b){0,16}c` | `-fno-revdet` | 643 | `0x1` possessive |
| `((a)\|b){0,16}c` | `-fno-revdet -fno-possessify` | 653 | `0x2` backtracking |

Possessification saves 3% of the emitted size and all of the frames. So under
D47.1's ruled application order — possessify FIRST, cheapest provable
machinery first — a possessifiable bounded repeat is claimed by rung 1's
modifier and then replicated anyway. **If counter-K covers only the
backtracking arm, possessify-first becomes a size trap: the cheapest rung by
frames is the most expensive by bytes, and the ladder's order makes it win.**

So counter-K is emitted in both preferences AND under the possessive modifier:
one counted loop with a per-iteration choice point, and one counted loop with
the `RX_CUT` discipline `vm_poss_chain` already establishes. §2.6 gives the
possessive shape; §3.3 records that it is the one arm whose counter needs no
trail entry.

---

## 2. The counter: where it lives, and the cheaper idea that does not work

### 2.1 It is a TRAILED SLOT in `stv`, one per quantifier

`../engine_m4.md` §2.4's ruled `stv` layout table already has the row —
"bounded-repeat counters (`{m,n}`)" — with no producer today
(`nstate = 2*ncaps + nguard + nlow + nmark + 3*nrev`, no counter term). This
rung fills it in, taking the next slot class after `vm_slot_rev`, allocated by
a `vm_slot_ctr` base following `vm_slot_mark`'s pattern exactly.

`../eng_brep_design.md` §4.2 asserted this placement and called it "not a
coincidence" without giving the reason. The reason is §2.2, and it is the one
structural fact the whole rung rests on.

### 2.2 Why the counter cannot be a plain local, or a frame field — STRUCTURAL

The tempting alternative is to keep the counter untrailed, the way `pos` and
the cursor are kept untrailed (`../engine_m4.md` §2.5's ruled discipline: "a
resume frame IS its save point"), and save it in the resume frame. It is even
FREE: the emitted frame is `{const void *k; size_t pos; unsigned mark;}`, which
gcc lays out at 24 bytes with four bytes of tail padding, and an `unsigned it`
lands in that padding at no cost at all (MEASURED: `sizeof` 24 before and 24
after; the `--trace` build's `int id` already claims those bytes, so tracing
would pay 8 and the shipped build would pay nothing).

**It is still wrong, and the counterexample is `(a|b){0,4}c`.** A resume frame
saves the counter only for resumes AT the loop's own label. The body has its
own choice points, and a frame pushed INSIDE the body at iteration 1 is
resumed, via the fail label's one indirect jump, straight back into the middle
of the body's code — at which point a plain local `it_` holds whatever value
the later iterations left in it, not 1. Under replication this cannot happen,
because the counter is the PROGRAM COUNTER: iteration 1's body is distinct code
that falls through to iteration 2's entry. Collapsing the copies deletes that
encoding, and the value has to be restored on EVERY resume into or below the
loop, not only at the loop's own label.

Exactly one mechanism in this VM does that: the trail. A frame's `mark` records
the trail depth at push time, and the fail label's rewind undoes every `RX_SET`
performed since — including the counter's. Saving the counter per-frame instead
would mean every `PUSH` inside a loop body carrying the counters of all
enclosing counter loops, which is a vector whose length is the nesting depth
and is not O(1).

The cost is one trail entry per COUNTER WRITE, and §3.2 is where K turns that
into one entry per K iterations.

### 2.3 One slot serves both phases

`X{m,n}` has a mandatory phase (m iterations, no choice point) and an optional
phase (n−m iterations, one choice point each). They are disjoint in time, so
ONE slot serves both: the optional phase's entry resets it to 0, and a resume
into a mandatory-phase body frame rewinds past that reset and recovers the
mandatory count. Two slots would also work and would read more plainly in the
listing; one is proposed because the slot count has to agree across
`vm_cost_rep`, `vm_count_slots` and `vm_rep`, and one number per quantifier is
the arithmetic least likely to drift (`vm_slot_rev`'s "three always, even where
a preference reads only two" is the same reasoning one rung up).

---

## 3. The emitted shape

### 3.1 The mandatory phase (m iterations, no choice point)

```
L_min:    RX_SET(ctr, 0)
L_mtrip:  if (stv[ctr] + K > m) goto L_mtail
          <K copies of the body>          ; no PUSH: a mandatory copy that
          RX_SET(ctr, stv[ctr] + K)       ; fails fails the whole quantifier
          goto L_mtrip
L_mtail:  <m mod K copies of the body>    ; the residue, as emitted today
          goto L_entry
```

This half exists because `copies` in `vm_count_slots` is
`a->rmax < 0 ? a->rmin + 1 : a->rmax` — it counts the MANDATORY copies too, and
`../eng_brep_design.md` §4.2's sketch counts only the OPTIONAL ones ("the
counter starts at 0 and counts the optional copies") and leaves the mandatory
prefix replicating. MEASURED: `((a)|ab){4000}` and `((a)|ab){4000,}` are
refused today by `PCREC_MAX_VM_REPEAT_COPIES` — the unbounded row reports 4,001
copies, which is `rmin + 1` — and `((a)|ab){65}` is refused one copy over the
cap while `{64}` compiles at 1,866 lines. An exact count is not automatically
somebody else's problem: `((a)|bc){4000}` compiles today in 299 lines because
its body is reverse-deterministic, so this half is owed only for the bodies
BOTH earlier rungs decline — which is the same population the rest of the rung
serves.

### 3.2 The optional phase, GREEDY

```
L_entry:  RX_SET(ctr, 0)
L_trip:   if (stv[ctr] + K > NOPT) goto L_tail      ; NOPT = n − m
   c1:    PUSH(L_skip)                              ; resume SKIPS the rest
          <body copy 1>            -> c2
   c2:    PUSH(L_skip); <body copy 2>  -> c3
          ...
   cK:    PUSH(L_skip); <body copy K>  -> L_step
L_step:   RX_SET(ctr, stv[ctr] + K)
          goto L_trip
L_tail:   <vm_opt_chain at count (NOPT mod K)>      ; today's emission, verbatim
          goto L_next
L_skip:   goto L_next
```

Four things about it.

**The residue is a COMPILE-TIME constant.** `L_tail` is reachable only from
`L_trip`'s guard, and `stv[ctr]` is only ever `0` or incremented by `K`, so the
tail is entered with `ctr = K·floor(NOPT/K)` and the residue is exactly
`NOPT mod K`. `../eng_brep_design.md` §4.2 writes the tail as "`(n − stv[ctr])`
copies", which reads as a runtime quantity; it is not, and the tail is
therefore the EXISTING `vm_opt_chain` at a smaller count rather than anything
new.

**The counter is written once per TRIP, not per iteration.** That is a second,
independent reason K > 1 pays, and it is one §4.3's two curves do not measure:
the trail cost of the counter is `1/K` per iteration. Inside a trip the K
copies are distinct code and the program counter distinguishes them, which is
replication's own encoding used at scale K.

**At K ≥ NOPT the loop never runs and the emitter reduces to today's output —
BYTE-IDENTICALLY, by construction rather than by careful arithmetic.** The trip
guard fails on its first evaluation, the tail emits all NOPT copies, and the
tail IS `vm_opt_chain`. `../eng_brep_design.md` §5.4 proposes this as a gate
that has to be checked; here it is a structural property of the shape, and it
is also why the default K = 8 leaves every bounded repeat with `n−m ≤ 8`
untouched — which is most of the corpus, and most of the predicted blast
radius with it.

**A count threshold therefore never has to be invented.** `rungselect_design.md`
§6 left "uniform application, with no count threshold" as an open direction
because a threshold would be an unearned tuning axis (D18). Counter-K needs no
such decision: `K` IS the threshold, it is already the one measured dial, and
below it the rung emits what the rung below it emits.

### 3.3 LAZY, and why a loop is nest-equivalent and not chain-equivalent

Lazy flips the preference at each copy, mirroring `vm_opt_chain`'s own
`greedy` arm:

```
   cj:    PUSH(Bj)          ; resume TAKES another iteration
          goto L_next
   Bj:    <body copy j>  -> c(j+1)
```

**This is the one place where getting the shape wrong is a MEASURED live
defect rather than a slowdown**, and the note owes the argument. `vm_opt_chain`
emits `X{0,3}` as `(X(X(X)?)?)?` — NESTED, not chained — and its comment
records why: with chained optionals a later copy's alternation choice outranks
an earlier copy's, and `(?:ab|a){0,2}?b` on `"abab"` gives `[0,2)` where PCRE2
and python give `[0,4)`. `src/ir/nfa.c`'s `A_REP` arm carries the same
measurement.

A counter loop LOOKS like a chain. It is not: an iteration's skip frame means
"the loop ran j−1 times and then left", identical to the nested form's `other`
label, and the frames are pushed in the same order (1, 2, …) and popped LIFO in
the same order, giving the same preference sequence — n, n−1, …, 0 greedy and
0, 1, …, n lazy. What a chain would additionally admit is SKIPPING copy 1 and
TAKING copy 2, and a loop structurally cannot express that. STRUCTURAL, and
`(?:ab|a){0,2}?b` on `"abab"` is a named acceptance cell in §8 precisely
because it is the witness that already exists.

Unrolling does not disturb it: at K > 1 the pushes occur in the same order and
mean the same thing, which is `../eng_brep_design.md` §4.1's "K changes no
choice point" verified against the emitted shape rather than argued from the
count.

### 3.4 POSSESSIVE

One frame for the whole loop instead of one per iteration, via `RX_CUT` against
a mark slot recorded at loop entry — `vm_poss_chain`'s discipline, applied per
ITERATION instead of per copy:

```
L_entry:  RX_SET(mark, w->btn); RX_SET(ctr, 0)
L_trip:   if (stv[ctr] >= NOPT) goto L_next
          PUSH(L_stop)                     ; this iteration cannot run -> leave
          <body>  -> L_step
L_step:   RX_CUT(mark); ctr++ ; goto L_trip
L_stop:   RX_CUT(mark); goto L_next
```

The push stays. `vm_poss_chain`'s recorded lesson applies unchanged: a frame at
an iteration serves TWO purposes — resume when the CONTINUATION fails (which
possessification kills) and resume when the BODY fails (this iteration cannot
run, so leave the loop), which stays completely alive. Deleting the push is not
available; cutting at the boundary is.

**The possessive arm's counter needs no trail entry** — it can be a plain
local, `vm_revdet_rep`'s `%s_rv%d_it` precedent exactly. Every frame inside the
loop is cut at the next boundary, so no resume can land below the loop's entry
carrying a stale counter, and an outer backtrack that re-enters the loop passes
through `L_entry`, which reinitialises it. This is the §2.2 argument read in
the direction where it does not bind. Whether to take the saving or keep one
uniform trailed shape is §10 ASK 3.

---

## 4. The K axis

### 4.1 The constant

`PCREC_DEFAULT_UNROLL_K = 8` in `src/core/limits.h`, per D47.2 verbatim ("this
is a magic number. put it in a file of constants"), with the limits.h comment
carrying `../eng_brep_design.md` §4.3's two curves and the knee at K ≈ 16, the
reason 8 rather than 16 (the throughput estimate substitutes the frames-rung
star for K = 1 and is labelled an estimate), and the D18 line that the sweep
may move it.

`--unroll=K` is the value parameter D47.3 requires ("a value parameter for K —
deny cannot express it"). `--unroll=1` is the pure counter loop, and
`--unroll=<large>` is replication reached through the counter path, which §8.1
uses.

### 4.2 The CLAMP, which is what makes counter-K K22's real fix

**Finding, and it refutes an expectation the plan row and K22 both state.**
K22's repro is a depth-35/40 tower of `(?:…(?:a){0,2}…){0,2}`. Every count in
it is 2. With K = 8, `NOPT = 2 ≤ K` at every level, so §3.2's trip guard fails
immediately, the tail emits both copies, and **counter-K as `../eng_brep_design.md`
§4.2 specifies it does nothing whatever for K22.** The copy tree K22 asks to
stop existing keeps existing, at 2 copies per level, product 2^(d−1) exactly as
today.

The fix is a CLAMP, and it is a safety clamp rather than a tuning heuristic:

> **K is reduced — never raised — for a quantifier whose emitted-copy product
> down the nesting path would otherwise exceed `PCREC_MAX_VM_REPLICATION_PRODUCT`.**

With `c(x, K) = x` when `x ≤ K` and `K + (x mod K)` otherwise, a quantifier
emits `c(m, K) + c(NOPT, K)` body copies. At K = 1 that is 1 copy for a
`{0,n}` and 2 for an `{m,n}` with `m > 0`. So the tower's `{0,2}` levels emit
ONE copy each at K = 1, the product collapses to 1, and depth 35 and 40
compile. That is K22 half (1), discharged.

Two properties worth stating because they are what make this a clamp and not a
per-pattern heuristic in the sense §4.5 forbids:

1. It only ever moves K DOWNWARD, and only to keep a bound the compiler
   already enforces from being hit. Its failure mode is "less unrolling", never
   "different semantics" — §4.1's structural result is that K is not a
   semantics at any value.
2. It reuses the running product `vm_count_slots` already threads (`repl`, the
   K22 interim guard's own argument), so it introduces no new analysis.

The simpler alternative — K = 1 for any quantifier whose body contains another
bounded repeat — reaches the same place for K22 and is one line, at the cost of
being a shape rule rather than a bound rule. §10 ASK 2.

### 4.3 Where K is DECIDED, and the three-call-sites hazard

`vm_cost_rep`, `vm_count_slots` and `vm_rep` must agree about K exactly as they
must agree about the rung; `emit_vm.c`'s own header comment names that
agreement as a standing hazard. So K is a VERDICT FIELD on the node —
`Ast.unroll_k`, 0 meaning "not this rung" — set by a pass and read three
times, which is `Ast.possessive` and `Ast.revbody`'s precedent exactly and the
"one field is both the verdict and the artifact" rule `rungselect_design.md`
§1.2 states.

The pass is `src/opt/counterk.c`, driven from `src/opt/select_engine.c` beside
`run_possessify` and `run_revdet`, gated on `fit->chosen == ENGM_VM` and on
`PCREC_NO_COUNTER` — so `-fno-counter` is the pass not running, `unroll_k`
stays 0, and the emitter falls through to replication with no emitter-side
check at all. Same three-point plumbing as the two flags before it.

**One disclosed conservatism.** The clamp needs to know which enclosing
quantifiers actually replicate, and `vm_cursor_fits` is an emitter-internal
predicate the pass cannot see (`a->revbody` and `a->possessive` it can). The
pass therefore treats every enclosing `A_REP` as replicating. That
over-estimates the product, so the clamp fires slightly early on patterns with
a nested cursor-rung quantifier — costing unrolling and nothing else, which is
the direction an error here has to point.

### 4.4 The bench sweep

`../eng_brep_design.md` §4.4's axes stand, with two additions this note owes:

- **K = 1 and K = 8 must be swept against a REAL counter loop**, because §4.3's
  throughput table substitutes the frames-rung star for K = 1 and the star
  differs from a counter loop by a counter write, a compare, and the ABSENCE of
  an empty-iteration guard — §8 item 1's own disclosure. The trail entry per
  trip is the term the estimate structurally could not see.
- **The three subject regimes**, of which the estimate measured only the first:
  loop satisfied at its maximum; satisfied well below it; and FAILING after
  maximal consumption, where backtracking actually runs and where K should
  matter most.

The harness is scaffolded in this directory (`probes/bench_k.sh`) while the
panel runs, per the lane brief. It is a measurement, not a gate: D18 says the
dial must earn its value, and the value that ships is whatever the sweep says.

---

## 5. Termination, and the guard that must NOT be added

E-2's ruling is load-bearing and unchanged: **bounded repeats take NO
empty-iteration guard**, and `../eng_brep_design.md` §6 is this note's input
rather than something to re-derive. What counter-K owes is the argument at the
new shape.

STRUCTURAL. `L_trip` is reached only from `L_entry` (which sets `ctr = 0`) and
from `L_step` (which sets `ctr + K`), the guard is `ctr + K > NOPT`, so the
number of trips is at most `ceil(NOPT/K)` and the number of body executions at
most `NOPT` — **whatever the body consumes, including nothing.** The bound is
on the COUNTER, not on progress through the subject, which is exactly the
difference from the unbounded star, where no counter exists and subject
progress is the only available bound.

The backtracking direction terminates from the other side: each frame belongs
to one copy at one counter value, the fail label pops monotonically, and the
counter is restored from the trail on unwind, so no frame can be re-entered at
the same (copy, counter) pair twice.

**And the behaviour is identical to replication, not merely terminating.** An
empty iteration under replication proceeds to the next copy; under counter-K it
increments the counter and returns to the trip guard. Same iteration count,
same choice points, same order. §8's oracle sweep keeps
`../eng_brep_design.md` §6's ten-pattern family as a dense cell, and the SLOTS
section of `--emit-ir` remains the check that no guard slot appeared: adding
the guard "for safety" is a semantic change, it is what E-2 measured wrong on
60 of 225,240 pairs, and the counter makes it unnecessary.

---

## 6. Nesting, and what happens to the K22 interim guard

**Counters compose.** Each counter-rung quantifier owns one slot; an inner
loop's entry resets its own counter (a trailed write), and an outer backtrack
rewinds both. Nothing is shared and nothing needs a stack, which is the whole
reason the counter is a slot rather than a local.

The consequence that matters is on `vm_count_slots`, not on the emitted code.
Today that pre-pass walks the body once per copy (`for i < copies:
vm_count_slots(a->l, total)`) — the Θ(2^d) walk that IS K22 — and under
counter-K it walks `c(m,K) + c(NOPT,K)` times, bounded by `2K−1` per phase and
by 1 under the clamp. With the clamp the walk down a `{0,n}` tower is LINEAR in
depth.

**The K22 interim product guard STAYS, and stops being reachable on the default
path.** It keeps its exact value and its exact safety argument (the product is
a lower bound on the emitted node count, so it can only move a refusal earlier),
and it keeps firing for `-fno-counter` builds and for the residual §9 names. It
becomes what the size cap becomes: a backstop for the strategy below.
`docs/dev/known_issues.md` K22 closes when the depth-35/40 tower COMPILES on
the default path, which §8 makes an acceptance cell.

**The residual, named rather than smoothed over.** At K = 1 an `{m,n}` with
`m > 0` still emits two body copies (one loop per phase), so a `{1,2}` tower
multiplies by 2 per level and is refused — honestly and in 0.12 s, but refused.
Merging the two phases into one loop with a runtime `ctr >= m` test before the
`PUSH` would emit ONE copy for any `{m,n}` and would close it; it costs a
predictable per-iteration branch on the 0 < m < n shapes and is not proposed
here. §10 ASK 2 offers it.

---

## 7. The E-5-shaped step charge — now owed for FOUR shapes

### 7.1 The debt, collected

The plan row and `rungselect_design.md` §5 item 8 carry it: three shapes
perform real work and charge no steps, because a step is a backtrack
resumption counted at exactly one place (the fail label's
`if (--w->budget < 0)`), and none of them resumes.

1. **Possessified loops.** MEASURED at the possessify landing: under
   `--engine=vm` a fast `RX_ERR_STEPS` give-up became a correct-but-quadratic
   answer — 0.033 / 0.581 / 2.297 s at 10 / 50 / 100 KB, and 228.5 s at 1 MB.
2. **The revdet forward scan.**
3. **The revdet backward capture walk**, O(span) per commit.
4. **And counter-K's possessive arm**, which is shape 1 at a new rung.

The mechanism behind the quadratic is worth stating because "one step per loop
entry" sounds too weak until you see it: the cost is not one long scan, it is
the SEARCH loop entering the loop once per start position — n entries, each
O(n). Charging at entry makes the ENTRY COUNT budgeted, which is exactly what
E-5 did for islands.

### 7.2 The proposal: charge at entry, on EVERY rung, uniformly

> **One step is charged at the entry of every `A_REP`'s loop, on every rung and
> under every strategy, in addition to the fail label's existing
> per-resumption charge.**

The uniformity is not tidiness; it is forced, and by this rung's own validation
plan. §8.1's differential compares the FAILURE SURFACE of a replication build
against a counter build. If counter-K charged an entry step and replication did
not, the two builds would exhaust the budget at different iteration counts and
the primary instrument would be red by construction, for a reason that is not a
bug. A charge attached to the QUANTIFIER rather than to the STRATEGY is
invariant under every denial flag, which is the property the differential needs.

It is also one line at one place per quantifier, and it discharges all four
shapes plus the non-possessive cursor scan (whose forward scan is O(n) and
uncharged today) without an exception list.

**What it does not claim.** E-5's own limitation applies verbatim: this does
not make DD-2 a wall-clock bound. At 1 MB the possessify case charges ~10^6
steps against a 10^6 default budget, so it fires near the end of the work
rather than near the start. It restores the property D22 asks for — a budget
that catches absurd entry counts — and nothing more.

**What it costs, and the measurement that decides it.** A search over an n-byte
subject with q quantifiers now charges q·n steps even when every match is
linear, where today forward progress is free. On the DEFAULT path the prefilter
gates start positions and the exposure is small; under `--engine=vm` (which
disables the prefilter, R21 E-6) it is n. The deciding measurement, owed before
this lands: sweep subject size against a linear-matching pattern on both paths
and find where the default budget begins refusing legitimate work, against
today's baseline. If the crossover is uncomfortably low, the fallback is the
narrower rule — charge only where per-entry work is not bounded by a
compile-time constant, i.e. the four shapes and the cursor scan but not the
backtracking arms — which costs an exception list and keeps the differential
aligned only because the shapes it names are the ones both builds share. The
recommendation is uniform; the number decides.

---

## 8. Validation

### 8.1 Primary: the pcrec-vs-pcrec differential (requirement 1)

`../eng_brep_design.md` §5.1's instrument, one axis over from
`tests/rungselect/run_rungdiff.sh`, reusing `tests/possessify/possdiff_driver.c`
through the same `-DDIFF_A_LABEL`/`-DDIFF_B_LABEL` seam both earlier rungs
reused. Ground truth is `-fno-counter` (replication, what ships today);
subject side is the default build. Compared on span, EVERY capture slot, and
the failure surface.

**Two corrections this note owes to §5.1's stated expectations**, both found by
working the cost model rather than at a panel:

- **§5.1 item 4 asks for the stamps to AGREE. They must not, and requiring it
  would be wrong.** Frames are unchanged — one per iteration, both builds, so
  `frame_capacity` and RX_ERR_FRAMES align exactly. TRAIL is not: the counter
  build writes `ceil(NOPT/K)` extra entries, so its honest `cost.trail` is
  larger and its stamped ceiling is correspondingly tighter. The correct check
  is not equality but HONESTY per artifact — the ceiling-floor shape
  `tests/vm/run_vm_tests.sh` already uses (run at the stamped ceiling, confirm
  no give-up). MEASURED baseline for the arithmetic: `((a)|ab){0,16}c` stamps
  33 resume frames and 65 trail entries today; at K = 8 the counter build's
  frames stay 33 and its trail becomes 67.
- **§5.1 item 3's "at the same iteration count" holds for FRAMES exhaustion and
  not for TRAIL exhaustion**, for the same reason. The differential runs both
  builds at an equal forced `--backtrack-frames=` so the arrays match, asserts
  frame exhaustion at the identical iteration, and treats the trail delta as a
  quantified, asserted-bound difference rather than as noise.

**Named cells the differential must carry**, each because something already
measured lives there:

| cell | why |
|---|---|
| `(?:ab\|a){0,2}?b` on `"abab"` | §3.3: the nested-vs-chained preference defect, already measured in `vm_opt_chain` and `nfa.c` |
| `((a)\|ab){0,N}c` | the endgame body — declines possessify AND revdet (MEASURED: `VM_RUNGS 0x2`, `VM_STRATS 0x2`) |
| `((ab)\|b){0,N}b` | reverse-ambiguous, `rungselect_design.md` §5 residual 1, also `0x2`/`0x2` |
| `X{m,n}` with `m > 0`, `m == n` | §3.1's mandatory-phase loop, which §4.2's sketch does not have |
| `N ≡ 0, 1, K−1 (mod K)`, and `N = K−1, K, K+1` | §3.2's residue arithmetic, the off-by-one's home |
| `(a?){0,4}`, `(a*){0,3}`, `(\|a){m,n}` | §5's territory; the last is where the ORACLES disagree (R24: python vs libpcre2 on 106 of 15,600 cells) |
| every shape GREEDY, LAZY and POSSESSIVE | R24 S-F1: a greedy-only sweep is the experiment that missed the lazy conjunct |

Plus the non-vacuity control both earlier lanes carry: a sweep where the rung
never fired must itself fail.

### 8.2 The oracle sweep on top (requirement 3)

D44's three-way rule — pcrec / python3 `re` / libpcre2 — dense at the edges
§8.1 names, with `../eng_brep_design.md` §3.6's no-pre-built-exclusion rule and
U9 consulted before investigating a possessive-family disagreement. The `.rxt`
corpus is generated by a committed script (`tests/counterk/counterk.rxt` from
`make_corpus.py`), importing `../possessify_impl/gen_rxt.py` for its oracle
plumbing rather than copying it — which is how it inherits that file's
instrument note for free (`pcre2_match` returns the number of ovector pairs it
FILLED, not the group count; reading only `rc` pairs makes every trailing UNSET
group vanish rather than read as unset).

### 8.3 Forcing and stamps (requirement 2, D46/D47.3)

- **`VM_RUNG_COUNTER`**, a fifth `VmRungKind`, bit `0x10`, name `counter`,
  joining `<PREFIX>_VM_RUNGS` and `--emit-ir`'s RUNGS section through the same
  `vm_rung_mark()` call every other rung goes through.
- **`-fno-counter` / `PCREC_NO_COUNTER`** (`1u << 6`), the third member of
  D47.3's deny family, spelled and documented like the two before it: a
  TESTING AND TUNING axis, not a user feature. Denying it drops the quantifier
  to `VM_RUNG_FRAMES_BOUNDED`, which is the shipped semantics, which is what
  makes the differential possible. `rx_info.flags` masks it out with the
  others, for the reason `emit_info_def` records.
- **Do-or-die is asserted against the STAMP**: under `-fno-counter` the
  `COUNTER` bit must appear in no artifact, read from the artifact and not
  from the fact that a flag was passed.
- **`--unroll=K`** is the value parameter (§4.1).
- **NO scalar `<PREFIX>_VM_UNROLL_K` macro.** K is per quantifier once §4.2's
  clamp exists, and a scalar would misreport a mixed artifact — which is
  precisely the first draft M4.5e corrected mid-lane for the rung stamp. K is
  reported per quantifier in the RUNGS listing rows (`at L<n> counter K=8`),
  which is where per-quantifier facts already live and what a check asserts.

### 8.4 Mech sabotages

Following S45–S52's shape, in a `counterkdiff` arm:

| | what it removes | what must catch it |
|---|---|---|
| S53 | the counter's `RX_SET` becomes a plain store (untrailed) | §2.2's exact defect: `(a\|b){0,4}c` and any body with an internal choice point |
| S54 | the residue tail emitted at `NOPT mod K` becomes `0` | §8.1's `N ≢ 0 (mod K)` cells |
| S55 | the optional phase's `PUSH` moved after the body | preference order, the `(?:ab\|a){0,2}?b` cell |
| S56 | the §4.2 clamp disabled | the K22 tower stops compiling |
| S57 | the empty-iteration guard ADDED to the bounded path | E-2's 60-of-225,240 family |

S57 is deliberately the sabotage that adds something. §5 says the one thing an
implementation lane must not do is add the guard for safety, and a sabotage row
is how that instruction acquires a check.

### 8.5 Acceptance cells

1. **`((a)|ab){0,4000}c` compiles.** MEASURED today: refused, "a bounded repeat
   would replicate its body 4000 times (limit 64)". It is the counter rung's
   own endgame, distinct from rung-select's `((a)|b){0,4000}c` (MEASURED:
   revdet takes that one, 296 lines) precisely because both earlier rungs
   decline it.
2. **The K22 tower at depth 35 and 40 compiles and runs.** Today: refused in
   0.12 s by the interim guard (and, before that guard, a hang). Measured by
   `../rungselect_impl/k22_sweep.sh`, unchanged, which is the point — the
   sweep is committed and re-runnable and this lane re-runs it rather than
   writing a new one.
3. **`((a)|ab){4000}`, `((a)|ab){4000,}` and `((a)|ab){8,4000}c` compile**,
   §3.1's mandatory-phase half. MEASURED: all three are refused today (the
   `{4000,}` row reports 4,001 copies, which is `rmin + 1`), and `((a)|ab){65}`
   is refused one copy over the cap while `{64}` compiles at 1,866 lines. The
   BODY matters and the obvious choice is wrong: `((a)|bc){4000}` already
   compiles today in 299 lines, because an exact count over a
   reverse-deterministic body belongs to the rung-select landing. `(a|ab)` is
   the body that declines both earlier rungs.
4. **Byte-identity at K ≥ n−m** (§3.2), over the whole corpus, in both
   directions: `--unroll=4096` against `-fno-counter`.

---

## 9. What goes GREEN-BECAUSE-FAST or GREEN-BECAUSE-SMALL, and the re-pin

D46's discipline, and this lane inherits an explicit warning: the D45
compile-budget positive control (`tests/lib/run_gen_timeout_tests.sh:168-189`)
already NAMES counter-K as the cause when its size floor fires —

> THE NEXT RUNG DOWN THE LADDER WILL MEET THIS AGAIN. Counter-K is the strategy
> that replaces replication for exactly this shape, so when it lands this line
> needs its denial too, or the control goes quiet a second time.

The mechanical rule for the sweep is one sentence: **every site that today
relies on "denying revdet or possessify falls to LITERAL REPLICATION" must add
`-fno-counter`.** Every `-fno-revdet` and `-fno-possessify` occurrence is
audited; the survey below is the starting list, not a substitute for the grep.

| site | what happens | action |
|---|---|---|
| `tests/lib/run_gen_timeout_tests.sh:184` | the positive control's artifact drops under the 1,000-line floor and the tripwire FIRES, exactly as written | add `-fno-counter`; the tripwire firing on the way is the evidence, and it is kept |
| `tests/vm/run_vm_tests.sh:454` | asserts `((a)\|b){0,4000}c` under `-fno-revdet` is REFUSED naming "replicate its body 4000 times" — it now compiles | add `-fno-counter`; pair with the other side (§8.5 cell 1 compiles at default) |
| `tests/codegen/run_ir_listing.sh` `cap_no`, `cap_d45` | same, at `{0,65}` and `{0,4000}` | same |
| `tests/rungselect/run_rungdiff.sh` (whole file) | **highest severity**: its ground truth is "`-fno-revdet` ⇒ replication ⇒ the shipped semantics literally unrolled". It silently becomes counter-vs-revdet | `-fno-counter` on every denied build in the file; the file's header claim is re-stated |
| `tests/rungselect/run_rungselect_tests.sh:192-199`, and its count ceiling of 64 | the ceiling is derived from `PCREC_MAX_VM_REPEAT_COPIES` on the DENIED build, which no longer refuses | `-fno-counter`; re-derive the ceiling's rationale in the CLAUDE.md that states it |
| `tests/possessify/run_possessify_tests.sh:149,182` | stack `-fno-possessify -fno-revdet` to keep the block about the FRAMES rung | add `-fno-counter` for the same stated reason |
| `tests/mech/sabotages/S44_vm_repeat_cap_off.sh` | raises the copies cap so a bounded repeat replicates unbounded; its detectability runs through the rows above | inherits their re-pins |
| `tests/captures/classes_trie_bounded.rxt` header | prose tied to the cap bounding the count | prose correction only (D26 tier: no behaviour) |

Checked and found NOT exposed, which is worth recording so the next lane does
not re-check it: `tests/vm/run_vm_tests.sh:182` (`residual`), `:307` (`ceil`)
and `:265`/`:266` (`bigbounded`/`smallbounded`). The first two are UNBOUNDED
quantifiers, which counter-K does not touch; `smallbounded` is `{0,3}`, below
K, so §3.2 makes it byte-identical; and `bigbounded`'s assertion is about the
FRAME requirement, which counter-K leaves at one per iteration and therefore
does not move. Four of the "five green-because-fast" checks from the previous
landing survive counter-K unchanged, and that is a fact about frames not being
what this rung shrinks.

**Every re-pin is paired with the other side of the fact** (D46, as the
previous landing did): each "still refuses under denial" row gains a "compiles,
and small, at default" companion, so a denial that silently stopped working
cannot read as green.

**The size cap becomes BACKSTOP-ONLY.** `PCREC_MAX_VM_REPEAT_COPIES` keeps its
value and its measurement; what changes is that no default-path bounded repeat
can reach it, since a counter quantifier emits at most `2K−1` copies per phase
whatever the count. Its diagnostic stops being the endgame and gets to point at
the strategy instead — D26 tier 3 work, not to be gold-plated. Same for
`PCREC_MAX_VM_REPLICATION_PRODUCT` (§6).

---

## 10. Open questions for the panel and the manager

1. **§7's step charge: uniform, or the narrow exception list?** The
   recommendation is uniform-at-every-`A_REP`-entry, because the differential's
   failure-surface comparison needs a charge that is invariant under strategy
   denial. The cost is that forward progress stops being free on the
   `--engine=vm` path. The deciding measurement is specified in §7.2 and is
   owed before the code, not after.
2. **§4.2's clamp: product-driven, or "K = 1 when the body contains another
   bounded repeat"?** Product-driven is proposed (it is a bound rule, not a
   shape rule, and reuses machinery that exists). And, separately, whether §6's
   `{1,2}`-tower residual is worth the merged-phase loop now or is a recorded
   residual.
3. **§3.4: does the possessive arm take the untrailed-counter saving, or does
   every arm carry one uniform trailed shape?** The saving is real and the
   argument for it is sound; the case against is that it puts two counter
   disciplines in one emitter, and `vm_slot_rev`'s "three always" precedent
   went the other way for exactly that reason.
4. **§2.3: one counter slot for both phases, or two?** One is proposed; two
   read more plainly in the listing and cost almost nothing.

---

## 11. The residual, collected

What counter-K does NOT do, each with its reason:

1. **Unbounded quantifiers** (`X*`, `X+`, `X{m,}`'s tail) stay on the frames
   star, which already emits one body copy. Only `{m,}`'s MANDATORY prefix is
   taken (§3.1).
2. **`{1,2}`-style towers** still multiply by 2 per level at K = 1 (§6), and
   are refused rather than compiled. The merged-phase loop would close it;
   §10 ASK 2.
3. **The step budget still does not bound wall time** (§7.2), and the entry
   charge is not claimed to. E-5's own limitation, inherited deliberately.
4. **The clamp over-estimates the product** where an enclosing quantifier takes
   the cursor rung (§4.3), costing unrolling on those shapes.
5. **`../eng_brep_design.md` §8 item 4 — nested bounded repeats generally —
   shrinks but does not close.** This rung makes the emitted size of a nesting
   path linear where the clamp applies, and says nothing new about the CAPTURE
   semantics of nesting, which is §3.4's single-level derivation's territory.
6. **§8.1's differential is blind above the replication knee.** There is no
   ground truth at N = 4000, because the ground truth is what the cap refuses.
   `((a)|ab){0,4000}c` is checked by the oracle sweep and by the strategy's own
   N-independence, not by the primary instrument — the honest limit of
   "replication is the true version", stated at §5.1 and repeated here because
   it is this rung's endgame cell that sits in it.
