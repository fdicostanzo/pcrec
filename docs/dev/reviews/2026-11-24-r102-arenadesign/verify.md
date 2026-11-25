# verify.md (r102 arenadesign) — INLINE by the coordinator (skill §6.2: every CONFIRMED item is a quote claim or a hand-run over the design text)
Review tree F = 88bb21d73 (worktrees/crit-arenadesign).

- PREMISE-1 / COSTPEAK-4: HOLDS. `grep -n -E 'keyseen|for \(;;\)' src/opt/minimize.c`: malloc :132, free :148, refinement loop :151.
- SIM-3: HOLDS. src/core/sb.c `pcrec_sb_free` resets only p/len/cap (sb_unstore; p NULL; len = cap = 0); design step (1) states no zeroing of a reused record.
- SIM-4: HOLDS. compile.c:3739-3744 takes out_c/out_h/out_ir and moves them into `out` before the success `job_cleanup` at :3745; a refusal placed "before the success job_cleanup" strands them.
- SIM-5 / UNL-6: HOLDS. sb.c channel users outside sb_grow/pcrec_arena_alloc: :228 sb_simd_fail, :473 pcrec_sb_take (sb_nomem), :793 render_prefix (sb_nomem); design step (1) record malloc "diagnoses through a->cx" bypasses both counted sites.
- SIM-6: HOLDS. compound.c:184-192 rc[i] = part_compile(...); a4_parts_dfa (:234-237) returns false on rc != 0, so the row declines and the compile succeeds; alloc_check.c:1034-1037 W6 pins `504, 982, 0` with "a refused part compile leaves the plain artifact". K163.md: today "outer compile is diagnosed".
- PREMISE-6 / COSTPEAK-1: HOLDS. compile.c:3735 `pf->memfn_forms = pcrec_sb_fragf(pf->into, ...)`; compound.c:182 `into = &w->cx->arena`; :183 `pcrec_arena_own_slot` (arena record).
- UNL-7: HOLDS. src/gen/memfn_sites.c:210-212: one binder, `ma->u = &cx->arena; ma->alloc = pcrec_memfn_arena_alloc;` (the design's path says memfn_sites.c, it is under src/gen/).
- CONFORM-3: HOLDS (rule part). tests/core/alloc_inject.h:28 "NOTHING UNDER `src/`, `cli/` OR `lib/` IS EDITED"; T1 puts a hook in pcrec_arena_alloc. The cost part rests on the critic's callgrind counts (32,951 arena allocs for W4), not re-run.
- CONFORM-7: HOLDS. scratch_builder_check.py:82-85 lists the heap mechanisms' own ALLOW rows (sb_store, sb_grow, pcrec_sb_take, pcrec_arena_alloc); the registry's record malloc and in-record StrBuf/Arena are new members of the same shapes.
- SIM-1, SIM-2, CONFORM-2, SIM-8, UNL-1, UNL-2/PREMISE-2, UNL-3: hand-runs over the design's own text (Scope = {a, mark, depth}, mark a record pointer, spare reuse; check `s->depth != a->depth`; pcrec_arena_free's stated order). Re-read by the coordinator against §API and §Discipline: HOLD as stated (each is a property of the text, the build may choose otherwise).
- COSTPEAK-2: HOLDS (valgrind massif documents `--peak-inaccuracy`, default 1.0%).
- REFUTED: none. Not verified: CONFORM-10's "0 of 3 profiles" for static functions (inlining; the critic says so).
VERIFY COMPLETE
