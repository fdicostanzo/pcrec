# lifetime findings (r108 arenaemit)

## Findings

### LIFE-1 CONFIRMED (size, design) - the selection-time TWIN of the scoped scratch stays on the parent: `pcrec_clskit_whole_bytes` materializes the same `build_pages` tables on `&cx->arena`
- Where: src/gen/clskit.c:446 `pcrec_clskit_whole_bytes` (P2/P3 arms call `build_pages(a, ...)`), reached through `whole()` (:614)
  from `pcrec_clskit_select` (:693) with the caller's arena. Sibling sites by grep (`pcrec_clskit_select(&...cx->arena`):
  4 = src/gen/emit_vm.c:1610, :1678 (the wide sets, `vm_wcls`), :1889; src/gen/emit_dfa.c:13154.
- Shape: identical to what SCOPE-4 scoped. The price materializes P3 (and at `--tune=2` P2) "so the price and the emitted
  table cannot disagree" (the :441 comment), and only a scalar (`out->bytes`) survives; the mask/first/pidx/leaf/intern
  slot/blocks arrays are dead at return but live to the end of the compile on the parent. Worse than the emitter's
  twin: it runs for every wide set whose row reads `whole()` (mid gate, size-page3, speed rows), INCLUDING sets whose
  chosen form is the kit (they are priced and never emitted whole).
- Repro (measured, scratch driver lifetime/drv/meas.c linked against each tree's build/libpcrec.a; a 650-range synthetic
  set 0x41..0x1e808, arena `used` deltas): partition 30,448 B; select's pricing 74,128 B at tune -2/-1 (form K chosen);
  `emit_whole(P3)` 74,176 B on BASE, 0 B on SUBJECT. So SCOPE-4 removed one of two equal-size copies; the other is
  still there wherever P3 is priced (every whole-form wide set at the default tune, since `mid_gate` prices P3 first).
- Fix shape: `pcrec_clskit_whole_bytes` takes `Arena *parent` and gets F2's shape (the `n <= 0` return first, scope only on
  the PAGE2/PAGE3 arms or for all, static body on the child, close); its result is a scalar, so nothing outlives the
  close by construction. Callers unchanged (`SelCtx.a` is the caller's non-child arena; the clskit driver's detached
  `a`). Expected effect: the f3 movers fall roughly a second time by the same order (the body prices the same sets).
- Effort: small (one function + its two reads in clskit.c; a sabotage row of S3644's shape; memgate is the net, the
  same levers). Blast radius: clskit.c only; emitted C byte-identical by construction (a price is a number).
- Not the same shape (listed, not proposed): `pcrec_clskit_partition`'s DP scratch (best/from/pick/bp/bm, ~30 KB here)
  is dead at return too, but `out->sec` must live on the parent, so it is a mixed-lifetime split, not a pure-scratch scope.

### LIFE-2 CONFIRMED (doc) - the route sentence names an emitter that never reaches `pcrec_clskit_emit_whole`
- Where: src/gen/clskit.c:1196-1202 (the new comment: "compile.c's pcrec_emit_vm/pcrec_emit_dfa, are its only compile
  routes") and docs/design/arena_scopes.md "SCOPE-4 BUILT" ("compile.c's `pcrec_emit_vm`/`pcrec_emit_dfa`; r107 C").
- Fact by grep: `pcrec_clskit_emit_whole(` has ONE src caller, emit_vm.c:13347 in `vm_emit_search_body`, whose one call is
  emit_vm.c:14572 in `pcrec_emit_vm`, whose one call is compile.c:3389 inside `compile_driver`'s attempt (handler
  compile.c:2578, unwind :2583). emit_dfa.c calls `pcrec_clskit_emit_kit` (:13225) but never `emit_whole`. The sentence
  was carried over from `emit_kit`'s comment, where both emitters are true. The conclusion ("its sole compile route is
  the attempt") HOLDS; only the named route set is wider than the fact, so a future reader auditing a DFA change would
  look for a client that is not there. Fix: name `pcrec_emit_vm` alone in both places. Effort: two words. Blast: none.

### LIFE-3 SUSPECTED (design, no code now) - GENERAL FORM: "pure-scratch child-arena scope around a callee" has 3 members; a 4th (LIFE-1) is the trigger for a scanner rule, not a helper
- Members by grep (`pcrec_scope_arena(`, 3 src sites): clskit.c:1133 `emit_kit` (body inline), clskit.c:1209 `emit_whole`
  (static body), mod_uprops.c:297 `uprops_produce` (no empty guard; its result is COPIED out by the callee before the
  close). The literal "empty guard + scope + static body + close" form has 1 member (emit_whole), 2 if emit_kit's body
  is counted. LIFE-1's `pcrec_clskit_whole_bytes` would be the 4th child-arena client and the 2nd of the literal form.
