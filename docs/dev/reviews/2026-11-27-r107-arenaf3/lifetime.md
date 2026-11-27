# CRITIC lifetime: arenaf3 (r107)

## Findings

### LIFE-1 W6 re-pin comment names all three rewrites inside part compiles; only S11 runs there
- CONFIRMED (trace + arithmetic). severity: doc. effort: one comment line. blast radius: the W6 pin's stated cause (D110 re-pin record).
- tests/core/alloc_check.c, the W6 block comment ("the three rewrites' scope records are new heap calls in each part
  compile"). In a walk part compile (compound.c:184, `unrendered = true`) S12 never runs (compile.c:3693 skips
  `pcrec_part_layout_render` when `emit_in->unrendered`) and S10 opens no scope (memfn_stamps.c:340-343: a part holds 0
  target-header marks and returns before the open). Only S11 (`splice_mark`, the MEMFN mark) opens a scope in a part.
- Repro: `kit.sh alloc subject --sites`: W6 1014 of 1057 absorbed vs F1's 1010 of 1045. +4 absorbed = 2 parts x 1 S11
  scope x 2 records (mark + STRBUF); +8 diagnosed = the outer compile's 4 scopes (MEMFN + 2 ks marks + render_buf csb).
  The numbers fit "S11 only in parts", not "the three rewrites in each part compile".
- Fix: say "S11's scope records (the MEMFN splice) in each part compile, and the outer compile's S11/S12 scopes".

### LIFE-2 the "(teardown only on the count_groups/syntax_dump routes)" parenthetical names routes these sites cannot be on
- CONFIRMED (trace). severity: doc. effort: three comment edits (plus the F2 sibling). blast radius: comments only.
- src/gen/memfn_stamps.c:253, :370; src/gen/part_layout.c:603 (and the F2 sibling src/gen/clskit.c:1124). The phrase is
  copied from mod_uprops.c:293, where it is true: a parse runs under count_groups (compile.c:3913, `job_cleanup` only)
  and the syntax_dump probes (syntax_dump.c:875/1209/1722, `pcrec_arena_free` only). Those routes are parse/doorway
  only; none reaches `pcrec_memfn_stamps_render` or `pcrec_part_layout_render`, whose only callers are compile.c:3430
  and :3693 inside compile_driver's attempt (grep: no other caller). For the gen sites the only recovery point is
  compile.c:2578, whose handler unwinds first (2583). The comment tells a reader there are two more exits to reason
  about that do not exist (and would hide a real one if a gen-reaching route without the unwind were ever added,
  because the comment already "accounts" for it).
- Fix: drop the parenthetical at the four gen sites (or replace with "compile_driver's attempt is the only route here").

### LIFE-3 S3572's re-aimed plant is a success-path LEAK, not the refusal-window strand its row describes; "only the scanner sees it" is false
- CONFIRMED (probe). severity: maintenance (check design: the plant's story and its nets disagree). effort: small (re-spell
  the plant, or correct SAB_DESC and the header). blast radius: one sabotage row, plus the S11 SINGLE-CONTROL wording in
  the design's F3 BUILT bullet if it rests on this row.
- tests/mech/sabotages/S3572_scratch_tail_back_to_heap.sh. The plant replaces `pcrec_scope_sb(&sc)` with a heap local
  but leaves `pcrec_scope_close(&sc)` as the only release, so the tail's storage is never freed on ANY path: every
  compile leaks it (splice_mark runs on every compile, MEMFN mark: 128/128 of my identity compiles; ks marks too).
