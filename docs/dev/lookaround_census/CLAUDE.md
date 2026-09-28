# docs/dev/lookaround_census/ — [UCP] lookaround SHAPE census, lane lacensus

Backs `docs/dev/lookaround_census.md`. Study only: never built or run by
pcrec's `make`; has no dependency on `src/` beyond invoking `build/pcrec
--list-source` (a light metadata read, not a compile).

## Files

- `shape_classify.py` — a from-scratch recursive-descent PCRE-lite parser
  (no pcrec dependency) that classifies every lookaround OCCURRENCE in a
  pattern's raw text by SHAPE: (a) single char/class width 1, (b) fixed
  width k>1 (or k=0, an empty body), (c) bounded variable width, (d)
  unbounded, (e) contains a capture/backref/call/nested lookaround (worst,
  overrides width). Recognizes all six of `src/parse/mod_lookaround.c`'s
  accepted spellings (`(?=` `(?!` `(?*` `(?<=` `(?<!` `(?<*`) plus their
  alpha-verb aliases (`(*pla:` etc.). Library entry points:
  `classify_pattern(pattern_bytes) -> [occurrence dict, ...]`,
  `worst_shape(occurrences)`. Also runnable standalone, one pattern per
  stdin line, for spot checks.
- `build_census.py PCREC TREE BENCH OUTDIR` — reproduces `studies/
  ucp_study/`'s 492/1,101 "VM-only-because-of-lookaround" population from
  its own committed `census_13b7c202.tsv`/`census_nocap_13b7c202.tsv`
  (reused, not recompiled — `lookaround_census.md` S1 explains why that is
  sound at this pin), re-gathers every selected pattern's FULL untruncated
  text fresh (never the census TSV's own 200-byte-truncated pattern
  column), classifies it with `shape_classify.py`, and prints the S2-S4
  tables `lookaround_census.md` quotes. ~1.3s, no compile, no boxlock.
- `shapes_9399d927.tsv` — the classified population (493 rows: id, source,
  encoding, caseless, occurrence count, worst shape, ALL-(a)/ALL-(a-or-b≤2)
  flags, the view-anchor note, the shape set, shape-(b) k values, the full
  pattern text), from `build_census.py` at commit `9399d927`.
- `report_9399d927.txt` — the same run's stdout (S2-S4 tables), archived
  verbatim.

## Reproducing

```
python3 docs/dev/lookaround_census/build_census.py \
    build/pcrec . /path/to/pcrec-bench docs/dev/lookaround_census/out
```
from the repo root (needs a built `build/pcrec` and a checkout of
pcrec-bench; both read-only). Re-running at a later pin will move the
population if `tests/lookaround/`, `tests/utf8/`, or the bench's pattern
files change — diff `git diff --stat <old>..<new> -- tests/ examples/`
first (`lookaround_census.md` S1's own check) before trusting a stale
`census_13b7c202.tsv` reuse at a much later pin.
