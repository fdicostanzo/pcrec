# studies/hyb_reseed_cal/shape/ — the O-81 slow-cell attribution probes

Lane `xcalldes` (2026-10-03, design only). The probes behind
`docs/design/xcall.md` §2-§4: what the bench's O-81 slow cells actually pay,
and the emitted-form variants priced against `-fno-hyb-reseed`. Scratch
tier; nothing here is built by `make` or run by `make test`.

## Files

- `README.md` — how to rebuild every row of `results/`.
- `sdrv.c` — the bench driver's three regimes over a subject list: `s` one
  search from 0 per subject (search_short), `f` find-all (throughput), `m`
  `rx_match_caps` at 0 (match). Compile with `-include <artifact>.h`.
- `cnt.c` — the counting driver for an instrumented artifact (calls, calls
  reaching the VM, attempts, failed attempts, re-seeds).
- `mkbound.py` — rewrites a shipped adaptive artifact into form F1 (one
  prefilter call site, a call-free step loop bounded by `step_end`) or F2
  (F1 with the run-state init on the entry pass only).
- `mkb3.py` — form F3: entry unchanged, the step budget as a position bound,
  the re-seed in a cold in-loop branch.
- `rr.sh` — the round-robin timer (6 launches of CELL.a and CELL.d each).
- `regen_bench_subjects.py` — regenerates pcrec-bench syntax@0.1's 42 short
  and 3 throughput subjects into a scratch directory, writing nothing into
  the bench checkout, sha256-verified against the bench manifests.
- `results/shape_2026-10-03.md` — every number xcall.md cites.
