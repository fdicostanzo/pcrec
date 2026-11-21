# docs/dev/lanes/preddoc3b_evidence/ — lane preddoc3b's evidence

Evidence for docs/dev/lanes/preddoc3b_report.md: the conversion of core.md's values, arrays, operators,
diagnostics and spellings sections and the new core/modules section (2026-11-19). Design evidence only;
nothing here rules, and no check under `make` reads it.

## Files

- `preddoc3b_model.py` — python3 `re` model: runs every example line of those sections in WHOLE, SEARCHED and
  FIND-ALL, requires each formatted line to occur verbatim in core.md, runs each named rival, and checks the
  manager's readings 1-2, the slug list and that no `?`/skeleton piece is left. Run:
  `timeout 300 python3 -I -B <this dir>/preddoc3b_model.py`. `PREDDOC3B_SABOTAGE=sN` plants one wrong rule.
- `preddoc3b_model.out` — the committed clean run (17 checks, 0 failed).
- `preddoc3b_sabotage.out` — the 17 plants, each run alone, each caught by its target check.

Lane files are historical after merge; never edited then.
