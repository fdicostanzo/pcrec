# docs/dev/lanes/predscope_evidence/ — lane predscope's evidence

Evidence for docs/dev/lanes/predscope_report.md: the owner's rulings of 2026-11-21 (pure-label, the `_` labels,
zero-in-definition, his three scope examples) folded into the predicate documents, and the manager's readings of
that day tested. Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predscope_model.py` — STANDALONE python3 `re` model. A mechanical lowerer (the expression text, macros as
  functions over rx text, the library bodies read from library.md) feeds lane predfix61's label matcher (copied;
  `\w`, the canonical-numeral domain and two scope nodes added for the closed variants); captures are tracked
  apart from labels. Every three-mode line it formats must occur verbatim in the documents (DOC). Controls: python
  `re` on independent hand regexes and on the codepoint range, the record's lines and words.
  Run: `timeout 110 python3 -I -B <this dir>/predscope_model.py`. `PREDSCOPE_SABOTAGE=sN` (s1..s21, its header)
  plants one wrong rule or fact.
- `predscope_model.out` — the committed clean run (20 checks, 0 failed).
- `predscope_sabotage.out` — the 21 plants, each run alone, each CAUGHT by its target check, no traceback.

Lane files are historical after merge; never edited then.
