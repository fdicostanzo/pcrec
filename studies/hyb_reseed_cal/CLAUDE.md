# studies/hyb_reseed_cal/ — [OPT-HYB-RESEED]'s calibration and timing harness

Committed by lane `reseedfix` (2026-09-30) after the r1 panel found the
calibration not reproducible from the repo (chk F4): lane `reseed`'s
generators, driver, hand-twin transformer and bench scripts lived only in
its session scratchpad. Nothing here is built by `make` or run by
`make test`. The design is `docs/design/hyb_reseed.md` (§3 cites this
harness) and the results it produced are `docs/dev/reseed/timing_mac.md`
and `docs/dev/reseed/clamped.md`.

## Files

- `README.md` — how to rebuild the reference compiler and re-run every table.
- `drv.c` — the find-all timing driver (median/min ns per byte over passes
  in ONE process, plus an answer hash).
- `subjects.py` — regenerates every named subject (gapG, bursty,
  dense_sparse, advG, cjkG, synth-*, lka_*, clamp_*). Deterministic.
- `gen114.py` — I-114's three synthetic subjects, verbatim seeds.
- `table.py` — one base / new / deny row per subject, with the noise floor
  (base/deny) in the row.
- `twin.py` — the hand-twin transformer over a BRANCH-POINT (abi 46)
  artifact: the retry tail becomes a build-time choice (`-DTW_MODE`).
- `xover.sh` — the step-vs-re-seed crossover sweep (design §3's gap column).
- `bench.sh`, `dbl.sh`, `init.sh`, `modes.sh` — lane reseed's twin
  explorations (block sizes, doubling/caps, first budget, gap-rule modes),
  kept as they ran, paths parameterized.
- `shape/` — lane xcalldes's O-81 slow-cell attribution probes (2026-10-03):
  short-search/match/find-all driver, counting driver, the F1/F2/F3 emitted-
  form rewriters, bench-subject regeneration. Backs `docs/design/xcall.md`.
  See its own CLAUDE.md.
- `bakeoff/` — lane rsform's [OPT-HYB-RESEED-FORM] A2 form bake-off
  (2026-10-03): the pack builder, the six-form rewriter and the Linux-side
  gcc+clang timing script the manager runs. See its own CLAUDE.md.
- `results/` — the raw outputs this lane's re-runs produced
  (`crossover_2026-09-30.txt`, `timing_2026-09-30.md`,
  `clamped_2026-09-30.md`), each with its date, box and load.
