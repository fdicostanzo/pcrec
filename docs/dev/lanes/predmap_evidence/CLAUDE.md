# docs/dev/lanes/predmap_evidence/ — lane predmap's evidence

Evidence for docs/dev/lanes/predmap_report.md (a study of the map accessor `m[key]`, [COND-FAMILY]; nothing ruled).

- `predmap_runs.py` — python3 -I `re` model: each proposed form lowered mechanically (map = alternation of labelled elements, selection in the key's order, join = sequence, read key = finite expansion checked against a reading reference); three modes per case. Exits non-zero iff a declared expectation fails; last line `predmap_runs: N cases, K failed`.
- `predmap_runs.out` — its committed output; the report pastes lines by `[ID]`.

Design evidence only; no check under `make` reads it.
