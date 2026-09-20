# Frank's guided tour of the refactored tree — the list

Started 2026-09-20 (seventy-second session), the day after the code-review
refactor closed. Frank reads source files and asks questions; items land here
only when both agree. His lens: **readability, clarity, maintainability** —
not functionality or methodology. Each item names the file, the observation,
the agreed shape, and the proof that it changed nothing. Items are chartered
as lanes from here (plan rows cite `[TOUR-n]`). CODE-ORGANIZATION candidates —
structure replacing a convention or a parallel mechanism, where "not worth
it" is an acceptable answer — go to the separate list
`2026-09-20-code-org.md` (`[ORG-n]`).

## [TOUR-1] src/gen/emit_vm.c — pcrec_emit_vm reads at three altitudes at once

**Observation (Frank):** the function creates a `Vm` and spends a long
stretch setting it up before any emission; "could those activities be cleanly
put into an init_vm type function?" — then, applying the consistent-altitude
idiom: if it starts with an init and a plan, the last section should be a
subfunction too.

**Measured at 11ff5f51:** the function spans 9388-12196; 1,106 code lines
under 1,644 comment lines. The setup phase (9449-9660) is 44 code lines
under 162 comment lines and sets ~12 fields (cx/b/p, ngroups + pend_of via
the backreference marks, tracing, unroll_k, mrl, mrl_win, fmin, up, cg /
has_calls / nregion); nothing in it depends on anything computed later; its
only shared local is `GenNames g` (pointer parameter).

**Agreed shape, three parts:**
1. `vm_init(Vm *v, Ctx *cx, Ast *root, GenNames *g)` — 9449-9660.
2. Finish the plan extraction — 9661-9942 (slot counts, per-region passes,
   the totals, the caller-buffer sizing surface and fast-tier capacities);
   `vm_plan_capacities` (wave 2) already owns the capacity policy.
3. The emission tail as one function per SECTION OF THE ARTIFACT, in the
   artifact's order: prologue (9943-9974), `vm_emit_stamps` (9975-10620,
   ~650 lines, the most self-contained — start here), `vm_emit_storage`
   (10767-11115: storage types, sentinels, work charge, MRL forms, the
   PUSH/CALL macros), `vm_emit_search_body` (11116-11875: wiring, resets,
   the walk, fail label, the search entry with guards and retry advance),
   `vm_emit_entries` (11876-12121), epilogue (12122-12196: residual, info,
   listing, size publications). pcrec_emit_vm becomes eight or nine calls.

**Design question the lane answers, not assumes:** which locals cross the
seams (`tiered`, `fwd_entries`, `ncaps`, `bufs`, `mguard`, ...). Each moves
either into `Vm` as a PLANNED FACT or into a small per-phase struct the
earlier phase returns (the `VmCaps` precedent). `Vm` must not become a bag of
every local.

**And the essays:** the setup's 162 comment lines are mostly history (the
DD-14.EMPTY root-width comment alone is 55 lines, half of it a correction of
a correction). coding_guide.md §4.2: comments carry the invariant and the
why-not-the-alternative; HISTORY goes to docs with a pointer. Prune each
essay to its invariant + a pointer to the decision/plan row it narrates. This
is what actually shortens the file.

**Proof:** `scripts/emit_sweep.py --ref <branch point>` byte-identical on all
five streams (as every wave 2 step); anchors 285/285 re-aimed per row; not an
abi event. Tier: opus (engine code).

## [TOUR-2] src/gen/emit_vm.c — vm_cost's accumulation is written out by field, twice

**Observation (Frank, walking vm_cost):** the concatenation arm's cost
additions "could be fn(c, r|h)".

**As it stands (11ff5f51, vm_cost at 2298-2635):** `A_CAT` writes the same
six-line field-by-field accumulate block twice (the spine loop over `t->r`,
then the head `t`); `A_ALT` writes the same six lines with max in place of
plus, `1 +` on frames. `struct Cost` (2006) has no combining helper.

**Agreed shape:** `static void cost_add(Cost *acc, Cost r)` (frames/trail/
pf/pt summed, unbounded/growable OR-ed) — the `A_CAT` arm becomes one call
per spine element and one for the head; its sibling `cost_max(Cost *acc,
Cost r)` (field-wise max, OR-ed flags) with the `1 +` on frames left visible
at the `A_ALT` call site, so the two arms read as SUM versus ONE-PLUS-MAX,
which is the semantic difference the field arithmetic buries. Adjacent, same
lane: the `A_ALT` arm's inline flatten of the left-nested chain into a branch
array duplicates the walk `vm_alt` does at emission — one shared flatten
helper, if the two walks prove identical.

