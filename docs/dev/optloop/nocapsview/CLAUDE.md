# docs/dev/optloop/nocapsview/ — the nocaps-vs-nocaps ledger's reproduction pieces

Lane `nocapsview`, 2026-09-23. Reproduction for
`../cycle1_nocaps_view.md` — the nocaps-vs-nocaps half of D119's
two-class-pure-ledger ruling (`docs/dev/decisions.md` addendum,
2026-09-23), paired with `../cycle1_caps_view.md`'s caps-vs-caps half.
**REVISED** same day to use pcrec-bench's own authoritative classification
table (I-99/I-100) — `rust-default` moved from caps into the NOCAPS
scored class — and to add Frank's standing cross-class anomaly query
(I-101).

## Files

- `build_nocaps_view.py` — reads `../cycle1_rows.tsv` (the 125-row ranked
  population and its class weights, unchanged from cycle 1) and two
  pcrec-bench report files: the BEFORE report (`2026-09-20-capability-0.1-
  budu-ryzen1600-fullroster-25b1984f.tsv`, the only report that ever
  measured `libpcre2_10.46_dfa-nocaps-simdna`, and the only one carrying
  `pcre2-interp`/`pcre2-jit`/`re2`/`re2-longest`/`tre`) and the AFTER
  report (`2026-09-23-capability-0.1-budu-ryzen1600-after-8d716693.tsv`,
  both pcrec pins measured together in one window, but only
  `oniguruma`/`rust`/`vectorscan` as non-pcrec testees). Nothing
  recompiled, nothing re-measured — pure re-parse of committed report
  TSVs. Computes THREE things: (1) the main NOCAPS ranking, `auto-nocaps`
  scored against `best_of({pcre2-dfa, rust-default})` per the frozen
  classification (`NOCAPS_SCORED` in the script); (2) the paired
  same-window pcrec-only Δ% from the AFTER report's own two pcrec-pin
  columns; (3) the §6 cross-class anomaly data — `auto-nocaps` against
  `best_of(YES_TESTEES)` (`pcre2-interp`, `pcre2-jit`, `re2-default`,
  `re2-longest`, `oniguruma`, `tre`), plus each cell's `min_ns`/`max_ns`
  for the within-window range clearance check. Unlike `capsview.py`'s
  `SP`-scratchpad convention, this script's paths are hard-coded absolute
  paths under `/Users/fdicostanzo` and need no re-pointing to re-run, as
  long as the two report files and `cycle1_rows.tsv` still exist there.
- `nocaps_rows.json` — one record per one of the 125 ranked cells: family,
  weight, the pcrec/`pcre2-dfa`/`rust` medians and mins/maxes for both
  pins, `before_ratio`/`before_score`/`after_ratio`/`after_score` against
  the best-of-two NOCAPS competitor (with `before_nocaps_competitor`/
  `after_nocaps_competitor` naming WHICH of the two won each cell),
  `delta_pct` (the paired same-window pcrec-only Δ%), and the §6 fields
  (`before_yes_best_testee`/`_ns`, `after_yes_best_testee`/`_ns`, the
  `*_competitor_max_ns`/`*_nocaps_min_ns`/`*_nocaps_max_ns` range-clearance
  inputs, `before_rust_ns`/`after_rust_ns` as the informational secondary
  check, and `before_caps_vs_nocaps_competitor`/`after_...` for the §6.6
  mirror). Read this rather than re-deriving a number from the markdown
  tables.
- `nocaps_rows.tsv` — the same data as a flat TSV.

Everything here is read-only with respect to
`/Users/fdicostanzo/pcrec-bench`: the script reads its committed report
files and its `docs/dev/inbox_from_pcrec.md` (cited, not parsed
programmatically — the classification is hand-transcribed into the
script's `NOCAPS_SCORED`/`YES_TESTEES` constants from that file's I-99/
I-100 text) and writes nothing there.
