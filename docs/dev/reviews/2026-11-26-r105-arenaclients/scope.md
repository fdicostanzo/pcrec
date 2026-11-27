# r105 arenaclients, lens scope

## Findings

### SCOPE-1 (a) Both regions are registry-sound on every arrival: CONFIRMED (no defect)
Severity: answer (none found). Effort: 0. Blast radius: none.
- Inside F2's region (src/gen/clskit.c:1130-1138) the only calls are emit_leaf_tables (:957), emit_bound (:1106),
  emit_tree/emit_leaf (:1086/:1014), intern_records (:358), emit_array, pcrec_sb_fragf on the CHILD and
  pcrec_sb_printf/puts on `c`. Inside F6's (src/parse/mod_uprops.c:295-302): pcrec_ucd_find -> pcrec_ucd_row_set ->
  ucd_decode on the CHILD (ucd_tables.c:143-159); pcrec_ast_class_from_iv (parse.c:933) -> node/cpset_init/add/
  cls_fold/cpset_publish, all `pcrec_arena_alloc` on `&cx->arena` (L3: legal, block chain, not a registry entry).
  NEITHER region calls pcrec_arena_hold, pcrec_scope_sb/_malloc/_calloc/_arena on the parent, a nested
  pcrec_scope_open, or lend/unlend (no lend exists in src at SUBJECT: `grep -rn lend src` = 0 API hits). The only
  registry calls in all of src are minimize.c:84-238, clskit.c:1130-1138, mod_uprops.c:295-302, compound.c:183 (the
  one hold), compile.c:2583/3747 (unwind, check). So close's post-condition (arena.c:145) cannot fail, L7 cannot
  fire, and no child pointer escapes: `iv` is consumed by value (cpset_add copies bounds), fn/t names are copied
  into `c` by printf. `c` is a heap Job StrBuf or a pcrec_sb_scratch on `&cx->arena` (emit_dfa.c:13249): growth is a
  parent BLOCK (L3), never released by the close.
- Nesting: none possible. Minimize's region calls only scope_*/arena_alloc/memset/memcpy/state_sig/fnv (awk over
  minimize.c:84-260), clskit's and uprops' regions reach no other opener, so depth on any arena is <= 1. Parent is
  always a Ctx's embedded `.arena` (`&f->cx->arena`, `&cx->arena` at emit_dfa.c:13225, emit_vm.c:13313/13345,
  mod_uprops.c:295), never DfaMemo.arena (dfamemo.c:161 is not passed) and never a child (L5 would reg_fail at
  arena.c:115). Every src Ctx sets `arena.cx` (compile.c:2491, 3907; syntax_dump.c:848, 1203, 1700), so the child's
  channel (`c->cx = a->cx`, arena.c:212) equals the old `{ .cx = cx }` / `{ .cx = c->cx }` locals' channel.
- Every arrival: compile_driver's handler unwinds first (compile.c:2583) then tears down or resumes; count_groups
  (compile.c:3913 -> job_cleanup -> pcrec_arena_free, :330 runs even with no Job) and the three syntax_dump
  handlers (:881, :1210, :1725) end in pcrec_arena_free, which releases the open mark and the ARENA entry (arena.c:281).
- Run (gdb, subject build/pcrec): `-p rx --tune=-2 --pattern '\w+@\w+'`, at clskit.c:1136 set `c->abort_over = 1`
  so the next write refuses INSIDE the kit scope. Observed: handler arrival with `a->open` == the kit's mark, the
  unwind closes exactly one scope (arena.c:220 hit once), then the refusal "size-term ladder trial over its scratch
  bound" exits rc 1 cleanly; no reg_fail. Natural arrivals: 6 patterns (incl. `[\p{L}\p{N}]+x[\p{Han}]{3,} -e utf8`,
  `(?:[\p{Lu}][\p{Ll}]+\s){5,40}\d -e utf8`) gave 4 handler arrivals, 0 with a scope open.

