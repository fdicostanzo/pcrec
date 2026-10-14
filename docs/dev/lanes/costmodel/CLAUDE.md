# docs/dev/lanes/costmodel/ — scripts, inputs and output behind costmodel_report.md

Analysis-only lane (2026-10-13, kit-manager-spawned): no clock is read and no
pcrec or kit build is made. Every script runs with `python3 -I`; inputs are
read-only copies of logs that earlier slots measured.

- `costmodel.py` — the whole analysis: regimes, the absolute re-score, the
  driver model and its fits, the density tables, the estimator, the decision
  table and its priced argmin, the per-source regret. Writes `analysis.txt`
  on stdout. `--price key=val ...` prices one hypothetical site against every
  row of the decision table (see its docstring).
- `cmload.py` — loaders and the compile-time facts per cell (cover terms,
  set size, site kind, the shipped prior summed over the set).
- `subjstats.py` / `subjstats.tsv` — subject facts per (cell, subject): byte
  density of the scanned set, landings, gap mean/CV, the walk's skip-run
  predictability (`skmode`). Reads the subject files.
- `analysis.txt` — `costmodel.py`'s output, cut into the report.
- `data/` — the measured inputs, copied byte for byte (`SHA256SUMS`): slot25c's
  ALPHA `time.log`, the spike's `time.log`/`time2.log`/`counts.tsv`/`counts2.tsv`
  and `counts9.txt`. The slot2 kernel sweep is read from its branch copy
  `docs/design/memfn/probes/r17/out/slot2/times.tsv`.
- `count9.sh`, `count_instrument.py`, `count_cnt.c` — rebuild `data/counts9.txt`:
  lane r17loss's counting instrument (copied verbatim) over all nine subjects.
  Its 80 slot25c lines equal r17loss's `counts.txt` byte for byte; re-running
  the script reproduces `counts9.txt` byte for byte.
