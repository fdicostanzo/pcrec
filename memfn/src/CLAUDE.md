# memfn/src/ — the kit's sources

Built into `libpcrec.a` by pcrec's Makefile (`KITSRCS`, compiled with `KITFLAGS`: no `-Ilib`/`-Isrc`, so nothing here can include pcrec). Every file includes its headers by relative path. pcrec's emitters render sites through the kit (`src/gen/memfn_sites.c`, DELEG_SITES): offset-skip block, pre-check composite, the VM's literal-run compare (VMRUN, runcmp.c), the prefilter find (PF, pffind.c).

## Standing rules

- External symbols go through `MF_NS` (`pcrec_mf_*`; C15), everything else `static`; an SPDX line and a provenance header on every file, with its row in `../PROVENANCE.md` (C16); nothing included from pcrec's `src/`/`cli/`/`lib/`. Scalar-arm provenance lines read `pcrec <commit> (relicensed 0BSD by its author, D145 addendum 1)` (R-4 Q1).
- The scalar arms are the LIVE scalar layer (D147): improvable kit code. Each byte-moving change adds its own `--memfn=no-NAME` deny row in `options.def` in the SAME commit, raises the floor in `docs/spec/registry.md` §6, and — where it moves a pcrec byte — is a pcrec abi event with `tests/memfn/pins/arms.tsv` re-pinned in the same commit. See `../CLAUDE.md` "The kit's option namespace".
- Selection is ONE walk, `kit_walk` (integration.md §R4.9.2.3): per row of the asked slot, in table order: deny, gate, predicate; first match; an empty slot is no selection and records nothing. Arms (`select_arm`), the run compare (`rc_row_of`) and `fn_rows[]` (`fn_select`) all call it. Do not add a parallel walk (finder's `fd_nested_walk` routes to the composer's walk).
- ROW CONTRACTS ([MEMFN-ROWCON], `docs/design/memfn/row_contracts.md`): every arm declares `ct` (`uses`/`serves` with a citation per declaration at the end of the row's own file); the gate ENFORCES (a failing row is declined, a site no row serves is refused naming the fields, `mf_use` re-checks). Each row checks its own contract (K96); unstated fields are refused. Every arm declares `arm.tests` (`ARM_TESTS_EVERY`/`_REQUIRED`/`_UNSTATED`; an UNSTATED FIND row is refused by `mf_define`/`mf_ask`).
- Field/class space: `fields.def` classes and fields are bit sets; classes are FULL at 64 and fields at 64 (a 128-bit `kit_set` since R-26 Zk); a new class/field needs a wider mask. Any site-vocabulary move bumps `MF_SITE_ABI` / `MF_CLASS_V`.
- Vocabulary rules every site must pass live in `site_check` (`pred_kinds`, `rank_ok`, `window_check`, `kit_presence_check`, `kit_proof_check`, `pres_layout_check`); out-of-vocabulary shapes are REFUSED loudly. An UNSTATED `body` is refused (R-23); a PARAM body until B8.
- No tuning constant without a D149 label (derive, measure, or label unmeasured); overlap lengths and width rules are DERIVED.
- Generic row (`generic.c`) is the last row of every table, tests every term, honours `floor`/`n`/`end_back`/empty on every op, reads nothing for an empty range (§R4.7 F1). Its `stmt_advance` is pcrec's in-loop skip text for ADVANCE delegated sites (frozen target tests/memfn/pins/r4h_target/; sabotage S214, S616 anchored on its cap line).
- Finder (`finder.c`): `fd_rows[]` 17 rows (R0, R5, R7 withdrawn at B4', ids reserved); LOCKDOWN: every row decides, no `routed` bit, R7w (the walk) the MEASURED default for every set FIND; a key ABSENT from the measurement set does not hold (never 0; S917, UNREACHED since no deciding row reads a key); pay rule T1 strict, T2/T3 ties pass; a refusal is ONE path (`define_sel`); the trace-only shadow is retired; REPORT row RPT is held for its R-26.6 preview. `memfn/docs/finder_history.md` logs routing.
- MF_TRACE (compile-time, off by default; format `../docs/trace_format.md`): `MFTRACE` records and reach counters; `REACH_DROPPED n=N` when the 32-row registry fills; `chosen=N asked=A`; keep `would_decline` meaning "the gate moved this selection".
- Zero-mover seam rules (R17-a): storage point protocol (`mf_locals` refused where `decl_point` is 0, twice, or with other `s`/`n` text; `mf_art_end` refuses "never placed"/"placed, never read" before "never used").
- SIMD rows (`vrun.c`) exist only as guarded, deny-able, ISA-gated forms; `policy` is a stated bit-set (PORTABLE/INLOOP/SIZE/NONE) a row must serve fully; scalar contracts serve MF_ANY; each SIMD form must beat scalar or show a named benefit (memory pcrec-post-spine-direction).
- Keep `mf_options()` (`--list-axes`) and `mf_opts_check()` (`--memfn=` acceptance) one table (`options.def`).
- THE WINDOW FAMILY (`window.c`, D172 S2 commit 1, `docs/design/memfn/window_site.md` rev 3.2) is reachable ONLY on an art previewing `"window-family"` (`mf_preview`); a site stating window facts (`mf_site.nalt`/`alts`/`wfloor`, appended last, no `MF_SITE_ABI` number move before commit 6) is checked as a statement on every art and decided by nothing on a default art. Its fields.def fields classify only through `gate_in.wf` (unstated in every other walk, so no older row can be declined by them). Every cost row reads `plan_cost.def`; every tie reads `wf_ties[]` (the TIE table); its E-func/E-stmt rows render the plan TRANSLATED into today's row's site (the composer's walk, the finder's routed pick included), so their text is today's; E-generic is the family's floor (`wf_floor_arm`). Its G2 family is `memfn/tests/run_g2_win.sh` (plants `--plants`).

## Files

- `kit.h` — INTERNAL header: `kb` text over the caller's `mf_arena`, `mf_art` and site records, arm interface (an arm writes straight to the sink), sink writers, `ofs_fn_*` renderer, `kit_table`/`kit_walk`, `gate_contract`, MF_TRACE calls, `MF_SERVES_*_TODAY`, `kit_set`. Never included outside this directory except by tests/memfn/proven_check.c.
- `compose.c` — K2, the composer: `mf_art`, define/use split (`mf_define`/`mf_use`/`mf_emit`/`mf_call`/`mf_art_end`), `site_check` rules, `kit_walk`, first-match arm table, `mf_ask`/`kit_class`/`proven[]`, `mf_locals`, `mf_defined`, `mf_preview`, `kit_report_exact`, stamps (`mf_stamps`: `RUN_WORDS`, `MEMFN_FORMS`, `MEMFN_LIBC` via `mf_art_note_libc`), `mf_reach`.
- `generic.c` — the generic scalar row (plain byte loop for every vocabulary site; STMT/FUNC/EXPR; `ctx_pred_test`).
- `ofsskip.c` — offset-skip arm: `fn_rows[]` BODY (`fn-pair`, `fn-memchr`) and PREFIX slots, `ofs_fn_define` routed as `<fn>__body` + `<fn>` selector; trace table `fn`.
- `vrun.c` — fused run-scan SIMD rows `vrun-w16`/`vrun-w32` (KB second filter, trim, padded verify; denies `no-vrun-kb`/`-trim`/`-pad`).
- `levels.def`, `levels.c` — the kit's ISA levels table (`MF_LEVEL`), `mf_levels()`, `kit_level()`.
- `precheck.c` — pre-check composite: `precheck_arm` (ON_MISS), `precheck_assign_arm`, `precheck_assign_byte_arm` (deny `precheck-assign-byte`; pcrec states the shape from [REQ-HANDOFF-L1] only).
- `runcmp.c` — run compare row table (`words`, `overlap`, `bytes`, `memcmp`), `run_cmp_render[_trim|_pad]`, `mf_flush_helpers`, `mf_run_rows`.
- `pffind.c` — prefilter find rows (`pf_memchr`, `pf_memchr_bounded`, `pf_walk`, `pf_walk_bounded`, `pf_memchr_back`).
- `mismatch.c` — F8 mismatch loop (`mm_render`; generic + `mismatch_inplace_arm`).
- `k1_ref.c` — K1 reference functions (`mf_ref_*`), G2's oracle side; never artifact text.
- `fields.def` — the field/class X-macros (`MF_CLASS`, `MF_FIELD`) of the row contracts.
- `gate.c` — row-contract gate: classifiers, `gate_check`, `gate_describe`, `MF_MISS_N`/`mf_miss_n`, `kit_is_ident`, shape helpers, MF_TRACE records, `policy` `class_set_of`.
- `options.def`, `options.c` — option registry `MF_OPT(...)`; `mf_options`, `mf_opts_check`, `kit_opt_denied` (`no-<name>`).
- `finder.c` — the finder table (`fd_rows[]`, `fd_decide`, `fd_route`, `fd_pres`, `mf_finder_rows`).
- `window.c` — the window family (D172 S2 commit 1): `wf_check`, Tables A (stop) / M (the MARGIN) / C (plan) / D (resume) / E (frame), the TIE table, `mf_wdecide` (phase 1), `wf_prepare` (phase 2), the floor row `wf_floor_arm` and its class.
- `plan_cost.def` — the window family's cost table `MF_COST(name, value, unit, provenance, box, basis)`: prefix_k's integers verbatim (window_site.md §3.3).
- `terms.c` — `mf_set_terms` cover search (R17-b; renderers at B4).
- `presence.c` — KW-8 ports `mf_pres_ports` / `kit_pres_picks` (read by the routed PRES slot; S458, S1094..7); the byte-rate and its masses `kit_byte_rate`/`kit_set_mass`/`kit_set_sum` (the window family reads them too).
- `formhash.c` — `mf_form_hash[_text]` (R-MS3 form identity; allocates with `malloc`, listing only).

## Pointers

`../CLAUDE.md`; `docs/design/memfn/integration.md` (§R4.7, §R4.9, §14-15), `row_contracts.md`, `r17b_prime.md`, `setfind.md`, `window_contract.md`; `../docs/trace_format.md`; `../PROVENANCE.md`; D145, D147, D149, D155, D157.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/memfn__src.md
