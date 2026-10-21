# zen4-grid1@1 — provenance

- **What it is.** The first committed measurement set ([MEASURE-SET] M0,
  `docs/design/measure_sets.md` §10.1): the grid1 run's values (slot grid1,
  2026-10-13, AMD Ryzen 7 7700X, CPU 14, gcc 15.2.0 -O2, measured code
  `540649453`), read by gridread (`docs/dev/lanes/gridread_report.md` §2.1-§4.4)
  and published by the kit as its interim set
  `memfn/data/sets/kit-interim-grid1.tsv` (`cb545ae3e`, sha-256
  `7babfe59825a98cbdbd03d9070e616b80f913e64888b480627f4cfe3f0ee1f19`). Tier
  `scratch`: one box, a lane's slot, never an official bench run.
- **How it was written.** Two header values changed, nothing else:
  `python3 -I measure_store/from_interim.py memfn/data/sets/kit-interim-grid1.tsv > x.tsv`
  (`id` -> `zen4-grid1`; `values_digest` recomputed under
  `docs/spec/measures.md` §3's code table, where the interim hashed first
  letters), then `pcrec --list-measurements x.tsv > set.tsv`, the canonical
  writer (so the file is canonical by construction: R4).
- **sha-256 of `set.tsv`:**
  `d332967cc5aa0d499729c7977261a2e2adbb4194c16a987191c59160968d33de`
  (also `../../index.tsv`; checked by `tests/knowledge/`).
- **Method.** The cards are `kit-grid@1` (`memfn/data/cards/kit-grid.tsv`, R-MS5),
  copied into the set's `cards` section.
- **The raw cells.** The interim set carries no `cells` (the fitted/interpolated
  rows were read off gridread's tables, not refit from committed cells), so
  the `interp-log2` rows' recompute (§8.2) has no input here: they are labelled
  in their own `source` column and a recompute of them is owed to the set that
  replaces this one (zen4-grid2, D167).
- **What derives from it.** Every compile that names no set reads it (the
  `idk` row of `../../DEFAULTS`, §3.4: the LATEST set until M2), and the memfn
  kit receives its `kit.` rows on `mf_art_begin` (R-MS1). No routed kit row
  reads a set key before the kit's B4, so no artifact byte depends on its
  values yet; the `<PREFIX>_MEASURES` stamp is empty on every artifact until
  one does.
