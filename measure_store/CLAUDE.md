# measure_store/ — the committed MEASUREMENT SETS ([MEASURE-SET], D166)

The store `--measures=NAME` and every bare compile read
(`docs/design/measure_sets.md` §2; `docs/spec/measures.md` is the contract).
`oracle_store/`'s shape applied to data derived by RUNNING pcrec's kit and
engines on a box: one directory per set id, one per revision, a self-checking
`set.tsv` and its `PROVENANCE.md`. A committed revision is IMMUTABLE: a
re-reading of the same cells is a new `rev`, a re-measure a new id.

| file | role |
|---|---|
| `<id>/<rev>/set.tsv` | the set, in its CANONICAL form (R4: `pcrec --list-measurements=<the file>` reproduces it byte for byte; the NAME's view is the cell-less embed, the file minus its `cells` rows); self-checking `rows` and `values_digest` |
| `<id>/<rev>/PROVENANCE.md` | the run, the method, how the file was written, its sha-256, what derives from it |
| `DEFAULTS` | one line per class, `<class> TAB <id>@<rev>`: the set a bare compile of that class reads. One row (`idk`, a compile that declares no class) until M2 |
| `DEFAULTS.log` | append-only, one row per `DEFAULTS` transition (seq, class, old, new, its movers file); `DEFAULTS` is each class's last row |
| `movers/<seq>.tsv` | the census of transition `seq`, written once by the commit that makes it, immutable; written by the census tool its own header names (0001 `docs/dev/lanes/m0build/census.py`, 0002 `docs/design/memfn/span_cards/slot/movers.py`) until emit_sweep's `measures` data kind (M1) |
| `index.tsv` | one row per committed revision: id, rev, class, box, tier, composite, method, supersedes, values_digest, file sha-256, status |
| `from_interim.py` | the ONE-TIME conversion that wrote `zen4-grid1/1` from the kit's interim set (its PROVENANCE.md has the command) |

**The embed.** `make gen-measures` (called from `make gen-tables`) writes
`src/core/measures_store.inc` (every committed set's TEXT, `scripts/embed_text.sh`)
and `src/core/measures_table.inc` (its PRE-PARSE and the `DEFAULTS` table,
`scripts/ksgen.c measures`, the library's own reader). The embed is CELL-LESS
(`measures.md` §8¶2): the text is each file stripped of its `cells` rows by the
Makefile's strip step, the pre-parse has no cell, and ksgen records each file's
cell count (`--list-measurements`' `file_cells`). Both are committed and
`make gen-tables && git diff --exit-code` is the drift gate; `tests/knowledge/`
checks every set file against `index.tsv`'s sha-256 and digest and against its
canonical view, re-runs the generation, and recomputes every format-2 set from
its cells and run record (`meas_recompute.py`).

Sets today: `zen4-grid1@1` (format 1, scratch) and `zen4-grid3@1` (format 2,
scratch, span_pick stage 2's cards; the `idk` default since `DEFAULTS.log` row 2).
