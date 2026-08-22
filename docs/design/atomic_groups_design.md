# Module `atomic-groups` — design

**[M6.4.1], the design gate.** `(?>...)` and the possessive-quantifier
spellings `*+` `++` `?+` `{n,m}+` (including `{n}+`, `{n,}+` and `{,n}+`) as
SEMANTICS — an unconditional cut, not a proof-gated optimisation. The existing
`src/opt/possessify.c` is this module's MECHANISM LIBRARY, not its feature.

Charter: `../dev/plan.md`'s `[M6.4]` row and its `[M6.4.1]` substep, plus
Frank's 2026-08-12 companion note (same file, under the M4 design notes).
Written to be attacked: the R30 panel found two HIGH defects in
`assertions_design.md`, and §14 below is this document's own list of where to
start.

---

## 0. How to read this

### 0.1 Claim marking

Adopted verbatim from `assertions_design.md` §0.1, which took it from
`engine_m4.md` §0.1, so the panel reads one vocabulary:

- **MEASURED** — a number or behaviour from an instrument, with its source
  cited. If the source is not cited it is not MEASURED.
- **PROTOTYPE** — measured, but on code that is not pcrec's. Says what a
  proposed shape does, never what the compiler does.
- **RULED** — settled by a D-number in `../dev/decisions.md` or by a plan-row
  ruling of Frank's. Consumed here, not re-litigated.
- **STRUCTURAL** — true by inspection of code that exists today, file and line
  cited. Weaker than MEASURED (no instrument ran), stronger than ARGUED.
- **ARGUED** — the author's reasoning, unmeasured. Every ARGUED claim in a
  load-bearing position is repeated in §14 with the experiment that refutes it.

Every premise below was re-verified against **this worktree's HEAD build**
(`build/pcrec`, `lane/agdesign`), not inherited from the documents that state
it, and the compiler-side ones are re-verifiable by a read-only critic:
`probes/probe_premises.sh`, archived as `out/premises.txt`. Where a
re-verification moved a number, the movement is recorded inline.

### 0.2 The design in one paragraph

An atomic group is a **cut**: at the moment its body first succeeds, every
choice point the body created is discarded, so the group can never be re-run
with a different answer. pcrec's VM already has that operation —
`RX_CUT(slot)`, emitted by `vm_cut` (`src/gen/emit_vm.c:1726-1737`), built for
[ENG-BREP]'s possessification — and **this module needs no new VM primitive**:
§3 shows the one invariant people worry about (the cut does not rewind the
trail) is *independent of the proof that licenses today's cuts*, and §3.4
runs a prototype on the emitted machinery to check it. What the module DOES
need is three things that are not the cut: a **node kind** (`A_ATOMIC`) so
every pass in the compiler is forced by `-Wswitch` to say what it does with
one (§3.2, MEASURED at 15 diagnostics across 6 files); a **correction to the
hybrid**, because the DFA prefilter necessarily runs the UNCUT language and
its span END is therefore not a bound on the cut match's end — MEASURED at
**122 refuting cells** (§4), and today's emitter feeds exactly that end to the
VM as an MRL pruning ceiling; and an **engine split** in which a
cut is VM-forcing *unless it is provably a no-op*, the free discharge, whose
condition is possessify's own §2.2 verdict and which is MEASURED sound at 0
violations over 532 positive-verdict patterns (§5). The full DFA cut
construction (Berglund et al.) is CHARTERED here as a follow-on row, not
built.

### 0.3 Measurements this lane produced

