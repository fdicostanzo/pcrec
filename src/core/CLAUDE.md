# src/core — pipeline driver and memory management

Home of the compilation pipeline driver and shared utilities: arena allocator for AST/IR, growable string buffer for codegen output, shared type definitions (`internal.h`), longjmp error handling, the knowledge/findings seam, the code-point set, case folds, and the declared tables (`*.def`).

## Standing rules

Maintenance: update this file when files are added/removed or their roles change.

- All dynamic allocations for AST/IR go through `pcrec_arena_alloc()` and are freed together; `StrBuf` accumulates generated code; error paths longjmp to `cx.jb`. `internal.h` is NOT installed; it is internal to `src/`.
- pcrec is a LIBRARY: never `abort()` on the caller's process (K7). A failed malloc calls `pcrec_ctx_nomem()` (Arena and StrBuf carry a `Ctx *cx`; NULL is legitimate only for `StrBuf`s outside a compile, e.g. `src/dump/syntax_dump.c`). Realloc into a temporary. Builders that can be interrupted by `pcrec_ctx_fail` must be arena-backed (no malloc builders: they leak on every diagnosed pattern).
- `compile.c` holds the tree's ONLY `setjmp`. `compile_driver` is a bounded retry loop (`COMPILE_MAX_ATTEMPTS`, [SEL-1]); a retry is one more input bit on a fresh `Ctx`, never a second local recovery point; `attempt`/`dfa_disabled` stay `volatile` (`-Wclobbered` under `make strict`). Cross-attempt state is plain `Ctx` fields, not arena text (the arena is freed by `job_cleanup`).
- `pcrec_compile` and `pcrec_emit_ir` (and `pcrec_compile_defs`/`--source`) are thin callers of ONE `compile_driver`; never fork a second driver (a listing from a second driver describes a compile that never happened; `--emit-ir` runs a real compile).
- Pass order is load-bearing: `parse -> altcls -> discharge_atomic -> callgraph -> select_engine -> postresolve`. `callgraph` runs after every pass that REBUILDS nodes (it is the only writer of `u.call.body`); engine selection runs after it (linkage decides VM-only). `compile.o` must name no `rxt_*` symbol (`Ctx.compose` hook, set only by `compile_defs.c`).
- Fit/size-cap ladder: `fit_rungs[]` (and T3 `pflw_rows[]`, T4 `st_whys[]`) is the ONE first-match dispatch; no rung tests `--size-cap=refuse` itself, `fit_rung_denied` is the one predicate (degrading column); every row states its cells (0 = UNSTATED); the build gate reads `Ctx.anchored_dropped` (the row FIRED), not a rung ordinal. `docs/spec/limits.md` §8.4 is the contract incl. the classification table. A new contributor rung on the VM side forces a MEASURED order (D77). "Optional" is a claim about every resource a component spends (K53): charge/drop optional machines at the point the cap is charged.
- Any optional machine (`build_anchored_dfa`) is built LAST, OPTIONAL (overflow is a selection outcome, not a diagnostic), with the engine overflow record saved/restored, and skipped for a VM hybrid. `--engine=vm` never builds the DFA pair (independent derivation).
- Raise-only caps share one table (`cli/main.c` `raise_only_limits[]`, `defo.max_*` 0 = default); clamp a raised value that exceeds an `int` parameter.
- `tune.c` is DATA in one file; sites ask it. Em-dash sentinel is 0 and each site resolves it against its OWN default; position 0 (`balanced`) stays a structural no-op (all sentinels, empty deny mask; `tests/codegen/run_tune_dial.sh` §2); a position is REFUSED if invalid, never clamped; applied in exactly three places (`compile_driver` validation + deny OR, `size_term_choose`/ladder trigger, `emit_vm.c` AUTO rung). `-fno-anchored-dfa` stays ABSENT from `min-size`. Contract `docs/spec/tuning.md` §5; D103.
- `axes.def`, `ctxfn.def`, `part_layout.def`, `limits.def` are X-macro single sources: a row names a macro token, never a copy of a bit value; they are Makefile prerequisites of every object; derived consumers (`cli/main.c`, `axes_dump.c`, `--list-axes`, part-layout parsers/stamp) read them, no hand-kept parallel spelling. `pcrec_axis_on(flags, deny, force)` resolves deny, force, then the row's declared default. Retired bit 45 (`-fno-req-set-lead`) is rewritten by the driver to the kit's `no-pres-set-lead`; header macro kept as alias.
- Flag-word reads go ONLY through `pcrec_flags_has/_opt_has/_flags_masked/_flags_without` (FLAG-ACCESS-BEGIN/END block in `internal.h`); writes (`|=`, `&= ~`) stay raw. `compile.c` static-asserts every deny/force key is a single bit. Gate: `tests/core/flag_access_check.py`.
- `ctxfn.def` is THE one A_CTX truth table: value DERIVED from the 9-cell grid, `_Static_assert` per row vs the stated hex and CLASS column (`CONTEXT`/`PIN_START`/`PIN_END`); the per-row predicates are COMPUTED from bits, never columns. Checked by CK-8 `tests/assertions/ctxfn_table_check.py` against libpcre2. Analyses that need anchored/pinned switch on `pcrec_ctx_class` with no `default:`.
- `internal.h`: new declarations go in their DEFINING layer's group (core, enc, parse, ir, opt, gen, driver, dump); a reordering keeps the declaration multiset. Per-layer headers split is deferred (not yet needed).
- `struct Ast` is a TAGGED UNION (D70): NO module may add a new top-level per-kind field; a new kind adds a union MEMBER; a field joins the common block only when a survey MEASURES it cross-kind (`not_repeatable`, `reg`, `reg_at` are common). A writer may touch `u.<payload>` only under a kind check that owns it; a generic copy/sanitise helper MUST guard (`rd_node` on `A_REP`, `mod_assertions.c` pin on `A_BOL||A_EOL`). Generic helpers must not FOLLOW `u.call.body` (shared, never owned; use `callgraph.c`'s memoised SCC fixpoint). Zero must be the SOUND answer for any derived field a walker may read before its writer runs (`nonnullable` inverted; `maxw` + `maxw_known`). A field set in a hook for a deferred check is a union member written unconditionally (`u.look.at`). `save`/`nsave` are filled by the emitter (`vm_count_slots`), never predicted elsewhere.
- Node KINDS encode STRUCTURE, node FIELDS encode parse-resolved MODIFIER state (D62); exhaustive switches over `AKind` carry no `default:` so a new kind is a compile error at every deciding pass (`src/opt/mrl.c`). `Ctx.mods` is an incomplete `ParseMods` (only `src/parse/parse_mods.h`): scoped modifier state is resolved at parse time onto the node. Before writing an analysis special-casing `$`, read `u.anch`'s successor comments / the D62 control-3 note in `internal.h`. `Ast.reg` NULL = ANY_ENGINE on purpose (fails unsound-direction, caught by `tests/registry/registry_check.c`'s tripwire); a discharge's output must not inherit the discharged node's stamp. `A_CAP` is born only when `Ctx.want_caps` (D31).
- Adding a `RegKind`: twelve-plus sites, no `-Wswitch` alarm (every RegKind switch has a `default:`); `check_kind_coverage` reads `--list-syntax` output. `PCREC_UNBUILT_MARKER` is shared by ext.c's UNBUILT macro and the classifier docs; built-status is DERIVED, not a column (D65).
- Per-file standing rules for `cpset.c`, `fold.c`, `sb.c` (text layer, gates), `limits.h`/`limits.def`, `findings.c`, `ksrc.c`/`ksrc.h`: moved verbatim to NOTES.md, section "Standing rules: cpset, fold, sb, limits, findings, ksrc details".
- `varexp.c` is a PURE grammar parser: refusals are RETURNED in `VarExpErr`, never raised; it deliberately does NOT evaluate (the evaluator is emitted C, `vm_emit_vars_resolve`); the colon is a `bool` beside the operator. Check `tests/core/varexp_check.c`.
- `compound.c`: every `CompPart` field stated (zero UNSTATED); `pcrec_comp_part_check` self-check refuses unstated/inconsistent; admission is listed conjuncts (`CompConj`); the namespace reservation table `ns_reserved[]` (cli.md §1.6 para 2) refuses `-p` containing `__` and `pcrec_harness_*`; the harness lever is hidden, build/pcrec-harness only. Check `tests/compound/`.
- Part-layout: `pcrec_part_layout_render` runs after size decisions and notes, before the prefix render, except in a spliced part's compile; the three control fields validate with `tune`.
- Changing emitted scaffolding is an `abi` bump + identity-gate re-pin in the same change (D76/D94); changing anything caller-observable updates `docs/spec/` in the same change (D80).

