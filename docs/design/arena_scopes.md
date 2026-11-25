# Scoped lifetimes registered on the Ctx's arena ([ARENA-SCOPES]): design
STATUS: PROPOSED (lane arenadesign, 2026-11-24). Next: a FRESH critic round (pcrec-critic, design mode), then the
owner's build go. Input of record: the ACCEPTED architecture note `docs/design/arena_scopes_arch.md` (site rows
S1-S28, remodels RM-1..RM-3, questions D-1..D-12), reviews r100 and r101 as RULED, review r96 (GENFORM-2/5/8/9,
COST-1/2), D203, known_issues K155 and K163.
TREE: T = 79a7ca279 (lane/arenadesign at start). `git diff --stat 4b8f6a719 T -- src cli lib memfn/src tests/core`
is empty, so every site row of the note still holds; the few new facts below are read at T and say how.
OWNER RULINGS IN FORCE: "arena-scopes-go: yes"; scope-reach, 2026-11-24, verbatim: "yes let design choose. I believe
I said "not proscribed" so that it was a source of inspiration rather than a specific instruction". R-3 (peak memory
binds: +7-12% refused; a `job_cleanup`-freed field refused "as a second mechanism"). R-1 (arena high-water delta, and
no refusal moves at the growth memory-cap rungs).

