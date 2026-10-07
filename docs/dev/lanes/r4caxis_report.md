# r4caxis — [MEMFN] R4c lane AXIS (2026-10-06, sonnet)

Branch `lane/r4caxis`, cut from the kit branch `lane/memfn-r4c`. Births pcrec's ONE kit axis,
`-fno-memfn-simd` / `-fmemfn-simd` (axis `memfn-simd`, bits 48/49, OFF by default, INERT: no SIMD
form exists before R4e', so both settings render identical artifacts). Scope: scope.md §6 lane AXIS,
rulings Q2 and Q5.

## Diff summary

- `lib/pcrec.h`: `PCREC_NO_MEMFN_SIMD` (bit 48), `PCREC_FORCE_MEMFN_SIMD` (bit 49), `#define`s after bit 47.
- `src/core/axes.def`: one `PCREC_AXIS` row on the `-fno-comments`/`-fcomments` shape, `DEFAULT_OFF`.
- `src/gen/emit_dfa.c`: `strategy_denials` gains both bits (one hunk), so `rx_info.flags` never moves.
- `src/dump/axes_dump.c`: the `--list-axes` rows (the dump's predicate rows are hand-stated per axis;
  `axes.def` alone does not list an axis): `memfn-simd` 1 `portable` / 2 `simd`, stamp `RX_MEMFN_FORMS`.
- THE HELPER for lane CORE: `uint32_t pcrec_memfn_policy(uint64_t flags)`, declared in
  `src/core/internal.h`, defined in `src/gen/memfn_stamps.c`. Returns `MF_P_PORTABLE_ONLY` iff
  `-fmemfn-simd` is not in force (deny, force, default resolved by `pcrec_axis_on`). Its one caller
  today is `pcrec_memfn_stamps_render` (replacing the hard-coded literal; pass `cx->opt->flags`).
  CORE: every `mf_art_begin`/site policy takes this, never a literal.
- D80: `docs/spec/tuning.md` new §2.43 (the `(bit 48)`/`(bit 49)` heading the registry check requires);
  `docs/spec/registry.md` §6 count 129/43 -> 131/44; `docs/spec/match_api.md` C11 sentence (identity
  half now runs, movers half UNREACHED).
- Pins: `tests/registry/run_registry_tests.sh` axes_registry_check 199 -> 205 (+3 checks per row).
  `tests/axes/run_axes.sh` derives its sweep from `--list-axes` and the tuning.md headings, so it picks
  the pair up with no pin to move.
- C11 identity half: `tests/memfn/libc_census.py` recompiles every pattern-stream artifact with
  `-fno-memfn-simd` and requires byte equality; prints "identical (no SIMD form)"; movers half still
  printed UNREACHED. Composition files are not re-compiled.

Files outside the charter list: `src/dump/axes_dump.c`, `src/core/internal.h`, `src/gen/memfn_stamps.c`
(the dump rows and the helper need them), `docs/spec/tuning.md` (the registry check requires the heading).

## The declared mover

`python3 scripts/emit_sweep.py --ref 691a8b7c` (230 s, log `build/scratch/sweep.log`, untracked): streams
1-4 `movers=0 asymmetric=0` (4606 argv, reach 4159/4160/4160, composition 38 producing); self-check
passed. Stream 5 `movers=1`: `--list-axes`, and the diff is exactly the two new `memfn-simd` rows
(`@@ -128,2 +128,4 @@`, `+memfn-simd 1 portable`, `+memfn-simd 2 simd`). Every artifact byte-identical.
Also spot-checked default vs `-fno-memfn-simd` vs `-fmemfn-simd` md5 on 3 patterns: equal.

## Validation

- `make` clean; `make strict`: clean.
- `make test-registry`: exit 0, axes_registry_check 205 PASS / 0 failed, PC-3 213 / 0.
- `CC=gcc-16 bash tests/memfn/run_libc_census.sh --quick`: 8 passed, 0 failed, including
  "FORMS identity: identical (no SIMD form) -- 546 pattern-stream artifacts". (With default `gcc` on
  the Mac the LIBC half reports `__chkstk_darwin`; that is the compiler choice, not this change.)
- `make test-codegen`: exit 0, 15/15 scripts passed, every group `checks failed: 0` (log `build/scratch/cg.log`).

## OWED

- Axes sweep for the new pair (a corpus run per axis, multi-hour class on the Mac):
  `AXES="-fno-memfn-simd -fmemfn-simd" bash tests/axes/run_axes.sh`.
- Full `make test` (Mac ~100 min; Linux verdict through the manager's slot).
- Full (non-quick) C11: `CC=gcc-16 bash tests/memfn/run_libc_census.sh`.
- Not run: `make test-axes`'s form census.

## Charter vs committed

- [x] bits 48/49 in lib/pcrec.h
- [x] axes.def row
- [x] strategy_denials, minimal hunk
- [x] registry.md + match_api.md (+ tuning.md) D80 hunks
- [x] registry pin
- [x] tests/axes pins: none needed (derived)
- [x] C11 identity half
- [x] MF_P_PORTABLE_ONLY helper: `pcrec_memfn_policy`
- [x] stream-5 diff proved to be exactly the new rows; artifacts identical
- [x] report + lanes/CLAUDE.md row
