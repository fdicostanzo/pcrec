# docs/dev/optloop/lossreview/dfa/ — lane lrdfa's instruments and data (phase 1, DFA route)

The reading is `../dfa.md`. Nothing here reads a clock (the box was busy).
Every script takes its paths as arguments or env; the scratch (`L`) holds a
`git archive` copy of pcrec-bench with its generators run IN THE COPY
(`bench/`), the compiled artifacts (`art/`), the twins (`tw/`) and the waf
match inputs (`match/`).

- `population.py GAP_ROWS CAUSES > population.tsv` — the trailing population
  (vs jit or a scalar peer, or rust alone) from gaprep3's `gap_rows.json`
  with the route stamps; `population.tsv` is its output.
- `dfa_patterns.tsv` — the 50 DFA-route (set, pattern) pairs, utf8/litrun
  excluded.
- `compile_all.py PCREC BENCH LIST OUTDIR` — compiles them the bench's way
  (`--features all`) with `.facts`/`.ir` beside each `.c`.
- `facount.c`, `run_facount.sh` — COUNTED find-all: `rx_search` calls,
  matches, `memchr` calls and bytes examined (`-Wl,--wrap`).
- `ws_summary.py` — sums the walk_survey instrument's per-phase loads
  (`studies/walk_survey/run_pop.py`, `WSDRV=wsdrv5.c`) per cell.
- `join.py` → `cells.tsv` — bench ns + stamps + loads + counts per cell.
- `causes_dfa.tsv`, `rollup.py` → `data/rollup.tsv` — the cause rules and
  the per-cause TOTAL-loss roll-up.
- `twins/` — the hand twins: `mk_twin_dfa.py` (k101, k101plant, precheck,
  deferpre, hiskip), `mk_split.py` + `split_rx.c`/`.h` (the exact
  [OPT-ATTEMPT-SPLIT] twin), `mk_count.py` + `stepcount.c` (skip-entry
  counts), `p2spans.c` (libpcre2 10.46 span oracle), `check_twins.sh`
  (answers vs base AND libpcre2, with a planted control), `facount_twins.sh`
  (counted work per twin), `time_twins.sh` (OWED quiet-slot timing; never
  run by the lane; `DRYRUN=1` builds only). Re-uses
  `docs/dev/optloop/waf/` (`mk_twin.py`, `spans.c`, `mk_inputs.py`) and
  `studies/walk_survey/` (`landtwin.py`, `fatime.c`) by path.
- `data/` — the verbatim outputs: `check_twins.log`, `facount_base.tsv`,
  `facount_twins.txt`, `stepcount.txt`, `ws_summary.tsv`, `ws_dfa.tsv.gz`,
  `rollup.tsv`, `cell_table.md`.
