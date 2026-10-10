# studies/specnum/ — the one-time numbering passes for docs/spec/match_api.md

Lane specnum (2026-10-09, `[SPEC-CLEAN]` numbering; Frank's ask: a spec is
cited like a legal code, by number that never changes). Reference material,
never built or run by `make`. The standing rule is docs/spec/CLAUDE.md's
"Numbering and citation"; the report is `docs/dev/lanes/specnum_report.md`.

## Files

- `number.py` — the labelling pass: reads `match_api.md` as lane specclean left
  it (`c2c11fa4`) and writes the numbered form (an `<a id>` line before every
  heading, `<a id="sN-pK"></a>[N¶K]` at the start of every paragraph, list
  item and block quote), plus the old-anchor map. It refuses an
  already-numbered file. The paragraph rule it applies is the one
  `tests/spec_history/specdoc.py` re-derives on every `make test`.
- `anchor_map.tsv` — old semantic `<a id>` (lane specclean's 151) -> the
  number it labelled, the new anchor id, and `section`/`paragraph`. A
  heading's old anchor maps to the section; an anchor that sat before a table
  or code block maps to the paragraph the block belongs to.
- `repoint.py` — the tree-wide rewrite of `match_api.md#anchor` and bare
  `#anchor` citations (a line that names `match_api`, or follows one within
  three lines) to `§N¶K`, collapsing `§S (§S¶k)` redundancy; markdown link
  targets keep an anchor (`#s6-3-4-p11`). Dry run by default, `--apply`.