All under `atomic_groups_measurements/`, probes committed, outputs archived
with their repo commit by `probes/archive.sh` (the ONLY writer of `out/` —
R30 M7's rule, inherited).

| instrument | kind | what it answers |
|---|---|---|
| `probes/probe_atomic_semantics.py` | MEASURED, both oracles | the interaction table as cells; **15 of 109** python-vs-libpcre2 divergences (§6, App. B) |
| `probes/probe_uncut_superset.py` | MEASURED, libpcre2, sweep | which of the prefilter's three outputs survive the erasure: rejection and start yes, END NO (122 cells) (§4) |
| `probes/probe_ceiling_shape.sh` | STRUCTURAL, in-pcrec | that today's emitter really does feed the prefilter's span end to the VM as a ceiling, with both negative arms (§4.2) |
| `probes/cut_proto.c` + `probes/probe_cut_trail.py` | PROTOTYPE, checked vs libpcre2 | that the proposed lowering computes PCRE2's answers, 14/14, **9 non-vacuous** (§3.4) |
| `probes/probe_free_discharge.py` | MEASURED, in-pcrec + libpcre2 | the free discharge: 0 violations / 532 positive-verdict patterns, and what it rescues (§5.3) |
| `probes/probe_possessify_under_cut.py` | MEASURED, in-pcrec + libpcre2 | that possessify's verdict survives a cut in all four quantifier positions: 0 / 48,000 (§6.4) |
| `probes/probe_premises.sh` | MEASURED, in-pcrec | §1's premise table and §6.3's error shapes, as one re-runnable script |
| `probes/probe_rk_alarm.sh` | MEASURED, self-restoring | that a fifth `RegKind` raises **NO** build alarm (§7.3) |
| `assertions_measurements/probes/probe_wswitch_alarm.sh` | **re-run, not rebuilt** | that a new `AKind` raises 15 (§3.2) |

The last row is deliberately a RE-RUN of another lane's instrument rather than
a copy: `assertions_measurements/CLAUDE.md` records why (a lane that rebuilds
the probe it is checking cannot detect that the original moved). Its output is
archived here as `out/wswitch_alarm_rerun.txt`.

---

## 1. Premises, re-verified on HEAD

| # | premise | verified how | result |
|---|---|---|---|
| P1 | `(?>` refuses, naming module `atomic-groups` | `probe_premises.sh` | `pcrec: (?>...) requires module 'atomic-groups' (pattern offset 0)` |
| P2 | the possessive suffix refuses, naming the same module, from OUTSIDE the registry | `src/parse/parse.c:987-988`; `probe_premises.sh` | `pcrec: possessive quantifier requires module 'atomic-groups' (pattern offset 2)` / `(pattern offset 5)` — the `+` in both cases |
| P3 | `{,n}` is ALREADY a quantifier in pcrec's base tier | `probe_premises.sh` | **match 0 3** — the quantifier reading, agreeing with PCRE2 10.46 and python 3.14 |
| P4 | `RX_CUT` does not touch the trail | `src/gen/emit_vm.c:4791-4793` (and the `--trace` twin at `:4823-4826`) | `run->resume_depth = slot_values[slot]`, one statement |
| P5 | the fail label rewinds the trail to the POPPED FRAME's mark | `src/gen/emit_vm.c:5071-5079` | `while (trail_depth > frame.trail_mark) { … }` |
| P6 | the emitted search loop already retries at later starts and RE-ASKS the prefilter | `src/gen/emit_vm.c:5169-5182`, `:5240-5256` | `attempt_position++` then the recompute block, verbatim in an emitted artifact (`out/ceiling_shape.txt`) |
| P7 | the artifact STAMPS which MRL ceiling it uses | `#define RX_VM_PRUNE_CEILING` | `"prefilter-window"` by default, `"subject-end"` under `-fno-prefilter` / `--engine=vm` |
| P8 | `--engine=dfa`'s VM_ONLY-construct refusal branch exists and has run | `src/opt/select_engine.c:321-335` | shipped, first used by `\K` ([M6.2] wave E) |
| P9 | possessify only ADDS marks and never reads `possessive` in its analysis | `src/opt/possessify.c:631-635` | `if (verdict && !a->possessive)`; no other read |
| P10 | revdet CLEARS `possessive` on its reversed copy | `src/opt/revdet.c:179` | `n->possessive = false;` — §6.5's hazard |

---

## 2. The mechanism, stated once

The VM's mutable state is two stacks (`engine_m4.md` §2.4), and the emitted
declarations are `src/gen/emit_vm.c:4672-4673`:

```c
rx_frame  resume_stack[RX_RESUME_FRAMES];
rx_trail_entry trail[RX_TRAIL_FRAMES];
unsigned  resume_depth, trail_depth;
```

Three operations move them, quoted from an emitted artifact:

```c
#define RX_SET(slot_, v_)  do { RX_TRAIL(slot_); slot_values[(slot_)] = (v_); } while (0)
#define RX_PUSH(lbl_, p_)  do { … resume_stack[resume_depth].trail_mark = trail_depth; resume_depth++; } while (0)
#define RX_CUT(slot_)      do { resume_depth = (unsigned)slot_values[(slot_)]; } while (0)
```

and one undoes them, at the fail label:

```c
const unsigned frame_index = --run->resume_depth;
scan_position = run->resume_stack[frame_index].resume_position;
while (run->trail_depth > run->resume_stack[frame_index].trail_mark) {
    run->trail_depth--;
    slot_values[run->trail[run->trail_depth].slot_index] = run->trail[run->trail_depth].saved_value;
}
goto *run->resume_stack[frame_index].resume_label;
```

Every fact in §3 is derived from those four blocks and nothing else.

---

## 3. (i) The VM lowering of an UNCONDITIONAL cut

### 3.1 The invariant, and why it does NOT rest on possessify's proof

`vm_cut`'s own comment (`src/gen/emit_vm.c:1672-1687`) states the
no-trail-rewind rule and gives two reasons for it. **They are different
reasons, and only one of them is possessify's.**

> "It truncates the resume stack back to the depth recorded in `slot` …
> That is exactly what a positive §2.2 verdict licenses: no retreat into this
> loop can produce a match the preferred path does not, so those frames are
> provably dead."

That is the licence for DISCARDING THE FRAMES, and an atomic group does not
have it — an atomic group discards frames that are *not* dead, which is
precisely the semantics. The comment then continues:

> "IT DOES NOT TOUCH THE TRAIL, and must not. The frames are dead; the capture
> writes they would have rewound are NOT … A frame below the cut carries a
> trail mark from before the loop ran, so unwinding to it still rewinds
> everything the loop wrote."

That second paragraph mentions the §2.2 verdict nowhere, and it does not need
to. Stated as the invariant it is (**STRUCTURAL**, from §2's four blocks):

> **CUT-INV.** Let `M` be the resume depth at the moment the atomic group is
> entered, and `T0` the trail depth at that same moment. Every frame `F` with
> index `< M` was pushed before `T0`, so `F.trail_mark ≤ T0`. Every trail entry
> the body writes has index `≥ T0`. `RX_CUT` sets `resume_depth = M` and leaves
> `trail_depth` where the body left it. Therefore any later pop of any frame
> below the mark still satisfies `trail_depth > F.trail_mark` for every one of
> the body's entries, and unwinds them all.

Each of the three clauses is checkable against the four blocks:

- *frames below `M` were pushed before `T0`* — the frames at indices `< M` are
  exactly the frames present at ENTRY, so they were pushed before entry and
  therefore before `T0`. None of them can be OVERWRITTEN while the group runs:
  every push during the body happens at index `≥ M`, because `RX_PUSH` is
  monotone in `resume_depth` and the only things that lower it are a pop (which
  leaves the group entirely if it goes below `M`) and an inner `RX_CUT` (whose
  mark is `≥ M`, §3.3 property 2);
- *`F.trail_mark ≤ T0`* — `RX_PUSH` records `trail_mark = trail_depth` at push
  time and `trail_depth` is monotone between pops;
- *the unwind is `>`, not `==`* — `src/gen/emit_vm.c:5076`.

So the invariant holds for an UNCONDITIONAL cut for exactly the reason it holds
for a proved one, and **`vm_cut` is reusable unchanged**. That is the single
most load-bearing claim in this document; §14 names its refutation.

**What would refute it:** a lowering in which the mark's own `RX_SET` runs
AFTER some push inside the body, or in which the atomic group is entered on a
path that skips the mark-set. Both break clause 2, and §3.3 turns both into
checks.

### 3.2 The spelling: a NODE KIND, not a flag

> **R31 D2 REFUTED THE PRECEDENT THIS SECTION CITED, AND NOT THE CONCLUSION.**
> The first revision said `assertions_design.md` §8.3 "settled the same
> question" and produced a house rule for node kinds. It did the opposite:
> §8.3's own annotation records that **D62 chose the FLAG** for `(?m)`. The
> sentence is deleted rather than softened.
>
> **The conclusion survives on D62's own principle**, which is the right
> ground and was available all along: *node KINDS encode STRUCTURE, node
> FIELDS encode parse-resolved MODIFIER STATE.* `(?m)` is a modifier — it
> changes how one assertion is evaluated and nothing else about the tree's
> shape. Atomicity is not a modifier: it changes the LANGUAGE (`(?>a*)a`
> matches nothing where `a*a` matches), it changes the BACKTRACKING (frames
> that would have been retried are discarded), and it is a bracketing
> construct with a body. By D62's own test it is structure. Two further
> supports, both this lane's and both measured: §6.5's revdet finding (a
> field is CLEARED by `rd_node` on the copy the emitter walks) and the
> 15-diagnostic measurement below. RULE 1 is now in §14 as an ARGUED claim
> with its refutation, which is where a conclusion whose first justification
> was wrong belongs.

The measurement that supports it. Re-run of `assertions_measurements`'
instrument (`probe_wswitch_alarm.sh`, output `out/wswitch_alarm_rerun.txt`,
**MEASURED**):

> a new `AKind` enumerator produces **15 `-Wswitch` diagnostics across 6
> files** — `src/gen/emit_vm.c` ×5, `src/opt/revdet.c` ×4,
> `src/opt/possessify.c` ×3, `src/ir/nfa.c`, `src/opt/mrl.c`,
> `src/opt/altcls.c` ×1 each. Under `make strict` each is a build failure.
> Adding a struct FIELD produces **zero** diagnostics anywhere.

Two of those fifteen are `src/opt/revdet.c:93` (`rd_shape`) and
`src/opt/revdet.c:185` (`rd_reverse`) — which are, by §6.5, precisely the two
places an atomic node must DECLINE or the module ships a miscompile. The
compiler naming them is the whole argument.

**RULE 1. `A_ATOMIC` is a new `AKind`, with `l` = the body.** Both surface
spellings parse to it: `(?>X)` directly, and `X q+` as `A_ATOMIC(A_REP(X))`,
which is PCRE2's own definition of the possessive suffix (`X*+ ≡ (?>X*)`).

> **R31 E6 REFUTED THE MEASUREMENT THAT SUPPORTED THE DESUGARING, AND THE
> RE-MEASUREMENT SUPPORTS IT.** The first revision cited "section B, 8 spelling
> pairs, both oracles agreeing on all 8" — and **every row in section B has
> body `a`**, a body with a unique iteration, where per-iteration and
> group-exit cutting CANNOT differ. It measured the equivalence on the one
> family that could not refute it.
>
> `probe_atomic_semantics.py` now carries a dedicated
> `spelling_equivalence()` check over bodies whose iteration can end in two
> places (`(?:a|ab)`, `(?:ab?)`, `(?:a|bc)`, nullable `(?:a*)`, `(?:a?)`):
> **18 pairs, 47 cells, 28 of them NON-UNIQUE-BODY cells, 0 disagreeing**
> (`out/atomic_semantics.txt`). It FAILS if the non-unique-body count is zero,
> so it cannot silently become the old vacuous check again. The desugaring
> holds on the population that could have refuted it.

**RULE 2. The module never writes `Ast.possessive`.** That field keeps exactly
its current meaning: possessify's optimisation mark, deniable by
`-fno-possessify`, and CLEARED on revdet's reversed copy
(`src/opt/revdet.c:179`, premise P10). Storing the module's semantics there
would make **`-fno-possessify` a miscompiler** and would let a copy constructor
delete a language feature. §11 gives both a sabotage row.

**RULE 3. The possessive-rung LIFT — REWRITTEN AFTER R31 E1, E2 AND E4, WHICH
REFUTED ITS FIRST FORM ON THREE SEPARATE COUNTS.** What the first revision said
was: emit `A_ATOMIC(A_REP(X))` through "the existing possessive rungs
(`vm_poss_star`, `vm_poss_chain`, `vm_counter_poss_opt`)", same answers, and
the decision is local to the emitter so nothing can lose it. Each clause was
wrong, and the corrected rule is below the evidence.

#### 3.2.1 `vm_rep` has FIVE dispatch paths, not three — MEASURED

`vm_rep` (`src/gen/emit_vm.c:3458-3492`) tries the cursor rung, then revdet,
then the counter rung, then falls through to the frames rung, whose bounded and
unbounded arms are different code. Driving a pattern possessify's SHIPPED
verdict marks down each one (`probes/probe_cut_dispatch.sh`,
`out/cut_dispatch.txt`, all `--engine=vm --no-captures`, `strats=0x1` on every
row):

| rung | witness | `RX_CUT(` call sites | second spelling | mark slot | what actually happens |
|---|---|---|---|---|---|
| CURSOR `0x1` | `a*b` | **0** | 0 | 0 | **FRAMELESS.** `vm_cursor_rep` sets `low`, `retry` and `again` to `-1` when possessive (`:2026-2027`): no slot, no labels, no push. There is nothing to cut |
| FRAMES_BOUNDED `0x2` | `(?:ab\|b){1,3}c` | 3 | 0 | 2 | `vm_poss_chain`, one cut per copy boundary |
| FRAMES_UNBOUNDED `0x4` | `(?:ab\|b)*c` | 1 | 0 | 2 | `vm_poss_star` — see §3.2.2 |
| REVDET `0x8` | `(?:a\|bc)*d` | **0** | **1** | 0 | cuts in the SECOND SPELLING — see §3.2.3 |
| COUNTER, bounded `0x10` | `(?:ab\|b){8,12}c` | 5 | 0 | 2 | `vm_counter_poss_opt` / `vm_poss_chain` |
| COUNTER, **unbounded** `0x10` | `(?:ab\|b){8,}c` | **0** | **0** | **2** | **K29. NO CUT AT ALL** |

**So the corrected requirement is not "every path ends in a cut" — that is
wrong for the cursor rung, whose right answer is to emit no cut because it
pushes nothing.** It is:

> **RULE 3 (corrected). Every dispatch path a SEMANTIC possessive can take must
> be CUT-EQUIVALENT: it either emits a cut (in EITHER spelling), or it provably
> pushes no frame a cut would have removed. `[M6.4.2]` owes ONE STRUCTURAL
> CHECK PER PATH, driven by the six witnesses above, and each check names which
> of the two answers that path gives.**

#### 3.2.2 The nullable carve-out — E1, and the first form would have HUNG

`vm_poss_star`'s header (`src/gen/emit_vm.c:2483-2492`) states its own
precondition and says why it is not an omission:

> "NO EMPTY-ITERATION GUARD IS NEEDED, and that is structural rather than an
> omission. §3.3's guard exists to stop a NULLABLE body iterating forever;
> §2.2's rule refuses to possessify a nullable body at all … So
> `a->possessive` on an unbounded repeat implies `!vm_nullable(a->l)`."

**A user-written possessive deletes that antecedent.** `(?:a*)*+`,
`(?:a?)*+b`, `(?:|a)*+`, `(?:a*)++` and `(?>(?:a*)*)b` are all legal, all
answered by both oracles, and all have nullable bodies. Routed onto
`vm_poss_star` they would push and cut at zero consumption forever, and no
work charge fires to stop them. **RULE 3 therefore carries an explicit
carve-out: a nullable body takes the GENERAL §3.3 shape — mark, `vm_star`
WITH its empty-iteration guard, exit cut — never the lift.** And
`vm_poss_star`'s precondition stops being a comment: `[M6.4.2]` turns it into
a CHECKED assertion at the top of the function, because a precondition that a
new caller can silently violate is the shape this whole finding is made of.

#### 3.2.3 There are TWO spellings of a cut, and only one is `RX_CUT`

`vm_revdet_rep` cuts by assigning `run->resume_depth = <prefix>_rvN_frame_mark`
(`src/gen/emit_vm.c:2833` and `:2966`) and its own comment says it "never goes
near the RX_CUT macro". `vm_cut`'s header records what that cost once: a
step-charge probe "reported a confident zero for the revdet rung because the
first version instrumented only the `RX_CUT` macro". **MEASURED here on
`(?:a|bc)*d`: 0 `RX_CUT(` call sites, 1 second-spelling cut, and the rung is
correct.** Every structural check this design proposes (§11.3) matches both
spellings; a check that matched only `RX_CUT` would inherit that same zero.
The revdet rung also cuts UNCONDITIONALLY — the assignment is not gated on
`a->possessive` — so a semantic possessive routed there is safe on the cut
axis. It is NOT safe on the frame axis: see E4 below.

#### 3.2.4 K29 — the path that emits no cut at all

`vm_counter_fits` accepts an unbounded repeat when `rmin >= K` (`:695`), and
`vm_counter_rep`'s unbounded arm (`:3355-3358`) hands the tail to `vm_star`,
which never reads `a->possessive`. MEASURED: `(?:ab|b){8,}c` is stamped
POSSESSIVE, allocates and writes `RX_SLOT_CUT_MARK0`, and emits neither
spelling of a cut. Today that is observability only (possessification is
proof-gated, so the cut it fails to emit would have discarded provably-dead
frames) — `known_issues.md` **K29**, opened by this panel. Under RULE 3 it
becomes a MISCOMPILE: a semantic `X{n,}+` through that arm answers the UNCUT
language. **The K29 fix travels with [M6.4.2]** — emit the exit cut in the
unbounded tail — and it is a fix to code that predates this module.

#### 3.2.5 E4 — the lift cannot be a purely local emitter decision

The first form said "nothing is written to the tree, so no flag and no copy
can lose it". That is true of the TREE and false of the EMITTER: `->possessive`
is read at **23 sites across 8 functions** (`grep -n -- '->possessive'
src/gen/emit_vm.c`), and three of them are PRE-PASSES that must agree with
emission exactly or the artifact is malformed rather than merely slow:

- **`vm_count_slots`** (`:1478`, `:1536`, `:1545`, `:1557`) allocates the
  cut-mark slot. A lift it cannot see means `vm_slot_mark(v, v->nmark++)` runs
  past `RX_NSLOTS` — an out-of-bounds write in EMITTED code, K27's class.
- **`vm_cost_rep`** (`:1120`, `:1241-1242`) computes the frame and trail
  budgets from the possessive branch.
- **`vm_counter_copies`** (`:717`) and **`vm_rev_canmove`** (`:975`).

And `vm_rev_canmove` is the sharpest: it returns `!a->possessive && …`, so
under RULE 2 (the module never writes that field) a lifted possessive on the
revdet rung is given a retreat frame and **can give back — the uncut
semantics**. §6.5 rules that `rd_shape` declines on `A_ATOMIC`, which closes
the plain-group case; the LIFTED case reaches `vm_rev_canmove` through the
A_REP, so it needs the predicate below and not only the decline.

> **RULE 3 (corrected, second half). ONE NAMED SHARED PREDICATE.** `[M6.4.2]`
> adds `vm_cuts(const Ast *a)` — "this quantifier is cut at its boundaries",
> true when `a->possessive` (possessify's mark) OR when the emitter's walk has
> it under an `A_ATOMIC` lift — and **the emitter and all four pre-passes call
> it instead of reading the field.** `src/gen/CLAUDE.md`'s one-call-one-truth
> rule, and `vm_cut`'s own header gives the precedent: the work charge became a
> primitive because "the charge has THREE emission sites in two different
> spellings" and a probe missed one.

#### 3.2.6 What survives of RULE 3's motivation

The reason for the lift is unchanged and still measured: `vm_star`'s frames
rung pushes one frame per iteration, so a naively-lowered `(?>a*)` exhausts
`RX_RESUME_FRAMES` where `a*+` does not — two spellings PCRE2 calls identical
with different `subject_ceiling`s. The lift is worth having; what R31 refuted
is the claim that it is free.

### 3.3 The emitted shape

For the general body (`A_ATOMIC` over anything that is not an `A_REP`), one new
emitter function, `vm_atomic`, in `src/gen/emit_vm.c`'s existing vocabulary
(`src/gen/CLAUDE.md`'s two rules apply: the mark slot joins the existing
`SLOT_CUT_MARK<n>` family — `src/gen/emit_vm.c:639` — so it is greppable, and
it is spelled in ONE place):

```
L_entry:  RX_SET(SLOT_CUT_MARKk, (ptrdiff_t)run->resume_depth)   /* BEFORE any push */
          goto L_body
L_body:   <body>                       -> L_cut       /* ordinary emission, ordinary frames */
L_cut:    RX_CHARGE_WORK((ptrdiff_t)run->resume_depth - slot_values[SLOT_CUT_MARKk]);
          RX_CUT(SLOT_CUT_MARKk);
          goto L_next
```

which is `vm_cut(v, mark, role)` verbatim — the work charge is already inside
it (`src/gen/emit_vm.c:1728-1735`) and its accounting rule is unchanged here:
"pushed, then CUT → CHARGED, at every cut: the frames being discarded were
never popped through `rx_fail`, so nothing counted them." An atomic group's
discarded frames are in exactly that category.

Three properties of that shape, each with the line that makes it true:

1. **The mark's `RX_SET` precedes every `RX_PUSH` in the body**, which is
   clause 2 of CUT-INV. It also makes the mark itself TRAILED, which is what
   makes NESTING and RE-ENTRY work: an outer backtrack restores the mark slot,
   and the group's entry label re-sets it on every entry. `vm_set`
   (`:1663-1671`) is the trailing writer, and the existing possessive sites
   already use it for their marks (`:3335`, `:3552`).
2. **`RX_CUT` is an assignment, not a `min()`** (`:4791-4793`). It is therefore
   only correct if `resume_depth ≥ mark` at every cut site. That holds because
   control cannot reach `L_cut` after a pop below the entry frame (such a pop
   jumps to a resume label OUTSIDE the group), and nested marks are monotone by
   construction. **This is the sharpest thing in the lowering** and §11 gives it
   a structural check rather than a comment.
3. **Nothing rewinds the trail.** Captures written inside the body are RETAINED
   on success (measured: `(?>(a)|ab)` on `"ab"` is `(0,1)` with group 1 = `(0,1)`,
   `out/atomic_semantics.txt` section I) and UNDONE on an outer failure
   (`((?>(a)|ab))c|(abc)` on `"abc"` is `(0,3)` with groups 1 and 2 UNSET and
   group 3 = `(0,3)` — same file, same section).

### 3.4 The prototype, and what it is worth

`probes/cut_proto.c` hand-lowers five atomic patterns onto the emitted VM's own
machinery — the four macros and the fail label copied VERBATIM from an artifact
`build/pcrec` produced — and `probes/probe_cut_trail.py` checks every row
against libpcre2.

> **R31 C6 REFUTED THIS SECTION'S EVIDENCE AND THE PROBE NOW MEASURES WHAT IT
> CLAIMED.** The first revision reported "14 rows, 0 disagreeing, 9
> NON-VACUOUS" and named `((?>(a)|ab))c|(abc)` as the row the no-trail-rewind
> question turns on. The critic injected a trail-rewinding cut into a scratch
> copy and found that **2 of 14 rows went red — both of them rows the probe
> labelled VACUOUS — while all nine advertised non-vacuous rows stayed
> GREEN.** The named row is one of the green ones.
>
> **The cause is that these are two different axes and the probe measured
> one.** *cut-vs-uncut* asks whether the cut changes the answer;
> *trail-rewind-vs-not* asks whether CUT-INV is doing any work. A row can be
> vacuous on the first and be the only thing standing between §3.1 and a
> silent capture loss.
>
> The probe now builds **BOTH ARMS every run** — `cut_proto.c` carries a
> `-DCUT_REWINDS_TRAIL` sabotage arm implementing the natural wrong cut (undo
> everything the discarded frames would have undone) — and diffs them row by
> row, so the second column is MEASURED rather than asserted. It FAILS if
> either column is zero.

**PROTOTYPE** (`out/cut_trail_proto.txt`), after the rebuild:

> **17 rows, 0 disagreeing with libpcre2; 10 discriminate CUT-vs-UNCUT and 4
> discriminate THE TRAIL INVARIANT.**

And the corrected naming, which is the part worth carrying forward:

- **The trail invariant's failing direction is RETENTION, not undo.** The four
  rows that go red under the sabotage are `(?>(a)|ab)` on `"ab"` and `"a"`, and
  `(?>(a)x|ab)` on `"ax"` and `"axb"` — a capture written inside the body on
  the path the cut commits to, which a rewinding cut erases.
- **`((?>(a)|ab))c|(abc)` does NOT discriminate it**, and the reason is worth
  knowing rather than embarrassing: that row tests the UNDO half, and a cut
  that rewinds the trail gets undo trivially right (it did the undo early).
  Only retention can catch it. The first revision named the row that tests the
  half no sabotage of the cut can break.

**What a green run does NOT mean**, stated in the probe's own header: nothing
here is pcrec's code, and if the module's real lowering differs from the shape
above this proves nothing about it. The permanent version of this evidence is
Appendix A's corpus.

### 3.5 What is NOT needed

- **No new VM primitive.** §3.1.
- **No trail-rewind variant of the cut.** A cut that rewound the trail would be
  a miscompile, not a variant; §11's S88 is its sabotage.
- **No change to the fail label.** It is already `>`-not-`==` and already
  rewinds to the popped frame's own mark.
- **No new give-up code** — but **NOT "the caps are unchanged": R31 C10 is
  right and this bullet was wrong.** The mark's `RX_SET` IS trailed (§3.3
  property 1), so an `A_ATOMIC` inside a quantifier costs one trail entry per
  entry to the group, and `vm_cost` (`src/gen/emit_vm.c:1311`, one of the
  fifteen `-Wswitch` sites) needs an `A_ATOMIC` arm that charges it. An
  uncharged trailed write is exactly the defect the SHIPPED
  `tests/mech/sabotages/S87_kreset_trail_uncharged.sh` guards for `\K`, and
  this module owes the same pairing: the `vm_cost` arm, and a CAPACITY sabotage
  row (§11.4 S94). What is unchanged is the give-up CODE SPACE and the two cap
  constants — not the arithmetic that decides when they fire.
- One further RESOURCE observation, **STRUCTURAL and reported rather than
  fixed**: because the cut discards frames but not trail entries, a
  capture-bearing atomic body under a quantifier (`(?>(a))*`) makes the TRAIL the
  binding cap where the FRAMES cap normally binds first (3072 entries at 2
  writes per iteration ≈ 1536 iterations, against 2048 frames). This is a
  shift of which cap fires, not a new failure mode, and `rx_info`'s stamped
  `subject_ceiling` reports it honestly either way. It is the one number
  [M6.4.2] should re-measure after the lowering exists.

---

## 4. (ii) THE HYBRID HAZARD — the part that can silently break

### 4.1 Why the prefilter runs the wrong language, unavoidably

The default path for a capture-bearing or VM-forced pattern is the
capture-erased forward+reverse DFA pair as a prefilter, plus the VM
(`engine_m4.md` §6.1). Frank's 2026-08-12 companion note states the trap
exactly: *"a DFA never backtracks in the first place — subset construction
keeps every alternative alive, which is exactly the NON-possessive semantics."*
So `src/ir/nfa.c`'s `A_ATOMIC` arm has only one sound choice — lower the body
transparently, i.e. build the machine for the **UNCUT** language — and the
prefilter therefore answers for a strict SUPERSET.

`engine_m4.md` §6.1's exactness claim **already excludes this module by name**:
it is stated "for a pattern whose only VM-forcing feature is capturing groups —
no backrefs, lookaround, callouts, `\K`, atomic/possessive, `\G`". This section
is what that exclusion cashes out to.

### 4.2 What the emitter does with the prefilter's two numbers, today

**STRUCTURAL**, from an artifact `build/pcrec` emitted this session
(`out/ceiling_shape.txt`, pattern `(a|bc){1,4}d`):

```c
if (rx_prefilter(subject, subject_length, search_from, window) != 1) return 0;
attempt_position = (size_t)window[0][0];
window_end = (size_t)window[0][1] < subject_length ? (size_t)window[0][1] : subject_length;
…
result = rx_match_anchored(&ctx, &run, window_end);
…
    attempt_position++;
    { … if (rx_prefilter(subject, subject_length, attempt_position, window) != 1) return 0;
        attempt_position = (size_t)window[0][0];
        window_end = … }
```

So `window[0][0]` seeds the first attempt and every retry, and `window[0][1]`
becomes `rx_window_end`, which `RX_PRUNE_TOO_SHORT` / `RX_PRUNE_CLAMP_SPAN`
(`:129-131` of that artifact) use to abandon or shorten. Both negative arms are
in the same archived output: under `-fno-prefilter` and under `--engine=vm` the
artifact emits `window_end = subject_length` and stamps
`RX_VM_PRUNE_CEILING "subject-end"`. The hazard is CONDITIONAL on the hybrid
being on, and the artifact says which form it took.

### 4.3 The measurement

`probes/probe_uncut_superset.py` generates 1,260 patterns of the shape
`PRE (?>ALT) MID | TAIL`, builds each one's twin by the two-byte `(?>` → `(?:`
edit, and runs both through libpcre2 over 14 subjects — **17,640 cells, 8,237
of them cells where both spellings match** (`out/uncut_superset.txt`,
**MEASURED**):

| rule | statement | violations |
|---|---|---|
| **R1** | uncut `nomatch` ⇒ cut `nomatch` (the prefilter may still REJECT) | **0** |
| **R2** | `start_uncut ≤ start_cut` (the start is a LOWER BOUND) | **0** |
| **R3a** | `end_uncut ≥ end_cut` (**required** for `window_end` to be a sound MRL ceiling) | **122 — REFUTED** |
| R3b | `end_uncut > end_cut` (ceiling merely loose; harmless direction) | 133 |

and, informationally, **180 cells where `start_uncut < start_cut`** — i.e.
where the emitted search loop's `attempt_position++` retry is actually reached.

The smallest R3a witness is
`(?>a|ab)c|abcd` on `"abcd"`: the atomic answer is **(0,4)**, the uncut twin's
is **(0,3)** (`out/atomic_semantics.txt` section N, both oracles agreeing).
A `window_end` of 3 prunes the (0,4) match away, silently, in the DEFAULT
engine.

> **R31 STRENGTHENED THIS FINDING BY REMOVING ITS ONE UNSTATED PROXY, and the
> result belongs here rather than in the review.** Everything above compares
> libpcre2's answer for the pattern with libpcre2's answer for the twin — which
> assumes, without saying so, that pcrec's `rx_prefilter` reports the twin's
> leftmost-first end. The `r31chk` critic compiled the capture-inserted uncut
> twin for all 46 R3a patterns and called `rx_prefilter` DIRECTLY:
> **122/122 window ends equal the uncut end, and 114 cells across 42 patterns
> carry a `"prefilter-window"` ceiling AND a window end strictly below the cut
> match's end.** That is the silent match loss, measured on the emitted
> prefilter rather than inferred from an oracle — 114 cells the default engine
> would get wrong the day this module lands without H3.

### 4.4 The rules

**RULE H1 — REJECTION stays sound, FOR EVERY PATTERN THIS MODULE CAN COMPILE.**
Because the uncut language is a superset, no uncut match means no atomic match;
an atomic match's own path is an uncut path.

> **SCOPED AFTER R31 E5, and the scope is not cosmetic.** Containment holds
> only in a POSITIVE context. Under negation a smaller inner language is a
> LARGER outer one, and the critic's witness is `(?!(?>a|ab)c)abc` on `"abc"`:
> the cut version matches `(0,3)`, the uncut version does not match at all — so
> a prefilter built from the uncut twin would REJECT a subject that matches.
> §4.3's generator contains no negated context and could not have found it.
>
> The rule is therefore: **H1 holds while every atomic group occurs in a
> positive context, which is every pattern module `atomic-groups` can compile,
> because negative lookaround is module `lookaround` ([M6.6]) and refuses
> today.** [M6.6] REOPENS H1 the way H5 reopens H4 — written down here so the
> lookaround design inherits the question instead of rediscovering it, and
> because "the prefilter may reject" is exactly the kind of rule that gets
> carried forward as unconditional once nobody remembers why it was true.
>
> **The 0-violations-in-17,640 figure is retained and re-labelled.** R31 C13
> is right that `r1_viol` can fire only on a libpcre2 bug given containment, so
> within the positive-context family the zero carries no weight; it is the
> implicit control for the sweep, not evidence for H1. The evidence for H1 is
> the containment argument plus the scope above. R2's mirror (`start_moved`,
> 180 cells) IS a real implicit control and is reported as one.

**RULE H2 — the START is a LOWER BOUND, and the mechanism that copes with that
already ships.** `window[0][0]` may be used to SEED an attempt and may never be
reported. It is already never reported: `rx_report_captures` is called with
`attempt_position` — the position the VM actually matched at — not with
`window[0][0]` (`src/gen/emit_vm.c:5256`). And the loop already advances and
re-asks the prefilter on failure (P6). **What changes is not the code but its
status**: D51 ruling 2's obligation (b) records a "STRUCTURAL argument that the
retry cannot fire" resting on span-equality between the two machines, and
deliberately does NOT rely on it — *"resting an unsound-direction correctness
property on a believed claim is what the ruling forbids"*. For a cut pattern
that argument is not merely believed, it is **false**, and the recompute the
ruling insisted on anyway is what makes the loop correct. **This is the single
best thing in this section: the correct behaviour is already shipped, because
a ruling refused to rest on an argument that has now expired.**

One PERFORMANCE consequence, not a correctness one: the recompute block is
emitted only when `v.nclamp > 0` (`src/gen/emit_vm.c:5169-5182`). A cut pattern
with no MRL clamp sites retries byte-by-byte instead of asking the prefilter
where the next candidate is. Recommendation (optional, [M6.4.2]'s call):
decouple the recompute from `nclamp` so it is emitted whenever a prefilter
exists. Correctness does not depend on it.

**RULE H3 — the END may NOT be used as an MRL ceiling on a cut-bearing
artifact. THE DIAGNOSIS AND THE PREDICATE SURVIVE R31 E3; THE SITE THE FIRST
REVISION NAMED WAS THE WRONG ONE, AND THE CHECK IT PROPOSED WOULD HAVE AGREED
WITH THE BUG.**

What the first revision said: edit `emit_vm.c:4351`'s `v.mrl_win =
job->fit.prefilter` to `&& !has_atomic(root)`, and the artifact's stamp is the
check. **MEASURED refutation:** `v.mrl_win` has exactly four occurrences —
`:418` (the declaration), `:4178` (the `--emit-ir` description text), `:4351`
(the assignment) and **`:4611` (the stamp)**. It is read NOWHERE ELSE. The
lines that actually build the ceiling are

```c
:5233   window_end = (size_t)window[0][1] < subject_length ? … : subject_length;   /* entry */
:5177   window_end = (size_t)window[0][1] < subject_length ? … : subject_length;   /* retry recompute */
```

and both are gated on `prefn` and `v.nclamp > 0`, **never on `mrl_win`**. So
the proposed edit flips the stamp to `"subject-end"` and leaves the ceiling
live — and `[M6.4-ATOMIC rule 1]` as first written asserts on the stamp, which
would then be GREEN on a matcher that is silently losing matches. *A check that
agrees with the bug is worse than no check*, and this one was derived from the
same variable the bug hides behind.

**The corrected rule, three parts:**

1. **ONE PREDICATE, THREE SITES.** `[M6.4.2]` introduces a single
   `cut_free_ceiling` predicate (`job->fit.prefilter && !has_atomic(root)`)
   and reads it at **`:5233`, `:5177` AND `:4611`** — the two emission sites
   and the stamp — so the stamp cannot disagree with the code it describes.
   `:4178`'s `--emit-ir` text reads the same predicate for the same reason.
2. **THE CHECK ASSERTS ON TWO SOURCES.** `[M6.4-ATOMIC rule 1]` (§11.3) pins
   the emitted `window_end` ASSIGNMENT TEXT — absent, or literally
   `= subject_length` — **and** the stamp. Either alone is satisfiable by a
   half-done edit; that is exactly what E3 demonstrated.
3. **THE CHECK PINS PATTERNS WITH `nclamp > 0`, AND SAYS SO — R31 C5.**
   `RX_VM_PRUNE_CEILING` is THREE-valued (`:4610-4611`): with `nclamp == 0` it
   stamps `"none"`, there is no `window_end` local and no ceiling argument at
   all. The critic measured the histogram over §4.3's 46 R3a patterns as
   **{prefilter-window 42, none 4}** — so a rule demanding `"subject-end"`
   would be RED on four correct artifacts, and the sabotage would be invisible
   on about 9% of the family. The check selects on `nclamp > 0` (equivalently:
   the artifact declares a `window_end` local) and the corpus file carries both
   populations.

Two alternatives, both rejected with reasons:

- *Keep the ceiling and widen it.* There is no cheap widening: R3a's violations
  are not bounded by a constant (`(?>ab|a)b|abcd` on `"abcd"` is cut (0,4),
  uncut (0,2) — a gap of 2 on a 4-byte subject), and any bound would have to be
  derived from the cut structure, which is the full construction §5.5 defers.
- *Turn the prefilter off entirely for cut patterns.* That discards H1 and H2
  as well, and §4.7 of `engine_m4.md` is explicit that losing the prefilter
  turns DD-2 into a regression: `(?>a*)b` over 8 MB of `a` is answered by the
  prefilter in one pass. Keeping rejection and the start seed while dropping
  only the ceiling is strictly better and costs one predicate.

**RULE H4 — the match-here entries need no change, and here is the evidence
rather than the assertion.** `assertions_design.md` §6.3 rule 3 was R30 E8's
find: the DFA artifact's `rx_match` is `rx_search` plus
`caps[0][0] != ctx->pos`, and BOTH lines break under `\K`. The correction
recorded there is that a `\K` pattern is VM-forced and so never HAS that entry.
The same is true here, and for the same two structural reasons
(`src/gen/emit_vm.c:5268-5300`): `rx_match_anchored` starts at `ctx->pos` and
never moves it, so "anchored at the requested position" is a property of the
call; and it returns `pos - ctx->pos`, computed from positions and never from
`caps`. **Additionally** — and this is the part that is this module's and not
`\K`'s — the match-here entries pass `ctx->len` as the ceiling, not a prefilter
window (D51 ruling 2 obligation (a), `src/gen/emit_vm.c:5368` (`<prefix>_match_caps` passes `ctx->pos`; the ceiling argument is `ctx->len`)), so H3's
hazard cannot reach them either. The obligation this creates is EVIDENCE, on
wave E's precedent: an entries driver (Appendix A) that runs all three entries
side by side on the cut corpus.

**RULE H5 — the day the cut construction lands (§5.5), H4 is reopened.** A
DFA-compiled atomic artifact would have the `rx_match` shape §6.3 quotes. Its
start-equality filter is CORRECT there (a true cut DFA reports the atomic
start), but the rule is written down now so the follow-on row inherits the
question instead of rediscovering it.

---

## 5. (iii) The engine split

### 5.1 What forces the VM — **REVERSED BY M-1: this module STAMPS, and SR-8 IS BUILT**

The first revision proposed a third hand-written `EngineAnalysis` row,
`forces_atomic`, on `forces_kreset`'s shape, and §8 argued for a second named
exception to `registry_check.c`'s engine-capability tripwire. **That tripwire's
own text forbids it** (`tests/registry/registry_check.c:1422-1424`):

> "If a SECOND construct arrives here, do not add a second exception: two is
> when the generic consultation has earned its axis and SR-8 is the right
> build."

`\K` is the first; `(?>` is the second. **RULED (D67): [M6.4.2] builds SR-8 in
D55's specified shape**, and this section is the stamping rule rather than a
third bespoke analysis.

**THE MECHANISM.** A module's producer stamps each AST node it creates with its
registry row's `engines` mask. ONE generic `EngineAnalysis` ANDs the stamps over
the **POST-DISCHARGE** tree; `why_pos`/`why` come from the first DFA-excluding
node's row. `forces_kreset` and the registry_check exception RETIRE INTO IT — a
deletion, not an addition. A sabotage row un-stamps `A_ATOMIC` and the
engine-selection assertion goes red.

**THE THREE CONTRACT NOTES, adopted verbatim from the [M6.5.1] lane's
read-only survey (M-1), because this module is the first customer and inherits
them:**

1. **SR-8 subsumes `forces_kreset` only — NOT `forces_captures`.**
   `select_engine.c:84-92` is a property of the generation REQUEST with no
   registry row behind it. Two kinds of forcing remain, **request-derived** and
   **node-derived**, and the `--engine=dfa` branch-ordering fix must read *"take
   the captures branch only when no NODE-DERIVED analysis contributed a why"*.
2. **Shared constructors must be decided deliberately.**
   `pcrec_ast_class_from_bits` (`parse.c` ~245, MOD-0.3c's ONE constructor for
   produced byte-sets) does not know its row: either the constructor takes the
   `RegRow`, or the port stamps after construction (silent-on-forget). It is
   not on this module's path (`A_ATOMIC` has its own producer) and the default
   stamp is `ANY_ENGINE`, so **a forgotten stamp fails in the UNSOUND
   direction** — which is precisely what the generic tripwire (every `VM_ONLY`
   row with a producer must refuse `--engine=dfa` by name) must keep catching.
3. **Discharge output must not inherit the discharged node's stamp**, or the
   fixpoint never converges to DFA with every answer still correct — the
   "changes no answer" failure shape. Rule: stamps live on NODES; a discharge
   REPLACES the discharged node (which is not copied) with a subtree whose NEW
   nodes are born `ANY_ENGINE`; **nodes copied from the body keep their own
   stamps** (copying a `\K` must keep forcing). The free discharge is
   deletion-shaped and satisfies this trivially; `[ENG-CUT]` inherits the rule.
   Sabotage row: an inherited stamp → the engine-selection assertion goes red.

**What this module owes, concretely.** `A_ATOMIC` carries an `engines` field
stamped by `src/parse/mod_atomic_groups.c` from row `registry.c:623`'s mask
(`VM_ONLY`) and from the four new `RK_QUANTSUFFIX` rows' masks (§7.4).
`first_atomic_pos` on `Ctx` is no longer needed for the verdict — the generic
analysis reports the offending NODE's row — but the module still records it,
because a node carries no source position (`forces_kreset`'s own recorded
limitation) and `why_pos` has to come from somewhere.

The `why` STRING stays per-CONSTRUCT because it comes from the ROW: `(?>a|ab)c`
says "atomic group at pattern offset 0" and `a*+b` says "possessive quantifier
at pattern offset 1", which is one more reason the possessive spellings need
rows of their own (§7.4) rather than an exemption — an exempted construct has
no row for the generic analysis to name.

### 5.2 `--engine=dfa` refuses, and needs no new code

The second branch of the override (`src/opt/select_engine.c:326-336`, the second
`ctx_fail` at `:334-335`) already does it — **with one ordering fix that comes
from M-1 contract note 1 and is this module's to make**: the branch currently
takes the CAPTURES arm whenever `cx->want_caps && cx->ncap > 0`, which on a
capture-bearing atomic pattern would advise `--no-captures`, a flag that cannot
help. Under SR-8 the rule becomes *take the captures branch only when no
NODE-DERIVED analysis contributed a `why`*. Then:

```
pcrec -p rx --features atomic-groups --engine=dfa '(?>a|ab)c'
  -> "atomic group at pattern offset 0 requires the VM engine,
      which --engine=dfa excludes"
```

This is the `\K` precedent applied verbatim (D44.6: a request the pattern
cannot honour is REFUSED, never silently downgraded), and it is the SECOND time
that branch runs without a line of it changing.

**The refusal is post-discharge, which is the whole payoff.** The override
switch runs after the analysis loop (`:264-300`), so `--engine=dfa '[^"]*+"'`
SUCCEEDS: the discharge removed the atomic node, nothing forces the VM, and the
artifact is a pure DFA. `--engine=dfa '(?>a|ab)c'` refuses. A user asking for a
DFA artifact and writing a possessive for speed gets what they asked for; a
user writing a possessive that CHANGES the language gets told so.

### 5.3 The free discharge

**THE RULE, NARROWED AFTER R31 E7.** `[M6.4.2]` ships **ONLY the
`A_ATOMIC(A_REP(X))` discharge** — the possessive spellings — whose condition is
possessify's FULL §2.2 verdict on that quantifier, unchanged, because the
verdict's entire content is *"no retreat into this loop can produce a match the
preferred path does not"*, which is exactly *"the cut deletes nothing"*.

> **The plain-group arm `(?>X)` is DEFERRED, and the first revision should not
> have shipped it.** It proposed discharging any `A_ATOMIC` whose body
> satisfies (U1) one-unambiguous and (U2) prefix-free. E7's three objections
> are all correct and all measured or structural:
> (a) **it is measured at ZERO cells** — `probe_free_discharge.py` reads the
> verdict off the non-possessive twin's `RX_VM_STRATS`, which requires a
> QUANTIFIER, so the `(?>X)` arm has no evidence at all;
> (b) **`possessify.c` exposes no callable subtree verdict** — the (U1)/(U2)
> machinery is internal to the pass;
> (c) **the run order is unspecified** — §5.4 runs the discharge BEFORE
> `run_possessify`, which itself runs only AFTER the engine is chosen
> (`select_engine.c:233-236`), so "reuse possessify's condition" names no
> reachable code.
>
> The narrowed rule is buildable today: factor a **callable verdict** out of
> `possessify.c` (the §2.2 predicate on one `A_REP`, with no marking side
> effect), call it from `pcrec_discharge_atomic`, and leave the plain-group arm
> to a follow-on row or to `[ENG-CUT]` — which subsumes it — once it has
> evidence. Deferring costs the module nothing measured; §14 item 4 keeps the
> gap named.

**THE MEASUREMENT** (`probes/probe_free_discharge.py`, `out/free_discharge.txt`,
**MEASURED, in-pcrec on one arm and libpcre2 on the other**). The verdict is
read off the SHIPPED analysis without writing any new code: compile the
pattern's non-possessive twin `--engine=vm --no-captures` and read
`RX_VM_STRATS` — `0x1` is `VM_STRAT_POSSESSIVE`, set by `vm_rung_mark` from
`a->possessive` (`src/gen/emit_vm.c:252-255`, `:1751-1753`).

> 1,764 generated patterns × 16 subjects = **28,224 cells**. **532 patterns
> with a POSITIVE verdict; 0 violations** — no cell where the verdict is
> positive and libpcre2's possessive and non-possessive answers differ.
> 16 of the positive-verdict patterns are U9-SHAPED.

**A correction to what that "16" licenses — R31 C12.** The first revision wrote
"so the subtraction had something to subtract". It did not: the U9 SUBTRACTION
branch is inside `if v:` and is reached only by a VIOLATION, and there were
none, so the archived line reads `U9-SHAPED cells subtracted: 0` and
`u9_shaped()` was never exercised by that run. The honest statement is: **16
positive-verdict patterns are U9-shaped and none of them produced a violation,
so nothing needed subtracting** — which is a weaker and true claim. The
predicate itself is exercised by the fourth CONTROL row (U9's own witness),
which is why that control is in the probe.

The probe prints four CONTROLS every run, because a zero from an instrument
that cannot fire is worth nothing: `a*+a` (verdict False, answers DIFFER),
`(?:a|ab){1,3}+c` (verdict False, DIFFER), `[^"]*+"` (verdict True, same), and
U9's own witness. All four behaved as required.

**COMPLETENESS, reported honestly.** 834 of the 1,232 negative-verdict patterns
never changed their answer on any of the 16 subjects — rescues the discharge
declines. That is not a defect (§2.2 is sufficient, and declining is always
safe — `possessify.c`'s own "EVERY SET IS COMPUTED IN THE SOUND DIRECTION"),
and the probe's own text warns that a 16-subject set OVERSTATES the gap:
"never differed on 16 subjects" is not "is a no-op".

**WHAT IT RESCUES.** 532 of 1,764 (30.2%) of the generated possessive patterns
— the canonical idiom family (`[^"]*+"`, `a*+b`, `a++c`) is entirely inside it.
A rescued pattern becomes DFA-eligible only if nothing ELSE forces the VM, so
in practice the rescued population is the capture-free one (`--no-captures`, or
a pattern with no groups). That is the honest size of the win and §14 lists the
measurement that would sharpen it (the same sweep over the real `.rxt` corpus
with `+` suffixes injected, which this lane did not do).

### 5.4 WHERE the discharge runs — NOT in the `discharge` socket

`engine_m4.md` §5.2 designed the `EngineAnalysis.discharge` hook with this
module named as a customer. **This design declines to use it, for the two
reasons `run_possessify`'s own header already gives** (`select_engine.c:194-231`),
plus one this lane measured:

1. *The socket only runs when the pattern is VM-FORCED.* A capture-free `a*+b`
   compiled `--engine=vm` would then be discharged differently from the same
   pattern compiled by default — "the same artifact kind, built by the same
   emitter, optimised differently for a reason nobody could see from the
   outside".
2. *`discharge`'s contract is "rewrite so the ENGINE FORCING no longer
   applies".* For a partially-dischargeable pattern (`(?>a*)b(?>c|cd)e`, one
   node discharged and one not) the rewrite happens and the mask does not move,
   which is exactly the shape §5.2 warns spins the fixpoint.
3. **STRUCTURAL, and it is a live defect in the socket rather than a design
   preference**: the fixpoint's discharge loop (`select_engine.c:283-294`) never
   CALLS a registered hook. It sets `rewrote = true` for any non-NULL
   `discharge` and loops. Registering a hook today would run the analysis pass
   `SELECT_MAX_ROUNDS` = 8 times and rewrite nothing. §5.2 anticipated this
   ("the first customer to need it is the first to design that plumbing") and
   this module's answer is that it is not that customer.

**So the discharge is an ordinary AST pass**, `pcrec_discharge_atomic` in
`src/opt/`, driven from the top of `pcrec_select_engine` before the analysis
loop, unconditionally — the same "the honest driver is the pattern, not the
socket" call `run_possessify` made. It is NOT gated by `-fno-possessify`: the
discharge is semantics-preserving by its own verdict, and gating it would make
an optimisation flag change which ENGINE a pattern gets.

**One consequence worth stating because it is a genuinely nice property, and
one carve-out that keeps it honest.** For the possessive spellings, discharging
is EMISSION-NEUTRAL on the VM path: if the discharge fires, possessify's
fixpoint re-derives the identical verdict on the same quantifier and re-marks
it, so the emitted VM code is byte-identical whether or not the discharge ran.
The discharge changes ENGINE SELECTION and nothing else. That is a CHECKABLE
claim, and Appendix A §3's driver checks it.

**The carve-out: `-fno-possessify`.** With that flag, `run_possessify` does not
run (`select_engine.c:236`), so a DISCHARGED `a*+` emits a plain backtracking
loop where the undischarged one would emit a cut. Emission-neutrality therefore
holds only in the flag's absence. It is not a correctness problem — the
discharge's own verdict says the two lower to the same answers, which is what
makes the discharge legal in the first place — but it is the reason §11.3's
rule 2 has to be scoped to an UNDISCHARGED possessive, and the reason a reader
should not read "emission-neutral" as unconditional.

For a plain `(?>X)` group the discharge is not emission-neutral at all (there
is no possessify rung to re-derive it), and the emitted VM loses a
provably-dead mark and cut — which is a win, not a difference to worry about.

### 5.5 The FULL cut construction, chartered not built — row `[ENG-CUT]`

Frank's companion note rules the long-term answer: cuts preserve regularity
(Berglund, Björklund, van der Merwe, *Cuts in Regular Expressions*), so an
atomic pattern is DFA-compilable, and the construction's one primitive — the
sub-expression's OWN priority-first match endpoint, computed ignoring the
continuation — is what pcrec's subset construction already does
(`src/ir/dfa.c:649-654`'s priority pruning — `if (cl->prune) { cl->ks->n = 0;
return; }` — and `src/ir/dfa.c:1027`'s `make_state`).

> **A citation-drift note, reported because the panel will check both.**
> `assertions_design.md` §2 cites `src/ir/dfa.c:632-651` for `make_state` and
> `engine_m4.md` cites `src/core/compile.c:216` for the priority prune. Neither
> is where those things are on this HEAD: `make_state` is at `:1027` and the
> prune is at `:649-654`. Both moved after those documents were written. This
> lane re-derived every line it cites rather than inheriting one, which is
> constraint (a); the older citations are not corrected here because they are
> not this lane's to edit.

**Charter for `[ENG-CUT]`:**

- **Where it plugs in.** `EngineAnalysis.discharge` — this IS that socket's
  intended customer, and building it means building §5.4's item-3 plumbing
  (a hook that publishes a new root, and a fixpoint that calls it).
- **What it does.** Replace `A_ATOMIC(X)` with an equivalent cut-free
  sub-automaton: run X's own priority-first-accept determinisation to fix, for
  each entry state, the single endpoint the cut commits to, and splice that
  deterministic prefix into the enclosing machine.
- **SIZE ESTIMATE, and it is the reason this is a separate row.** The
  conversion is worst-case EXPONENTIAL in |X| (the cited result gives
  regularity with "possibly-exponential conversion"). Concretely, the cut needs
  a product of the enclosing machine with X's own determinisation, so the bound
  is `|D(X)| × |D(rest)|` states, against the existing caps
  `PCREC_MAX_NFA_STATES` and the DFA state caps (ENG_UNANCH 32,000 /
  ENG_ATTEMPT 10,000 — `assertions_design.md` §3.4.1's two denominators). The
  rewrite must therefore ESTIMATE BEFORE COMMITTING and DECLINE past the cap
  rather than expand and hit it, which is §5.2's recorded obligation on the
  rewrite author. A declining rewrite falls back to the VM, i.e. to this
  module.
- **What it buys, and why the evidence gate is not yet met.** It converts
  capture-free atomic patterns from VM to DFA. The population is exactly the
  532-pattern class MINUS what §5.3's free discharge already rescues — i.e. the
  patterns where the cut genuinely changes the language AND the caller wants no
  captures. This lane did not measure that population's size on real inputs,
  and D50's evidence gate (the same one that re-homed exact islands) should
  apply: build it when a [BENCH-1]/[ENG-PGO]-class customer exists.
- **What it must not do.** Lower `A_ATOMIC` by ignoring atomicity. The registry
  row's own comment (`src/parse/registry.c:615-622`) already records this trap;
  the construction must be a REWRITE that preserves the language, and §11's S90
  is the sabotage for exactly this failure.

---

## 6. (iv) The interaction table

Every row MEASURED against libpcre2 10.46 with python3 3.14 alongside;
`probes/probe_atomic_semantics.py`, 95 cells, `out/atomic_semantics.txt`.
The AGREE column is python-vs-libpcre2; **BOTH-ERR** means both refuse (D26
tier 2 satisfied, tier 3 wording ours).

### 6.1 The table

| # | question | probe cell | libpcre2 | reading |
|---|---|---|---|---|
| 1 | nesting | `(?>(?>a\|ab)c\|abd)` on `"abd"` | (0,3) | the INNER cut kills alt 1; the OUTER alternation still has alt 2. Marks are monotone; §3.3 property 2 |
| 2 | nesting, inner cut inside an outer body | `(?>a(?>b\|bc))c` on `"abc"` | (0,3) | |
| 3 | possessive inside atomic | `(?>a*+)a` on `"aaa"` | nomatch | |
| 4 | atomic INSIDE a quantifier | `(?>a\|b)*c` on `"abac"` | (0,4) | each iteration cuts independently — the mark is TRAILED and re-set per entry |
| 5 | atomic inside a quantifier, cut bites | `(?>a\|ab)*c` on `"abc"` | (2,3) | the search MOVES: the leftmost start fails and start 2 wins. §4's H2 in one cell |
| 6 | quantified atomic group | `(?>ab)+c` on `"ababc"` | (0,5) | |
| 7 | **empty body** | `(?>)` on `"abc"` | **(0,0)** | LEGAL, matches empty. `(?>)a` is (0,1) |
| 8 | **empty-iteration rule** | `(?>a*)*b` on `"aaab"` | (0,4) | terminates; `(?>a*)*` on `"aaa"` is (0,3) |
| 9 | nullable atomic body under a star | `(?>a?)*b` on `"aab"` | (0,3) | |
| 10 | empty atomic body under a star | `(?>)*a` on `"a"` | (0,1) | |
| 11 | alternation priority, longer first | `(?>ab\|a)b` on `"abb"` | (0,3) | |
| 12 | alternation priority, shorter first | `(?>a\|ab)b` on `"abb"` | (0,2) | |
| 13 | priority + longer follow | `(?>a\|ab)bc` on `"abbc"` | nomatch | |
| 14 | **lazy inside** | `(?>a*?)b` on `"aaab"` | **(3,4)** | the cut commits to the LAZY choice (empty), so the match starts at 3 |
| 15 | lazy inside, then `a` | `(?>a*?)a` on `"aaa"` | (0,1) | |
| 16 | lazy plus | `(?>a+?)b` on `"aaab"` | (2,4) | |
| 17 | **captures RETAINED** | `(?>(a)\|ab)` on `"ab"` | (0,1) g1=(0,1) | §3.1's success half |
| 18 | **capture abandoned INSIDE the body** | `(?>(a)x\|ab)` on `"ab"` | (0,2) g1=UNSET | ordinary backtracking, BEFORE the cut |
| 19 | **captures undone on an OUTER failure** | `((?>(a)\|ab))c\|(abc)` on `"abc"` | (0,3) g1,g2 UNSET g3=(0,3) | §3.1's failure half — CUT-INV's whole content, as one cell |
| 20 | possessive on a capturing group | `(a)*+` on `"aaa"` | (0,3) g1=(2,3) | last iteration wins, as uncut |
| 21 | possessive capturing alternation | `(a\|b)*+c` on `"abc"` | (0,3) g1=(1,2) | |
| 22 | `\K` inside | `(?>a\Kb)c` on `"abc"` | (1,3) | **python cannot express this** |
| 23 | `\K` on the NOT-taken branch | `(?>a\|a\Kb)b` on `"abb"` | (0,2) | the cut takes branch 1, so no `\K` is crossed |
| 24 | `\K` before an atomic group | `a\K(?>b\|bc)c` on `"abcc"` | (1,3) | |
| 25 | `\G` inside | `(?>\Ga\|b)c` on `"xbc"` | (1,3) | **python cannot express this** |
| 26 | `\G` outside, atomic inside | `\G(?>a\|ab)c` on `"abc"` | nomatch | |
| 27 | `\b` inside | `(?>a\b)c` on `"ac"` | nomatch | |
| 28 | `(?m)^` inside | `(?m)(?>^a\|b)c` on `"ac"` | (0,2) | |
| 29 | `(?m)$` inside, cut kills the retreat | `(?m)(?>a$\|ab)` on `"ab"` | (0,2) | |
| 30 | `\Z` inside | `(?>a\Z\|ab)` on `"ab"` | (0,2) | |
| 31 | caseless around the group | `(?i)(?>a\|ab)c` on `"ABC"` | nomatch | the cut is case-blind; folding happened at parse time |
| 32 | caseless SCOPED inside the body | `(?>(?i)a\|ab)c` on `"ABc"` | nomatch | **python rejects the pattern** |
| 33 | caseless possessive | `(?i)a*+A` on `"aaA"` | nomatch | `a*+` folded to `[aA]*+` eats the `A` |
| 34 | startpos > 0 | `(?>a\|ab)c` on `"xabc"` at 1 | nomatch | |
| 35 | first candidate fails, a later start wins | `x(?>a\|ab)c` on `"xabxac"` | (3,6) | the find-all / retry cell |
| 36 | **the CEILING cell** | `(?>a\|ab)c\|abcd` on `"abcd"` | **(0,4)** | uncut control `(a\|ab)c\|abcd` is **(0,3)**. §4 |
| 37 | `{n}+` on an exact count | `a{2}+a` on `"aaa"` | (0,3) | possessive on `{n}` is legal and a no-op here |
| 38 | `{n,}+` | `a{2,}+a` on `"aaaa"` | nomatch | |
| 39 | **`{,n}+`** | `a{,2}+b` on `"aab"` | (0,3) | see §6.2 |
| 40 | **`a*?+` — the lazy-then-possessive shape** | `a*?+` | **ERROR** | see §6.3 |
| 41 | quantified atomic is NOT that error | `(?>a)*` on `"aaa"` | (0,3) | |
| 42 | **`{n}+` over a NON-UNIQUE body** | `(?:a\|ab){2}+` on `"aba"` | **(0,3)** | **python says `nomatch`** — see §6.2.1 |
| 43 | its atomic spelling | `(?>(?:a\|ab){2})` on `"aba"` | (0,3) | PCRE2 agrees with row 42; python agrees here |
| 44 | `{n,m}+` over the same body | `(?:a\|ab){2,3}+` on `"ababa"` | (0,3) | python `nomatch` |
| 45 | `{n,}+` over the same body | `(?:a\|ab){2,}+` on `"ababa"` | (0,3) | python `nomatch` |
| 46 | with a follow | `(?:a\|ab){2}+c` on `"abac"` | (0,4) | python `nomatch` |
| 47 | CONTROL: `*+` over the same body | `(?:a\|ab)*+` on `"aba"` | (0,1) | **python AGREES** — the divergence is the BRACE forms only |
| 48 | CONTROL: `++` over the same body | `(?:a\|ab)++c` on `"abac"` | (2,4) | python agrees |

#### 6.2.1 A python divergence the first revision missed entirely — R31 E6

Rows 42-48 are a family, and the shape is exact: **on a BRACE possessive
(`{n}+`, `{n,m}+`, `{n,}+`) over a body whose iteration can end in two places,
python `re` cuts PER ITERATION and PCRE2 cuts at the GROUP EXIT.** `*+` and
`++` over the identical body agree (rows 47-48), which is what makes this a
family rather than a one-off and what makes the controls load-bearing.

Five new divergences, all in the dangerous direction (python reports NO MATCH
where PCRE2 matches), on a construct both oracles support — so a `.rxt` cell
written from python would encode "no match" for a pattern that matches. It goes
to the D27 author as a goal fact (Appendix B.3) and to `possessive.rxt` as a
`# pcre2-only` block.

### 6.2 `{,n}` — the base tier already agrees, and this module must not touch it

The charter asks what pcrec's base tier does with `{,n}` TODAY, before ruling
how the possessive suffix composes. **MEASURED on HEAD** (premise P3):
`build/pcrec -p rx 'a{,2}b'` compiles and matches `"aab"` at **(0,3)** — the
QUANTIFIER reading, not the literal one. libpcre2 10.46 and python 3.14 both
give (0,2) for `a{,2}` on `"aaa"`, agreeing with pcrec.

So PCRE2 10.43+'s change is already reflected and **this module changes
nothing**. The possessive suffix composes with whatever the brace parser
produced, at `src/parse/parse.c:986-988`, which is a single site downstream of
`try_quant` and does not know or care which brace form was accepted. Measured
end to end today: `a{,2}+b` refuses at pattern offset 5 — the `+` — which is
the right blame position and the right module. The module's only obligation is
a corpus cell per brace form (`{n}+`, `{n,}+`, `{n,m}+`, `{,n}+`), which
Appendix A carries.

### 6.3 `a*?+` — REAL-vs-ERROR is exact, the wording is not

**MEASURED:** libpcre2 10.46 refuses `a*?+`, `a*?+b` and `a*++` with
**"quantifier does not follow a repeatable item"**; python refuses all three
with "multiple repeat". D26 tier 2 (RECOGNITION) says pcrec must also REFUSE;
tier 3 says the wording is ours. **pcrec already refuses all three** — see the
table below — so this section is a pinning obligation, not an implementation
one.

pcrec DOES carry libpcre2's exact sentence at
`src/parse/parse.c:974` — `ctx_fail(cx, cx->pos - 1, "quantifier does not
follow a repeatable item")`, with a comment recording that the blame position
was measured against PCRE2's cell for cell — but that is NOT the message this
shape produces; the `multiple quantifiers on the same item` guard fires first
(MEASURED below). **Do not "fix" that** (D26): the requirement is a clean
refusal naming nothing false, both messages are ours to word, and changing a
shipped diagnostic to chase 10.46's phrasing is exactly the tier-3 effort D26
exists to prevent.

The structural rule: after the lazy `?` has been consumed
(`src/parse/parse.c:986`), a following `+` is an ERROR, not a possessive
marker. **That already happens and was MEASURED on HEAD this session** (`out/premises.txt`), so the
module gets it for free rather than having to build it:

| pattern | pcrec on HEAD | libpcre2 10.46 | D26 verdict |
|---|---|---|---|
| `a*?+`  | `multiple quantifiers on the same item (pattern offset 3)` | `quantifier does not follow a repeatable item` | tier 2 ✓ (both REFUSE); tier 3 wording ours |
| `a*?+b` | same, offset 3 | same | ✓ |
| `a*++`  | `possessive quantifier requires module 'atomic-groups' (offset 2)` | `quantifier does not follow a repeatable item` | ✓ today; **after the module lands the first `+` is consumed as the possessive marker and the second re-enters the quantifier loop, so this becomes `multiple quantifiers on the same item`** — still a refusal, still tier-2 correct |
| `a**`   | `multiple quantifiers on the same item (offset 2)` | (the same family) | the CONTROL: this is the existing path `a*?+` already falls into |

The mechanism is `src/parse/parse.c:963-964`'s `if (quantified) ctx_fail(…)`
guard, reached because the lazy `?` ends the round and the `+` starts a new
one. **[M6.4.2] owes only the `tests/reject/` pins**, one per row above,
including the `a*++` row whose message CHANGES when the module lands — which is
the row a reject-suite author would otherwise not think to re-pin.

### 6.4 The existing possessify / [ENG-BREP] rungs meeting a user-written possessive

Three separate questions, and they have three different answers.

**(a) Does possessify's §2.2 verdict stay SOUND when there is a cut in the
pattern?** Nobody has ever asked: the verdict was validated ([ENG-BREP], R24)
on a corpus that could not contain a cut. The subset argument — a cut only
removes paths, and "the winner is never a retreat-into-Q path" is inherited by
a subset — **has a visible hole**: the verdict is about the UNCUT winner `W`,
and if the cut deletes `W`, nothing says the best SURVIVING path is not a
retreat-into-Q path.

**FIRST MEASUREMENT, AND R31 C2 REFUTED ITS NON-VACUITY COUNTER.**
`probe_possessify_under_cut.py` reported 48,000 cells and 0 violations across
four positions, with a "non-vacuity counter" of 202. **The counter measures the
wrong axis**: it counts cells where the POSSESSIVE spelling changes the answer
with the verdict IGNORED. The cell that can refute the claim needs BOTH
properties at once — the verdict POSITIVE *and* the cut BITING. The critic
measured that population in the old generator at **29 patterns / 59 cells
(0.57%), with two of four positions contributing ZERO**. A zero over a
population that thin is not evidence.

**THE RE-MEASUREMENT** (`probes/probe_puc_targeted.py`,
`out/puc_targeted.txt`), generated from atomic groups chosen BECAUSE they bite
and quantifier bodies chosen BECAUSE §2.2 accepts them, with the refutable-cell
count ASSERTED as a per-position FLOOR that the run fails if it cannot reach:

| quantifier position | patterns | verdict + | cut bites | **REFUTABLE cells** | violations |
|---|---|---|---|---|---|
| inside the atomic body | 8,820 | 5,250 | 3,402 | **399** | **0** |
| wrapping the atomic group | 8,820 | **0** | 3,990 | 0 (see below) | 0 |
| before the atomic group | 8,820 | 8,310 | 2,065 | **6,130** | **0** |
| after the atomic group | 8,820 | 5,250 | 2,490 | **3,975** | **0** |

**776,160 cells examined; 10,504 REFUTABLE cells; 0 violations** — against the
critic's measured 59 refutable cells in the old generator, a 178x larger
population on the axis that matters.

Two things the rebuild had to learn, both kept in the probe:

- **The obvious "inside" shape measures nothing.** The first form was
  `(?>QB q|QB xy)tail`: 1,050 positive verdicts, 672 biting patterns and **0
  cells with both**. The cut bites only when the body has a LOWER-PRIORITY
  alternative that would have reached FURTHER, so the second branch has to
  out-reach the quantified first one. `(?>ab*|abc)d` on `"abcd"` is the
  smallest witness (atomic `nomatch`, uncut `(0,4)`).
- **"Q wrapping the atomic group" is EMPTY BY CONSTRUCTION, not by accident,
  and the probe ASSERTS that instead of faking a floor.** Measured: **0
  positive verdicts out of 8,820.** When the quantifier's body IS the atomic
  group, §2.2 evaluates (U2) prefix-freeness on `a|ab` read TRANSPARENTLY (the
  rule below) and declines every time. The probe fails if a positive verdict
  ever appears there, because that would mean the transparency argument is
  wrong.

  **That zero is also a design finding worth stating: possessify's
  transparency is SOUND but measurably INCOMPLETE.** An atomic group is
  *exactly* a unique-match guarantee, so a possessify that understood
  `A_ATOMIC` rather than seeing through it would accept all 8,820. Declining is
  always safe (`possessify.c`'s own invariant), so this is an opportunity and
  not a defect — deliberately not taken in `[M6.4.2]`.

This is EVIDENCE, not a proof, and one correlation remains and is stated rather
than hidden: the verdict is read off the atomicity-ERASED twin, so the verdict
arm and the "cut bites" arm are computed from related objects. Removing that
needs the callable subtree verdict E7 schedules. §14 keeps the claim on the
attack list.

**(b) Does it DOUBLE-CUT?** No, and the reason is Rule 2 of §3.2: the module
never writes `Ast.possessive`. possessify may mark a quantifier that is also
inside or under an `A_ATOMIC`; the emitter then emits the possessive rung's
per-iteration cut AND the atomic group's exit cut, against DIFFERENT marks, in
strictly increasing order (§3.3 property 2). Two cuts at nested marks are not a
double cut; the second is a no-op-or-shrink. `possessify.c:631` also guards
re-marking (`if (verdict && !a->possessive)`), so the fixpoint terminates
unchanged.

**(c) Does it MIS-RUNG?** The rung stamp `RX_VM_STRATS` is set from
`a->possessive` (`emit_vm.c:1751-1753`). Under Rule 2 that stays exactly
possessify's verdict, so a user-written possessive that was NOT discharged does
not colour the stamp — which is right: the stamp reports which OPTIMISATION the
emitter took, and `--list-rungs`-style consumers should keep reading it that
way. The module's own presence is reported by `RX_ENGINE_WHY`, which is where a
reader should look for "why is this a VM artifact".

### 6.5 The revdet hazard this lane found — STRUCTURAL, and it is the reason §3.2's rule 1 is not cosmetic

`src/opt/revdet.c:178-179`, in `rd_node` (the reversed-body copy constructor):

```c
/* The copy is walk material, never a rung host: nothing analyses it and
 * nothing may read a stale verdict off it. */
n->revbody = NULL;
n->possessive = false;
```

and that copy IS emitted — `vm_rev_emit(v, revl, a->revbody, wstepl, &R)` at
`src/gen/emit_vm.c:2887`. `rd_shape` (`revdet.c:128-130`) accepts an `A_REP`
inside the body when `rmin == rmax && rmin >= 1`, so a `{2}+`-shaped item can
sit inside a revdet-approved body. **If the module had stored its semantics in
`Ast.possessive`, `rd_node` would silently delete it on the copy the emitter
walks.**

Under §3.2's rule 1 the semantics live in the node KIND, so the copy carries
them.

**THERE ARE FOUR revdet SITES, NOT TWO — R31 C9.** The `-Wswitch` re-run lists
`src/opt/revdet.c:93` (`rd_shape`), `:185` (`rd_reverse`), **`:321`** (the
byte-set widening walk) and **`:402`** (`rd_alt_disjoint`). The first revision
answered two and §12's slice list enumerated none. All fifteen sites are now
named in §12 slice 1.

**AND "the compiler will not let the module land" IS TOO STRONG — R31 E8.**
Two corrections, both this lane's error:

- `-Werror` is `make strict` only (R5-Q1, and CLAUDE.md says so in as many
  words). A `-Wswitch` diagnostic is a WARNING on a plain `make`. It is a loud,
  enumerated, 15-site warning — which is the whole value — but it does not
  block a build.
- **`rd_shape` and `rd_reverse` do not fail the same way, and the second one is
  dangerous.** `rd_shape` declines by FALLTHROUGH (`revdet.c:143-146`), so an
  unhandled `A_ATOMIC` there is safe by accident. `rd_reverse`'s fallthrough is
  `rd_node`, which copies the node and NULLs `l` and `r` — so an unhandled
  `A_ATOMIC` becomes an **EMPTY-BODY atomic group**, silently, rather than a
  declined one. That is a miscompile produced by a warning nobody turned into
  an error.

**THE ANSWER AT ALL FOUR SITES IS AN EXPLICIT ARM THAT DECLINES**, on `\K`'s
precedent (`revdet.c:184-208`), never a fallthrough: an atomic group is not
reversal-invariant, because its cut is defined relative to the FORWARD priority
order and "the body's first success" is not a property a backwards walk can
reproduce. `rd_shape` sets `S->ok = false`; `rd_reverse` raises as it does for
`A_KRESET`; `:321` widens to all bytes (the sound direction); `:402` declines
disjointness. Declining costs those patterns the revdet rung, and `revdet.c`'s
own rule is that "declining is always available and always safe".

**The decline is NOT sufficient on its own for the LIFTED case**, and this is
where §3.2.5's shared predicate earns itself: `rd_shape` sees the `A_REP` of a
lifted `A_ATOMIC(A_REP(X))`, not the `A_ATOMIC`, so the decline never fires and
`vm_rev_canmove` (`:975`, reading `->possessive`, which RULE 2 leaves false)
hands the loop a retreat frame. `vm_cuts(a)` is what closes that.

---

## 7. (v) The registry

### 7.1 What is there today

`(?>...)` IS a registry row (`src/parse/registry.c:623`):

```c
GROUP('>',  "(?>...)",  atomic_groups,  VM_ONLY, "atomic (non-backtracking) group", QF_YES),
```

carrying a load-bearing comment (`:615-622`) that records the per-pattern split
and the trap ("naive determinization implements the NON-atomic semantics …
this row must never be lowered by simply ignoring the atomicity"). Under D65
its `built` column flips to `built` the day the module wires a producer for it,
derived rather than declared.

The possessive suffixes are **NOT** a registry row. They refuse from
`src/parse/parse.c:988`, and `registry.c`'s own header (`:39-51`) names this as
one of three deliberate exemptions:

> "Two 'requires module' diagnostics also remain in parse.c because they are
> sub-cases of BASE constructs rather than doorways … `\x{...}` … and the
> possessive `+` suffix (a quantifier suffix, not an atom). … These three are
> the registry's known outstanding second homes; SR-4 must special-case the
> first two or silently drop their tests/reject/ coverage, since neither has a
> row to iterate."

### 7.2 The defect this module creates if nothing changes

The day `atomic-groups` lands, `--list-syntax` and the generated index in
`docs/pcre2_compliance.md` will say `(?>...)` is **built** and will say
**nothing at all** about `*+`, `++`, `?+`, `{n,m}+`. A reader has no way to
distinguish "not implemented" from "not in the table", which is a D26 tier-2
(RECOGNITION) discoverability defect, not a tier-3 wording one.

### 7.3 What a fifth row kind would cost — MEASURED, and the number argues for caution

`probes/probe_rk_alarm.sh` (`out/rk_alarm.txt`) appends `RK_QUANTSUFFIX` before
`RK_COUNT` and compiles every `.c` in `src/` and `cli/`:

> 28 files offered, **28 compiled clean**, **0 `-Wswitch` diagnostics naming
> the new enumerator**.
>
> VERDICT: a new `RegKind` raises NO build alarm. Adding one is a change whose
> incompleteness is INVISIBLE to the compiler.

That is the opposite of `AKind`'s 15, and it is the fact that decides this
section. (The probe's own first run died silently on `set -e` plus an
assignment from a failing `ls` — the identical defect
`assertions_measurements/CLAUDE.md` records for `probe_kreset_identity.sh` —
and the note stays in the file.)

### 7.4 The ruling

**RULE R1 — the possessive suffixes GET rows, of a new kind `RK_QUANTSUFFIX`
that is NOT a doorway.** Four rows (`*+`, `++`, `?+`, `{n,m}+`), module
`atomic_groups`, with `syntax` fields that are complete probeable patterns
(`a*+`, `a++`, `a?+`, `a{1,2}+`). The parse path does not change at all: no
doorway consults the new kind, so `registry.c`'s stated reason for the
exemption — that inventing a doorway would cost the BASE tier a lookup on every
quantifier — is preserved exactly. The rows exist for the DUMP, which is a
precedent the file already carries for a row that "exists so the table is
complete for the dump" (`:29-30`).

**RULE R2 — D65's `built` derivation for the new kind drives the row's own
`syntax` through a full compile probe, not a doorway call.** `syntax_dump.c`'s
derivation already works by driving a row's syntax through a gate-forced-open
isolated `Ctx`; for a non-doorway row that call is simply a compile of the
`syntax` string. The three-valued vocabulary (built / unbuilt / "—") is
unchanged.

**RULE R3 — because the compiler will NOT flag an unhandled `RegKind`, the
design supplies the missing check itself.** `tests/registry/registry_check.c`
gains a per-kind assertion: every `RegKind` value must be reached by the dump
and by the built-status derivation, and a kind that no code path handles is a
DEFECT ASSERTION, not a silently-skipped row. Without R3, R1 is a change that
can land half-done invisibly, which is what §7.3 measured.

**The alternative that loses, stated so the panel can weigh it.** An explicit
EXEMPTION (leave the refusal in `parse.c`, record the reason, and let
`pcre2_compliance.md`'s hand-written annotation layer carry the possessive
spellings). It is cheaper and it is what the file already does. It loses
because [DOC-DRV] just spent a whole lane making the compliance page's facts
DERIVED rather than asserted, and a construct whose built-status is only ever
a hand annotation is exactly the thing that document now exists to prevent from
drifting. R1 costs four rows and one check; the exemption costs a permanent
manual entry in the one place the project decided manual entries should not be.

---

## 8. (vi) SR-8 — this module does NOT build it

D55 defers SR-8's lowering-time engine-capability consultation until a
VM_ONLY-masked `RS_MODULE` row acquires a producer, and installs
`tests/registry/registry_check.c`'s `check_engine_capability_tripwire` to fire
on that day. D59 names atomic-groups and backrefs as the second-construct
trigger for the general consultation. `\K` was the first, and [M6.2] wave E
answered it with a NAMED, ARGUED exception rather than by building SR-8.

**RULING: the same answer, with the reason updated rather than copied.**

The tripwire WILL fire when `(?>`'s row gets a producer. The module adds the
SECOND named exception. What this module contributes to the SR-8 question is
not code but the missing evidence, and it is worth writing down because it is
the first time the `engines` column has been shown to be wrong in BOTH
directions on the same row:

- `VM_ONLY` is too STRONG for `(?>a*)b` — the free discharge (§5.3) makes it
  DFA-compilable, MEASURED on 532 patterns.
- `ANY_ENGINE` would be too WEAK for `(?>a|ab)c`, which no engine but the VM
  can compile today.

So the row's mask cannot be made true by editing it, which is precisely Frank's
"the engine answer is per-PATTERN, not per-row". **Reclassifying to
`ANY_ENGINE` (D59's answer for named-groups' three rows) is therefore
REJECTED here**, and the difference is real rather than stylistic: named-groups
rows genuinely lower to both engines for every pattern; `(?>` does not.

The consequence to record on the row rather than act on: **two named exceptions
now exist**, and a third would be the point at which the exception mechanism is
carrying more weight than the column. That is the evidence D55's revisit-when
was waiting for, and it belongs to backrefs ([M6.5]) or to a dedicated SR-8
row, not to this one.

---

## 9. (vii) D58 residue — NONE, and here is why

D58's coupling is "the enumerable RESIDUE": every place emitted code does byte
arithmetic or byte classification that a non-byte encoding would have to
redefine. Enumerated for this module:

| candidate | verdict | why |
|---|---|---|
| `RX_CUT` | no residue | it assigns `resume_depth = slot_values[mark]`. The value is a STACK DEPTH, not a position. No byte is read, no offset is computed |
| the mark slot | no residue | holds `run->resume_depth`, a frame count |
| the work charge | no residue | a difference of two depths (`emit_vm.c:1730-1733`) |
| `A_ATOMIC` in `nfa.c` | no residue | transparent lowering of the body; the body's own constructs carry their own residue |
| `A_ATOMIC` in `mrl.c` | no residue | `pcrec_minw(A_ATOMIC) = pcrec_minw(body)`; widths are already in the units MRL uses everywhere |
| §4's H3 predicate | no residue | `window_end = subject_length`, a length already in scope |

**A cut is position-free.** That is the whole answer, and it is worth
contrasting with `assertions`, whose residue list was non-empty precisely
because its constructs read BYTES (`\b`'s word classification) or MOVED by
bytes (lookbehind's back-step). This module reads no byte it did not already
read as part of the body.

**The one thing to watch, stated so it is not mistaken for a residue.** An
atomic body may CONTAIN encoding-sensitive constructs. Those route through
`src/gen/enc/`'s residual entries from birth, as D58 requires, and the atomic
wrapper neither adds nor removes that obligation. A reviewer looking for this
module's seam entries should find none, and finding none is the correct
outcome, not an omission.

---

## 10. (viii) Module gating and partial enable

The module NAME `atomic-groups` already exists in both refusal sites (P1, P2),
so `--features` gating needs no new name and `tests/reject/`'s gated pins keep
working unchanged.

**RULING: ship both spellings in ONE wave.** Partial enable across waves is
POSSIBLE — `(?>`'s registry row would flip `built` while the `parse.c` refusal
kept the suffixes closed — but there is no reason to want it: under §3.2's rule
1 the possessive suffix is a DESUGARING (`X q+` → `A_ATOMIC(A_REP(X))`), so
shipping `(?>` without it saves no lowering work at all, and PCRE2's own
equivalence is MEASURED to hold on all 8 spelling pairs
(`out/atomic_semantics.txt` section B). A partial ship would leave the project
carrying a `parse.c` refusal for a construct the compiler could already lower,
which is the "enabled but not implemented" shape `ext.c`'s `UNBUILT` machinery
exists to make loud.

If [M6.4.2] nonetheless wants to split, the ONLY defensible split is by
LOWERING and not by spelling: wave 1 the cut and the engine split (both
spellings, VM-forced, no discharge), wave 2 the free discharge. The discharge is
additive, is measured independently (§5.3), and changes no answer — only which
engine produces it — so it is the one seam where a half-landed module is still
truthful.

---

## 11. (ix) The identity gate and the mech sabotage rows

### 11.1 The identity claim

> **An atomic-free pattern's emitted C is byte-identical before and after this
> module.**

It is unusually strong here, and the reason is §9's: the module refines no
alphabet (`assertions`' `\b`/`(?m)` did) and interns no DFA state (`\z` did).
It adds a node kind nothing constructs, an `EngineAnalysis` row that returns
`ENGM_DFA|ENGM_VM` when `has_atomic` is false, an AST pass that rewrites
nothing, and one PREDICATE at `emit_vm.c:4351`.

### 11.2 The reference, and why the `-D` knob is the wrong one here

`tests/mech/CLAUDE.md`'s finding (its §"AND THE FINDING THIS DIRECTORY SHOULD
READ FIRST") is that `run_*_identity.sh` builds its reference from THE TREE'S
OWN SOURCES with a `-D` knob, so under a sabotage BOTH builds are sabotaged and
an edit outside the knob's gated region CANCELS — MEASURED at 1175/1175 and
1135/1135 blind on two separate waves. The 2026-08-19 repair slice sharpened it
further: the knob must sit on **the stage that DECIDES THE EMITTED TEXT**, and
for an analysis that refines an alphabet or interns a state, no emitter-side
knob can un-do it.

**This module has no such stage.** There is no refinement to un-refine and no
state to un-intern; the whole surface is "is there an `A_ATOMIC` in the tree",
which is false for every pre-module pattern. That makes a `-D` knob usable in
principle and USELESS in practice: it would gate code that never runs on the
population under test, so the sweep would report 100% identical no matter what
was sabotaged — the exact blindness the directory warns about, in its purest
form.

**RULING: the identity claim is ONE-SHOT and its reference is a PINNED
PRE-MODULE COMMIT**, on `probe_kreset_identity.sh`'s precedent ([M6.2] wave E,
`assertions_measurements/`) — build the reference compiler from the pinned
commit via `git archive`, so it shares no sources with the subject and no edit
to the subject can reach it. Two engine modes (default and `--engine=vm`, for
wave E's stated reason: under the default most corpus patterns route to the DFA
and never exercise the VM emitter), and a **REFUSAL-MISMATCH column as the
positive control** — the reference cannot compile an atomic pattern at all, so
a run reporting zero differing AND zero refusal mismatches has lost its atomic
population or is comparing two builds of the same tree.

### 11.3 The PERMANENT structural checks

The one-shot gate above does not survive the wave, so four checks go into
`tests/codegen/run_codegen_tests.sh`, each named and each with a sabotage row:

- **`[M6.4-ATOMIC rule 1]`** — a cut-bearing artifact stamps
  `RX_VM_PRUNE_CEILING "subject-end"` and its search entry contains
  `window_end = subject_length`, never a `window[0][1]` assignment. (§4's H3.)
- **`[M6.4-ATOMIC rule 2]`** — `-fno-possessify` on a pattern with an
  UNDISCHARGED user-written possessive (e.g. `(?:a|ab){1,3}+c`, whose §2.2
  verdict is MEASURED negative — `out/free_discharge.txt`'s second control)
  still emits `RX_CUT`. (§3.2 rule 2: the flag denies the possessification
  REWRITE, never a written possessive.) **The scoping is load-bearing**: on a
  DISCHARGED possessive there is correctly no cut to emit, so a rule written
  without it would be red on a correct compiler — see §5.4's carve-out.
- **`[M6.4-ATOMIC rule 3]`** — inside the emitted function, the mark's
  `RX_SET(RX_SLOT_CUT_MARKk, …)` appears BEFORE every `RX_PUSH` that the atomic
  body emits, and every `RX_CUT(k)` is textually reachable only from labels
  after it. (CUT-INV clause 2, §3.3 properties 1 and 2.)
- **`[M6.4-ATOMIC rule 4]`** — a DISCHARGED pattern emits no mark slot and no
  `RX_CUT`; a capture-free discharged pattern emits no VM at all
  (`RX_ENGINE` absent — MEASURED: a `--no-captures` DFA artifact contains zero
  `RX_ENGINE` defines). (§5.3.)

### 11.4 The mech sabotage rows

Shape per `tests/mech/sabotages/S85_*`: `SAB_ID`, `SAB_FILE`, `SAB_SUITES`,
`SAB_HARNESS_TARGET`, `SAB_DESC`, `SAB_DOC_FIGURE`, `SAB_BEFORE`/`SAB_AFTER`.
Numbering continues from S85/S86.

| row | the sabotage | the claim it is the failing direction of | expected to move |
|---|---|---|---|
| **S87** | `emit_vm.c:4351` keeps `v.mrl_win = job->fit.prefilter` on cut artifacts | §4 H3 | codegen rule 1 RED; the `ceiling.rxt` family (`(?>a\|ab)c\|abcd`) RED |
| **S88** | `RX_CUT` also truncates `trail_depth` to the frame's mark | §3.1 CUT-INV | the capture-retention corpus RED (`(?>(a)\|ab)`); codegen GREEN, which is the point — this one is invisible to structure |
| **S89** | the mark's `RX_SET` is emitted AFTER the body's first `RX_PUSH` | CUT-INV clause 2 | codegen rule 3 RED; the nesting and quantified-atomic corpus RED |
| **S90** | the discharge fires unconditionally (drops atomicity whether or not the verdict was positive) | §5.3 | the whole atomic corpus RED; `run_atomic_diff.sh` RED. This is registry.c:615-622's named trap, as a row |
| **S91** | `-fno-possessify` clears the user-written possessive | §3.2 rule 2 | codegen rule 2 RED; the corpus RED **only under the flag**, which is why it needs its own row |
| **S92** | the possessive suffix parses but the mark is never recorded (silent UNCUT lowering) | the house "never miscompile" rule | the corpus RED broadly; `--list-syntax` still reports `built`, which is the row's whole warning |
| **S93** | `rd_shape` ACCEPTS `A_ATOMIC` instead of declining | §6.5 | the revdet-eligible slice of the corpus RED; nothing else moves |

Every `SAB_DOC_FIGURE` is [M6.4.2]'s obligation, measured through the canonical
driver (`run_sabotage_matrix.sh SNN`), never hand-applied — wave D's S82 lesson.
**S88 and S93 are the two that matter most**, because both are invisible to
every structural check and are caught only by the corpus; if either scores
UNDETECTED the corpus is too small, not the row.

---

## 12. Proposed wave structure for [M6.4.2]

One wave, four slices, in this order:

- **Slice 1 — parse + node + refusals.** `A_ATOMIC`, the producer in
  `src/parse/mod_atomic_groups.c`, the suffix desugaring, the `a*?+` error
  path, `Ctx.first_atomic_pos`, and the FIFTEEN `-Wswitch` sites answered
  (§3.2). `tests/reject/` pins move from "requires module" to the real
  diagnostics.
- **Slice 2 — lowering.** `vm_atomic`, the possessive-rung lift (§3.2 rule 3),
  `rd_shape`/`rd_reverse` declines (§6.5), `nfa.c` transparent arm, `mrl.c`
  width arm.
- **Slice 3 — engine.** `forces_atomic`, `pcrec_discharge_atomic`, the
  `--engine=dfa` refusal (which needs no code), and **H3's one predicate**.
- **Slice 4 — evidence.** Appendix A's corpus and drivers, the four codegen
  rules, the seven sabotage rows, the one-shot identity probe, `compliance-refresh`,
  the registry rows and `registry_check` assertion (§7.4), CLAUDE.md updates.

H3 (slice 3) is the only thing in this list that can silently lose a match on a
pattern the compiler otherwise gets right, so it should not be the last thing
written.

---

## 13. What this design does NOT measure

- **Any pcrec behaviour on an atomic pattern.** pcrec refuses all of them. Every
  in-pcrec measurement here is on a PROXY (the atomicity-erased twin, the
  possessive-verdict stamp) or on emitted code for a pattern that has no cut.
- **The cost of the lowering.** No throughput number for a cut artifact exists
  and none could; §3.2 rule 3's frame-count argument is STRUCTURAL, not
  benchmarked.
- **The real-corpus size of the discharge's win.** §5.3 measures a generated
  family; the `.rxt` corpus was not swept with `+` suffixes injected.
- **The `[ENG-CUT]` size blowup on real patterns.** §5.5's bound is analytic.
- **Anything under `--encoding` other than byte.** §9 argues there is nothing
  to measure; that argument is not itself a measurement.

---

## 14. ARGUED claims, with the experiment that refutes each

The panel should start here.

1. **CUT-INV holds for an unconditional cut (§3.1).** STRUCTURAL, and
   PROTOTYPE-checked at 14/14. *Refute by:* finding a reachable path on which a
   frame below the mark has `trail_mark > T0` — e.g. a lowering where the atomic
   group can be ENTERED from a resume label that skips the mark-set, or where
   an enclosing construct pushes its frame AFTER the body has written. The
   prototype tests one lowering; it does not enumerate lowerings.
2. **`RX_CUT`'s assignment is safe because `resume_depth ≥ mark` at every cut
   site (§3.3 property 2).** ARGUED. *Refute by:* a construct that can jump to
   `L_cut` after popping below the entry frame. Nested lookaround (M6.6) is the
   place to look; this design does not cover it.
3. **possessify's §2.2 verdict survives a cut (§6.4a).** MEASURED at 0/48,000
   but ARGUED as a theorem. *Refute by:* a pattern where the cut deletes the
   uncut winner and the best surviving path IS a retreat-into-Q path. The
   generator used four positions and one quantifier per pattern; two
   quantifiers, or a quantifier straddling a nested cut, is the unexplored
   region.
4. **The free discharge's condition is exactly §2.2 (§5.3).** MEASURED at
   0/532 patterns. *Refute by:* a positive-verdict pattern whose possessive and
   plain spellings differ on a subject outside the 16 used. Long subjects and
   subjects with repeated structure are the obvious gap.
5. **H1 (sound rejection) and H2 (start lower bound) (§4.4).** MEASURED at
   0 violations in 17,640 cells, and ARGUED by containment. *Refute by:* a
   pattern where the erased NFA is NOT a superset — which would mean
   `nfa.c`'s `A_ATOMIC` arm does something other than lower the body
   transparently. That is a claim about code nobody has written.
6. **H4: the match-here entries need no change (§4.4).** STRUCTURAL, on lines
   that exist. *Refute by:* an entry path that passes a prefilter window as the
   ceiling. R30 E8 found exactly this class of thing by reading the entries
   rather than the search loop, and this design has read them once.
7. **The identity claim (§11.1).** ARGUED from "the module has no alphabet or
   state action". *Refute by:* any emitted byte that moves on an atomic-free
   pattern. The pinned-commit sweep is the experiment and it has not been run.
8. **Rule 3's frame argument (§3.2).** STRUCTURAL from `vm_star`'s shape.
   *Refute by:* measuring `subject_ceiling` on `(?>a*)` lowered naively vs
   `a*+`; if they are equal the lift is unnecessary.
9. **§7.4's ruling that four dump-only rows are worth their cost.** ARGUED.
   *Refute by:* showing that `registry_check`'s new per-kind assertion is not
   enough to make a half-landed fifth kind loud — §7.3 MEASURED that the
   compiler will not help.

---

## 15. Open questions for Frank

1. **§7.4 (the registry rows).** This design recommends four `RK_QUANTSUFFIX`
   rows over the cheaper explicit exemption, on a [DOC-DRV] consistency
   argument. The exemption is defensible and is what `registry.c` does today.
   **Manager/Frank's call**; nothing else in the module depends on it.
2. **§10 (one wave or two).** The design recommends one. Splitting at the
   discharge is the only truthful split.
3. **§5.5 (`[ENG-CUT]`).** Chartered here with a size estimate and an evidence
   gate borrowed from D50. Confirm the gate, or ask for the population
   measurement that would open it.
4. **§8 (SR-8).** Two named tripwire exceptions will exist after this module.
   Recording that as the trigger for a dedicated SR-8 row (rather than letting
   backrefs add a third) is a scheduling call.

---

## Appendix A — corpus plan

Shaped on `tests/assertions/`, whose CLAUDE.md is the model for an oracle-split
directory.

### A.1 `.rxt` files

| file | population | oracle |
|---|---|---|
| `atomic_basic.rxt` | `(?>...)`: the cut, alternation priority, nesting, empty body, follow interactions | python + libpcre2, both |
| `possessive.rxt` | `*+ ++ ?+ {n,m}+ {n}+ {n,}+ {,n}+`, and the `X q+` ≡ `(?>X q)` pairs cell for cell | python + libpcre2 |
| `atomic_caps.rxt` | captures inside: retained, abandoned-inside, undone-on-outer-failure (§6 rows 17-21) | python + libpcre2 |
| `atomic_quant.rxt` | atomic inside quantifiers, quantified atomic, nullable bodies, the empty-iteration rule | python + libpcre2 |
| `atomic_ceiling.rxt` | §4's R3a family: patterns whose cut match ENDS LATER than the uncut one. **The one file that would go green with H3 unfixed and the corpus too small** | libpcre2 (python agrees; kept dual) |
| `atomic_assert.rxt` | `\K`, `\G`, `\b`, `(?m)`, `\Z` inside and around | **`# pcre2-only` in its entirety** — python cannot express `\K` or `\G` at all (MEASURED, 7 cells) |
| `atomic_case.rxt` | `(?i)` around, inside, and scoped inside the body | mixed: the scoped-inside cells are `# pcre2-only` (python rejects `(?>(?i)a|ab)c`) |

The oracle split is not a formality: `out/atomic_semantics.txt` measures **15
of 109 cells diverging**, and Appendix B enumerates them.

### A.2 Differential drivers

Modelled on `tests/assertions/run_gstart_diff.sh` / `run_kreset_diff.sh`:

- **`run_atomic_diff.sh` §1 — subjects × startpos against libpcre2.** For each
  corpus pattern, every subject in a generated set × every startpos in
  `[0, len]`, compared to `pcre2_ctypes`. This is the instrument S88 and S93
  must go red in, so its subject set must include capture-bearing bodies and
  revdet-eligible bodies by construction, not by luck.
- **`run_atomic_diff.sh` §2 — the ENGINE differential.** Every pattern compiled
  BOTH ways: default (hybrid: prefilter + VM) and `--engine=vm` (prefilter OFF,
  R21 E-6). §4's whole hazard lives in the difference between those two
  artifacts, and a suite that ran only one of them would not see it. **This is
  the single most important driver in the module.**
- **`run_atomic_diff.sh` §3 — the DISCHARGE differential.** Every dischargeable
  pattern compiled with and without the discharge (a `-f` knob, on
  `-fno-possessify`'s precedent), asserting IDENTICAL ANSWERS and, for the
  possessive spellings, identical emitted BYTES (§5.4's emission-neutrality
  property, which is a checkable claim and should be checked).
- **`atomic_entries.c`** — all three entries (`_search`, `_match`,
  `_match_caps`) side by side on the cut corpus, on `kreset_entries.c`'s
  precedent, with the anchored-match oracle spelled `\G(?:PAT)` at the same
  startpos (wave D's trick, since this tree has no anchored flag).
- **`run_atomic_findall.sh`** — the find-all loop over cut patterns, because
  §4's H2 makes "the leftmost candidate is not the leftmost match" a normal
  occurrence rather than an edge case.

### A.3 The generated set for the differentials

`probe_uncut_superset.py`'s generator (`PRE (?>ALT) MID | TAIL`) is the right
shape and is already written; the driver should reuse it rather than invent a
second one. Add the four `{...}` brace forms and the four possessive suffixes,
and keep the two-byte `(?>` → `(?:` twin construction — a hand-written twin can
differ in something other than the atomicity, which makes divergences
unattributable.

---

## Appendix B — GOAL FACTS for the [M6.4.3] D27 blinded author

The author is denied `src/` and `tests/` and writes from the PCRE2 goal. These
are the facts a spec-first writer needs and cannot get from the code.

**B.1 The semantics, in one line each.**
`(?>X)` matches whatever `X` matches at the current position on `X`'s OWN first
attempt, and then refuses to reconsider: if what follows fails, the whole group
fails rather than letting `X` try again. `X*+`, `X++`, `X?+`, `X{n,m}+` are
defined by PCRE2 as `(?>X*)`, `(?>X+)`, `(?>X?)`, `(?>X{n,m})` — MEASURED
identical on all 8 pairs tested.

**B.2 The oracle of record is libpcre2 10.46**, driven by
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py` (a ctypes binding;
there is no `pcre2test` on this box). `tests/named_groups/d27/lib_pcre2.py` and
`tests/assertions/verify_pcre2.py` are the existing drivers to copy.

**B.3 python3 3.14 supports BOTH spellings and is a usable second oracle —
except for these 13 cells, MEASURED** (`out/atomic_semantics.txt`):

| cell | libpcre2 | python 3.14 | class |
|---|---|---|---|
| `(?>a\Kb)c` on `"abc"` | (1,3) | `error: bad escape \K` | python CANNOT EXPRESS |
| `(?>a\Kb\|ab)c` on `"abc"` | (1,3) | same error | python cannot express |
| `(?>a\|a\Kb)b` on `"abb"` | (0,2) | same error | python cannot express |
| `a\K(?>b\|bc)c` on `"abcc"` | (1,3) | same error | python cannot express |
| `(?>\Ga\|b)c` on `"ac"` | (0,2) | `error: bad escape \G` | python cannot express |
| `(?>\Ga\|b)c` on `"xbc"` | (1,3) | same error | python cannot express |
| `\G(?>a\|ab)c` on `"abc"` | nomatch | same error | python cannot express |
| `(?>(?i)a\|ab)c` on `"ABc"` | nomatch | `error: global flags not at the start of the expression` | python cannot PARSE |
| `a?(?:b){0,4}+a` on `"a"` | **nomatch** | **(0,1)** | **U9 — a real answer divergence** |
| `(a?)(?>(b){0,4})a` on `"a"` | **nomatch** | **(0,1)** g1=(0,0) | **U9, atomic spelling** |

(The remaining three rows in the raw table are group-tuple padding artefacts of
the C API, corrected in the probe and listed here as agreeing.)

**B.4 U9 is the one to internalise** (`docs/dev/upstream_issues.md`): on
libpcre2 10.46, a possessive or atomic BOUNDED repeat `{m,n}+` of a GROUP,
preceded by an item that consumed and can give back, refuses to backtrack into
that PRECEDING item. python and a hand derivation both disagree with libpcre2
here. All three conjuncts are necessary — `a?b{0,4}+a` (character item, not a
group), `a?(?:b)*+a` (`*+` not `{m,n}+`) and `x?(?:b){0,4}+a` (the prefix
consumed nothing) all MATCH. **Re-measured on HEAD this session: still
reproduces.** A D27 author writing `{m,n}+`-over-a-group cells with a
backtrackable prefix must take libpcre2's answer, and should say in the file
that they did.

**B.5 Facts that are pcrec's promise, not PCRE2's.** `--engine=dfa` on a
cut pattern REFUSES rather than downgrading (D44.6). `-fno-possessify` denies
the possessification REWRITE and must NOT change a written possessive's
answer. `{,n}` is a quantifier (PCRE2 10.43+), and pcrec's base tier already
agrees. `(?>)` is legal and matches empty.

**B.6 Where a blinded author should aim.** The three shapes this design says
are hardest are: (1) a cut whose match ENDS LATER than the same pattern's
uncut match (§4's family — write these from the definition, not from
intuition); (2) captures written inside a body that the cut commits to and an
OUTER failure then has to undo; (3) an atomic group inside a quantifier, where
each iteration cuts independently. All three are places where a
plausible implementation is wrong in the direction of returning an ANSWER
rather than an error.

---
