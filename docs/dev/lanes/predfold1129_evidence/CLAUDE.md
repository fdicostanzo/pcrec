# docs/dev/lanes/predfold1129_evidence/ — lane predfold1129's evidence

Evidence for docs/dev/lanes/predfold1129_report.md: the fold of seven owner rulings of 2026-11-28 (record
docs/design/plan_row_bodies/COND-FAMILY.md, reference-example-checked to same-path-last) into the predicate
documents. Design evidence only. Nothing here rules, and no check under `make` reads it.

## Files

- `predfold1129_model.py`: a STANDALONE python3 model, the successor of `../predfix113_evidence/predfix113_model.py`.
  It loads predfix113 unchanged up to its checks, then puts its own walker GATE129 (the one gate rule) and a
  mechanical regex builder MECH129 in front, switched by `X129[0]` (off: predfix113 as merged, the control).
  - `PREDFOLD1129_CENSUS=1` prints the census and exits 0.
- `predfold1129_census.out`: the census at the start commit 43bbce01f, committed BEFORE any document edit: every
  program printed on a three-mode or compile-error line of the six documents, the in-force engine against GATE129.

## Pinned commits

The model reads git only by commit id (START129 = 43bbce01f).

## Known limits

- The reader parses no label parameter, named list, `occurrences` call, `rx.repeat` or map form: those programs are
  counted as not parsed (the census says how many) and judged by hand in the report.
- Reads printed in bullet prose (not on a three-mode or compile-error line) are not in the census.

Lane files are historical after merge; never edited then.
