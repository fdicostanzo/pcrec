# docs/dev/lanes/predasc_evidence/ — lane predasc's evidence

Evidence for docs/dev/lanes/predasc_report.md: the owner's ruling "quantified-order: PCRE's priority order; and classes
lowest to highest; sorting only when asked" (2026-11-19) folded into the predicate documents. Design evidence only;
nothing here rules, and no check under `make` reads it.

## Files

- `predasc_model.py` — STANDALONE python3 `re` model, lane predloop's model with the class order turned to ascending.
  A generic `enumerate` (PCRE priority order, a class lowest to highest) and the nested-loop lift build every
  example's alternation from its expression text; each line is run in WHOLE, SEARCHED and FIND-ALL and must occur
  verbatim in core.md or library.md. Controls: the documents at the base commit 5a299d40d (read by `git show`; the
  changed and unchanged printed answers), the record's printed asc.py answers, the rx itself (re-join; a class's
  members in shuffled orders). Run: `timeout 300 python3 -I -B <this dir>/predasc_model.py`.
  `PREDASC_SABOTAGE=sN` (s1..s26, its header) plants one wrong rule or document fact.
- `predasc_model.out` — the committed clean run (24 checks, 0 failed).
- `predasc_sabotage.out` — the 26 plants, each run alone, each CAUGHT by its target check, no traceback.

Lane files are historical after merge; never edited then.
