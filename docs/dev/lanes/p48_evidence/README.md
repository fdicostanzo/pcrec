# p48_evidence: scan-edge admission and pricing (lane p48, 2026-10-29)

Evidence for `../p48_report.md`. Nothing here is built or run by `make`, and
no check reads it.

## Twin compilers (scratch, never committed as trees)

Each twin is `git archive b05ccfc0b` unpacked under
`$PCREC_TMPDIR/scratch/p48/<name>/`, patched with one script, then built with
`make build/pcrec`. Every twin also gets `patch_trace.py`, which adds a
`P48_TRACE=1` stderr line per stay skip and scan edge per machine and is inert
without the variable. A forward declaration has to be added by hand: see
the `sed` in the report's method notes.

| twin | patch | what it is |
|---|---|---|
| `tset` | none | HEAD |
| `tsingle` (and `twin`, untraced) | `patch_single.py` | pre-[SCANEDGE-SET]: singleton class sets only |
| `trelax` | `patch_relax.py` | HEAD plus the one-state relaxation (a self-loop head with any exits) |
| `tnogoto` | `patch_nogoto.py` | HEAD with the loop-entry dispatch emitted for BOUNDED heads only |

## Drivers and scripts

- `drv.c`: a find-all loop with the bench's advance (`timed.c`), calling
  `rx_search`.
- `drv_anch.c`: `rx_match` at every `x` (the break-even micro).
- `mk.sh LIST OUT`: compiles each pattern in the `set`, `single` and `none`
  arms.
- `bld.sh DIR`: compiles each matcher at `-O2 -fPIC` in its own TU and links
  it to `drv.c`.
- `meas.sh DIR ID SUBJECT ITERS`, with `ARMS=` to pick the arms: one match
  count plus instructions, cycles and branch misses per iteration, from
  `perf stat -r 3`.
- `be_run.sh FAM IDS`: the break-even sweep.
- `census.py`, `502-p48-census`: the corpus and bench census through the
  three traced twins (a queue job). `census_read.py` reduces its output.
- `500-p48-relaxcorpus`, `501-p48-nogotocorpus`: queue jobs that run the
  answer sections of `make test` against the `trelax` and `tnogoto` trees.

## Data

- `cells.tsv`: the O-111 cell patterns.
- `cells_measure.txt`: the per-cell twin measurements (the report's
  Regressions table).
- `breakeven_measure.txt`: the A/B/C sweep (the report's Break-even table).
- `run_lengths.txt`: edge entries, guard passes and run bytes, from
  hand-instrumented set-arm artifacts.
- `census_summary.txt`: `census_read.py` over the census.

The box was loaded by queue `make test` runs for all of this. Instruction
counts are deterministic. Cycles are indicative only.
