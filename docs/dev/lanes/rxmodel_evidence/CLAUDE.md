# docs/dev/lanes/rxmodel_evidence/ — lane rxmodel's evidence (2026-11-17)

Evidence for `docs/dev/lanes/rxmodel_report.md`: a REGEX MODEL for each open choice of the predicate language
(`docs/design/predicates_draft.md` R.8 and lane pathimpact's E1-E7), RUN on the installed libpcre2-8 and compared with
lane pathimpact's engine running each candidate reading. DESIGN EVIDENCE ONLY; rules nothing. Historical after merge;
never edited after.

## Files

- `pcre2h.py` — a ctypes harness on libpcre2-8 (the library is run, never read: D181): compile, WHOLE / SEARCHED /
  FIND-ALL, string callouts `(?C"name")` served by Python functions that see the captures by name, the match start
  and the current position, and answer "continue" or "fail here". `selfcheck()` verifies the option values it uses
  and the callout-as-condition form by behaviour.
- `rxmodel.py` — the models. Loads `../pathimpact_evidence/pathimpact_model.py`'s definitions in memory (its text up
  to PART A, plus named blocks, never edited) and prints, per model: the PCRE2 pattern, its answers on a WHOLE value,
  a SEARCHED text and a FIND-ALL text, and its comparison with each engine candidate over a text set (counts per
  mode, first difference). `RXMODEL_SABOTAGE=1` inverts every callout (the comparisons must move).
- `rxmodel.out` — the forward run's output (about 30 seconds).

Commands: the report's COMMANDS section.
