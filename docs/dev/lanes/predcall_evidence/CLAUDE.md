# docs/dev/lanes/predcall_evidence/ — lane predcall's evidence

Evidence for docs/dev/lanes/predcall_report.md: the owner's call-prefix ruling (case 1: a macro's name qualifies the
labels its call surfaces) folded into the predicate documents, his leans on case 2 and closed-argument stated, his
statement "[ c = B(A) ] does not allow c.A", his second `hits` example, and the manager's readings (a)..(e) of the
lane brief tested. Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predcall_model.py` — STANDALONE python3 model. It LOADS lane predref's model by executing
  `../predref_evidence/predref_model.py` up to its line "the checks" (definitions only, unchanged; predref in turn
  loads predbound's lowerer and matcher), then adds MACRO-PREFIX (a pattern macro's call is a use of the macro's
  name, prefixing what the call surfaces, by binding-prefix's own mechanism) and ARG-COUNT (an argument counts as
  one use of its name in the caller's text). The record's pasted lines are read from the record. It also runs
  predref's model as a subprocess and names its red checks (PREDREF). Every line it formats must occur verbatim in
  the documents (DOC).
  Run: `timeout 300 python3 -I -B <this dir>/predcall_model.py`. `PREDCALL_SABOTAGE=sN` (s1..s12, its header)
  plants one wrong rule or fact per check.
- `predcall_model.out` — the committed clean run (13 checks, 0 failed).
- `predcall_sabotage.out` — the 12 plants, each run alone, each caught by its target check, no traceback.

Lane files are historical after merge; never edited then.
