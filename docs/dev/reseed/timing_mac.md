# [OPT-HYB-RESEED] Mac scratch timing (re-run by lane reseedfix, 2026-09-30)

**SCRATCH TIER, DIRECTIONAL ONLY.** Setup:

- Apple M1, gcc-16 `-O2`, find-all.
- The box was LOADED throughout: load1 6.0 at the start and 14.2 at the end,
  with a `make test-axes` and an answer differential running.
- Reproduce with `studies/hyb_reseed_cal/` (`subjects.py`, then `table.py`
  per row). The raw log is `studies/hyb_reseed_cal/results/timing_2026-09-30.md`.

The columns:

- **base** is the branch point (abi 46).
- **new** is this change (lane reseedfix's compiler). Its adaptive text is
  the r1 shrink. The algorithm is lane reseed's, and a re-check of one cell
  on lane reseed's own compiler read the same (the raw log's last rows).
- **deny** is new with `-fno-hyb-reseed`. It is byte-identical to base.

Method:

- Each binary is launched 5 times, round-robin with the other two, and runs
  5 passes per launch.
- A cell is the median of the per-launch medians, in ns per subject byte.
- This is NOT a fresh-launch median in the sense of plan row I-114's
  caveat: 5 launches sample the per-process layout lottery; they do not
  control it.

**THE NOISE FLOOR IS THE base/deny COLUMN.** Base and deny are the same
program, so their ratio is pure noise on that subject and that box.

- It reads ×0.99-×1.03 on most rows.
- It reaches ×0.71-×1.14 on five rows: fixed gap1/gap4/synth-dense and
  varwidth synth-64k-asc/gap64/bursty.
- So a base/new ratio within about ±5% is a NULL result. On those five rows
  the floor is wider still.

