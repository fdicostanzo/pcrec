# Scoped arenas registered on the Ctx ([ARENA-SCOPES]): architecture note
STATUS: DRAFT (lane arenaarch, 2026-11-24; for the `pcrec-critic` ARCHITECTURE round)
FORM: full   (trigger: at least 4 existing decision sites touched (S1 `pcrec_arena_alloc`'s error-channel branch, S3 `pcrec_arena_free`'s owned walk, S4 `job_cleanup`, S9 the two storage transplants' heap-only free); mechanisms added: one new record (a scope: an arena with a lifetime nested in another's) and its registration)
TREE: T = 15e37b00510f64272dbb2e2c46cd3606674494f1 (main, "land k155fix: ARENA-SCOPES refs, K155 status")   REQUIREMENTS: plan row [ARENA-SCOPES] @T; the owner's words of 2026-11-24 (as the brief and the row quote them); D203 (docs/dev/decisions.md @T); known_issues.md K155 @T (FIXED in general form, merge d69bdc2af); review `docs/dev/reviews/2026-11-24-r96-k155code.md` @T (GENFORM-5, GENFORM-8/9, COST-1, COST-2); `docs/dev/lanes/k155fix2_report.md` @T (COST-1's fix and its loop census); src/core/CLAUDE.md @T (arena-backed builders)   REGISTER READ: `docs/dev/guide/architecture.md` register @T, and `docs/design/stream/roadmap.md` @T (register row 12)

Every command runs from any checkout with `T=15e37b005`. `GG` is `git grep -n PATTERN $T -- PATHS`, `GS` is
`git show $T:PATH`. No command reads the working tree.

## Goals served

- **Goal 1 (one home per question).** The question "what dies when this piece of work ends, on a return AND on a
  longjmp?" has at least seven hand-kept answers at T (review r96 GENFORM-8's list, re-counted in the site map: the
  attempt arena S1, its `owned` list S3, `job_cleanup`'s named list S4, the memo's compile-lifetime arena S7 with
  five hand frees, the hand-freed tables in `minimize.c` S13 and `scanedge.c` S15, the caller-owns hooks S16, and
  the private arena in `clskit.c` S14). The feature adds an eighth unless it is built as the general form of the
  first three (section "The general form"). It serves goal 1 only in that form.
- **Goal 2 (data with its writer; accessors).** Two units outside `sb.c` write a StrBuf's storage fields by hand
  and `free()` the old bytes (S9). A scope makes those bytes arena bytes, so the transplant has to move into its
  owner (`sb.c`) first: remodel RM-1.
- **Goal 3 (seams).** The kit seam `mf_arena` (S17) is backed by the attempt arena and its contract says the
  memory lives until pcrec's arena dies. The feature must not hand a scope across it; no new fact crosses it.
  Layer direction: the clients (opt/, gen/) call down into core/ (`arena.c`, `sb.c`); no new upward call.
- **Goal 4 (remodels ride along).** RM-1 rides first. Register row 20 rides first only on one design choice (S5).
  Register row 7b would delete two of the clients outright (section "Register rows looked up"), so the scope's shape
  must not be built around them.
- **Traded against.** Nothing is traded at the architecture level. The speed gate (no existing regex gets slower)
  binds the build: peak memory and compile time are measured on R-3's families. Emitted bytes must not move.

