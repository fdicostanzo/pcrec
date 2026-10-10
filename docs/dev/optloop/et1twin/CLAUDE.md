# docs/dev/optloop/et1twin/ — [ENG-TACTICS] stage 1's D77 trigger (lane et1twin, 2026-10-10)

The K12 recount under D151's gates and the reverse-inner HAND TWINS on the
top surviving DFA cells (D151 addendum 4). MEASUREMENT ONLY: nothing under
`src/` changes. The reading is `docs/dev/lanes/et1twin_report.md`. Every
number here is SCRATCH TIER (one Linux dev box, one pinned core).

## Files

- `recount.py` — Step A: classifies every K12 cell (G1, G2 as
  `where_to_start.md` §2.4 states it, the factor-free refinement, route and
  anchoring) and sums walk_survey's own `est_ns_K12` weights per verdict.
  Its hand table IS the G2 reading (no inner-split fact exists yet).
  `recount.txt` is its output.
- `k12_cells_now.tsv` — the K12 cells (default config) of
  `studies/walk_survey/analyze.py` re-run over walk_survey's instrument
  (`wsdrv5.c`, `m_gap`) on the K12 patterns at this lane's pin (c87d20af).
- `k12_census_now.tsv` — `studies/walk_survey/k12_census.py` at the pin
  (the static K12 population, 24 bench patterns).
- `twin.c` — the reverse-inner twin, generic over one cell: `#include`s the
  cell's UNMODIFIED artifact (`rx.c`: landmark scanner + anchored finish
  `rx_match_caps`) and pcrec's own artifact for `(?:P·L)\z` (`rxpl.c`, which
  [OPT-REVEND] compiles to a pure reverse walk: called with length `j+|L|`
  it is the reverse DFA over `P·L` seeded at the landmark, floored at
  `search_from`). Cell knobs `ET_LANDMARK`, `ET_LLEN`, `ET_LBYTE`.
- `etdrv.c` — the driver, built once per variant (`-DET_FN=rx_search` /
  `tw_search`): `ident` (find-all + every-startpos hashes), `spans`,
  `time` (median of batches, ns/call).
- `p2drv.c` — the libpcre2-8 (10.46, linked directly) side of `ident`.
- `build.sh` — emits and builds the three cells (ipv6, kvq, sfx64).
- `gen_adv.py` — 400 adversarial subjects per cell (landmark edges).
- `ident.sh` — o vs t vs p2 over bench short + throughput + adversarial
  subjects; `ident.txt` is its output.
- `time.sh` — the pinned-core interleaved timing; `times.tsv` its raw
  output, `summarize.py` / `times_summary.txt` the per-cell reading.

Bench subjects are regenerated in a `git archive` COPY of pcrec-bench
(generators run in the copy; throughput hashes checked against its
manifests); pcrec-bench itself is read only.