- Helper: NOT worth it. C has no closure, the four signatures differ, and the open/arena/close is 3 lines; a
  callback-taking helper would replace 3 readable lines with a function pointer plus a context struct per client (the
  house "general mechanism" bar is not met by a wrapper that removes nothing). The shared FACT worth stating once is
  the escape rule: nothing the child allocates is stored through a parameter, a field, or returned. Today that rule is
  held by reading (I traced it for emit_whole: see PROBED) and by L4 for Ctx/Job fields only.
- Unlock + trigger: when LIFE-1 lands (4 child clients), add ONE scanner rule beside L2-static: in a function that calls
  `pcrec_scope_arena`, the child's variable is passed only as a call argument (never assigned to a member, through a
  pointer, or returned). Grep-level, no flow analysis; its fixture is a planted `w->x = pcrec_arena_alloc(child, ..)`
  through an out-param. LIMIT, stated: it checks the opening function only; the body's own out-params into LOCALS
  (`build_pages(a, .., &w)` filling a stack `WholePages`) are legal and a grep cannot tell them from an escape, so the
  rule is a tripwire at the open site, not a proof. Until the trigger: no action.

## PROBED-AND-HELD

- (1) NOTHING OUTLIVES THE CLOSE (traced, all three arms + callees): every child allocation is `b` (B1), the `WholePages w`
  arrays (a STACK local, filled by `build_pages`/`intern_records`), and the `pcrec_sb_fragf(a, ..)` names; each is
  read only by `emit_array`/`pcrec_sb_printf`, which COPY into `c`. Nothing is stored into `c`'s struct, a Vm/Ctx/Job
  field, a name table, or returned (the function is void; `fn` comes in from the caller's parent arena, emit_vm.c:13344,
  allocated before the open). `c`'s own growth: sb.c `sb_store` (heap, or `c->ar`, never the child: `c` exists before
  the scope); no sb.c path the body reaches allocates on `c->cx->arena` (the one such site, sb.c:710, is the stamp
  filter, not reached). The child is zeroed like the parent (`pcrec_arena_alloc` either way), so B1's `|=` holds.
- (2) EVERY EXIT RELEASES ONCE, LIFO: normal return -> close (top==below post-condition in arena.c holds). Refusals in the
  body (child-arena nomem via `child->cx = parent->cx`; the size-term ladder trial, sb.c:49-51 `abort_over` ->
  `pcrec_ctx_fail`, reachable from `emit_array`'s printf mid-table) longjmp to compile.c:2578, whose first act is
  `pcrec_scope_unwind(&cx.arena)` (:2583), including the FIT_FORCE_NEXT resume. No scope is open on `cx->arena` around
  the call (grep: the 7 opens are minimize, uprops, part_layout, 2x memfn_stamps, emit_kit, emit_whole; all
  open-and-close in one function, none encloses `pcrec_emit_vm`); in the wcls loop emit_kit and emit_whole each close
  before the next iteration; no body callee opens a scope (and L5 would refuse one on the child). The count/syntax_dump
  handlers (compile.c:3913, syntax_dump.c x3) are parse-only: they never reach an emitter. Nested compile (D-4/S21): the
  inner `compile_driver` has its own Ctx and arena, so an inner emit_whole scopes on the inner arena; no lent use.
- (3) STATED FACTS: "sole compile route is the attempt" HOLDS (LIFE-2: but via pcrec_emit_vm only). "the tests/clskit
  driver owns its arena" HOLDS (clskit_driver.c:169 `Arena a = {0}`, detached, freed :228 by `pcrec_arena_free`, which
  releases the registry). EMITTED C BYTE-IDENTICAL BASE vs SUBJECT: 98 build/pcrec pairs (196 compiles), 0 diffs: 35
  patterns at default tune, 15 synthetic sets, 50 patterns at `--tune=2` and `--tune=-2`, 3 large degrade-ladder patterns
  (42-97 KB artifacts), 4 identical refusals; forms reached through the CLI: P3 (33+ compiles) and P2 (16, at tune 2),
  plus `(?i)`, alternated and nested classes; B1 is not chosen by any CLI probe I found, so B1/P2/P3 were driven
  directly: scratch driver lifetime/drv/whole.c (12 sets x 3 forms + the empty set, 37 matchers, 92 KB) linked against
  each tree's libpcrec.a under ASan+LSan: outputs byte-identical, no leak, `a.open` NULL after every call.
  F3 MOVERS ALL DOWN: my two memgate samples (MG_ENC=1 MG_ENG=2, base->subject): first 1,500 items 0 movers (as f3 saw for
  its first 2,000); strided `--shard 3/5` 1,480 items: 24 movers, ALL DOWN (min -262,360 B), 0 up, 0 errors, arena
  high-water lowered on 24 raised on 0 (consistent with f3's 108 of 7,402). The coordinator's full logs had not landed
  when I finished.
- Largest witness: memgate corpus compile at 2,447,584 B peak (unchanged), largest mover -262,360 B; largest emitted
  artifact 96,897 B.

CRITIC COMPLETE
