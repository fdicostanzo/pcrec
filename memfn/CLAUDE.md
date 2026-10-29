# memfn/ — pcrec-memory-functions, the in-tree search-code kit

[MEMFN] (docs/dev/plan.md; D146 delegation, D147 layers + addenda 1-16, D149, D155, D157, D165, D166, Q36). pcrec describes a search SITE (`mf_site`: operation over a predicate, proven facts, hooks); the kit returns the C text for it and owns EVERY choice inside the site (scalar forms, SWAR, libc calls, ISA arms). pcrec does no cost comparison and carries no architecture knowledge. Stand-alone it is also a product (K3: CLI + reference functions); pcrec's requests come first.

## Standing rules

## The layers (D147)

- Layers (D147), binding on every kit change: ONE SIMD switch, `-fno-memfn-simd`/`-fmemfn-simd` (axis `memfn-simd`), OFF by default (default flip = R4f, its own ruled event). OFF = portable C (plain C, SWAR on ordinary integers, libc calls, loop-free forms); ON = hardware-optimized, may not execute elsewhere. ISA levels, forms and run-time cascades are the kit's per-site choice (a cascade only where it beats the single-level form, named with its dispatch cost, K-6). pcrec sends one bit (`MF_P_PORTABLE_ONLY`), plus the sink's `simd_open`/`simd_close` and `mf_pred.rank_*` facts; there is no `portable`/`native`/`baseline` profile and no `--isa=` axis.
- Scalar layer = pcrec's algorithm + the kit's scalar arms (SWAR and libc are scalar, Q50); live, improvable forever; accepted on SIMD-off measurements. SIMD layer must beat the CURRENT best scalar layer; a scalar improvement re-opens the comparison. Every acceptance reading for a change touching searching reports BOTH layers.
- Kit forms obey D149 (integration.md §8.6 K-7): every unroll width, block size, cut-over is measured, derived, left to the compiler, or labelled in place `UNMEASURED DEFAULT:`.
- No frozen baseline: pcrec's pre-migration text is only a per-step byte-identity comparator (shadow comparator, movers-by-ID gate); never a permanent arm, never the SIMD-off arm.
- Every kit change that moves bytes carries its own deny (D144 item 4): a row in `src/options.def`, reached as `--memfn=no-NAME`; add the row in the SAME commit (it is the change's alpha OFF arm). Kit work and pcrec scalar work proceed in parallel.
## The kit's option namespace

- Option namespace (D147 add. 9): pcrec has ONE axis; per-form switches are `--memfn=<opt>[,..]`, carried uninterpreted (`mf_site.opts`); `no-NAME` denies row NAME, bare `NAME` forces it for `MF_OPT_PAIR` rows; kit validates (`mf_opts_check`), refusal text shown unchanged. Registry is the X-macro `MF_OPT(name, kind, budget, layer, doc)` (names kit-owned and arch-blind; kind DENY/PAIR; budget `MF_B_SCAN`/`LOOP`/`ANY`, D91; layer SCALAR/SIMD, SIMD rows inert at `-fno-memfn-simd`); accessor `mf_options(size_t *n)`; printed = parsed table.
- `pcrec --list-axes` prints pcrec's axes then a `memfn` section (`table_contract.md` §4) from `mf_options()`: the ONE enumeration point for `test-axes`, identity gates and the registry check. Its independent control is a floor on the section's member count, pinned as a literal in `docs/spec/`; raise it in the change that adds a row.
- A kit byte move is a pcrec abi event in the SAME commit (Q36; S693 cites this rule): pcrec's abi bump, re-pins (readers found by grep, D76/D94), stamp values, `docs/spec/` hunk where caller-observable (D80), and G1 alpha at both layers. A split commit is a delivery failure. After a migration step, edits to a migrated pcrec emitter are kit work here, not under `src/gen/`.
- Every search site migrates to the kit (Q42 reversed; completeness is a ruled D77 exception); each step zero-mover (R4e'.0b/D155 the one ordered byte move). Memchr ratchet C12 ends at 0 outside the kit; C17 at 0 pending. A byte-moving kit change still needs its measured trigger and G1 alpha at both layers.
- D155: a function that does work never contains `#if`; a selector's whole body may be the `#if` chain, one call per arm.

## Compile-time stack (R-28)

- The kit runs inside `pcrec_compile`, on a caller's thread of any size. Bar: NO kit function has a stack frame over 4 KB; working storage beyond that lives on the heap (or the caller's arena) and an allocation failure takes a loud refusal (`mf_form_hash` -1; `mf_set_terms` -1, which is not a decline). Held by `tests/memfn/run_link_checks.sh` (`make test-memfn-link`), which compiles every `memfn/src` file `-O2 -fstack-usage`.
- PEAK, measured 2026-10-23 (gcc 15.2 x86_64 -O2, `tests/memfn/run_link_checks.sh`'s `-fstack-usage` recipe, re-read at the S3 code review's C1 build): the largest single frame is 3,600 B (`pcrec_mf_form_hash`; next `define_sel` 3,456 B, `wf_parts_prepare` 3,376 B, `wf_parts_check` 3,024 B, `pair_facts` 2,448 B; S3's `fd_find_form` (3,456 B, one `mf_site`) retired for `fd_find`, 560 B, below `define_sel` through `wf_prepare` 720 B and `wf_find_decide` 416 B; `kit_report_exact`'s 3,184 B retired with RPT). The deepest measured kit chain (`mf_form_hash` over both canonical forms, which renders a site through `mf_emit`, and `mf_set_terms` at K=4 on a painted stack) reaches 13.7 KB. Before R-28 the frames were 36,368 B (`mf_form_hash`) and 36,256 B (`mf_set_terms`) and the same chain reached 47.1 KB. Re-measure if a recursion or a fixed table is added (`dfs` recurses at most `MF_SET_K` deep at 1,376 B a level).

## The boundary with pcrec

- Boundary: pcrec's sources reach the kit ONLY through `memfn/include/memfn.h`; the kit links nothing from `src/`, `cli/`, `lib/`. Generated artifacts never depend on the kit (only TEXT reaches them). pcrec->memfn carries facts only (D157).
- Stamps (both on every artifact, born R4a'; neither carries a kit version): `<PREFIX>_MEMFN_FORMS` is `none` iff identical to the SIMD-off compile, else the forms used with carried levels; `<PREFIX>_MEMFN_LIBC` lists libc functions the search code calls (Q53 spelling).
- Ownership split (see integration.md): pcrec owns WHICH sites are delegated (`DELEG_SITES`, by semantic operation, never cost), the predicate's facts, SIMD switch state, the CHECKED SITE MANIFEST (`tests/memfn/site_manifest.tsv`, C17: every search site `delegated` or `pending`), hook text, G1 timing, knowledge keys of the regime table + `docs/design/regime_tables.md`, the MEASUREMENT SET format/loader/store/stamp ([MEASURE-SET], D166), the mover census, official verdict (pcrec-bench, D144 add. 4). The kit owns site code, plan/form/fallback, own tests (G2) and timed control (K-5), the REGIME TABLE and its pick function, set values and method, the evaluator [REGIME-EVAL] (`regime_eval.md`) and [REGIME-TWIN]. Kit timings are unofficial.
- Symbols: every external symbol via `MF_NS(name)` -> `pcrec_mf_name`; internals `static`; libpcrec exports only `pcrec_`-prefixed names (C15).
- Licence: 0BSD for the kit's text (`LICENSE`, D145); text translated from Rust `memchr` takes its `Unlicense` arm; MIT/BSD/Apache text is ideas-only. Every source file whose text can reach an artifact carries an SPDX line + provenance header (C16); `PROVENANCE.md` maps file -> source -> licence -> derivations.
- MF_SITE_ABI / MF_VOCAB / MF_CLASS_V changes are kit-contract changes: record in memfn/docs/journal.md and the request/response ledger; state facts (an UNSTATED zero is refused), no byte moves unless the abi rule above is met.
- Process: requests = `docs/requests.md` (ONLY writer: pcrec manager, single-file `[requests]` commit on main; a request is on main before its lane is briefed); responses = `docs/responses.md` (ONLY writer: kit session, single-file `[responses]` commit on the kit branch, merged by the manager) (D78). Kit journal `docs/journal.md` (append-only); pcrec's `docs/dev/dev_journal.md` gets a line when a kit change merges. A kit session works in its OWN worktree under `worktrees/`, never merges to main (`/pcrec-memfn-manager`, `docs/wake.md`). Kit lanes are ordinary pcrec lanes (`docs/dev/lanes/BOILERPLATE.md`, one heavy suite at a time, Linux verdicts only, D144 add. 1).
- Standing design questions for every kit design (docs/design/CLAUDE.md): (1) name the measurement regime (throughput vs per-call, hit-dense vs sparse, compiler, box); a choice must hold in every regime its site can be in (K-1); Linux, `taskset`-pinned, calibrated loops, absolute deltas against a floor. (2) independent control: G1 is pcrec's timing vs its own deny with population from a pcrec-side artifact diff (never the kit's `moved`); G2 checks against the scalar byte loop and a GENERATED predicate space. (3) regenerating the kit's measured data (`data/*` with `generate.py`) that moves a byte is a pcrec abi event (integration.md §21.3).
- Slot runs of the full suite: `scripts/perfrun --label NAME -- LOGFILE`, not a raw `make -k -jN -Otarget test`; read a red with its `LOGFILE.perfrun` note first (K44-ONLY and LOAD-SUSPECT reds are re-run solo per section). See BOILERPLATE.md, docs/dev/ttune_measurement.md.
- Checks: `make test-memfn-g2` (quick, a `make test` section), `make test-memfn-g2-full` (opt-in), `make test-memfn-finder` (incl. `tests/memfn/proven_check.c`, `run_proof.sh`, `prov_check.c`), `tests/memfn/run_link_checks.sh` (C15/C16).

## Files

- README.md — stand-alone pitch, licence, status.
- LICENSE — 0BSD.
- docs/ — ledger pair (requests/responses), journal, session wake template (own CLAUDE.md).
- PROVENANCE.md — file -> source -> licence -> derivations, one row per file under include/ and src/.
- include/memfn.h — the one header pcrec includes.
- src/ — composer, generic scalar row, K1 reference functions, `options.def` and accessor/parser, finder table (`finder.c`), presence ports (`presence.c`), terms/mask rows, vrun SIMD rows (`vrun.c`, `levels.def`), the standalone find-any kernel (`vany.c`, not routed), mismatch renderer.
- tests/ — G2, the kit's own tests.
- data/ — measured data: method cards (`data/cards/`), measurement sets (`data/sets/generate.py`). Own CLAUDE.md.

## Pointers

`docs/design/memfn/integration.md` (rev 4.9; read §R4.9, §R4.8, §R4.7 first; §22 skeleton), `setfind.md`, `r17b_prime.md`, `regime_eval.md`, `docs/design/kit_proof.md`, `docs/design/regime_tables.md`; decisions D144-D166; lane reports `docs/dev/lanes/*_report.md`; memfn/docs/requests.md and responses.md.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/memfn.md
