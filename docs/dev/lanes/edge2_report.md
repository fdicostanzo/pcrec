# edge2 — [OPT-EDGE] STEP 1.1 (narrow precondition (8)) + the owed ladder and floor

Lane B′ of the 2026-09-04 wave. Branch `lane/edge2`, based on main
`b048fa61` (abi **20** -- `386abf94`'s shared-sentinel dispatch merged at 19,
[DD-13b.W1.3]'s composition at 20; edge1's report says 19 and is one merge
stale). Written
under the box hold: no `make test`, no test-axes, no batteries, no timing
loops. Every number that needs a suite or a quiet box is marked **OWED**.

`docs/dev/lanes/edge1_report.md` is the predecessor's record and this report
does not restate it.

---

## 1. THE DESIGN, AND THE FINDING THAT CHANGED IT

Written 2026-09-04 ~10:5x EDT, after reading `src/opt/scanedge.c`,
`src/gen/emit_dfa.c`'s `unanch_start` / `dfa_pfs` / `emit_scan_loop` /
`seed_emit_seeded`, and `src/core/compile.c`'s pipeline — and BEFORE editing a
line. §1.5 is the prediction table this lane is scored on.

### 1.1 THE BRIEF'S PREMISE IS INCOMPLETE, AND ACTING ON IT ALONE WOULD SHIP A MISCOMPILE ON ITS OWN ACCEPTANCE POPULATION

The brief (and `plan.md`'s STEP 1.1 filing, and edge1's §3.6b) name ONE hazard
behind precondition (8): the offset-set prefilter's RESEED
(`pf_emit_ofs_reseed`), the one MID-BODY writer of the state variable. The
proposed narrowing is "seed AND a reseeding prefilter", and its acceptance is
that the 9 `\b`-family artifacts with `byte-class`/`memchr` prefilters regain
their edge.

**There is a SECOND writer, it is not mid-body, and (8) is what has been
guarding it since STEP 1 landed.** `seed_emit_seeded` (axis D's `seeded` form,
`emit_dfa.c:3965`) initialises the state variable, ONCE PER SEARCH and BEFORE
the loop, to

```c
rx_forward_state forward_state =
    search_from ? rx_forward_seed_state[rx_forward_byte_class[subject[search_from - 1]]] : 0;
```

i.e. to `s1u[upc(s[search_from - 1])]` — **any** member of the seed family, not
only `s0`. `emit_scan_loop`'s one-per-search entry dispatch then asks

```c
if (forward_state == <cell_of(s0)>) goto rx_forward_scan_edge;
```

