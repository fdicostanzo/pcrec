# tests/findings/data_census/ — [KNOW-SRC] K0's data-mover census fixtures

`scripts/emit_sweep.py --data` (docs/design/measure_sets.md rev 3 §9.3)
reproduces a HAND-MADE movers list on each fixture change below. Each list
was written from the change's meaning BEFORE the census ran; its header says
the reasoning.

- `fx_bundles.py DIR` — writes the fixture change, `DIR/old/fx.rxt` and
  `DIR/new/fx.rxt`: one analysis bundle `fx` in two versions, `Z` rare and
  `@` common, then the reverse, every other count identical (so every other
  byte's normalized rate is identical too). Written per run, never
  committed: a committed `.rxt` joins the corpus that every population pin
  counts (res_fixtures.py's precedent).
- `patterns.txt` — the analysis fixture's population (5 patterns).
- `analysis_movers.tsv` — its hand-made list: the two patterns with both `Z`
  and `@` necessary, at both bases, on both engines (8 movers). Checked by
  `run_findings_tests.sh` §13 on every `make test-findings`.
- `limits_patterns.txt`, `limits_movers.tsv` — the limits fixture:
  `PCREC_MAX_AUTO_DFA_ELEMS` 30000000 -> 3000 (emit_sweep's own `lowdfa`
  value); only `lowdfa`'s witness moves, on the default engine, at both
  bases. NOT in `make test` (the arm builds two `git archive` trees); re-run:

      python3 scripts/emit_sweep.py --data limits \
          PCREC_MAX_AUTO_DFA_ELEMS=30000000 PCREC_MAX_AUTO_DFA_ELEMS=3000 \
          --ref HEAD --no-corpus \
          --patterns-file tests/findings/data_census/limits_patterns.txt \
          --expect-movers tests/findings/data_census/limits_movers.tsv

Maintenance: update this file when files are added/removed or their roles
change.
