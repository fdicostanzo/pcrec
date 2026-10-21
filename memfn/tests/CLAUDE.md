# memfn/tests/ — G2, the kit's own tests

G2 (integration.md §10.2, §14.6) checks the kit's rendered code against G2's OWN scalar byte loop over a GENERATED predicate space, never against another output of the kit's generator. Originally written D27-blinded (lane memfng2) from the contract (integration.md §8.3, §14) and `memfn/include/memfn.h` only, without the kit's source. The pcrec-side kit checks (C4, C5, C9-C17, pins under `tests/memfn/`) live in pcrec's `tests/`, not here.

## Standing rules

- Independence: G2's reference (`g2/g2_ref.c`) calls NO kit function (not even `mf_ref_*`); the floors in `run_g2.sh` are literals sharing no source with the generator or driver (K35: count populations). `g2_k1.c` is the only G2 file that links the kit's `mf_ref_*` answers; G2 never uses them as its oracle.
- Extending G2 to a new site-ABI/shape: write from `memfn.h` and integration.md §14/§15 contract sentences, not the kit's source (blinded families: stride, mismatch, ABI 6); the families written by the row's author (landmark gate sites, SIMD family) rest on the oracle and the compiler, and say so. Each lane's contract coverage and open questions go in its `G2*_REPORT.md`.
- Every new family draws its OWN RNG stream and id range (base none; `pf` via `pf_enter`/`pf_leave`; `stride` 1000000; `mismatch` 800000; `mline` 700000; landmark `gate` 2000000) so no older site moves; give it a `--<fam>-only` generator switch if its row-count check needs one.
- From MF_SITE_ABI 11 the generator STATES the window (`g2_win`/`G2W(site)`) at every `mf_emit`/`mf_define` call and, from ABI 18, span 0's class (`g2_span0`), AFTER every perturbation so each refusal case keeps its refusal; the window rules are C5's gate cases (tests/memfn/arm_fixtures.c `seq_cases`), the R-26 proof checks are `tests/memfn/run_proof.sh`.
- ENFORCED CLASSES (hook-nonident, miss-unstated, refusal-unnamed, fn_ref-unstated, pf-edge, loop-exit; renamed from PENDING-ENFORCE): each a named population with a floor (`FLOOR_CLS_*`) and printed count; they render in their own batches. `G2_STRICT_HOOKS=0` is diagnostic only. Refusals must NAME the field the header names.
- Poison differential: every field the contract says a site does not use is set to junk; rendering must be byte-identical or refused (bisected to the field, `FAIL poison`). An UNSTATED `note` hook is never poisoned; a FUNC site's `pred.fn_ref` is never poisoned on ALL_PRESENT.
- Two entry paths differ by contract: `mf_emit` holds use hooks at selection; `mf_define`+`mf_use` refuse a use the form does not serve (lawful, counted `USEREFUSE`, unnamed must be 0). A refusal at `mf_define` of a site `mf_emit` rendered fails.
- Witnesses: W1 (reference defects `--ref-defect K`, 1-10), W2 (kit-text mutations `--mutate K`, 1-16; every mutated, non-equivalent site must be killed), W3 (planted functions: over/under-read, `st-*`, `mm-*`). A change to a reference range/shape adds its W1/W2/W3 witness. Guard-page witnesses run without aliases where an alias would fault anyway (`mm_noalias`).
- Read-limit layouts: U (guard at `s + n`), L (guard below `s + floor`, floor <= lo), A (exact heap, alignment 0..15), plus TIGHT for strided sites; a fault is a failure; a non-returning loop is stopped by a 10 s alarm and fails.
- Rows: `--rows` (implied by `--quick`) links against `build/libpcrec_mftrace.a` and sums `MFTRACE REACH chosen=N`; checks (a) REACH_DROPPED 0, (b) every row n >= 1, (c) distinct rows >= literal `FLOOR_ROWS` (20 now), (d) every process printed REACH lines, (f)/(g) MISMATCH-only and stride-only floors (`ST_ROW_FLOORS`). A new row raises `FLOOR_ROWS`.
- Every step runs under GNU timeout; `run_g2.sh` exits 0 only when failures 0, every floor holds and every witness fired. `make test-memfn-g2` = `--quick` (a `make test` section); `make test-memfn-g2-full` is opt-in, never part of `make test`. Mech arm `g2gate` for `run_g2_gate.sh`.
- SIMD family host gate: arms for higher ISA levels are always BUILT but RUN only when the host supports the level; a skipped arm prints `SKIPPED ARM <level>: <why>; N checks NOT run` plus `skipped arms: K` (never a silent pass); `G2V_SKIP_ARMS` forces a skip; `G2V_CPUS` pin is honoured as given (hard error outside the affinity set); `G2V_JOBS` concurrent builds. Its checks: ranking check, verify check, padded verify, guarded bytes vs `tests/memfn/simd_bounds.tsv`, answers across levels and ASan+UBSan, per-path execution floors, six plants per level, no PDEP/PEXT/gather.
- Triage: `G2_TRACE=<site id>` prints every call of that site (layout U).
- Maintenance: update this file when a family, witness or runner changes; add the lane report here.

