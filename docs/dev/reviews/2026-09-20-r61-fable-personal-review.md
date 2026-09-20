# r61 — a personal review of the five most complicated sections (Fable, 2026-09-20)

Frank: "most of this code was written and reviewed by sonnet or perhaps opus.
please select the 5 most complicated sections of the repo and do a personal
review of them rather than just a manager perspective." Selection by
measurement (function census: code lines, nesting depth; comment-to-code
ratio as a churn signal, Frank's addition), weighted to the semantic core:

| # | section | code | comment | why |
|---|---|---|---|---|
| 1 | src/ir/dfa.c — the priority subset construction (clo_walk, closure, intern, make_state, pcrec_build_dfa) | ~600 | ~700 | the correctness heart: leftmost-first semantics as a DFA |
| 2 | src/opt/select_engine.c — pcrec_select_engine | 117 | 424 | highest churn ratio in the tree (3.6); the routing the bench keeps finding |
| 3 | src/gen/emit_vm.c — vm_revdet_rep (+ vm_rev_canmove) | 171 | ~140 | an optimisation rung that rewrites captures after the fact |
| 4 | src/gen/emit_vm.c — vm_counter_rep / vm_counter_phase | 112+112 | ~150 | the unroll-K rung: two phases, one trailed slot, runtime MRL |
| 5 | src/opt/callgraph.c — build, the three fixpoints, cg_eligibility | ~200 | ~450 | recursion semantics: greatest fixpoints, splice budgets |

I read each in full, comments included, with the callers I needed
(compile_driver's retry decision, vm_rev_caps, revdet.c's eligibility). This
is what I found, ranked by how much I would act on it. Confidence is stated
per finding; "verified" means I checked the code path, not the comment.

## Findings, ranked

### F1 (act on it) — dfa.c aborts the caller's process on the compile path, against the spec

`DFA_INVARIANT(cond)` (dfa.c:274) is `abort()`, used twice in the shipped
build: `clo_open`'s "loop not already open" check and `clo_walk`'s
"the open loop is the stack top" check. Its own comment justifies the idiom
as "this file's existing idiom (tab_grow, intern)" — **stale**: K7 moved
both of those to `pcrec_ctx_nomem`/longjmp precisely so a library caller is
never aborted, and docs/spec/match_api.md:3345 now promises "It never
abort()s the caller on the compile path." These two are the only `abort()`
reachable from `pcrec_compile` (arena.c/sb.c's are on DETACHED buffers).
The checks are premises of a termination argument and the author says a
future construct breaking proper loop nesting is the only thing that would
fire them — which is exactly the situation where a clean `pcrec_ctx_fail(cx,
0, "internal error: ...")` is worth more than a core dump: same detection,
the fuzzer and the corpus can FIND it, and the caller survives. Verified.
**Proposed: K-row + a one-line fix (`DFA_INVARIANT` → a `pcrec_ctx_fail`
with the invariant's text), spec unchanged since the fix makes it true.**

### F2 (act on it) — pcrec_select_engine's engine_sel ladder is held together by non-overlap arguments in five comment blocks

Lines 537-592: a nine-arm conditional whose correctness rests on
"this arm CANNOT OVERLAP with those below" claims made in [OPT-4],
[OPT-4.1], [OPT-4.2], [LIM-1] and [K53-SELRETRY] comments, each amending
the previous one. I checked the premises I could: "`force_on` is always
false whenever `dfa_disabled` is true" — TRUE, compile_driver's
`ovf_eligible` requires `!PCREC_FORCE_PREFILTER` (verified). "The size-drop
rung and the overflow rung are mutually exclusive by engine" — plausible
(drops are DFA-engine, overflow makes the engine VM) but asserted nowhere;
if both ever held, `ESEL_SIZE_CAP_RETRY` would hide the overflow. The
function is 117 code lines under 424 of comment and is the code most likely
to be wrong the next time it changes. **Proposed (tour, opus): (a)
`esel_of()` — the ladder as its own function with the non-overlap argument
stated ONCE as a table in its header; (b) the prefilter decision block as
`prefilter_decision()`; (c) DELETE the `discharge` loop (lines 98-110): no
hook is registered, the one customer moved to compile.c in wave G, and the
`rewrote = true` that never publishes a root would spin `SELECT_MAX_ROUNDS`
if anyone registered one — dead scaffolding built ahead of need (D77).**

### F3 (act on it, small) — callgraph.c's three fixpoints are one loop written three times

minw / cwmin / cwmax: identical 18-line round loops (init ⊤, publish,
re-evaluate each body, `changed`, the `round == n` internal error) differing
in the init value, the publish callback and the evaluator. The direction is
RIGHT in all three — descent from ⊤ computes the GREATEST fixpoint, which is
the truth on a DAG and the safe over-estimate on a cycle (∞ minw = empty
language, ∞ cwmax = unbounded), and I checked the awkward cases
(`X = a X`, `X = X | b`, `X = X a | b`). But three copies of a round bound
and a failure message is how one gets a fix in two of them. **Proposed:
`cg_fixpoint(cx, cg, top, publish, eval, what)`; byte-neutral.**

### F4 (note) — cg_eligibility's budget drop leaves stale expansions

After the total-budget loop drops target j from splicing, every caller i's
`exp[i]` still includes j's expansion (computed while `splice[j]` was true),
and `splice[i]` was decided against that larger figure. Direction:
CONSERVATIVE (over-estimates, may decline a splice that would now fit, may
drop one more target than needed) — never unsafe. Worth one sentence at the
loop, or a recompute if the budget ever binds in practice; today
PCREC_MAX_SPLICE_TOTAL is not reached by the corpus (my reading of the
lanes' reports; not re-measured).

### F5 (note, praise) — the three rungs and the DFA construction are internally consistent

I went looking for the classic defects and found them handled:
- revdet: capture writes suppressed in the forward scan would break a body
  that READS a group (`(?:(a)\1)*`) or resets the start (`\K`) — revdet.c
  DECLINES A_BREF, A_KRESET, A_CALL, A_LOOK and >PCREC_MAX_REVDET_BODY_GROUPS
  (verified at revdet.c:126/201/208/322/359). vm_rev_caps' silent truncation
  at `cap` is therefore unreachable; a one-line assert-by-ctx_fail there would
  make that structural rather than a cross-file fact.
- revdet's greedy retreat cannot go below rmin: the push is gated on
  `scan_position > slot_values[sl]` (the low-water after rmin iterations) —
  correct, and `iteration` is deliberately never read at the commit.
- counter: ONE trailed slot serves both phases (the optional phase's reset is
  a trailed write, so a resume into a mandatory-phase frame recovers the
  count); the runtime MRL expression `count - (i+1) - slot_values[ctr]`
  agrees with the compile-time residue arithmetic at the last trip — I
  re-derived both. The `residue == 0` tail-label emission (the trip guard
  still jumps to it) is the kind of thing a refactor loses; keep the comment.
- dfa.c: the source list is read ONCE before `make_state` can realloc `d->st`
  (worklist loop) — correct; `endvar` canonicalized against the EOL view, not
  the base, is the load-bearing line and it is right; the global `emitted`
  dedup across contexts is sound because priority order = first occurrence.

### F6 (note) — vm_counter_fits is the one rung predicate that reads the option flags

`vm_counter_fits` checks `PCREC_NO_COUNTER` itself; `vm_cursor_fits` /
`vm_revdet_fits` are pure shape predicates and their deny flags are checked
by the callers. Three walks call these in a fixed order ([ORG-1]); a deny
flag read in one predicate and outside another is how the ladder's
three copies drift. Move the flag to the callers or into all three.

## What I did NOT find

No wrong answer, no unsound over/under-charge, no reachable crash other
than F1's abort, in ~1,400 code lines of the hardest code in the tree. The
comment load is where the risk lives now: F2's ladder is correct today and
is defended by prose; the next change is the exposure.

## Dispositions for Frank

- F1: file as K61 and fix (sonnet, one lane, an hour) — a spec promise is
  currently false.
- F2: [TOUR-4] (opus) — esel_of + prefilter_decision + delete the discharge
  loop; proof = registry stamps + emit_sweep 0 movers + tests/axes.
- F3, F6: fold into the same lane or a sonnet admin lane; byte-neutral.
- F4, F5: comments only, ride whichever lane next touches the file.
