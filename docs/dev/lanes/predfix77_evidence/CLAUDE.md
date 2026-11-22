# docs/dev/lanes/predfix77_evidence/ — lane predfix77's evidence

Evidence for docs/dev/lanes/predfix77_report.md: review r77's ruled dispositions (predfold1121) applied to the
predicate documents, with the owner's array-in-piece ruling (b) of 2026-11-22 and the manager's readings tested.
Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predfix77_model.py` — STANDALONE python3 model. A lowerer (the expression language, `/rx/` with holes, `[x = E]`,
  `|`, `&`, `SEQ`, postfix loops, bound names and macros; the library bodies `occurrences`, `rx.repeat`, `rx.digit`,
  `rx.digits`, `chars`, `nchars`, `any_case` read from library.md) feeds lane predarr's label matcher (copied),
  extended with definition SCOPES (a used binding or macro body is a scope of its own; a group sets its label for
  every enclosing scope), `0` marks, group questions evaluated at their point, and `(?i:..)`. A duplicated-name
  check runs libpcre2-8 through ../rxmodel_evidence/pcre2h.py (run, never read: D181). Every three-mode line it
  formats must occur verbatim in the documents or the report (DOC). Controls: python `re` on independent hand
  regexes, direct counts, libpcre2-8, the record's words and pasted lines.
  Run: `timeout 300 python3 -I -B <this dir>/predfix77_model.py`. `PREDFIX77_SABOTAGE=sN` (s1..s20, its header)
  plants one wrong rule or fact, one per check.
- `predfix77_model.out` — the committed clean run (20 checks, 0 failed).
- `predfix77_sabotage.out` — the 20 plants, each run alone, each CAUGHT by its target check, no traceback.

Lane files are historical after merge; never edited then.