THE DESIGN IN ONE PARAGRAPH. Each `Arena` keeps a LIFO REGISTRY of entries. An entry is a lifetime-owned resource of
one of three MEMORY kinds (a heap block, a heap-backed StrBuf, a child arena), declared in one kind table with its
release function. A SCOPE is a mark in that registry: `pcrec_scope_open` takes it, `pcrec_scope_close` releases every
entry above it, newest first. `pcrec_arena_free` releases the whole registry before the blocks, so EVERY teardown that
exists today (the five `setjmp` handlers and the test tier's six recovery points all end in it) releases open scopes on
a longjmp with no new call. Entry RECORDS are heap, not arena, so the attempt arena's bytes do not move at all. Heap
temporaries stay heap and are freed exactly when they are freed today, so peak memory does not move. This is shape (B),
r96 GENFORM-8's registry, restricted to memory kinds (GENFORM-9: non-memory entries wait for a second member).

## Goals

Ranked; a higher goal wins a conflict. Each has who benefits and a checkable form.

1. **G1 Emitted bytes do not move** (users; the speed gate's proof). Check: the byte-identity sweep over the corpus
   gives 0 differing artifacts at every unit; no `abi` bump anywhere in the build.
2. **G2 Peak memory does not move** (users with large patterns; R-3, R-1 bind). Checks: (a) attempt-arena high-water
   bytes IDENTICAL on the corpus (records are heap; nothing new is allocated from any Ctx arena); (b) massif peak heap
   on R-3's three-rewrite families and on k155fix2's witnesses within +1% or +4 KB of base, whichever is larger (the
   only new heap is entry records, at most one per live entry, reused); (c) 0 refusal moves at the growth memory-cap
   rungs (R-1). A favourable move cannot arise, because no peak is lowered; if one appears it is reported, not kept.
3. **G3 Nothing strands on a refusal for the client set** (library callers; K155, K163, D203). Checks:
   `tests/core/alloc_check.c` diagnosed-and-nothing-stranded over every trial, with BOTH filed `known_stranded` rows
   deleted (2 to 0) and a new witness that fails arena allocations taking no new block (W7); the growth sweep's 13
   LSan leak shards (cloud run 45492837175) green; K163's lent-channel check reads 0 uses over the corpus.
4. **G4 One home for "what dies when"** (maintainers; architecture goal 1). Checks: the hand-kept answers the first
   build deletes, counted in D-1 (6 family members: S10-S15); scanner `ALLOW` rows naming [ARENA-SCOPES] 5 to 0;
   hand `free()` calls in the client functions 25 (minimize.c) + 37 (scanedge.c) + the 2 transplants' to 0.
5. **G5 Compile-time cost stays in noise** (users; compile speed is not the product, but must not regress). Check:
   instruction count (callgrind, or `perf stat -e instructions` on the dev box) of compiling the corpus within +1%.

NON-GOALS. COST-1's grow-by-copy retention class (D-5, its own row); converting `job_cleanup`'s named list (D-3,
P4 keeps its trigger); the memo's compile lifetime (S7, U3/U9 keep RM-2's trigger); non-memory entries (FILE*,
end actions; GENFORM-9); moving the 22 scratch builders into scopes (U1); the kit's own arenas (`fh_arena`,
`wd_blk`, `kb`: the kit's lifetimes, D157); any `mf_arena` wording (a kit request, never this build).

### Standing questions (docs/design/CLAUDE.md)
1. Measurement regime: RELEVANT. Peak heap is read by valgrind massif (deterministic for a given allocator; glibc
   2.x on the dev box, gcc 15.2, Zen 4), arena high-water by counting arena bytes (exact), RSS only as a secondary
   read (glibc trim makes it noisy; it would not flip G2, because massif and the arena count are primary). Compile cost
   is an instruction count, not wall time, so no timing window is needed (D191 addendum 1's derived consequence).
   Probes run only after the owner's box hold (01:00), each under `scripts/watchdog`.
2. Independent control: RELEVANT. The source-scan scanner (`tests/core/scratch_builder_check.py`) and the runtime
   witnesses (`alloc_check.c`'s stranded-heap property; LSan on the growth shards; ASan use-after-free) read different
   sources, and each is the other's control. The runtime LIFO and lent-channel checks are controlled by their
   sabotage rows (section "Tests and sabotage"). Populations nobody counted before: arena allocations that take no
   new block (W7 counts them), and recovery points outside src/ (the test tier's six; they reach release through
   `pcrec_arena_free`, verified by grep below).
3. What moves when data is regenerated: NOT relevant (no table, measure set or oracle store is read or written).

## Decisions D-1..D-12

### D-1 The API and the mechanism: shape (B), the registry, memory kinds only

THE CHOICE, decided by deleted special cases as the owner ruled. A "special case" here is a hand-kept answer to
"what dies when this work ends" (the note's family list). Counted per site:

| site (arch note) | today's hand answer | (A) arenas only: deletes? | (B) registry: deletes? |
|---|---|---|---|
| S4 `job_cleanup` named list (27 `free` + 6 `pcrec_sb_free`) | one list a writer must remember | NO, cannot: the machine arrays grow by `realloc` in place and are swapped between fields by value (compile.c `revend` x-set swap); an arena or a by-value owned slot cannot follow either | CAN (an entry keyed on the FIELD survives realloc and the swap), all 33 lines. NOT TAKEN in this build (D-3) |
| S7 memo arena, 5 hand frees | 5 calls at 5 returns | NO without one exit for `compile_driver` (RM-2) | NO without RM-2; equal to (A) |
| S22 end actions (2 folds) | ordered lines | n/a (not memory) | n/a: classified NOT resource entries (D-3) |
| S21 nested compile copy (K163) | none (a bug) | fixed by the existing own-slot hold (D-4); same in both | same |
| S3 `Arena.owned` | the attempt-lifetime heap list | kept beside scopes | kept, as the registry's BASE level (same release walk); not counted as deleted |
| S10 `target_headers_render` `nb` | heap builder, strands (K155) | NO: an arena builder grows by copy (about 2x retained) and adoption into the heap `csb` must COPY the whole artifact: a peak rise R-3 refuses | YES: heap builder in a STRBUF entry, adopted by hand-off, no copy, today's peak |
| S11 `splice_mark` `tail` | heap builder | YES (one append: one block, no doubling) | YES |
| S12 `render_buf` `o` | heap builder, strands | NO (as S10) | YES |
| S13 `pcrec_minimize_dfa` (8 tables, 25 `free`, 3 free-then-nomem exits) | hand frees | YES (child arena per call, plus a nested scope per refinement pass for `keyseen`, else its per-pass table is retained n times) | YES (HEAP entries; `keyseen` released early, as today) |
| S14 `pcrec_clskit_emit_kit` private arena | unregistered arena | YES | YES (ARENA entry) |
| S15 `pcrec_scanedge_dfa` (10 tables, 37 `free`) | hand frees | YES | YES (HEAP entries) |
| **deleted in the first build** | | **4** (S11, S13, S14, S15) | **6** (S10-S15) |
| **at the deciding sites S4/S7, capability** | | **0 / 0** | **33 lines / 0** |

(B) deletes more at every site, and at S4 it is the only shape that can delete anything. (A) also leaves K155's
three-rewrite remainder half open (S10, S12) and keeps 2 of 5 `ALLOW` rows and 1 of 2 `known_stranded` rows. So the
mechanism is (B), with arenas as ONE entry kind. Non-memory kinds (FILE*, end actions) are NOT added: GENFORM-9's
second non-memory member has not appeared (GENFORM-2's FILE* was fixed by reordering; S22 is classified in D-3).

THE SHAPE. A scope is NOT an arena; it is a mark in an arena's registry (S8 stays AS-IS: a scope StrBuf is plain
heap storage, `.ar` NULL). The handle is explicit: only client code that opens a scope sees it; the 462 allocation
calls (S24) keep their meaning; there is no implicit "current arena". Records live on the heap (malloc), so the arena
blocks, and so the arena high-water mark, are byte-identical to today (G2a).

### D-2 The LIFO discipline (S1, S13, S21, S23)

Rules, each with its check in "Discipline and checks":
- L1 Scopes on one arena close innermost first. A close that is not the innermost is an internal error.
- L2 Every scope opened by a function is closed by that function on every RETURN path; a longjmp is not a return
  and needs no close (release happens in the teardown). On a successful attempt, no scope is open at the end.
- L3 Allocating into an OUTER level while a scope is open is LEGAL and needs nothing: the scope owns only its own
  entries; the attempt arena's blocks are not entries. So `minimize.c`'s results (`ns[c].up`, `ns[c].tr`, allocated
  from `&cx->arena` while its tables are live) are unchanged. This is why a scope cannot be a mark/release on the
  attempt arena's own block chain: that would free the results.
- L4 A scope-owned object never escapes its scope: it is never stored in a Ctx, Job, AST or other longer-lived field.
  The only way out is ADOPTION (D-6), which moves the storage to a longer-lived owner. Scopes are not available to
  src/parse/ at all, so no AST payload can capture one: D70's revisit trigger is NOT met (S23).
- L5 A child arena (ARENA entry) is allocation-only: no scope opens on it. One level of nesting per arena keeps the
  release order a single list.

### D-3 What `job_cleanup`'s list becomes (S4, S22, P4)

KEPT AS IS in this build. Reasons, each a site fact:
- R-3 forbids ADDING a member for these clients, and the design adds none (the clients' resources are scope entries).
- Converting the 33 lines (P4) RELOCATES them to 33 registrations at the allocation sites (nfa.c, dfa.c, the
  revend swap, LANDWALK's machine); it deletes the rule "a new allocation belongs here or it leaks on abort" but adds
  33 calls, and no stranding exists to fix: the two recovery points that own a Job (`compile_driver`,
  `pcrec_count_groups`) already reach `job_cleanup`.
- The `lmnfa`/`lmdfa` lines are roadmap H-FLAGS's, with [LANDWALK] STATE:started: this build touches no line of the
  list, so there is NO overlap with [LANDWALK]. P4 keeps its trigger (the next Job heap array or end action a
  CLIENT of this feature would add); when it fires, the entry is keyed on the Job FIELD (the revend swap), and the
  `lmnfa`/`lmdfa` lines move only with H-FLAGS naming their owner.
- S22's two end actions: CLASSIFIED as NOT GENFORM-9 resource entries. They release nothing; they fold the attempt's
  record into the compile's unions before the Job dies. They stay `job_cleanup`'s first two lines, so the D77 gate for
  non-memory entries is not met (U6 waits).

### D-4 Lifetimes and the longjmp (S6, S21, D109)

- Release is inside `pcrec_arena_free`: the registry (top level, newest first; then base) is released before the
  blocks, exactly where `Arena.owned` is released today. All five src handlers and the six test-tier recovery points
  end in `pcrec_arena_free` on their Ctx's arena (`git grep -n -E 'setjmp\(|pcrec_arena_free' -- src tests` at T),
  so RM-2 is NOT needed (register row 20 keeps its re-based trigger). Memset-only Ctxs hold: a zeroed Arena is an
  empty registry.
- The ONE arrival that resumes the attempt instead of tearing it down is `compile_driver`'s `FIT_FORCE_NEXT` row
  (`goto facts_force`, after a forced fact ask failed). Every arrival therefore first unwinds the attempt arena's
  scopes to the base level, one unconditional call at the top of the handler, before `fit_walk`. It reads nothing the
  handler later reads: by L4 no Ctx or Job field points into a scope, so `fit_labels`, the `sets` carries and
  `job->fit.chosen` are untouched.
- The 6 mid-compile retries: each calls `job_cleanup`, hence `pcrec_arena_free`, and the next attempt's `memset`
  starts an empty registry (D109's shape).
- The memo (S7): not a scope client; its arena has no scopes (no client allocates from it), so nothing changes.
- The nested compile (S21, K163): its inner Ctx has its own registry and its own recovery point; the class fix
  (Clients, unit F4) makes the inner compile write nothing through the outer arena, so an inner failure lands at the
  INNER point and the inner teardown runs.
- D109's Revisit: its premise ("four handlers read no per-attempt Ctx field") still holds in its own terms: the
  registry is inside `cx.arena`, which those handlers already read through `pcrec_arena_free`; no new field is read
  by any handler. The design adds a one-line D109 addendum saying so (manager's file; listed in Open questions).

### D-5 COST-1 (S19, S20)

NOT solved here; it stays [ARENA-REGROW]'s (the arch note's plan-row update), trigger unchanged (U7: an S19 member
measured super-linear, or a retained-garbage share of peak above noise). What this design adds to that row's options:
a builder grown in a loop can be a scope StrBuf (heap, freed at close, no retention) without any new mechanism, so a
site that the trigger names has a fix that is one call. The kit's `kb_reserve` retention is not stated to the kit:
the trigger has not fired (D157: facts only when there is one to send).

### D-6 Adoption (S10, S12, RM-1)

A HAND-OFF, heap to heap: `pcrec_sb_adopt(dst, src)` moves `src`'s storage into `dst`, frees `dst`'s old storage,
leaves `src` empty (`p` NULL), so the scope's later release frees nothing. Both sides are heap in every client (the
Job's `csb`/`hsb` and a scope StrBuf), so no copy and no peak change. The by-`.ar` widening r96 named is NOT built: it
has no caller under shape (B). The primitive REFUSES (internal-error `pcrec_ctx_fail`, or `abort` on a detached
buffer) a source or destination with `.ar` set; that refusal row is the check.

| src storage | dst storage | action |
|---|---|---|
| heap (incl. a scope StrBuf) | heap | move storage; free dst's old; src emptied |
| arena (`.ar` set) | any | refuse: internal error |
| any | arena (`.ar` set) | refuse: internal error |

(Three rows, one accepting; in code it is one guard before the move, not a chain.)

### D-7 Registration home (S5, row 20, row 6a)

On the Ctx's attempt arena (`Ctx.arena`): the registry is fields of `Arena`, written only by arena.c, read only by
arena.c (row 6a's corollary: one writer unit, named readers). Not a new Ctx field, not on the Job. The plan row's
"registered on the Ctx" is met through the Ctx's own arena. D109's memset gives "empty at every attempt" by
construction. A detached arena (cx NULL) may hold scopes too (the clskit test driver calls the kit with no Ctx); its
checks abort, the same rule `pcrec_arena_alloc` already applies to a detached arena.

### D-8 The client set (S10-S15, S25)

First build: S10, S11, S12 (STRBUF), S13 (HEAP), S14 (ARENA), S15 (HEAP, taken by choice: P3's trigger has not
fired, but it is the same call shape as S13 and deletes 37 `free` calls and an `ALLOW` row; a separable last unit
the manager may drop). NOT taken: S25 (`scr_test`/`scr_desc` are Job fields freed by `job_cleanup`: already safe on
every arrival); U1 (no measured peak need, D77); S16 (CALLER-OWNS, needs nothing).

### D-9 Tests and gates

In "Tests and sabotage". The open R-1 wording (a favourable refusal move) does not arise: G2 keeps peak unchanged.
LEAK-ATTRIBUTION (REQ-OPEN) is the fail-fast census's first item.

### D-10 The Arena comment (S2)

internal.h's sentence becomes, after RM-1 corrects the false clause: "Three kinds. A Ctx's own (`cx` set; freed by
its teardown). A scope's child (`child` set; freed by its scope's close, or with its parent on a refusal; holds no
scope). Detached (`cx` NULL; freed by its owner; a failure aborts). `base` and `top` are the registry
(`pcrec_scope_open`)."

### D-11 The `mf_arena` pin (S17)

pcrec's side states: "the art's `mf_arena` is the attempt's arena, never a scope's child arena". Check: the kit's
allocation callback `pcrec_memfn_arena_alloc` (memfn_sites.c) refuses an arena with `child` set (internal error).
A sabotage row hands it a child arena. No memfn.h change (any wording is a kit request, PLAN, not this build).

### D-12 src/core/CLAUDE.md's cross-attempt rule

Unchanged: the design adds no compile-level lifetime, so "Cross-attempt state is plain `Ctx` fields, not arena text"
keeps the note's reading (the retry decision state) without a wording change.

## API

All in `src/core/internal.h` (declarations) and `src/core/arena.c` (definitions); module-internal; no public header,
no spec change (nothing a caller observes moves; D80 has no hunk to write).

```c
typedef struct LEnt LEnt;                 /* an entry record: heap, arena.c's own */
typedef struct {
    ABlock *head; Ctx *cx;
    AOwn   *owned;      /* BASE level: attempt-lifetime heap blocks (K155, kept) */
    LEnt   *top;        /* scope level: newest entry first */
    LEnt   *spare;      /* released records, reused */
    unsigned depth;     /* open scopes */
    bool    child;      /* a scope's child arena: allocation only (L5) */
} Arena;                /* every field's zero is valid: the 33 hand writers need no change */

typedef struct { Arena *a; LEnt *mark; unsigned depth; } Scope;   /* the client's mark, by value */

Scope   pcrec_scope_open(Arena *a);              /* refuses on a child arena (L5) */
void    pcrec_scope_close(Scope *s);             /* releases newest-first to the mark; L1 check */
void   *pcrec_scope_malloc(Scope *s, size_t n);  /* HEAP entry */
void   *pcrec_scope_calloc(Scope *s, size_t n, size_t sz);
void    pcrec_scope_free(Scope *s, void *p);     /* early release of one HEAP entry (keyseen) */
StrBuf *pcrec_scope_sb(Scope *s);                /* STRBUF entry: heap storage, .cx = a->cx */
Arena  *pcrec_scope_arena(Scope *s);             /* ARENA entry: child, .cx = a->cx */
void    pcrec_scope_unwind(Arena *a);            /* release every scope (handler top, D-4) */
void    pcrec_scope_check_closed(Arena *a);      /* L2 at a successful attempt's end */
void  **pcrec_arena_hold(Arena *a);              /* BASE entry, linked at birth (refactor R2) */
void    pcrec_sb_adopt(StrBuf *dst, StrBuf *src);/* sb.c, D-6 (refactor R1) */
```

THE ORDER INSIDE EVERY REGISTERING CALL, so no refusal falls between a resource's birth and its owner (the K155
two-step made one call): (1) take a record (spare, else malloc; a failure diagnoses through `a->cx`, nothing yet
to lose); (2) link it, holding NULL; (3) make the resource (malloc / the StrBuf's first growth / the child's first
block; a failure diagnoses, and the record releases NULL); (4) store it in the record. A StrBuf or child Arena lives
INSIDE its record, so a `realloc` in `sb_grow` updates the field the release reads: the entry is keyed on the field,
never on a pointer value.

THE KIND TABLE (arena.c, `static const`; the release walk indexes it, no switch):

| kind | record holds | release | may refuse? | members (first build) |
|---|---|---|---|---|
| HEAP | `void *p` | `free(p)` | no | S13 minimize (8), S15 scanedge (10) |
| STRBUF | `StrBuf sb` (heap storage) | `pcrec_sb_free(&sb)` | no | S10 `nb`, S11 `tail`, S12 `o` |
| ARENA | `Arena ar` (`child` set) | `pcrec_arena_free(&ar)` | no | S14 clskit |

A row's release function never allocates and never refuses (it runs inside a teardown); a new row is a design
change, reviewed, never a local addition.

`pcrec_arena_free(a)`: release `top` newest-first (each record to `spare`), then `owned`, then free `spare`, then the
blocks; reset every field but `cx` and `child`.

CLIENT SHAPE (render_buf, for illustration; the build writes the real text):
```c
Scope sc = pcrec_scope_open(&cx->arena);
StrBuf *o = pcrec_scope_sb(&sc);          /* freed at close, or by the teardown on a refusal */
... pcrec_sb_printf(o, ...); pcrec_ctx_fail(...) may longjmp here ...
pcrec_sb_adopt(sb, o);                    /* sb takes o's storage; o left empty */
sb->layout_bytes = 0;                     /* records stay at the site (RM-1) */
pcrec_scope_close(&sc);
```

## Discipline and checks

Every rule has a check that runs in `make test`; none is a comment.

| rule | violation | check | where | witness / control |
|---|---|---|---|---|
| L1 innermost first | close of a non-innermost scope, double close | `s->depth != a->depth` -> internal-error refusal (abort if detached) | `pcrec_scope_close` | sabotage row swapping two closes: the corpus compile refuses |
| L2 closed on return | a scope left open on a successful attempt | `pcrec_scope_check_closed(&cx.arena)` before the success `job_cleanup` -> internal error | `compile_driver` success path | sabotage row deleting one client's close |
| L2 static | an open with no close in the same function | scanner: every `pcrec_scope_open` has a `pcrec_scope_close` in the same function | scratch_builder_check.py | self-test fixture (planted unpaired open) |
| L4 no escape | a scope object stored in a longer-lived field, read after close | ASan heap-use-after-free; scanner: `pcrec_scope_*` results assigned only to locals; no `pcrec_scope_` under src/parse/ | `make asan`; scanner | scanner fixture; ASan is the runtime control on the source rule |
| L5 child allocation-only | `pcrec_scope_open` on a child arena | `a->child` -> internal error | `pcrec_scope_open` | sabotage row |
| D-11 pin | the kit's `mf_arena` backed by a child arena | `child` -> internal error | `pcrec_memfn_arena_alloc` | sabotage row |
| D-6 adoption | arena storage handed to `free` | `.ar` set on either side -> internal error | `pcrec_sb_adopt` | sabotage row setting `.ar` on a scope StrBuf |
| K163 class | allocation through a Ctx's error channel while a nested compile runs on another Ctx | `Ctx.lent`: `walk_part` sets it around `part_compile`; `pcrec_arena_alloc` and `sb_grow` count a use on a lent Ctx (no longjmp there); `walk_part` refuses (internal error, at the OUTER point, inner already torn down) if the count is nonzero | arena.c, sb.c, compound.c | control: on today's tree it fires on every compound part with kit forms (the `into` copy); after F4, 0 |

THE FIVE `setjmp` HANDLERS (S6) meet a scope like this:

| handler (file) | teardown at T | releases scopes through | scope clients reachable | witness |
|---|---|---|---|---|
| `compile_driver` (compile.c) | handler-top unwind (new), then the `fit_rungs` row: `job_cleanup` (+ memo free) on refuse/propagate/retry rows; resume on `FIT_FORCE_NEXT` | the unwind, then `pcrec_arena_free` in `job_cleanup` | all six clients | alloc_check W1-W7; growth LSan shards |
| `pcrec_count_groups` (compile.c) | `job_cleanup` | `pcrec_arena_free` | none (parse only) | none needed; the scanner rule keeps scopes out of src/parse |
| `built_status_probe` (src/dump/syntax_dump.c) | `pcrec_arena_free(&cx.arena)` | the same call | none (parse-tier doorways) | as above |
| `pcrec_probe_ask` (syntax_dump.c) | `pcrec_arena_free(&cx.arena)` | the same call | none | as above |
| `pcrec_syntax_explain` (syntax_dump.c) | 2 `pcrec_sb_free` + `pcrec_arena_free` | the same call | none | as above |

The test tier's six recovery points (definitions_check.c x3, definitions_oracle_gen.c, branch_count_check.c,
cwmax_check.c) each end in `pcrec_arena_free(&cx.arena)` at T, so they release too.

## Clients and migration order

Every unit is answer-identical (G1) and separately landable; each names its gate. Order: the census, then the
refactors, then the core with its first client, then one client family per unit.

| unit | what | gate (beyond `make strict`, `make test`, `m6read_check_sab_anchors.py`) |
|---|---|---|
| C0 fail-fast census (no code commit; about an hour, after 01:00) | (a) LEAK-ATTRIBUTION: the 13 growth leak cells re-run under ASan with `fast_unwind_on_malloc=0`, each leak's allocating function named; (b) peak base: massif on R-3's three families and the k155fix2 witnesses, arena high-water on the corpus; (c) reach: `alloc_check --sites` over W1-W6, naming which client files each witness reaches; pick a witness for any client unreached (clskit is the likely one); (d) K163: a scratch-build counter of lent-channel uses over the compound corpus (expect exactly the `into` copy); (e) whether any scope client is reachable from `pcrec_facts_force_all` (decides whether the handler-top unwind's sabotage row has a witness, or is listed UNREACHED) | STOP and reassess if a leak is outside S10-S15 (the client set is wrong), or (d) finds a second site (K163's class is wider; D203) |
| R1 (= RM-1) | `pcrec_sb_adopt`, heap-only; the two transplants call it; S2's sentence corrected | byte identity; S1897, S1899, S1111-S1127 (reach the swaps); S256/S257 anchors |
| R2 | `pcrec_arena_hold` (a base entry linked at birth, holding NULL) replaces `pcrec_arena_own_slot` + `pcrec_arena_own`; `walk_part`'s part text uses it; coding.md 1.6 and src/core/CLAUDE.md follow | byte identity; compound corpus; alloc_check W6 nothing stranded |
| T1 (test only) | W7: in the `alloc_inject.h` build only, `pcrec_arena_alloc` consults the injector, so a failure can land on an allocation that takes no new block (the product build has no hook) | W7 over W1-W6's patterns: every trial diagnosed; the one known stranding (`target_headers_render`) still shown, proving W7 reaches (control) |
| F1 | the registry: Arena fields, kind table, scope API, release in `pcrec_arena_free`, handler-top unwind, success-path closed check; FIRST CLIENT S13 minimize (HEAP; `keyseen` by early release) | byte identity; arena high-water identical; massif on a DFA family within G2b; alloc_check W1-W7 with minimize's `known_stranded` row deleted; scanner minimize `ALLOW` row deleted; sabotage L1/L2/L5 rows |
| F2 | S14 clskit (ARENA); `pcrec_clskit_emit_kit` takes the parent `Arena *` explicitly (src callers pass `&cx->arena`, the test driver its own detached arena); D-11 check | byte identity; clskit suite; the C0-chosen clskit witness under W7; `ALLOW` row deleted; D-11 sabotage row |
| F3 | S10, S11, S12 (STRBUF + `pcrec_sb_adopt`) | byte identity; massif on R-3's families within G2b (R-3's own gate); the 13 growth LSan shards green (cloud run); alloc_check's `target_headers_render` row deleted, with its stack recording and `fn` column removed (they become unreached, learnings §3) and S3584/S3572 re-aimed or retired; 3 `ALLOW` rows deleted; K155's remainder closed |
| F4 (K163, a bug, D203) | `PcrecPartFacts.into` (an outer `Arena *`) is replaced by a hold the outer reserves with `pcrec_arena_hold` before `part_compile`; the inner compile stores a heap copy into it (its own error channel); the `Ctx.lent` check | compound corpus answers identical; the lent check reads 0 (and fired on the pre-F4 tree: the control); W7 failing the inner copy: diagnosed at the INNER point, nothing stranded; K163 closed |
| F5 (optional) | S15 scanedge (HEAP) | as F1, scanedge's `ALLOW` row deleted |

F4 may land before F1 (it needs only R2 and T1); it is placed after F3 so the build lane carries one mechanism at a
time. ASan/LSan on the growth leak shards runs at F3 (it closes the leaks) and once at the end over the whole set.

## Tests and sabotage

- alloc_check: the property (every failed trial diagnosed, nothing stranded) unchanged; populations are floors
  (D110). New: W7 (T1); both `known_stranded` rows deleted (F1, F3); its `target_headers_render` stack recording and
  `fn` column deleted with their row (F3).
- Growth sweep, library stage under LSan: the 13 shards green (F3); the memory-cap rung cells: 0 refusal moves (R-1).
- Scanner: the 5 [ARENA-SCOPES] `ALLOW` rows deleted as their clients move (U5); new rules L2-static and L4 with
  self-test fixtures (a planted unpaired open; a `pcrec_scope_` call under src/parse/; a scope result stored in a
  field), so each rule can FAIL.
- Sabotage rows (`tests/mech/sabotages/`), one per release path and per check: (1) drop the registry walk from
  `pcrec_arena_free` (alloc_check strands; LSan red); (2) drop the release in `pcrec_scope_close` (LSan red on the
  normal path, `make asan`); (3) drop the handler-top unwind (witness from C0(e), else listed UNREACHED); (4) swap two
  closes (L1); (5) delete a close (L2); (6) open on a child (L5); (7) child arena to the kit (D-11); (8) `.ar` into
  `pcrec_sb_adopt`; (9) reintroduce the outer-arena copy (the lent check). Each row's witness is run with
  `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` before delivery ([MECH-REACH]).
- The dump-tier handlers get no scope sabotage row: no client runs under them, and the scanner's src/parse rule is
  what keeps it so (C-6b's gap is unchanged, and is register row 20's).

## Cost and measurement

BUILD COST (estimate). Code: about 200-250 lines in arena.c/internal.h (registry, kind table, scope API), about 15 in
sb.c (adopt), about 10 in compile.c (unwind, closed check), about 25 in compound.c/compile.c (F4), and net-negative
client edits (minimize.c and scanedge.c lose 62 `free` calls; the transplants and heap builders shrink). Tests: W7
(about 40 lines), scanner rules (about 60), 9 sabotage rows. Lanes: one opus build lane for C0 + R1 + R2 + T1 + F1
(the core is engine-adjacent), one sonnet lane per client unit (F2, F3, F5) and one for F4, or one opus lane for all if
the manager prefers fewer hand-offs. Validation: one `make test` per unit (about 40 minutes each, 8 units), one cloud
growth LSan run (F3), one `make asan` at the end, mech REACH runs per unit. Calendar: about two working days of lane
time plus the queue.

RUN-TIME COST. Compile time: one load and branch per arena allocation (the lent check), one record malloc per scope
entry (reused through `spare`), and the release walk. Estimate well under G5's +1%; measured at F1 and F4 by
instruction count on the corpus. Emitted code: none (G1). Memory: arena bytes 0; heap +1 record per live entry
(a record holds at most a StrBuf, about 200 bytes), bounded by the maximum number of live entries (about 10, in
scanedge), so under 4 KB at peak (G2b).

NUMBERS CITED, not re-run: r96 COST-1 (n=400: 8,272 KB -> 27,816 KB; the regression k155fix2 fixed); journal 15:19's
23-site census ("no other super-linear site"); r96's retention per converted site, RSS 0.98-1.02 (the G2b band this
design must stay inside). No probe was run by this lane (box hold until 01:00).

## Refactors (answer-identical)

Listed for the pre-go briefing; under D191 addendum 2 they need no go of their own:
- R1 (= RM-1): `pcrec_sb_adopt`, heap-only, at the two storage transplants; S2's false sentence corrected.
- R2: `pcrec_arena_hold` (one call, linked at birth) replaces the two-call `pcrec_arena_own_slot`/`pcrec_arena_own`;
  `walk_part` uses it; coding.md 1.6 and src/core/CLAUDE.md name it.
- F2's signature change: `pcrec_clskit_emit_kit` takes its parent `Arena *` (three src callers, one test driver).
- NOT taken: RM-2 (release is in `pcrec_arena_free`, which every handler reaches); RM-3 (every new Arena field's zero
  is valid, so the 33 hand writers need no change; P6 keeps its trigger: a field whose zero is not valid); P5
  (truncations); P4 (D-3).

## Open questions

- None for the owner. The mechanism was his to delegate and is chosen in D-1; peak is held unchanged, so R-1's
  favourable-move wording does not arise.
- For the manager (its files, not this lane's): (a) a one-line D109 addendum (D-4: the registry is read through
  `pcrec_arena_free`, which the four handlers already call); (b) register row 20 keeps its re-based trigger, since
  RM-2 is not taken; (c) whether F5 (scanedge, P3's trigger not fired) is in the build or stays P3; (d) the arch
  note's DOC drifts still stand (stale "one setjmp" comments, C-6c).

## STATE AT HANDOFF

Lane arenadesign, 2026-11-24. Tree T = 79a7ca279; no code drift from the arch note's tree. Rulings file
`arenadesign_rulings.md`: empty at every re-read, no ruling applied. No probe run (the owner's box hold); every
number above is cited from the records named in "Cost and measurement" or counted by grep at T.
OWED: none
