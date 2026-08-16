# docs/design/rungselect_impl — the [ENG-BREP] RUNG-SELECT lane's measurements

The lane that builds `eng_brep_design.md` §3's REVERSE-DETERMINISTIC rung (and,
as a first separate slice, the K22 interim guard). Its own probes, scripts and
archived outputs, kept separate from `../eng_brep_measurements/` (the design
lane's territory) and `../possessify_impl/` (the previous rung lane's) so the
three are never confused — the same separation possessify_impl was created for.

Everything here is COMMITTED AND RE-RUNNABLE. R24 M-F4's lesson: a number that
cannot be re-run is not a measurement, and this lane's predecessor lost a table
to exactly that.

## Files

- **`k22_sweep.sh`** — the K22 nested-bounded-repeat compile sweep. Generates
  the `(x)(?:...(?:a){0,2}...){0,2}z` tower of
  `../possessify_impl/k22_repro.txt` at a range of nesting depths and times
  `pcrec --engine=vm` on each. `--engine=vm` is the precondition, not a
  convenience: on the default path the NFA 131072-state cap refuses every one
  of these instantly and the defect is unreachable.
- **`k22_sweep_before.txt`** / **`k22_sweep_after.txt`** — that sweep either
  side of the product guard, with a source header each. BEFORE reproduces
  `k22_repro.txt`'s own timings exactly (depth 15 compiles 0.32 s, depth 30
  refuses in 11.8 s, depth 35 and 40 hang past 30 s). AFTER: depth 15 still
  compiles, depth 19 and up refuse in 0.12 s.

  **Depth 18 is the interesting row and it did not move.** It refuses in 0.72 s
  through `PCREC_MAX_VM_NODES`, not through the new guard, because the tower's
  innermost `(?:a){0,2}` takes the CURSOR rung and replicates nothing — so a
  depth-*d* tower's replication product is 2^(d−1), and depth 18's is exactly
  the limit rather than over it. That is the guard's soundness property visible
  in a measurement: it shares `PCREC_MAX_VM_NODES`'s value because a
  replication product is a LOWER BOUND on the emitted node count, so it can
  only ever move a refusal EARLIER, never make one wider.

- **`rungselect_design.md`** — the emitted-shape design sketch for the
  reverse-deterministic rung, written before the code (the manager reviews
  direction from it).

Maintenance: update this file when files are added/removed or their roles
change.