**Proof:** byte-neutral by construction; `scripts/emit_sweep.py --ref
<branch point>` 0 movers on five streams; the per-iteration fields (`pf`/
`pt`) are what `subject_ceiling` divides from, so the stamped ceilings in the
size log must not move either (0 movers by column). Tier: sonnet (mechanical
once the helper is written), or folded into [TOUR-1]'s opus lane.

**Step 2 (Frank): one pricing function per node kind, `vm_emit`'s own
precedent.** After the helpers land, `vm_cost`'s switch becomes a dispatcher
— `case A_REP: return vm_cost_rep(...)` is already the shape — with one
function per arm that has a body OR a correctness argument: `vm_cost_cat`,
`vm_cost_alt`, `vm_cost_call` (real bodies); `vm_cost_cap`, `vm_cost_atomic`,
`vm_cost_kreset`, `vm_cost_look` (2-4 code lines under 30-60 comment lines —
the comment becomes the function's HEADER, the form coding_guide §4.2 asks
for, instead of prose floating between case labels). The free-node kinds
(classes, anchors, word boundaries, `\G`, backreference) stay one shared
`return c` group — a function returning zero for six kinds is ceremony. The
payoff beyond length: `vm_cost_<kind>` sits beside `vm_<kind>`, the emitter
arm it must agree with, so the two-walk contract is checkable pairwise.
Order: helpers first, then the split, so the arms are born short.

## [TOUR-3] src/parse/parse.c — p_class "was written by blood"

**Observation (Frank):** a lot of history comments. Measured at 1994eab9:
p_class 980-1265, 286 lines, 111 code / 167 comment, 24 comment blocks —
five tagged [M4-QUOTING], six [M5.0 stage n], plus K12 (the endpoint rule),
R9 (range endpoints), MOD-0.3c (produced members).

**What to keep, what to prune:** most blocks END in a measured PCRE2 cell
(`[a\t-\tz]` is a-z; `[\Q^\E]` does not negate; `[[:alpha:]-z]` is 150;
`[\Qa-b\E]` is {a,-,b}) — under D26 those cells ARE the contract and the
oracle tests behind them are what makes the function changeable; they stay.
The wave narrative around them ("THE FIX-3 BLOCK THAT STOOD HERE IS GONE",
"this comment used to say", who found what when) goes to the decision or
plan row with a pointer (coding_guide §4.2).

**The structural cause of the length:** the four-way MEMBER DECODE (quoted
byte / escape via esc_class_value / high byte via lit_next_cp / plain byte)
is written twice — once at the item-loop top for the low endpoint
(~1057-1110), once inside the range arm for the high endpoint (1124-1140),
and the inline quote-open MIRROR exists only because the second copy is not
at an item boundary. Agreed shape: (1) one `cls_read_member(cx, &claim,
&quoted)` used at both sites — removes the mirror, the duplicate decode and
the two comments explaining why they differ; (2) the range arm (dash
lookahead → interval add, 1113-1148) as `p_class_range`; (3) the pruning
above, cells kept verbatim.

**Proof:** tests/classes + the reject table + the registry checks (semantics),
`scripts/emit_sweep.py` 0 movers (an unchanged AST emits identical C).
Tier: sonnet with an opus review of the member reader's claim handling
(the deferred-refusal ordering, steps 1-4 of the K12 endpoint rule, must
survive the extraction exactly).

## [TOUR-4] src/ir/dfa.c — DFA_INVARIANT aborts the caller on the compile path (r61 F1)

`DFA_INVARIANT(cond)` (dfa.c:274) is `abort()` in the shipped build, at two
sites in the closure walk (clo_open's "loop not already open", clo_walk's
"the open loop is the stack top"). Its comment's justification ("this file's
existing idiom — tab_grow, intern") is STALE since K7 moved both to
`pcrec_ctx_nomem`; docs/spec/match_api.md:3345 promises "It never abort()s
the caller on the compile path", and these are the only two aborts reachable
from `pcrec_compile`. **Agreed shape:** `DFA_INVARIANT` → `pcrec_ctx_fail(cx,
0, "internal error: ...")` carrying each invariant's text (the macro needs
`cx`; both sites have it through `Clo`/`CloScratch` or a parameter); the
stale comment rewritten; a K-row (K61) recording the contradiction and its
close; the spec unchanged because the fix makes it true. Same detection,
fuzzable, caller survives. Proof: make test + emit_sweep 0 movers (no emitted
byte depends on it) + a sabotage row that forces the invariant false and
expects the refusal. Tier: sonnet.

## [TOUR-5] src/opt/select_engine.c — the engine_sel ladder and the dead discharge loop (r61 F2)

