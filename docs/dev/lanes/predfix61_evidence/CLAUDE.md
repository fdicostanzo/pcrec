# docs/dev/lanes/predfix61_evidence/ — lane predfix61's evidence

Evidence for docs/dev/lanes/predfix61_report.md: review r61's FIX-NOW items applied to the predicate documents and
the run lines of four new open pieces (flat-read-outside, bare-nested-scope, array-vs-passes, class-hole-order).
Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predfix61_model.py` — STANDALONE python3 `re` model. (1) A small backtracking label matcher (the documents'
  label rules: branchings reset, pass-start read, a hole reads labels as they stand, unset fails a comparison and
  NOT of it holds) builds each program from its text, with a LEXICAL variant for the nested-scope question;
  (2) lane predasc's enumerate and nested-loop lift, copied. Every three-mode line it formats must occur verbatim
  in the documents (DOC). Control: python `re` on the review coordinator's hand regexes (CONTROL), the record's
  words (QUOTES). Run: `timeout 110 python3 -I -B <this dir>/predfix61_model.py`. `PREDFIX61_SABOTAGE=sN`
  (s1..s13, its header) plants one wrong rule or fact.
- `predfix61_model.out` — the committed clean run (15 checks, 0 failed).
- `predfix61_sabotage.out` — the 13 plants, each run alone, each CAUGHT by its target check, no traceback.

Lane files are historical after merge; never edited then.
