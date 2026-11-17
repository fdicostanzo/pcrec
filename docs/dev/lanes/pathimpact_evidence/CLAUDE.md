# docs/dev/lanes/pathimpact_evidence/ — lane pathimpact's evidence (2026-11-17)

Evidence for `docs/dev/lanes/pathimpact_report.md`: what the owner's branch-scope ruling (reading (ii), COND-FAMILY
2026-11-17) does to `docs/design/predicates_draft.md` rev 23.2. DESIGN EVIDENCE ONLY; rules nothing, writes no draft
text. Historical after merge; never edited after.

## Files

- `pathimpact_model.py` — one script, standard library only (Python 3.14's `re._parser`). A PATH enumerator over
  Python's own parse of each regex lists every complete way it matches from a start in PCRE's preference order (PART
  A checks it against Python `re` on 14 regexes); a program evaluator applies the rule (a condition is one more piece:
  the first path whose conditions are all TRUE is reported) and, beside it, rev 23.2's reading (iii) and one parse (i).
  PART B re-runs the four earlier engines (predspec23, 23b, 23c, searchrow) through predspec23d's exec mechanism with
  path hooks and diffs against `predspec23d_model.out`; PART C the draft's worked lines; PART D the manager's claimed
  properties; PART E every OPEN candidate; PART F the R.8 owner questions; PART G the rulings-file R1 table
  formulation built independently. Every C/D/F line prints MOVED or same against (iii).
- `pathimpact_model.out` — the forward run's output (about 1.5 minutes).

Commands (swap check, sabotage and its measured reach, the rule switch `PATHIMPACT_READING=iii`): the header of
`pathimpact_model.py` and the report's COMMANDS section.