pcrec_select_engine: 117 code lines under 424 of comment (the tree's highest
churn ratio). **Agreed shape:** (a) `esel_of(const EngineFit *, const Ctx *)`
— the nine-arm `engine_sel` ladder (537-592) as its own function, its header
stating the NON-OVERLAP argument ONCE as a table (arm → the condition that
excludes every arm below it), replacing the five stacked comment blocks
([OPT-4], [OPT-4.1], [OPT-4.2], [LIM-1], [K53-SELRETRY]); add the one
unasserted premise as a check — size-drop rung and overflow rung mutually
exclusive (`size_drop_rung != SDR_NONE` implies `!dfa_disabled`), internal
error if not; (b) `prefilter_decision()` — the block at 206-482; (c) DELETE
the `discharge` fixpoint scaffolding (98-110): no hook registered, the one
customer moved to compile.c in wave G, `rewrote = true` never publishes a
root (D77). Also r61 F6: `vm_counter_fits` reads PCREC_NO_COUNTER inside the
predicate while the cursor/revdet deny flags are read by callers — make the
three alike (emit_vm.c, same lane or [TOUR-2]'s). Proof: the registry stamp
checks, tests/axes (the axis deny/force matrix is this function's contract),
emit_sweep 0 movers, make test. Tier: opus.

## Manager's assessment — 2026-09-20, seventy-third session ([TOUR-EXEC])

Frank's ruling: assess, do the worth-it items, forgo the unimportant ones.
One paragraph per item; every DO becomes its own plan row citing this file.

**[TOUR-4] — DO (sonnet, wave 1).** A spec promise is currently false
(match_api.md "never abort()s the caller on the compile path") and the
comment defending the abort cites an idiom the tree abandoned at K7. Three
sites, not two (dfa.c:590, 667, 857 at 82dd396a). Cheapest item on the list
with the highest contract value. Ships with the K61 row and a sabotage row.

**[TOUR-5] — DO (opus, wave 1).** The ladder is correct today and defended
by five stacked comment blocks; the next change to select_engine is the
exposure. esel_of with the non-overlap table as its header, the one
unasserted premise made a check, prefilter_decision extracted, the dead
discharge fixpoint deleted (D77: no hook, no customer). r61 F6 (the deny
flag read inside vm_counter_fits) lives in emit_vm.c and goes to the
TOUR-2 lane instead, so emit_vm.c has ONE writer at a time.

**[TOUR-2] — DO (sonnet, wave 1), both steps.** cost_add / cost_max make
the CAT and ALT arms read as SUM versus ONE-PLUS-MAX; then the per-kind
dispatcher so vm_cost_<kind> sits beside vm_<kind>. The shared alt-flatten
helper only if the two walks prove identical — the lane reports the
comparison either way. F6 rides here. Byte-neutral by construction; the
size log's stamped ceilings are the second proof column.

**[ORG-7] — DO (folded into the TOUR-4 sonnet lane).** Nine exports with
no reader → static, the internal.h declarations deleted. Locations at
82dd396a: tune.c (1), emit_dfa.c (3), nfa.c (1), mod_verbs.c (1),
rxt_schema.c (2), rxt_source.c (1). None of those files is touched by the
other wave-1 lanes. Gate: make strict + the export census check.

**[TOUR-1] — DO (opus, wave 2, after TOUR-2 merges).** The largest and the
one the file-grain experiment says pays most: the read cost of emit_vm.c
is the one giant function, not the file. vm_init / the plan tail / one
function per artifact section / essay pruning to invariant + pointer.
Sequenced behind TOUR-2 because both edit emit_vm.c. The seam-crossing
locals are the lane's design question (Vm as PLANNED FACTS, VmCaps-style
per-phase structs — never a bag of locals).

**[TOUR-3] — DO (sonnet with opus review, wave 2).** One member reader at
both endpoints removes the quote-open mirror and the duplicate decode;
the range arm extracted; every measured PCRE2 cell kept verbatim (D26:
those cells are the contract). The opus review is scoped to the claim
ordering of the K12 endpoint rule surviving the extraction. parse.c has
no other writer, so it could run in wave 1, but the lane cap is three.

**FORGONE: r61 F3 (callgraph's three fixpoints in one loop) and F4/F5
(comment notes).** Not on the tour list; F3 is correct code whose only
cost is a comment; trigger to revisit = the next change to
src/ir/callgraph.c's fixpoint. F4/F5 ride whichever lane next touches
their files, unchartered.

Order: wave 1 = TOUR-4+ORG-7 (sonnet), TOUR-5 (opus), TOUR-2 (sonnet).
Wave 2 = TOUR-1 (opus), TOUR-3 (sonnet + opus review). Merges serialized
through the manager with `make test` between; no battery is in flight.
Branch point for every lane: 82dd396a.
