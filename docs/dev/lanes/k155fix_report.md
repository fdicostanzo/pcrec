# k155fix report: K155 in its general form (the census, the small builders, the guard)

Lane k155fix, opus, 2026-11-24. Branch `lane/k155fix`, branched from main `01171dfee`. Rulings applied: R-1, R-2 and R-3 (`docs/dev/lanes/k155fix_rulings.md`).

## Summary

The owner gave the build go for "clean up on exit", in its general form. R-3 then narrowed what this lane lands. It lands four things:

1. **The census.** It lists every builder that is live when a refusal's longjmp happens. Builders without a `Ctx` are classified too.
2. **The small builders, fixed through one helper.**
   - 23 compile-path fragment StrBufs now use `pcrec_sb_scratch(Arena *)`. A scratch StrBuf lives in the arena, so a refusal strands nothing.
   - compound's part texts are handed to the compile arena with `pcrec_arena_own`. This is a two-step ownership record: the slot is taken before the heap block exists, and the link step allocates nothing.
3. **A guard with two independent halves.**
   - `tests/core/scratch_builder_check.py` is a static census in `make test` (test-core). It has sabotage rows S3570-S3572.
   - `tests/core/alloc_check.c` gains a dynamic **stranded-heap property** in `make test-alloc`. A refusal that leaves live heap now FAILS, even when it was diagnosed.
4. **Docs.**
   - known_issues K155 status;
   - the plan row `[K155-STAMPS-LEAK]`;
   - a correction to coding.md 1.6;
   - the testing.md note;
   - the CLAUDE.md entries.

**K155 stays OPEN (R-3).** Three whole-artifact rewrites stay on the heap:
- `target_headers_render`'s `nb`, which is K155's own site;
- `render_buf`'s `o`;
- `splice_mark`'s `tail`.

In the compile arena these raised peak heap by 7-12 % (measured, below). Their fix is the owner's scoped arenas, `[ARENA-SCOPES]`. Two other sites are listed as that row's first clients: `minimize.c`'s tables and `clskit.c`'s private arena. All five appear in the guard's allowlist by name, and the K155 site is also a filed stranding in alloc_check.

The emitted bytes do not change, and the refusal set does not move (Validation).

## Census

The question for each builder: is it a malloc-backed builder, live while something can reach `pcrec_ctx_fail`/`pcrec_ctx_nomem`, inside a compile?

The method had three parts:
- a grep of every `StrBuf` object, private `Arena` and raw heap call under the compile-path layers (src/core, enc, parse, ir, facts, opt, gen);
- a read of each site;
- a check with `alloc_check`'s stranded-heap property. It fails every allocation of the W1-W4 witnesses in turn and reports the live heap after each refusal. Before the fix it found strandings on W1, W2, W4 (sb.c StrBufs) and W3 (minimize.c).

