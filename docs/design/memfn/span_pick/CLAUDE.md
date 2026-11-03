# docs/design/memfn/span_pick/ — span_pick.md rev 2's recount instruments

Lane spanpick2 (2026-11-02). Every number rev 2 quotes from R-33's raw sweep is recomputed here (the
review's lesson 1: recompute with the design's own formula). A study only: never built or run by `make`.

## Files

- `onestream.py SIMDIR SWEEP.jsonl` — the census of stage 3's row ONE-STREAM over every no-entry
  alternative (reuses R-33's committed `docs/dev/lanes/r33_sim/sim.py` candidate builder unchanged), and
  smp20's prices under rev 2's formula (Zen 1 `plan_cost.def` constants; hit(PAIR) at 20 and 40 c).
- `counts.py SWEEP.jsonl` — the populations rev 2 quotes (PF sites with two alternatives, OFS sites with
  no consumer kind, entry x Table A row, run member vs stop, finder rows reached).
- `onestream.out`, `counts.out` — their outputs at lane time.

SWEEP is R-33's raw `sweep.jsonl` (not committed; `/var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/`,
re-made by `docs/dev/lanes/r33_sim/240-kit-r33-sweep.sh`). Run with `python3 -I`.
