# docs/dev/lanes/predref_evidence/ — lane predref's evidence

Evidence for docs/dev/lanes/predref_report.md: the owner's label-reference ruling ("required") swept over every
printed program of the predicate documents, the flat-read statements rewritten, and his helper-captures ruling
folded (a provided body's groups are labels only; the label-only group `(?<:x>...)` under construction). Design
evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predref_model.py` — STANDALONE python3 model. It LOADS lane predbound's lowerer and matcher by executing
  `../predbound_evidence/predbound_model.py` up to its line "the checks" (definitions only, unchanged), then adds
  the label-only group, `[\s\S]`, `atomic` and `hits` read from library.md, and the tuple comparison. SCAN is a
  textual label-reference checker over every backtick program span of the three base files, with the LEFT list
  (each span still bare, and why). The OLD printed lines are read from 915b47e64 by `git show`. Every line it
  formats must occur verbatim in the documents (DOC).
  Run: `timeout 300 python3 -I -B <this dir>/predref_model.py`. `PREDREF_SABOTAGE=sN` (s1..s10, its header)
  plants one wrong rule or fact per check.
- `predref_model.out` — the committed clean run (8 checks, 0 failed).
- `predref_sabotage.out` — the 10 plants, each run alone, each caught by its target check, no traceback.

Lane files are historical after merge; never edited then.