which is exact ONLY because precondition (8) refuses every seed target except
`s0` as a head. The loop's own comment says so in as many words
(`emit_dfa.c:5488`: *"the value is a runtime table read whose only head-valued
outcome is `cell_of(s0)` (precondition (8) refuses every other seed target as a
head), so an equality against that ONE cell is exact"*).

Narrow (8) to the reseed alone and that sentence stops being true. A search at
`search_from > 0` whose preceding byte seeds into a head `h != s0` enters the
loop with the state variable holding `h`, takes the GENERIC path (the prefilter
guard is `state == s0`, false; no stay skip fires at a head; the stop test has
not run yet), and reaches the step — which reads `tr[h][C]`, **the cell the
pass killed**. The scan never runs and the machine dies at that position.

**MEASURED, on the acceptance population itself.** `\b\w+\b` compiled by this
branch's own baseline (`--features all`):

| fact | value |
|---|---|
| `rx_forward_seed_state[2]` | `{ 0, 2 }` |
| forward machine | 3 states, `ncls` 2, premultiplied (cells 0/2/4) |
| `s1u[UPC_PLAIN]` | cell 0 = state 0 = `s0` |
| `s1u[UPC_WORD]` | cell 2 = **state 1**, which is NOT `s0` |
| prefilter | `byte-class-bounded` — **no reseed** |

State 1 is the `\w+` chain's head. It is a seed target, it is not `s0`, and its
prefilter does not reseed. It is exactly one of the 9, and under the brief's
narrowing it becomes a head the loop's entry test cannot see.

So **the narrowing is two changes, not one**, and the second is the one that
makes the first safe.

### 1.2 (i) THE ENTRY DISPATCH BECOMES THE SHARED SENTINEL TEST

The entry test asks a SPECIAL-CASE question — *"is the state variable exactly
`cell_of(s0)`"* — where the general one is *"is the state variable a scan-edge
head"*. That general question is already spelled, once, for the loop body:
`is_stop(s) && !is_dead(s)`. So the entry becomes

```c
if (<p>_<m>_is_stop(state) && !<p>_<m>_is_dead(state)) goto <p>_<m>_scan_edge;
```

emitted whenever the machine carries an edge AND the state variable can hold a
head at entry. Under the `constant` seed with `s0` a head the state IS
`cell_of(s0)`, so the unconditional `goto` shipped today stays exactly as it is
— that is the fold, not a second form.

This is the general mechanism the row already chose one level down (memory
`pcrec-general-mechanisms-not-special-cases`): the loop's per-byte test and its
per-search test now ask the SAME question through the SAME predicate, and the
`s0` equality stops being a fact about the seed family that (8) has to keep
true.

Cost: one compare per SEARCH on a seeded, edge-bearing machine — the same place
today's equality already sits, in the same shape. Nothing on the per-byte path
moves.

The emission condition is a new predicate, `dfa_seed_can_be_scan_head(d)`: `s0`
is a head, or the machine takes the `seeded` form and some live `s1u[u]`/
`s1g[u]` is a head. `dfa_start_is_scan_head` KEEPS its other reader — the
prefilter's placement, which is genuinely a question about `s0` alone (the
prefilter's own guard is `state == cell_of(s0)`) — and this change is precisely
what separates the two questions that (8) had conflated into one.

### 1.3 (ii) THE PRECONDITION NARROWS TO THE RESEED, AND THE FORM ANSWERS IT

With (i) in place the entry seed is no longer a hazard, and (8) is left holding
exactly one: the offset-set prefilter's mid-body reseed. The narrowed rule is

> a chain head may not be a state any seed family names **when this machine's
> emitted prefilter WRITES the state variable**.

Three pieces, and the point of each is that nothing gets a second derivation.

**(a) THE FACT LIVES ON THE FORM OBJECT.** `DfaPf` gains a `bool reseeds`.
The two offset-set rows set it true; `memchr`, `memchr-bounded`, `byte-class`,
`byte-class-bounded` and `none` set it false. That is D82's axis machinery used
as intended: "does this prefilter write the state variable" is a property of a
prefilter FORM, so it is declared in the same struct literal that declares the
form's emitter, and a seventh form added later cannot forget to answer it
without the initialiser looking wrong. The alternative — a list of form NAMES
somewhere else — is the parallel mechanism the house rule forbids.

**(b) THE SELECTION IS ASKED BEFORE THE PASS RUNS, AND IT IS THE SAME
SELECTION.** `emit_dfa.c` exports

```c
bool pcrec_dfa_scan_state_written(Ctx *cx, const Dfa *d);
```

which builds the same `DfaSel` `dfa_form_derive` builds (`.forward = (d ==
&cx->job->dfa)`, so the reverse and anchored machines decline through axis B's
own `s->forward` clause rather than through a branch here), runs the same
`DFA_SELECT` over `dfa_pfs` with the same flags, and returns
`pf->reseeds && dfa_needs_seed(d)`. `src/core/compile.c` calls it immediately
before each `pcrec_scanedge_dfa` and passes the answer in.

**(c) WHY THE ANSWER IS THE SAME ONE THE EMITTER WILL REACH.** `unanch_start`
is INVARIANT under `pcrec_scanedge_dfa`, and that is a claim with a proof
rather than a hope:

| what `unanch_start` reads | why the pass cannot move it |
|---|---|
| `dfa_has_eolvar`/`dfa_has_endvar` on both machines | a member must pass `pcrec_state_view_invariant`, so no state carrying a view is ever a member or dropped |
| `fd->clsctx`, `rd->clsctx` | untouched |
| `state_acc_any(fd->st[fs])`, and the `s1u[u]` states under `fseed` | accept bits are never rewritten; `s0` always survives, and no `s1u[u]` can be dropped (a seed target has an in-edge from the seed, so `indeg != 1` truncates the chain in front of it) |
| `dfa_needs_seed(fd)` — equality of `s1u[u]` across `u` | `remap` is injective on survivors, so equalities are preserved |
| `cand_from_escapes(fs)` — `tr[fs][clsmap[b]] != fs` for each byte | the only cell the pass rewrites is `tr[head][C] = -1`, and `-1 != fs` exactly as the old target `u_1 != fs` did; every other cell is `remap`ped, and `remap[t] != remap[fs] ⟺ t != fs` |
| `pcrec_prefix_ksets(cx, &job->nfa, cand.set, …)` | walks the NFA, which this pass never touches, over a candidate set the row above shows is unchanged |

**AND IT IS CHECKED RATHER THAN ASSERTED.** `dfa_form_derive` already reads
back two of the pass's claims (the heads are the top rows; no state carries
both a skip and an edge). A THIRD check joins them, and it is the one that
cannot share a source with what it checks — the emitter, holding the form it is
about to write, re-derives the precondition from the machine itself:

