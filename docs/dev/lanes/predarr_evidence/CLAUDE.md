# docs/dev/lanes/predarr_evidence/ — lane predarr's evidence

Evidence for docs/dev/lanes/predarr_report.md: the owner's rulings of 2026-11-21 array-vs-passes (a) and
joint-in-some (agree) folded into the predicate documents, and the manager's readings of both entries tested.
Design evidence only; nothing here rules, and no check under `make` reads it.

## Files

- `predarr_model.py` — STANDALONE python3 `re` model. A small lowerer (`/rx/` with holes, `[x = E]`, `|`, `(E)+`,
  `E & C`, the library bodies `hits`, `chars`, `nchars`, `anything` read from library.md) feeds lane predfix61's
  label matcher (copied; lazy quantifiers, the atomic group, `\A` `\z`, `(?s:..)` and a joint condition added),
  which keeps every setting and every pass on the path. A group question is an end test read in one of four modes:
  settings (the ruling), passes (rejected (b)), byindex and byitem (joint-in-some's (a) and (b), not adopted).
  Every three-mode line it formats must occur verbatim in the documents (DOC). Controls: python `re` on
  independent hand regexes, python `re`'s finditer for the arrays, the record's lines and words.
  Run: `timeout 110 python3 -I -B <this dir>/predarr_model.py`. `PREDARR_SABOTAGE=sN` (s1..s17, its header)
  plants one wrong rule or fact.
- `predarr_model.out` — the committed clean run (17 checks, 0 failed).
- `predarr_sabotage.out` — the 17 plants, each run alone, each CAUGHT by its target check, no traceback.

Lane files are historical after merge; never edited then.