Standing questions (docs/design/CLAUDE.md). (1) Measurement regime: RELEVANT. The feature's benefit and its gate
are peak memory (R-3's +7-12% in the job arena; r96's massif and peak-RSS witnesses) and stranded heap
(`tests/core/alloc_check.c`, the growth sweep's library stage under LSan). (2) Independent control: RELEVANT.
The allowlist scanner (`tests/core/scratch_builder_check.py`) reads the source; `alloc_check.c` and LSan read the
running allocator. They are two different sources, and the second is the control on the first. (3) What moves
when data is regenerated: NOT relevant. No table, measure set or oracle store is read.

## Requirements read

- The owner, 2026-11-24 (verbatim, as the brief quotes it): "the arena memory system is in my mind a stack memory
  extension system. Not proscribed: If arenas were registered such that the exit could free them, then they could
  be allocated up and deallocated down the stack with the registration used to clean up on exit. You could then use
  them for special areas like minimization". Then "arena-scopes-go: yes".
- Plan row [ARENA-SCOPES] @T: "scoped arenas registered on the Ctx: freed LIFO on the way out, all at once on a
  longjmp". The clients it names: K155's three whole-artifact rewrites, `minimize.c`'s tables, `clskit.c`'s local
  arena; "maybe job_cleanup's free() list". Its next line asks for a short design (API, LIFO discipline, what
  job_cleanup's list becomes) and a critic round, then an opus build lane.
- D203: a bug is handled at the CLASS level. K155's class is "a resource live across a refusal that nothing frees
  on the longjmp". The scopes are that class's general mechanism for TEMPORARIES. The arena-backed builder
  (K155's fix) covers results that live as long as the attempt.
- K155 @T: FIXED in general form. Three whole-artifact rewrites stay heap by ruling R-3 (+7-12% peak in the job
  arena) "until [ARENA-SCOPES]". Their witnesses still leak until then, and `alloc_check.c` names
  `target_headers_render` as a FILED stranding.
- Review r96: GENFORM-5 and COST-2 (the two raw storage swaps; "one sb.c primitive that moves or copies storage by
  `.ar`"), GENFORM-8/9 (the general form: "one Ctx registry of {pointer, free fn} with scope marks AND a release
  operation"; unlocks with triggers; "resource entries only at a second member"), COST-1 (an arena-grown StrBuf
  never frees its old blocks: a builder re-grown in a loop retains the sum of its calls).
- COST-1 @T: fixed at its one super-linear site by k155fix2 (each key rendered once, `Ctx.var_exp_keys`). Its
  loop census found 4 linear-per-item sites and "No site needs a scoped arena" (k155fix2_report.md). So COST-1's
  CLASS (grow-by-copy retention in an arena) is open as a mechanism question, but it has no live super-linear
  member at T.
- The growth sweep's 13 leak shards (cloud run 45492837175): per the journal (11-24 17:26, growtri), 32,768 B
  each (65,536 B on one shard), byte-identical to grow9fix's set. The CI stacks stop at `__wrap_realloc`. Which of
  the three rewrites each one is: **REQ-OPEN leak-attribution** (a `fast_unwind_on_malloc=0` repro, an input
  for the design step). The note counts them as members of the three-rewrite client set, not as new sites. That is
  the journal's claim; this note did not re-run it.
- RULINGS THIS NOTE CROSSES: D19 (thread safety: "All per-build state is arena memory owned by the Job"; a
  per-Ctx registry keeps that), D56 (job_cleanup's wholesale free is why K7's longjmp leaks nothing; minimize was
  the one exception), D105 (emit_state_legend's scratch moved INTO the job arena: retention accepted for
  simplicity, the opposite trade from R-3), the R-3 ruling of lane k155fix, D203. Also src/core/CLAUDE.md's
  "one setjmp" and "cross-attempt state is plain Ctx fields, not arena text". Found by
  `grep -n -i -E 'arena|job_cleanup|longjmp' docs/dev/decisions.md` (30 hits read; D19, D56, D105 are the ones
  that bear on the feature). Superseded or already built at T: nothing of the row. `git log --grep=ARENA-SCOPES`
  shows only plan edits and k155fix's allowlist and comment commits.
- VOCABULARY (each grepped, section "Site map" commands): `Arena`, `ABlock`, `AOwn`, `pcrec_arena_alloc`,
  `pcrec_arena_free`, `pcrec_arena_own`/`_own_slot`, `Ctx.arena`, `DfaMemo.arena`, `RxtSource.arena`,
  `StrBuf.ar`, `pcrec_sb_scratch`, `sb_store`/`sb_unstore`/`sb_grow`, `pcrec_sb_take`, `job_cleanup`, `setjmp`,
  `pcrec_ctx_nomem`/`pcrec_ctx_fail`, `mf_arena`, `kb_reserve`, `fh_arena`, `arena_regrow`, `fq_push`,
  `cont_push`, `ALLOW` (scanner), `known_stranded` (alloc_check). Zero hits: `scope` as an arena term (a new shape).

## Site map

| # | site (file, function or table) | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| S1 | `Arena` record, internal.h (`typedef struct { ABlock *head; Ctx *cx; AOwn *owned; } Arena`); `pcrec_arena_alloc` arena.c (error channel: `a->cx` then `abort()`) | C-1, C-2 | one flat block list per arena, freed only wholesale; no parent, no nesting | WIDEN (the feature's own new shape: a nested lifetime). Generic writers: the 9 `Arena a = { 0 }` / `{ .cx = ... }` locals and 3 struct fields (C-2), `m->arena.cx = cx` (dfamemo.c, C-7), `pcrec_arena_free`'s reset | "A shape states the inputs it covers" |
| S2 | the comment on `Arena` in internal.h: "there are none today; every Arena is a Ctx's own" | C-2 | FALSE at T: 9 detached locals plus `RxtSource.arena` have no Ctx | (drift, rewritten by the feature's S1 unit; not AS-IS) | "No silent defaults" |
| S3 | `Arena.owned` / `pcrec_arena_own_slot` / `pcrec_arena_own` (arena.c), one caller compound.c | C-3 | a list, in the arena, of heap blocks freed with it (K155) | SHARED: "what else dies with this arena" already has this one answer, so a scope's registration is the same question. The design says which survives | "One question, one primitive, from the second caller" |
| S4 | `job_cleanup` compile.c | C-4 | 27 `free()` of Job heap arrays + 6 `pcrec_sb_free` + `free(job)` + `pcrec_arena_free(&cx->arena)`; called on success and every longjmp | SHARED, CONDITIONAL: the teardown a longjmp reaches, so "all at once on a longjmp" lands here or in `pcrec_arena_free`. SHARED with S3 if the design turns the named list into registrations | goal 1; "Notice siblings" |
| S5 | the five `Ctx` instances and their teardowns: `compile_driver`, `pcrec_count_groups` (compile.c), three in syntax_dump.c (12 hand `pcrec_arena_free(&cx.arena)`) | C-5, C-1 | each frees its own arena by hand; register row 20 counts the copies | SHARED, CONDITIONAL: if scopes register on the CTX, every teardown copy must release them (row 20 rides first). If they register on their PARENT ARENA, `pcrec_arena_free` covers every copy and row 20 is not carried | "One question, one primitive" |
| S6 | `compile_driver`'s `setjmp` handler (compile.c, `if (setjmp(cx.jb))`) | C-6 | reads Ctx fields (`fit_labels(&cx)`), then the attempt's cleanup | AS-IS if release happens inside S4/S3. Its reads happen BEFORE `job_cleanup`, and any arena text they read must not sit in a released scope (hand-off D-4) | src/core/CLAUDE.md "one setjmp" |
| S7 | `DfaMemo.arena` (internal.h; dfamemo.c), freed by 5 hand calls in compile_driver | C-7 | an arena that lives ACROSS attempts (compile lifetime); `.cx` re-pointed per attempt | AS-IS (not a client: it is the level ABOVE the attempt, not below it). A member of the lifetime family; unlock U3 | "Notice siblings" |
| S8 | StrBuf storage by `.ar`: `sb_store`, `sb_unstore`, `sb_grow`'s scratch branch, `pcrec_sb_take` (sb.c) | C-8 | a two-way choice, heap or "this arena" | AS-IS if a scope is presented as an `Arena *` (the existing `.ar` branch takes it unchanged); WIDEN if the design makes a scope some other type | "One table per slot" |
| S9 | the two storage transplants: `target_headers_render` (memfn_stamps.c: `free(c->p); c->p = nb.p; c->len = ...; c->cap = ...`) and `render_buf` (part_layout.c: `sb->p = o.p ... free(old)`) | C-9 | another unit writes a StrBuf's storage fields and `free()`s; correct only while both sides are heap | ACCESSOR (primary: storage fields written outside `sb.c`), SHARED (secondary: one move/copy-by-`.ar` primitive, r96 GENFORM-5/COST-2). Remodel RM-1 | goal 2; "A structure is read and written through its owner's accessors" |
| S10 | `target_headers_render`'s pass-2 `StrBuf nb` (memfn_stamps.c) | C-9 | heap builder, then ADOPTED as the Job's `csb` storage (S9); K155's own site | SHARED, already satisfied (`pcrec_sb_scratch` over the chosen arena) once RM-1 exists. The adoption is the design's (D-6) | K155; D203 |
| S11 | `splice_mark`'s `StrBuf tail` (memfn_stamps.c) | C-9 | heap temporary, freed at the function's end; not adopted | SHARED, already satisfied (`pcrec_sb_scratch`); the plain LIFO case | K155 |
| S12 | `render_buf`'s `StrBuf o` (part_layout.c) | C-9 | heap builder ADOPTED into the rendered buffer (S9) | as S10 | K155 |
| S13 | `pcrec_minimize_dfa` (minimize.c): `part`, `newpart`, `sig`, `htab`, `keys`, `keyseen`, `seq`, `ns` | C-10 | 8 heap temporaries hand-freed on every RETURN. While live they call `pcrec_arena_alloc(&cx->arena, ...)` for the RESULT (`ns[c].up`, `ns[c].tr`), so an OOM there strands them (alloc_check's filed row) | SHARED (with S3/S4: a hand-kept free list). The fact the design must meet: the client allocates into the OUTER arena while its scope is open | goal 1; the owner's "special areas like minimization" |
| S14 | `pcrec_clskit_emit_kit` (clskit.c), `Arena a = { .cx = c->cx }` | C-11 | a private arena, freed on return, never registered: a refusal strands its blocks | SHARED (a private copy of the mechanism the feature adds) | "One table per slot: no private copy of a declared mechanism" |
| S15 | `pcrec_scanedge_dfa` (scanedge.c), 10 hand-freed temporaries | C-12 | safe at T by the allowlist's argument: their only refusals are their own allocation failures, which free first | SHARED, CONDITIONAL: a client only if the design's registry takes plain heap blocks; otherwise unlock U2 | goal 1 |
| S16 | the CALLER-OWNS hooks `fd_hook` (facts_dump.c), `lc_hook` (callouts_dump.c) | C-13 | heap builders freed by the hook's caller after compile_driver returns nonzero | AS-IS (the longjmp never leaves compile_driver, so nothing strands; GENFORM-8 counts them but no scope is needed) | src/core/CLAUDE.md CALLER-OWNS |
| S17 | the kit seam `mf_arena` (memfn/include/memfn.h) and pcrec's backing `pcrec_memfn_arena_alloc` + `pcrec_memfn_art` (memfn_sites.c) | C-14 | the art's allocations go to the ATTEMPT arena; contract: "memory lives until pcrec's arena dies and is never freed by the kit"; the art lives to `mf_art_end` | AS-IS, with a constraint on the design: the art's `mf_arena` stays the attempt arena (or any lifetime enclosing `mf_art_end`); a scoped `mf_arena` would be a kit seam event | goal 3; D146 |
| S18 | the checks' tables: scanner `ALLOW[]` (5 rows naming [ARENA-SCOPES]), `alloc_check.c` `known_stranded[]` (2 rows) | C-15 | allowlisted or filed as clients waiting on this row | ROW (rows deleted as each client moves) | "A row checks its own contract" |
| S19 | grow-by-copy inside an arena: `sb_grow`'s scratch branch (sb.c), `arena_regrow` + `cont_push` (dfa.c), `fq_push` (possessify.c); and the kit's `kb_reserve` (memfn/src/compose.c) over pcrec's arena | C-16 | each growth takes a fresh block and copies; the old block stays until the arena dies (COST-1's mechanism) | SHARED, CONDITIONAL (plan row [ARENA-REGROW] holds three members; `sb_grow` is a fourth since K155): a member here only if the design answers COST-1 with a scope mechanism (D-5) | "Notice siblings"; COST-1 |
| S20 | the job-arena scratch that is dead when its function returns: the 22 scratch builders on `pcrec_sb_scratch(&cx->arena)` and D105's legend arrays | C-17 | retained to the attempt's end; measured linear (k155fix2 census) | AS-IS (not clients: R-3's 7-12% was the WHOLE-ARTIFACT rewrites; these are linear and small); unlock U1 | "Build under measurement" |

### Commands and counts (all at T)

- C-1 `GG 'pcrec_arena_free(&' src cli lib memfn/src`: 29 calls. findings_dump.c 9, syntax_dump.c 12 (lines
  881-1941), measures_dump.c 2, compile.c 2 (`pcrec_subst_compile`, `job_cleanup`), cli/main.c 1, clskit.c 1,
  emit_subst.c 1, dfamemo.c 1, rxt_source.c 1. `GS src/core/arena.c` (71 lines): `pcrec_arena_alloc` (the `a->cx`
  branch, then `abort()`), `pcrec_arena_own_slot`, `pcrec_arena_own`, `pcrec_arena_free` (the owned walk, then the
  blocks).
- C-2 `GG -E '\bArena\s+[a-z_]+\s*(=|;|\[)' src cli lib memfn/src`: 9 locals (cli/main.c `esc`; compile.c
  `pcrec_subst_compile`; findings_dump.c 4; measures_dump.c 1; clskit.c 1; emit_subst.c 1) and 3 fields
  (`struct Ctx` `arena`; `RxtSource` `arena`; `DfaMemo` `arena`). `GG -E 'Arena|AOwn' src/core/internal.h`:
  the record and the "there are none today" comment (S2).
- C-3 `GG -E 'pcrec_arena_own(_slot)?\(' src`: one caller outside arena.c and internal.h, compound.c (slot taken,
  then `pcrec_arena_own` on the part text).
- C-4 `GS src/core/compile.c | awk '/^static void job_cleanup/,/^}/' | grep -c -E '^\s*free\('` gives 27;
  `... | grep -c pcrec_sb_free` gives 6 (csb, hsb, vmsb, irsb, scr_test, scr_desc).
- C-5 `GG -E '^\s*(struct )?Ctx\s+[a-z_]+\s*(=|;)' src cli lib`: 5 (compile.c `compile_driver`,
  `pcrec_count_groups`; syntax_dump.c 3).
- C-6 `GG 'setjmp' src cli`: the one call `if (setjmp(cx.jb))` in compile.c `compile_driver`; the rest are
  comments.
- C-7 `GG -E 'dfa_memo|DfaMemo' src/core/compile.c src/opt/dfamemo.c`: `DfaMemo dmemo` and 5
  `pcrec_dfa_memo_free(&dmemo)` in compile.c; `m->arena.cx = cx` and `pcrec_dfa_memo_free` in dfamemo.c.
- C-8 `GG -E '(sb|b|s)->ar\b' src/core/sb.c`: `sb_store`, `sb_unstore`, `sb_grow` (`if (sb->ar)`), `pcrec_sb_take`
  (`sb->p && !sb->ar ? sb->p : strdup(...)`): 4 decisions.
- C-9 `GG -E 'StrBuf (nb|tail|o)\b|free\(c->p\)|c->p = nb\.p|free\(old\)|sb->p = o\.p' src/gen/memfn_stamps.c
  src/gen/part_layout.c`: `tail` (splice_mark), `nb` + `free(c->p)` + `c->p = nb.p` (target_headers_render),
  `o` + `sb->p = o.p` + `free(old)` (render_buf). The field copies around them: `GS src/gen/memfn_stamps.c`
  (target_headers_render's end, `c->len = nb.len; c->cap = nb.cap;`), `GS src/gen/part_layout.c`
  (render_buf's end, `sb->len`, `sb->cap`, `sb->layout_bytes = 0`).
- C-10 `GG -E 'malloc|calloc|free\(|pcrec_arena_alloc|pcrec_ctx_nomem' src/opt/minimize.c`: 8 heap temporaries,
  3 `pcrec_ctx_nomem` exits that free by hand first, 2 `pcrec_arena_alloc(&cx->arena, ...)` while they are live.
  One caller: `GG 'pcrec_minimize_dfa(' src` gives dfamemo.c `pcrec_build_min_dfa`.
- C-11 `GS src/gen/clskit.c`, `pcrec_clskit_emit_kit`: the local arena, its `[ARENA-SCOPES] client` comment,
  `pcrec_arena_free(&a)` on return.
- C-12 `GG -E 'malloc|calloc|free\(' src/opt/scanedge.c`: 10 temporaries in `pcrec_scanedge_dfa`, hand frees on
  each exit.
- C-13 `GG -E 'fd_hook|lc_hook' src`: facts_dump.c and callouts_dump.c, one definition and one use each.
- C-14 `GS memfn/include/memfn.h` (`typedef struct mf_arena`, its comment); `GG 'pcrec_memfn_arena_alloc' src`
  (memfn_sites.c: the callback over `pcrec_arena_alloc`, and `pcrec_memfn_art` setting `ma->u = &cx->arena`).
  `GG -i arena memfn/src`: `kb` over the caller's `mf_arena` (compose.c, kit.h); formhash.c's own `fh_arena`
  (malloc-backed, freed after one rendering, errors by return, no Ctx). formhash.c has no pcrec caller
  (`GG formhash src` gives nothing; register row 49 notes it).
- C-15 `GS tests/core/scratch_builder_check.py` (`ALLOW`: `minimize.c pcrec_minimize_dfa`, `memfn_stamps.c
  target_headers_render strbuf:nb`, `memfn_stamps.c splice_mark strbuf:tail`, `part_layout.c render_buf strbuf:o`,
  `clskit.c pcrec_clskit_emit_kit arena:a`); `GG -E 'known_stranded|ARENA-SCOPES' tests/core/alloc_check.c`
  (rows for minimize.c and target_headers_render).
- C-16 `GG -E 'arena_regrow|fq_push|cont_push' src`; `GS src/core/sb.c` (`sb_grow`'s scratch branch);
  `GS memfn/src/compose.c` (`kb_reserve`: "the old block stays in the arena"). Plan row: `scripts/entry
  ARENA-REGROW -l 2`.
- C-17 `GG 'pcrec_sb_scratch(' src`: 24 hits, 22 of them calls in .c files outside sb.c (facts.c 7, emit_dfa.c 5,
  memfn_stamps.c 3, part_layout.c 2, varexp.c, emit_vm.c, known.c, memfn_sites.c, mod_callouts.c). This is at
  least the population; k155fix's census names 23 converted builders.

Population sentences are counts of the grep shown, not of a name list, except GENFORM-8's "about seven
registries". That one is a FLOOR (at least 7), re-derived here as S1, S3, S4, S7, S13, S14, S15 plus S16.

## Register rows looked up

Greps: `GS docs/dev/guide/architecture.md | grep -n -i -E 'arena|job_cleanup|sb\.c|minimize|clskit|memfn_stamps|
part_layout|ARENA-SCOPES|StrBuf|longjmp|setjmp'` (3 hits: rows 7b and 20, and the tier-3 text citing
memfn_stamps.c), then every row's WHERE read against the site map's files. `GS docs/design/stream/roadmap.md |
grep -n -i -E 'arena|job_cleanup|memfn_stamps|part_layout|minimize|clskit|StrBuf'`: 3 hits, all naming
`job_cleanup` or `part_layout.c` as places where other areas' machines are freed or rendered. No roadmap area owns
memory lifetime.

| register row | why it matches | disposition |
|---|---|---|
| 20 One Ctx/longjmp/arena wrapper | S5: the five Ctx instances and their hand teardowns. WHERE drift: `pcrec_compile` is compile.c :3771 at T (row says :3762), `pcrec_compile_in` :3800 (row :3791); compile_defs.c :43 matches (`GG -E '^int pcrec_compile\(|^int pcrec_compile_in\(' src/core/compile.c`) | RIDES FIRST only if the design registers scopes on the Ctx (S5's condition). NOT CARRIED if they register on the parent arena: `pcrec_arena_free` then releases them on every copy, and the row keeps its own trigger ("a fifth copy") |
| 7b The artifact as typed parts, kit returns parts | S10/S11: memfn_stamps.c's header-mark splice is one of the row's "three string protocols" (WHERE `memfn_stamps.c:334-341` falls inside `target_headers_render`, which begins :331 at T) | NOT CARRIED: the feature changes where the rewrite's bytes live, not the protocol, and the row's event is "the next post-render rewrite" (this adds none). Consequence for the design: when 7b lands, `nb` and `tail` are deleted, not scoped. The scope's shape is judged on S11 and S13, not on the adoption case (S10/S12) alone |
| 6a Name each Job/Ctx field's writer and readers | if the design adds a Ctx field (S5's Ctx branch) | NOT CARRIED (its event is an emitter-to-driver flag). The corollary still binds the new field: one writer (arena.c or the scope primitive), named readers (the teardown). Tier 1's DRAFT question `ctx-owner` is open; the field joins whatever it rules |

Rows the note PROPOSES (register columns):

- P1 | grow-by-copy inside an arena asked one way (4 members: `sb_grow` scratch, `arena_regrow`, `cont_push`,
  `fq_push`; the kit's `kb_reserve` is the kit's own, D157) | One question, one primitive; Notice siblings |
  sb.c `sb_grow`; dfa.c `arena_regrow`; possessify.c `fq_push` (C-16) | the [ARENA-SCOPES] design if it answers
  COST-1 by an arena mechanism (D-5), else [ARENA-REGROW]'s own trigger | S, no-mover | 3-4 hand regrow copies |
  open. This joins plan row [ARENA-REGROW] (it gains `sb_grow` as a member) rather than duplicating it.
- P2 | the compile-lifetime resources registered once (the memo arena's 5 hand frees) | One question, one
  primitive | compile.c `compile_driver` (`pcrec_dfa_memo_free` x5, C-7) | a second compile-lifetime resource
  (D77) | S, no-mover | 4 of 5 hand frees | open.
- P3 | hand-freed heap temporaries become scope allocations (`scanedge.c`'s ten) | goal 1 | scanedge.c
  `pcrec_scanedge_dfa` (C-12) | the next refusal added while they are live, or the design's choice to take it
  (S15) | S, no-mover | the hand frees, the allowlist row | open.
- P4 | `job_cleanup`'s named list becomes registrations | goal 1; Notice siblings | compile.c `job_cleanup`
  (C-4) | the design's answer to D-3, if it does not take it now; else the next Job heap array | M, no-mover | the
  named list (27 frees, 6 sb_frees) | open.

`minimize.c` (S13) and `clskit.c` (S14) get no proposed row: they move with the feature. RM-1 lands first and
gets none either.

NOTED DEVIATIONS on touched sites: none. Rows 29-32 and 49-51 were read; row 49 (formhash.c) names a kit file
whose private arena is a sibling (C-14) but which the feature does not touch. This note proposes none.

D-row "Revisit when" triggers on mapped sites: D56's trigger (a legitimate pattern measured needing more than
the cap) is not met. D19, D105 and D203 carry none. Found by `grep -n -i revisit docs/dev/decisions.md` within
those rows.

## Remodels that land first

**RM-1: StrBuf storage moves through `sb.c` (S9; r96 GENFORM-5/COST-2).** WHAT CHANGES SHAPE: the two
transplants (`target_headers_render`'s and `render_buf`'s) stop writing `p`/`len`/`cap` and calling `free()`
themselves; one `sb.c` primitive moves or copies a finished builder's storage into a destination buffer by
`.ar`. GATE: no-mover, byte identity (both sides heap at T, so the primitive frees exactly what the two sites free
today). SIZE: S. CHECKS THAT BIND THE MOVED CODE: S256 (`sb_grow`'s nomem route; anchor recheck by
`python3 scripts/m6read_check_sab_anchors.py`), S257 (csb attachment), S3572 and S3584 (the allowlist narrowed to
`nb` by name), S3570 (heap local), the scanner's `ALLOW` rows for `nb` and `o`, `alloc_check.c`'s
target_headers_render filed row (`GG -l -E 'target_headers_render|render_buf|sb_grow' tests/mech` gives S256,
S257, S3571, S3572, S3584, S701). The SIMD/scaffold/layout records the swaps also adjust (`simd_guarded`,
`simd_size`, `layout_bytes`) stay where they are. The primitive moves storage only. SEPARABLE: yes, it lands
answer-identical with no scope in the tree, because at T every storage it moves is heap. SPEED: byte-identical
emitted code; one call in place of five assignments, no timing check needed. DELETES: two hand transplants and
their raw `free()`s, so goal 2's two direct writers of StrBuf storage outside sb.c go.

**RM-2 (CONDITIONAL): register row 20, one Ctx/longjmp/arena wrapper.** Lands first ONLY if the design registers
scopes on the Ctx (S5). Then the five teardowns (C-5) each need the release, and one wrapper must exist first.
GATE no-mover, SIZE S (the row's own). CHECKS: the dump tier's tests and S255 (arena nomem). SEPARABLE: yes.
DELETES: four copies. If the design registers on the parent arena instead, this is not a unit.

No other site needs a remodel first. S3/S4 (SHARED) are the feature's own general form (next section), not a
reshaping the feature could land without. S14 and S13 are clients and move with the feature.

## The general form and its siblings

THE GENERAL FORM. A lifetime is an arena. Lifetimes nest: compile > attempt > scope. Each level owns what was
allocated in it plus what was registered with it (`Arena.owned` is the first registration kind at T). A level is
released (a) on its own normal exit, innermost first, and (b) all together when the attempt's teardown runs after
a longjmp. The owner's "stack memory extension" is this shape. "Registered such that the exit could free them" is
(b); "allocated up and deallocated down the stack" is (a).

THE FAMILY TODAY (one answer each to "what dies when", site map): the attempt arena (S1) and its owned list (S3);
the compile-lifetime memo arena (S7); job_cleanup's named list (S4); the hand-freed temporaries (S13, S15); the
private arena (S14); the caller-owns hooks (S16, which need nothing); the detached no-Ctx arenas (C-2: 9
locals, `RxtSource.arena`), outside any compile and needing nothing. The kit has its own sibling (`fh_arena` in
formhash.c, C-14), and it stays the kit's.

PLANNED ROWS THAT EXTEND THE SAME SHAPE: [ARENA-REGROW] (arena-grown stacks; the shape covers it if a scope can
hold a growing region, else it widens at that row: D-5); [K155-STAMPS-LEAK]'s next line ("move nb/render_buf/splice
tail onto a scoped arena", plan @T) is this feature's first client set. `scripts/entry -g arena -in 2` and a plan
grep for `scoped|job_cleanup` found no other row that extends it.

UNLOCKS, each with its trigger:
- U1: the 22 scratch builders (S20) and D105's legend arrays move into short scopes, which lowers peak memory.
  Trigger: a measured peak cost in the job arena (D77; k155fix2 measured them linear and small).
- U2: `scanedge.c`'s hand frees go (P3). Trigger: as P3.
- U3: the memo's five hand frees become one compile-level registration (P2). Trigger: as P2.
- U4: `job_cleanup`'s named list becomes registrations (P4); "a new allocation belongs here or it leaks on
  abort" (its own comment) stops being a rule a writer must remember. Trigger: the design's D-3.
- U5: the scanner's allowlist (S18) shrinks to the heap mechanisms themselves as clients move. Trigger: each
  client's move (in the same change).
- U6 (r96 GENFORM-8): a non-memory resource entry (a FILE*, {pointer, free fn}). Trigger: a SECOND non-memory
  member (D77; GENFORM-2's FILE* was fixed by reordering, so there is no member at T).

## Seams

| seam | writer | readers | facts down | facts up | new calls and their layer direction | text round trip |
|---|---|---|---|---|---|---|
| core arena/StrBuf API (internal.h; module-internal, not public) | arena.c, sb.c | every src/ layer (C-1, C-17) | a lifetime to allocate in | none | clients in opt/ and gen/ call down into core/ for open/close and the RM-1 move; no upward call | n/a (in-process memory; no serialized form, none needed) |
| kit `mf_arena` (memfn.h; MODULE seam, D146) | pcrec (memfn_sites.c builds it over the attempt arena) | the kit (`kb`, `mf_art_begin`) | an allocator whose memory outlives `mf_art_end` | none | NONE: the seam does not change; the art's arena stays the attempt arena (S17) | unchanged |
| the one longjmp (compile.c setjmp to the attempt's teardown) | `pcrec_ctx_fail`/`pcrec_ctx_nomem` | compile_driver's handler, then `job_cleanup` | that scopes are open (whatever record the design chooses) | none | none new; release happens in the existing teardown (S4) or `pcrec_arena_free` (S3) | n/a |

The kit shares pcrec's arena only through `mf_arena`. That is an existing module seam and the feature leaves it
as is. The kit's `kb_reserve` grows by copy in pcrec's attempt arena (S19), which is COST-1's mechanism inside
the kit. Whether it matters is a kit question, stated to the kit as a fact (its blocks are retained to the
attempt's end) if D-5 makes it one. No kit code shares a scope.

## What is deleted

- RM-1: the two hand transplants (S9) and their raw `free()`s.
- RM-2 (if taken): four Ctx/arena teardown copies (row 20's count).
- The feature: `clskit.c`'s private arena and its comment (S14); `minimize.c`'s 8 hand frees and its 3
  free-then-nomem exits (S13); the three rewrites' heap builders and their `[ARENA-SCOPES] client` comments
  (S10-S12); 5 scanner `ALLOW` rows and 2 `alloc_check.c` `known_stranded` rows (S18), with K155's three-rewrite
  remainder closed; the false "there are none today" comment (S2). If the design takes D-3: `job_cleanup`'s named
  list in favour of registrations.

## What the design step must decide

Handed on, not decided here (the five the brief names first):

- D-1 THE API (S1, S3, S8): how a scope is opened, allocated from and closed; whether a scope IS an `Arena`
  (so S8's `.ar` branch takes it unchanged) or another type (S8 becomes WIDEN).
- D-2 THE LIFO DISCIPLINE and how a violation is caught (S1, S13): closing a scope that is not the innermost;
  allocating into an OUTER level while an inner one is open (minimize's `ns[c].up`/`.tr` must outlive its
  tables); a result pointer escaping a closed scope.
- D-3 WHAT `job_cleanup`'S LIST BECOMES (S4, P4): kept, or registrations, given that the Job's machine arrays
  grow by `realloc` in place, which an arena cannot do without COST-1's retention.
- D-4 HOW A SCOPE INTERACTS WITH THE LONGJMP (S5, S6): where the "all at once" release runs (the parent arena's
  free or a Ctx registry, which decides RM-2); its order against the `setjmp` handler's reads; the memo arena (S7)
  whose `.cx` points at the attempt but whose lifetime is longer.
- D-5 COST-1 (S19, S20, P1): whether a scope answers grow-by-copy retention (for example by releasing a region
  early), or a separate mechanism ([ARENA-REGROW]) does; and whether the kit is told the fact.
- D-6 ADOPTION (S10, S12, RM-1): how a builder's finished bytes leave a scope to become the Job's `csb` (a copy,
  or a hand-off of storage). This is RM-1's primitive's contract.
- D-7 REGISTRATION HOME (S5, row 20, row 6a): on the Ctx (as the plan row words it) or on the parent arena.
- D-8 THE CLIENT SET for the first build (S13-S15, S20): at least S10-S14. S15 and U1 are by trigger.
- D-9 TESTS AND GATES: the alloc_check property for scope clients, the scanner's rule for a builder on a scope,
  the growth library stage going green (K155's witnesses), sabotage rows for the release paths, and the peak
  measurement against R-3's families (+7-12% was the cost the scope must not pay). LEAK-ATTRIBUTION
  (REQ-OPEN): the 13 growth leaks' sites, from a `fast_unwind_on_malloc=0` repro.
- D-10 the S2 comment's replacement text (the detached arenas exist).

## Open questions for the owner

- **scope-reach** (CONFIRM). TODAY: `minimize.c`'s tables are malloc'd and hand-freed; an out-of-memory inside it
  strands them (`alloc_check.c` files it). EXAMPLE (hand-worked): in a scope, those tables are arena blocks of the
  scope, and closing it or the longjmp frees them; no per-pointer free list is needed. QUESTION: do your words
  ("If arenas were registered such that the exit could free them") cover arenas only, with any heap temporary
  becoming an arena allocation in a scope? Or a general registry of any resource ({pointer, free function}, review
  r96 GENFORM-8)? LEANING: arenas only now; a general resource entry waits for a second non-memory member. That
  is the review's own unlock ("resource entries only at a second member", r96 GENFORM-8/9, ruled PLAN). Records:
  the owner 2026-11-24 as quoted above; r96.
- **scope-peak** (CONFIRM). TODAY: the three whole-artifact rewrites stay on the heap because, moved into the job
  arena, they raised peak memory 7-12% (ruling R-3). QUESTION: is lowering peak memory on the success path
  ("deallocated down the stack") a goal equal to freeing everything on a refused compile? LEANING: yes, both. R-3
  already treated peak as binding, and your words name both directions. Records: the owner 2026-11-24; K155's
  status (R-3); plan row [ARENA-SCOPES].