| class | site (file:line, function) | evidence | disposition |
|---|---|---|---|
| LEAK, fixed | src/facts/facts.c:740 pf_hex; :791, :812, :846, :859, :882, :912 pcrec_fact_render (7) | local heap StrBuf live across `pcrec_ctx_*` callees | `pcrec_sb_scratch` |
| LEAK, fixed | src/gen/emit_dfa.c:1168 emit_req_handoff_rest `round`; :3675 residual_sites `loop`; :5376 scan_set_text `b`; :8059 emit_req_landmark_move `round`; :13248 scan_test `c` | the same; also live across the ladder's scratch-bound abort (csb/vmsb `abort_over`) | `pcrec_sb_scratch` |
| LEAK, fixed | src/gen/emit_vm.c:12751 vm_var_emit_eval `lit` | the same | `pcrec_sb_scratch` |
| LEAK, fixed | src/gen/known.c:723 pcrec_cover_listing_cells; src/gen/memfn_sites.c:1026 pcrec_memfn_span_site `fb` | the same | `pcrec_sb_scratch` |
| LEAK, fixed | src/gen/memfn_stamps.c:313 ks_stamps_render `line`; :343 target_headers_render `lines`; :406 pcrec_memfn_stamps_render `lines` | stranded at sb.c under alloc_check W1/W2/W4 | `pcrec_sb_scratch` |
| LEAK, fixed | src/gen/part_layout.c:547 stamp_value `v`; :679 pcrec_part_layout_facts `rows` | the same class | `pcrec_sb_scratch` |
| LEAK, fixed | src/core/sb.c:692 sb_stampv `v`; src/core/varexp.c:312 pcrec_varexp_render `b`; src/parse/mod_callouts.c:67 co_echo `b` | the same class | `pcrec_sb_scratch` |
| LEAK, fixed | src/core/compound.c walk_part `w->out[i].c_src` (the part compiles' heap outputs) | heap texts live across later part compiles and shell emission; previously freed by job_cleanup's hand list | arena-owned (`pcrec_arena_own_slot` before the part compile, `pcrec_arena_own` on rc 0) |
| LEAK, [ARENA-SCOPES] client (R-3) | src/gen/memfn_stamps.c:363 target_headers_render `nb` (**K155**) | LSan witnesses (known_issues K155); alloc_check W1-W4 strand 16 KB at sb.c under this function | stays heap; guard row `strbuf:nb`; alloc_check filed stranding narrowed to this function |
| LEAK, [ARENA-SCOPES] client (R-3) | src/gen/part_layout.c render_buf `o`; src/gen/memfn_stamps.c splice_mark `tail` | whole-artifact rewrites, the same class; no alloc_check witness reaches them | stays heap; guard rows `strbuf:o`, `strbuf:tail` |
| LEAK, [ARENA-SCOPES] client (R-1/R-2) | src/opt/minimize.c pcrec_minimize_dfa (7 heap tables) | alloc_check W3: tables live across arena allocations (OOM only) | filed; guard row; alloc_check filed stranding |
| LEAK, [ARENA-SCOPES] client (R-2) | src/gen/clskit.c:1126 pcrec_clskit_emit_kit private `Arena a` | never registered on the Ctx; its blocks strand on a refusal | listed, not fixed; guard row `arena:a` |
| heap, never live across a refusal | src/opt/scanedge.c pcrec_scanedge_dfa (10 temporaries) | no arena/ctx call while they are live; each own-allocation failure frees first | allowlisted |
| heap, Job-owned | src/ir/nfa.c nst; src/ir/dfa.c intern, tab_grow; src/opt/dfamemo.c pcrec_build_min_dfa | realloc'd in place on Job structures that job_cleanup frees; dfamemo attaches `st` to the Job's Dfa before any further allocation | allowlisted |
| outside a compile (no Ctx, errors by return) | src/gen/emit_subst.c support_unit, pcrec_emit_subst; src/core/compile.c pcrec_subst_compile `Arena a`; src/parse/rxt_source.c (4 StrBufs, heap); src/parse/ks_analysis.c analysis_write_canonical, analysis_write_decoded | no longjmp can reach them | allowlisted by name |
| outside a compile | src/dump/* | not a compile-path layer (renders after the pipeline) | out of scan scope |
| not a builder | src/gen/emit_compound.c part_splice `t` | a non-owning view for `pcrec_sb_splice`, never grown or freed | allowlisted |

**A diagnosed non-OOM refusal with a live builder.** The census found none that a pattern can reach. The non-OOM windows are:
- internal errors (render_buf's mark checks, target_headers pass 1, compound's slot check);
- the size ladder's scratch-bound abort (`abort_over` on csb/vmsb), which crosses while a local builder is live.

Ladder probes on the pre-fix ASan CLI showed no leak. Even so, the ladder window is exactly the one the scratch conversion closes for the small builders.

**A further finding, not fixed and listed for [ARENA-SCOPES].** In a nested part compile, `pf->memfn_forms = pcrec_sb_fragf(pf->into, ...)` allocates into the PARENT compile's arena. An OOM there longjmps to the parent's setjmp and strands the nested compile's Job. This is a cross-compile leak class, distinct from K155.

## Fix

The one general helper for StrBufs is `pcrec_sb_scratch(Arena *a)` in src/core/internal.h. It takes an `Arena *`, so a scoped arena can be passed later (R-2).

- `StrBuf.ar` selects where the bytes live, through `sb_store`/`sb_unstore` in src/core/sb.c.
- A scratch builder grows by a fresh arena block and a copy.
- `pcrec_sb_free` on a scratch builder only drops the pointer.
- `pcrec_sb_take` of a scratch text copies it out to the heap. A scratch text that only has to outlive its function needs no take.

Heap results go through `pcrec_arena_own_slot` / `pcrec_arena_own` (src/core/arena.c). `Arena.owned` is freed by `pcrec_arena_free` before the arena's blocks. Compound's part texts use it, and `job_cleanup`'s hand-kept free loop over `comp_shell->text[]` is deleted.

Reverted by R-3: the Job rewrite buffer (`Job.rwsb`, `pcrec_sb_move_text`) and `pcrec_sb_replace`. The three whole-artifact rewrites and `clskit.c` are byte-for-byte main's code, apart from a guard comment and clskit's initializer, which is designated now because `Arena` has a third field.

## Guard

**Static census: `tests/core/scratch_builder_check.py`**, run by `tests/core/run_core_tests.sh` (test-core).

What it scans:
- every compile-path .c file, with comments and literals blanked;
- three shapes: a StrBuf object not built by `pcrec_sb_scratch(`, a private `Arena` object, and a raw malloc/calloc/realloc/strdup/strndup/realpath call.

Every hit FAILS unless an ALLOW row names its file, its function and, where needed, its OBJECT (`strbuf:nb`, `arena:a`), with a reason. The name-narrowed rows exist so that a second heap builder planted beside an allowlisted one is still caught (S3572). The rows group into:
- the [ARENA-SCOPES] clients;
- the cx-NULL sites;
- the Job-owned arrays;
- the heap mechanisms.

It also checks the other half of the rule: every StrBuf field of `Job` is freed in `job_cleanup`.

Its controls:
- self-test fixtures (9 must-flag, 8 must-pass);
- stale allowlist rows FAIL;
- floors of 45 files and 12 scratch builders, about half of today's 91 and 23.

Today: 91 files, 23 scratch builders, 24 allowlisted sites, 6 Job buffers, 0 findings. Red-direction control: on main's `01171dfee` source it reports 24 heap-builder findings (the census list).

**Dynamic property: `tests/core/alloc_check.c`**, run by `make test-alloc`. This is the independent control; it shares nothing with the scan.
- `alloc_inject.h` now redirects `free` as well.
- The child keeps a live-block table and a live-byte balance.
- A diagnosed refusal that leaves live heap FAILS ("STRANDED HEAP"), and the profiling pass must end at zero live heap.

Filed exceptions live in `known_stranded`. Each must be REACHED, or it FAILS as stale. A row can be narrowed to blocks allocated UNDER one function: `backtrace()` is recorded only for sb.c blocks and symbolized with `addr2line -i` only for stranded ones, because every StrBuf's storage comes from sb.c and a file-only row would excuse them all.

Today: minimize.c reached in 8 trials; K155's `target_headers_render` reached in 20 trials across W1-W4. Positive control: with the three rewrites back on heap and no filed row, the property FAILED W1-W4 at sb.c:64 ("16392 bytes still live").

**Sabotage rows (core arm).**

| row | plant | what catches it |
|---|---|---|
| S3570 | emit_dfa `round` respelled as a heap `{ 0 }` | the strbuf finding |
| S3571 | job_cleanup's `irsb` free dropped | the Job-field check |
| S3572 | target_headers_render's `lines` made heap, beside the allowlisted `nb` | the name-narrowed row |

All three were hand-checked against the guard before queueing (each FAILS with exactly its finding). Mech verdicts: Validation.

## Validation

Done, with verdicts read by the lane:
- `make -s strict`: clean.
- `make -s test-plan-lint`: 2 of 2 checks passed.
- `bash tests/core/run_core_tests.sh`: 9 of 9 checks passed, including the new `scratch_builder_check`.
- `make alloc` (= test-alloc's body): rc 0, 10 checks passed. The two filed strandings were reached: minimize.c in 8 trials, and `target_headers_render` in 20 trials across W1-W4. With the three rewrites back on the heap and no filed row, the same run FAILED W1-W4 (the positive control).
- Emit identity, `200-k155fix-sweep` (`scripts/emit_sweep.py --ref 01171dfee`): GREEN, rc 0.
  - Movers: 0 in every stream: c-default, c-vm, emit-ir-vm, facts, emit-ir-auto (all three prefilter arms), stderr, composition and dumps.
  - Population: 7599 argv rows and 468 composition files.
  - The binary it ran predates the two comment-only commits that followed; the object code is the same.
- Peak heap, small locals only (R-3): a 60-compile sample over the full peak driver (alloc_inject.h live-heap accounting, main `01171dfee` vs this tree).
  - Total: +0.003 %. Every compile moved by +48 B, a constant per compile.
  - The noise is 0 B: the measurement is deterministic, and three repeated runs of the same driver gave identical output (md5).
  - The full corpus + cells run is owed below.
  - For comparison, before R-3, with the three whole-artifact rewrites also on the arena: +7-12 % (R-2 STOP).

Owed (box queue). Every job carries refuse-after 2026-11-24 19:30 (exit 77 after it):
- `k155fix-codegen`: `make test-codegen`.
- `k155fix-mech`: rows S3570 S3571 S3572 on the core arm. Each must be DETECTED.
- `k155fix-mg-peak-1`, `k155fix-mg-peak-2`: `memgate.py peak`, the full corpus + every non-red growth cell, uncapped, before vs after. Read `LARGEST-ABS`/`LARGEST-REL` and the total line in each job.log.
- `k155fix-mg-rungs-1`, `k155fix-mg-rungs-2`: `memgate.py rungs`, every growth cell at every LADDER rung, before vs after. Read the `rungs: VERDICT IDENTICAL|MOVED` line.
- `k155fix-asan`, `k155fix-ubsan`: `make asan`, `make ubsan`.

Scratch tools for the memory gate: `$PCREC_TMPDIR/scratch/k155fix/tools/` (memgate.py, peak.c, peak_before/after, gdrv_before/after). The outputs go to `.../k155fix/mg/`.

## STATE AT HANDOFF

Last ruling applied: R-3 (the last entry in k155fix_rulings.md). Branch `lane/k155fix` is committed.

DONE:
- the census;
- the 23 scratch builders and compound's arena ownership;
- the guard: the static check plus the alloc_check stranded-heap property;
- sabotage rows S3570-S3572 (hand-checked);
- docs: K155 PARTIAL/OPEN, the plan row, coding.md 1.6, testing.md, the CLAUDE.md entries, the lanes history index;
- strict, plan-lint, core, alloc and the emit sweep: all green.

Not filed: a separate [MINIMIZE-ARENA-LEAK] row (R-1). [ARENA-SCOPES], filed after R-1, already names minimize.c as a client, so a second row would duplicate it. The alloc_check filed row cites [ARENA-SCOPES].

OWED (box queue; the manager reads the verdicts): k155fix-codegen k155fix-mech k155fix-mg-peak-1 k155fix-mg-peak-2 k155fix-mg-rungs-1 k155fix-mg-rungs-2 k155fix-asan k155fix-ubsan.

What each verdict decides:
- codegen red, or any mech row UNDETECTED: a fix lane.
- mg-peak above noise (any compile over the +48 B constant): STOP per R-3. Name the site from LARGEST-ABS.
- mg-rungs `MOVED`: STOP per R-1.
- asan red: check whether its only leak is the K155 site (expected: still OPEN) before calling it a regression.
- ubsan red: a fix lane.

STILL TO DO after a green queue (the follow-up agent):
1. `scripts/cloudrun --owner main --kind test --name k155fix --ref <tip sha>`;
2. `scripts/cloudrun --owner main --kind growth --name k155fix --ref <tip sha>`;
3. prove both with `git ls-remote origin 'refs/heads/cloud/main/*/k155fix*'`.

The growth run's library stage will still show K155's leak (open by R-3).
