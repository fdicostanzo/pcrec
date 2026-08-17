# tests/bench/compare — cross-engine comparison matrix and its ratchet

Produces the numbers this project quotes about itself: pcrec against
PCRE2-interp, PCRE2-JIT and python `re` over a fixed case matrix. Slow (tens of
minutes, full matrix), so it is run deliberately — before and after any
performance-relevant change — rather than from a make target.

## Files

- **compare.sh** — the matrix. Pins to a core, repeats `BENCH_TRIALS` times per
  engine/case, reports medians and max/min spread, verifies every case's match
  span against an oracle, and emits a machine-readable TSV block plus a
  `results-<host>-<date>.md` write-up.
- **eng_pcrec.c**, **eng_pcre2.c**, **eng_py.py** — the per-engine drivers.
- **gate.sh** — the ratchet over compare.sh's own pcrec numbers. `UPDATE=1`
  rewrites floors.tsv (and appends to run_history.tsv); `EARN=1` reports
  (never applies) a margin run_history.tsv can justify per case (R3.7).
- **floors.tsv** — per-case reference value AND per-case margin.
- **run_history.tsv** — accumulated independent runs, one row per (run, case),
  seeded from the two results-\*.md snapshots and every `rebaseline.sh` /
  `gate.sh UPDATE=1` run since (R3.6/R3.7). What `EARN=1` and `rebaseline.sh`
  read to decide whether a case has "enough" independent data yet.
- **rebaseline.sh** — the re-baseline MECHANICS for a single floors.tsv case
  (R3.6): runs `compare.sh` N times for one case, checking load before/after
  each run, appends to run_history.tsv, and reports the cross-run median —
  it does not write floors.tsv itself.
- **results-\<host\>-\<date\>.md** — captured baselines.

## Conventions

**The floors are machine-specific.** On new hardware, regenerate with
`UPDATE=1 bash gate.sh` and treat that as re-baselining, not as a comparison.
Never widen a margin to make a red run green; journal the change instead.

The gate deliberately checks pcrec's ABSOLUTE numbers, not ratios against the
other engines: a ratio moves when PCRE2, python or the box changes, and R2-B1
showed those ratios flipping sign run to run.

Margins are per case, derived from that case's own trial spread as
`clamp(1/(spread*1.05), 0.70, 0.90)` (R3.5). One global 0.70 fires only below
1.43x, which is how M2.10's 27% regression passed this gate while the review
credited the gate with catching it. The ceiling is fixed rather than derived
from a single run's WITHIN-run spread, which is a sample, not a distribution.

CORRECTION (R3.7, 2026-08-11): this file used to justify the 0.90 ceiling with
"the box's noise floor is ~10% no matter how tight one run looks" — that
number was never backed by any measurement in this repository (also corrected
in gate.sh and floors.tsv; D17 in docs/dev/decisions.md still needs the same fix).
The ceiling stays at 0.90 regardless: `run_history.tsv` (one row per case per
independent `compare.sh` run — see `rebaseline.sh`) and `gate.sh`'s `EARN=1`
mode are the honest path to tightening it, and as of this correction every
case still has fewer than `EARN_MIN_RUNS` (default 8) independent dates of
history, so nothing has been earned yet. Each run still prints, per case, the
smallest regression its margin can catch.

Two known gaps, carried deliberately: case (d) matches at 0.99% of its buffer
so its "throughput" is exit latency (R2-B4, fixed in run_bench's sibling case
but not here), and gate.sh has no minimum-coverage floor beyond requiring that
every floor row was measured.

**Case (j), added [M4.6b] (2026-08-17), is the one case in this matrix that is
CAPTURE-BEARING on purpose.** `([01]*)1([01]{8})` is DD-9's capture-bearing
sibling of case (f) — engine_m4.md §8.5's non-regression floor for the
VM+prefilter hybrid: capture groups route pcrec off (f)'s pure DFA and onto
the hybrid (confirmed per-run from the compiled artifact's
`rx_info.engine == ENGM_VM` and a non-NULL `engine_why`), which is exactly
the shape most likely to embarrass it — the DFA prefilter finds a span
covering the whole 8 MB buffer (span/subject ratio 1.0, §6.2(a)'s stated
worst case), so the VM then re-walks essentially all of it a third time.
Floor derivation (floors.tsv): three independent quiet-box `CASES=j` runs,
150.350/150.369/150.397 MB/s, spreads 1.00x-1.01x — reference is the median
(150.369), margin is the standard R3.5 formula
(`clamp(1/(spread*1.05), 0.70, 0.90)`) at the worst of the three spreads,
which clamps to the 0.90 ceiling like most other rows here. Every other case
in this file is deliberately span-only (see the Scope disclosure section of
README.md); (j) is the sole exception and README.md's disclosure is worded
to say so.

Maintenance: update this file when cases, engines or gating rules change.
