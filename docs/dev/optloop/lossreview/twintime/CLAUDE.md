# lossreview/twintime/ — the quiet-box TWIN TIMING slot (lane `twintime`, 2026-10-11)

Charter: `../fixes.md` revision 2 §3 step 0, the r2 panel row C1
(`docs/dev/reviews/2026-10-11-r2-lossreview-fixes.md`) and misc.md §7's T5.
Scratch tier: Ryzen 7 7700X (Zen 4), gcc 15.2.0, `taskset -c 14` (SMT sibling
cpu 6 idle), nothing else heavy on the box, ONE timing process at a time.
Nothing here is built or run by `make`. The artifacts and the pcrec-bench copy
live in the worktree's gitignored `build/lr` (`LR`); `TMPDIR` is pointed at
`$LR/tmp` (gcc otherwise writes to /tmp).

- `build_arms.sh` — builds every candidate-1 arm (cells bak2, bak1, modj,
  phone; arms `base`, `base_b` = a second compile of today's artifact (the null
  arm), `seam` = `static_seam` (always_inline, PLT removed AND specialized),
  `noinline` = `static_noinline` (PLT removed, not inlined, but gcc still emits
  a `.constprop.0` clone), `noclone` = `static_noinline_noclone` (strict PLT-only
  arm); twins made by `../vm/twins/twin.py`, which gained the two new transforms)
  at `PADS` code layouts (`.skip PAD` at the top of rx.c: every function shifts).
- `timeit.py` — the interleaved driver (shuffled arm x pad order per round,
  seeded by the round; every row kept; aborts on any answer-checksum
  mismatch against base).
- `run_c1.sh` — the charter's step 1 as run; `summarize.py` — per
  (cell, pad, arm) median-of-rounds totals and the gain vs base.
- `raw/` — raw TSVs: `cell regime pad arm round subject ns ck`.
- `summary.md` — the readings.
