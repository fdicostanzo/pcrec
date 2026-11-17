# docs/dev/lanes/predspec23d_evidence/ — lane predspec23d's evidence (2026-11-17)

Evidence for `docs/design/predicates_draft.md` rev 23.2 (review r34's fixes; DESIGN ONLY) and
`docs/dev/lanes/predspec23d_report.md`. Historical after merge; never edited after.

## Files

- `predspec23d_model.py` — review r34 A1: the earlier engines compared some numbers BY VALUE where the draft's §2.2
  reads an unpadded integer set as CANONICAL numerals. It READS the engines of lanes predspec23, predspec23b,
  predspec23c and searchrow (never edits them), replaces each value-compare site (listed in its header; each
  replacement must match exactly once), runs them in memory, and prints PART A (every line that moved, before = the
  committed .out, after = canonical), PART B (every engine line under §2.2, the numbers rev 23.2 quotes), PART X (the
  closing example with the re-chosen default `m = 0`) and PART Y (review r34's witnesses: branch-scope's three
  readings, find-all places, record-under-not and the completion alternative, polarity, De Morgan).
- `predspec23d_model.out` — the forward run's output.

Commands (swap check, its sabotage and the sabotage's measured reach): the header of `predspec23d_model.py`.
