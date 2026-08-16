# The REVERSE-DETERMINISTIC rung — emitted shape, as built

The [ENG-BREP] RUNG-SELECT lane's implementation sketch, written BEFORE the
code on this project's design-first precedent. Design of record:
`../eng_brep_design.md` §3 (rung selection, §3.4's corrected two-clause capture
derivation) and `../engine_m4.md` §2.5 (the ladder and the rung's exactness
condition). Rulings: D46 (observability + controllability), D47.1 (ladder
order), D47.3 (deny-flag surface + per-quantifier stamps).

Claims are marked STRUCTURAL / MEASURED / BELIEVED in the house style
(`../eng_brep_design.md` §0.1).

---

## 0. What this rung is for, in one paragraph

`emit_vm.c`'s per-`A_REP` choice is three-way today: possessified (a modifier),
deterministic fixed-length body → span-loop cursor, everything else → frames.
On the frames rung a BOUNDED repeat is full replication (`X{m,n}` is `m`
mandatory copies plus `n−m` nested optionals), which is O(N·body) emitted C and
the D45 incident. This rung slots between cursor and frames and emits ONE body
copy for a body that is variable-length or choice-bearing but whose consumed
run decomposes into iterations UNIQUELY — the acceptance cell being
`((a)|b){0,4000}c`, sixteen characters and 3.5 MB today.

---

## 1. The condition, and why it is TWO unique-iteration checks

**FORWARD** — the body must admit a unique iteration: (U1) one-unambiguous,
(U2) prefix-free, and non-nullable, on its position (Glushkov) automaton. This
is `src/opt/possessify.c`'s existing `body_admits_unique_iteration`, unchanged
and shared rather than re-implemented. It is what makes the forward scan
deterministic: from any boundary at most one iteration can run and it has
exactly one end, so the boundary chain `q₀ < q₁ < …` from the loop's entry is
DETERMINED (§2.3's chain, the same object possessification's soundness rests
on).

**REVERSE** — the REVERSED body must admit a unique iteration too, checked by
building the reversed AST and running the identical predicate on it. This is
what makes the retreat computable locally: from a boundary `q` there is at most
one `p` with the body matching `[p, q)`, so a backward walk necessarily lands
on the chain's own predecessor rather than on some other decomposition.

**Both are needed, and each has a witness.**

- `(aa?)` — §2.5's own counterexample — fails FORWARD (U2): its accepting
  position `a₁` (with `a?` empty) has an outgoing edge. Stays on frames, as the
  design requires.
- `(?:ab|b)` — passes FORWARD (initial positions `a`,`b` are byte-disjoint; no
  accepting position continues) and fails REVERSE: reversed it is `(?:ba|b)`,
  whose two initial positions are both `b`. MEASURED as a real ambiguity rather
  than a modelling artifact: on `"abab"` the boundaries are 0,2,4, and a
  backward walk from 4 can read `b` and stop at 3 (branch `b`) or read `ab` and
  stop at 2 (branch `ab`) — both are genuine body matches and only one is a
  chain boundary.

