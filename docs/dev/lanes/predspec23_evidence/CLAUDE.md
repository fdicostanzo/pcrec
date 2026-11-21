# docs/dev/lanes/predspec23_evidence/ — lane predspec23's evidence (2026-11-16)

Evidence for `docs/design/predicates_draft.md` rev 23 (DESIGN ONLY) and `docs/dev/lanes/predspec23_report.md`.
Historical after merge; never edited after.

## Files

- `predspec23_model.py` — the ruled condition model as an evaluator (rows are potential matches; three-valued
  conditions with Kleene `&` and NOT; per-test defaults; `$a` reads the real label; complement after `&` =
  pattern difference). Every answer is printed in BOTH modes: WHOLE (the row is the whole value) and SEARCHED
  (candidate R22 of `searchrow_evidence/searchrow.py`, the searched reference). NOT on a condition is new here,
  implemented from the 23:48 record's text. The draft's own readings it implements (R1, Kleene AND over passes,
  `some` = EXISTS over real passes) are listed in its header. PART 1 the definition block's examples; PART 2-3
  the three spellings (pools SV 341, REP 364, T2 11,110); PART 4 rev 22's closing example rewritten (1,111 lists);
  PART 5 zero passes. `PREDSPEC23_SWAP=1` reverses every order (the run must print the same lines);
  `PREDSPEC23_SABOTAGE=1` makes Kleene AND order-dependent (the swap run then differs).
- `predspec23_model.out` — the forward run's output, the numbers rev 23 and the report quote.

Commands: the header of `predspec23_model.py`.
