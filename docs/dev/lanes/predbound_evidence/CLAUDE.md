# docs/dev/lanes/predbound_evidence/ — lane predbound's evidence

Evidence for docs/dev/lanes/predbound_report.md: the owner's rulings of 2026-11-22, bound-condition (b) and
count-in-set (b), folded into the predicate documents, and the manager's readings (a)..(h) of the lane brief
tested. Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predbound_model.py` — STANDALONE python3 model. Lane predfix77's lowerer and label matcher are copied in
  unchanged (between the two "copied from predfix77_model.py" marks; its own plants renamed so none fires,
  except s1); this lane's extensions follow: the ruling as a check AT THE BINDING (a body naming a label no
  pattern in it holds is refused, used or not), a value left of `:` (a `$` read, arithmetic, `count(c)`),
  comparisons against a value, `between` read from library.md, a member's `.index`. The OLD printed lines are
  read from the starting commit 1e0384941 by `git show` (FIVE). Every three-mode line it formats must occur
  verbatim in the documents (DOC). Controls: python `re` on hand regexes, direct counts, the record's words and
  its pasted line.
  Run: `timeout 300 python3 -I -B <this dir>/predbound_model.py`. `PREDBOUND_SABOTAGE=sN` (s1..s17, its
  header) plants one wrong rule or fact, one per check.
- `predbound_model.out` — the committed clean run (17 checks, 0 failed).
- `predbound_sabotage.out` — the 17 plants, each run alone, each caught by its target check, no traceback.

Lane files are historical after merge; never edited then.
