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
