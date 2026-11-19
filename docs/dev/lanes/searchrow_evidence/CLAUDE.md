# docs/dev/lanes/searchrow_evidence/ — lane searchrow's evidence (2026-11-16)

Evidence for `docs/design/condition_kind.md` Part IV (what a result row and a complement are in SEARCHED mode; an
EXPLORATION, rules nothing) and `docs/dev/lanes/searchrow_report.md`. Historical after merge; never edited after.

## Files

- `searchrow.py` — its own span-level evaluator (Python `re` as the PCRE stand-in; D196's leftmost start, then the
  left operand's preference order of ends) for six candidates of the searched result row: R22 (rev 22: every
  filter, a complement too, may send the search to the next end), X (every span is a row), S (a complement per
  subject), M (PCRE's reported matches, then filtered, no retry), M+ (D196 retry for conditions; a complement removes
  finished rows), Mr (M+ with SQL EXCEPT on row identity). PART 1: the examples; PART 2: the counts.
  `SEARCHROW_SWAP=1` reverses every order (pools, candidates, condition and complement lists; the run must print the
  same lines); `SEARCHROW_SABOTAGE=1` leaks M+'s complement answer from one subject to the next (the swap run then
  differs). Earlier lanes' engines are whole-value only and are not imported (Part IV's standing questions say why).
- `searchrow.out` — the forward run's output, the numbers Part IV and the report quote.

Commands: the header of `searchrow.py`.
