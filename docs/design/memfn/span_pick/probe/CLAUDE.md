# docs/design/memfn/span_pick/probe/ — the census's site probe (successor)

Written by memfn plan_frame.md 3.0b (lane b30b, 2026-11-12) to replace R-33's
`docs/dev/lanes/r33_sim/probe.c` as the census instrument's probe; the lane directory stays
as R-33 left it (historical). Never built or run by `make`. Run python with `python3 -I`.

## Files

- `probe.c` — linked into a traced scratch pcrec with `--wrap` over the kit's
  `mf_art_begin`/`mf_define`/`mf_emit`, it prints one `R33 {json}` line per site and one
  `R33RATE` line per art, the predecessor's records key for key. Its wrappers are declared
  by `__typeof__` of the public entries (a seam move fails its build), and its phase-1
  ask is `mf_wdecide` call NONE with no hooks (the decision group only). Compiled
  `-fsyntax-only` by `tests/memfn/run_link_checks.sh` on every run.
- `build.sh TREE OUTDIR` — the traced build plus the probe link (copy of r33_sim's).
- `collect.py`, `sim.py` — the record parser and the simulator (copies; stdlib only).
- `sweep.sh`, `rp.sh` — boxqueue jobs, copies of jobs 240 (the sweep) and 241 (the
  rule-list pilot's arms) whose `SIM` is this directory and whose tree is stated as
  `PROBE_TREE` (never a lane worktree); outputs under `scratch/memfn/r33/` as before.
  The census's re-make jobs (440, 488) are re-queued from `sweep.sh`.
