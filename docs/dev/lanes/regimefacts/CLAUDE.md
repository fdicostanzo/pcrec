# docs/dev/lanes/regimefacts/ — scripts and outputs behind regimefacts_report.md

Facts-only lane (2026-10-13): no clock read, no pcrec build. All scripts are pure readers (`python3 -I`); inputs are read-only (the kit's `worktrees/memfn-slot/spike1` logs, `pcrec-bench/reports`, `pcrec-bench/bench/*/manifest*.tsv` and `expectations.tsv`).

- `fit_vecspike.py` / `fit_vecspike.out` — F, c_byte, n* per form from the vecspike time.log; per-match fixed cost; 3-term OLS.
- `bench_population.py` / `population.tsv` — 30,117 measured pcrec cells joined with subject lengths (which report and testee per subbench is its SPEC table).
- `floor_fits.py` / `floor_fits.out` — the bench `floor` series: empty-call floor, memchr-class slope, litrun per-landing law.
- `classify.py` / `classify.out`, `setgrain.py` / `setgrain.out`, `density.py` / `density.out` — the population by length band, set-grain cell, and match gap.
