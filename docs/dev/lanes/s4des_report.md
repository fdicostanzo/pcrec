# s4des: `[OPT-LITSCAN]` S4 design (lane report)

Lane `s4des` (opus), 2026-10-03, branch `lane/s4des` from main `c231ffc1`
(abi 55). Design only: nothing under `src/`, `cli/`, `lib/` or `tests/`
changed. No `make test` was run. One `make -j4 CC=gcc-16` built the
worktree's compiler for the census.

## Delivered

- `docs/design/litscan_s4.md`: the design note. §0 is the findings, §10 the
  eleven questions for the manager, each with a recommendation.
- `docs/dev/optloop/s4/`: its instruments (`census.py`, `spell.c`,
  `one.c`/`two.c`, `hot.c`, with a `CLAUDE.md`).
- Index entries in `docs/design/CLAUDE.md` and `docs/dev/optloop/CLAUDE.md`.

## Summary a resuming agent needs

S4 is one emitter function, `pcrec_emit_run_compare` in a new
`src/gen/runcmp.c`. It has four first-match rows:
- `words`: masked, any L, decomposed into overlapping natural-width words;
- `overlap`: exact, L in {3, 5-7, 9-15};
- `bytes`: the masked fallback;
- `memcmp`: today's P4, the exact fallback.

The design lands in four commits:
- **C0** moves the byte cube into `src/core/cpset.c`
  (`pcrec_cube_of`/`pcrec_cls_cube`), with clskit's `cube_of` as a caller.
  It moves no bytes.
- **C1** re-points P4's three callers. Bit 42 is `-fno-run-overlap`.
- **C2** lets `pcrec_lit_run` admit any one-cube position. Bit 43 is
  `-fno-lit-run-fold`.
- **C3** widens `src/facts/req.c` to cube runs, used only where today's
  exact run declines. It adds the two-stream scan arm in the run block and a
  `req_admit` conjunct, and gates the `prefix_k.c` pin to exact runs, so
  `dfa_pfs[]` is untouched. Bit 44 is `-fno-req-run-fold`.

Each of C1, C2 and C3 is its own abi event.

C3's measured customer is `union-select`. Bench O-55's hand twin for the
chosen pick (`select` on `c`) read 0.4389 ns/B against base 0.7178.

## Probes run (scratch, this box)

- **`gcc-16 -O1/-O2 -S` and `clang -O2 -S` (arm64, x86_64) on `spell.c`.**
  The spelling decides branchiness on both compilers: `&&` early-exits, and
  `|`-of-xors is branchless. The `memcpy`-from-literal constants fold to
  immediates everywhere.
- **`gcc-16 -O2 -fsanitize=address -S` on `one.c`/`two.c`.** The word loads
  are instrumented, two checks at L = 5. The inlined constant `memcmp` gets
  none.
- **`hot.c`, gcc-16 `-O2`, M1, load 2-4, three runs.** Exact L = 7 `memcmp`
  measured 0.466 ns/pos against `overlap` at 0.620, which contradicts
  `memcmp_lowering_study.md` §11 in this loop shape. Masked `&&` measured
  0.620 against `|` at 0.684 and the byte chain at 0.635. Directional only.
- **`census.py` over 339 bench patterns.**
  - 55/317 default-route and 92/318 forced-VM artifacts carry a compare at
    an overlap length.
  - Only 2 default-route artifacts carry a VM fold test; 17 forced-VM ones
    do.

## Owed (not this lane's)

- The build lanes owe the corpus mover census for C1-C3 and C3's cube-run
  census.
- The Linux alpha block (design note §6, executor channel). Its step 0 is
  `[WORD-FOLD]`'s owed gcc-15/x86 instruction arm.
- The panel the manager rules for C3 (Q4).