| cell | row | subject | matches | answers | base ns/B | new ns/B | deny ns/B | base/deny (noise) | base/new |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
| fixed `(?<=é)x` | adaptive | synth-1m | 0 | same | 2.033 | 1.730 | 2.054 | ×0.99 | ×1.18 |
| fixed | adaptive | synth-64k-asc | 0 | same | 1.709 | 1.465 | 1.724 | ×0.99 | ×1.17 |
| fixed | adaptive | synth-dense | 10523 | same | 4.145 | 4.015 | 4.485 | ×0.92 | ×1.03 |
| fixed | adaptive | gap1 | 0 | same | 1.932 | 1.421 | 1.688 | ×1.14 | ×1.36 |
| fixed | adaptive | gap4 | 0 | same | 1.686 | 1.436 | 1.883 | ×0.90 | ×1.17 |
| fixed | adaptive | gap16 | 0 | same | 1.702 | 1.391 | 1.707 | ×1.00 | ×1.22 |
| fixed | adaptive | gap64 | 0 | same | 1.723 | 0.407 | 1.679 | ×1.03 | ×4.23 |
| fixed | adaptive | bursty | 0 | same | 1.823 | 0.123 | 1.698 | ×1.07 | ×14.82 |
| fixed | adaptive | adv16 | 0 | same | 1.688 | 1.414 | 1.686 | ×1.00 | ×1.19 |
| fixed | adaptive | dense_sparse | 0 | same | 1.699 | 0.716 | 1.730 | ×0.98 | ×2.37 |
| varwidth `(?<=a\|é)x` | adaptive | synth-1m | 6918 | same | 8.642 | 3.271 | 8.586 | ×1.01 | ×2.64 |
| varwidth | adaptive | synth-64k-asc | 23 | same | 8.545 | 3.540 | 10.727 | ×0.80 | ×2.41 |
| varwidth | adaptive | synth-dense | 22505 | same | 6.495 | 6.960 | 6.600 | ×0.98 | ×0.93 |
| varwidth | adaptive | gap1 | 0 | same | 8.800 | 9.042 | 8.773 | ×1.00 | ×0.97 |
| varwidth | adaptive | gap4 | 0 | same | 8.701 | 8.636 | 8.705 | ×1.00 | ×1.01 |
| varwidth | adaptive | gap16 | 0 | same | 8.834 | 1.645 | 8.675 | ×1.02 | ×5.37 |
| varwidth | adaptive | gap64 | 0 | same | 8.941 | 0.422 | 12.544 | ×0.71 | ×21.16 |
| varwidth | adaptive | bursty | 0 | same | 8.749 | 0.440 | 9.782 | ×0.89 | ×19.90 |
| varwidth | adaptive | adv16 | 0 | same | 8.852 | 2.883 | 8.984 | ×0.99 | ×3.07 |
| varwidth | adaptive | dense_sparse | 0 | same | 9.085 | 4.471 | 8.830 | ×1.03 | ×2.03 |
| neg `(?<!日)本` | adaptive | synth-1m | 2771 | same | 4.515 | 0.444 | 4.532 | ×1.00 | ×10.17 |
| neg | adaptive | synth-dense | 9093 | same | 5.965 | 5.325 | 5.880 | ×1.01 | ×1.12 |
| neg | adaptive | cjk1 | 0 | same | 2.993 | 3.189 | 2.984 | ×1.00 | ×0.94 |
| neg | adaptive | cjk4 | 0 | same | 2.895 | 2.383 | 2.895 | ×1.00 | ×1.21 |
| neg | adaptive | cjk16 | 0 | same | 2.983 | 0.702 | 3.004 | ×0.99 | ×4.25 |
| lka-pos `item(?= done)` | adaptive | lka_sparse | 5 | same | 0.523 | 0.404 | 0.518 | ×1.01 | ×1.29 |
| lka-pos | adaptive | **lka_dense** | 6535 | same | 1.201 | 1.942 | 1.190 | ×1.01 | **×0.62** |
| lka-pos | adaptive | lka_dense (lane reseed's realization) | 20477 | same | 1.912 | 2.030 | 1.899 | ×1.01 | ×0.94 |
| lka-pos | adaptive | synth-1m | 0 | same | 0.519 | 0.515 | 0.509 | ×1.02 | ×1.01 |
| ` (?=the)` | adaptive-dense | lka_sparse | 18976 | same | 2.317 | 2.411 | 2.337 | ×0.99 | ×0.96 |
| ` (?=the)` | adaptive-dense | synth-1m | 6776 | same | 1.633 | 1.737 | 1.630 | ×1.00 | ×0.94 |

What the table supports, stated against the floor:

- **Where the old loop stepped a sparse region, the win is real and large:**
  - ×2.0-×21.2 on gap16/gap64/bursty/dense_sparse/adv16/synth for
    varwidth and neg;
  - ×2.4-×14.8 on gap64/bursty/dense_sparse for fixed.
  - The largest measured ratio is ×21.2 (varwidth gap64). No cell reads
    ×28; that figure in lane reseed's first report matched no row.
- **fixed's ×1.17-×1.36 on synth-1m, synth-64k, gap1, gap4, gap16 and adv16
  is NOT a mechanism win.** At those gaps the adaptive machine should sit in
  step mode, or re-seed only at gap16, and equal the step arm. Two of those
  rows have a noise floor of ×0.90/×1.14. It is layout or alignment luck
  until an x86 measurement says otherwise.
- **Flat within noise:** fixed synth-dense (×1.03 against a ×0.92 floor),
  varwidth gap1/gap4, lka-pos synth-1m. Also ` (?=the)` on both subjects
  (×0.94-×0.96): marginal, at the edge of the floor.
- **Real losses:**
  - **lka-pos on a match-dense prose subject, ×0.62** on this lane's
    realization, where `item` is about a third of the words.
  - On lane reseed's realization, ×0.94.
  - neg cjk1 ×0.94 and varwidth synth-dense ×0.93 are marginal.
- The lka-pos loss is the per-call regime. Find-all makes one call per
  match, about one per 160 B here. Each call re-learns the density: the
  entry prefilter, a 64-step first budget, then 2-3 re-seeds to arm and
  enter a block. At ~25-40 ns each, those re-seeds are the ~0.75 ns/B the
  cell loses.
- That is the named trigger of `[OPT-HYB-RESEED-XCALL]`: "a measured
  short-subject / find-all cell losing to the per-call probe". It is
  reported to the manager as MET on the Mac scratch tier. The bench's own
  `lka-pos` cell decides the magnitude.

The old table (lane reseed, 2026-09-29, a loaded box, one launch per cell
per repeat) is superseded by this one. Its lka rows used a different subject
realization, so they are not comparable row for row.
