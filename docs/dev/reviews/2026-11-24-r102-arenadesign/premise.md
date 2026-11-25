# Findings: lens premise (r102 arenadesign)

## Findings



### PREMISE-1 CONFIRMED (design; effort XS; blast: D-1 row S13's (A) column only, verdict count unchanged): `keyseen` is not a per-refinement-pass table
§D-1 row S13, (A) column: "plus a nested scope per refinement pass for `keyseen`, else its per-pass table is retained n times".
FALSE at F. `src/opt/minimize.c:130` mallocs `keyseen` ONCE, inside the initial-partition block, and frees it at :148,
BEFORE the refinement loop `for (;;)` at :151 starts; the loop itself allocates nothing (`sed -n 130,190p
src/opt/minimize.c`; `grep -n -E 'malloc|calloc' src/opt/minimize.c` = 8 sites: part, newpart, sig, htab, keys at
:83-89, keyseen :130, seq/ns :197-198, none inside the loop). Under (A) a child arena per call retains `keyseen` (n
ints) to the call's end ONCE, beside `keys` (n*siglen ints), i.e. a peak rise of 1/(siglen+4) of the tables, not n
copies, and no nested scope is needed. The row's (A) cell overstates (A)'s cost; the S13 "YES / YES" outcome stands.
Expected: "(A): child arena per call; `keyseen` (allocated once) is retained to the call's end, +n ints".

### PREMISE-2 CONFIRMED (design; effort S; blast: D-1's "deciding sites" row and its prose "at S4 it is the only shape that can delete anything"): the S4 "CAN, 33 lines" needs an entry kind the design's kind table does not have, and the same kind is open to (A)
The S4 cell says "an entry keyed on the FIELD survives realloc and the swap". The kind table (§API) has HEAP (`void *p`,
a VALUE), STRBUF (`StrBuf sb` INSIDE the record) and ARENA (`Arena ar` inside the record). The S4 arrays live in Job
fields, not in records: `free(cx->job->nfa.st)` .. `free(cx->job->lmdfa.tab)` (`src/core/compile.c:280-312`), grown
by `realloc(nfa->st, ...)` (`src/ir/nfa.c:172`, `src/ir/dfa.c:1591`) and swapped BY VALUE at `src/core/compile.c:587-591`
(`tn = job->nfa; job->nfa = job->xnfa; job->xnfa = tn;` .. the conditional `adfa` swap). A HEAP entry holding the
value is wrong after the first realloc AND after the swap (it would free the x-set's array via the primary's record
and vice versa only by luck of symmetry, and a stale pointer after realloc). Keying on the field needs a FOURTH kind
(record holds `void **field`), which the design says is "a design change, reviewed, never a local addition". Two
consequences: (1) the capability row credits (B) as DESIGNED with something it cannot do without a new kind; (2) the
(A) cell's reason ("a by-value owned slot cannot follow either") is a property of today's `AOwn` (`{ next; void *p; }`,
`src/core/internal.h:345`), not of shape (A): an `Arena.owned` slot holding `void **` (the arch note's (A) admits heap
blocks "through `Arena.owned` (S3)", arch note "TWO CANDIDATE SHAPES") follows realloc and the swap exactly as (B)'s
fourth kind would. So at S4 the honest row is "(A): CAN with a by-address owned slot / (B): CAN with a by-address
kind", 33/33 (both not taken, D-3), and "the only shape that can delete anything" at S4 is not true.
Also: of the 33, one is `free(cx->job)` itself (compile.c:311), the record that holds the 32 keyed fields; a field-keyed
entry must be released before it, which the LIFO order gives only if the Job's entry is registered first (before
`compile_driver` writes any field). Not stated; no impact while D-3 keeps the list.