### SCOPE-2 (b) REGISTRY-1's TRIGGER has NOT fired: CONFIRMED
Severity: answer (none). Effort: 0. Blast radius: none. § Deviations at build, r104 REGISTRY-1 (arena_scopes.md:786).
- FIT_FORCE_NEXT is asked only on FIT_L_FORCING (compile.c:1332), which is `job->pf.forcing` (compile.c:1522), true
  only inside pcrec_facts_force_all (facts.c:697-712). So the part after `facts_force:` (prefix render, facts_hook,
  the part-facts block, compile.c:3694-3744) refuses as an ordinary teardown, not a resume.
- force_all reaches only pf_derive (facts.c:322): every external callee from src/facts/*.c (grep of `pcrec_*(`
  calls, ~120 names) is an AST/NFA/DFA READ (kinds, nullable, start_set, req_walk, kset_walk, land_char,
  width_walk, never_matches -> pcrec_dfa_accepts_nowhere/pair_matches_nothing on BUILT DFAs, dfa.c:2085/2101,
  find_byte_rate in findings.c). None is a parse/ext/uprops, a gen/clskit or a min-DFA build entry.
- gdb (breakpoints pcrec_scope_open + pcrec_facts_force_all) with `--emit-facts` on 3 patterns that hit BOTH
  clients (`(?i)[\p{Greek}\p{Cyrillic}]+q -e utf8`; `\w+@\w+ --tune=-2`; `x\p{L}y[\p{Greek}a-f]+z -e utf8
  --engine=vm --tune=-2`): 2+2+0 uprops opens, 0+5+1 kit opens, 4+4+0 minimize opens, ALL before FORCE-ENTER; 0 after.
- pcrec_count_groups is a separate setjmp (compile.c:3913) with no fit rows, not reachable from the force loop
  (one caller, cli/main.c:3315). So the unwind stays NOT load-bearing for either client; the subject correctly
  builds no resume witness/sabotage row (D77), and the trigger stands unchanged (the next client must re-ask it).

### SCOPE-3 Comments say "teardown" where compile_driver's release is the handler-top UNWIND: CONFIRMED, doc nit
Severity: doc. Effort: 2 lines. Blast radius: comments only. src/parse/mod_uprops.c:292-293 ("longjmps with the scope
open; the compile arena's teardown releases the child") and src/gen/clskit.c:1122-1123 ("or by the parent's teardown if
a refusal leaves here"). In compile_driver every arrival first runs pcrec_scope_unwind (compile.c:2583), which
releases the child through the close (rec_release -> kind_arena's release) BEFORE any fit row, and on the
FIT_FORCE_NEXT row there is NO teardown; teardown is the releaser only for count_groups and syntax_dump. Witness:
SCOPE-1's gdb run (unwind's close freed it). Suggested words: "released by the refusal's unwind or teardown (D-4)".
Cites D-4; not a contract change.

### SCOPE-4 SIBLING OF A FAMILY: the hand-kept in-compile arena family is CLOSED; one retained-scratch sibling remains: pcrec_clskit_emit_whole
Severity: size (SUSPECTED for the peak claim). Effort: 3 lines (F2's shape). Blast radius: emit_vm.c:13347 (one caller).
- Grep `\bArena +[a-z_0-9]+ *(=|;)` over src: 7 locals, ALL detached `{ 0 }` outside any compile/setjmp
  (compile.c:252 subst compile, emit_subst.c:1210, measures_dump.c:63, findings_dump.c:265/332/376/422) plus 3 struct
  fields (Ctx.arena internal.h:4105, RxtSource.arena :7346 with cx NULL, DfaMemo.arena :8076). So 0 hand-kept
  Ctx-bound locals remain after F2+F6; D-10's new "two kinds and a scope's child" text (internal.h:347) is exact.
- The same CALL SITE's other arm, `pcrec_clskit_emit_whole(c, &cx->arena, ...)` (emit_vm.c:13347; clskit.c
  `build_pages`, intern_records' slot table, BITMAP1's bitmap), writes its pure scratch straight into the attempt
  arena, retained to the attempt's end. Measured by gdb (block `used` sum on `a` around the call, -e utf8 --engine=vm):
  `x\p{L}y` 119,440 B retained of 2,977,696 B arena total (4.0%); `x[\p{L}\p{N}\p{M}]y` 497,232 B of 4,516,208 B (11.0%).
  Not a strand (no refusal loses it); the COST-1 class (D-5, [ARENA-REGROW]). That row's trigger U7 is "a
  retained-garbage share of peak above noise": 11% of arena bytes MAY meet it. Confirm: memgate peak RSS of the
  L+N+M witness with emit_whole's scratch in a scope child (F2's 3-line shape, `a` -> child for scratch, fragf names
  may stay on the child since emit_array copies them) vs today. If above noise, it is F2's form, not a new mechanism.

### SCOPE-5 GENERAL FORM + UNLOCKS
Severity: design. Effort: none now. Blast radius: none now.
- General form already in place: "transient decode/emit scratch = scope on `&cx->arena` + one ARENA child, closed on
  the one return path" (minimize HEAP, F2 and F6 ARENA). F2 takes `Arena *parent` as a parameter rather than reading
  `&c->cx->arena`: correct (the test driver tests/clskit/clskit_driver.c:169/197 passes a detached arena, and a
  StrBuf's cx can be NULL outside a compile).
- UNLOCK 1 (trigger: SCOPE-4's peak measurement above noise): emit_whole joins F2's shape; with it every clskit
  scratch is scoped and `pcrec_clskit_emit_whole`'s `Arena *a` param becomes `parent` (one signature, both arms).
- UNLOCK 2, L5's lift trigger (arena_scopes.md D-2 L5) names "a helper reached from both a parent and a child arena that
  must open a scope (clskit.c intern_records is the candidate)". After F2 the "reached from both" half is TRUE
  (intern_records/build_pages via emit_whole on `&cx->arena`, via emit_kit on the child); the "must open a scope"
  half is NOT (it opens none). Trigger unmet; record the half-fired state so the next reader does not re-derive it.
- UNLOCK 3 (REGISTRY-1, unchanged trigger): the first pf_derive arm that builds (rather than reads) a machine or
  parses would be the force-loop client; src/facts' callee list (SCOPE-2) is the place to grep at each new fact.

Minimum witness size reached: 7-char patterns (`\w+@\w+`, `x\p{L}y`). Compiles used: ~30 (all gdb runs, subject only).

## PROBED-AND-HELD
- Registry calls in src: 3 openers + 1 hold + unwind + check (grep, 1 sweep): no opener reachable inside another's region. HELD.
- Natural handler arrivals with a scope open: 6 patterns, 4 arrivals, 0 open. HELD (no natural witness at this size).
- Forced refusal inside the kit scope (gdb, abort_over=1): 1 case, unwind closes 1 scope, clean rc 1. HELD.
- Forged FIT_FORCE_NEXT arrival inside the kit scope (gdb: pf.forcing=1 + abort_over=1), unwind kept vs skipped
  (`return` at pcrec_scope_unwind): 2 cases; both end in the K79 prefix-render refusal (the forged resume skips the
  rest of emission), a teardown, so the forged shape never reaches check_closed: not a realizable witness; consistent
  with SCOPE-2 (the shape is unreachable). HELD.
- Force loop vs scope opens under --emit-facts: 3 patterns, 0 opens after force entry. HELD.
- Channel equality (child cx vs old local cx): 5 src Ctx constructors set arena.cx; 0 tests parse with a Ctx lacking it. HELD.
- Parent identity: 3 call sites + 1 test driver; none passes DfaMemo.arena or a child. HELD.

CRITIC COMPLETE
