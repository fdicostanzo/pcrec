# docs/dev/optloop/revend/ — `[OPT-REVEND]`'s census instruments and outputs

Reproduction pieces behind `../revend_census.md` (lane `revend`, 2026-10-05):
the D77 census of the END-ANCHORED, start-unanchored population a
reverse-from-end search could serve. Compile-side, plus one scratch-tier
timing block. Everything ran on ubuntubudu (gcc 15.2) from a `git archive` of
the branch under `scratch_lx/revend/`; pcrec-bench was read, never written.

- `revend_probe.c` — links `libpcrec.a` (`gcc -O1 -Ilib -Isrc ... build/libpcrec.a`);
  a copy of `src/facts/endwin.c`'s `ew_walk` with `(?m)$` kept as its own
  level, plus widths, a leading-unbounded flag, `\G`. Cross-checked against
  the shipped fact by `census.py`.
- `census.py` — builds the bench (`bench/*/patterns/*.rx`) and corpus
  (`--list-source`, each block's own encoding/flags) populations, runs the
  probe and `pcrec --emit-facts` (env: `PCREC PROBE BENCH CORPUS OUT`,
  `FACTS_ALL=1` for the converse cross-check), writes `census_rows.tsv`.
- `analyze.py` — classes S/B/UL/UI/G/F, the cross-check, stamps; its verbatim
  output is `summary.txt`.
- `bench_cells.py` — the round-1 (`c4c70f2c`, O-83) report cells of every
  end-pinned bench pattern: `bench_cells.tsv`.
- `mksubj.py`, `timedrv.c`, `run_timing.sh` — the scratch-tier 1 MiB timing of
  today's search; verbatim `timing_linux.txt`.
- `census_rows.tsv.gz` — every probed pattern (4,857 rows) with the probe and
  facts columns; `pattern_hex` is the pattern's bytes.

Regenerating `census_rows.tsv.gz` moves `summary.txt`, `bench_cells.tsv` and
every number in `../revend_census.md` §3; `timing_linux.txt` is independent.
