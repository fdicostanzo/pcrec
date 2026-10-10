# studies/specclean/ — the match_api.md facts-only rewrite's safety net

Lane specclean (2026-10-09, `[SPEC-CLEAN]`). Reference material, never built
or run by `make`. Report: `docs/dev/lanes/specclean_report.md`.

## Files

- `claims.tsv` — THE LEDGER: every normative claim of the pre-rewrite
  `docs/spec/match_api.md` (aee1a570), with its status (MAPPED / POINTED /
  SUPERSEDED / HISTORY / INTERNAL / ELSEWHERE), the line and anchor in the
  rewritten doc at landing, and a note (evidence for every SUPERSEDED row).
  Header row; built by `build_ledger.py`.
- `claims_C1..C7.tsv` (+ `claims_C6a/b.tsv`, the C6 split for mapping) — the
  raw extraction by old line range; `EXTRACT_BRIEF.md` is the extractors'
  brief.
- `map_*.tsv` — the mappers' per-claim verdicts against the draft at
  848e6564; `MAP_BRIEF.md` is their brief.
- `resolutions.tsv` — the lane's resolution of every UNMAPPED / SUPERSEDED row
  (status, a locator string in the final doc, note).
- `build_ledger.py` — assembles `claims.tsv`; fails on any unmapped claim or
  unfound locator; carries draft line numbers to the final doc by a difflib
  alignment.
- `ANCHORS.txt` — the new doc's 151 anchors at landing, with their lines.
- `cites_1..7.tsv`, `part1..7.txt`, `CITE_BRIEF.md` — the inbound-citation
  re-pointing: per-occurrence log (file, line, old, new, status, note), the
  file partition, and the brief.
