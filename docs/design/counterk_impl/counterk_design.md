# COUNTER-K — the bounded-repeat counter rung, emitted shape and its debts

The [ENG-BREP] COUNTER-K lane's design note, written BEFORE the code on this
project's design-first precedent (K18's scheduling, the possessify and
rung-select lanes' own notes). Design of record: `../eng_brep_design.md` §4
(the K axis), `../engine_m4.md` §2.5 (the ladder) and §4 (the step budget and
DD-2's two bounds). Rulings consumed: D45 (+ its three addenda), D46
(observability + controllability), D47 (all six ENG-BREP rulings, D47.1's
ladder order and D47.2's K-as-a-named-constant most of all), and R25's two
manager rulings (§10.1). Open issue: K22. Open with Frank: F-1, F-2 (§10.2).

Claims are marked STRUCTURAL / MEASURED / BELIEVED in the house style
(`../eng_brep_design.md` §0.1). Every MEASURED claim below was taken from the
committed tree with `build/pcrec` built from it; the reproduction commands are
in `probes/` (see this directory's CLAUDE.md).

---

## PANEL OUTCOME — R25 (2026-08-16), read this before any section

Three read-only critics over the note at `4d1306f`, plus the lane's own §7.2
measurement which landed mid-panel and refuted the note's own proposal
(`../../dev/reviews/2026-08-16-r25-counterk.md`). **Four blockers and nine
majors; every one is applied in place below rather than appended, which is this
directory's house style.** What a returning reader most needs:

- **§4.2's clamp did not work as first specified (E1).** It was a predicate
  over an ancestors-only product, which cannot see a subtree, so the K22 tower
  still refused and the acceptance cell was red on first run. Respecified as a
  BOTTOM-UP algorithm and its arithmetic PROVED ahead of the code by
  `probes/clamp_arith.py`. The "no new analysis" property the first draft
  claimed is gone, and §4.2 now says so.
- **The note's own sabotage witnesses could never fire (E2).** Both sat below
  the default K, so no counter was emitted and neither sabotage was
  detectable — controls sharing a source with what they control, reached from
  a new direction. Every witness now selects the strategy and asserts the
  stamp.
- **The §9 survey missed the one site that breaks `make test` (C1).** Its
  search key was "denial falls back to replication"; the site denies nothing.
  A second search key is added and the site gets a rewrite plan.
- **Two things the note claimed and could not have (E5, E7).** The possessive
  arm's untrailed-counter "saving" was a mandatory-phase miscompile; and the
  rung shrinks SIZE but not FRAMES, so the endgame cell trades a compile-time
  refusal for a ~512-byte runtime ceiling — now stated, with a Cost arm
  (§3.5) the first draft did not specify at all.
- **Two questions go to Frank**: F-1, whether K may vary per quantifier at all
  (§4.2's licence — `eng_brep_design.md` §4.5 says no, and the note
  self-authorized the exception); and F-2, §7.3's replacement step charge and
  its SHIFT. §4.2 and §7.3 are marked pending those rulings.
- **Verified clean and not to be re-checked**: every spelling and citation the
  docs critic examined, the differential's failure-surface premise, the
  four-of-five green-because-fast survivors, §8.1's 33-frames/65-trail
  baseline, §2.3's one-slot rewind, and the `bt[]` 24→24 measurement.

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

MEASURED. A possessified bounded repeat does NOT stop replicating today —
`vm_poss_chain` emits one copy per optional repetition and buys frames, not
size:

| pattern | flags | emitted lines | `VM_STRATS` |
|---|---|---|---|
| `((a)\|b){0,64}c` | `-fno-revdet` | 1,939 | `0x1` possessive |
| `((a)\|b){0,64}c` | `-fno-revdet -fno-possessify` | 1,997 | `0x2` backtracking |
| `((a)\|b){0,16}c` | `-fno-revdet` | 643 | `0x1` possessive |
| `((a)\|b){0,16}c` | `-fno-revdet -fno-possessify` | 653 | `0x2` backtracking |

Possessification saves 3% of the emitted size and all of the frames.

**The mechanism, corrected** [R25 E10]. The first draft said a possessifiable
quantifier is "claimed by rung 1's modifier and then replicated anyway", which
contradicts §1.1's own model two paragraphs above: possessification is an
ORTHOGONAL MODIFIER, not a rung, so a possessified bounded repeat is still ON
the frames-bounded rung and nothing claims it away from anything. The honest
statement is narrower and is a statement about a CHOICE rather than about
ladder order: **if counter-K is built for the backtracking arm only, then
possessified bounded repeats keep replicating — not because possessify-first
put them out of reach, but because this rung declined them.** There is no trap
in D47.1's order; there would be one in the omission.

**And the population is real, MEASURED on the path that ships**
(`probes/census_default.sh`, archived `census_default.txt`; the first draft
argued this over a `-fno-revdet` table, which is a population the default path
never reaches, and exhibited no member of the cell at all):

| routing | patterns reaching the VM | frames-bounded quantifiers | of which POSSESSIFIED |
|---|---|---|---|
| DEFAULT (ships) | 166 of 881 | 94 | **6** |
| `--engine=vm` | 513 of 881 | 258 | **6** |

Six, not zero — `(x)(?:ab|b){0,4}c` and `(x)(?:((a)|b){0,2}c){0,3}d` among them
— so the arm has customers. Six of 94 is also not many, and the note should not
overclaim from an adversarial `.rxt` corpus: `../eng_brep_design.md` §2.6
measures 17% of bounded quantifiers possessifiable there against **82%** on a
realistic set, so this cell is the one most likely to be much larger in the
field than in `tests/`. The argument for covering the arm is that the
population is non-empty and the emitter cost is one more use of machinery §3.4
already specifies — not that six is a large number.

So counter-K is emitted in both preferences AND under the possessive modifier:
one counted loop with a per-iteration choice point, and one counted loop with
the `RX_CUT` discipline `vm_poss_chain` already establishes. §3.4 gives the
possessive shape.

---

## 2. The counter: where it lives, and the two cheaper ideas that do not work

### 2.1 It is a TRAILED SLOT in `stv`, one per quantifier

`../engine_m4.md` §2.4's `stv` layout table already has the row —
"bounded-repeat counters (`{m,n}`)" — with no producer today
(`nstate = 2*ncaps + nguard + nlow + nmark + 3*nrev`, no counter term). This
rung fills it in, allocated by a `vm_slot_ctr` base following `vm_slot_mark`'s
pattern exactly.

**On the ORDER, since this note cites that table as authority** [R25 E12]. The
table puts counters immediately after the capture pairs and before the
empty-iteration guards; this note APPENDS the class after `vm_slot_rev`. The
deviation is real and it is the table that is stale: as-built already carries
three slot classes the table does not mention at all (`nlow`, `nmark`,
`3*nrev`), each appended as its rung landed. Appending is therefore the
as-built convention rather than a departure from one. Nothing is load-bearing
in the order — only that `vm_cost_rep`, `vm_count_slots` and the emitter agree
on it — so the proposal is to append and to AMEND `engine_m4.md` §2.4's table
to the as-built order when counter-K lands, rather than to contort the
allocation to match a sketch that four rungs have now outgrown.

`../eng_brep_design.md` §4.2 asserted the `stv` placement and called it "not a
coincidence" without giving the reason. The reason is §2.2.

### 2.2 Why the counter is a trailed slot: two alternatives, two different failures

The tempting alternative is to keep the counter untrailed, the way `pos` and
the cursor are kept untrailed (`../engine_m4.md` §2.5's ruled discipline: "a
resume frame IS its save point"), and save it in the resume frame. It is even
FREE: the emitted frame is `{const void *k; size_t pos; unsigned mark;}`, which
gcc lays out at 24 bytes with four bytes of tail padding, and an `unsigned it`
lands in that padding at no cost at all (MEASURED: `sizeof` 24 before and 24
after; the `--trace` build's `int id` already claims those bytes, so tracing
would pay 8 and the shipped build would pay nothing).

There are TWO alternatives here and they fail for different reasons. The first
draft of this section refuted one and claimed to have refuted both [R25 E4];
the panel was right, and separating them is what makes the real argument
visible.

**A PLAIN LOCAL is a correctness failure, and the counterexample is
`(a|b){0,4}c`.** The body has its own choice points, and a frame pushed INSIDE
the body at iteration 1 is resumed, via the fail label's one indirect jump,
straight back into the middle of the body's code — at which point an untrailed
`it_` holds whatever value the later iterations left in it, not 1. Under
replication this cannot happen, because the counter IS the program counter:
iteration 1's body is distinct code falling through to iteration 2's entry.
Collapsing the copies deletes that encoding, so the value must be restored on
EVERY resume into or below the loop, not only at the loop's own label.

**A PER-FRAME FIELD is not a correctness failure — it is CORRECT at one nesting
level — and it dies on cost.** Restored on every pop, exactly as `pos` already
is, it satisfies the requirement above: the pop that lands inside the body
carries that frame's own counter value. Traced by hand at one level, it works.
What kills it is nesting. Each frame would need ONE FIELD PER OPEN COUNTER
LOOP, because a frame pushed inside two nested counter loops must restore both
— so the field becomes a VECTOR whose length is the loop-nesting depth, in a
struct whose whole design is a fixed-size array of fixed-size elements, and
every resume label additionally needs to know which of those slots is its own
loop's. The frame stops being 24 bytes of padding-reuse and starts being
depth-shaped, which is the opposite of the property that made it attractive.

So the choice is cost against cost, not correctness against cost, and the trail
wins because the mechanism already exists: a frame's `mark` records the trail
depth at push time and the fail label's rewind undoes every `RX_SET` since,
including the counter's, at any nesting depth, with no new field and no
per-label knowledge.

**What the choice costs, said here because two later sections are consequences
of it and not of the rung.** One trail entry per COUNTER WRITE — which §3.2's K
amortises to one per K iterations — and that trail traffic is precisely why
§8.1's differential cannot expect the two builds' trail stamps to agree, and
why sabotage S53 (untrail the counter) is a row that can exist at all. A design
choice whose cost shows up as two entries in the validation plan should say so
where the choice is made.

### 2.3 One slot per quantifier, serving both phases — RULED

> **RULED (manager, R25 ASK 4): one counter slot per quantifier.** The panel
> traced the one-slot rewind sound; the reasoning below stands as written.

`X{m,n}` has a mandatory phase (m iterations, no choice point) and an optional
phase (n−m iterations, one choice point each). They are disjoint in time, so
ONE slot serves both: the optional phase's entry resets it to 0, and a resume
into a mandatory-phase body frame rewinds past that reset and recovers the
mandatory count. Two slots would also work and would read more plainly in the
listing; one is taken because the slot count has to agree across
`vm_cost_rep`, `vm_count_slots` and `vm_rep`, and one number per quantifier is
the arithmetic least likely to drift (`vm_slot_rev`'s "three always, even where
a preference reads only two" is the same reasoning one rung up).

**With one carve-out: `NOPT == 0` allocates NOTHING** [R25 E14]. For `X{m,m}`
the optional phase does not exist, so its entry reset would write a slot no
code can ever read — and, worse, it would write it in a build where §3.2's
byte-identity property says the emitter must reduce to `vm_opt_chain`'s output
exactly. A slot allocated and reset but never read breaks that identity at
EVERY K, including `K > NOPT`, which is the one place the note promises it
holds unconditionally. So the rule is explicit rather than emergent: a
quantifier with `rmin == rmax` emits the mandatory phase and no counter reset
for an optional phase that has no iterations.

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

**At K > NOPT — STRICTLY greater — the loop never runs and the emitter reduces
to today's output BYTE-IDENTICALLY, by construction rather than by careful
arithmetic.** The trip guard is `stv[ctr] + K > NOPT` evaluated at `ctr = 0`,
so it takes the tail exactly when `K > NOPT`; the tail emits all NOPT copies,
and the tail IS `vm_opt_chain`. `../eng_brep_design.md` §5.4 proposes this as a
gate that has to be checked; here it is a structural property of the shape.

**The strictness is not pedantry** [R25 E3]. At `K == NOPT` the loop RUNS: one
trip of K copies with a zero-length residue. It emits the same NUMBER of body
copies as replication and is not the same CODE, so byte-identity holds at
`K > NOPT` and nowhere else — and §8.1's `N = K−1, K, K+1` cell exists to sit
exactly on that boundary. Consequently the default K = 8 leaves every bounded
repeat with `n−m < 8` untouched (not `≤ 8`), which is still most of the corpus
and most of the predicted blast radius.

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
L_step:   RX_CUT(mark); RX_SET(ctr, stv[ctr] + 1); goto L_trip
L_stop:   RX_CUT(mark); goto L_next
```

The push stays. `vm_poss_chain`'s recorded lesson applies unchanged: a frame at
an iteration serves TWO purposes — resume when the CONTINUATION fails (which
possessification kills) and resume when the BODY fails (this iteration cannot
run, so leave the loop), which stays completely alive. Deleting the push is not
available; cutting at the boundary is.

**The counter here is the same TRAILED slot as everywhere else — RULED, and
the saving this note proposed for it was a MISCOMPILE.**

> **RULED (manager, R25 ASK 3): a uniform trailed counter slot in v1, all
> arms.** The optional-phase-only saving becomes a later measured row if a
> bench number ever asks for it (`vm_slot_rev`'s "three always" precedent).

The withdrawn proposal was that a possessive loop could keep its counter in a
plain local, on `vm_revdet_rep`'s `%s_rv%d_it` precedent, because every frame
inside the loop is cut at the next iteration boundary and so no resume can land
below the loop carrying a stale value. **That argument is true of the OPTIONAL
phase and false of the MANDATORY one** [R25 E5]. `vm_poss_chain` cuts at each
copy boundary (`emit_vm.c:1494`); the mandatory copies have NO cut between them
(`emit_vm.c:2013-2017`), because possessification removes the loop's giveback
and not the body's own need to find its match. So a body-internal frame pushed
during mandatory iteration 1 survives, resumes with an untrailed local reading
`m`, and the loop runs ONE iteration where it must run three —
`(?:a|bc){3}+` mis-matches. The saving was scoped to a phase the note's own
§3.1 had just introduced, and the two sections did not meet.

Recorded rather than deleted because the appealing part is real: on the
optional phase alone the cut argument holds, and it is a genuine trail saving
that a later measured row may take. What it is not is free, and "free" is what
the first draft called it.

**The possessive arm has no trip, no tail and no K** [R25 E6], which is why
§8.5 cell 4's byte-identity sweep is explicitly scoped away from it and why
§8.3's per-quantifier K row has nothing to report for a possessified
quantifier. Giving the arm the same K-unrolled trip/tail would remove both
exceptions at the cost of a second unrolled shape in the emitter; §10.3 ASK 2b.

### 3.5 The COST arm, and the ceiling the endgame cell inherits

`vm_cost_rep` gets a counter arm, and it is written out here because the panel
noted the first draft specified none [R25 E7] — at the exact call site where
the revdet rung's own silent cap already happened (`emit_vm.c:699-718`). An
under-counted frame requirement is a silent cap; an under-counted slot count
makes two live loops share one slot.

Against today's bounded frames arm (`emit_vm.c:800-820`), with
`NOPT = rmax − rmin`:

| | today (replication) | counter-K |
|---|---|---|
| `frames` | `rmin·bf + NOPT·(1 + bf)` | **unchanged** |
| `trail` | `rmax · bt` | `rmax·bt` + `(m>0 ? 1 + ⌈m/K⌉ : 0)` + `(NOPT>0 ? 1 + ⌈NOPT/K⌉ : 0)` |
| `pf` | `1 + bf + body.pf` | **unchanged** |
| `pt` | `bt + body.pt` | **unchanged** |
| `growable` / `unbounded` | | **unchanged** |

The `1 +` on each phase is the ENTRY RESET, which the first draft's arithmetic
dropped [R25 E8]; the worked cell `((a)|ab){0,16}c` at K = 8 is
`65 + 1 + ⌈16/8⌉ = 68`, not 67. That number is the differential's calibration
constant, so being off by one in it is being wrong about the instrument.

`pt` does NOT change, and the reason is worth stating: `pt` is the
per-subject-byte growth used to derive `subject_ceiling`, and the counter's
writes are bounded by the COUNT, which is a property of the pattern. They
belong in `trail`, which is exact for a bounded repeat, and not in the growth
term.

**The consequence the first draft did not draw: counter-K shrinks SIZE, not
FRAMES.** One choice point per iteration is semantics-dictated (§4.1), so the
frame requirement is identical under every K including replication — and for
the endgame cell that is a large number. `((a)|ab){0,4000}c` needs ~8,000
frames; `VM_MAX_AUTO_BT_FRAMES` is 1,024, so the capacity clamps, `fits` is
false, and `vm_ceiling` stamps a `subject_ceiling` of roughly 512 bytes.

**So the endgame cell trades an honest COMPILE-TIME refusal for an honest
RUN-TIME ceiling, and §8.5 must claim the second rather than implying the
first.** The artifact compiles, stamps `subject_ceiling ≈ 512`, matches
correctly below it and returns `RX_ERR_FRAMES` above it. That is D44.1's
designed answer for the residual class and not a defect — but "the pattern the
cap refused now compiles" is a weaker claim than it sounds, and the cell now
says which claim it is making.

**Growable frames, evaluated and declined.** Raising the cap is not available:
`rx_work` is a local under D19's 128 KB thread-stack budget, and 8,000 frames
at 24 bytes is 192 KB — over it by itself. Heap growth would end the
allocation-free property the whole VM is designed around. What DOES remove the
frames is possessification, which needs one frame for the entire loop
(§3.4) — so a possessified `{0,4000}` compiles AND runs at any length. That is
an independent argument for §1.2's possessive arm, reached from the cost model
rather than from the census.

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

> **PENDING F-1.** `../eng_brep_design.md` §4.5 (paneled R24) rules that K
> "must not become a per-pattern heuristic in v1", and everything in this
> section varies K per quantifier. The note is not entitled to carve itself an
> exception, and the first draft did exactly that. Frank rules whether K may
> vary at all in v1; this section specifies what to build if it may, and §11
> records what is lost if it may not.

**First finding: K = 8 alone does nothing for K22.** K22's repro is a
depth-35/40 tower of `(?:…(?:a){0,2}…){0,2}` and every count in it is 2. With
K = 8 the trip guard skips the loop at every level (§3.2), the tail emits both
copies, and the copy tree K22 asks to stop existing keeps existing at 2 copies
per level. The plan row and the K22 entry both credit counter-K with the fix;
counter-K without a clamp does not deliver it.

**Second finding, R25 E1, and it refutes this note's own first repair.** That
draft specified the clamp as a predicate over `vm_count_slots`'s running `repl`
product and claimed, as one of its two justifying properties, that it therefore
"introduces no new analysis". `repl` is ANCESTORS-ONLY and top-down
(`emit_vm.c:924,1019,1028), so on the tower nothing clamps until level 18, the
product parks at 2^17 = `PCREC_MAX_VM_NODES`, and depths 35/40 still refuse —
the acceptance cell red on first run. **The two claimed properties were not
simultaneously satisfiable**, and the honest statement is the one the first
draft avoided: making the clamp work REQUIRES a new analysis. It is a
whole-subtree, descendant-aware quantity, and no top-down product can compute
it.

#### The algorithm

A post-order (BOTTOM-UP) pass over the `A_REP` nesting forest. With
`copies(v, K)` the body copies one quantifier emits — §3.1's mandatory phase
plus §3.2's optional phase, `count` if `K > count` and `K + (count mod K)`
otherwise, and zero for an empty phase (E14):

```
sub(v) = 1                              if v has no A_REP descendant
       = max over immediate A_REP children c of ( copies(c, K_c) · sub(c) )

K_v    = PCREC_DEFAULT_UNROLL_K         if sub(v) == 1
       = 1                              otherwise
```

`K_c` is already decided when `v` is visited, which is what makes the pass
bottom-up and what the ancestors-only product structurally could not do.

**In one sentence: unroll only where unrolling multiplies nothing.** Unrolling
costs multiplicatively down a nesting path, so it is taken at the innermost
replicating level and nowhere above it.

The downshift is BINARY — `PCREC_DEFAULT_UNROLL_K` or 1, no intermediate
values. Intermediate values would be a tuning heuristic; two values are a
tractability switch, which is the distinction F-1 turns on.

#### The arithmetic, PROVED before the code

`probes/clamp_arith.py`, archived at `clamp_arith.txt`. It models the shape
rather than compiling, because the pass does not exist and a compile today
would measure replication; it reads `PCREC_MAX_*` out of `limits.h` rather than
copying the numbers, since a constant transcribed into a check is a control
sharing a source with the thing it controls.

| cell | product today | product clamped | verdict |
|---|---|---|---|
| `((a)\|ab){0,4000}c` | 4,000 | **8** | compiles |
| `((a)\|ab){4000}` | 4,000 | **8** | compiles |
| `((a)\|ab){4000,}` | 4,001 | **9** | compiles |
| `((a)\|ab){8,4000}c` | 4,000 | **16** | compiles |
| `((a)\|ab){65}` | 65 | **9** | compiles (refused today) |
| `((a)\|b){0,3}c` | 3 | 3 | replication, unchanged |
| `(a(b\|c)?){0,4000}` | 4,000 | **8** | compiles — the nested `{0,1}` does NOT over-clamp |
| K22 tower d=18 | 262,144 | **2** | compiles |
| K22 tower d=30 | 1.07 × 10⁹ | **2** | compiles |
| K22 tower d=35 | 3.44 × 10¹⁰ | **2** | compiles |
| K22 tower d=40 | 1.10 × 10¹² | **2** | compiles |
| `{1,2}` tower d=20 | 1,048,576 | 1,048,576 | **still REFUSES** |

against `PCREC_MAX_VM_REPLICATION_PRODUCT` = 131,072. The tower is flat at 2 at
ANY depth: the innermost replicating level takes K = 8 and contributes 2, every
level above it is clamped to 1 and contributes a factor of ONE.

The `(a(b|c)?){0,4000}` row is the one that kills the cheap alternative. "K = 1
for any quantifier whose body contains another bounded repeat" — offered in the
first draft as the simpler option — would clamp it, because `(b|c)?` IS a
nested `A_REP`. But `{0,1}` emits one copy and multiplies nothing, so the
subtree PRODUCT is 1 and the real rule leaves the unrolling alone. A shape rule
over-clamps a common shape; the product rule does not. This inverts the first
draft's recommendation, which called the shape rule the cheap fallback and the
product rule the principled one: the product rule is right, and it is right
because it is a product and not a shape.

The `{1,2}` rows are in the probe because a probe that shows only its own
successes is not evidence. §6 carries them as the named residual.

#### What this costs, stated plainly

The "no new analysis" property is GONE. This is a second traversal of the AST
computing a quantity nothing else needs, in a new pass, and the note previously
claimed the opposite. What survives from the first draft's two properties is
the other one, and it is the one that matters: the clamp only ever moves K
DOWNWARD, so its failure mode is "less unrolling" and never "different
semantics" — §4.1's structural result is that K is not a semantics at any
value.

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
check at all. Same three-point plumbing as the two flags before it. §4.2's
bottom-up traversal is this pass's whole body; it runs once, post-order, and
writes one field per node.

**One disclosed conservatism.** The clamp needs to know which nested
quantifiers actually replicate, and `vm_cursor_fits` is an emitter-internal
predicate the pass cannot see (`a->revbody` and `a->possessive` it can). The
pass therefore treats every nested `A_REP` as replicating. That over-estimates
the subtree product, so the clamp fires slightly early on patterns with a
nested cursor-rung quantifier — costing unrolling and nothing else, which is
the direction an error here has to point. The K22 tower is exactly such a
pattern: its innermost `(?:a){0,2}` takes the cursor rung and replicates
nothing, and `probes/clamp_arith.py` models it as replicating anyway, so the
proved product of 2 is itself the conservative answer.

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
here. §10.3 ASK 2a offers it.

---

## 7. The step charge — the fix of record is REFUTED, and replaced

**This section was written as a cost estimate for the E-5-shaped entry charge
and turned into a refutation of it.** The measurement is
`probes/step_charge.sh`; every number below is from one run of it at `4d1306f`,
and the probe counts both quantities at the two REAL charge sites in the
emitted artifact rather than at proxies — `--emit-ir`'s RUNGS rows name the
exact label `vm_rung_mark(v, entry, ...)` was called with, which is the label
an entry charge would sit at, and `rx_fail:` is the one charge site that exists
today.

### 7.1 The debt as it was recorded

The plan row and `rungselect_design.md` §5 item 8 carry it: shapes that perform
real work and charge no steps, because a step is a backtrack resumption counted
at exactly one place and none of them resumes — possessified loops (measured at
the possessify landing as 0.033 / 0.581 / 2.297 s at 10 / 50 / 100 KB and
228.5 s at 1 MB), the revdet forward scan, the revdet backward walk, and now
counter-K's own possessive arm. The fix of record, in all three documents, is
"an E-5-shaped one-step-per-loop-ENTRY charge".

### 7.2 REFUTED: entries and steps are the same number

MEASURED, `([a-z]+)9` against a subject of `n` bytes of `a` under
`--engine=vm`, which is the possessify lane's own shape:

| n | seconds | steps today | entries an entry charge would add | `-fno-possessify` steps |
|---|---|---|---|---|
| 10,000 | 0.023 | 10,001 | **10,001** | 50,015,001 (0.404 s) |
| 50,000 | 0.536 | 50,001 | **50,001** | 1,250,075,001 (9.320 s) |
| 100,000 | 2.121 | 100,001 | **100,001** | 5,000,150,001 (37.875 s) |

Three things fall out, and the first two were not known when §7 was written.

**The loop does not charge NOTHING.** An unanchored failing search already
charges one step per start position, on every rung, possessified or not,
because each attempt's final failure goes through the fail label. So the defect
is not the one the plan row describes. **The defect is that the charge is
LINEAR while the work is QUADRATIC**, and an entry charge is also linear.

**So the entry charge moves the crossover by a factor of two.** Against the
`1,000,000` default budget: today the possessified build gives up at
n = 1,000,000 bytes, by which point it has done ~5 × 10¹¹ byte-operations; with
an entry charge added it gives up at n = 500,000, at ~1.25 × 10¹¹. The
`-fno-possessify` control shows where the number needs to land — its steps are
n²/2, so it gives up at n ≈ 1,414. The gap is three orders of magnitude and the
proposed fix closes half of one.

**The `q·n` cost model in the first draft was also wrong.** MEASURED: at q = 1,
2 and 4 (`([a-z]+)9`, `([a-z]+)-([0-9]+)9`,
`([a-z]+)-([0-9]+)-([a-z]+)-([0-9]+)9`) the entry count is IDENTICAL — 1,001 /
100,001 / 1,000,001 at 1 KB / 100 KB / 1 MB for all three. A quantifier the
attempt never REACHES is never entered, so entries scale with the quantifiers
actually run, not with the pattern's quantifier count. The cost of an entry
charge is at most a doubling, not a q-fold increase.

### 7.3 The replacement: charge the ITERATION COUNT at loop EXIT

> **At the exit of every repeat loop that pushes NO per-iteration resume frame,
> charge `iterations >> PCREC_STEP_SCAN_SHIFT` steps. Loops that push a frame
> per iteration are already charged one step per iteration and get nothing.**

**Why the exclusion is exact, not a judgement call.** MEASURED: at n = 10,000
the `-fno-possessify` build charges 50,015,001 steps, and
n(n+1)/2 + (n+1) = 50,005,000 + 10,001 = 50,015,001 — the identity holds at all
three sizes. So a loop with a per-iteration frame ALREADY charges exactly one
step per iteration through the fail label, and charging again would double-count
the one case that was never broken. The blind spot is precisely and only the
loops that push no per-iteration frame: the possessive arms on every rung, the
cursor scan, the revdet forward scan, and the revdet backward walk.

**Why this respects D22.** The charge is one shift and one subtract at loop
EXIT, not per iteration. D22 forbids trading the budget against execution
speed, and a per-iteration decrement inside a possessified scan is exactly that
trade; a single arithmetic operation on a path that runs once per loop entry is
not.

**Why it stays strategy-invariant, which §8.1's differential requires.** The
charge attaches to the loop's SHAPE and its ITERATION COUNT. Under
`-fno-counter` a possessified bounded repeat is `vm_poss_chain` (replicated
copies, one cut frame, no per-iteration frame); under counter-K it is the §3.4
counted loop (no per-iteration frame). Both are in the charged class, both run
the same number of iterations on the same subject, so both charge the same
amount and the failure surface stays aligned. The backtracking arms need no
charge at all and are aligned trivially. This is a better answer than §7.2's
forced uniformity: it aligns because the quantity is real, not because the rule
was made blunt.

**What the shift buys, arithmetically.** The quadratic charges
n²/2^(SHIFT+1), so the give-up point moves as 2^((SHIFT+1)/2)·1,414:

| SHIFT | gives up at | work done by then | cost to a legitimate linear match |
|---|---|---|---|
| 0 | n ≈ 1,414 | ~10⁶ ops — the `-fno-possessify` build's own point, restored exactly | a 1 MB single-pass match charges 10⁶: at the budget |
| 6 | n ≈ 11,300 | ~6 × 10⁷ | a 64 MB match charges 10⁶ |
| 10 | n ≈ 45,000 | ~10⁹, about 1 s | a 1 GB match charges 10⁶ |

SHIFT is the trade between catching the pathology early and letting a genuinely
linear match over a huge subject run, it is a named `limits.h` constant on
K's own precedent (D47.2), and it is picked by measurement rather than here.
SHIFT = 10 is the recommendation: it keeps single-pass matching viable to ~1 GB
while cutting the pathological give-up point from 1 MB of subject and 200
seconds to 45 KB and about one second.

### 7.4 Blast radius, and the honest scope of the whole debt

MEASURED, the same pathological input on the DEFAULT (prefiltered) path:

| n | default path | `--engine=vm` |
|---|---|---|
| 10,000 | 0.000 s, 0 steps, 0 entries | 0.023 s |
| 100,000 | 0.001 s, 0 steps, 0 entries | 2.121 s |
| 1,000,000 | 0.003 s, 0 steps, 0 entries | >120 s (extrapolates to ~213 s from the 100 KB row; the possessify lane measured 228.5 s) |

**The DFA prefilter chooses the start positions, so the VM is never entered at
all and the quadratic is unreachable on the shipped path.** `--engine=vm`
disables the prefilter deliberately (R21 E-6) so the VM can be cross-checked
against the DFA instead of echoing it, which is what makes that path
diagnostic. So the whole debt — all four shapes — is a DIAGNOSTIC-PATH
exposure, and this is the fact that should decide how much is spent on it. It
is not an argument for doing nothing: `--engine=vm` is how every differential
in this project's last three lanes was run, and a diagnostic mode that takes
200 seconds where it should take one is a real cost to the people who use it
most. It is an argument for §7.3 rather than for anything larger.

**And E-5's own limitation survives either way.** None of this makes DD-2 a
wall-clock bound. It makes the budget proportional to work for the loops where
it currently is not, which is what D22's ROBUSTNESS framing actually asks for.

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
  build writes `1 + ⌈NOPT/K⌉` extra entries per phase (§3.5), so its honest
  `cost.trail` is larger and its stamped ceiling correspondingly tighter. The
  correct check is not equality but HONESTY per artifact — the ceiling-floor
  shape `tests/vm/run_vm_tests.sh` already uses (run at the stamped ceiling,
  confirm no give-up). MEASURED baseline: `((a)|ab){0,16}c` stamps 33 resume
  frames and 65 trail entries today; at K = 8 the counter build's frames stay
  33 and its trail becomes **68** — the entry reset included, per E8.
- **§5.1 item 3's "at the same iteration count" holds for FRAMES exhaustion and
  not for TRAIL exhaustion**, for the same reason.
- **And that distinction is NOT OBSERVABLE from outside as the emitter stands**
  [R25 E9], which the first draft's "compare frames exactly, treat trail as a
  quantified delta" quietly assumed away. Both overflows return the SAME
  sentinel (`emit_vm.c:2807-2808`) and `--backtrack-frames=` sets BOTH
  capacities from one number (`emit_vm.c:2633-2634`), so a differential cannot
  tell which array a give-up came from and cannot provision one without the
  other. Two ways out, and the lane proposes the first:
  1. **A distinct trail sentinel.** `rx_search`'s negative space is reserved
     for engine give-up conditions and has room (D42.3), so an `RX_ERR_TRAIL`
     beside `RX_ERR_FRAMES` costs one enum value and makes the two failure
     modes separately assertable — which the differential needs and which is
     also better diagnosis for a user who hits one.
  2. **Over-provision instead.** The differential forces a large capacity so
     the trail cannot be the binding array, and compares frame exhaustion
     only — cheap, and it gives up on ever checking the trail bound.
  Option 1 touches the emitted error surface, so it is named in §10 as an ask
  rather than assumed.

**Named cells the differential must carry**, each because something already
measured lives there:

**Every cell below obeys §8.4's selection rule** — `--unroll=1` or `NOPT > K`,
with the `COUNTER` bit asserted from the artifact — because a cell that does
not select the strategy tests the rung below it under this rung's name.

| cell | why |
|---|---|
| `(?:ab\|a){0,2}?b` on `"abab"` at `--unroll=1` | §3.3: the nested-vs-chained preference defect, already measured in `vm_opt_chain` and `nfa.c` |
| `((a)\|ab){0,N}c` | the endgame body — declines possessify AND revdet (MEASURED: `VM_RUNGS 0x2`, `VM_STRATS 0x2`) |
| `((ab)\|b){0,N}b` | reverse-ambiguous, `rungselect_design.md` §5 residual 1, also `0x2`/`0x2` |
| `X{m,n}` with `m > 0`, and `m == n` (`NOPT = 0`) | §3.1's mandatory-phase loop, and §2.3's emits-nothing carve-out |
| `N = K−1, K, K+1` and `N ≡ 0, 1, K−1 (mod K)` | §3.2's residue arithmetic and E3's strict `K > NOPT` boundary — the off-by-one's home |
| a revdet or cursor loop NESTED inside a counter loop at `NOPT > K` | E16: the one place trip-to-trip local sharing could leak, paired with sabotage S58 |
| a counter loop nested inside a counter loop | §4.2's clamp in its normal (non-tower) form |
| `(a?){0,12}`, `(a*){0,12}`, `(\|a){m,n}` with `NOPT > K` | §5's territory; the last is where the ORACLES disagree (R24: python vs libpcre2 on 106 of 15,600 cells) |
| every shape GREEDY, LAZY and POSSESSIVE | R24 S-F1: a greedy-only sweep is the experiment that missed the lazy conjunct |

The nullable-body cells are spelled at `{0,12}` rather than §5's `{0,4}` for
the same reason the sabotage witnesses moved: at `{0,4}` the counter is never
emitted and the cell would be checking replication's termination, which E-2
already settled, instead of the counter's.

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

> **EVERY WITNESS BELOW EXERCISES THE COUNTER, AND THE FIRST DRAFT'S DID
> NOT** [R25 E2, blocker]. S53's catcher was `(a|b){0,4}c` and S55's was
> `(?:ab|a){0,2}?b` — both `NOPT ≤ K`, so §3.2's trip guard takes the tail,
> replication is emitted, no counter exists and neither sabotage is
> detectable. That is this project's recorded controls-share-a-source failure
> reached from a new direction: the witnesses were chosen for the SEMANTICS
> they discriminate and never checked against the STRATEGY they must select.
>
> The rule, applied to every row here and to every §8.1 cell: a case meant to
> exercise the counter carries `--unroll=1` or `NOPT > K`, **and** the suite
> asserts the `COUNTER` bit in `<PREFIX>_VM_RUNGS` for it. The stamp assertion
> is not belt-and-braces — it is the only thing that keeps this from happening
> again the next time a default moves, and §8.3's own do-or-die discipline
> already says selection is asserted from the artifact and never assumed from
> pattern construction.

Following S45–S52's shape, in a `counterkdiff` arm:

| | what it removes | witness (counter-selecting) | what must catch it |
|---|---|---|---|
| S53 | the counter's `RX_SET` becomes a plain store (untrailed) | `(a\|b){0,4}c` **at `--unroll=1`**, and `(a\|b){0,32}c` at the default | §2.2's exact defect: any body with an internal choice point |
| S54 | the residue tail emitted at `NOPT mod K` becomes `0` | `((a)\|ab){0,20}c` (20 ≡ 4 mod 8) | §8.1's `N ≢ 0 (mod K)` cells |
| S55 | the optional phase's `PUSH` moved after the body | `(?:ab\|a){0,2}?b` **at `--unroll=1`**, and `(?:ab\|a){0,12}?b` at the default | preference order (§3.3) |
| S56 | the §4.2 clamp forced to `K_default` everywhere | K22 tower depth 35 | the tower stops compiling |
| S57 | the empty-iteration guard ADDED to the bounded path | `(a?){0,12}b` (12 > K) | E-2's 60-of-225,240 family |
| S58 | a resume label reads an untrailed loop local | a revdet or cursor loop nested inside a counter loop at `NOPT > K` | E16's invariant, below |

Each row is paired with a POSITIVE CONTROL asserting `VM_RUNG_COUNTER` is
stamped for its witness on the unsabotaged build. A sabotage row whose witness
does not select the strategy is a green row that proves nothing, which is
exactly what the first draft shipped.

S57 is deliberately the sabotage that ADDS something. §5 says the one thing an
implementation lane must not do is add the guard for safety, and a sabotage row
is how that instruction acquires a check.

**S58 and the invariant it attacks** [R25 E16, verified by the panel]. Counter-K
makes slot and local SHARING ACROSS TRIPS load-bearing: one emitted body copy
is re-entered at every iteration, so any per-loop local inside it is reused
where replication gave each copy its own. That is safe today only because of an
invariant stated in exactly one comment (`emit_vm.c:1821-1823`) — **a resume
label reads only trailed slots or `pos`, never an untrailed local.** Counter-K
does not introduce the invariant; it makes it carry weight it has not carried
before, and an invariant with no check is a sentence. Hence the row, and hence
§8.1's nested cell: a revdet or cursor loop INSIDE a counter loop at
`NOPT > K`, which is the shape where an untrailed inner local would be read
across an outer trip boundary.

### 8.5 Acceptance cells

1. **`((a)|ab){0,4000}c` compiles, and stamps an honest ceiling.** MEASURED
   today: refused, "a bounded repeat would replicate its body 4000 times
   (limit 64)". It is the counter rung's own endgame, distinct from
   rung-select's `((a)|b){0,4000}c` (MEASURED: revdet takes that one, 296
   lines) precisely because both earlier rungs decline it.

   **The cell asserts the ceiling, not unbounded matching** [R25 E7]. §3.5's
   cost model says the frame requirement is untouched by K — ~8,000 frames,
   clamped to `VM_MAX_AUTO_BT_FRAMES`, `subject_ceiling ≈ 512`. So the cell
   asserts four things: it compiles; the artifact stamps a nonzero
   `subject_ceiling`; a subject at half that ceiling matches correctly; and a
   subject well above it returns `RX_ERR_FRAMES` rather than a wrong answer.
   Writing the cell as "the pattern the cap refused now compiles" would be
   true and would hide the trade.
2. **The K22 tower at depth 35 and 40 compiles and runs.** Today: refused in
   0.12 s by the interim guard (and, before that guard, a hang). Measured by
   `../rungselect_impl/k22_sweep.sh`, unchanged, which is the point — the
   sweep is committed and re-runnable and this lane re-runs it rather than
   writing a new one.

   **This cell depends on §4.2's clamp and on nothing else in the rung**, and
   its arithmetic is proved ahead of the code by `probes/clamp_arith.py`
   (product 2 at any depth, against a limit of 131,072). Without the clamp it
   is red on first run — which is what R25 E1 found and why the probe exists.
   It is therefore also the cell that F-1 can remove: if K may not vary per
   quantifier, this cell is withdrawn and K22 closes as fast-refusal only.
3. **`((a)|ab){4000}`, `((a)|ab){4000,}` and `((a)|ab){8,4000}c` compile**,
   §3.1's mandatory-phase half. MEASURED: all three are refused today (the
   `{4000,}` row reports 4,001 copies, which is `rmin + 1`), and `((a)|ab){65}`
   is refused one copy over the cap while `{64}` compiles at 1,866 lines. The
   BODY matters and the obvious choice is wrong: `((a)|bc){4000}` already
   compiles today in 299 lines, because an exact count over a
   reverse-deterministic body belongs to the rung-select landing. `(a|ab)` is
   the body that declines both earlier rungs.
4. **Byte-identity at K > n−m** (§3.2 — strictly greater, R25 E3), over the
   whole corpus, in both directions: `--unroll=4096` against `-fno-counter`.
   **SCOPED to the non-possessive arms** [R25 E6]: §3.4's possessive loop has
   no trip, no tail and no K at all, so a possessified bounded repeat cannot
   satisfy this cell at any `--unroll` value, and the cell as first written was
   unachievable rather than demanding. §10.3 ASK 2b asks whether the possessive
   arm should instead GAIN the trip/tail so the scope restriction disappears;
   until that is ruled the cell states its own exclusion rather than quietly
   failing on it.

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

**That rule has a hole, and the panel found what fell through it** [R25 C1,
blocker]. `tests/vm/run_vm_tests.sh:507-519` asserts the K22 towers REFUSE on
the DEFAULT `--engine=vm` path with NO denial flag anywhere in it — the literal
negation of §8.5 cell 2. `-fno-counter` cannot re-pin it, because nothing is
being denied there to begin with, and the search key above ("denial falls back
to replication") structurally cannot find a site that denies nothing. It breaks
`make test` unconditionally on the day this lands. The second search key, added
here: **every site that asserts a REFUSAL of a shape counter-K is meant to
compile**, denial flags or not.

| site | what happens | action |
|---|---|---|
| `tests/vm/run_vm_tests.sh:507-519` | **BREAKS `make test` ON LANDING.** Asserts depth-30/40 towers refuse; §8.5 cell 2 says they compile | REWRITE, not re-pin. The default-path rows assert compiles-and-runs-correctly; the refusal, its "MULTIPLY through nesting" diagnostic and the no-output-file check are re-pinned under `-fno-counter`, which is where replication — and therefore the product — still lives |
| `tests/lib/run_gen_timeout_tests.sh:184` | the positive control's artifact drops under the 1,000-line floor and the tripwire FIRES, exactly as written | add `-fno-counter`. **The firing happens ONCE, during bring-up, as evidence that the prediction was right; the SHIPPED check is green with the denial in place** [R25 C5]. A red positive control is never committed — the point of the tripwire is that it fired when it should, not that it stays firing |
| `tests/vm/run_vm_tests.sh:454` | asserts `((a)\|b){0,4000}c` under `-fno-revdet` is REFUSED naming "replicate its body 4000 times" — it now compiles | add `-fno-counter`; pair with the other side (§8.5 cell 1 compiles at default) |
| `tests/codegen/run_ir_listing.sh` `cap_no`, `cap_d45` | same, at `{0,65}` and `{0,4000}` | same |
| `tests/rungselect/run_rungdiff.sh` (whole file) | **highest severity**: its ground truth is "`-fno-revdet` ⇒ replication ⇒ the shipped semantics literally unrolled". It silently becomes counter-vs-revdet | `-fno-counter` on every denied build in the file; the file's header claim is re-stated |
| `tests/rungselect/run_rungselect_tests.sh:192-199` | the frame-capacity contrast: replication's frame requirement scales with the count | `-fno-counter`. **The "count ceiling of 64" is NOT here** [R25 C3/D4] — the first draft cited this line for it; the ceiling lives in `run_rungdiff.sh` and `tests/rungselect/CLAUDE.md`, i.e. in the row above, and the miscitation is corrected rather than kept |
| `tests/possessify/run_possessify_tests.sh:149,182` | stack `-fno-possessify -fno-revdet` to keep the block about the FRAMES rung | add `-fno-counter` for the same stated reason |
| `tests/mech/sabotages/S44_vm_repeat_cap_off.sh` | raises the copies cap so a bounded repeat replicates unbounded; its detectability runs through the rows above | inherits their re-pins |
| `tests/captures/classes_trie_bounded.rxt` header | prose tied to the cap bounding the count | prose correction only (D26 tier: no behaviour) |
| `tests/vm/run_vm_tests.sh:109` (`--step-budget=50` pin), `:428` (prefilter contrast), `tests/lib/run_gen_timeout_tests.sh:250` (budget sized to complete), `tests/cli/run_cli_tests.sh:1594` | **step-budget-pinned checks** [R25 E11]. They do not care about replication and are not re-pinned by `-fno-counter` — they care about the step COUNT, so any change to what is charged moves them | join §7.3's landing, not this table's. Listed here because the two lists are otherwise easy to confuse: this table is about the SIZE strategy, that one is about the BUDGET |
| `docs/dev/known_issues.md` K22, and the `[ENG-BREP]` plan row | both credit "counter-K" alone with a fix that §4.2's CLAMP structurally provides — counter-K without the clamp leaves the tower exactly where it is | [R25 D5] corrected at landing, in the same change, naming the clamp |

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

## 10. Open questions, and what R25 already settled

### 10.1 RULED at R25 — recorded here so the list does not re-open them

- **ASK 3 — a uniform TRAILED counter slot in v1, all arms** (manager). The
  untrailed-local saving was a mandatory-phase miscompile as scoped; §3.4
  carries the ruling and the refutation. An optional-phase-only saving is a
  later measured row if a bench number asks for it.
- **ASK 4 — one counter slot per quantifier** (manager), with §2.3's explicit
  `NOPT == 0` emits-nothing carve-out.

### 10.2 With FRANK

- **F-1: may K vary per quantifier in v1 at all?** `../eng_brep_design.md`
  §4.5 says K "must not become a per-pattern heuristic in v1", and §4.2's
  clamp varies K per quantifier — the note is not entitled to grant itself
  that exception, and its first draft did. The manager's recommendation to
  Frank is a BINARY downshift (the constant, or 1 — no intermediate values)
  computed by §4.2's bottom-up pass, as a D47 addendum annotating §4.5 in
  place with the tuning-versus-tractability distinction, conditioned on
  `probes/clamp_arith.py` proving the arithmetic first. That probe now exists
  and the proof is §4.2's table. **If F-1 goes the other way**, §8.5 cell 2 is
  withdrawn, K22 closes as fast-refusal only on the interim guard already
  landed, and the clamp becomes its own ruled row later; the rest of the rung
  is unaffected, which is worth knowing before ruling.
- **F-2: §7.3's step charge, and SHIFT.** The E-5 entry charge is refuted by
  measurement (§7.2); §7.3 proposes `iterations >> SHIFT` at the exit of loops
  that push no per-iteration frame, SHIFT = 10 recommended. §7.4 should size
  the effort before it is spent: the entire four-shape debt is reachable only
  on `--engine=vm`, since the prefilter means the VM is never entered on the
  shipped path. DD-2/D22 territory with the D44/R21 E-5 precedent, so not a
  lane or manager call.

### 10.3 Still open for the manager

1. **ASK 2a — §6's `{1,2}`-tower residual**: worth the merged-phase loop now
   (one body copy for any `{m,n}`, at the cost of a runtime `ctr >= m` test on
   the `0 < m < n` shapes), or a recorded residual? The note recommends
   recording it: the shape is rare and the merge complicates the one place
   §3.2's byte-identity argument is currently clean.
2. **ASK 2b — should the POSSESSIVE arm gain a K-unrolled trip/tail?**
   [R25 E6] Today it has none, which is why §8.5 cell 4 excludes it and
   §8.3's per-quantifier K row has nothing to report for it. Giving it the
   trip/tail removes both exceptions and adds a second unrolled shape to the
   emitter. The note leans to giving it, since two exceptions in the
   validation plan cost more to explain than one more emission arm costs to
   write — but it is a real trade and the lane should not self-authorize it.
3. **ASK 5 — a distinct `RX_ERR_TRAIL` sentinel?** [R25 E9] Trail and frame
   overflow are indistinguishable from outside today, and
   `--backtrack-frames=` sets both capacities from one number, so §8.1's
   promised "frames at the identical iteration, trail as a quantified delta"
   is not observable as the emitter stands. `rx_search`'s negative space has
   room (D42.3). It touches the emitted error surface, so it is asked rather
   than assumed; the fallback is over-provisioning and checking frames only.

---

## 11. The residual, collected

What counter-K does NOT do, each with its reason:

1. **Unbounded quantifiers** (`X*`, `X+`, `X{m,}`'s tail) stay on the frames
   star, which already emits one body copy. Only `{m,}`'s MANDATORY prefix is
   taken (§3.1).
2. **`{1,2}`-style towers** still multiply by 2 per level at K = 1 (§6), and
   are refused rather than compiled. The merged-phase loop would close it;
   §10.3 ASK 2a.
3. **The step budget still does not bound wall time** (§7.3), and neither the
   refuted entry charge nor its replacement claims to. E-5's own limitation,
   inherited deliberately. What §7.3 changes is that the budget becomes
   PROPORTIONAL to work for the loops where it currently is not.
4. **§7.3's charge is designed and unmeasured against a real implementation.**
   The arithmetic in its SHIFT table is derived from the measured step and
   iteration counts, not from a build that charges this way — the charge does
   not exist any more than the counter loop does. It is the same disclosure
   `../eng_brep_design.md` §8 item 1 makes about K itself.
5. **The frame requirement is UNTOUCHED, so the endgame cell gains a runtime
   ceiling where it loses a compile-time refusal** (§3.5). One choice point per
   iteration is semantics-dictated; no value of K moves it, and growable frames
   are declined against D19's stack budget. `((a)|ab){0,4000}c` compiles and
   then stamps `subject_ceiling ≈ 512`. Only possessification removes the
   frames, which is the possessive arm's second independent justification.
6. **The clamp over-estimates the subtree product** where a nested quantifier
   takes the cursor rung (§4.3), costing unrolling on those shapes.
7. **Everything in §4.2 is contingent on F-1.** If K may not vary per
   quantifier, the clamp does not exist, §8.5 cell 2 is withdrawn, and K22
   closes as fast-refusal only on the interim guard already landed. The rest
   of the rung — the counter, the two phases, the cost arm, the size win on
   flat bounded repeats — is unaffected either way.
8. **`../eng_brep_design.md` §8 item 4 — nested bounded repeats generally —
   shrinks but does not close.** This rung makes the emitted size of a nesting
   path linear where the clamp applies, and says nothing new about the CAPTURE
   semantics of nesting, which is §3.4's single-level derivation's territory.
9. **§8.1's differential is blind above the replication knee.** There is no
   ground truth at N = 4000, because the ground truth is what the cap refuses.
   `((a)|ab){0,4000}c` is checked by the oracle sweep and by the strategy's own
   N-independence, not by the primary instrument — the honest limit of
   "replication is the true version", stated at §5.1 and repeated here because
   it is this rung's endgame cell that sits in it.
