# docs/dev/lanes/predloop_evidence/ — lane predloop's evidence

Evidence for docs/dev/lanes/predloop_report.md: the owner's ruling "class-positions: nested loops, classes
descending" (2026-11-19) folded into the predicate documents. Design evidence only; nothing here rules, and no check
under `make` reads it.

## Files

- `predloop_model.py` — STANDALONE python3 `re` model. A generic `enumerate` (PCRE priority order, a class
  descending) and the nested-loop lift build every example's alternation from its expression text; each line is run
  in WHOLE, SEARCHED and FIND-ALL and must occur verbatim in core.md or library.md. Controls: the old rule's lists
  (class-order: longest and the open class-positions candidates), PCRE's own pattern for enumerate's re-join, the
  record's printed witness. Run: `timeout 300 python3 -I -B <this dir>/predloop_model.py`.
  `PREDLOOP_SABOTAGE=sN` (s1..s20, its header) plants one wrong rule or document fact.
- `predloop_model.out` — the committed clean run (20 checks, 0 failed).
- `predloop_sabotage.out` — the 20 plants, each run alone, each CAUGHT by its target check, no traceback.

Lane files are historical after merge; never edited then.
