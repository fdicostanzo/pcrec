# docs/design/endmark/b3meas/ — B3 measured: today's rev-end vs a B3 hand twin

Lane b3meas (2026-10-12): the hard numbers behind "B3 saves a pass" (endmark.md
§2.3, D164 add. 3, review r3). Nothing here is built or run by `make`; run the
Python with `python3 -I` and `PYTHONDONTWRITEBYTECODE=1`. Report:
`docs/dev/lanes/b3meas_report.md`.

- `probe.c` — links `build/libpcrec.a`; builds pcrec's own minimized reverse DFAs
  for tag0 `X\z` and tag1 `X\n\z` (the pipeline `../b3cost_probe.c` uses) and dumps
  their tables. Build line in its header.
- `gen.py` — the driver (env and run line in its header). `pop` rebuilds the 266
  rev-end `$`/`\Z` population (b3cost's rule) and writes `results/population.tsv`
  (distinct by pattern/enc/icase, plus five idioms). `check` builds, per artifact,
  today's shipped artifact (`-p T`), its A/A copy (`-p A`) and the B3 twin (today's
  file with `T_search`'s body replaced by one tagged reverse walk: the
  Moore-minimized product of the two dumps, run-skip on self-loop states, the
  `mark_prio` fact classified empirically, verify-at otherwise) and the control R
  (today's algorithm over today's machine in the twin's code style, `-p R`);
  answer-checks all three against libpcre2 10.46 and counts subject loads
  (`harness.c -DCHECK`). `time` times today / A/A / twin / R per regime, pinned
  (`taskset`, env `CPU`). `states` records today's reverse machine size.
- `harness.c` — the per-artifact check (`-DCHECK`, links libpcre2-8) and timing
  (`-DTIME`) driver.
- `report.py` — aggregates `check.json` and `time.tsv` into the tables in
  `results/report.txt`.
- `results/` — `population.tsv`, `check.json` (per artifact: answers, loads per
  regime, tie observations, table bytes, search text size), `time.tsv` + `time2.tsv` (two independent runs; raw ns/call
  rows: k regime n iters today A B R, then the four minima), `states.json`, `report.txt`.
