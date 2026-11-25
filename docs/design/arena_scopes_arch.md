# Scoped arenas registered on the Ctx ([ARENA-SCOPES]): architecture note
STATUS: ACCEPTED (manager, 2026-11-24, after reviews r100 and r101, RULED). Open owner question: scope-reach. Rev 2 by lane arenaarch2 plus r101 text fixes (lane arenafix3); rev 1 (lane arenaarch, tree 15e37b005) superseded in place. Next: the design step, which cites this note.
The "r100 disposition" and "r101 disposition" tables at the end map each finding to its answer.
FORM: full   (trigger: at least 9 existing decision sites touched, a floor from the site map's ROW/CHAIN/SHARED/WIDEN/ACCESSOR rows: S1 `pcrec_arena_alloc`'s error channel, S3 `pcrec_arena_free`'s owned walk, S4 `job_cleanup`, S6 the five `setjmp` handlers, S8 `sb.c`'s storage-kind tests, S9 the two storage transplants, S21 the nested part compile's facts copy, S22 `job_cleanup`'s end actions, S25 the Job scratch pair; mechanisms added: one lifetime record nested in another's, and its registration)
TREE: T = 4b8f6a7194482adc1a103a6df13e42580c462a59 (lane/arenaarch HEAD at this lane's start: rev 1 plus main merged in, 46ec58349, plus two deliver-file commits). `git diff --stat 15e37b005 $T -- src cli lib memfn/src tests docs/dev/guide` is empty, so no code cited by rev 1 or by r100 moved; every record below was nevertheless re-run at this T.
REQUIREMENTS: plan row [ARENA-SCOPES] @T; the owner's words of 2026-11-24 (journal @T, entries 10:54 and 10:55); the rulings k155-fix-go (journal 10:32), R-1 (10:36), R-3 (11:01); D203; known_issues.md K155 @T; review r96 (`docs/dev/reviews/2026-11-24-r96-k155code.md` @T: GENFORM-2, -5, -8/9, COST-1, COST-2); review r100 and its RULED section @T; src/core/CLAUDE.md @T.   REGISTER READ: `docs/dev/guide/architecture.md` register @T; `docs/design/stream/roadmap.md` @T (register row 12).

Every command runs from any checkout with `T=4b8f6a719`. `GG` is `git grep -n PATTERN $T -- PATHS`, `GS` is
`git show $T:PATH`. No command reads the working tree. Rev 1 cited `docs/dev/lanes/k155fix2_report.md`; r100's lenses
could not verify it, so rev 2 cites only the journal's 15:19 entry for k155fix2 (at T) and states no claim that
rests on the report alone.

## Goals served

- **Goal 1 (one home per question).** The question is "what dies when this piece of work ends, on a return AND
  on a longjmp?". It has at least ten hand-kept answers at T (a floor: the family is a name list, re-derived in the
  site map): the attempt arena S1 and its `owned` list S3; `job_cleanup`'s named list S4; the five `setjmp`
  handlers' own teardowns S6; the memo's compile-lifetime arena S7, freed by five hand calls; the hand-freed tables
  in `minimize.c` S13 and `scanedge.c` S15; the private arena in `clskit.c` S14; the caller-owns hooks S16; the
  Job's hand-built scratch pair S25; and the kit's own heap chain in `window.c` S27. The feature serves goal 1 only
  if it replaces answers instead of adding one. Which shape does that is the design's choice (section "The general
  form").
- **Goal 2 (data with its writer; accessors).** Two units outside `sb.c` SWAP OR FREE a StrBuf's storage by hand
  (S9: `free(c->p); c->p = nb.p`, and `sb->p = o.p ... free(old)`). A scope that backs those builders breaks both,
  so the swap moves into `sb.c` first (RM-1). Six more sites outside `sb.c` TRUNCATE a StrBuf by hand (S26). They
  are correct for every storage kind, so the feature does not need them moved (proposed row P5). `Arena` itself has
  no init accessor: 9 initialisers and 7 `.cx` writers spell it by hand (S28). They change only if a scope is an
  `Arena` that gains fields (conditional RM-3).
- **Goal 3 (seams).** The kit seam `mf_arena` (S17) is backed by the attempt arena. Its contract ("memory lives
  until pcrec's arena dies") becomes ambiguous once arenas nest (D-11). The longjmp crossing carries a new fact UP:
  opt/ and gen/ clients write the open-scope record that the handler's teardown reads (section "Seams"). Layer
  direction: clients call down into core/ (`arena.c`, `sb.c`); no new upward call.
- **Goal 4 (remodels ride along).** RM-1 rides first. RM-2 (register row 20, re-based) and RM-3 ride first only
  on named design choices. The roadmap's H-FLAGS area names `job_cleanup`'s `lmnfa`/`lmdfa` frees with [LANDWALK]
  in flight (STATE:started), so D-3 overlaps it (section "Register rows looked up").
- **Traded against.** Two gates bind the build, and they are records, not choices of this note:
  - R-3 (journal 11:01): peak memory. +7-12% peak in the job arena was judged too costly, and the
    `job_cleanup`-freed `Job.rwsb` was REFUSED "as a second mechanism".
  - R-1 (journal 10:36): the gate is the "arena high-water delta + no refusal moves at growth memory-cap rungs".
    A scope that lowers peak memory can MOVE a refusal at a memory-cap rung, in the favourable direction (a
    pattern refused today compiles). Whether that direction counts as a move under R-1 is not decided here (D-9).
  - Emitted bytes must not move (the speed gate's proof).

Standing questions (docs/design/CLAUDE.md).
1. Measurement regime: RELEVANT. The feature's benefit and its gates are peak memory (R-3's families; r96's massif
   and peak-RSS witnesses), refusals at the growth memory-cap rungs (R-1), and stranded heap (`tests/core/
   alloc_check.c`; the growth sweep's library stage under LSan).
2. Independent control: RELEVANT. The allowlist scanner (`tests/core/scratch_builder_check.py`) reads the source.
   `alloc_check.c` and LSan read the running allocator. They have different sources, and the second is the control
   on the first. Two populations nobody counts at T: the scanner's LAYERS are src/ only, so a kit heap block live
   across a pcrec hook (S27) is outside it; and `alloc_check.c`'s single-shot sweep fails the Nth MALLOC, so an
   arena allocation that takes no new block is never failed (K163's reachability, S21).
3. What moves when data is regenerated: NOT relevant. No table, measure set or oracle store is read.

## Requirements read

- The owner, 2026-11-24 10:54 (journal @T; the record is marked "Owner DIRECTION (not yet a build go), verbatim"),
  quoted whole: "Memory fix: the arena memory system is in my mind a stack memory extension system. Not
  proscribed: If arenas were registered such that the exit could free them, then they could be allocated up and
  deallocated down the stack with the registration used to clean up on exit. You could then use them for special
  areas like minimization". Then 10:55: RULING arena-scopes-go: "yes".
- k155-fix-go (journal 10:32), the owner: "In general yes, we should clean up on exit. My concern is less why we
  are exiting but whether this is a bit of a hack in that it's special case for this allocation." then "Go with
  your general form". The class-level frame this feature inherits.
- R-1 (journal 10:36, the manager within that go): the scratch-builder fix; `minimize.c` filed as a peak-memory
  trade (the separate row it named was never filed, r96 GENFORM-3; [ARENA-SCOPES] holds minimize.c); the gate
  "arena high-water delta + no refusal moves at growth memory-cap rungs".
- R-3 (journal 11:01): "+7-12% peak heap (59-175 KB) from 3 whole-artifact rewrites now in the arena ... Lane
  proposed Job.rwsb (job_cleanup-freed) — REFUSED R-3 as a second mechanism; those 3 sites become [ARENA-SCOPES]
  clients". CONSEQUENCE for the design (C3): it may not answer its clients by adding a member to `job_cleanup`'s
  named list. Turning that list into registrations (P4) is the allowed direction, implement-then-replace. That turns the WHOLE named list into registrations, including the `lmnfa`/`lmdfa` frees (compile.c:304-306), so it overlaps H-FLAGS / [LANDWALK] (STATE:started).
- Plan row [ARENA-SCOPES] @T: "scoped arenas registered on the Ctx: freed LIFO on the way out, all at once on a
  longjmp". Its clients are K155's three whole-artifact rewrites, `minimize.c`'s tables, `clskit.c`'s local arena,
  and "maybe job_cleanup's free() list". Its next line is "a short design (API, LIFO discipline, what job_cleanup's
  list becomes) + critic round, then an opus build lane".
- D203: a bug is handled at the CLASS level. K155's class is "a resource live across a refusal that nothing frees on
  the longjmp". The arena-backed builder (K155's fix) covers results that live as long as the attempt. This feature
  is that class's mechanism for TEMPORARIES. K163 (filed by this lane, SUSPECTED) is a member whose resource is an
  entire inner compile.
- K155 @T: FIXED in general form. Three whole-artifact rewrites stay heap by R-3 "until [ARENA-SCOPES]". Their
  witnesses still leak until then, and `alloc_check.c` names `target_headers_render` as a FILED stranding.
- Review r96: GENFORM-5 and COST-2 (the two raw storage swaps; "One sb.c primitive that moves or copies storage by
  `.ar`, used by both sites, as part of the scopes design"); GENFORM-8/9 ("one Ctx registry of {pointer, free fn}
  with scope marks AND a release operation, so heap temporaries are freed when they are today (no peak cost) and
  on a longjmp"; unlocks with triggers; "resource entries only at a second member (D77)"); COST-1 (an arena-grown
  StrBuf never frees its old blocks). COST-1 was fixed at its one super-linear site by k155fix2. The journal (15:19)
  records its 23-site census: "no other super-linear site". COST-1's CLASS (grow-by-copy retention) stays open as a
  mechanism question.
- The growth sweep's 13 leak shards (cloud run 45492837175, plan row [ARENA-SCOPES]'s refs @T: "13 leaks = grow9fix
  set, site attribution needs a fast_unwind_on_malloc=0 repro"). The journal entry rev 1 cited (11-24 17:26) is not
  at T. So **REQ-OPEN leak-attribution**: which rewrite each leak is, from a `fast_unwind_on_malloc=0` repro (an
  input to the design step). The note counts them as the three-rewrite client set, per the plan row only.
- RULINGS THIS NOTE CROSSES. Found by `grep -n -i -E 'arena|job_cleanup|longjmp' docs/dev/decisions.md` at T:
  33 hit lines in 14 rows (D16, D19, D29, D31, D32, D33, D38, D56, D70, D104, D105, D109, D110, D203). The rows
  that bear:
  - D19: "All per-build state is arena memory owned by the Job". Any per-Ctx record keeps that.
  - D56: `job_cleanup`'s wholesale free is why a longjmp from any allocation leaks nothing.
  - D70's Revisit-when: "a future allocation-model change makes the arena pointer in a payload wrong". Scopes ARE
    that trigger wherever an AST payload's arena pointer could name a closed scope (S23, D-2).
  - D105: the legend's scratch moved INTO the job arena; its reason is proportionality ("16n bytes of scratch
    beside an n*ncls transition table"), the opposite trade from R-3.
  - D109: the handler tests `failed_nomem` FIRST, and `Ctx` is memset at the top of every attempt, so per-attempt
    Ctx state starts empty by construction (D-4, D-7).
  - D110: `alloc_check.c` populations are FLOORS (D-9).
  - D32 §8: it refused a "trial mode" whose `Ctx` copy leaked into an arena "unreachable from the real Ctx". That is
    the same hazard shape as K163.
  - D203.
  The other hits (D16, D29, D31, D33, D38, D104) name the arena or the longjmp in passing (a parse result's home,
  the K7 abort, the export prefix) and carry no lifetime rule. Also src/core/CLAUDE.md: "error paths longjmp to
  `cx.jb`"; its "ONLY `setjmp`" line is stale (S6, a DOC drift for the manager); and "Cross-attempt state is plain
  `Ctx` fields, not arena text" (D-12). Superseded or already built at T: nothing of the row. `git log
  --grep=ARENA-SCOPES` shows only plan, allowlist and comment commits.
- VOCABULARY (each grepped; commands in "Commands and counts"): `Arena`, `ABlock`, `AOwn`, `pcrec_arena_alloc`,
  `pcrec_arena_free`, `pcrec_arena_own`/`_own_slot`, `Ctx.arena`, `DfaMemo.arena`, `RxtSource.arena`,
  `PcrecPartFacts.into`, `StrBuf.ar`, `pcrec_sb_scratch`, `sb_store`/`sb_unstore`/`sb_grow`, `pcrec_sb_take`,
  `pcrec_sb_free`, `pcrec_sb_fragf`, `job_cleanup`, `setjmp`, `pcrec_ctx_nomem`/`pcrec_ctx_fail`, `failed_nomem`,
  `scr_test`/`scr_desc`, `mf_arena`, `wd_blk`/`wd_alloc`, `KsAlloc`, `kb_reserve`, `fh_arena`, `arena_regrow`,
  `fq_push`, `cont_push`, `cpset_init`, `ALLOW` (scanner), `known_stranded` (alloc_check). Zero hits: `scope` as an
  arena term (a new shape).

## Site map

| # | site (file, function or table) | command (at T) | today | class | goal/rule |
|---|---|---|---|---|---|
| S1 | `Arena` record, internal.h (`{ ABlock *head; Ctx *cx; AOwn *owned; }`); `pcrec_arena_alloc` arena.c (error channel: `a->cx` then `abort()`) | C-1, C-2 | one flat block list per arena, freed only wholesale; no parent, no nesting. THREE kinds at T: Ctx-owned (the 5 `Ctx.arena`s), Ctx-bound but unregistered (`clskit.c`'s local, S14; `DfaMemo.arena`, S7), detached (8 `{ 0 }` locals and `RxtSource.arena`, `.cx = NULL`) | WIDEN (the feature's own new shape: a nested lifetime). Generic writers: S28 | "A shape states the inputs it covers" |
| S2 | the comment on `Arena` in internal.h: "there are none today; every Arena is a Ctx's own" | C-2 | FALSE at T, independent of the feature: 8 detached locals plus `RxtSource.arena` have no Ctx | (drift; corrected as a no-mover inside RM-1) | "No silent defaults" |
| S3 | `Arena.owned` / `pcrec_arena_own_slot` / `pcrec_arena_own` (arena.c), one caller compound.c `walk_part` | C-3 | a list, in the arena, of heap blocks freed with it (K155) | SHARED: "what else dies with this arena" already has this one answer; a registration is the same question. The design says which survives | "One question, one primitive, from the second caller" |
| S4 | `job_cleanup` compile.c: the named list | C-4 | 27 `free()` calls (one of them `free(cx->job)`) + 6 `pcrec_sb_free` + `pcrec_arena_free(&cx->arena)`. Called on success, on every handler exit, AND mid-compile before each retry: 10 calls in `compile_driver`, 6 of them followed by `continue` (C-4b). So whatever the feature opens must be EMPTY between attempts. WRITERS beside `realloc`: compile.c:587-591 swaps the machine arrays between the primary and x-set Job fields by value (SUSPECTED), so a registration must key on the owner field. The arrays grow by `realloc` in place; four allowlisted sites rely on that (C-15: nfa.c `nst`; dfa.c `tab_grow`, which frees and NULLs the old table first; `intern`; dfamemo.c `pcrec_build_min_dfa`, which attaches the restored array "before any further allocation") | SHARED, CONDITIONAL (D-3): the teardown a longjmp reaches. SHARED with S3 if the named list becomes registrations. R-3 bars adding a member to it (C3). Its `lmnfa`/`lmdfa` lines are roadmap H-FLAGS's, with [LANDWALK] STATE:started (overlap) | goal 1; "Notice siblings" |
| S5 | the five `Ctx` instances: `compile_driver` (inside the attempt loop, memset per attempt), `pcrec_count_groups` (compile.c), `built_status_probe`, `pcrec_probe_ask`, `pcrec_syntax_explain` (syntax_dump.c) | C-5 | each owns its arena and its teardown | (the population of S6) | |
| S6 | the FIVE `setjmp` handlers, one per S5 Ctx | C-6 | three teardown spellings: `job_cleanup` (+ `pcrec_dfa_memo_free` on the driver's returning rows) in `compile_driver` and `pcrec_count_groups`; `pcrec_arena_free(&cx.arena)` alone in `built_status_probe` and `pcrec_probe_ask`; two `pcrec_sb_free` + `pcrec_arena_free` in `pcrec_syntax_explain`. The three dump-tier handlers never reach `job_cleanup`. `compile_driver`'s handler reads Ctx fields (`fit_labels(&cx)`, the `sets` carries) BEFORE `job_cleanup`. No sabotage row binds the dump-tier teardowns (C-6b) | SHARED, CONDITIONAL (D-4/D-7): release placed in `pcrec_arena_free` reaches all five (and must also hold for memset-only test Ctxs); placed in `job_cleanup` it reaches 2 of 5 src handlers, 2 of 11 counting the test tier's 6 more Ctx + `setjmp` recovery points (definitions_check.c x3, definitions_oracle_gen.c, branch_count_check.c, cwmax_check.c), all with hand teardown that never reaches `job_cleanup` (then RM-2 lands first). At least 5 comments claim one setjmp TREE-WIDE (C-6c): DOC drift, the manager files it | goal 1; src/core/CLAUDE.md (stale) |
| S7 | `DfaMemo.arena` (internal.h; dfamemo.c), freed by 5 hand calls in `compile_driver` | C-7 | an arena that lives ACROSS attempts (compile lifetime); `.cx` re-pointed per attempt (`m->arena.cx = cx`) | SHARED, CONDITIONAL: a compile-lifetime member of the family. It is a DECIDING site between the two candidate shapes (section "The general form"); its five hand frees are register row 20's (re-based) | "Notice siblings" |
| S8 | StrBuf storage kinds: `sb_store`, `sb_unstore`, `sb_grow`'s arena branch, `pcrec_sb_take` (sb.c), plus the BORROWED view `part_splice` (emit_compound.c, `StrBuf t = { .p = (char *)text, ...}`, allowlisted "never grown or freed") | C-8 | THREE storage kinds: heap, "this arena" (`.ar`), borrowed (`.p` owned by someone else). `pcrec_sb_take` already decides "move if heap, copy if arena" by `.ar` | AS-IS if a scope is presented as an `Arena *` (the `.ar` branch takes it unchanged); WIDEN if the design makes a scope another type. The borrowed kind is not a scope client | "One table per slot" |
| S9 | the two storage transplants: `target_headers_render` (memfn_stamps.c: `free(c->p); c->p = nb.p; c->len = ...; c->cap = ...`) and `render_buf` (part_layout.c: `char *old = sb->p; sb->p = o.p; ... sb->layout_bytes = 0; free(old)`) | C-9 | another unit swaps a StrBuf's storage and `free()`s; correct only while both sides are heap | ACCESSOR (primary), SHARED (secondary: with `pcrec_sb_take`'s by-`.ar` decision). RM-1 | goal 2; "A structure is read and written through its owner's accessors" |
| S10 | `target_headers_render`'s pass-2 `StrBuf nb` | C-9 | heap builder ADOPTED as the Job's `csb` storage (S9); K155's own site | client (D-6, D-8) | K155; D203 |
| S11 | `splice_mark`'s `StrBuf tail` (memfn_stamps.c) | C-9 | heap temporary, freed at the function's end; not adopted | client: the plain LIFO case | K155 |
| S12 | `render_buf`'s `StrBuf o` (part_layout.c) | C-9 | heap builder ADOPTED into the rendered buffer (S9); `pcrec_ctx_fail` is called 4 times while it is live | as S10 | K155 |
| S13 | `pcrec_minimize_dfa` (minimize.c): 8 heap temporaries | C-10 | hand-freed on every return; 3 `pcrec_ctx_nomem` exits free first; while they are live, 2 `pcrec_arena_alloc(&cx->arena, ...)` calls make the RESULT (`ns[c].up`, `ns[c].tr`), so an OOM there strands them (alloc_check's filed row) | SHARED (with S3/S4: a hand-kept free list). The fact the design must meet: the client allocates into the OUTER level while its own is open | goal 1; the owner's "special areas like minimization" |
| S14 | `pcrec_clskit_emit_kit` (clskit.c), `Arena a = { .cx = c->cx }` | C-11 | a private arena, freed on return, never registered: a refusal strands its blocks | SHARED (a private copy of the mechanism the feature adds) | "One table per slot: no private copy" |
| S15 | `pcrec_scanedge_dfa` (scanedge.c), 10 hand-freed temporaries | C-12 | safe at T by the allowlist's argument: their only refusals are their own allocation failures, which free first | SHARED, CONDITIONAL: a client only if the design's form takes plain heap blocks; else proposed row P3 | goal 1 |
| S16 | the CALLER-OWNS hooks `fd_hook` (facts_dump.c), `lc_hook` (callouts_dump.c) | C-13 | heap builders freed by the hook's caller after `compile_driver` returns | AS-IS (the longjmp never leaves `compile_driver`, so nothing strands) | src/core/CLAUDE.md CALLER-OWNS |
| S17 | the kit seam `mf_arena` (memfn/include/memfn.h) and pcrec's backing (memfn_sites.c: `pcrec_memfn_arena_alloc`, `pcrec_memfn_art` setting `ma->u = &cx->arena`) | C-14 | the art's allocations go to the ATTEMPT arena; contract: "memory lives until pcrec's arena dies and is never freed by the kit" | AS-IS on pcrec's side, with a pin the design must state (D-11): the art's `mf_arena` is the attempt's arena, never a scope; a scoped `mf_arena` would be a kit seam event | goal 3; D146 |
| S18 | the checks' tables: scanner `ALLOW[]` (5 rows naming [ARENA-SCOPES], 4 Job heap-array rows), `alloc_check.c` `known_stranded[]` (2 rows) | C-15 | allowlisted or filed as clients waiting on this row | ROW (rows deleted as each client moves). Also checks that exist only for the rows deleted: S3584's SAB_BEFORE is the literal `nb` client line; S3572's premise is the name-narrowed `nb` row; `alloc_check.c`'s stack recording and its `fn` column serve only the `target_headers_render` row, so they become unreached mechanisms (learnings §3) | "A row checks its own contract" |
| S19 | grow-by-copy inside an arena | C-16 | each growth takes a fresh block and copies; the old block stays until the arena dies (COST-1's mechanism). At least 18 sites: the shape grep prints 42 lines in 16 src/ files, plus `sb_grow`, `fq_push` and the kit's `kb_reserve` that it misses. `arena_regrow` (dfa.c, file-static) has 2 callers; no other site calls it | SHARED, CONDITIONAL (D-5): a member here only if the design answers COST-1 by a scope mechanism; else plan row [ARENA-REGROW] (updated, not duplicated: see "Register rows") | "Notice siblings"; COST-1 |
| S20 | job-arena scratch dead when its function returns: the 22 scratch builders on `pcrec_sb_scratch(...)` and D105's legend arrays | C-17 | retained to the attempt's end; COST-1's census found them linear (journal 15:19) | AS-IS (not clients; R-3's cost was the WHOLE-ARTIFACT rewrites); unlock U1 | "Build under measurement" |
| S21 | the NESTED PART COMPILE: compound.c `walk_part` sets `w->facts[i].into = &w->cx->arena` (the OUTER attempt's arena) and runs `part_compile` -> `pcrec_compile_driver`, a whole inner compile on its own `Ctx`; the inner compile copies into it (compile.c, `pf->memfn_forms = pcrec_sb_fragf(pf->into, ...)`) BEFORE its own `job_cleanup` / memo free | C-18 | an allocation under the inner Ctx through a handle whose error channel (`.cx`) is the OUTER Ctx. On OOM the longjmp lands at the OUTER `setjmp`, skipping the inner teardown: the inner Job, arena and memo strand. **K163, SUSPECTED**, not reproduced: W6's 1,008 forced failures never landed on the copy, because the outer arena's head block always had room. The lifetime order is not linear: outer attempt > inner compile > inner attempt, across two Ctxs | WIDEN, CONDITIONAL (the lifetime shape must cover a level owned by another Ctx, D-2/D-4); the bug is K163's, fixed at its class, not by this feature | D203; D32 §8; "A shape states the inputs it covers" |
| S22 | `job_cleanup`'s END ACTIONS: `*cx->find_union |= pcrec_find_asked(cx)` and `*cx->meas_union = true`, before any free | C-4 | two non-memory, ORDER-BOUND entries (they read the Job, so they run before it is freed) | SHARED, CONDITIONAL (D-3): if the named list becomes registrations, these are its first non-memory entries | goal 1 |
| S23 | `Arena *` captured in long-lived structs: `StrBuf.ar`, `PcrecCpSet.ar` (19 `cpset_init(` hits), `PcrecPartFacts.into`, endwin.c, clskit.c, dfa.c `LCtxTab`/`PMemo`/`ContStack`, rxt_find.c, rxt_source.c, subst_template.c | C-19 | at least 11 fields by the shape grep (r100 read 13 by hand; a floor either way). Each holds a lifetime handle past the call that gave it | WIDEN hazard (D-2: a handle naming a closed scope), D70's trigger for AST payloads | "A shape states the inputs it covers" |
| S24 | the allocation-call population | C-20 | 462 `pcrec_arena_alloc(` call lines outside arena.c/internal.h; 340 pass a Ctx's arena through a `cx` handle (251 the literal `&cx->arena`) | AS-IS if a scope is an explicit `Arena *` handed only to client code; WIDEN if the design adds an implicit "current arena" (all 340 change meaning) (D-1) | "No silent defaults" |
| S25 | `Job.scr_test` / `Job.scr_desc` (internal.h; set up in `compile_driver`, freed in `job_cleanup`; used in emit_vm.c) | C-21 | an existing hand-built longjmp-safe scratch (added after a LeakSanitizer find). `scr_test` is spliced into the program (follows the artifact, adopted like S10), `scr_desc` into the listing (a pure temporary) | SHARED, CONDITIONAL: family members. Clients of a scope only if D-8 takes them | goal 1; "Notice siblings" |
| S26 | StrBuf TRUNCATIONS outside sb.c: `splice_mark` (`sb->len = at; sb->p[at] = 0`), emit_vm.c x4 (`len = 0; p[0] = 0`), vm_stmt.c (`b->len = 0; b->p[0] = 0`) | C-22 | 6 direct writes of `len`/`p[...]`; storage untouched, so correct for every storage kind | ACCESSOR, not needed by the feature: proposed row P5 | goal 2 |
| S27 | kit siblings: window.c `wdecide_framed`, an `mf_arena` over `wd_alloc` (calloc blocks chained in `wd_blk`, freed by `wd_free` before return; reached from emit_dfa.c `mf_wdecide` on a shipped path); pcrec's own `KsAlloc` handles (measures.c `{ meas_alloc, &cx->arena }` and three detached) | C-23 | the kit's own heap arena, freed on return. SUSPECTED: kit heap live across a pcrec hook that can longjmp (between the `wd_blk` allocations and `wd_free`, `wf_plan_site` calls pcrec's `def` hooks); a population nobody counts (scanner LAYERS are src/ only). Partial evidence: in K163's repro run, `alloc_check.c` W6 failed `wd_alloc` at 896 trials, each diagnosed with no stranded heap (one witness only) | AS-IS for the feature (no scope crosses either handle); the SUSPECTED hazard is PLAN (the manager traces it, then states it to the kit as a FACT, D157) | goal 3; D157 |
| S28 | `Arena` initialisers and `.cx` writers | C-2, C-24 | src: 9 hand initialisers (`Arena a = { 0 }` x8, `{ .cx = c->cx }` x1) + 3 struct fields; 7 `.cx` writes (compile.c 2, syntax_dump.c 3, dfamemo.c, rxt_source.c `= NULL`). tests/ (compiled in `make test`): 17 more writers = 11 `.cx` writes + 6 `{0}` initialisers. Total 33 writers (16 src + 17 test). No init accessor (`pcrec_arena_(init|open|attach)` 0 hits) | ACCESSOR, CONDITIONAL: all 33 change if a scope is an `Arena` that gains fields (RM-3); else proposed row P6 | goal 2 CHECK |

### Commands and counts (all at T)

- C-1 `GG 'pcrec_arena_free(&' src cli lib memfn/src`: 29 calls. findings_dump.c 9, syntax_dump.c 11, measures_dump.c
  2, compile.c 2 (`pcrec_subst_compile`, `job_cleanup`), cli/main.c 1, clskit.c 1, emit_subst.c 1, dfamemo.c 1,
  rxt_source.c 1. `GS src/core/arena.c` (71 lines): `pcrec_arena_alloc` (the `a->cx` branch, then `abort()`),
  `pcrec_arena_own_slot`, `pcrec_arena_own`, `pcrec_arena_free` (the owned walk, then the blocks).
- C-2 `GG -E '\bArena\s+[a-z_]+\s*(=|;|\[)' src cli lib memfn/src`: 13 hits. 9 locals (cli/main.c `esc`; compile.c
  `pcrec_subst_compile`; findings_dump.c 4; measures_dump.c 1; clskit.c 1; emit_subst.c 1), 3 fields (`struct Ctx`
  `arena`; `RxtSource` `arena`; `DfaMemo` `arena`), 1 comment (internal.h "Arena entries"). `GG -E 'Arena|AOwn'
  src/core/internal.h`: the record and the "there are none today" comment (S2).
- C-3 `GG -E 'pcrec_arena_own(_slot)?\(' src`, excluding arena.c and internal.h: 2 lines, both compound.c
  `walk_part` (slot, then `pcrec_arena_own` on the part text).
- C-4 `GS src/core/compile.c | awk '/^static void job_cleanup/,/^}/' | grep -c -E '^\s*free\('`: 27; `... | grep -c
  pcrec_sb_free`: 6 (csb, hsb, vmsb, irsb, scr_test, scr_desc); the same range shows the two union folds first.
  C-4b `GS src/core/compile.c | awk 'NR>=2043 && NR<=3870 && /job_cleanup\(|pcrec_dfa_memo_free\(/'`: 10
  `job_cleanup` calls and 5 `pcrec_dfa_memo_free` calls inside `compile_driver` (the file holds 13 `job_cleanup(` = 1 definition + 10 + 2 in `pcrec_count_groups`). Six `job_cleanup` calls continue
  the loop (the `sets` routine's retry, the size-term ladder's three, the trial catch, the compound-off retry).
- C-5 `GG -E '^\s*(struct )?Ctx\s+[a-z_]+\s*(=|;)' src cli lib memfn/src`: 5 (compile.c `compile_driver`,
  `pcrec_count_groups`; syntax_dump.c 3). Each function is found by the nearest preceding definition line.
- C-6 `GG 'setjmp' src cli lib memfn/src | grep -v -E ':\s*(/?\*|//)'` filtered to calls: 5 `if (setjmp(cx.jb))`
  (compile.c `compile_driver`, `pcrec_count_groups`; syntax_dump.c `built_status_probe`, `pcrec_probe_ask`,
  `pcrec_syntax_explain`). The rest of the hits, re-run with `if (setjmp` and comment-led lines filtered OUT,
  print 8 lines: 1 `#include <setjmp.h>`, 4 CLAUDE.md prose lines, and 3 code lines whose `setjmp` is inside a
  trailing comment (compile.c `defo = *opt`, syntax_dump.c's two `cx.arena.cx = &cx`). None is a call (r100
  lesson 1; rev 1's "the rest are comments" took its count from a comment).
  C-6b `GG -l -E 'built_status_probe|pcrec_probe_ask|pcrec_syntax_explain' tests/mech`: 0 files. C-6c `GG -i -E
  "(only|single)( other)? .?setjmp" src`, read for tree-wide claims: src/core/CLAUDE.md, src/parse/CLAUDE.md,
  compile.c (the pipeline's header comment), parse.c, syntax_dump.c ("the tree's only other `setjmp`"), at least
  5. The other hits say "the compile's one setjmp" and stay true.
- C-7 `GG -E 'dfa_memo|DfaMemo' src/core/compile.c src/opt/dfamemo.c`: `DfaMemo dmemo` and 5
  `pcrec_dfa_memo_free(&dmemo)` in compile.c; `m->arena.cx = cx` and `pcrec_dfa_memo_free` in dfamemo.c.
- C-8 `GG -E '(sb|b|s)->ar\b' src/core/sb.c`: 5 lines, 4 decisions (`sb_store`, `sb_unstore`, `sb_grow`'s
  `if (sb->ar)`, `pcrec_sb_take`'s `sb->p && !sb->ar ? sb->p : strdup(...)`). The borrowed kind: `GG -E
  'StrBuf\s+[a-z_]+\s*=\s*\{\s*\.p' src cli lib`: 1 (emit_compound.c), the scanner's `part_splice` ALLOW row.
- C-9 `GG -E 'StrBuf (nb|tail|o)\b|free\(c->p\)|c->p = nb\.p|free\(old\)|sb->p = o\.p' src/gen/memfn_stamps.c
  src/gen/part_layout.c`: `tail` (splice_mark), `nb`, `free(c->p)`, `c->p = nb.p` (target_headers_render), `o`,
  `sb->p = o.p`, `free(old)` (render_buf). `GS src/gen/part_layout.c`, `render_buf`: 4 `pcrec_ctx_fail` calls
  while `o` is live.
- C-10 `GG -E 'malloc|calloc|free\(|pcrec_arena_alloc|pcrec_ctx_nomem' src/opt/minimize.c`: 8 heap temporaries
  (`GG -c -E '\b(malloc|calloc)\('` gives 8), 3 `pcrec_ctx_nomem` exits that free by hand first, 2
  `pcrec_arena_alloc(&cx->arena, ...)`. One caller: `GG 'pcrec_minimize_dfa(' src` gives dfamemo.c.
- C-11 `GS src/gen/clskit.c`, `pcrec_clskit_emit_kit`: the local arena, its `[ARENA-SCOPES] client` comment,
  `pcrec_arena_free(&a)` on return.
- C-12 `GG -c -E '\b(malloc|calloc)\(' src/opt/scanedge.c`: 10 temporaries in `pcrec_scanedge_dfa`, hand frees on
  each exit.
- C-13 `GG -E 'fd_hook|lc_hook' src`: facts_dump.c and callouts_dump.c, one definition and one use each.
- C-14 `GS memfn/include/memfn.h` (`typedef struct mf_arena` and the comment above it); `GG
  'pcrec_memfn_arena_alloc' src` (memfn_sites.c: the callback over `pcrec_arena_alloc`, and `pcrec_memfn_art`).
  `GG -i arena memfn/src`: `kb` over the caller's `mf_arena` (compose.c, kit.h); formhash.c's own `fh_arena`.
- C-15 `GS tests/core/scratch_builder_check.py`, `ALLOW`. The 5 [ARENA-SCOPES] rows: minimize.c
  `pcrec_minimize_dfa`; memfn_stamps.c `target_headers_render strbuf:nb` and `splice_mark strbuf:tail`;
  part_layout.c `render_buf strbuf:o`; clskit.c `pcrec_clskit_emit_kit arena:a`. The 4 Job heap-array rows: nfa.c
  `nst`; dfa.c `tab_grow` and `intern`; dfamemo.c `pcrec_build_min_dfa`. `GG -E 'known_stranded|ARENA-SCOPES'
  tests/core/alloc_check.c`: rows for minimize.c and target_headers_render.
- C-16 `GS` each file under src/: `grep -n -B4 -A4 -E 'pcrec_arena_alloc\(' | grep -E
  '(cap|ncap|newcap|nc|n)\s*(\*\s*2|\*=\s*2|<<=?\s*1)|2\s*\*\s*[a-z_>.-]*cap'` (run over a `git archive` of T): 42
  lines in 16 files (rxt_source.c 15, emit_vm.c 8, cpset.c 2, varexp.c 2, vm_stmt.c 2, dfa.c 2, mod_vars.c 2, and
  one each in endwin.c, clskit.c, emit_code.c, known.c, nfa.c, atomic.c, callout.c, lower_enc.c, rxt_compose.c).
  Not every line is a growth (some are sizing). `sb_grow` (sb.c), `fq_push` (possessify.c) and the kit's
  `kb_reserve` (compose.c: "the old block stays in the arena") grow by copy and are missed by that grep, so the
  family is at least 18 sites. `GG -E 'arena_regrow' src`: the definition and 2 callers, both dfa.c. Plan row:
  `scripts/entry ARENA-REGROW -l 2`.
- C-17 `GG 'pcrec_sb_scratch(' src`, excluding sb.c and internal.h: 23 lines, one of them prose (22 code calls; k155fix's census names 23 converted builders).
- C-18 `GG -E '(->|\.)into\b' src cli lib memfn/src`: 3 lines (compound.c `w->facts[i].into = &w->cx->arena`;
  compile.c the NULL check and `pcrec_sb_fragf(pf->into, ...)`). `GS src/core/compound.c`: `walk_part`,
  `part_compile` (`pcrec_compile_driver(...)`). `GS src/core/arena.c`: on a failed block `malloc`,
  `pcrec_ctx_nomem(a->cx)`.
- C-19 `GG -E 'Arena\s*\*\s*[a-z_]+\s*;' src cli lib memfn/src`, excluding assignments: 11 fields (internal.h 3:
  `StrBuf.ar`, `PcrecCpSet.ar`, `PcrecPartFacts.into`; endwin.c; clskit.c; dfa.c 3; rxt_find.c; rxt_source.c;
  subst_template.c). `GG -c 'cpset_init(' src`: 19 hits.
- C-20 `GG -E 'pcrec_arena_alloc\(' src cli lib memfn/src`: 465 hits, 462 outside arena.c/internal.h with the stated filter (comments counted as hits).
  `git grep -h -o -E 'pcrec_arena_alloc\(\s*[^,]*' $T -- src cli lib memfn/src`, counted by first argument: 251
  `&cx->arena`, 340 naming `cx->arena` or `cx.arena` through any handle.
- C-21 `GG -E 'scr_test|scr_desc' src`: internal.h `StrBuf scr_test, scr_desc;`; compile.c (the `.cx` attach, the
  comment "`scr_test` follows the artifact and `scr_desc` does not", the two frees); emit_vm.c 4 code lines and 3 comments.
- C-22 `GG -E '(sb|csb|vmsb|out|o|body|b|t|d)(->|\.)p\[[^]]+\]\s*=\s*(0|.\\0.)' src`, excluding sb.c: 6 lines
  (memfn_stamps.c 1, emit_vm.c 4, vm_stmt.c 1), each beside its `len =` write.
- C-23 `GG -E 'wd_blk|wd_alloc|wd_free|wdecide_framed' memfn/src/window.c`; `GG 'mf_wdecide(' src` (emit_dfa.c 3
  calls); `GG -E 'KsAlloc\s+[a-z_]+\s*=' src` (measures.c 2, rxt_find.c, rxt_source.c).
- C-24 `GG -E 'arena\.cx\s*=' src cli lib memfn/src`: 7; `GG -E 'pcrec_arena_(init|open|attach)' src`: 0.

Population sentences are counts of the grep shown, except the family in "Goals served" and "The general form" (a
FLOOR, "at least"), C-16's family (a floor), and C-19 (a floor).

## Register rows looked up

Greps:
- `GS docs/dev/guide/architecture.md | grep -n -i -E 'arena|job_cleanup|sb\.c|minimize|clskit|memfn_stamps|
  part_layout|ARENA-SCOPES|StrBuf|longjmp|setjmp'`.
- Then BY FUNCTION (r100 C18): every register row whose WHERE names a site-map file or function (`compile_driver`,
  `Job`, `Ctx`, `job_cleanup`, compound.c, internal.h). Rows 3, 6a, 6b, 7b, 20 matched; rows 29-32 and 49-51 (the
  noted deviations) were read.
- `GS docs/design/stream/roadmap.md | grep -n -i -E 'arena|job_cleanup|memfn_stamps|part_layout|minimize|clskit|
  StrBuf|internal\.h|compound\.c|compile\.c|sb\.c'`: areas H-FLAGS, A-ENTRY, H-HEADER.

| register row | why it matches | disposition |
|---|---|---|
| 20 One Ctx/longjmp/arena wrapper | S5/S6. WHERE DRIFT IN KIND, not only lines: the row names `pcrec_compile` (compile.c :3771 at T), `pcrec_compile_in` (:3800), `pcrec_compile_defs` (compile_defs.c :43) and "the dump tier's two". The first three are one-line forwarders with no Ctx (`GS src/core/compile.c`, the bodies are `return compile_driver(...)`), and the dump tier has three Ctxs, not two. RE-BASED from C-5/C-6: the population is the FIVE Ctx-owning `setjmp` sites with three teardown spellings, plus the memo's five hand frees (rev 1's P2, folded here). On the re-based count the row's event "a fifth copy" has been met | RIDES FIRST as RM-2 if the design places release anywhere but `pcrec_arena_free` (S6's condition); otherwise NOT CARRIED. The re-based WHERE and the event's status are the manager's to write (the register is the manager's) |
| 7b The artifact as typed parts, kit returns parts | S10/S11: memfn_stamps.c's header-mark splice is one of the row's "three string protocols" (WHERE `memfn_stamps.c:334-341` falls inside `target_headers_render`, defined at :331 at T) | NOT CARRIED: the feature changes where the rewrite's bytes live, not the protocol; the row's event is "the next post-render rewrite" (this adds none). Consequence: when 7b lands, `nb` and `tail` are deleted, not scoped, so the scope's shape is judged on S11 and S13, not on adoption alone |
| 6a Name each Job/Ctx field's writer and readers | if the design adds a Ctx or Job field (D-7) | NOT CARRIED (its event is an emitter-to-driver flag). Its corollary binds any new field: one writer, named readers |
| 6b Stage outputs as typed records | `Job` (S4, S25) | NOT CARRIED: "as roadmap areas migrate, never standalone"; the feature migrates no area |
| 3 Refusal table | `compile_driver` | NOT CARRIED: the feature adds no refusal arm; the handler's fit-rung walk is untouched |

Roadmap areas (each disposed against its own trigger line):
- **H-FLAGS** names "`lmwalk_build` in `compile_driver`, `Job.lmnfa` / `lmdfa`, freed in `job_cleanup`". Its
  trigger is "name the owner, declare the shape". [LANDWALK] is STATE:started (`scripts/entry LANDWALK -l 1`: stage
  1 landed, child rows open). OVERLAP: any design answer to D-3 that rewrites `job_cleanup`'s list rewrites the
  `lmnfa`/`lmdfa` lines. The design names that overlap and leaves those two lines' owner to H-FLAGS. Not carried.
- **A-ENTRY** names compound.c and part_layout.c (composition). S21's nested compile and S12's `render_buf` are in
  its files. Its trigger (X15: the iterate rule reads a declared fact) is not met by this feature. Not carried. The
  design keeps any change to `walk_part` to the facts copy's lifetime (K163's site).
- **H-HEADER** (internal.h, "rides each area's migration"): a new lifetime record lands in internal.h. Not
  carried, because the feature migrates no area.

Rows the note PROPOSES (register columns: remodel | shape (rule) | where | event | size and gate | deletes | state):
- P3 | hand-freed heap temporaries become scope allocations | goal 1 | scanedge.c `pcrec_scanedge_dfa` (C-12) | the
  next refusal added while they are live (the allowlist's safety argument then fails), or the design taking S15 |
  S, no-mover | the hand frees and its ALLOW row | open. (Rev 1's U2 is this row; it is not restated as an unlock.)
- P4 | `job_cleanup`'s named list becomes registrations | goal 1; Notice siblings | compile.c `job_cleanup` (C-4),
  with S22's two end actions | the next Job heap array or end action added to the list by this feature's clients (R-3 refuses that addition for them, so the addition is this row's trigger instead; R-3 is read in that scope, not over every future Job heap array, e.g. [LANDWALK]'s machine arrays use the list's own mechanism), unless D-3 takes it now | M, no-mover | the named list (27 frees, 6
  sb_frees, the 2 folds as list members) | open. Overlap: H-FLAGS / [LANDWALK] (the `lmnfa`/`lmdfa` lines).
- P5 | StrBuf truncation through its owner (`pcrec_sb_truncate`-shaped; the name is the design's) | goal 2; "A
  structure is read and written through its owner's accessors" | memfn_stamps.c `splice_mark`; emit_vm.c x4;
  vm_stmt.c (C-22) | a StrBuf storage kind whose truncation is not "write `len`, NUL the byte" (e.g. a mark or
  layout record kept beside the bytes), or a seventh hand truncation | S, no-mover | 6 hand truncations | open.
- P6 (only if RM-3 is not taken) | `Arena` initialised and bound to a Ctx through `arena.c` | goal 2 | the 33
  writers (C-2, C-24; 16 src + 17 tests) | a field added to `Arena` | S, no-mover | 16 hand initialisations | open.

Rev 1's P1 (grow-by-copy) is WITHDRAWN as a register row (r100 C10). Its event has fired: plan row [ARENA-REGROW]
says "the allocation half ... is ready now". So it is a PLAN-ROW UPDATE for the manager: the row gains `sb_grow`,
the kit's `kb_reserve` (a kit fact, D157), and C-16's population as a declared grep. Its refs cite `src/gen/dfa.c`,
but the file is `src/ir/dfa.c` (DOC). Rev 1's P2 is folded into row 20 (above).

NOTED DEVIATIONS on touched sites: none. Rows 29-32 and 49-51 were read; row 49 (formhash.c) names a kit file
whose private arena is a sibling (C-14) that the feature does not touch. This note proposes none.

D-row "Revisit when" triggers on mapped sites: D70's ("a future allocation-model change makes the arena pointer in
a payload wrong") IS met by this feature wherever an AST payload holds an `Arena *` that could name a scope (S23).
The design either keeps scopes out of payloads or carries D70's revisit. D56's trigger (a legitimate pattern
measured needing more than the cap) is not met. D109's Revisit says its scope excludes four handlers because they "read no per-attempt Ctx field". If the open-scope record is a Ctx field that those handlers' teardown reads (D-7's "on the Ctx"), that premise stops holding, so the design carries D109's revisit (D-4/D-7). D19, D105, D110 and D203 carry none. D109's Revisit clause BEARS (see below). Found by `grep -n -i
revisit docs/dev/decisions.md` within those rows.

## Remodels that land first

**RM-1: a heap-only StrBuf storage swap moves into `sb.c` (S9; r96 GENFORM-5/COST-2), plus the S2 comment's
truth.**
- WHAT CHANGES SHAPE: the two transplants stop writing `p`/`len`/`cap` and calling `free()` themselves. One `sb.c`
  primitive ADOPTS a finished builder's storage into a destination buffer. At T it is stated over `pcrec_sb_take`'s
  existing decision (move if heap), and it REFUSES (an internal-error `pcrec_ctx_fail`, or an assertion: the
  design's spelling) a source whose `.ar` is set. There is no caller of the arena branch at T. Building it now
  would be built ahead of need, and r96 placed the by-`.ar` primitive "as part of the scopes design". So the arena
  branch is D-6's, inside the feature.
- The records the swaps also adjust (`simd_guarded`, `simd_size`, `layout_bytes`) stay at their sites. The
  primitive moves storage only.
- The same unit corrects S2's comment to name the three Arena kinds (comment only, no-mover).
- GATE: no-mover, byte identity (both sides heap at T, so the primitive frees exactly what the two sites free
  today). SIZE: S.
- CHECKS THAT BIND THE MOVED CODE, by population: `GG -l -E 'target_headers_render|render_buf|sb_grow' tests/mech`
  gives S256, S257, S3572, S3584, S701 (5 files; rev 1 listed an S3571 that this grep does not print).
  - Anchored INSIDE `target_headers_render`: S1897 (`rest = strchr(h + strlen(held), ...)`) and S1899
    (`- nheld * strlen(held)`), whose populations reach the swap.
  - Nothing is anchored inside `render_buf`. The part-layout rows S1111-S1127 (8 files with `SAB_FILE` part_layout.c)
    have witnesses that render layout marks and so reach `render_buf`. S1115 and S1126 read `layout_bytes`, which the
    swap zeroes.
  - S3572/S3584 bind the scanner's name-narrowed `nb` row (source-level, they do not run the swap). S256 binds
    `sb_grow`'s nomem route (anchor recheck: `python3 scripts/m6read_check_sab_anchors.py`). S257 binds `csb`'s
    attachment. S3570 (emit_dfa.c) does not anchor in moved code.
  - Also: the scanner's `ALLOW` rows for `nb` and `o`, and `alloc_check.c`'s `target_headers_render` filed row
    (stays reached: the swap still runs on the heap).
  - The gate names a population that reaches BOTH sites: the memfn header-mark tests and the part-layout corpus.
- SEPARABLE: yes. It lands answer-identical with no scope in the tree, because at T every storage it moves is heap.
- SPEED: byte-identical emitted code; one call in place of five assignments; no timing check needed.
- DELETES: two hand transplants and their raw `free()`s (goal 2's "swap or free storage outside sb.c" writers go to
  zero); the false S2 sentence.

**RM-2 (CONDITIONAL): register row 20 re-based, one Ctx/setjmp/teardown wrapper.**
- Lands first if the design places release anywhere but `pcrec_arena_free` (D-4/D-7). Release in `job_cleanup`
  reaches 2 of the 5 src handlers (2 of 11 with the test tier's 6 more recovery points, S6), and the three dump-tier handlers free by hand.
- One wrapper over the five Ctx-owning sites must exist first. It also takes the memo's five hand frees, which
  makes it one exit for `compile_driver` (U9).
- GATE: no-mover. SIZE: S (the row's own).
- CHECKS: S255 (arena nomem), the dump tier's tests. No sabotage row binds the dump-tier teardowns (C-6b), so the
  unit adds one per spelling it removes.
- SEPARABLE: yes.
- DELETES: four of the five hand teardown spellings and four of the five memo frees.
- If release is inside `pcrec_arena_free`, this is not a unit and row 20 keeps its re-based trigger.

**RM-3 (CONDITIONAL): `Arena` initialised through `arena.c` (S28; goal 2 CHECK).**
- Lands first if D-1 makes a scope an `Arena` with a new field (a parent link, a mark). The 33 hand writers (16 in src: 9
  initialisers, 7 `.cx` writes; 17 in tests/: 11 `.cx` writes, 6 `{0}`) then go through one initialiser, so the new field has one writer.
- GATE: no-mover, byte identity. SIZE: S.
- CHECKS: S255 (`pcrec_arena_alloc`'s nomem route, arena.c); `alloc_check.c` W1-W6, which compile through
  `pcrec_compile` and so reach the Ctx-owned arenas only. The detached and dump-tier initialisers have no witness
  named here, so the unit names the check that reaches them.
- SEPARABLE: yes.
- DELETES: 33 hand spellings.
- If D-1 adds no field, proposed row P6 holds it.

No other site needs a remodel first. S3/S4/S7 (SHARED) are the feature's own general form, not a reshaping the
feature could land without. S13 and S14 are clients and move with the feature. S21 is K163's (a bug, fixed at its
class, D203), not a remodel.

## The general form and its siblings

THE GENERAL FORM, representation-free (r100 C2). Work has LIFETIMES, and lifetimes nest: compile > attempt >
scope. A nested part compile (S21) adds outer attempt > inner compile > inner attempt, across two Ctxs, so the
nesting is a tree, not a line. Each lifetime owns what was registered with it. A lifetime is released:
- (a) on its own normal exit, innermost first;
- (b) all together when its recovery point's teardown runs after a longjmp.

Its end actions (S22) run before its memory goes. The owner's "stack memory extension" is this shape:
"registered such that the exit could free them" is (b), "allocated up and deallocated down the stack" is (a).

TWO CANDIDATE SHAPES, both inside that form. The design picks one (owner: "Not proscribed"; scope-reach below is a
CONFIRM that the mechanism is the design's):
- **(A) arena levels**: a scope is an arena whose blocks are freed at its exit; heap blocks join through
  `Arena.owned` (S3). Under the note's own D-3 reasoning, S4's realloc'd Job arrays cannot join (an arena cannot
  grow in place without COST-1's retention), and S7's cross-attempt memo sits ABOVE the attempt. Both stay second
  mechanisms unless (A) also takes heap entries.
- **(B) r96 GENFORM-8's registry**: one per-Ctx list of {pointer, free fn} entries with scope marks AND a release
  operation. Heap temporaries are freed when they are today (no peak cost) and on a longjmp. Arena blocks are one
  entry kind. S4's arrays and S22's end actions are entries, and S7 is an entry at a compile-level mark. Under (B) the whole named list, `lmnfa`/`lmdfa` included, becomes entries: the H-FLAGS / [LANDWALK] overlap applies.
- (B) is the WIDER form. (A) is (B) restricted to arena entries. The DECIDING sites are S4 and S7 (and S22, S21):
  the shape that covers them deletes the most answers. GENFORM-8/9's "resource entries only at a second member
  (D77)" gates NON-MEMORY entries (a FILE*, an end action). It does not gate heap pointers, which are memory. Rev
  1's U6 said "no non-memory member at T". Whether S22's two order-bound end actions (they free nothing) count as
  GENFORM-9 "resource entries" ({pointer, free fn} that a longjmp frees) is an OPEN CLASSIFICATION, listed under D-3
  for the design step; this note declares no gate met.

THE FAMILY TODAY (one answer each to "what dies when", site map; at least 13 members, a floor):
- the attempt arena S1 and its owned list S3;
- the compile-lifetime memo arena S7;
- `job_cleanup`'s named list S4 and its end actions S22;
- the five handlers' teardowns S6;
- the hand-freed temporaries S13, S15;
- the private arena S14;
- the Job scratch pair S25;
- the nested part compile's facts copy S21 (K163);
- the caller-owns hooks S16 (need nothing);
- the detached no-Ctx arenas (C-2: 8 locals and `RxtSource.arena`), outside any compile and needing nothing;
- the kit's own siblings, which stay the kit's: `fh_arena` (formhash.c), `wd_blk` (window.c `wdecide_framed`) and
  `kb` (compose.c). S27's `KsAlloc` handles are pcrec's.

PLANNED ROWS THAT EXTEND THE SAME SHAPE:
- [ARENA-REGROW] (arena-grown stacks). The shape covers it if a lifetime can hold a growing region released
  early (D-5). Else it stays that row's own primitive.
- [K155-STAMPS-LEAK]'s next line ("move nb/render_buf/splice tail onto a scoped arena") is this feature's first
  client set.
- `scripts/entry -g arena -in 2` and a plan grep for `scoped|job_cleanup` found no other row that extends it.

UNLOCKS, each with its trigger:
- U1: the 23 scratch builders (S20) and D105's legend arrays move into short scopes, lowering peak. Trigger: a
  measured peak cost in the job arena (D77; COST-1's census found them linear).
- U3: the memo's five hand frees become one compile-level registration. Trigger: RM-2, or a design taking S7.
- U4: `job_cleanup`'s named list becomes registrations (P4). "A new allocation belongs here or it leaks on abort"
  (its own comment) stops being a rule a writer must remember. Trigger: as P4. Overlap: it rewrites the `lmnfa`/`lmdfa` lines, H-FLAGS / [LANDWALK] (STATE:started).
- U5: the scanner's allowlist (S18) shrinks as clients move. Trigger: each client's move (same change).
- U6: non-memory resource entries (a FILE*, r96 GENFORM-2's shape). Trigger: GENFORM-9's second NON-MEMORY member.
  Whether S22's end actions are a second member is open (D-3's classification); GENFORM-2's FILE* was fixed by reordering.
- U7: grow-by-copy released early (a lifetime that frees a growing region's old blocks). Trigger: a S19 member
  measured super-linear, or a retained-garbage share of peak above noise.
- U8: the nested part compile's teardown registered with the enclosing attempt (S21), so a longjmp to the outer
  recovery point also frees the inner compile. Trigger: the first scope design (D-2/D-4 decide it), or K163's
  witness.
- U9: one exit for `compile_driver` (the memo frees and the teardown in one place). Trigger: RM-2.
- (Rev 1's U2 is proposed row P3.)

## Seams

| seam | writer | readers | facts down | facts up | new calls and their layer direction | text round trip |
|---|---|---|---|---|---|---|
| core lifetime API (arena.c, sb.c; internal.h; module-internal) | arena.c, sb.c | every src/ layer (C-1, C-17, C-20) | a lifetime to allocate in | none | opt/ and gen/ clients call down into core/ for open/close and RM-1's adoption; no upward call | n/a (in-process memory; none needed) |
| the longjmp crossing (five `setjmp` handlers, S6) | `pcrec_ctx_fail`/`pcrec_ctx_nomem` (core) | each handler, then its teardown (`job_cleanup`, or the hand frees) | that the work failed (`failed_nomem` first, D109) | the OPEN-SCOPE RECORD: opt/ and gen/ clients write it (opening and closing their lifetimes), the handler's teardown reads it to release. One writer per entry (the client that opens it), one reader (the teardown) | none new; release happens in the existing teardown(s) | n/a |
| the nested compile (compound.c -> `pcrec_compile_driver`, S21) | the outer attempt (`walk_part`: options, `meas`, `facts.into`) | the inner compile | options, the inherited measurement set, an outer-arena handle | the part's facts, copied into the outer arena (`memfn_forms`), the part text (owned by the outer arena via `pcrec_arena_own`) | none new. The design states which recovery point owns an allocation made through `facts.into` (K163; U8) | the facts are plain values plus one string; they could be written to text and read back |
| kit `mf_arena` (memfn.h; MODULE seam, D146) | pcrec (memfn_sites.c, over the attempt arena) | the kit (`kb`, the art) | an allocator whose memory outlives `mf_art_end` | none | NONE: unchanged. pcrec PINS on its side that the art's `mf_arena` is the attempt's arena, never a scope (D-11). Any memfn.h wording change is a kit request (PLAN) | unchanged |

The kit's `kb_reserve` grows by copy in pcrec's attempt arena (S19), which is COST-1's mechanism inside the kit.
Whether that matters is a kit question, stated to the kit as a fact (its blocks are retained to the attempt's end)
if D-5 makes it one. `window.c`'s `wd_blk` heap is the kit's own lifetime. The SUSPECTED hazard (S27) is a kit fact
to state after the trace. No kit code shares a scope.

## What is deleted

- RM-1: the two hand transplants (S9) and their raw `free()`s; the false S2 sentence.
- RM-2 (if taken): four hand teardown spellings and four memo frees.
- RM-3 (if taken): 33 hand Arena writers (16 src, 17 tests).
- The feature:
  - `clskit.c`'s private arena and its comment (S14);
  - `minimize.c`'s 8 hand frees and its 3 free-then-nomem exits (S13);
  - the three rewrites' heap builders and their `[ARENA-SCOPES] client` comments (S10-S12);
  - 5 scanner `ALLOW` rows and 2 `alloc_check.c` `known_stranded` rows (S18), with K155's three-rewrite remainder
    closed;
  - the checks that exist only for those rows (S18): S3584's SAB_BEFORE (the `nb` client line), S3572's premise (the `nb` row), and `alloc_check.c`'s stack recording and `fn` column (unreached once `target_headers_render` leaves its filed row);
  - if D-3 takes it, `job_cleanup`'s named list in favour of registrations (P4), excluding the `lmnfa`/`lmdfa` lines'
    ownership (H-FLAGS);
  - if D-8 takes S25, the Job scratch pair's hand frees.

## What the design step must decide

Handed on, not decided here:

- D-1 THE API (S1, S3, S8, S24): how a lifetime is opened, allocated from and closed; shape (A) or (B) ("The general
  form"), judged at S4, S7, S21, S22; whether a scope IS an `Arena *` (S8's `.ar` branch takes it unchanged, RM-3
  fires if it gains fields) or another type (S8 WIDEN). It also decides how 462 allocation calls see it: an explicit
  handle at client sites only, or an implicit "current" lifetime that changes 340 calls' meaning.
- D-2 THE LIFO DISCIPLINE, and how a violation is caught (S1, S13, S21, S23):
  - closing a lifetime that is not the innermost;
  - allocating into an OUTER level while an inner one is open (minimize's `ns[c].up`/`.tr` outlive its tables; the
    inner compile's `facts.into` copy);
  - a handle escaping a closed scope through the 11+ captured `Arena *` fields (D70's revisit for AST payloads).
- D-3 WHAT `job_cleanup`'S LIST BECOMES (S4, S22, P4). It is kept, or it becomes registrations. Constraints:
  - the Job's machine arrays grow by `realloc` in place (the 4 allowlisted sites; two rely on an
    adopt-before-next-allocation order);
  - the two end actions are order-bound before any free. OPEN CLASSIFICATION: whether they are GENFORM-8/9 resource entries at all (they free nothing), hence whether the D77 second-member gate is met. This note does not decide it; GENFORM-9 is a candidate the design picks;
  - the registration must key on the owner FIELD, not the pointer value: compile.c:587-591 swaps the machine arrays between the primary and x-set Job fields by value (`revend` tagged form), a second mutation beside `realloc` (SUSPECTED, SITEMAP-5);
  - R-3 bars adding a member to the list;
  - the `lmnfa`/`lmdfa` lines overlap H-FLAGS / [LANDWALK] (STATE:started).
- D-4 HOW A LIFETIME INTERACTS WITH THE LONGJMP (S6, S21):
  - which of the five handlers' teardowns release it (decides RM-2);
  - its order against `compile_driver`'s handler reads (`fit_labels`, the `sets` carries, all BEFORE
    `job_cleanup`);
  - every lifetime EMPTY at each of the 6 mid-compile retries (C-4b);
  - the memo (S7), whose `.cx` is the attempt but whose lifetime is longer;
  - the nested compile, whose OOM lands at the OUTER recovery point (K163);
  - D109's Revisit: its scope excludes four handlers because they "read no per-attempt Ctx field". An open-scope record on the Ctx that those handlers' teardown reads voids that premise, so the design carries D109's revisit (D-7).
- D-5 COST-1 (S19, S20): whether a lifetime answers grow-by-copy retention (U7), or [ARENA-REGROW] does; whether
  the kit is told the fact.
- D-6 ADOPTION (S10, S12, RM-1): how a builder's finished bytes leave a scope to become the Job's `csb` (a copy, or
  a hand-off). This WIDENS RM-1's heap-only primitive to the by-`.ar` form (r96's "as part of the scopes design").
- D-7 REGISTRATION HOME (S5, row 20, row 6a): on the Ctx (as the plan row words it), on the parent lifetime, or on
  the Job. D109's memset makes per-attempt Ctx state start empty by construction.
- D-8 THE CLIENT SET for the first build: at least S10-S14; S15, S25 and U1 by trigger or by choice.
- D-9 TESTS AND GATES:
  - the alloc_check property for lifetime clients (populations are floors, D110);
  - a witness that fails an allocation which takes no new arena block (the single-shot sweep cannot: K163);
  - the scanner's rule for a builder on a scope;
  - the growth library stage going green (K155's witnesses);
  - sabotage rows for each release path, the dump-tier handlers included;
  - the peak measurement against R-3's families;
  - R-1's "no refusal moves at growth memory-cap rungs", and whether a favourable move (a refused pattern now
    compiles) is allowed. That is a gate wording question for the manager, asked by the design with the measured
    moves.
  - LEAK-ATTRIBUTION (REQ-OPEN): the 13 growth leaks' sites.
- D-10 the scope sentence of S2's comment (RM-1 writes the three-kinds sentence; the design adds scopes).
- D-11 the `mf_arena` pin (S17): "the art's `mf_arena` is the attempt's arena, never a scope", stated on pcrec's
  side, with the check that holds it (a test, or an assertion at `pcrec_memfn_art`). Any memfn.h wording is a kit
  request.
- D-12 src/core/CLAUDE.md's "Cross-attempt state is plain `Ctx` fields, not arena text". This note reads it as
  binding the RETRY DECISION state (what the handler carries to the next attempt), not data that legitimately
  lives across attempts (the memo arena, S7, already does). If the design adds a compile-level lifetime, the rule's
  wording gains that distinction in the same change (DOC).

## Open questions for the owner

- **scope-reach** (CONFIRM, re-framed against r100 C2).
  - TODAY: `minimize.c`'s tables are malloc'd and hand-freed; an out-of-memory inside it strands them
    (`alloc_check.c` files it). Other "what dies when" answers in the tree (Job arrays grown by realloc, the memo's
    cross-attempt arena) are not arenas.
  - EXAMPLE (hand-worked): under shape (A), those tables become arena blocks of a scope, and the realloc'd Job
    arrays stay in `job_cleanup`'s list (a second mechanism). Under shape (B), each table is a {pointer, free fn}
    entry under a scope mark, freed at its exit and on a longjmp, with no peak cost; the Job arrays and the memo
    are entries too. (Taking the whole named list, `lmnfa`/`lmdfa` included, overlaps H-FLAGS / [LANDWALK], STATE:started; the design names it.)
  - QUESTION: your words ("Not proscribed: If arenas were registered such that the exit could free them") name
    arenas. Do they leave the MECHANISM to the design, so the design may build the wider registry (r96 GENFORM-8,
    which takes arenas as one entry kind) if it deletes more special cases?
  - LEANING: yes. The record reads that way ("Not proscribed"; "Go with your general form", k155-fix-go). The design
    picks at the deciding sites S4/S7. Non-memory entries still wait for their second member (GENFORM-9), which S22
    may already supply.
  - Records: the owner 2026-11-24 10:32 and 10:54 as quoted above; r96 GENFORM-8/9; r100 C2.
- **scope-peak**: DROPPED (r100 C24, RULED: "drop it, citing the records, or re-ask it with each answer's priced
  consequence"; this note DROPS it). The records already answer it. R-3 treated peak memory as a binding gate (it
  refused the 7-12% and a `job_cleanup`-freed field). R-1 set the gate as "arena high-water delta + no refusal moves
  at growth memory-cap rungs". The owner's words name both directions ("allocated up and deallocated down the
  stack" and "the registration used to clean up on exit"). Lowering peak on the success path and freeing everything
  on a refusal are therefore both requirements (stated in "Goals served", Traded against). The one open wording, a
  favourable refusal move under R-1, is a manager gate question handed to D-9.

## r100 disposition

| C-n | ruled | where answered in rev 2 (or why NOTED) |
|---|---|---|
| C1 | FIX-NOW + DOC | S5/S6 (five handlers, three spellings, mid-compile retries in S4/C-4b); C-6 re-run with the filter; D-4; the stale "one setjmp" comments counted (C-6c) for the manager to file |
| C2 | FIX-NOW | "The general form": stated representation-free; candidate shapes (A)/(B) with S4/S7/S21/S22 as deciding sites; scope-reach re-asked as "may the design pick the mechanism" |
| C3 | FIX-NOW | Requirements (R-3's refusal and its consequence; k155-fix-go cited); S4; D-3; P4 |
| C4 | FIX-NOW + PLAN | S21; the family; D-2/D-4; seam "the nested compile"; U8; K163 filed in known_issues.md with the repro attempt |
| C5 | FIX-NOW | S22; D-3; U6 corrected |
| C6 | FIX-NOW | RM-1 made heap-only over `pcrec_sb_take`'s decision, refusing `.ar`; D-6 widens it |
| C7 | FIX-NOW | RM-1's checks re-derived by grep (no S3571; S1897/S1899 added; S1111-S1127's population and S1115/S1126 named) |
| C8 | FIX-NOW | Goals (goal 2 sentence narrowed to swap-or-free, 2); S26 (6 truncations) and P5; S8 gains the borrowed kind |
| C9 | FIX-NOW | Register row 20 re-based (kind drift, five sites, event met); RM-2 re-derived (2 of 5 under `job_cleanup`; dump-tier sabotage gap); C-1's syntax_dump count is 11 |
| C10 | FIX-NOW + DOC | S19 counted by a declared grep (at least 18); P1 withdrawn as a plan-row update to [ARENA-REGROW]; the `src/gen/dfa.c` ref drift named for the manager |
| C11 | FIX-NOW | S24 (461 / 340 / 251); D-1 |
| C12 | FIX-NOW | S23 (at least 11 by the shape grep; r100's 13 noted as a hand read); D-2 |
| C13 | FIX-NOW | S25; the family; D-8 |
| C14 | FIX-NOW | S1 (three Arena kinds); S2 corrected inside RM-1; D-10 keeps the scope sentence only |
| C15 | FIX-NOW + PLAN | S27; the family; Seams text (the rev 1 "no kit code shares a scope" now follows the read of window.c); the SUSPECTED hazard is PLAN for the manager (trace, then a kit fact) |
| C16 | FIX-NOW | S28; RM-3 (conditional) or P6 |
| C17 | FIX-NOW | Register section: H-FLAGS, A-ENTRY, H-HEADER disposed one by one; the [LANDWALK] overlap named at S4, P4, D-3 and "What is deleted" |
| C18 | DOC | Rows 3 and 6b, one line each, NOT CARRIED; the register grep now runs by function too |
| C19 | FIX-NOW | Rev 1's P2 folded into row 20 (re-based); U3/U9 point at RM-2 |
| C20 | DOC | P4's trigger is now an event; P3 and U2 merged (U2 removed) |
| C21 | FIX-NOW | Requirements' D-row survey: 33 hits, 14 rows; D109, D70's revisit, D110 (and D32 §8) added; D70's trigger in "Register rows" |
| C22 | FIX-NOW | Goals "Traded against" (R-1's rung gate); D-9 |
| C23 | FIX-NOW + PLAN | S17 and D-11 (the pin on pcrec's side and its check); seam table's facts up for the longjmp crossing; memfn.h wording is a kit request (PLAN, manager) |
| C24 | FIX-NOW | scope-peak DROPPED, citing R-3, R-1 and the owner's two directions |
| C25 | DOC | The owner quote now carries the record's "Memory fix:" lead and marking; rulings cited by journal entry time at T; D105's reason is proportionality |
| C26 | FIX-NOW | D-12 (the reading this note takes, and the DOC change if a compile level is added) |
| C27 | DOC | S4 names the four allowlisted Job heap-array sites and their ordering; D-3 |
| C28 | FIX-NOW | Unlocks U7, U8, U9 with triggers; U6's fire-ability restated |
| C29 | NOTED | No change: coding.md's scratch-builder rule cites [ARENA-SCOPES] outside the register, and the register stays silent on the five allowlisted clients until they move (U5); the register is the manager's |

## r101 disposition

Review `docs/dev/reviews/2026-11-24-r101-arenaarch2.md`, RULED all accepted as proposed (FIX-NOW 5, DOC 5). Applied by lane arenafix3. Tree T is unchanged (no re-freeze: every item is text or a count).

| item | ruled | where answered |
|---|---|---|
| DISPO-1 | FIX-NOW | the [LANDWALK] / H-FLAGS overlap now named at the R-3 consequence (Requirements), shape (B), U4 and the scope-reach EXAMPLE (the four missed sites); a grep for `lmnfa` and for "named list" over this note lists every site |
| DISPO-2 | FIX-NOW | "D-row Revisit triggers": D109 now BEARS (removed from "carry none"); D-4 gains the D109-revisit bullet (carried to D-7) |
| DISPO-3 | FIX-NOW | P4's event, scoped to this feature's clients, with R-3 not read over every future Job heap array |
| DISPO-4 | FIX-NOW | "The general form" and U6 no longer declare the GENFORM-9 gate met; D-3 lists S22's classification as an OPEN item the design picks |
| DISPO-5 | DOC | K163's fix option 1 (known_issues.md) is worded as a direction (a holder the outer level owns before the copy), not a recipe |
| SITEMAP-1 | DOC | S4 and C-4b: 10 `job_cleanup` calls in `compile_driver` (13 in the file = 1 + 10 + 2); S4's `free(job)` double count removed |
| SITEMAP-2 | FIX-NOW | S6, S28, RM-2, RM-3, "What is deleted": the test tier's 6 more recovery points (2 of 11) and 17 more Arena writers (33 total); release must also hold for memset-only test Ctxs |
| SITEMAP-3 | DOC | S18 and "What is deleted" name S3584, S3572 and `alloc_check.c`'s stack recording and `fn` column |
| SITEMAP-4 | DOC | C-17 (22 code calls of 23 lines), C-20 (462), C-21 (4 code lines, 3 comments); S20, S24 and D-1 follow |
| SITEMAP-5 | DOC | S4 (writer) and D-3 (constraint: key on the owner field), SUSPECTED |

## STATE AT HANDOFF

Lane arenaarch2, 2026-11-24. T = 4b8f6a719 (lane/arenaarch HEAD at start). Rulings file `arenaarch2_rulings.md`:
empty at every re-read, so no ruling was applied. Every site-map command was re-run at T. K163 was filed in
docs/dev/known_issues.md. Its one repro attempt (alloc_check W6, `--both --sites`, 19:12-19:17) did NOT reproduce it, and the entry gives the reason. Next: the light re-check round named in r100's RULED section.
OWED: none

Lane arenafix3 (2026-11-24): applied r101's 5 FIX-NOW and 5 DOC items (see "r101 disposition"); T unchanged; rulings file empty at every re-read.
OWED: none