## Files

- `run_g2.sh` — the one command: builds generator against `build/libpcrec.a` (`-I memfn/include` only), renders, compiles (gcc+clang, ASan+UBSan on quick tier), runs driver and W1-W3, holds floors (`FAM_FLOORS`, `FORM_FLOORS`, `FLOOR_MT_*`, poison/semantic floors, libc leg `MEMFN_LIBC` vs `nm -u`). Options `--quick`, `--keep`, `--seed N`, `--rows`/`--no-rows`; prints `checks passed/failed`.
- `run_g2_gate.sh` — the landmark `gate` family standalone (~30 s): ASan+UBSan runs, LMSITES floors, `precheck_assign_byte` chosen by trace, control (W2 mutation 2 kills >= 80%).
- `run_g2_simd.py` — SIMD-family runner (run_g2.sh section 4a; alone `python3 memfn/tests/run_g2_simd.py [--quick]`).
- `g2/g2.h` — G2's site description (`g2_site`, `g2_pred`, `g2_term`; `G2_MAXT` 32), outcomes, miss values, helpers; `G2_FAM_STRIDE`, `st_*` fields. Does not include `memfn.h`.
- `g2/g2_gen.c` — generator and G2's only kit caller: families `base`, `ofs`, `ofsrun`, `stmt`, `onebyte`, `gate` (+`landmark_one`), `setrest`, `vmrun`, `pf` (four cells + edges), `mline`, `mismatch`, `stride`, `sem` (semantic differential, incl. `site-fn_ref`), PENDING queue, REFUSAL table, poison differential, `--mutate K`, `--gate-only`, `--mm-only`, `--stride-only`.
- `g2/g2_ref.c`, `g2/g2_ref.h` — the independent REFERENCE (one plain loop per operation; `g2_ref_range`/`g2_ref_readsbelow` the one statement of the read-bounded range; `g2_ref_mismatch`, `g2_ref_stride`; `--ref-defect K`).
- `g2/g2_driver.c` — driver: subjects (lengths 0..129, planted hits, near-misses, random; two (lo, floor) pairs), three layouts, census, `run_stride`, `run_mismatch`/`mm_instance`, `--witness-overread` (W3), `--mutants` (W2).
- `g2/g2_k1.c` — K1: kit `mf_ref_*` functions vs G2's loops (every length 0..129, alignment 0..15, `mf_ref_skip_blocks`).
- `g2/g2_simd_gen.c`, `g2/g2_simd.h`, `g2/g2_simd_driver.c` — SIMD family generator, site table, driver (vrun rows; denies kb/trim/pad classes).
- `G2U_REPORT.md`, `G2X_REPORT.md` (interim, superseded), `G2M4_REPORT.md` (ABI 6, R-7), `G2M6_REPORT.md` (ABI 8 strided ADVANCE), `G2M7_REPORT.md` (ABI 7 MISMATCH), `G2ROWS_REPORT.md` — lane reports.

## Not here yet

The `moved` property test and arm-differs property (§10.2); cross-target `-fsyntax-only` and the kit's timed suite (K-5); the agreement check against `pcrec_cls_cube` (needs pcrec's `tests/`).

## Pointers

`docs/design/memfn/integration.md` (§8.3, §10.2, §14, §15.x, §R4.7), `memfn/include/memfn.h`, `docs/dev/lanes/memfng2_report.md`, `tests/memfn/`, `../CLAUDE.md`, D27, K35.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/memfn__tests.md