That second class is exactly the residual `engine_m4.md` §2.5 predicts the
BOUNDARY-RECORD rung shrinks to ("bodies deterministic forward but ambiguous
backward"). Recording it here is the honest statement that this rung does not
take it.

### 1.0.1 The two reverse checks are MUTUALLY REDUNDANT, MEASURED

There are two reverse-direction tests in the shipped analysis — reverse
unique-iteration, and `rd_alt_disjoint`, which re-derives on the reversed tree
the branch-first-set disjointness the emitted backward walk's byte dispatch
depends on. §1.2 below says the second is kept because "implied by" is how a
dependency quietly survives a change to what it implies.

**MEASURED, by a sabotage that came back green:** on the shape space this rung
admits, either check ALONE declines everything the other does. Sabotage S50's
first version removed reverse unique-iteration and kept `rd_alt_disjoint`, and
the differential reported **0 divergences over 201 patterns** — not for want of
a discriminating pattern (`(?:ab|b)` is in the population) but because reverse
ambiguity over the admitted shapes always presents as an alternation whose
branches share a first byte, which is exactly what `rd_alt_disjoint` tests.
Removing BOTH diverges immediately: on `":abb:ab"` the rung build answers `(5,6)`
where replication answers `(1,2)`.

The mechanism is worth stating, because it also says when the redundancy would
END. §1.1's scope bounds exclude ranged nested quantifiers, nullable bodies and
assertions, so every remaining source of a reverse follow-set conflict is an
alternation. A body admitting a ranged nested quantifier could conflict without
one — the two checks would then diverge, and the reverse unique-iteration test
would become independently load-bearing. Both are kept for that reason and
because either alone is cheap; S50 is stated as "the reverse direction is
unchecked", which is the property that actually carries the rung.

A green sabotage row is a finding about the population OR about the redundancy
of what it removed, and this one turned out to be the second — the same shape as
S48 one rung up, reached from the other direction.

### 1.1 The four additional scope bounds, each with its reason

1. **No assertion in the body** (`A_BOL`/`A_EOL`). The Glushkov model skips
   them, which is sound-in-the-right-direction for a FORWARD-only argument
   (`possessify.c`'s note, R24 H4) and is not re-derived here for a backward
   walk. Declining costs a rare shape and keeps the reverse argument the same
   argument as the forward one. RESIDUAL.
2. **A nested `A_REP` in the body only when `rmin == rmax >= 1`.** A fixed count
   is literal replication, which the reverse emitter mirrors by emitting the
   reversed sub-body that many times. A ranged or unbounded nested quantifier
   would need the reverse emitter to reproduce a whole second ladder backwards.
   RESIDUAL.
3. **Single level: an `A_REP` inside another `A_REP`'s body declines.**
   `eng_brep_design.md` §8 item 4 names nested bounded repeats as the largest
   unexplored corner and §3.4's capture derivation is explicitly single-level.
   The brief rules this bound; it is taken as ruled, not re-argued. RESIDUAL.
4. **At most `VM_MAX_BODY_CAPS` capturing groups in the body**, because the
   capture recovery holds one span pair and one seen-flag per body group in
   emitted LOCALS. Same bound and same reason as the cursor rung's own
   (`vm_cursor_fits`): a group the table could not hold would report UNSET on a
   match it participated in, which is a silent wrong span.

### 1.2 Where the verdict lives

On the `A_REP` node, as `Ast.revbody` — the reversed body AST, non-NULL exactly
when the rung is selected. ONE field is both the verdict and the artifact the
emitter needs, so the two cannot disagree, and the three call sites that must
agree about the rung (`vm_cost_rep`, `vm_count_slots`, `vm_rep`) read one field
instead of re-running an analysis. This is `Ast.possessive`'s precedent exactly
(`src/opt/possessify.c` marks, `src/gen/emit_vm.c` acts).

The pass is `src/opt/revdet.c`, driven from `src/opt/select_engine.c` beside
`run_possessify` and for the same reason recorded there: the honest driver is
the CHOSEN ENGINE, not the `discharge` socket.

### 1.3 The ladder order this produces

Per `A_REP`, cheapest provable machinery first:

| | condition | emitted |
|---|---|---|
| 1 | `vm_cursor_fits` (deterministic fixed length) | span-loop cursor |
| 2 | `a->revbody` | **this rung: one body copy** |
| 3 | — | frames (replication if bounded) |

with **possessification as an orthogonal modifier at every rung**, exactly as it
is today for rungs 1 and 3. That placement is load-bearing rather than tidy:
the acceptance cell IS possessifiable (FIRST `{a,b}` disjoint from FOLLOW `{c}`
over a unique-iteration non-nullable body — MEASURED, `--emit-ir` stamps
`possessive` at N=60), and possessification alone does NOT save it, because
`vm_poss_chain` still emits one copy per optional repetition. A possessified
revdet loop is strictly the cheapest shape in the file: forward scan, no retreat
frame, no replication.

---

## 2. The emitted shape

Three trailed `stv` slots per rung loop, all written ONCE per loop ENTRY, never
per iteration — which is the property the whole rung exists for:

| slot | holds |
|---|---|
| `entry` | the loop's start position. The capture walk's floor. |
| `low` | the boundary after `m` iterations. The retreat's floor. |
| `hi` | the maximal boundary the scan reached. The lazy extension's ceiling. |

Three always, even where a given preference reads only two. A per-preference
count would put the same rule in three places that must agree; one uniform
number is what keeps `vm_count_slots` from drifting from the emitter, which is
that function's own documented standing hazard.

### 2.1 The forward scan (both preferences share it)

```
L_entry:   RX_SET(entry, pos); RX_SET(low, pos)      ; low is fixed up below when m > 0
           it_ = 0
L_scan:    if (it_ >= n) goto L_full                 ; bounded only
           mark_ = w->btn
           PUSH(L_short, pos)                        ; this iteration cannot run -> leave
           <body>                     -> L_bodyok
L_bodyok:  w->btn = mark_                            ; CUT: the iteration is committed
           it_++
           if (it_ == m) RX_SET(low, pos)
           goto L_scan
L_short:   if (it_ < m) goto fail                    ; the minimum is unreachable
L_full:    RX_SET(hi, pos)
```

Three things about it.

**The cut is the possessive cut, applied per ITERATION rather than per copy**,
and it is licensed by (U1)+(U2): once the body has matched `[p,q)` there is no
other way to match an iteration there, so its internal choice points are dead.
It discards the body's own frames AND the `L_short` frame, which is what makes
the resume stack O(1) in the iteration count instead of O(n). Frames are still
cut at an iteration BOUNDARY and never inside a body — a one-unambiguous body
still needs its own frames to FIND its match (`(?:a|bc)` on `"bc"` tries `a`
first), which is `vm_poss_chain`'s own recorded lesson.

**`it_` is a plain local and is only ever read where it is provably live.** The
`it_ < m` test sits at `L_short`, reached by falling out of the scan, and NOT at
the commit label — which is re-entered later by a retreat, at a point where an
outer backtrack may have re-entered the loop and reset `it_`. Every other test
the commit makes is on slots or on `pos`.

**Capture writes inside the body are SUPPRESSED during the scan.** They are
what would otherwise make the trail grow per iteration, and they are redundant:
§3.4's derivation recovers every one of them from the committed span. For a
body with no other slot writes — the acceptance cell — the loop's whole trail
cost is the three entry writes.

### 2.2 Commit, retreat and the backward walk (GREEDY)

```
L_commit:  ; pos = B, a boundary, entry <= low <= B <= hi
           walk backward from B (see 2.4): sets prev_, and rvc_[]/rvs_[]
           if (B > stv[low] and prev_ valid) PUSH_AT(L_commit, prev_)
           publish captures from rvc_/rvs_        ; AFTER the push
           goto next
```

The retreat frame RESUMES AT `L_commit` ITSELF, carrying the retreat target as
its recorded position — so the resume arrives with `pos` already at the previous
boundary and re-derives everything from it. This is the cursor rung's ruled
re-push discipline (D44/R21 E-4) one rung down: never more than one live frame
per loop at any instant, though the loop may be re-entered (k − m) times across
a match, because each re-push replaces the frame that was just popped.

Publishing captures AFTER the push is not cosmetic. The frame's trail mark must
sit BELOW those writes so that every retreat rewinds the previous commit's
capture values rather than accumulating them — the cursor rung states the same
ordering rule for the same reason.

### 2.3 LAZY

Same scan (it computes `hi`), then commit at `low` and EXTEND on backtrack:

```
L_commit:  pos = stv[low]  (first arrival only; a resume arrives with pos set)
           ... same walk / push / publish, with the frame resuming L_ext ...
L_ext:     if (pos >= stv[hi]) goto fail        ; the n cap, positionally
           <body, second copy>   -> L_extok
L_extok:   cut to the extension's mark; goto L_commit
```

The `n` cap is enforced **positionally** against `hi` rather than by a counter,
which is what keeps lazy free of a per-extension trailed counter — `hi` is
already the boundary the scan stopped at, and the scan stops at `n` or at the
first body failure, so `pos >= hi` is exactly "no further iteration is
available". Cost: a second forward copy of the body, a constant factor, not a
replication.

### 2.4 The backward walk — one mechanism, two jobs

Run at every commit, over the reversed body emitted ONCE:

```
           for j in body groups: rvs_[j] = 0
           nseen_ = 0; prev_ = -1
L_walk:    if (pos <= stv[entry]) goto L_walkend
           wmark_ = w->btn; PUSH(L_walkend, pos)
           <reversed body>   -> L_walkstep
L_walkstep: w->btn = wmark_
           if (prev_ < 0) prev_ = pos          ; the FIRST step is the retreat target
           if (nseen_ == NG) goto L_walkend
           goto L_walk
L_walkend: pos = B                             ; the walk is a derivation, not a move
```

**Why one walk and not two.** The retreat needs the previous boundary; the
captures need §3.4's backward scan over the loop's final committed span. The
first is the first step of the second, so the reversed body is emitted once and
the walk records `prev_` on its way past.

**Why it terminates and why it cannot land wrong.** Each step moves `pos`
strictly left (the body is non-nullable) and the floor is the loop's own entry
slot. Reverse unique-iteration makes each step's landing the only body match
ending there, and forward unique-iteration makes the chain from `entry` the only
decomposition — so the walk retraces exactly the boundaries the scan produced.

**Captures, per §3.4's corrected two-clause derivation.** In the reversed body,
`A_CAP` writes the group's END at its right edge and its START at its left, into
LOCALS, under a per-group `seen` guard; the open sets `seen`. Going backward,
the FIRST time a group is witnessed is the LAST iteration that ENTERED it, which
is precisely PCRE2's rule and precisely the thing the plan row's constant-offset
formula got wrong on 1,799 of 15,036 matches. The walk stops early once every
body group is witnessed. Groups never witnessed are never published, so their
PREVIOUS value stands — which delivers §3.4's **ZERO-ITERATION clause** as a
special case rather than as an extra branch: at `B == entry` the walk takes no
step, publishes nothing, and every body group reports what it held before the
loop (unset, in the motivating cell).

Writing to locals and publishing after the push, rather than writing through
`RX_SET` during the walk, is what keeps the trail cost at ≤ 2 entries per body
GROUP per commit instead of per iteration.

### 2.5 POSSESSIVE

No retreat frame and no extension: the scan commits at `hi` and that is the
whole loop. The walk still runs when the body has groups, because the captures
still have to be derived. Greedy and lazy collapse into one shape, for the
reason `vm_cursor_rep` already records: under a positive §2.2 verdict a lazy
loop is forced to the same maximal exit a greedy one tops out at.

---

## 3. What this costs, stated so the stamps can be checked against it

| | frames | trail |
|---|---|---|
| per LOOP | 1 (0 possessified) | 3 slot writes + ≤ 2·NG per commit |
| per ITERATION | **0** | the body's own non-capture slot writes |

`vm_cost_rep`'s revdet arm therefore sets `pf = 0` — frames do not grow with the
iteration count, which is the rung's headline — and keeps `pt` at the body's own
per-iteration trail cost, which is 0 for a body whose only writes were captures
(they are suppressed) and non-zero for a body with a nested quantifier owning
slots. That second case still earns an honest `subject_ceiling`; saying so is
the same honesty `vm_cost_rep`'s possessive arm already carries about the trail.

---

## 4. Observability and controllability (D46, D47.3)

- A fourth `VmRungKind`, `VM_RUNG_REVDET`, bit `0x8`, name `revdet`. It joins
  `<PREFIX>_VM_RUNGS` and `--emit-ir`'s `RUNGS` section through the SAME
  `vm_rung_mark()` call every other rung goes through, so the mask, the listing
  row and the emitted machinery are one decision reported three ways.
- `-fno-revdet` / `PCREC_NO_REVDET`, the second member of D47.3's deny family
  after `-fno-possessify`, spelled the same way and documented the same way: a
  TESTING AND TUNING axis, not a user feature. Denying it drops each quantifier
  one rung to frames, which is the shipped semantics, which is what makes the
  differential possible.
- Do-or-die is asserted against the STAMP: under `-fno-revdet` the `REVDET` bit
  must not appear in any artifact, and a check reads the artifact rather than
  trusting that the flag was passed.
- `rx_info.flags` masks `PCREC_NO_REVDET` out, like `PCREC_NO_POSSESSIFY`: a
  strategy denial changes what the artifact DOES by exactly nothing, and
  stamping it would destroy the byte-identity gate that is the rung's own safety
  argument.

---

## 5. The residual, collected

Bodies that stay on frames, each with the reason:

1. reverse-ambiguous (`(?:ab|b)`, `(a|ab)`) — the boundary-record rung's class.
2. forward-ambiguous (`(aa?)`, `(a|ab)`) — the frames rung's class proper.
3. nullable bodies — no chain (§2.3 step 2 needs strict increase).
4. an assertion in the body (§1.1 item 1).
5. a ranged or unbounded nested quantifier in the body (§1.1 item 2).
6. an `A_REP` nested inside another `A_REP`'s body (§1.1 item 3).
7. more than `VM_MAX_BODY_CAPS` groups in the body (§1.1 item 4).
8. the step budget still cannot see a loop that performs no resumptions — the
   possessify lane's owed item (1), INHERITED here rather than fixed: a
   possessified revdet loop charges no steps for the same reason a possessified
   cursor loop does not. Fix of record is unchanged (an E-5-shaped one-step
   charge per loop entry, owed with the counter-K step).

---

## 6. Open direction the manager may want to rule

**Uniform application, with no count threshold.** The rung fires on every
qualifying quantifier, including `((a)|b){0,3}` where three replicated copies
are plausibly cheaper than the scan-plus-walk machinery. The case for uniform:
D18 says a tuning axis must earn itself and no measurement exists yet; a
threshold would also make the rung fire only on shapes nobody writes by hand,
which is the D46 scenario about a strategy that quietly stops being tested. The
case against: the blast radius on the corpus is much larger, since every small
choice-bearing bounded repeat changes its emitted C. Built uniform; a threshold
is a one-line change in `src/opt/revdet.c` if a measurement ever asks for one.