### PREMISE-3 CONFIRMED (design; effort S; blast: D-1's deciding count 4-vs-6 and "(B) deletes more at every site"): the (A) column scores a narrower shape than the accepted note's (A); under the note's (A), S10 and S12 delete too
The accepted arch note defines (A) as "a scope is an arena whose blocks are freed at its exit; heap blocks join through
`Arena.owned` (S3)" (arch note, "TWO CANDIDATE SHAPES"). D-1's S10/S12 (A) cells consider ONLY an arena-backed builder
(`.ar` set: `sb_grow`'s arena branch, `src/core/sb.c:60-62`, a fresh block and a copy per doubling) and so conclude
"NO: grows by copy ... adoption must COPY". They never score the note's other (A) path: a HEAP StrBuf owned by the
scope's child arena. The design's own STRBUF row shows how that is done without realloc trouble: "A StrBuf ... lives
INSIDE its record, so a `realloc` in `sb_grow` updates the field the release reads" (§API). An `Arena.owned` record
holding a `StrBuf` (instead of `void *p`) is that same record on (A)'s owned list; the builder then grows by `realloc`
(`src/core/sb.c:64`) exactly as today, the hand-off at `memfn_stamps.c:375-378` / `part_layout.c:643-648` stays a
heap-to-heap transplant with no copy, and the child arena's release frees an emptied record. Peak = today's. So
under the note's (A): S10 YES, S12 YES, and the deleted count is 6 (S10-S15) for BOTH shapes. Re-derived table:
S10 6/6 equal, S11 equal, S12 equal, S13 equal (PREMISE-1: no nested scope needed), S14 equal, S15 equal; S4 equal
in capability (PREMISE-2); S7 equal (the design's own row). The 4-vs-6 margin is an artefact of the (A) variant scored,
not of the shapes. What still separates them is not a deleted special case but cost and form: (A) puts a 64 KB
`ABLOCK_MIN` block (`src/core/arena.c:6,18`) under every child arena whose first allocation is a record (PREMISE-4),
and (A)'s owned list cannot release one member early (`keyseen`, minimize.c:148) without a second list operation.
The verdict (B) may well survive on those grounds, but D-1 says it is "decided by deleted special cases as the owner
ruled", and on that criterion, re-derived, it is a tie. Expected: D-1 scores the note's (A) (with heap joining through
an owned record) and decides on the stated tiebreaker, or states why the owned path is excluded from (A).

### PREMISE-4 SUSPECTED (design/memory; effort XS; blast: D-1 (A) cells S11, S13; strengthens (B) but on a ground D-1 does not state): (A)'s "YES" cells omit the arena's 64 KB block floor
`src/core/arena.c:6` `#define ABLOCK_MIN (64 * 1024)` and :18 `size_t cap = sz > ABLOCK_MIN ? sz : ABLOCK_MIN;`: a
child arena's first allocation mallocs at least 64 KB. D-1 marks (A) YES at S11 ("one append: one block, no doubling")
and S13 ("child arena per call") with no peak check, while S10/S12 are marked NO on a peak argument. At S11 today's
`tail` is a heap block of the next power of two above the tail's length (`sb_grow`, sb.c:52-53), small on a small
artifact; at S13 the eight tables are n- or m-sized ints (minimize.c:83-89,130,197-198), tiny on a small DFA. Under
(A) each live call holds >= 64 KB, against G2b's "+1% or +4 KB". (B)'s records are heap (about 200 bytes each), so
(B) does not have this cost. Would confirm: massif on a small-DFA corpus pattern under a scratch (A) build, or the
arithmetic against C0(b)'s base peak. Effect on the verdict: an (A) floor cost the table should state; if it breaches
G2b, (A)'s S11/S13 cells are "YES at a peak cost", the same class of NO the S10/S12 cells use.

### PREMISE-5 CONFIRMED (doc; effort XS; blast: one D-3 sentence, the argument stands): `pcrec_count_groups` owns no Job
§D-3: "the two recovery points that own a Job (`compile_driver`, `pcrec_count_groups`) already reach `job_cleanup`".
`src/core/compile.c:3870-3912` (`pcrec_count_groups`): `Ctx cx; memset(&cx, 0, ...)`, `cx.arena.cx = &cx`, setjmp at
:3904, `job_cleanup(&cx)` at :3905/:3912; `sed -n 3870,3913p src/core/compile.c | grep job` shows only the two
`job_cleanup` calls: `cx.job` is never allocated, so `job_cleanup` runs its `if (cx->job)` body never and reduces to
`pcrec_arena_free`. Only `compile_driver` owns a Job (`cx.job = calloc(1, sizeof(Job))`, compile.c:2491). The D-3
reasoning (no stranding to fix in the named list) is unaffected; the sentence should say "the one recovery point that
owns a Job, `compile_driver`, reaches `job_cleanup`; `pcrec_count_groups` reaches it with no Job".

### PREMISE-6 CONFIRMED (design/memory gate; effort XS; blast: G2a's check on compound corpus patterns at F4, possibly R2): "nothing new is allocated from any Ctx arena, high-water IDENTICAL" is false for the units that move arena bytes OUT
G2a: "attempt-arena high-water bytes IDENTICAL on the corpus (records are heap; nothing new is allocated from any Ctx
arena)"; G2: "A favourable move cannot arise, because no peak is lowered; if one appears it is reported, not kept".
At F the K163 copy is an OUTER-arena allocation: `pf->memfn_forms = pcrec_sb_fragf(pf->into, "%s", cx.job->memfn_forms)`
(`src/core/compile.c:3735`), `pf->into = &w->cx->arena` (`src/core/compound.c:182`), reached on EVERY successful part
(the guard at compile.c:3732 makes a part without forms an internal error), plus the K155 record
`pcrec_arena_own_slot` -> `pcrec_arena_alloc(a, sizeof(AOwn))` (`src/core/arena.c:44`, compound.c:183). F4 replaces the
first with "a heap copy" in a hold, and R2's `pcrec_arena_hold` record is, by §API's "THE ORDER INSIDE EVERY
REGISTERING CALL ... (1) take a record (spare, else malloc ...)", a heap record, not an arena one. Both units therefore
LOWER the outer attempt arena's bytes on every compound pattern with a part (rounded 16-byte cells; a block boundary
can move with them), so G2a reads DIFFERENT there, and the rule "reported, not kept" would reject F4, a D203 bug fix.
Expected: G2a scoped to F1-F3/F5 (or "identical except the K163 copy and the hold record, which leave the arena at F4/R2,
listed"), and F4's/R2's gate naming that expected move. Also unstated: whether base-level (`owned`) records become heap
(then `pcrec_arena_free`'s walk must free them, §API's release order names only `spare` and the blocks) or stay arena.

### PREMISE-7 CONFIRMED (doc; effort XS; blast: G4's checkable form, D-1/D-8 counts): counts stated with no command; re-derived, all hold
The design gives a command for one count only (the recovery points, §D-4). The rest are bare or cite the arch note.
Re-derived at F (review tree), each holds:
- "25 (minimize.c) + 37 (scanedge.c)" `free` calls (G4, D-1, D-8, Cost): `grep -o -E '\bfree\(' src/opt/minimize.c | wc -l` = 25;
  same for `src/opt/scanedge.c` = 37 (no command in the design, and not in the arch note's C-10/C-12 as these totals).
- "8 tables" (S13): part, newpart, sig, htab, keys (minimize.c:83-89), keyseen (:130), seq, ns (:197-198) = 8.
  "10 tables" (S15): scanedge.c:621-622 lists 9 + `ns` (:787) = 10. "about 10 live entries" (Cost) = this 10.
- "27 `free` + 6 `pcrec_sb_free`" (S4): compile.c:280-312, 27 incl. `free(cx->job)` at :311; 6 sb_free :302-307.
- "5 ALLOW rows": `grep -n 'ARENA-SCOPES' tests/core/scratch_builder_check.py` = 6 lines, 5 rows (:94, :97-100) + 1 comment (:95).
- "2 known_stranded rows": tests/core/alloc_check.c:210, :212.
- "462 allocation calls": `git grep -n -E 'pcrec_arena_alloc\(' -- src cli lib memfn/src | grep -v -E '^src/core/(arena\.c|internal\.h):' | wc -l` = 462.
- "22 scratch builders": the same filter over `pcrec_sb_scratch\(` = 23 lines (arch C-17: one is prose), holds.
- "33 hand writers": src 9 initialisers (`git grep -n -E '\bArena\s+[a-zA-Z_]+\s*=' -- src cli lib memfn/src`) + 7 `.cx`
  writes (compile.c:2490,3898; syntax_dump.c:848,1203,1700; dfamemo.c:161; rxt_source.c:2838); tests 11 `.cx` writes + 6
  initialisers = 33.
- "13 LSan leak shards (cloud run 45492837175)": cited, not re-derivable from the tree (not probed).
Expected: G4's counts carry their command (the counts are the build's own exit check).

### VERDICT on sub-part (b), D-1's 4-vs-6
Does not survive as a count. Scored as the design scores it (arena-backed builders only), 4-vs-6 is mechanically right
(S10/S12 (A) NO holds: an `.ar` builder grows by a fresh block per doubling, sb.c:60-62, while the source csb is still
live, so about 3x against today's about 2x; and adoption of arena storage into heap `csb` must copy, sb.c:470-473 shows
the same rule for `pcrec_sb_take`). A child arena per call released after the hand-off removes the retention to the
attempt's end but NOT the copy or the in-build doubling, so it does not rescue that variant. But the accepted note's (A)
also lets heap blocks join through `Arena.owned`; with the StrBuf inside the owned record (the design's own STRBUF
trick) S10/S12 delete under (A) too, so the count is 6/6 (PREMISE-3), and S4's capability is 33/33 (PREMISE-2). No row
was found where (A) deletes and (B) does not (checked S7, S19, S20, S25, S16, S6, S9). What does separate the shapes is
cost and form: the 64 KB `ABLOCK_MIN` floor per child arena under (A) (PREMISE-4), (A)'s owned list having no early
release (`keyseen`), and (B)'s heap records leaving arena bytes alone. (B) is likely still the right pick, but on those
grounds, which D-1 should state as its deciding criterion.

## PROBED-AND-HELD

- Recovery points: `git -C <tree> grep -n -E 'setjmp\(|pcrec_arena_free' -- src tests`: 5 src setjmps (compile.c:2577,
  3904; syntax_dump.c:875, 1209, 1722), each ending in `pcrec_arena_free` (directly or through `job_cleanup`); 6 test
  points (definitions_check.c:98/168/576, definitions_oracle_gen.c:426, branch_count_check.c:123, cwmax_check.c:227), each
  ending in `pcrec_arena_free` (definitions_check.c:107 `release`, :599-626; oracle_gen :429; branch_count :135; cwmax
  :236). No other `jmp_buf` re-arm in src (`git grep -n -E 'jmp_buf|->jb|\.jb\b' -- src`); tests/memfn/proof_run.c's
  sigsetjmp is not a Ctx point. cli/ lib/ memfn/src: no setjmp.
- FIT_FORCE_NEXT is the one resuming arrival (compile.c:2596-2614 `goto facts_force`); every other row returns or
  `continue`s after `job_cleanup`. 10 `job_cleanup` calls in `compile_driver`, 6 followed by `continue` (2658, 2709, 3499,
  3512, 3522, 3614).
- S4 list 27 + 6 (compile.c:280-312); swap BY VALUE at compile.c:587-591 (adfa conditional); realloc at nfa.c:172,
  dfa.c:1591.
- `scr_test`/`scr_desc` are Job fields freed in `job_cleanup` (compile.c:306-307), `.cx` set at :2496. HOLDS.
- `pcrec_arena_alloc` aborts on a detached arena (arena.c:26-27). HOLDS.
- clskit test driver calls the kit with no Ctx: `Item.text` memset-zero (clskit_driver.c:156), so `c->cx` is NULL in
  `pcrec_clskit_emit_kit`'s `Arena a = { .cx = c->cx }` (clskit.c:1126). HOLDS. Three src callers (emit_vm.c:13313,
  13344; emit_dfa.c:13225), each with a Ctx in scope. HOLDS.