> if this form's prefilter `reseeds` and the machine needs a seed, then no
> state named by `s1u[]`/`s1g[]` other than `s0` may carry a scan edge.

A pass-time answer that drifts from the emission-time one is then a loud
`ctx_fail` naming the state, not a silent miscompile.

### 1.4 WHAT I CONSIDERED AND DID NOT BUILD

- **Moving the pass after axis B.** Rejected, and not on size: axis B is
  selected inside `dfa_form_derive`, which runs during emission, after the
  tables would have to have been emitted from a machine the pass has not yet
  shrunk. There is no point in the pipeline that is both "after the form is
  chosen" and "before anything reads the machine". The invariance argument in
  §1.3(c) is what makes asking EARLY legitimate, and it is the smaller move.
- **Reading `PCREC_NO_OFFSET_SKIP` and nothing else.** That is a second
  spelling of axis B's own filter. `DFA_SELECT` already applies the deny mask,
  so asking the selection asks the flag too, once.
- **Leaving the entry dispatch alone and narrowing (8) to
  `seedtgt && (reseeds || the seed can name a head)`.** Equivalent to today's
  (8) on the whole acceptance population (all 9 are seeded head targets), so it
  buys nothing. §1.1 is why.

### 1.5 THE PREDICTION TABLE

Scored at §4.

