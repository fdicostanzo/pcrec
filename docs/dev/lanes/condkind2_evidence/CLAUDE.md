# docs/dev/lanes/condkind2_evidence/ — lane condkind2's evidence (2026-11-16)

Evidence for `docs/design/condition_kind.md` Part II (the model WITHOUT the optional mark; an EXPLORATION, rules
nothing) and `docs/dev/lanes/condkind2_report.md`. Historical after merge; never edited after.

## Files

- `condkind2_nomark.py` — exec's lane condkind's engine (`../condkind_evidence/condkind_model.py`, unedited) for
  its pools, codings and rev 22 reference, then runs the NO-MARK model with its own one-row evaluator: the model's
  properties (PART 1), THE REWRITE RUN (PART 2: every marked program searched for a defaults-only rewrite giving
  rev 22's answers, by tier T0-T4), the default's scope (PART 3), silent drift (PART 4). `CONDKIND2_SWAP=1` reverses
  every order (the engine's too; the run must print the same lines); `CONDKIND2_SABOTAGE=1` makes the evaluator
  order-dependent (the swap run must then differ).
- `condkind2_nomark.out` — the forward run's output, the numbers the note and the report quote.

Inputs: the rev 22 reference TSV made by `../condkind_evidence/rev22_ref.py` (scratch, not committed).
Commands: the header of `condkind2_nomark.py`.