- Repro: `kit.sh alloc plant:S3572 --sites`: FAIL on W1, W2, W3, W4, W6, W7/W3, each "profiling pass did not succeed
  cleanly (K=-1; ... one that left heap live after pcrec_output_free) -- cannot sweep"; `FAIL: alloc_check: 6
  witness(es) misbehaved`. LSan would see the same leak. Compare `plant:Vo` (S12 on the heap, storage adopted, so no
  normal-path leak): every witness PASSES, so S12 really is single-control; and `plant:Vnb`: 12 stranded-heap trials
  (W1 N=2532, W2 N=20, W3, W4 x7, W6, all at sb.c:64), so S10 has its dynamic witness.
- So SAB_DESC ("only tests/core/scratch_builder_check.py (core arm) sees it, S11 has no dynamic witness") is false for
  this plant, and the plant does not model the class the row names ("a refusal while it is live strands it"): it models a
  plain leak that any leak check catches. The faithful pre-F3 shape (heap tail plus its hand `pcrec_sb_free` before the
  close, two edits) strands only inside the window; whether a witness then reaches it is SUSPECTED no (csb's doubling
  capacity means no realloc fails inside the window; would be confirmed by an alloc run on that plant, which I cannot
  build under the no-make rule).
- Fix: plant the faithful shape (SAB_COUNT 2: the heap local and a `pcrec_sb_free(tail);` before the close), or keep this
  plant and correct the description to "the scanner and alloc_check's profiling pass both see it".

## PROBED-AND-HELD


1. THE ONE QUESTION, traced by file:line and held for all three scopes:
   - Registry: `pcrec_scope_open` (arena.c:113) pushes a MARK; `pcrec_scope_sb` (arena.c:194) pushes a STRBUF record
     (`rec_take` calloc, then link; a failed calloc links nothing); `pcrec_scope_close` (arena.c:138) checks L1, releases
     down to the mark, restores `prev_open`, post-checks `top == below`. `release_strbuf` = `pcrec_sb_free` (frees NULL
     after an adopt). Unwind (arena.c:217) closes innermost-first; `pcrec_arena_free` (arena.c:279) releases whatever is left.
   - Normal return: S10 memfn_stamps.c:371-381 open, build, adopt, close; S11 :255-262; S12 part_layout.c:604-650 adopt,
     `layout_bytes = 0`, close. Each record released exactly once at its close. Early returns (splice_mark :249, render_buf
     :598, target_headers :343) all precede the open.
   - Refusals inside the window: nomem in puts/printf/putc (sb_grow keeps the old pointer in `sb` on a failed realloc,
     sb.c:63-66), nomem of either `rec_take`, the four `pcrec_ctx_fail`s in render_buf (:622, :627, :638-641), the adopt
     guard (sb.c:493, before any move), csb's ladder `abort_over` in splice_mark's appends, `stamp_lines`' arena alloc
     (pcrec_sb_upper; legal under L3, opens no scope, takes no hold). All longjmp to compile.c:2578, whose FIRST act is
     `pcrec_scope_unwind(&cx.arena)` (2583): the STRBUF record frees the partial storage, then the mark. No path frees it
     twice: after an adopt `src->p = NULL` (sb.c:502), and a refusal before the adopt leaves dst untouched.
   - LIFO: no other scope is open on `cx->arena` at these calls. The six openers (grep): minimize.c:84, mod_uprops.c:296,
     clskit.c:1130 each open and close inside their own function, earlier in the pipeline; the three F3 sites are called
     only from compile.c:3430 (`pcrec_memfn_stamps_render`) and :3693 (`pcrec_part_layout_render`) at attempt top level;
     ks_stamps_render's `line` is an arena scratch builder, not a registry record. The two render_buf calls (csb, hsb) and
     the up-to-three splice_mark calls are sequential, never nested.
   - Nested compiles: a walk part (compound.c:184) runs its own compile_driver with its own Ctx/arena/setjmp; its S11 scopes
     are on the inner arena and closed (or unwound by the inner handler) before it returns; S10 opens nothing in a part
     (0 marks), S12 is skipped (`unrendered`). The outer `pcrec_arena_hold` (compound.c:183) runs with no outer scope open.
     The lent `pf->into` copy (compile.c:3742, K163) runs after the inner scopes are closed, so F3 adds nothing to K163's
     strand.
   - Success path: `pcrec_scope_check_closed` (compile.c:3747) precedes the takes; none of the three can be open there.
   - count_groups (compile.c:3913) and the syntax_dump probes never reach the gen sites (LIFE-2).
2. Emitted C identity BASE vs SUBJECT: 128 of 128 pattern x flag pairs byte-identical (.c and .h; 256 compiles + 7 pairs
   both refused identically for `\b`), 20 compiling patterns (21 tried) over 12 flag sets (default, -fmemfn-simd, =x86-64-v3, --part-layout=
   prefilter:inline, --part-inline-rank=measured, --emit-main, -e utf8, -i, combinations). Reach: S11 in all 128 (MEMFN
   mark), S12 in 40 (artifacts carrying `PART_LAYOUT` stamps: render_buf ran its stamp branch), S10 in 60 (a target
   region, the header render's non-empty path). `Pattern:` headers checked per file. Largest/most nested witness:
   `((a|b)(c|d))+e` and `^(?:foo|bar)baz.*qux$` under `-fmemfn-simd=x86-64-v3 --part-layout=prefilter:inline`.
3. alloc_check `--sites` (4 runs): subject all 8 witnesses PASS, no stranded heap, W6 1014/1057 (the pin holds);
   plant:Vnb strands (12 trials, sb.c:64): S10's window is dynamically witnessed and the subject's scope closes it;
   plant:Vo passes everywhere: S12 is SINGLE-CONTROL as the design says (D-8); plant:S3572 see LIFE-3.
4. Stated facts: "None of the three is reachable from `pcrec_facts_force_all`" HOLDS: the only caller is compile.c:3695,
   after both renders, and FIT_FORCE_NEXT's `goto facts_force` (compile.c:2621) lands at :3694, after them; REGISTRY-1's
   trigger has not fired. "The close frees an empty buffer and nothing is copied" HOLDS for nb and o (sb_adopt moves the
   pointer; the close's `pcrec_sb_free` frees NULL); for `tail` the close frees real storage, which the design does not
   claim otherwise.
5. SIBLING OF A FAMILY: `pcrec_sb_adopt` has exactly the two F3 callers; no `StrBuf x = { .cx = ... }` heap builder
   remains on the compile-path layers (the one match, emit_compound.c:67, is the ALLOWed non-owning view). The remaining
   whole-artifact rewrite, `pcrec_sb_render_prefix` (sb.c:803), allocates exact-size and swaps with no refusal between
   the allocation and the swap: not the same shape, safe. Remaining hand-kept members are the design's own S15 scanedge
   (F5, ALLOW row "ten temporaries"), S7 memo and S4 job_cleanup (ruled NOT TAKEN): no unlisted sibling found.
6. GENERAL FORM: S10 and S12 are "open; scope_sb; build; adopt into a Job buffer; close" (4 lines each); a
   rewrite-then-adopt helper would need a builder callback and saves two lines per site. Not worth it now (D77). TRIGGER:
   a third whole-artifact rewrite of a Job buffer with a refusal inside its build (render_prefix does not count: no
   refusal window). UNLOCK it would bring: the scanner could require that every `pcrec_sb_adopt` source is a scope entry
   (today nothing checks an adopt's source is registered; a heap source would be caught only by the generic StrBuf-object
   shape).

CRITIC COMPLETE