## Files

- `ctxfn.def` — the one A_CTX truth table (ten rows; grid, hex, class, VM forms).
- `part_layout.def` — part-layout vocabulary X-macros (`PL_CLASS/VALUE/RANK/WHY`).
- `axes.def` — optimization-axis table (deny/force tokens, `-fno-X`/`-fX` spellings, default polarity).
- `limits.h` / `limits.def` — every accept/reject/promise number, provenance-tiered.
- `internal.h` — shared types (Arena, StrBuf, Ctx, Job, Nfa, Dfa, Ast union, RegRow vocabulary, VerbName/PosixName tables, ExtPort types, BufSurface, CompPart/PcrecEmitIn, fit/ladder types) and layer-grouped declarations.
- `compile.c` — pipeline driver (`compile_driver`, retry/fit ladder, tune application, composer/tree hooks, compound walk, `pcrec_ctx_fail`, `pcrec_default_options`, `pcrec_count_groups`, `pcrec_compile_driver` exported face).
- `compile_defs.c` — `pcrec_compile_defs` (`--source` composition entry) and nothing else.
- `compound.c` — compound tool parts, admission rows, placement, shell build.
- `arena.c` — zeroing arena allocator (16-byte aligned, 64KB min block).
- `sb.c` — string buffer, comment gate, SIMD/layout brackets, text layer, fragf, stamp writers, prefix render.
- `tune.c` — `--tune` speed-vs-size policy table and accessors (+ part-layout preset columns).
- `fold.c` — ASCII fold partition, Unicode simple fold walker, Latin-1 fold; `fold_tables.inc` generated.
- `cpset.c` — code-point interval set, cube, `pcrec_lit_run`, `A_WCLASS` accessors.
- `varexp.c` — `${...}` expansion grammar parser.
- `findings.c` / `findings.h` — findings seam (rate accessor, PICK/COMPARE/MASS, stamp, store); `findings_store.inc`, `findings_table.inc` generated and committed.
- `ksrc.c` / `ksrc.h` / `ksrc_kinds.c` — knowledge-source module parts and kind table.
- `ks_measures.c` / `ks_measures.h` — measures kind row; `measures.c` — measure store loading/resolve; `measures_store.inc` / `measures_table.inc` generated by `make gen-measures`, committed, never hand-edit.

## Pointers

`APPROACH.md`; `docs/design/utf8_design.md` (§2.2 cpset, §4 folds); `docs/design/subroutines_design.md`; `docs/design/findings/design.md` §6; `docs/design/compound.md`; `docs/design/dec_fallback.md`; `docs/design/ctx_span.md`; `docs/design/measure_sets.md`; `docs/design/compound_entries.md`; `docs/design/variables_common.md`; `docs/spec/limits.md` §8; `docs/spec/tuning.md`; `docs/spec/measures.md`; `docs/spec/findings.md`; `docs/dev/coding_guide.md`; decisions D26, D31, D46, D58, D62, D65, D67, D70, D76, D77, D80, D81, D82, D94, D103, D108, D111/D112, D126, D135, D146/D147, D157. See `src/gen/CLAUDE.md`, `src/opt/CLAUDE.md`, `src/parse/CLAUDE.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/src__core.md

See also NOTES.md in this directory (history, lessons, rationale, moved detail).
