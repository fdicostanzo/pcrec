# docs/dev/lookaround_census/ — [UCP] lookaround SHAPE census, lane lacensus;
# [CTX-PREFILTER]/[ENG-LOOK] step-0 censuses, lane lacens2

Backs `docs/dev/lookaround_census.md` (lane lacensus) and
`docs/dev/ctx_prefilter_census.md` / `docs/dev/eng_look_census.md` (lane
lacens2, both plan.md step-0 rows filed off this directory's own
population). Study only: never built or run by pcrec's `make`; has no
dependency on `src/` beyond invoking `build/pcrec --list-source`/
`--engine=dfa --no-captures --pattern` (light metadata reads and small
single-pattern compiles, never a corpus/suite run).

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
- `lac_engine.py` — lane lacens2's SHARED machinery for the two step-0
  censuses below: erasure of a lookaround construct from pattern text
  (including a trailing quantifier on the construct itself, e.g.
  `(?<=abc)*z`); TWO independent atom/body parsers (an EXACT-width one for
  [ENG-LOOK]'s fixed-k population, and a LOOSER one accepting the full PCRE
  quantifier grammar for [CTX-PREFILTER]'s shape-c/d population, each
  resolving a body to byte-level `frozenset`s, refusing rather than
  guessing anything unresolvable); a from-scratch NFA-then-subset-
  construction DFA builder (`build_ends_with_dfa`/`build_starts_with_dfa_
  reversed`/`build_delayed_accept_dfa`) for a body's "ends-with"/"starts-
  with"/"verify-next-k-bytes" recognizer; an exact BFS product-of-two-DFAs
  reachability walk; and a parser for pcrec's OWN generated C
  (`parse_pcrec_tables`) that recovers the real forward/reverse DFA
  transition tables (confirming `RX_DFA_TABLE "premultiplied"`
  empirically) for a REAL state-count baseline, never a modeled one. Own
  module docstring states exactly what each parser does and does not
  resolve.
- `eng_look_growth.py PCREC OUTDIR` — [ENG-LOOK] step 0 driver: for every
  k=2-4 fixed-width lookaround occurrence in `shapes_9399d927.tsv`, erases
  all of the pattern's lookarounds, compiles the erased form
  (`--engine=dfa --no-captures --features all`), and measures the exact
  state growth of folding the target occurrence's own body recognizer into
  the FORWARD machine (lookbehind) or REVERSE machine (lookahead, this
  census's own literal brief) AND, for lookahead, a second construction
  matching plan.md's own stated mechanism (a forward-pass "k-byte delayed
  acceptance") — see `docs/dev/eng_look_census.md` S3 for why these two
  lookahead numbers disagree and what that disagreement means.
  `eng_look_growth_61cbc894.tsv`/`eng_look_skipped_61cbc894.tsv` are this
  lane's own committed run (98 candidates, 97 compiled, 140
  occurrence-x-method rows).
- `ctx_prefilter_probe.py PCREC TREE OUTDIR` — [CTX-PREFILTER] step 0
  driver: over every pattern still VM-routed post-[UCP]-U2
  (`tests/ucp/ctxnode_route.tsv`), every POSITIVE shape-b/c/d lookaround
  occurrence's necessary first/last-byte set, whether it is NARROW (size
  <=8, or not already implied by the adjacent consuming atom — best-effort,
  `n/a` when that neighbor is not one simple atom), and an independence-
  model tightening estimate against `APPROACH.md`'s own prose as the
  representative subject (named and justified in
  `docs/dev/ctx_prefilter_census.md` S1 — the bench-derived share of this
  population is only 6 patterns). `ctx_prefilter_61cbc894.tsv`/
  `ctx_prefilter_skipped_61cbc894.tsv` are this lane's own committed run
  (146 positive multi-char occurrences over 354 VM-routed patterns).

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
