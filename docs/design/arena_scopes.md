# Scoped lifetimes registered on the Ctx's arena ([ARENA-SCOPES]): design
STATUS: PROPOSED, REVISION 2.1 (lane arenadesign21, 2026-11-25: TEXT fixes only, no new mechanism and no new
measurement), answering review r103 (`docs/dev/reviews/2026-11-24-r103-arenadesign2.md`, every disposition ACCEPTED by
the manager; RULED section). Rev 2 (lane arenadesign2, 2026-11-24) answered review r102
(`docs/dev/reviews/2026-11-24-r102-arenadesign.md`, every disposition ACCEPTED). Rev 1 (lane arenadesign, b8308584a) was
replaced in full, not patched; the "r102 disposition" table says where each finding B1-B32 is answered and the "r103
disposition" table at the end says where each finding C1-C20 is answered. Next: the manager's inline check of rev 2.1
against C1-C20 (no third round), then the owner's build go.
INPUT OF RECORD: the ACCEPTED architecture note `docs/design/arena_scopes_arch.md` (site rows S1-S28, remodels
RM-1..RM-3, questions D-1..D-12, unlocks U1-U9); reviews r100, r101, r102, r103 as RULED; review r96 (GENFORM-2/5/8/9,
COST-1/2); D109, D191 (addenda 1 and 2), D203; known_issues K155 and K163.
TREE: T = 046438a1c (lane/arenadesign, main merged in). `git -C <tree> diff --stat 79a7ca279 T -- src cli lib memfn/src
tests` is empty, so every site fact read by rev 1 and by r102's critics still holds at T. REV 2.1's counts are re-run at
main d4a6c0b74 (which carries lane dpcompact's `uprops_produce` strand and lane upropfix's ALLOW row for it, C20);
the one new site fact since T is that client, `S29` below. Counts a rev 2.1 sentence changes are marked "at d4a6c0b74".
OWNER RULINGS IN FORCE: "arena-scopes-go: yes"; scope-reach, 2026-11-24, verbatim: "yes let design choose. I believe
I said "not proscribed" so that it was a source of inspiration rather than a specific instruction". R-3 (peak memory
binds: +7-12% peak was refused, and a `job_cleanup`-freed field was refused "as a second mechanism"). R-1 (the arena
high-water delta, and no refusal moves at the growth memory-cap rungs).

THE DESIGN IN ONE PARAGRAPH. Each `Arena` keeps one LIFO REGISTRY of entry records. An entry is a lifetime-owned
resource of one of three MEMORY kinds (a heap block, a heap-backed StrBuf, a child arena), declared in one kind table
with its release function. A SCOPE is a MARK record in that registry, stamped with a generation number:
`pcrec_scope_open` pushes it, and `pcrec_scope_close` checks the handle against the innermost open mark and its stamp,
then releases every entry above the mark, newest first. Entries pushed while no scope is open (the attempt-lifetime
HOLDS that replace `Arena.owned`) are the registry's bottom, released by the same walk. `pcrec_arena_free` releases the
whole registry before the blocks, so every teardown that exists today (the five `setjmp` handlers and the test tier's
six recovery points all end in it) releases open scopes on a longjmp with no new call. Records are heap (one `calloc`
per entry, sized by kind, freed at release). Heap temporaries stay heap and are freed when they are freed today, so the
attempt arena's bytes and the peak heap move only by the record bytes, which are bounded and stated per unit. This is
shape (B), r96 GENFORM-8's registry restricted to memory kinds. D-1 re-scores it against the ACCEPTED note's shape (A):
the count ties, and (B) is chosen on FORM: one list for every memory kind, which deletes the second mechanism (r103 C1).

## Goals

Ranked; a higher goal wins a conflict. Each has who benefits and a checkable form.