- minimize.c's results from `&cx->arena` while tables live (minimize.c:220, 226). HOLDS (L3's premise).
- StrBuf-in-record follows realloc: `sb_grow` writes `sb->p`/`sb->cap` (sb.c:65-66). HOLDS.
- csb/hsb are heap in every client: no `.ar` write on a Job StrBuf (`git grep -n -E '\.ar\s*=' -- src` = dfa.c:1927
  scratch tables + internal.h:516 `pcrec_sb_scratch` only). D-6's "both sides heap" HOLDS.
- K163's copy goes through `pcrec_arena_alloc` (sb.c:647 via `pcrec_sb_fragf`), so the lent check's counter at
  `pcrec_arena_alloc` sees it; it runs on EVERY successful part (compile.c:3732-3735), not only "with kit forms".
- `pcrec_memfn_arena_alloc` exists (memfn_sites.c:70), its arena is set at one site, `ma->u = &cx->arena` (:211).
- Kept functions: `job_cleanup` frees the Job before `pcrec_arena_free`; no release function in the kind table reads
  the Job, so the order is safe. `pcrec_arena_free` walking entries before blocks is required already (AOwn records live
  in blocks) and is kept. Every new Arena field's zero is valid (depth 0, child false, NULL lists); the one positional
  initialiser form, `Arena a = { NULL, c->cx }`, is a scanner fixture string (scratch_builder_check.py:217), not code.
- Largest case reached: the compile_driver handler (fit_walk + sets routine, compile.c:2577-2720) and the nested part
  compile (compound.c:172-194 with compile.c:3720-3745). No compiles run (0 of 60).

CRITIC COMPLETE premise 7
