# docs/dev/lanes/defscope_evidence/ — lane defscope's evidence (2026-11-16)

Evidence for `docs/design/condition_kind.md` Part III (the SCOPE of a default in the model without the mark; an
EXPLORATION, rules nothing) and `docs/dev/lanes/defscope_report.md`. Historical after merge; never edited after.

## Files

- `defscope_options.py` — exec's lane condkind2's script (`../condkind2_evidence/condkind2_nomark.py`, unedited,
  which exec's lane condkind's engine) for its pools, codings, rev 22 targets and one-pass evaluator, then runs
  every scope option (LOCAL per test, COLUMN per label for the statement, POS positional, DOLLAR `$` reads the
  statement's default, DECL declared at the label's definition) with its own program evaluator: the battery
  (PART 1), the rewrite run under each option (PART 2), "all" without the mark (PART 3). `DEFSCOPE_SWAP=1`
  reverses every order (the engines' too; the run must print the same lines); `DEFSCOPE_SABOTAGE=1` evaluates
  COLUMN positionally in engine order (the swap run must then differ).
- `defscope_options.out` — the forward run's output, the numbers the note and the report quote.

Inputs: the rev 22 reference TSV made by `../condkind_evidence/rev22_ref.py` (scratch, not committed).
Commands: the header of `defscope_options.py`.