1. **G1 Emitted bytes do not move** (users; the speed gate's proof). Check: `scripts/emit_sweep.py --ref <base>` reads
   0 movers in every stream at every unit; no `abi` bump in the build.
2. **G2 Peak memory moves only by the stated record bytes** (users with large patterns; R-3 and R-1 bind). Checks, per
   unit, against that unit's predicted move (section "Cost and measurement", table "Predicted memory moves"):
   - (a) attempt-arena BLOCK high-water: no unit raises it on any compile; F1 and F4 may LOWER it by the bytes named,
     and a lowered peak is KEPT and reported (F4 is a D203 bug fix: refusing a favourable move would refuse the fix);
   - (b) per-compile peak live heap (memgate `peak`, below): every compile's delta is within its unit's predicted
     bound; any compile above the bound is a STOP for that unit, named by compile;
   - (c) refusals at the growth memory-cap rungs (memgate `rungs`): `VERDICT IDENTICAL` (R-1), judged on REQUESTED
     bytes (the owner, 2026-11-25, "rung-edge: agree with lean"): `VERDICT LAYOUT`, every move a layout move, also
     passes (D-9).
3. **G3 Nothing strands on a refusal for the client set** (library callers; K155, K163, D203). Checks:
   `tests/core/alloc_check.c`'s property (every failed trial diagnosed, nothing stranded) over every trial, with the
   filed `known_stranded` rows deleted (2 to 0; plus the one row F1 files for the `uprops_produce` strand, deleted at
   F6); its arena-window witness W7 (unit F1, widened at F4) green AND PROVEN TO SEE A STRANDED ARENA (the SEEN gate,
   "Tests and sabotage", C20); no unit claims a strand closed before that gate reads; the growth
   sweep's 13 LSan leak shards (cloud run 45492837175) green; the lent-channel count reads 0 over the corpus after F4.
4. **G4 One home for "what dies when"** (maintainers; architecture goal 1). Checks: the seven hand-kept answers S10-S15
   and S29 (`uprops_produce`, C20) deleted (D-1); scanner `ALLOW` rows net -6 +2 named (D-8, B19, C8), -7 +2 with F5;
   hand `free()` calls in the client functions (the bare-`free(` regex `(^|[^_[:alnum:]])free\(`, which does not count
   `pcrec_scope_free(`/`pcrec_sb_free(`, C17) read 0 in minimize.c and scanedge.c (F5) after their units, with the
   expected count of `pcrec_scope_free(` calls stated by the F1/F5 lane (the early releases kept); the two transplants'
   hand frees to 0; `Arena.owned` deleted (its answer moves into the registry's bottom).
5. **G5 Compile-time cost stays in noise per compile** (users; compile speed is not the product, but must not regress).
   Check: memgate `instr` (user-mode instruction count around each `pcrec_compile`, in-process) before vs after: p95
   per-compile ratio <= 1.01 and max <= 1.02. Both bands are UNMEASURED defaults until T1 measures the instrument's
   noise (two identical runs); any compile over 1.02 is named and is a STOP for its unit.
   MEASURED A/A noise (lane mgfix, 2026-11-26, 4,500 corpus compiles, base against a copy of base): with ASLR ON the
   ratio spans 0.979..1.022 (max |delta| 20,770 instructions; 3 compiles over 1.02), so `instr` runs under ASLR off
   (`setarch -R`), where the same read is max ratio 1.00001 (max |delta| 246, on the multi-million-instruction
   compiles; the 91k refusal compiles agree within 1). The bands are unchanged.

NON-GOALS. COST-1's grow-by-copy retention class (D-5; [ARENA-REGROW]); converting `job_cleanup`'s named list (D-3; P4
keeps its trigger); the memo's compile lifetime (S7; U3/U9 keep RM-2's trigger); non-memory entries (FILE*, end
actions, the trace build's restores; GENFORM-9, U6); moving the 22 scratch builders into scopes (U1); the kit's own
arenas (`fh_arena`, `wd_blk`, `kb`: the kit's lifetimes, D157); any `mf_arena` wording (a kit request, never this build).

### Standing questions (docs/design/CLAUDE.md)
1. Measurement regime: RELEVANT. Peak heap is read by memgate `peak`: an `alloc_inject.h` build whose driver keeps the
   live byte count (`malloc_usable_size`) and its maximum per compile, in-process, glibc on the dev box (Zen 4, gcc
   15.2). It is deterministic: k155fix ran it three times with identical output (md5), 0 B noise. The same driver
   splits arena BLOCK bytes from other heap BY ARENA IDENTITY (its `--wrap` hook on `pcrec_arena_alloc` sees `a`; every
   arena's blocks come from the one `malloc` in arena.c, so the allocating line cannot tell the attempt arena from the
   memo, clskit, detached and F2/F6 child arenas, C14), which is G2a's reading (the ATTEMPT arena's blocks). Compile cost is a
   user-mode instruction count (G5), not wall time, so no timing window is needed (D191 addendum 1's derived
   consequence). valgrind massif is a cross-check only, on the three largest movers of a unit, pinned
   `--peak-inaccuracy=0.0 --heap-admin=0` (its default 1% peak inaccuracy is above every predicted move, r102 B12). A
   different allocator would move the usable-size numbers and could not flip a decision: every bound is stated in
   records, and D-1 is decided on form, not on a number. RSS is not read (glibc trim
   makes it noisy; the spare-list concern of B12 is gone, because rev 2 has no spare list).
2. Independent control: RELEVANT. The source scanner (`tests/core/scratch_builder_check.py`) and the runtime witnesses
   (`alloc_check.c`'s stranded-heap property, LSan on the growth shards, ASan) read different sources, and each is the
   other's control. The runtime checks inside arena.c (L1's stamp, the close post-condition, the lent count) are
   controlled by sabotage rows that make each one fire (section "Tests and sabotage"). Populations nobody counted
   before: arena allocations that take no new block (W7 fails them, inside the windows where they matter);
   error-channel uses through a lent Ctx (counted at one accessor, B4); and recovery points outside src/ (the test
   tier's six; they release through `pcrec_arena_free`, by grep below).
3. What moves when data is regenerated: NOT relevant (no table, measure set or oracle store is read or written).

## Decisions D-1..D-12

### D-1 The mechanism: shape (B), re-scored against the ACCEPTED note's shape (A) (r102 B8, B9)

THE ACCEPTED NOTE'S (A), quoted from its "The general form": "a scope is an arena whose blocks are freed at its exit;
heap blocks join through `Arena.owned` (S3)". Rev 1 scored a narrower (A) with no heap entries. Re-scored here with
the note's (A), given the same two record tricks rev 1 gave (B): a record may hold a StrBuf by value (so `sb_grow`'s
realloc updates the field the release reads), and a record may hold the ADDRESS of a field (a `void **` slot, which
survives the realloc and the by-value swap at compile.c's revend x-set swap, r102 B8). A "special case" is a hand-kept
answer to "what dies when this work ends" (the note's family list):

| site | today's hand answer | (A) child arena per scope, heap through its owned list | (B) registry of kinded records under marks |
|---|---|---|---|
| S4 `job_cleanup` list (27 `free` + 6 `pcrec_sb_free`) | one list a writer must remember | CAN, with a by-address owned slot per field and the Job registered before its fields (`free(cx->job)` precedes `pcrec_arena_free` today) | CAN, with a FIELD row (`void **`), same Job-first order. NOT TAKEN by either (D-3) |
| S7 memo arena, 5 hand frees | 5 calls at 5 returns | NO without one exit for `compile_driver` (RM-2) | NO without RM-2 |
| S10 `nb`, S12 `o` (whole-artifact rewrites) | heap builder, strands (K155) | YES, the StrBuf held in an owned record; no copy | YES, a STRBUF entry; no copy |
| S11 `tail` | heap temporary | YES | YES |
| S13 minimize (8 tables) | hand frees, 3 free-then-nomem exits | YES; `keyseen` is allocated ONCE per call before the refinement loop (minimize.c `pcrec_minimize_dfa`), so no nested scope is needed; it cannot be freed early and stays 4n bytes until close | YES; `keyseen` released early, as today |
| S14 clskit private arena | unregistered arena | YES | YES (ARENA entry) |
| S15 scanedge (10 tables) | hand frees | YES | YES |
| S29 `uprops_produce` `Arena tmp` (src/parse/mod_uprops.c; NEW at main d4a6c0b74, not in the note's S1-S28; r103 C20) | a Ctx-bound local arena freed by hand, a KNOWN strand when `pcrec_ast_class_from_iv` refuses (K155 sibling, an ALLOWed scanner row) | YES (a child arena; it takes the first block it takes today) | YES (ARENA entry, the same kind as S14) |
| S21 nested compile copy (K163) | none (a bug) | the holder of D-4 / F4, same in both | same |
| S22 end actions | ordered lines | n/a (not memory) | n/a (D-3) |
| **deleted in the first build** | | **7** (S10-S15, S29) | **7** (S10-S15, S29) |
| **cost per scope** (CONTEXT only; D-1 does not rest on it) | | 0 to 64 KB, by where the owned record lives: today's `pcrec_arena_own_slot` takes the record from the arena's own blocks, which opens a `max(sz, ABLOCK_MIN)` = 64 KB block (arena.c); an (A) whose records come from `calloc` or from the parent arena takes no child block (about 16 B) | one heap record per entry, 24-232 B usable by kind (API) |

THE COUNT IS A TIE, 7/7 (r102 B9 confirmed; S29 added by r103 C20). THE DECIDING REASON IS THE FORM (r103 C1; r102 B9's
ruling stands: the mechanism stays (B)). (A) brought to the tie needs a KIND on each owned record (heap block, StrBuf,
field slot), a LIFO unlink of the child from its parent, a generation stamp for stale handles, and L6's bounded early
free: that is (B)'s registry under another name, with the scope represented as an Arena instead of a mark. (B) is ONE
list for EVERY memory kind (heap block, StrBuf, child arena, and later a FIELD or RUN row), with one release walk
and one teardown; choosing (A) means keeping that list AND the child-arena machinery beside it, which is a second
mechanism for the same question ("what dies when this work ends"), and the project's rule is one general mechanism, not
two (D75 addendum). (B) deletes the second mechanism: the child arena survives only as ONE entry kind, used by the
clients that already have an arena (S14, S29: each takes its first block today, so no new floor there).

CONTEXT, NOT THE REASON (r103 C1, C2). An earlier revision decided on R-3's peak cost: under (A) every compile that runs
`target_headers_render` opens a child arena whose first record takes a 64 KB block, live across the rewrite. That block
comes from where TODAY'S `pcrec_arena_own_slot` allocates its record (arena.c: the AOwn record is carved from the arena's
own blocks, which opens a `max(sz, ABLOCK_MIN)` block). It is a property of the current allocation site, not of shape
(A): S10-S12 put nothing else in a child (`nb`, `tail`, `o` are heap StrBufs), and an (A) whose owned record comes from the
parent arena or from `calloc` takes no child block (about 16 B), against (B)'s 256 B per rewrite. So (A)'s cost is "0 to
64 KB by where the owned record lives" and is not what decides. The figures are kept as context, re-derived from the
cited TSVs (k155fix's memgate run, `$PCREC_TMPDIR/scratch/k155fix/mg/peak{1,2}of2.tsv`, before-side column) and read over
SUCCESSFUL compiles only: of 7,402 rows, 1,385 are refusals (819 of them at exactly 111,520 B: parse rejects such as
`\A*`, which run no emitter and no scope), leaving 6,017 successful compiles with median peak 821,680 B. A 64 KB block is
+8.0% at that median, above 5% on 3,782 of the 6,017 and above 1% on 5,393 (over all 7,402 rows, the figures a first
reading gave: min 111,520 B, median 736,368 B, +8.9%, 4,994 over 5%, 6,607 over 1%). Premise (the rewrite buffers are live
at the peak): a gdb probe of k155fix's injected binary on 150 sampled successful corpus compiles reached the final peak
inside `pcrec_memfn_stamps_render` on 146 of 150 (r103 C3); the cited k155fix evidence itself did not show it (k155fix
moved the buffers INTO the arena, where retention shows at any later peak). This is a PREDICTION from those numbers, not a
measured (A) build, and nothing in D-1 depends on it. The numbers keep one role: F3's bound (the rewrite adds one STRBUF
record and one MARK to the peak, Predicted memory moves) is measured against the same population.

THE SHAPE. A scope is NOT an arena; it is a mark in an arena's registry (S8 stays AS-IS: a scope StrBuf is plain heap
storage, `.ar` NULL). The handle is explicit: only client code that opens a scope sees it, the 463 `pcrec_arena_alloc(` (at d4a6c0b74)
call lines (S24) keep their meaning, and there is no implicit "current arena". Non-memory kinds (FILE*, end actions)
are NOT added: GENFORM-9's second non-memory member has not appeared (GENFORM-2's FILE* was fixed by reordering; S22 is
classified in D-3; the trace build's restores are an unlock on the plan row, r102 B27).

### D-2 The LIFO discipline (S1, S13, S21, S23; r102 B1, B25)

Rules; each has its check in "Discipline and checks".
- L1 Scopes on one arena close innermost first, and a handle closes once. The check (B1): each mark carries a
  GENERATION STAMP (`Arena.gen`, incremented at every open, never reset within an attempt; `uint64_t`, so it does not
  wrap) and the arena keeps its innermost open mark (`Arena.open`). `pcrec_scope_close(s)` and `pcrec_scope_free(s, p)`
  first require `a->open && a->open == s->mark && a->open->gen == s->gen` (`a->open` tested FIRST: a zero handle with no
  scope open reads `NULL == NULL` and must not dereference, C19 i), reading only the LIVE mark through `a->open`, never
  the handle's possibly freed `s->mark`. The test is ONE shared function, `scope_check(s)`, run by ALL SIX handle-taking
  calls: `pcrec_scope_close`, `pcrec_scope_free` and the four registering calls `pcrec_scope_malloc`, `_calloc`, `_sb`,
  `_arena` (C4: rev 2 ran it in the first two only, so `scope_malloc(&S1)` while S2 was open landed its entry above m2
  and `close(&S2)` freed it while S1's client still used it; a dead handle pushed an unchecked base entry). A failure
  is an internal-error refusal (`abort` on a detached arena). The pointer test alone is not enough: records are freed at release, so `calloc` may hand the next mark the same address (the
  stale-handle drill, below); the stamp tells them apart. `Arena.gen` resets in `pcrec_arena_free`, so stamps are unique PER ATTEMPT only; that is
  enough because no handle can survive an attempt (its frame is below the `setjmp`, and the unwind closes every open
  scope at the handler top, D-4) (C19 v).
- L2 Every scope opened by a function is closed by that function on every RETURN path; a longjmp is not a return and
  needs no close (release happens in the teardown). On a successful attempt, no scope is open at the end.
- L3 Allocating into an OUTER level while a scope is open is LEGAL and needs nothing: the scope owns only its own
  entries, and the attempt arena's blocks are not entries. So minimize's results (`ns[c].up`, `ns[c].tr`, from
  `&cx->arena` while its tables are live) are unchanged. This is why a scope cannot be a mark/release on the attempt
  arena's own block chain: that would free the results.
- L4 A scope-owned object never escapes its scope: it is never stored in a Ctx, Job, AST or other longer-lived field.
  The only way out is ADOPTION (D-6). Scopes are not available to src/parse/ EXCEPT for ONE named client, `uprops_produce`
  (S29, r103 C20), so no AST payload can capture one; D70's revisit trigger is NOT met (S23). THE C20 CHOICE: L4 is
  NARROWED for that one client, by an `ALLOW`-style row in the scanner (the rule becomes "no `pcrec_scope_` under
  src/parse/ except in `mod_uprops.c`'s `uprops_produce`", with the row's reason). Reasons: (1) the object it owns, the
  decoded interval list, is a pure transient: `pcrec_ast_class_from_iv` copies it into the class node, so nothing in the
  AST, Ctx or Job points into the scope, which is the property L4 protects; the ban existed so an AST payload could not
  capture a scope, and this client captures nothing. (2) The alternative, a STREAMING decode that needs no scope, is a new
  algorithm for `pcrec_ucd_find`'s consumer and would need its own peak measurement (D77: no build ahead of a measured
  need), where the registry form is the same call shape as S14 and needs none. (3) Decoding into `cx->arena` instead was
  measured at +29% peak for 4,000 `\p{L}` and refused under R-3 (the upropfix report), so that form stays closed. The
  scope opens on the attempt arena (`&cx->arena`, never a child: L5), is closed on the function's one return path, and
  its ARENA entry is the child arena `pcrec_ucd_find` allocates into.
- L5 No scope opens on a child arena (an ARENA entry). REASON, corrected (B25): rev 1's "keeps the release order a single
  list" is false, because an ARENA entry's release is `pcrec_arena_free`, which already walks the child's own
  registry. The true reason is D77: no client needs a scope inside a child, and the check is one line. TRIGGER to
  lift it: the first client that needs marks inside a bump area (the owner's "special areas" form), or a helper
  reached from both a parent and a child arena that must open a scope (clskit.c `intern_records` is the candidate).
  STATE (r105 SCOPE-5, 2026-11-26): the second half of the trigger has HALF-FIRED: after F2, `intern_records` is reached
  from both a parent arena and clskit's child, but it opens no scope, so L5 stands; REGISTRY-1's trigger is unchanged
  (the force loop reaches only `pf_derive` readers, 0 scope opens after force entry on 3 patterns hitting both clients).
- L6 (B1) `pcrec_scope_free(s, p)` releases one HEAP entry of the INNERMOST scope only: it passes L1's check, then
  searches from `a->top` down to (not including) `s->mark` for a HEAP record holding `p`. MARK records are never matched
  (kind test), and the search cannot pass `s->mark`, so no call can unlink a nested scope's mark or an enclosing scope's
  entry. Not found is an internal error.
- L7 (B7) A hold (`pcrec_arena_hold`, the base level) is refused while a scope is open on that arena (`a->open` set).
  So every hold sits below every open mark, the base is the registry's bottom, and one list with one walk serves both.

THE DRILLS, by hand (r102 "simulate" lesson). AS UNIT TESTS (C19 vi) they run on a detached arena, where a refusal
`abort`s: each refusing step runs in its OWN forked child (fork per refusal) which must die by that abort, and the steps
after a refusal are run in a fresh child that replays the steps before it, so the test continues past refusing steps. Registry written top first; `m1@g1` is a mark record at address m1 with
stamp 1; `a->open` and `a->gen` after each step.

Stale-handle drill (close, reopen at the same depth, close the stale handle). Unit test 4b does not rely on `calloc`
returning the freed address (under `-fsanitize=address` it does not, so 4b would pass with the stamp deleted, C5): it
asserts the reuse precondition, or FORGES the handle with the live mark's address and an old `gen`, so the stamp half is
the only thing that can refuse:

| step | call | registry (top first) | `a->open` | `a->gen` | result |
|---|---|---|---|---|---|
| 1 | `S1 = open(a)` | m1@g1 | m1 | 1 | S1 = {a, m1, 1} |
| 2 | `p = scope_malloc(&S1, 8)` | e(p), m1@g1 | m1 | 1 | |
| 3 | `close(&S1)` | (empty) | NULL | 1 | test: open == m1, m1.gen 1 == 1, pass. Walk frees e(p), then m1; post-condition holds |
| 4 | `S2 = open(a)` | m1@g2 (`calloc` returned the freed address m1) | m1 | 2 | S2 = {a, m1, 2} |
| 5 | `q = scope_malloc(&S2, 8)` | e(q), m1@g2 | m1 | 2 | |
| 6 | `close(&S1)` (stale) | unchanged | m1 | 2 | test: open == m1 (the pointer test PASSES: same address), open->gen 2 != S1.gen 1: REFUSED, internal error. e(q) is not released, so S2 still owns it |
| 6' | the same with no stamp (rev 1's depth test, or a pointer test alone) | | | | would pass and free e(q), which S2 still uses: the r102 B1 use-after-free |

Free-the-mark drill (a nested scope, early frees aimed at the wrong level):

| step | call | registry (top first) | `a->open` | result |
|---|---|---|---|---|
| 1 | `S1 = open(a)`; `p1 = scope_malloc(&S1, 8)` | e(p1), m1@g1 | m1 | |
| 2 | `S2 = open(a)`; `p2 = scope_malloc(&S2, 8)` | e(p2), m2@g2, e(p1), m1@g1 | m2 | m2.prev_open = m1 |
| 3 | `scope_free(&S1, p1)` | unchanged | m2 | test: open m2 != S1.mark m1: REFUSED (S1 is not innermost) |
| 3b | `scope_malloc(&S1, 8)` (a REGISTERING call on the outer handle, C4) | unchanged | m2 | the shared `scope_check`: open m2 != S1.mark m1: REFUSED. Without the check the entry would land above m2 and step 6 would free it while S1's client still used it |
| 3c | `scope_malloc(&Z, 8)` with `Z` a zero handle and no scope open | unchanged | NULL | `a->open` is NULL: REFUSED before any dereference (C19 i) |
| 4 | `scope_free(&S2, p1)` | unchanged | m2 | test passes; search e(p2), reaches m2 (S2's own mark): stops, p1 not found: REFUSED. m2 is never a candidate (MARK kind) |
| 5 | `scope_free(&S2, p2)` | m2@g2, e(p1), m1@g1 | m2 | found below top: unlinked, freed |
| 6 | `close(&S2)` | e(p1), m1@g1 | m1 | test passes; walk frees m2 only; `a->open = m2.prev_open = m1`; post-condition: top == the record below m2 saved at the test (e(p1)), open == m1 |
| 7 | `close(&S1)` | (empty) | NULL | frees e(p1), m1 |

### D-3 What `job_cleanup`'s list becomes (S4, S22, P4; r102 B30)

KEPT AS IS in this build. Reasons, each a site fact:
- R-3 forbids ADDING a member to it for these clients, and the design adds none (the clients' resources are scope
  entries).
- Converting the 33 lines (P4) RELOCATES them to 33 registrations at the allocation sites (nfa.c, dfa.c, the revend
  swap, LANDWALK's machine), each a FIELD row (D-1's S4 row: `void **`, Job registered first). It deletes the rule "a
  new allocation belongs here or it leaks on abort" but adds 33 calls, and no stranding exists to fix: the one recovery
  point that owns a Job (`compile_driver`) reaches `job_cleanup` on every arrival, and `pcrec_count_groups` (which owns
  no Job; it also calls `job_cleanup`) has nothing to strand (B30).
- The `lmnfa`/`lmdfa` lines are roadmap H-FLAGS's, with [LANDWALK] STATE:started: this build touches no line of the
  list, so there is NO overlap with [LANDWALK]. P4 keeps its trigger (the next Job heap array or end action a CLIENT of
  this feature would add).
- S22's two end actions: CLASSIFIED as NOT GENFORM-9 resource entries. They release nothing; they fold the attempt's
  record into the compile's unions before the Job dies. They stay `job_cleanup`'s first two lines (U6 waits).

### D-4 Lifetimes and the longjmp (S6, S21, D109; r102 B3, B5, B6, B24)

- Release is inside `pcrec_arena_free`: the whole registry (newest first, marks and holds alike) is released before
  the blocks, where `Arena.owned` is released today. All five src handlers and the six test-tier recovery points end in
  `pcrec_arena_free` on their Ctx's arena (`git grep -n -E 'setjmp\(|pcrec_arena_free' -- src tests`), so RM-2 is
  NOT needed (register row 20 keeps its re-based trigger). Memset-only Ctxs hold: a zeroed Arena is an empty registry.
- The ONE arrival that resumes the attempt instead of tearing it down is `compile_driver`'s `FIT_FORCE_NEXT` row
  (`goto facts_force`). So every arrival first calls `pcrec_scope_unwind(&cx.arena)` (close every open scope; holds stay,
  by L7 they are below every mark), one unconditional call at the top of the handler, beside the
  `pcrec_cand_eval_reset` already there. It reads nothing the handler later reads: by L4 no Ctx or Job field points
  into a scope, so `fit_labels`, the `sets` carries and `job->fit.chosen` are untouched.
- The 6 mid-compile retries: each calls `job_cleanup`, hence `pcrec_arena_free`, and the next attempt's `memset` starts
  an empty registry (D109's shape).
- The success path (B3): `pcrec_scope_check_closed(&cx.arena)` runs BEFORE the first take (`cx.job->out_c =
  pcrec_sb_take(&cx.job->csb)`), after the part-facts block, so a refusal there strands nothing: `out_c`/`out_h`/`out_ir`
  are still Job StrBufs that `job_cleanup` frees.
- The memo (S7): not a scope client; nothing changes.
- S29 (`uprops_produce`, F6): its scope opens and closes inside the parse, on the attempt arena. A refusal inside
  `pcrec_ast_class_from_iv` longjmps to the handler and `pcrec_arena_free` releases the ARENA entry with the registry:
  the strand closes by the teardown, no new call. `pcrec_count_groups` parses too, so it can reach the client; its
  `job_cleanup` ends in `pcrec_arena_free`, so it releases it (handler table).
- The nested compile (S21, K163): the fix is a HOLDER the OUTER level owns, reserved before the inner compile runs,
  plus a counted, refused class (the lent channel, D-7). F4's order (B6), each step's failure stated:
  1. the outer reserves two holds, `forms = pcrec_arena_hold(&cx->arena)` and `text = pcrec_arena_hold(&cx->arena)`
     (outer channel, not lent yet; a failure diagnoses at the outer point with nothing yet to lose);
  2. `pcrec_ctx_lend(cx)` (no allocation);
  3. `part_compile`. On its success path the inner compile copies the forms string to the HEAP through its OWN channel
     (a failure diagnoses at the INNER point: the inner teardown runs, rc -1) and stores the pointer into `*forms` (a
     store, no allocation). A later inner refusal (a take) leaves the string owned by the outer hold;
  4. `uses = pcrec_ctx_unlend(cx)` (no allocation);
  5. if rc 0, `*text = out.c_src` (a store);
  6. if `uses`, an internal-error refusal at the OUTER point. Both stores are done, so this refusal strands nothing.
  The count never changes an allocation: it is counted, never failed.
- WHAT AN OOM IN THE COPY ANSWERS, before and after (B5): today it lands at the OUTER point (the outer compile refuses
  with "out of memory" and the inner compile strands). After F4 it lands at the INNER point, rc -1, and `a4_parts_dfa`
  DECLINES by design (`w->rc[i] != 0`), so the compile SUCCEEDS with the plain artifact. That is the by-design
  fallback, the same one W6 already pins (982 absorptions single-shot). So F4's gate reads "nothing stranded; the
  failure absorbed by the by-design fallback; W6's exact absorption pin re-pinned in the same unit (D110)".
- U8 WEIGHED (B24). U8 (the enclosing attempt owns the inner compile's teardown) was the K163 entry's other fix shape. It
  is not taken: it keeps the cross-channel allocation and only makes its failure survivable, where the holder removes
  it; and the inner Job, arena and memo live in `compile_driver`'s own frame, which the longjmp destroys, so the outer
  could free them only after a remodel moving that state into storage the outer owns. U8 keeps its trigger (a second
  cross-compile member, or a nested compile that must allocate into the outer). An ALLOW row in the scanner's seam rule
  ("seam types carry no outer channel", r110 C) IS this trigger firing.
- D109's Revisit: its premise ("four handlers read no per-attempt Ctx field") holds in its own terms: the registry is
  inside `cx.arena`, which those handlers already read through `pcrec_arena_free`, and the lent pair is read by arena.c
  only. The design asks for a one-line D109 addendum saying so (manager's file; Open questions).

### D-5 COST-1 (S19, S20; r102 B26)

NOT solved here; it stays [ARENA-REGROW]'s, trigger unchanged (U7: an S19 member measured super-linear, or a
retained-garbage share of peak above noise). What this design adds to that row's options, corrected: for a StrBuf
builder grown in a loop, the fix is one call (a scope StrBuf: heap, freed at close, no retention). For the ARRAY members
of S19 (dfa.c `arena_regrow`, possessify.c `fq_push`) it is not one call: they need a `pcrec_scope_realloc` (a HEAP
entry that grows by `realloc` in place), which is not built here. dfa.c's own rule "scratch is arena-owned so longjmp
cannot leak" (its header, R1 R-3a) is a family member this design does not count: it is the arena's answer to the same
question, and it stays (COST-1's retention is its price, [ARENA-REGROW]'s row). The kit's `kb_reserve` retention is not
stated to the kit: the trigger has not fired (D157).

### D-6 Adoption (S10, S12, RM-1)

A HAND-OFF, heap to heap: `pcrec_sb_adopt(dst, src)` moves `src`'s storage into `dst`, frees `dst`'s old storage, and
leaves `src` empty (`p` NULL), so the scope's later release frees nothing. Both sides are heap in every client (the
Job's `csb`/`hsb` and a scope StrBuf; no `.ar` write on a Job StrBuf, r102 PROBED-AND-HELD), so no copy and no peak
change. The by-`.ar` widening r96 named is NOT built: it has no caller under shape (B). The primitive refuses (an
internal-error refusal, or `abort` on a detached buffer) a source or destination with `.ar` set; that refusal is the
check. Records beyond the storage (`layout_bytes` and the other StrBuf records) stay at the site (RM-1).

| src storage | dst storage | action |
|---|---|---|
| heap (a scope StrBuf included) | heap | move storage; free dst's old; src emptied |
| arena (`.ar` set) | any | refuse: internal error |
| any | arena (`.ar` set) | refuse: internal error |

(Three rows, one accepting; in code, one guard before the move.)

### D-7 Registration home, and the lent channel (S5, row 20, row 6a; r102 B4, B16)

- The registry lives on the Ctx's attempt arena (`Ctx.arena`): fields of `Arena` (`top`, `open`, `gen`, `child`),
  WRITTEN only by arena.c and READ only by arena.c (row 6a's corollary). `child` is set only by `pcrec_scope_arena`
  (B17). The plan row's "registered on the Ctx" is met through the Ctx's own arena; D109's memset gives "empty at every
  attempt". A detached arena (cx NULL) may hold scopes too (the clskit test driver); its checks abort, the rule
  `pcrec_arena_alloc` already applies to a detached arena.
- CORRECTED (B16): rev 1 said "not a new Ctx field". The lent check needs one Ctx field pair, `Ctx.lent` (bool) and
  `Ctx.lent_uses` (unsigned). WRITER: arena.c only, through `pcrec_ctx_lend`, `pcrec_ctx_unlend` and `pcrec_err_chan`.
  READERS: arena.c only, PLUS the test driver's two read-only accessors (r103 C9): `bool pcrec_arena_open_p(const Arena *)`
  (is a scope open) and `bool pcrec_ctx_lent_p(const Ctx *)`, declared in internal.h, named as read only by
  `tests/core/alloc_check.c` (W7's sampling reads both through them; nothing else calls them, which the scanner checks by
  name). `pcrec_ctx_unlend` returns the count; compound.c `walk_part` reads the returned value, never the field. Callers of lend/unlend: compound.c `walk_part` only.
- THE ONE CHANNEL ACCESSOR (B4). `Ctx *pcrec_err_chan(Ctx *cx)` returns `cx` and, when `cx` is lent, counts one use.
  Every refusal or nomem made through an Arena's or a StrBuf's `.cx` in arena.c and sb.c takes its Ctx from it. Today's
  readers, by `git grep -n -E '(sb|a)->cx\b' -- src/core/sb.c src/core/arena.c`: 5 lines at 4 sites, which are
  `pcrec_arena_alloc`'s nomem, `sb_nomem` (reached from `sb_grow`, `pcrec_sb_take` and `render_prefix`), the
  size-term abort in `sb_grow`, and `sb_simd_fail`. The registry's own record allocation (`rec_take`) goes through it
  too. A use that does NOT fail must be counted as well (an arena allocation that fits its head block is exactly how
  K163 hid from W6), so EVERY allocating entry that holds a channel calls the accessor unconditionally (r103 C11: rev 2 counted two, and
  `pcrec_sb_take`'s `strdup` and `pcrec_sb_render_prefix`'s heap `sb_store` read `.cx` only on failure, so a future member
  there would have hidden as K163 did): `pcrec_arena_alloc` at entry, `sb_grow` after its capacity early return (B13: an
  append that fits allocates nothing and is not counted), `pcrec_sb_take` and `pcrec_sb_render_prefix`. A statement of the
  claim: the count sees every allocation made through an Arena or a StrBuf that carries a `.cx`; an allocation by a bare
  `malloc` is outside the class and is what the scanner and alloc_check's own property cover. `pcrec_err_chan(NULL)` is
  LEGAL (a detached arena has no Ctx): it returns NULL and counts nothing (C19 iv). The
  scanner holds it: in arena.c and sb.c, every `pcrec_ctx_nomem(`/`pcrec_ctx_fail(` takes `pcrec_err_chan(` as its Ctx
  argument (fixture: a planted direct `sb->cx`).

### D-8 The client set, and each client's witness (S10-S15, S29, S25; r102 B19, B22; r103 C8, C20)

First build: S10, S11, S12 (STRBUF), S13 (HEAP), S14 (ARENA), S29 (ARENA; r103 C20, a CLIENT in src/parse/ under L4's
narrowing) and S15 (HEAP, by choice: P3's trigger has not fired,
but it is the same call shape as S13; a separable last unit the manager may drop). NOT taken: S25 (`scr_test`/`scr_desc`
are Job fields freed by `job_cleanup`, safe on every arrival); U1 (no measured peak need, D77); S16 (CALLER-OWNS).

| client | unit | dynamic witness that goes red-then-green | if none |
|---|---|---|---|
| S13 minimize | F1 | alloc_check `known_stranded` row "minimize.c tables" (reached in 8 trials, k155fix report) | |
| S10 `nb` | F3 | alloc_check `known_stranded` row `target_headers_render` (20 trials across W1-W4); growth LSan shards | |
| S11 `tail` | F3 | none filed: C0(c) names one if `alloc_check --sites` reaches `splice_mark`'s window | SINGLE-CONTROL (the scanner row only) |
| S12 `o` | F3 | none filed: C0(c) names one if a witness reaches `render_buf` while `o` is live | SINGLE-CONTROL; no sabotage row (r107 D: its heap plant is the scanner rule S3572 holds red; no alloc witness compiles a layout-marked artifact) |
| S14 clskit | F2 | none filed; clskit did not appear in 3 single-compile profiles (r102 B22): C0(c) searches the clskit corpus | SINGLE-CONTROL |
| S14b clskit whole | SCOPE-4 | none filed (the body allocates scratch only; same SINGLE-CONTROL reasoning as S14); S3643 (close deleted) is scored by the L2 runtime check + the scanner; S3644 (body back on the parent) has no strand witness and NO mech suite catches it (r108 A, measured: `make alloc --both` 13 PASS / 0 FAIL on the plant), so it is declared `SAB_EXPECT=UNDETECTED`; its net is `MG_ENC=1 MG_ENG=2 python3 -I tests/core/memgate/memgate.py peak CLEAN PLANT OUT --bound 0` (exit 1 on the plant) | SINGLE-CONTROL |
| S14c clskit whole_bytes | SCOPE-4 (lane scope4fix, r108 B) | none filed (the pricing tables are scratch, the result is one scalar: nothing can escape); S3648 (pricing body on the parent) is declared `SAB_EXPECT=UNDETECTED`, net = the same memgate command as S3644 | SINGLE-CONTROL |
| S15 scanedge | F5 | none (its only refusals today free first) | SINGLE-CONTROL |
| S29 `uprops_produce` | F6 | alloc_check W3 (`\p{L}` under `-e utf8`), SEEN by the stranded-arena gate (Tests and sabotage, "THE SEEN GATE"); the filed `known_stranded` row F1 adds for it is REACHED before F6 deletes it | |

SCANNER ROWS (B19, C8, C20): the `[ARENA-SCOPES] client` rows (`grep -c '"\[ARENA-SCOPES\] client'
tests/core/scratch_builder_check.py` = 6 at d4a6c0b74: minimize, `nb`, `tail`, `o`, clskit, and `uprops_produce`'s)
are deleted as their units land (F1 minimize, F2 clskit, F3 the three, F6 uprops); F5 deletes scanedge's row too. The
registry's own rows are the ones the SCANNER'S RULES flag, which is not every function that builds a payload: the scanner
flags a declarator or a raw allocator, so `pcrec_scope_sb` and `pcrec_scope_arena`, which build their payloads inside a
`calloc`'d record (no declarator, no raw call of their own), match nothing and get NO row (a row for them would FAIL as
stale). The rows named now: arena.c `rec_take` (heap: the entry record's `calloc`) and the HEAP-kind block's `malloc` in
`pcrec_scope_malloc` (`pcrec_scope_calloc` is written through it, `malloc` plus a zeroing, so it needs no row of its
own; if the build writes it with its own `calloc` it adds a third row). NET: -6 +2 (or +3), -7 +2 (or +3) with F5. The
build lane confirms them against the scanner's output at F1; a further row is a design question, not a local addition.
`shape:NAME` has FOUR users (the `nb`, `tail`, `o` rows and clskit's `arena:a`): the feature and its parse are
deleted at the LATER of F2 and F3 (an unreached mechanism, learnings §3).

### D-9 Tests and gates

In "Tests and sabotage". R-1's open wording (a favourable refusal move) is answered by G2: a lowered peak is kept and
reported (F4 can lower the arena high-water); refusals at the memory-cap rungs must read IDENTICAL, and a moved rung is
a STOP, reported to the manager with the move. THE RUNG RULE (the owner, 2026-11-25, "rung-edge: agree with lean"): a
rung is judged on the bytes the compiler REQUESTS, not on the heap's address-space extent. A rung where one side
compiles and the other refuses, on a cell whose requested-byte peak (memgate `peak`'s measure, uncapped) is UNCHANGED,
is a LAYOUT move: recorded as information (the cell, both sides' thresholds, the heap-extent delta), not a STOP. A move
with a requested-byte change, or any other move (a message, an ERR side), still STOPs. memgate `rungs` applies the rule
itself (`LAYOUT` / `MOVE-FAILS` lines; `VERDICT IDENTICAL | LAYOUT | MOVED`), so it is the check's rule, not a note. The
first layout move: `depth/ncaltrep@250` at the 8 MiB rung, F1 (requested peak 7,710,800 on both sides; threshold base
8,380,416, F1 8,392,704; extent delta +12,288). LEAK-ATTRIBUTION (REQ-OPEN) is the census's first item.

### D-10 The Arena comment (S2; r102 B23)

Two steps, because `child` and the registry arrive at F1. R1 writes the interim sentence (the correction alone): "Three
kinds. A Ctx's own (`cx` set, freed by its teardown). Ctx-bound and freed by hand (`DfaMemo.arena`: `.cx` re-pointed
per attempt, freed by `compile_driver`'s hand calls; and two LOCALS: clskit's and `uprops_produce`'s `tmp`). Detached (`cx` NULL, freed by its owner; a
failure aborts)." F2 and F6 replace the two locals with "A scope's child (`child` set, an ARENA entry: freed at its scope's
close, or by its parent's teardown; no scope opens on it)" and F1 adds "`top`/`open`/`gen` are the registry
(`pcrec_scope_open`)". The sentence reads three kinds until F6 lands, then two plus the scope's child.

### D-11 The `mf_arena` pin (S17; r102 B28)

pcrec's side states: "the art's `mf_arena` is the attempt's arena, never a scope's child arena". MOVED (B28): rev 1
placed the check in the shared callback `pcrec_memfn_arena_alloc` (src/gen/memfn_sites.c), whose only binder
(`pcrec_memfn_art`, `ma->u = &cx->arena`) passes the attempt arena by construction, so the check could fire only under
its own sabotage row, and it would block a later scope-child `mf_arena` for the kit's scratch (S27). The pin is held
at the BINDER instead, as a scanner rule: every `mf_arena` binding under src/ (`ma->u =`) is in `pcrec_memfn_art` and
binds `&cx->arena` (fixture: a planted second binder). No memfn.h change; any kit wording is a kit request (PLAN).

### D-12 src/core/CLAUDE.md and coding.md (r102 B20)

The cross-attempt rule ("Cross-attempt state is plain `Ctx` fields, not arena text") is UNCHANGED: the design adds no
compile-level lifetime. The BUILDER rule changes, and its hunks ride the units that change it:
- src/core/CLAUDE.md (F1): "Builders that can be interrupted by `pcrec_ctx_fail` must be arena-backed (...)
  `pcrec_arena_own` for a heap result" becomes "... arena-backed (`pcrec_sb_scratch(&cx->arena)`) or scope-owned
  (`pcrec_scope_sb`, `pcrec_scope_malloc`); a heap result that lives with the attempt goes in `pcrec_arena_hold`".
- docs/dev/guide/coding.md 1.6 (F1, F5): minimize.c and scanedge.c stop being "the named exceptions" (hand-freed heap
  tables); the rule's text names scopes as the form for a temporary heap table, and `pcrec_arena_hold` replaces
  `pcrec_arena_own`.

## API

All in `src/core/internal.h` (declarations) and `src/core/arena.c` (definitions), except `pcrec_sb_adopt` (sb.c).
Module-internal; no public header and no spec change (nothing a caller observes moves; D80 has no hunk to write).

```c
typedef struct LEnt LEnt;     /* an entry record: calloc'd by arena.c at the kind's size, freed at release */
typedef struct {
    ABlock  *head; Ctx *cx;
    LEnt    *top;   /* the registry, newest first; holds (the base) at the bottom */
    LEnt    *open;  /* the innermost open MARK; NULL when no scope is open */
    uint64_t gen;   /* the last scope stamp issued on this arena (L1) */
    bool     child; /* written by pcrec_scope_arena only: a scope's child; no scope opens on it (L5) */
} Arena;            /* every field's zero is valid, so the 33 hand writers need no change (RM-3 declined, below) */

struct LEnt {
    LEnt *next;
    const struct LKind *kind;   /* its row in the kind table */
    _Alignas(max_align_t) unsigned char payload[];   /* the kind's storage */
};
/* MARK payload: { LEnt *prev_open; uint64_t gen; LEnt *below; } */

typedef struct { Arena *a; LEnt *mark; uint64_t gen; } Scope;   /* the client's handle, by value */

Scope   pcrec_scope_open(Arena *a);                   /* refuses on a child arena (L5) */
void    pcrec_scope_close(Scope *s);                  /* L1 test, release to the mark, post-condition */
void   *pcrec_scope_malloc(Scope *s, size_t n);       /* HEAP entry */
void   *pcrec_scope_calloc(Scope *s, size_t n, size_t sz);
void    pcrec_scope_free(Scope *s, void *p);          /* early release of one HEAP entry, innermost scope (L6) */
StrBuf *pcrec_scope_sb(Scope *s);                     /* STRBUF entry: zeroed, .cx = a->cx, grows on first use */
Arena  *pcrec_scope_arena(Scope *s);                  /* ARENA entry: zeroed, .cx = a->cx, child set, no block yet */
void    pcrec_scope_unwind(Arena *a);                 /* close every open scope (handler top, D-4) */
void    pcrec_scope_check_closed(Arena *a);           /* L2 at a successful attempt's end, before the takes */
bool    pcrec_arena_open_p(const Arena *a);           /* READ-ONLY, for alloc_check W7 only (D-7): is a scope open */
bool    pcrec_ctx_lent_p(const Ctx *cx);              /* READ-ONLY, for alloc_check W7 only (D-7): is the Ctx lent */
void  **pcrec_arena_hold(Arena *a);                   /* base HEAP entry holding NULL; refused while a scope is open (L7) */
void    pcrec_sb_adopt(StrBuf *dst, StrBuf *src);     /* sb.c, D-6 (R1) */
Ctx    *pcrec_err_chan(Ctx *cx);                      /* the one error-channel read (D-7) */
void     pcrec_ctx_lend(Ctx *cx);                     /* compound.c walk_part, around part_compile */
unsigned pcrec_ctx_unlend(Ctx *cx);                   /* returns the uses counted while lent */
```

`pcrec_arena_own_slot` and `pcrec_arena_own`, `AOwn` and `Arena.owned` are DELETED at F1 (their one caller,
`walk_part`, moves to `pcrec_arena_hold`). Every registering call and `pcrec_scope_close`/`_free` begin with the one
shared `scope_check(s)` (L1); `pcrec_arena_hold` instead tests L7 (`a->open` set: refused).

`pcrec_scope_open(a)`, in order (C19 iii): (1) refuse on a child arena (L5); (2) take the MARK record through `rec_take`
(a failure diagnoses through `pcrec_err_chan(a->cx)` with nothing yet to lose); (3) fill the payload `{ prev_open =
a->open, gen = ++a->gen, below = a->top }` (`below` read BEFORE the push, so it is the record under the mark); (4) push
it on `a->top`; (5) `a->open = mark`; return `{ a, mark, mark.gen }`. No step after (2) can refuse.

THE ORDER INSIDE A REGISTERING CALL, so no refusal falls between a resource's birth and its owner (B14):
1. take a record: `calloc(1, offsetof(LEnt, payload) + kind->size)`; a failure diagnoses through
   `pcrec_err_chan(a->cx)` with nothing yet to lose;
2. set its kind and push it on `a->top`;
3. HEAP only: `malloc` the block. A failure diagnoses; the record, already linked and holding NULL, is released by the
   teardown (`free(NULL)`). Then (4) store the block in the record.
STRBUF and ARENA entries stop after step 2: their payload is zeroed by the `calloc`, then `.cx` (and `child`) set, and
the buffer or the child's first block is made lazily on first use, exactly as today's `StrBuf o = { .cx = cx }` and
`Arena a = { .cx = c->cx }` (no 64 KB block on clskit's empty path; G1 holds). A StrBuf or child Arena lives INSIDE its
record, so `sb_grow`'s realloc updates the field the release reads. Because every record is a fresh `calloc`, a record
never carries a previous kind's state (r102 B2 cannot arise: there is no reuse list).

THE KIND TABLE (arena.c, `static const`; the release walk indexes it through `kind->release`, no switch). The release
signature is generic now (B29), `void release(void *storage)`, so a later FIELD row (`void **`, U4/P4) or a RUN row (a
restore or end action, U6) fits without a signature change:

| kind | payload | `size` | release(storage) | may refuse? | members (first build) |
|---|---|---|---|---|---|
| MARK | `{ prev_open, gen, below }` | 24 | nothing | no | every scope |
| HEAP | `void *p` | 8 | `free(*(void **)storage)` | no | S13 (8), S15 (10), the holds |
| STRBUF | `StrBuf` | `sizeof(StrBuf)` | `pcrec_sb_free(storage)` | no | S10 `nb`, S11 `tail`, S12 `o` |
| ARENA | `Arena` | `sizeof(Arena)` | `pcrec_arena_free(storage)` | no | S14 clskit |

A release function never allocates and never refuses (it runs inside a teardown); a new row is a design change,
reviewed, never a local addition.

`pcrec_scope_close(s)`: (1) L1's test; (2) save `below = mark.below` (the record under the mark, taken at open) and
`prev = mark.prev_open`; (3) release from `a->top` down to and including the mark, each record's `release` then
`free`; (4) `a->open = prev`; (5) POST-CONDITION (B10): `a->top == below`, compared with the value saved before the walk, else
an internal error. A dropped or short walk leaves `a->top` above `below` and fails (5). (C19 ii, stated plainly: `a->open
== prev` is not a check, since step 4 just assigned it, so it is not in the post-condition; and `below` always equals
`mark->next` at the time of the test, so it is the walk's stop mark and a corrupted link is what disagrees with it.)

`pcrec_arena_free(a)`: release every record from `a->top` (marks, scope entries, holds: one walk), then the blocks;
reset every field but `cx` and `child`.

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
| L1 innermost, once | close of a non-innermost scope; a stale handle (closed, its address reused); a registering call on a non-innermost or dead handle (C4) | `a->open && a->open == s->mark && a->open->gen == s->gen`, else internal error (abort if detached): ONE shared `scope_check`, run by all six handle-taking calls | `pcrec_scope_close`, `_free`, `_malloc`, `_calloc`, `_sb`, `_arena` | sabotage (4) swaps two closes; (4b) closes a FORGED handle (the live mark's address, an old `gen`: no allocator luck needed, C5) and the unit test asserts the reuse precondition when it uses a real reopen; (4c) drops the `gen` compare, detected by (4b), run with `REACH_ONLY=1`; the free-the-mark drill's steps 3b and 3c (a registering call on the outer handle, a zero handle) refuse |
| close releases | a dropped or short release walk | post-condition `a->top == below && a->open == prev` | `pcrec_scope_close` | sabotage (2) drops the walk: the corpus compile refuses (B10) |
| L2 closed on return | a scope left open on a successful attempt | `pcrec_scope_check_closed(&cx.arena)` before the first take | `compile_driver` success path | sabotage (5) deletes one client's close |
| L2 static | an open with no close in the same function | scanner: each `pcrec_scope_open` has a `pcrec_scope_close` in its function | scratch_builder_check.py | fixture: a planted unpaired open |
| L4 no escape | a scope object stored in a longer-lived field | scanner: `pcrec_scope_*` results assigned to locals only; no `pcrec_scope_` under src/parse/ EXCEPT the one allowed row for `uprops_produce` (C20); ASan use-after-free at run time | scanner; `make asan` | fixtures (a field store; a src/parse call in another function, which must FAIL); ASan is the runtime control on the source rule |
| L5 | `pcrec_scope_open` on a child arena | `a->child`, internal error | `pcrec_scope_open` | sabotage (6) |
| L6 | an early free of another scope's entry or a mark | L1's test, then a search bounded by `s->mark` over HEAP records | `pcrec_scope_free` | the free-the-mark drill as a unit test (steps 3 and 4 refuse) |
| L7 | a hold pushed above an open mark | `a->open` set, internal error | `pcrec_arena_hold` | unit test |
| D-11 pin | a second `mf_arena` binder, or one not binding `&cx->arena` | scanner rule keyed on the TYPE `mf_arena` and on `mf_art_begin(` callers, not on the spelling `ma->u =` (the kit's own idiom is an initializer, `mf_arena ar = { &fa, fh_alloc };` in memfn/src/formhash.c; C12) | scratch_builder_check.py | fixtures in BOTH spellings (an assignment binder and an initializer binder) (sabotage (7) is now a fixture) |
| D-6 adoption | arena storage handed to `free` | `.ar` set on either side, internal error | `pcrec_sb_adopt` | sabotage (8) |
| D-7 channel | a refusal through `.cx` that bypasses the accessor; an allocating entry with a channel that does not count | scanner: every `pcrec_ctx_nomem(`/`pcrec_ctx_fail(` in arena.c and sb.c takes `pcrec_err_chan(`; and no arena.c function calls `pcrec_arena_alloc` (it would bypass W7's wrap, C16) | scratch_builder_check.py | fixtures |
| K163 class | an ALLOCATION through a lent Ctx's channel (a refusal-only use is not counted: the static seam rule, r110 C, covers it) | `pcrec_ctx_unlend` count nonzero, internal error at the outer point after both stores | arena.c, sb.c, compound.c | sabotage (9) restores the outer-arena copy: the compound corpus refuses; C0(d) is the pre-fix control |

THE FIVE `setjmp` HANDLERS (S6) meet a scope like this:

| handler (file) | teardown at T | releases scopes through | scope clients reachable | witness |
|---|---|---|---|---|
| `compile_driver` (compile.c) | handler-top unwind (new), then the `fit_rungs` row: `job_cleanup` (+ memo free) on refuse/propagate/retry; resume on `FIT_FORCE_NEXT` | the unwind, then `pcrec_arena_free` in `job_cleanup` | all six clients | alloc_check W1-W7; growth LSan shards |
| `pcrec_count_groups` (compile.c) | `job_cleanup` (no Job; the arena only) | `pcrec_arena_free` | S29 `uprops_produce` only (it parses a `\p`; F6) | W3 under W7 reaches S29 through `compile_driver`; here the release is the same call; the scanner keeps every OTHER src/parse function scope-free |
| `built_status_probe` (src/dump/syntax_dump.c) | `pcrec_arena_free(&cx.arena)` | the same call | none that a scope-opening call reaches, unless its Ctx parses a `\p` (S29), which the same call releases | as above |
| `pcrec_probe_ask` (syntax_dump.c) | `pcrec_arena_free(&cx.arena)` | the same call | as above | as above |
| `pcrec_syntax_explain` (syntax_dump.c) | 2 `pcrec_sb_free` + `pcrec_arena_free` | the same call | as above | as above |

The test tier's six recovery points (definitions_check.c x3, definitions_oracle_gen.c, branch_count_check.c,
cwmax_check.c) each end in `pcrec_arena_free(&cx.arena)`, so they release too. Two drivers run a Ctx with no recovery
point (cpset_model_check.c, varexp_check.c, r102 B32, pre-existing); no scope client is reachable from them.

## Clients and migration order

Every unit is answer-identical (G1) and separately landable. Order: the census, the refactor, the measurement tool, the
core with its first client, then one client family per unit. Each unit has a STOP (D191 addendum 1(b): a result that
differs from the expectation is a reason to reassess, not to push on). The gate column is beyond `make strict`, `make
test`, `python3 scripts/m6read_check_sab_anchors.py` and the emit sweep's 0 movers.

| unit | what | gate | STOP when |
|---|---|---|---|
| C0 fail-fast census (no code commit; about an hour; scratch builds only, under `scripts/watchdog` and `scripts/boxlock run`) | (a) LEAK-ATTRIBUTION: the 13 growth leak cells re-run under ASan with `fast_unwind_on_malloc=0`, each leak's allocating function named. (b) PEAK BASE: memgate `peak` and `rungs` on the base (the k155fix population: full corpus + every non-red growth cell; the PEAK reading over its SUCCESSFUL compiles only, C3), with the peak instant's live builders attributed BY THE METHOD r103 used: a gdb breakpoint-at-final-peak probe on an injected binary, naming the frame of the allocation that sets the compile's final peak (record: 146 of 150 sampled successful corpus compiles peak inside `pcrec_memfn_stamps_render`); it checks F3's premise that S10-S12 are live at the peak (no instrument beyond gdb and the existing driver is needed before T1). (c) REACH: `alloc_check --sites` over W1-W6, naming the client files each witness reaches; a witness for S11, S12 and S14 searched (S14 in the clskit corpus); a client with none is listed SINGLE-CONTROL (D-8). (d) K163: a SCRATCH arena-failure hook on today's tree (not F1's W7, which does not exist yet: a `--wrap` of the exported `pcrec_compile_driver` that keeps a nesting depth, plus a `--wrap` of `pcrec_arena_alloc` that fails allocations while depth is 2 and the arena's Ctx is the outer one) failing arena allocations made through a lent outer Ctx, over the compound corpus: expect strandings at exactly the `into` copy (K163 SUSPECTED becomes CONFIRMED), and count the lent uses (expect the copy alone). (e) whether a scope client is reachable from `pcrec_facts_force_all` (decides whether sabotage (3) has a witness) | none (a census) | a leak outside S10-S15 (the client set is wrong); (b) shows S10-S12 NOT live at the peak (F3's bound is re-based to 0 for that site, reported to the manager; D-1 does not move, it rests on form); (d) finds no stranding at the copy (K163's class read is wrong) or a second lent use site (the class is wider; D203) |
| R1 (= RM-1) | `pcrec_sb_adopt`, heap only; the two transplants call it; D-10's interim sentence | the rows that reach the swaps, by suite arm (C7): S1897 and S1899 (arm `memfntargets`, `target_headers_render`'s swap) hold; the `partlayout` arm (S1111, S1127 are members of that arm, not of `render_buf`'s swap in particular: the lane confirms the arm reaches the swap with `REACH_ONLY=1`); S255/S256 are NOT R1's rows (they anchor arena.c and sb.c's error channel, F1); memgate `peak` 0 movers | any memgate mover (a hand-off must move nothing) |
| T1 (test tooling) | memgate committed under `tests/core/memgate/` (k155fix's scratch `memgate.py` and `peak.c`, made reproducible: `peak`, `rungs`, and a new `instr` mode; arena-block bytes split BY ARENA IDENTITY, the `--wrap` hook on `pcrec_arena_alloc` seeing `a`, C14); opt-in (`make memgate`), never in `make test` | two identical base runs give identical output (the noise read, G5's bands confirmed or re-set) | nonzero noise: G2b/G5 bands are re-derived before F1 |
| F1 | the registry: Arena fields, kind table, scope API, release in `pcrec_arena_free`, handler-top unwind, success-path check; `pcrec_arena_hold` replaces `own_slot`/`own` and `AOwn` (walk_part's part text); `pcrec_err_chan` at the sites (D-7); W7 (scope window AND hand-kept-arena window: THE SEEN GATE) with its link in BOTH places alloc_check is linked, `tests/core/run_alloc_tests.sh` and `tests/resource/run_resource_tests.sh` (the W6/S3580 arm): once the driver defines `__wrap_`/`__real_` a link without `-Wl,--wrap=pcrec_arena_alloc` fails (C16); FIRST CLIENT S13 minimize (`keyseen` by early release); D-12's hunks. ANCHORS AND READERS MOVED AT F1 (C7): the sabotage rows S255 (arena.c) and S256 (sb.c) move to `pcrec_err_chan(`; S3580 (compound.c, the only control on the compound part text, detector W6) anchors on the deleted `pcrec_arena_own` and is RE-AIMED at the hold's store, not retired; readers of the deleted names are rewritten in the same change: internal.h's `AOwn`/`Arena.owned`/`own_slot` comments and the `pcrec_arena_own` comment near the compound declarations, compile.c's `job_cleanup` comment, compound.c's `walk_part` comment, alloc_check.c's W6 comment, and docs/testing.md's W6 paragraph (false at F1 and F3), all found by `git grep -n -E 'pcrec_arena_own|AOwn|owned' -- src tests docs/testing.md` | memgate within F1's predicted moves; arena block high-water not raised; alloc_check W1-W7, minimize's `known_stranded` row deleted and the new `uprops_produce` row filed (SEEN gate); W6's exact pin re-pinned (D110, direction: UP, the records' `calloc`s are malloc trials, C6); scanner: minimize's row deleted, +2 registry rows (-1 +2); sabotage (1), (1b), (2), (4), (4b), (4c), (5), (6); unit tests for both drills (fork per refusal), L7 | any memgate compile above its bound; W7's population over its budget (below); the minimize row not reached before its deletion |
| F2 | S14 clskit (ARENA); `pcrec_clskit_emit_kit` takes its parent `Arena *` (three src callers pass `&cx->arena`, the test driver its own detached arena); D-11's binder rule (type-keyed, both spellings, C12) | clskit suite; W6's pin re-pinned if W6 reaches clskit (D110, UP); C0's clskit witness under W7, or SINGLE-CONTROL named; `ALLOW` row deleted (`shape:NAME` stays: nb/tail/o still use it); D-11 fixtures | the child's first block appears on clskit's empty path (laziness broken) |
| F3 | S10, S11, S12 (STRBUF + `pcrec_sb_adopt`) | memgate within F3's predicted moves (R-3's own gate); the 13 growth LSan shards green (cloud run); `target_headers_render` row deleted with its stack recording and `fn` column (unreached, learnings §3), S3584/S3572 re-aimed or retired; W6's pin re-pinned (D110, UP); 3 `ALLOW` rows and the `shape:NAME` feature deleted; K155's remainder closed | any compile above +1 STRBUF record + 1 MARK at its peak (256 B: sizeof(StrBuf) 192, usable 216, plus MARK 40; the peak sits inside the rewrite on about 97% of compiles, so a stop at 216 B would trip on a correct F3, C13); an LSan shard still red at a client site |
| F4 (K163, a bug, D203) | the lent pair and its check; the two holds in `walk_part`; the inner heap copy through its own channel (D-4's order); `PcrecPartFacts.into` deleted and REPLACED by `PcrecPartFacts.hold` (a `void **`, the address of the outer `forms` hold; WRITER compound.c `walk_part`, set before `part_compile`; READER compile.c, which stores the heap copy into `*hold` where it read `into` before, and keeps today's NULL check as the "no hold, plain compile" case; part compiles pass NULL hooks, so the hold is stored once), C15; W7's lent window | compound corpus answers identical; lent uses 0 over the corpus; sabotage (9) refuses; W6 (a MALLOC failure of the inner copy, not W7's lent window: after F4 the copy is a heap allocation) failing the inner copy: nothing stranded, absorbed by the by-design fallback; W6's exact absorption pin re-pinned in the same unit (D110); W7's lent window holds 0 arena allocations by construction after F4, so it is kept as C0(d)'s pre-fix control and as the population-0 floor of sabotage (9), never as a gate that can pass by emptiness (K35); arena high-water may FALL by F4's named bytes; K163 closed | a nonzero lent count on the fixed tree (a second site: the class is wider) |
| F5 (optional) | S15 scanedge (HEAP) | as F1; scanedge's `ALLOW` row deleted; coding.md 1.6's scanedge sentence; W6's pin re-pinned if moved (D110, UP) | as F1 |
| F6 (C20) | S29 `uprops_produce` (ARENA entry; the scope opens on `&cx->arena`, `pcrec_ucd_find` allocates into the child); L4 narrowed by one scanner row (L4); D-10's sentence | alloc_check W3 (`\p{L}`) green under W7 with the filed `uprops_produce` `known_stranded` row DELETED (it was REACHED at F1: THE SEEN GATE); the scanner's uprops `ALLOW` row deleted and the one L4 row added; memgate within F6's bound: <= + 1 ARENA record (72 B usable) + 1 MARK (40 B) while the decode runs, 0 block bytes (the child takes the block today's `tmp` takes); the +29% `cx->arena` form is NOT taken | a memgate mover above that bound on any compile; W3 not reaching the row at F1 (the gate is blind: back to the manager) |

9 units: C0 plus 8 code units (R1, T1, F1-F4, F6, and F5 optional). F6 lands after F2 (the same ARENA kind) and may ride F2's lane. F4 may land before F1 only if it carries the hold and the accessor itself;
it is placed after F3 so one build lane carries one mechanism at a time. ASan/LSan on the growth leak shards runs at F3
and once at the end.

F4 AS A D203 FIX (B18), the four items:
- CLASS: work running under one recovery point allocates, or refuses, through a handle whose error channel is ANOTHER
  recovery point's Ctx, so a failure skips the running Ctx's teardown (K155's class: a resource live across a refusal
  that nothing frees on the longjmp; here the resource is a whole inner compile).
- HOUSE RULE BROKEN: src/core/CLAUDE.md "error paths longjmp to `cx.jb`", and arena.c's premise ("the longjmp lands in
  compile_driver, which frees this arena wholesale"), both of which assume the arena's Ctx is the running one.
- SIBLINGS, by grep: `git grep -n -E '(->|\.)into\b' -- src cli lib memfn/src` = 3 lines (1 writer, compound.c; 1
  allocating reader, compile.c; the NULL check); one `pcrec_compile_driver(` call made from inside a compile (compound.c
  `part_compile`). The grep cannot see a second site that reaches the outer Ctx through another struct (`meas` hands
  the inner compile outer Job pointers), so the RUNTIME count is the sibling census: C0(d) over the compound corpus,
  and F4's gate over the whole corpus.
- FIX SHAPE at the class: every error-channel read goes through one accessor that counts uses on a lent Ctx, and a
  nested compile runs lent, so the class is a counted population refused at the outer point (this catches any future member that ALLOCATES
  through an Arena or a StrBuf carrying a `.cx`: D-7's counted entries, C11; a bare `malloc` is outside it. A
  refusal-only use longjmps to the outer point before `pcrec_ctx_unlend` reads the count, so it is NOT counted: that half
  is covered by the static seam rule "seam types carry no outer channel", r110 C); the one member found today is removed by the holder. K163 is SUSPECTED: if C0(d) does not strand at the copy,
  that is a STOP, not a pass. F4 is not sized as a plan unit (D203: no 90%, no one-pass); its place in the order is only
  "one mechanism per lane".

R2's REACH (B24). Rev 1's R2 (now inside F1) moves `walk_part`'s PART TEXT from `AOwn` to a hold. The accepted note's
A-ENTRY scope for `walk_part` was "only the facts copy's lifetime"; this design goes beyond it on purpose, because the
hold replaces `Arena.owned` itself (one record type, one walk, B7), and `walk_part` is `owned`'s only caller.

## Tests and sabotage

- alloc_check: the property (every failed trial diagnosed, nothing stranded) unchanged; populations are floors (D110).
  Both `known_stranded` rows deleted (F1, F3); the stack recording and `fn` column deleted with the second (F3); the
  `uprops_produce` row F1 files for the S29 strand is deleted at F6 (it needs the stack recording extended to arena.c's
  block `malloc`, `STACK_FILE`, so its `fn` can name `uprops_produce`; F3's deletion of the recording waits for F6).
- W7 (B11), the arena-window witness, lands at F1 and widens at F4:
  - WHERE THE HOOK LIVES: in the test link only. alloc_check's link adds `-Wl,--wrap=pcrec_arena_alloc`, and the
    driver defines `__wrap_pcrec_arena_alloc`, which either calls `__real_pcrec_arena_alloc` or, on the chosen trial,
    takes the real failure path (`pcrec_ctx_nomem(a->cx)` when `a->cx`, else `abort`). Nothing under `src/`, `cli/` or
    `lib/` is edited for it, so alloc_inject.h's rule holds. GNU ld only; the driver is already glibc-only (it includes
    `<malloc.h>`), so no box loses coverage it has today.
  - SAMPLING: only arena allocations inside a WINDOW are trial points: the arena has an open scope (`a->open`), or its
    Ctx is lent (F4), or a HAND-KEPT arena is live (below). The driver reads the first two through the two read-only
    accessors `pcrec_arena_open_p` and `pcrec_ctx_lent_p` (D-7's reader line names alloc_check.c as their only reader,
    C9). The window is by the ALLOCATING arena's `open`: clskit allocates into its CHILD (L5: no scope open there), so
    W7 sees none of S14's allocations, and C0(c) is told so (S14's witness is the clskit corpus, not W7).
  - COUNTER: W7's own (`arena_n`), separate from the malloc counter. This does NOT keep W1-W6's pins still (C6): every
    registry record is a `calloc`, and alloc_inject.h turns each into a malloc-counter trial, so W6's exact pin (`504,
    982, 0`; its comment says allocation-shape churn on the compound path re-pins it) moves at F1 (minimize under a
    part's DFA), F2, F3, F5 and again at F4; each of those units names W6's re-pin (D110) in its gate, direction UP
    (more malloc trials; the absorption count is read again, never assumed).
  - FLOOR: `min_total` = half the population measured at F1 (D110).
  - BUDGET: W7 adds at most 2,000 trials and 60 s to `test-alloc` (unmeasured defaults; today about 162 malloc trials
    for W4 in about 60 s). A larger population at F1's profiling run is a STOP for F1; the fallback is a stated stride.
    DEVIATION AT BUILD (lane arenabuild2, ruling R-1): F1 measured 2,112 trials; the stride is 4 on scope-window-only
    points, every hand-kept-window point kept (W7/W3: 535 trials at R-1, 528 after F6 removed the uprops hand-kept window; reproduce: `ALLOC_ARGS=--w7-only make alloc` prints W7/W3's population), and the DFA memo arena is excluded from the
    hand-kept window, its premise (compile_driver frees it on every arrival) asserted by alloc_check (sabotage S3603);
    "Deviations at build" below.
  - CONTROLS: sabotage (1) (drop the registry walk from `pcrec_arena_free`) makes W7 strand minimize's tables; C0(d)
    shows the lent window stranding the `into` copy on today's tree. After F4 the lent window's population is 0 by
    construction (C10): it stays as the pre-fix control only, and its floor is 0 for sabotage (9)'s member, so it is
    never counted as a gate that passes.
  - r105 CHECKS-3 (the trade the SEEN gate now carries): after F6 no real compile exercises W7's hand-kept window (9 trial
    points removed, 535 -> 528); the planted control (S3602's w7_plant) is the ONLY net on the hand-kept branch of the
    wrap. The hand-kept window has a single control, and `SAB_REACH_POP` proves a definition exists, not that the control is wired.
  - THE SEEN GATE (r103 NEW, C20): `make test-alloc` is GREEN with the `uprops_produce` strand present, because its W3
    witness is `\p{L}` and a failure of `pcrec_ast_class_from_iv`'s arena allocations takes no malloc (they fit the
    compile arena's open block), while the `tmp` arena's block was taken earlier: alloc_check's malloc-trial counter never
    fails at the one moment the strand needs, so it does not SEE a stranded arena. BEFORE any F-unit claims a strand
    closed, W7 gets a third window: a HAND-KEPT arena is live (Ctx-bound, not its Ctx's own `&cx->arena`, holding a
    block), tracked by the test link through `__wrap_pcrec_arena_alloc` (first block taken) and
    `__wrap_pcrec_arena_free` (released); every arena allocation made while one is live is a trial point, and a trial
    that strands reads code 4 exactly as a malloc trial does. THE GATE, in F1: (i) a unit test in `tests/core/` plants a
    strand (a hand-kept `Arena tmp`, a block, then an arena allocation that W7 fails while it is live) and requires
    alloc_check's property to read it as STRANDED: the control that can fail; (ii) on today's `uprops_produce`, W3 under
    W7 reads the strand (code 4), which F1 files as a `known_stranded` row and REQUIRES REACHED, floor 1 (a stale or
    unreached row fails, learnings §3); (iii) sabotage (10) drops the `__wrap_pcrec_arena_free` bookkeeping and W3's
    row reads UNREACHED (red). No unit deletes a `known_stranded` row or writes "strand closed" before (i)-(iii) read
    green; F6 deletes the row only after F6's own scope makes W3 green.
- Growth sweep, library stage under LSan: the 13 shards green (F3); memgate `rungs`: IDENTICAL or LAYOUT at every unit (R-1, the rung rule in D-9).
- Scanner: the 6 [ARENA-SCOPES] `ALLOW` rows (at d4a6c0b74) deleted as their clients move (U5), 2 registry rows added
  and 1 L4 row for `uprops_produce` (D-8); new rules L2-static, L4, D-7 channel (including "no arena.c function calls
  `pcrec_arena_alloc`"), D-11 binder, each with a self-test fixture so it can FAIL.
- Unit tests (tests/core, a detached arena, no compile; fork per refusal, since refusals `abort` there): the stale-handle
  drill (4b: forged handle plus the real reopen with its reuse precondition asserted), the free-the-mark drill (steps 3,
  3b, 3c, 4), L7, and the SEEN gate's planted strand.
- Sabotage rows (`tests/mech/sabotages/`): (1) drop the registry walk from `pcrec_arena_free` (alloc_check and W7
  strand); (1b) drop the `free` inside the shared per-record release (every path strands; alloc_check red); (2) drop
  the walk in `pcrec_scope_close` (the post-condition refuses the corpus compile, B10); (3) drop the handler-top unwind
  (witness from C0(e), else listed UNREACHED); (4) swap two closes (L1); (5) delete a close (L2); (6) open on a child
  (L5); (8) `.ar` into `pcrec_sb_adopt`; (9) restore the outer-arena copy (the lent check); (4b) drop the `gen` compare
  (unit test 4b detects it; the plant that makes the pointer half pass is the forged handle, so it also runs under `make
  asan`, C5); (10) drop the hand-kept-arena bookkeeping (the SEEN gate). Rev 1's (7) is now the
  D-11 scanner fixture. Each row's witness runs with `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` before
  delivery ([MECH-REACH]).
- The dump-tier handlers get no scope sabotage row: no client opens a scope under them but the one parse client S29
  (which their own `pcrec_arena_free` releases), and the scanner's src/parse rule (with its one allowed row) keeps it so
  (C-6b's gap is unchanged; register row 20's).

## Cost and measurement

BUILD COST (estimate). Code: about 220-260 lines in arena.c/internal.h (registry, kind table, scope API, holds, the
accessor and the lent pair); about 15 in sb.c (adopt) plus the 4 accessor call sites; about 10 in compile.c (unwind,
check); about 30 in compound.c/compile.c (F4); net-negative client edits (minimize.c and scanedge.c lose 62 `free`
calls; the transplants shrink). Tests: memgate committed (about 210 lines from the scratch tool), W7 (about 60), scanner
rules (about 80), unit tests for the drills (about 60), 12 sabotage rows (the 10 plus (4b), (10)). Lanes: one opus lane for C0 + R1 + T1 + F1
(the core is engine-adjacent); one sonnet lane per client unit (F2 with F6, F3, F5) and one for F4, or one opus lane for all if
the manager prefers fewer hand-offs. Validation per code unit: one `make test` (about 40 minutes), one memgate peak +
rungs run (its run time is measured at T1, then stated), mech REACH; one cloud growth LSan run (F3); one `make asan` at
the end. Calendar: about two and a half working days of lane time plus the queue.

RUN-TIME COST. Compile time: per arena allocation one accessor call (a load and a branch on `cx->lent`); per entry one
`calloc` and one `free`, and the release walk. Entries per compile are tens (8 per minimize call, 10 per scanedge
call, 3 rewrites, the holds) against thousands of mallocs today. r102's measurement of the lent check on 2 patterns:
about 0.04-0.05% of instructions; nothing superlinear in a size the user controls. G5 is gated per compile (memgate
`instr`), so a heavy compile cannot hide a light one's regression (B13). Emitted code: none (G1).

PREDICTED MEMORY MOVES (B7), per unit, glibc usable sizes on the dev box (a `calloc` of n bytes has usable size
`max(24, round_up(n + 8, 16) - 8)`; record header 16 B, so a HEAP record is 24 B usable, a MARK 40 B):

| unit | attempt-arena block bytes | per-compile peak live heap (memgate) | source of the number |
|---|---|---|---|
| R1 | 0 | 0 (a hand-off moves storage) | the transplants' own text |
| T1 | 0 | 0 (test only) | |
| F1 | 0 within a block; `AOwn` records (16 B each, one per compound part) leave the arena, so a compound compile's in-block use falls 16 B per part | non-compound: + at most 8 HEAP records (24 B each) + 1 MARK (40 B) live during minimize, i.e. <= +232 B and only if minimize runs at the peak instant; compound: + 1 HEAP record (24 B) per part hold, for the attempt | sizes from the kind table |
| F2 | 0 (clskit's child arena takes the same 64 KB block today's local does) | <= + 1 ARENA record (48 B payload, 72 B usable) + 1 MARK (40 B) while clskit runs | today's clskit local |
| F3 | 0 | <= + 1 STRBUF record (`sizeof(StrBuf)`, about 200 B payload, measured by `sizeof` at F3) + 1 MARK per rewrite, live at the peak instant: about +256 B per compile, constant (216 usable + MARK 40; STOP at 256 B, C13) | r102 PROBED-AND-HELD; sizeof(StrBuf) 192, usable 216 |
| F4 | FALLS by `round16(strlen(forms) + 1)` per DFA part (the copy leaves the outer arena), and by a whole 64 KB block on a compile where that copy opened one | + usable(strlen(forms) + 1) + 2 HEAP records (48 B) per part, for the attempt | `pcrec_sb_fragfv` allocates exactly `n + 1` |
| F5 | 0 | <= + 10 HEAP records + 1 MARK (280 B) during scanedge | |
| F6 | 0 (the child takes the block today's `tmp` takes) | <= + 1 ARENA record (72 B usable) + 1 MARK (40 B) while a `\p` decode runs | today's `uprops_produce` local |

The worst simultaneous live set in the first build is about 10 records (scanedge, r102 PROBED-AND-HELD: nesting depth 1,
no client calls another while its scope is open): 280 B of HEAP records. Records sized by kind make r102's 2.2 KB
bound (10 records at about 224 B) an upper bound only; the largest kind (STRBUF) is live one at a time. Either way the
move is two orders below a 64 KB block, and below 0.05% of the median compile's peak. Each unit's memgate gate is its row
above: "every compile's peak delta is within its unit's bound" (G2b). The k155fix change is NOT a constant (r103 C2): its
before/after delta reads +48 B on 7,211 compiles but +65,608 B on 20 and -4,000 B on 25, among others, and today's tree is
the AFTER side of k155fix: the bounds are measured against today's tree (T1's two base runs), not against a constant.

NUMBERS CITED, not re-run: r96 COST-1 (n=400: 8,272 KB to 27,816 KB; the regression k155fix2 fixed); k155fix's R-3
measurement (+7-12%, +59-175 KB) and its memgate run (7,402 compiles; min/median/p90 peaks above; 0 B noise in three
runs); journal 15:19's 23-site census ("no other super-linear site"); r102's PROBED-AND-HELD peak and cost reads; the
grep counts (B31): `grep -o 'free(' src/opt/minimize.c | wc -l` = 25, the same on scanedge.c = 37 (today's counts of the
raw pattern; G4's targets use the bare-`free(` regex); `job_cleanup`'s
body `free(` = 27 and `pcrec_sb_free` = 6 (awk over `static void job_cleanup` to its closing brace); 6 `[ARENA-SCOPES]
client` scanner rows at d4a6c0b74 (command in D-8; 5 at T); 2 `known_stranded` rows (tests/core/alloc_check.c); `git grep -n
'pcrec_arena_alloc(' -- src cli lib`, minus arena.c and internal.h, = 463 at d4a6c0b74 (462 at T; +1 is
`uprops_produce`'s `pcrec_ucd_find`/`tmp` caller line, C20); 34 Arena writers at d4a6c0b74 (the note's S28 counted 33,
C-2/C-24; the +1 is `Arena tmp = { .cx = cx }` in mod_uprops.c). The hand-`free(` counts: the bare-`free(` regex of G4
(C17); the earlier `grep -o 'free('` also matched `pcrec_scope_free(` and `pcrec_sb_free(` and could not read 0. No probe
was run by this lane: every number above is cited, or counted by grep or `git grep` at d4a6c0b74 where stated.

## Refactors (answer-identical)

Listed for the pre-go briefing; under D191 addendum 2 they need no go of their own:
- R1 (= RM-1): `pcrec_sb_adopt`, heap-only, at the two storage transplants; S2's false sentence corrected (D-10).
- Inside F1: `pcrec_arena_hold` (one call, linked at birth, the registry's bottom) replaces the two-call
  `pcrec_arena_own_slot`/`pcrec_arena_own` and `AOwn`; `walk_part` uses it; coding.md 1.6 and src/core/CLAUDE.md name it.
- Inside F1: `pcrec_err_chan` at the 4 error-channel sites of arena.c and sb.c (answer-identical: it returns its
  argument; the count is read only by F4).
- F2's signature change: `pcrec_clskit_emit_kit` takes its parent `Arena *` (three src callers, one test driver).
- NOT taken: RM-2 (release is in `pcrec_arena_free`, which every handler reaches). RM-3 DECLINED, said plainly (B17):
  the note's trigger was "a scope that is an `Arena` that gains fields"; under (B) a scope is a mark, and the fields
  `Arena` does gain are all zero-valid, so the 33 hand writers stay correct. This RE-WORDS P6's event from the note's
  "a field added to `Arena`" to "an `Arena` field whose zero is not valid"; the re-wording is this design's, listed for
  the manager. P5 (truncations) and P4 (D-3) are not taken.

## Open questions

- For the owner: none. The mechanism was his to delegate and is chosen in D-1 on FORM (one list for every memory kind,
  no second mechanism), with R-3's peak cost kept as context; the count tie is stated, not hidden. R-1's favourable-move wording is answered in D-9 (a lowered peak is kept; refusal
  moves stay a STOP, judged on requested bytes since the owner's rung rule, 2026-11-25: a layout move is recorded).
- For the manager (its files, not this lane's):
  - (a) a one-line D109 addendum (D-4: the registry and the lent pair are read through `pcrec_arena_free` and arena.c,
    which the four handlers already reach);
  - (b) register row 20 keeps its re-based trigger, since RM-2 is not taken;
  - (c) whether F5 (scanedge, P3's trigger not fired) is in the build or stays P3;
  - (d) the arch note's DOC drifts still stand (stale "one setjmp" comments, C-6c);
  - (e) the items r100/r101 sent as PLAN, carried here so they are not dropped (B21): the S27 kit-hook trace (then a
    FACT to the kit, D157); the [ARENA-REGROW] row update (D-5's `pcrec_scope_realloc` option); proposed row P5
    (truncations); the kit wording of D-11 (a kit request, never this build);
  - (f) P6's re-worded event (Refactors) and RM-3's decline;
  - (g) R2's reach beyond A-ENTRY's walk_part scope (Clients, "R2's REACH");
  - (i) r103 C20's choices, for the manager's ruling at the go: L4 narrowed for the one client `uprops_produce` (D-2 L4's
    reasons), S29 as unit F6, and the SEEN gate in F1 (Tests and sabotage); the build go should cite them;
  - (h) r102 B27 is filed as an unlock on [ARENA-SCOPES]'s refs (the trace build's arrival restores as GENFORM-9's
    possible second non-memory member); whether trace-only members count toward GENFORM-9 is the manager's call.

## Deviations at build (F1, lanes arenabuild2 and arenabuild3, the manager's rulings R-1..R-6)

- R-1, W7. The DFA memo arena (S7) is not a hand-kept arena for W7: compile_driver frees it on every arrival, so it
  cannot strand, and its window spans the whole compile (W7/W1 alone read 2,614 trials with it). BINDING: every
  alloc_check child (malloc trials, arena trials, the profiling pass) exits 6, a FAIL naming the memo, if a memo arena
  still holds a block when the compile returns; sabotage S3603 drops the memo free at the nomem arrival. The stride is
  `W7_SCOPE_STRIDE` = 4 on points in the scope window only; every point in the hand-kept window is a trial.
- R-2, memgate. Peak and the arena block columns count REQUESTED bytes (per pointer; block = `sizeof(ABlock) + cap`);
  the `malloc_usable_size` peak is an informational column. Usable size moved with heap history, not with bytes asked.
- R-3, the registry: a MEASURED, REVERTED TRY (lane arenabuild2 built it, lane arenabuild3 reverted it under ruling
  R-5; F1's per-record form above stands). The try: each Arena kept ONE heap array used as a LIFO stack (first growth
  16 records, doubling; popped on close; freed by `pcrec_arena_free`), handles named records by position and stamp,
  and a hold became an `ArenaHold` set through `pcrec_hold_set`. Its aim was the 8 MiB rung on `depth/ncaltrep@250`.
  Measured: it did not move the rung (the smallest RLIMIT_DATA that compiles, 4 KiB grain: base 8,380,416, F1
  8,392,704, R-3 8,392,704); the glibc thread-arena `mprotect` high-water (strace) read base 7,757,824 and both F1 forms
  7,770,112 (+12,288); an oldest-first release (scratch, uncommitted) needed the same 8,392,704; and the array cost
  +512 B of requested peak on 4,464 of 7,402 compiles (66 at +1,024), over F1's bound of 232, where the per-record form
  is within it (max +184). The rung move is heap layout, not requested bytes: under the rung rule (D-9) it is a LAYOUT
  move. Numbers: `docs/dev/lanes/arenabuild2_report.md`.
- R-6, the rung rule (the owner, 2026-11-25, "rung-edge: agree with lean"): rungs are judged on requested bytes; D-9
  states it and memgate `rungs` applies it.
- F2 and F6 BUILT (lane f2f6, 2026-11-26; the Clients rows F2 and F6 above are delivered, validation OWED to the queue,
  `docs/dev/lanes/f2f6_report.md`). F2: `pcrec_clskit_emit_kit(c, parent, fn, k, cp_max)`; the scope opens AFTER the
  empty-set return, so the empty path opens no scope and takes no record; the D-11 rule is `d11_findings` in
  `scratch_builder_check.py` (type-keyed on `mf_arena`, both spellings, `mf_art_begin(` callers; floor: one allowed binder
  seen); sabotage S3613 (close deleted), S3614 (binder spelled through a cast). F6: `uprops_produce` opens its scope on
  `&cx->arena` and `pcrec_ucd_find` allocates into the child; `SCOPE_PARSE_ALLOW` carries the one row; the scanner's
  uprops `ALLOW` row, the filed `uprops_produce` `known_stranded` row and K155's uprops sibling line are deleted; S3602's
  re-aim (its witness was that row) is the planted-strand control alone; sabotage S3615 (close deleted).
- r104 (code review of F1, the manager's ruling 2026-11-25), REGISTRY-1: sabotage (3), dropping the handler-top
  `pcrec_scope_unwind`, is UNREACHED. Its one reason is FIT_FORCE_NEXT, and the only scope client (minimize, a leaf)
  is not reachable from `pcrec_facts_force_all`, so no witness exists (C0(e) answers: none) and no row is built
  (D77). TRIGGER: the first scope client reachable from the force loop; that unit builds the resume-shaped witness
  and the sabotage row.
- r104, CHECKS-6: sabotage S3598 (the "-asan" copy of S3597) is DELETED: the core arm passes no sanitizer flags
  (SAB_REQUIRE=asan only probed the box), so it ran byte-identically to S3597, whose forged-handle drill is the
  allocator-independent witness for (4c).
- r104, CHECKS-4: `scope_check` defines `abort`, so a refusal ends the child with a tagged exit status (77); a glibc
  `free(): invalid pointer` abort no longer reads as a refusal.
- r104, MEMGATE-7: `pcrec_err_chan` is the channel for arena.c and sb.c refusals only (D-7, the scanner's scope); the
  16 `sb->cx` refusals in vm_stmt.c (11) and enc.c (5) read the Ctx directly: an F4 input.
- F3 BUILT (lane f3, 2026-11-27; `docs/dev/lanes/f3_report.md`). `target_headers_render`'s `nb`, `splice_mark`'s
  `tail` and `render_buf`'s `o` are `pcrec_scope_sb` entries of a scope on `&cx->arena` (`splice_mark` now takes the
  Ctx); `nb` and `o` hand their storage to csb/hsb by `pcrec_sb_adopt` before the close, so the close frees an empty
  buffer and nothing is copied. `nb`'s scope opens at pass 2 (after `pcrec_memfn_target_headers`, so no kit call runs
  inside it); `o`'s after `render_buf`'s early return. None of the three is reachable from `pcrec_facts_force_all`
  (both renders run before the force loop), so REGISTRY-1's trigger has not fired. Bound used: sizeof(StrBuf) 192
  (measured), so a STRBUF record requests 208 B (16 B header + 192) and a MARK 40 B: +248 B requested per rewrite live
  at the peak; the gate bound stays 256 B (C13). DELETED: the scanner's 3 `ALLOW` rows and its `shape:NAME` narrowing
  (`classify` returns shapes only); `alloc_check.c`'s `target_headers_render` row WITH THE WHOLE filed-stranding table
  (`known_stranded`, its seen counts, exit code 5, the stale-row loop) and the allocation-stack recording and `fn`
  column. The table is deleted rather than left empty: with no row nothing can reach it (learnings section 3), and a
  later filed stranding restores it with its first row. S3572 is RE-AIMED at S11 (the plant is the faithful pre-F3 shape: `tail` back on the
  heap AND freed before the return, two edits; S11 is SINGLE-CONTROL for stranding, the scanner the only net that NAMES
  the site; `alloc_check` W6's exact allocation pin also moves, incidentally, because the scope's STRBUF record is gone:
  an allocation-count net, not a strand check, r107 A). No row aims at S12 `o` (r107 D): its plant (a heap `o`) is the
  same scanner heap-builder rule S3572 already holds red, and no alloc witness compiles a layout-marked artifact (a heap
  `o` is empty after the adopt, so not even a success-path leak shows); a scanner-only row per client is the cheap
  option if one is ever wanted; S3584 is RE-AIMED at a heap second declarator beside
  `target_headers_render`'s scratch `lines` (per-declarator classification still matters without names).
  `MIN_SCOPE_OPENS` 2 -> 3 (half of 6 opening sites, D110).
- SCOPE-4 BUILT (lane scope4, 2026-11-27; `docs/dev/lanes/scope4_report.md`; review r105 SCOPE-4, measured by lane f3).
  `pcrec_clskit_emit_whole(c, parent, ...)` has F2's shape: the empty-set return first (no scope, no record), then a
  scope on `parent`, the body (`emit_whole_body`, static) on `pcrec_scope_arena(&sc)`, the close. Client S14b. Its sole
  compile route is the attempt (compile.c's `pcrec_emit_vm`, the one caller; r107 C, r108 D), so a refusal inside the body
  is released by compile_driver's handler-top unwind. Emitted C is byte-identical (no abi change). Measured at f3:
  under `-e utf8` + VM, 108 of 7,402 compiles move, all down (median -131,120 B, max -327,920 B). The memgate gate
  needed two levers to see it: `MG_ENC` (encoding) and `MG_ENG` (corpus engine), tests/core/memgate/CLAUDE.md.
  `MIN_SCOPE_OPENS` stays 3 (half of 7, rounded down; D110, grep in its comment). Sabotage S3643 (close deleted;
  S3613 re-anchored one line up because both closes read alike), S3644 (body routed back to the parent).
- S14c BUILT (lane scope4fix, 2026-11-27; review r108 B + A/C/D/E; `docs/dev/lanes/scope4fix_report.md`). F2's shape on
  `pcrec_clskit_whole_bytes(parent, ...)`, the selection-time pricing of a whole-set form: the `CLSF_PAGE2`/`PAGE3` tables
  (about 74 KB on a 650-range set, the twin of the copy SCOPE-4 removed) are built in a scope's child arena by a static
  body and released at the close; the result is one scalar. `CLSF_BITMAP1` and the empty set open no scope. Emitted C
  byte-identical (96 BASE/SUBJECT pairs, VM and auto, `-e utf8`). Sabotage S3648 (pricing body on the parent). The scope
  floor `MIN_SCOPE_OPENS` re-derived 3 -> 4 (half of 8 sites, D110, command in its comment). r108 A: S3644 and S3648 are
  declared `UNDETECTED` (no mech suite can see an arena identity); their net is memgate `peak` under the levers with
  `--bound 0`. Sibling not scoped: `pcrec_clskit_partition`'s DP scratch is mixed-lifetime (`out->sec` lives on the parent).
- F4 BUILT (lane f4, 2026-11-27; `docs/dev/lanes/f4_report.md`; K163 FIXED). D-4's six steps as written: `walk_part`
  takes the `forms` and `text` holds, sets `PcrecPartFacts.hold = forms`, lends, compiles, unlends, stores the text,
  refuses on a nonzero count. The part's copy is `part_forms_copy` (compile.c, static: exactly `strlen + 1` heap bytes
  through the part's own Ctx, stored into `*hold` before anything else can refuse; its own scanner `ALLOW` row). The
  accessor counts at `pcrec_arena_alloc` entry, `rec_take`, `sb_grow` past its capacity return, `pcrec_sb_take` and
  `pcrec_sb_render_prefix` (rec_take added to D-7's four: it allocates through an Arena carrying a `.cx`, so the claim
  needs it). The scanner's `readers` rule adds `pcrec_ctx_lent_p` (no src caller) and the lent pair (compound.c
  `walk_part` only), with fixtures. W7's lent window is its own row over W6 (`lent_window`: only lent points are trials,
  each one a trial); population 0 prints an INFO line, never a PASS. Sabotage (9) is S3653 (two edits: `walk_part`
  hands the outer arena where the hold was, the part's compile_driver copies into it with `pcrec_sb_fragf`). Measured:
  lent uses 0 over tests/compound/split.rxt; emitted C byte-identical (102 compiled + 3 refused identically, no abi move); W6 1016 of 1061.

## r102 disposition

| finding | disposition | where answered |
|---|---|---|
| B1 stale close, free-the-mark | FIX-NOW | D-2 L1 (generation stamp, `a->open`), L6, the two drills; API `pcrec_scope_close`; Discipline rows L1, L6 |
| B2 reused record state | FIX-NOW | API "THE ORDER": fresh `calloc` per record, no spare list, so no reuse |
| B3 check after the takes | FIX-NOW | D-4 success path; Discipline row L2 |
| B4 channel bypasses | FIX-NOW | D-7 "THE ONE CHANNEL ACCESSOR"; Discipline row D-7 |
| B5 F4 absorbed, W6 pin | FIX-NOW | D-4 "WHAT AN OOM IN THE COPY ANSWERS"; F4's gate |
| B6 F4 order | FIX-NOW | D-4's six-step order |
| B7 base level, G2a | FIX-NOW | D-2 L7; API (one list, one walk, `AOwn`/`owned` deleted); G2; "Predicted memory moves" |
| B8 S4 needs a FIELD row | FIX-NOW | D-1 S4 row (both shapes CAN; Job first); D-3 |
| B9 D-1 re-score | FIX-NOW | D-1: 6/6 tie with the note's (A); rev 2 gave R-3's peak cost and form as the reason; REV 2.1 states FORM alone (r103 C1); no flip |
| B10 close-release sabotage | FIX-NOW | API close post-condition; sabotage (2), (1b) |
| B11 W7 price and hook | FIX-NOW | Tests "W7": `--wrap` in the test link, windows, own counter, floor, budget, STOP |
| B12 massif inaccuracy | FIX-NOW | Standing question 1 (memgate primary; massif pinned, cross-check); gates on predicted deltas |
| B13 per-pattern G5 | FIX-NOW | G5 (per-compile p95/max); D-7 (sb_grow count after the early return) |
| B14 eager resources | FIX-NOW | API "THE ORDER": STRBUF/ARENA lazy, HEAP only takes steps 1-4 |
| B15 instruments, STOPs | FIX-NOW | T1 (memgate committed, arena-block split); C0(b) population named; every unit's STOP column |
| B16 `Ctx.lent` field | FIX-NOW | D-7 (field pair, writer/reader line) |
| B18 D203 items for F4 | FIX-NOW | Clients "F4 AS A D203 FIX"; C0(d) STOP |
| B19 ALLOW arithmetic | FIX-NOW | D-8 "SCANNER ROWS" (rev 2: net -5 +3; rev 2.1: -6 +2, by the scanner's rules, C8; `shape:NAME` deleted at the later of F2/F3) |
| B20 builder rule hunks | FIX-NOW | D-12 |
| B22 witness reach | FIX-NOW | D-8 witness table; C0(c) |
| B28 D-11 placement | FIX-NOW | D-11 (scanner rule at the binder) |
| B17 P6 re-wording, `child` writer | DOC | Refactors (RM-3 declined, P6 re-worded); D-7 (`child` written by arena.c only) |
| B21 dropped PLAN items | DOC | Open questions (e) |
| B23 DfaMemo kind, interim | DOC | D-10 (two steps) |
| B24 U8 weighed; R2 reach | DOC | D-4 "U8 WEIGHED"; Clients "R2's REACH" |
| B25 L5 reason | DOC | D-2 L5 (corrected reason, kept, trigger) |
| B26 D-5 arrays; dfa.c rule | DOC | D-5 |
| B29 generic release, base level | DOC | API kind table (`release(void *storage)`); D-2 L7 (base = bottom) |
| B30 one Job-owning point | DOC | D-3 |
| B31 count commands | DOC | Cost and measurement, "NUMBERS CITED" |
| B27 trace restores | PLAN | [ARENA-SCOPES] refs in docs/dev/plan.md (unlock and trigger); Open questions (h) |
| B32 driverless Ctxs | NOTED | Discipline and checks, after the handler table |

## r103 disposition

| finding | disposition | where answered |
|---|---|---|
| C1 D-1's deciding reason is not the 64 KB | FIX-NOW (design) | D-1 ("THE DECIDING REASON IS THE FORM", "CONTEXT, NOT THE REASON", the cost-per-scope table row "0 to 64 KB"); header paragraph; Standing question 1; Open questions (owner line) |
| C2 D-1's numbers re-derived, refusals in the population | FIX-NOW (doc) | D-1 "CONTEXT": successful compiles only (6,017: median 821,680, +8.0%, 3,782 over 5%, 5,393 over 1%); Cost and measurement, the k155fix base is not a constant |
| C3 liveness premise, method and population | FIX-NOW (design) | D-1 "CONTEXT" (146 of 150, gdb probe, successful compiles); Clients C0(b) |
| C4 registering calls skip L1 | FIX-NOW (memory) | D-2 L1 (one shared `scope_check`, all six calls); free-the-mark drill step 3b; Discipline row L1; API |
| C5 stamp clause has no control that must fail | FIX-NOW | D-2 stale-handle drill (forged handle); Discipline row L1 (4b, 4c); Tests: sabotage (4b) |
| C6 W6 pin moves at F1, F2, F3, F5 | FIX-NOW | Tests "COUNTER"; Clients F1, F2, F3, F4, F5 gates |
| C7 F1's anchor rows and readers | FIX-NOW | Clients F1 (S255/S256 move, S3580 re-aimed, the readers by grep), R1 (rows by suite arm) |
| C8 scanner rows not what the scanner flags | FIX-NOW | D-8 "SCANNER ROWS" (-6 +2 or +3; `shape:NAME` four users, deleted at the later of F2/F3); G4; Tests (scanner) |
| C9 reader line, accessors, W7 and S14 | FIX-NOW | D-7 (two read-only accessors, alloc_check.c named); API; Tests "SAMPLING" |
| C10 W7's lent window cannot fail after F4 | FIX-NOW | Clients F4 gate (W6 for the inner copy; the lent window kept as pre-fix control, floor 0); Tests "CONTROLS" |
| C11 the lent count's reach | FIX-NOW | D-7 (four counted entries; claim stated); F4 as a D203 fix, FIX SHAPE |
| C12 D-11's binder rule keyed on a spelling | FIX-NOW | Discipline row "D-11 pin" (type and `mf_art_begin(` keyed, both spellings); Clients F2 |
| C13 F3's STOP below its bound | FIX-NOW | Clients F3 STOP (256 B); Predicted memory moves F3 |
| C14 T1's split by allocating line | FIX-NOW | Standing question 1; Clients T1 (by arena identity) |
| C15 F4's `into` replacement unnamed | FIX-NOW (doc) | Clients F4 (`PcrecPartFacts.hold`, writer, reader) |
| C16 alloc_check's two links; arena.c callers | FIX-NOW | Clients F1 (both link sites); Discipline row "D-7 channel" (no arena.c function calls `pcrec_arena_alloc`) |
| C17 G4's `free(` grep | DOC | G4 (bare-`free(` regex, expected `pcrec_scope_free(` count stated by the lane); Cost and measurement "NUMBERS CITED" |
| C18 C0(d)'s scratch method | FIX-NOW | Clients C0(d) (a `--wrap` of `pcrec_compile_driver` with a nesting depth; not T1's hook) |
| C19 (i) NULL deref, (ii) vacuous conjunct, (iii) open order, (iv) NULL channel, (v) gen reset, (vi) fork per refusal | FIX-NOW (i), (vi); DOC rest | (i) D-2 L1 and drill 3c; (ii) API close post-condition; (iii) API open order; (iv) D-7; (v) D-2 L1; (vi) the drills' preface and Tests unit tests |
| C20 `uprops_produce` `Arena tmp` | FIX-NOW + design decision | D-1 table row S29 and the 7/7 count; D-2 L4 (narrowed for the one client, with reasons); D-4 (S29); D-8 and Clients F6; D-10's kinds sentence; counts at d4a6c0b74 (463 `pcrec_arena_alloc(`, 34 writers, 6 scanner rows); handler table; Open questions (i) |
| NEW (RULED) `make test-alloc` green with the strand | gate added | Tests "THE SEEN GATE" (unit planted-strand test, the filed row required REACHED, sabotage (10)); G3; Clients F1 and F6 |

## STATE AT HANDOFF

Lane arenadesign21, 2026-11-25. Rev 2.1: text only. Tree T = 046438a1c for the design; counts re-run at main d4a6c0b74.
Rulings file `arenadesign21_rulings.md`: empty at every re-read; no ruling applied beyond the brief's RULED section.
C20's choice: L4 narrowed for the one client `uprops_produce`, as unit F6. No probe, no code, no new measurement.
OWED: none
