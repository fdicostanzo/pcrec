# docs/dev/lanes/predspec23b_evidence/ — lane predspec23b's evidence (2026-11-17)

Evidence for the body of `docs/design/predicates_draft.md` rev 23 (DESIGN ONLY), completed by lane predspec23b,
and for `docs/dev/lanes/predspec23b_report.md`. Historical after merge; never edited after.

## Files

- `predspec23b_model.py` — imports `../predspec23_evidence/predspec23_model.py` READ-ONLY (its Kleene `&`/NOT and
  pools) and adds a small engine of the same shape whose pass rows carry every label of the pass. Every answer is
  printed in BOTH modes (WHOLE value; SEARCHED = candidate R22). PART 0 control lines (re-derives predspec23's and
  predspec21's T2 numbers); PART 1 §0.1 L94; PART 2 §2.6/§4.3 `occurrences` rows; PART 3 §4.3 the pairing rule;
  PART 4 §4.4 a computed label; PART 5 §8 `when`, the TM2-L list table, caveat (2); PART 6 §13 O28; PART 7 the two
  whole-text routes (find-all included). Route (i)'s reading of a condition inside a lookahead is the lane's own.
- `predspec23b_model.out` — the forward run's output, the numbers the draft and the report quote.

Commands (swap check and its sabotage): the header of `predspec23b_model.py`.
