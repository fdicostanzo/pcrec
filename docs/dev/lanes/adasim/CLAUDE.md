# docs/dev/lanes/adasim/ -- lane adasim's count-only simulation (no clock, no product code)

Report `../adasim_report.md`. Python 3 + numpy only; nothing here is built or run by `make`. Run order (paths are the
lane's worktree and the e8/grid2 slots read-only):
- `feat.py OUTDIR` -- the real member mask of every 64-byte stretch of every subject flat and e8 timed (set read from
  each cell's V1 artifact). `fit.py OUT.json` -- per-stretch cost model as a delta to the walk, LOO and hold-out.
  `sim.py MODEL.json OUTDIR` -- threshold fit, the rule (R1 transitions, R2 members+transitions), tables, sensitivity.
- `common.py` -- loaders (flat_report tables, e8_cells.tsv, per-stretch features, the Q-proxy).
- `cells.tsv` (per-cell predictions), `model.json` (fitted coefficients), `run.txt` (sim.py's full output).
