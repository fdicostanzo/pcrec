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
- **gate.sh** — the ratchet over compare.sh's own pcrec numbers.
- **floors.tsv** — per-case reference value AND per-case margin.
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
credited the gate with catching it. The ceiling is fixed rather than derived,
because the box's noise floor is ~10% no matter how tight one run looks. Each
run now prints, per case, the smallest regression its margin can catch.

Two known gaps, carried deliberately: case (d) matches at 0.99% of its buffer
so its "throughput" is exit latency (R2-B4, fixed in run_bench's sibling case
but not here), and gate.sh has no minimum-coverage floor beyond requiring that
every floor row was measured.

Maintenance: update this file when cases, engines or gating rules change.