| # | prediction |
|---|---|
| **P1** | The 9 `byte-class`/`memchr` artifacts regain a scan edge, by name: `(\b\w+\b)`, `(foo\B)`, `\b\w+\b`, `\b\w+\b$`, `\b\w+\b\z`, `\b\w+\z`, `\b\w\b`, `foo\B`, and `\b\K\w+` back from 1 edge to 2. |
| **P2** | The 2 `offset-set-bounded` artifacts, `\Bfoo\B` and `\bfoo\B`, STILL DECLINE. |
| **P3** | Every artifact with no seed table is byte-identical to this branch's baseline. (8) is unreachable without a seed either way, and (i) emits nothing on a machine with no edge. |
| **P4** | Every artifact whose forward machine has a seed but NO scan edge is byte-identical too: (i) is gated on `nscan > 0`. |
| **P5** | An artifact where `s0` is a head under the `constant` seed keeps its unconditional `goto` byte for byte. |
| **P6** | THE POSITIVE CONTROL: with (i) reverted and (8) narrowed, `\b\w+\b` LOSES matches at `search_from > 0` after a word character. Predicted symptom: a match that begins inside the seeded run is not found. |
| **P7** | THE SECOND POSITIVE CONTROL: with (8) removed ENTIRELY (both halves), `\bfoo\B` — an `offset-set-bounded` machine with a reseed — misbehaves, and (i) alone does NOT save it, because the reseed is mid-body. |
| **P8** | Emitted scaffolding moves (the entry test's text on seeded edge-bearing machines), so this is an abi event. Number assigned at the merge. |
| **P9** | `RX_DFA_SCAN_EDGE` MOVES on the 9, `"none"` → `"range"`, so unlike edge1's census the stamp is a usable instrument here. |

---

## 2. THE LADDER AND THE FLOOR — PROTOCOLS (designed under the hold; run after `.lift`)

### 2.1 The ladder, by the isolation that works

edge1's ladder failed by DESIGN, not by execution: subtracting the
`-fno-scan-edge` arm subtracts a DIFFERENT MACHINE (chain interiors intact), so
the difference carries the scan collapse's own per-byte win and the entry cost
reads negative at every rung. The isolation that works is **branch against
main, same machine, same edges, only the dispatch differing** — and here "main"
means the compiler at `9d8401a` (pre-dispatch) against `b048fa61` (post), both
built from `git archive` into the scratch dir.

- **Rungs.** Four patterns whose FORWARD machine carries 1, 2, 3 and 4 edges,
  each count VERIFIED by counting `[OPT-5] SCAN EDGE` markers in the artifact
  before it is timed (`PCREC_MAX_SCAN_EDGES` is 4; edge1's F2). Starting set
  `\d{2}y`, `\d{2}y\d{2}`, `\d{2}y\d{2}y\d{2}`, `\d{2}y\d{2}y\d{2}y\d{4}`,
  re-verified rather than inherited.
- **Subjects.** ONE near-miss subject PER RUNG, drawn so the rung's own chain
  is ENTERED and LEFT without a match. edge1's lesson stated as a floor: a
  subject that reads under ~0.1 ns/byte never entered the chain and measures
  nothing; the harness REFUSES such a rung rather than reporting it.
- **Arms.** `branch` and `main` only. `-fno-scan-edge` is retained as a
  CONTROL that must move with neither (it is a different machine and its number
  is not subtracted from anything).
- **Method.** 15 rounds × 10 sweeps, 256 KB subjects, `taskset`-pinned, arms
  interleaved WITHIN each round, ratio taken per round from that round's own
  pair, median reported WITH the per-round range. Preconditions: `load1 < 0.5`
  before the run and re-checked between rounds; a round taken above it is
  DISCARDED, not caveated.
- **The output** is `t_main(k) − t_branch(k)` per byte, fitted as `a + b·k`.
  The claim under test: `b > 0` (the old loop's per-edge compare) and the
  branch's own `b ≈ 0`. A `b` indistinguishable from zero on BOTH arms means
  the compares were hiding behind the load-latency chain all along and the
  dispatch's win is fixed-per-artifact — which is a real answer and is what
  decides `PCREC_MAX_SCAN_EDGES`.

### 2.2 The floor, on the NEW loop

Precondition (5) admits `m >= 2`. The pay-off length on the O(1) dispatch is a
different number from the old loop's, which is the row's own SEQUENCING ruling.

- **Ladder.** Chains of `m` = 2, 3, 4, 8 (`[0-9]{m}` and `[a-z]{0,m}` families,
  both, because the nullable form is the one edge1's `t-digits-016k` note shows
  behaving differently), each timed on THIS branch, default against
  `-fno-scan-edge` — here the noedge arm IS the right control, because the
  question is "is the edge worth taking at this length", which is exactly the
  two-machine comparison.
- **Subjects.** Near-miss runs drawn to STRADDLE `m`, so the chain is entered
  and abandoned rather than completed.
- **The choice.** The floor is placed INSIDE a measured gap — a length where
  the two arms are separated by more than the per-round range at BOTH
  neighbours — never at a crossing point read off a median.
- **The landing.** A `limits.def` row of kind `selection knee`, with the
  numbers at the row and `docs/spec/limits.md`'s entry. If no gap is measured,
  the floor is NOT moved and the row records the measurement that says so
  (D77).
- **`PCREC_MAX_SCAN_EDGES` (4)** is re-chosen ONLY if §2.1's `b` supports it,
  and the report states what the ladder said either way. Today it is an
  emitted-bytes budget (edge1's F4) and has never been measured as one.

---


## 3. WHAT EXISTS ON THE BRANCH

| commit | what |
|---|---|
| `2cfe6e1f` | §1's design and prediction table, committed before any edit |
| `5025e795` | the mechanism: the entry dispatch generalises, (8) narrows, `DfaPf.reseeds`, `pcrec_dfa_scan_state_written`, the emitter's third read-back check |
| `29e7d0a3` | `tests/codegen/run_scan_edge_census.sh`, wired into `test-codegen`; `docs/spec/tuning.md` §2.18; `src/opt/`, `src/gen/`, `tests/codegen/` CLAUDE.md rows |

`make -j2` and `make strict` are clean. **NO abi bump** — §7 is the site list
and the number is the manager's.

### 3.1 THE MECHANISM, AS BUILT

**(i) `emit_scan_loop`'s entry dispatch.** `dfa_seed_can_be_scan_head(d)` is
the new emission condition (`s0` is a head, or the machine takes the `seeded`
form and some live `s1u[u]`/`s1g[u]` is one — `s1g` joins even though only
`s1u` is emitted as this engine's seed table, because over-answering costs one
folded compare per search and under-answering is the miscompile). The emitted
test is `is_stop(state) && !is_dead(state)`. Under the `constant` seed the
unconditional `goto` is unchanged. `dfa_start_is_scan_head` keeps its other
reader, the prefilter's placement.

**(ii) `DfaPf.reseeds`,** true on `offset-set-bounded` and `offset-set`, false
on the other five. `pcrec_dfa_scan_state_written(cx, d)` builds the same
`DfaSel` `dfa_form_derive` builds and returns `pf->reseeds &&
dfa_needs_seed(d)`; `src/core/compile.c` calls it at all three
`pcrec_scanedge_dfa` sites. `collect()`'s (8) becomes
`if (prefilter_reseeds && seedtgt[s]) continue;`.

**(iii) A THIRD READ-BACK CHECK in `dfa_form_derive`,** beside the two STEP 1
added. It re-derives (8) from the machine the form is about to be written from
— if this form reseeds and the machine needs a seed, no `s1u[]`/`s1g[]` member
other than `s0` may carry an edge — and `ctx_fail`s naming the state and the
form. It is the one reading here that does not share a source with the pass's
decision: (a) and (b) check a layout the pass produced, this checks an
AGREEMENT between two derivations taken at two different times.

---

## 4. THE PREDICTION TABLE, SCORED

| # | outcome |
|---|---|
| **P1** the 9 regain an edge | **HIT**, and `\b\K\w+` goes 1 → 2 as predicted. §4.1. |
| **P2** the 2 offset-set artifacts still decline | **MISS IN LETTER, HIT IN SUBSTANCE, and the miss is the lane's second real finding.** Both regain an edge — on their REVERSE machine, which carries no prefilter at all. Their FORWARD machines still decline, which is where (8) applies. §4.1. |
| **P3** no-seed artifacts byte-identical | **HIT.** 19 of 19 non-seed patterns identical to main. |
| **P4** seeded-but-edgeless artifacts byte-identical | **HIT**, inside the same 19. |
| **P5** the `constant`-seed unconditional `goto` unchanged | **HIT** — `[a-z]*`, `[a-z]{0,4}`, `[0-9]{16}`, `foo[a-z]{0,50}bar` are all byte-identical to main. |
| **P6** sabotage A (entry reverted) loses matches on `\b\w+\b` | **HIT ON THE PREDICTION, MISS ON THE WITNESS.** The hazard is real and measured, but not on `\b\w+\b`: there the seeded head is only reachable mid-word, where no match starts, so the loss is unobservable. The witness is `foo\B` — §4.2. |
| **P7** sabotage B ((8) removed) misbehaves on `\bfoo\B` | **MISS, and it is the lane's third finding.** (8) removed entirely changes NOTHING: 30 of 30 patterns byte-identical, all answers unchanged. The reseed hazard has NO WITNESS. §5 F2. |
| **P8** an abi event | **HIT.** The entry test's text moves on seeded edge-bearing machines. §7. |
| **P9** `RX_DFA_SCAN_EDGE` moves on the 9 | **HIT**, `"none"` → `"bitmap"`/`"range"` — but it is still the WRONG INSTRUMENT for the census, because it cannot see 1 → 2. The check counts markers. |

### 4.1 THE PER-MACHINE CENSUS

Edge blocks per machine, from each artifact's own `[OPT-5] SCAN EDGE` markers
attributed by the state variable the block tests. Same output basename on both
compilers (the artifact embeds its own `.h` name — the trap edge1 recorded).

| pattern | main f/r/a | branch f/r/a | forward prefilter |
|---|---|---|---|
| `(\b\w+\b)` | 0/0/0 | **1**/0/0 | `byte-class-bounded` |
| `\b\w+\b` | 0/0/0 | **1**/0/0 | `byte-class-bounded` |
| `\b\w+\b$` | 0/0/0 | **1**/0/0 | `byte-class-bounded` |
| `\b\w+\b\z` | 0/0/0 | **1**/0/0 | `byte-class-bounded` |
| `\b\w+\z` | 0/0/0 | **1**/0/0 | `byte-class-bounded` |
| `\b\w\b` | 0/0/0 | **1**/0/0 | `byte-class-bounded` |
| `\b\K\w+` | 1/0/0 | **2**/0/0 | `byte-class-bounded` |
| `(foo\B)` | 0/0/0 | 0/**1**/0 | `memchr-bounded` |
| `foo\B` | 0/0/0 | 0/**1**/0 | `memchr-bounded` |
| `\Bfoo\B` | 0/0/0 | 0/**1**/0 | `offset-set-bounded` |
| `\bfoo\B` | 0/0/0 | 0/**1**/0 | `offset-set-bounded` |

Byte identity over a 30-pattern set (the 11 plus 19 chosen for the shapes P3-P5
name): **exactly the 11 move against main, and nothing else does.**

Answers: the 10 of the 11 that python3 `re` can express, over 16 subjects each
under the find-all loop, agree cell for cell.

### 4.2 THE POSITIVE CONTROL FOR (i), AND ITS WITNESS

Sabotage A is this branch with the entry dispatch reverted to `state ==
cell_of(s0)` and (8) left narrowed — i.e. the brief's own proposal built alone.

```
foo\B on "xfoofoox"     branch [(1,4) (4,7)]     sabotage A []
```

Two matches lost outright. The mechanism is in the artifact: `foo\B`'s edge is
on the REVERSE machine, whose seed table is `{ 0, 12, 12, 12 }` against a stop
floor of 12 — **three of its four seed classes land exactly on the head**, the
`s0` equality sees none of them, the reverse walk steps into the killed cell
and the match START is never recovered.

The census check goes **11 of 13 rows red** against that build, and 11 of 13
red against the STEP 1 compiler. Both failing directions were run.

**WHY `\b\w+\b` DOES NOT WITNESS IT, which is worth knowing.** Its forward
seed does land on the head (`{ 0, 4 }` against a floor of 4), so the emitted
code is wrong there too — but the only searches that reach it start
mid-word, and no match of `\b\w+\b` begins mid-word, so the wrong answer and
the right one coincide. A witness has to be a pattern whose seeded head is
reachable at a position a match can start at.

---

## 5. FINDINGS

**F1 — PRECONDITION (8) GUARDED TWO HAZARDS AND ONLY ONE WAS NAMED.** §1.1.
The entry seed is the second, it is live, and narrowing (8) without §1.2 would
have shipped a lost-match miscompile. The general shape, worth carrying: a
precondition adopted to make ONE emitted site sound gets silently depended on
by the NEXT site that reads the same fact, and nothing links them. Here the
only record of the second dependency was a clause inside a comment about
something else (`emit_dfa.c:5488`). The cure is what this lane did — make the
second site ask its own question — not a longer comment.

**F2 — THE HAZARD (8) NOW GUARDS HAS NO WITNESS, AND THE STEP 1 CENSUS'S
"2 of 11 carry it" IS WRONG.** Measured three ways:

- an artifact compiled with (8) **removed entirely** is byte-identical to this
  branch's on all 30 patterns, and answer-identical on the subject sweep;
- the two artifacts the STEP 1 census called hazardous regain their edge on the
  **reverse** machine, which has no prefilter at all — the census read the
  artifact-level `RX_DFA_PREFILTER` stamp, which describes the FORWARD machine,
  and attributed a reverse-machine edge to it;
- ten constructed `offset-set` shapes (`\b\.[0-9]{4}Z`, `\b[0-9]{4}-[0-9]{2}`,
  `\bab[0-9]{5}cd`, `\bq[0-9]{6}q`, …) have **no forward scan edge with (8)
  removed either**, and the reason is structural: the offset-k selection wants
  a leading literal/assertion prefix, whose restart threads give the counting
  states a class-dependent exit and break precondition (1)'s uniformity.

(8) is kept — exact, cheap, and guarding a mechanism that genuinely writes the
state variable mid-body — and the emitter's read-back check is what makes the
day its population stops being empty loud rather than silent. **It is not a
check with a failing direction, and `run_scan_edge_census.sh` says so in its
own header rather than implying otherwise.**

**F3 — THE CENSUS INSTRUMENT HAS TO BE PER MACHINE.** edge1's census counted
`[OPT-5] SCAN EDGE` markers per ARTIFACT and read the prefilter stamp per
artifact; an artifact has up to three machines and only the forward one has a
prefilter. Every conclusion about which artifacts "carry the hazard" was drawn
at the wrong resolution. The check in this branch attributes each marker by the
state variable its block tests.

**F4 — A COMPILE-TIME COST NOBODY IS PAYING ATTENTION TO.**
`pcrec_dfa_scan_state_written` calls `unanch_start`, which calls
`pcrec_prefix_ksets` (an NFA walk). It is gated on `dfa_needs_seed(d)` first,
so the overwhelming majority of compiles skip it entirely, but on a seeded
machine it is up to three extra `unanch_start` calls per compile on top of the
two `dfa_engine_is_empty` already makes. Not measured. If it matters, the fix
is memoising `unanch_start` on the `Job`, which is a general improvement and
not this row's.

---

## 6. WHAT IS UNVERIFIED, AND WHAT NEEDS A RULING

**UNVERIFIED — all of it is the box hold, and none of it is a doubt about the
mechanism.**

- `make test`, `make test-codegen`, `make test-registry`, `make test-axes`.
  ANSWER IDENTITY across the axes is the one that matters here: 11 artifacts'
  machines changed shape, and `-fno-scan-edge` / `-fno-offset-skip` are the two
  axes that interact with this row.
- `make test LINTGEN=1` and the sanitizer axes.
- **THE LADDER AND THE FLOOR.** Designed (§2), harnessed, and the reference
  compilers built; the rung edge counts are VERIFIED 1/2/3/4 from the
  artifacts. Nothing timed — the box has been at load 3.5-4.2 for the whole
  write phase.
- The corpus-wide version of §4.1's census (2,539 artifacts). The 11 are
  edge1's list, re-measured; that the list is still COMPLETE is a corpus sweep.

**NEEDS A RULING.**

1. **The abi number**, and the (B) FILEPIN re-pin. §7.
2. **Should (8) survive at all?** F2 says its population is empty and its
   hazard has no witness. Frank's own posture on edge1's F5 was "no row, no
   hunt" — but this is the inverse: a guard with no witness, kept. My view is
   KEEP: the reseed provably writes the state variable where nothing can see
   it, the precondition costs one bool, and the emitter's read-back check makes
   a future population loud. Deleting it would be relying on a co-occurrence
   nobody is enforcing.
3. **`dfa_seed_can_be_scan_head` reads `s1g[]` as well as `s1u[]`**, though
   only `s1u` is emitted as this engine's seed table. Deliberate
   over-answering; costs a folded compare. Say if the tree prefers the narrow
   read plus a comment.
4. **A mech sabotage row for (i)** is owed and not written (mech is forbidden
   under the hold). §4.2's sabotage A is the row's content, and the census
   check is already red on it — the row would aim at the emitted entry test.

---

## 7. THE abi SITE LIST (D94), FOUND BY GREP, NOT BUMPED

`rx_info.abi` is **20** on main (`b048fa61`; edge1's report says 19 and
predates [DD-13b.W1.3]'s merge). This branch is one abi event: the entry
test's emitted text moves on every seeded machine that carries a scan edge.
Every reader of the number, from
`grep -rEn '\.abi = |ABI_EXPECT|rx_info\.abi. is|RECURSION_IDENTITY_FILEPIN' src lib cli tests docs/spec Makefile`:

| site | what it is |
|---|---|
| `src/gen/emit_dfa.c:1662` | `".abi = 20,\n"` — the emitted value, the only producer |
| `tests/codegen/run_codegen_tests.sh:2758` | `ABI_EXPECT=20` |
| `tests/codegen/run_codegen_tests.sh:2760` | the bump narrative, which gains a `20->21` clause |
| `tests/codegen/run_recursion_identity.sh:699` | `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-8d68ddc2}"` — gate (B)'s pin, re-pinned to the MERGE commit |
| `docs/spec/match_api.md:159` | "`rx_info.abi` is `20`" |
| `docs/spec/match_api.md:1801` | "**`rx_info.abi` is `20` on every artifact today**", the per-bump narrative |

Two further hits are HISTORICAL cross-references and do not move
(`match_api.md:2190` "the abi-6 fields", `:2298` "the abi-17 statics"); they
are listed because D94's lesson is that a hand-enumerated list missed a fifth
reader in this exact file.

**COMPARISON (A) of `run_recursion_identity.sh`** extracts `goto <p>_L0;`
through `<p>_accept:` — the VM's own program. Nothing on this branch is emitted
inside that span: the entry test is written by `emit_scan_loop` inside
`pcrec_emit_dfa_engine`, which for a hybrid is called from the prefilter block
ABOVE the program marker, and a non-hybrid DFA artifact has no `goto <p>_L0;`.
(A) should be byte-identical and (B) re-pins. PREDICTION, not a measurement.

---

## 8. WHERE THE MEASUREMENT HARNESSES ARE

Scratch, not the tree:
`.../scratchpad/edge2/lad/` — `bench.c` (the find-all timing driver),
`run_ladder.sh`, `run_floor.sh`, and `c_before/` (`9d8401a`) and `c_after/`
(`b048fa61`) built. Both scripts REFUSE on `load1 >= 0.5` rather than
caveating, discard a round whose load rose, and drop a rung whose subject
never entered the chain (edge1's lesson as a floor rather than a note).
