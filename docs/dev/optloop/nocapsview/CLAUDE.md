# docs/dev/optloop/nocapsview/ — the nocaps-vs-nocaps ledger's reproduction pieces

Lane `nocapsview`, 2026-09-23. Reproduction for
`../cycle1_nocaps_view.md` — the nocaps-vs-nocaps half of D119's
two-class-pure-ledger ruling (`docs/dev/decisions.md` addendum,
2026-09-23), paired with `../cycle1_caps_view.md`'s caps-vs-caps half.

## Files

- `build_nocaps_view.py` — reads `../cycle1_rows.tsv` (the 125-row ranked
  population and its class weights, unchanged from cycle 1) and two
  pcrec-bench report files: the BEFORE report (`2026-09-20-capability-0.1-
  budu-ryzen1600-fullroster-25b1984f.tsv`, the only report that ever
  measured `libpcre2_10.46_dfa-nocaps-simdna`) and the AFTER report
  (`2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv`, both
  pcrec pins measured together in one window, no `pcre2-dfa` row at all).
  Nothing recompiled, nothing re-measured — pure re-parse of committed
  report TSVs. Unlike `capsview.py`'s `SP`-scratchpad convention, this
  script's paths are hard-coded absolute paths under `/Users/fdicostanzo`
  (both bench reports and this repo) and needs no re-pointing to re-run,
  as long as those two report files and `cycle1_rows.tsv` still exist at
  those paths.
- `nocaps_rows.json` — one record per one of the 125 ranked cells: family,
  weight, `before_nocaps_ns`/`dfa_ns`/`before_ratio`/`before_score`,
  `after_nocaps_ns`/`after_ratio`/`after_score`, and `delta_pct` (the
  PAIRED same-window pcrec-only Δ%, read from the AFTER report's own two
  pcrec-pin columns — the cleanest available before/after comparison,
  independent of the `pcre2-dfa` reuse question in §0's methodology
  note). Read this rather than re-deriving a number from the markdown
  tables.
- `nocaps_rows.tsv` — the same data as a flat TSV.

Everything here is read-only with respect to
`/Users/fdicostanzo/pcrec-bench`: the script reads its committed report
files and writes nothing there.
