# docs/dev/lanes/predspec23c_evidence/ — lane predspec23c's evidence (2026-11-17)

Evidence for `docs/design/predicates_draft.md` rev 23.1 (review r33's fixes; DESIGN ONLY) and
`docs/dev/lanes/predspec23c_report.md`. Historical after merge; never edited after.

## Files

- `predspec23c_model.py` — imports `../predspec23b_evidence/predspec23b_model.py` READ-ONLY (and through it
  predspec23's engine) and overrides ONE thing: the search order of `|` over filtered branches, end-major (predspec23b,
  unstated) -> BRANCH-MAJOR (the manager ruling **branch-order**, COND-FAMILY 2026-11-17 03:01 item (3)). Every answer
  in BOTH modes (WHOLE value; SEARCHED = candidate R22). PART 0 controls (the old order reproduces review r33's 125 and
  400); PART 1 `when` re-run, before/after per line; PART 2 F1 (L83 under NOT, the closing example's record twin);
  PART 3 F7 (`default.unused` (b)); PART 4 F8 (the empty-intersection error's domain); PART 5 F3; PART 6 F12 (NOT over
  a nested program); PART 7 F11/F4 (find-all; a filtered argument's hits); PART 8 F17 (nullable B); PART 9 the
  re-allowed-NOT sweep rows that needed a run.
- `predspec23c_model.out` — the forward run's output, the numbers rev 23.1 and the report quote.

Commands (swap check and its sabotage): the header of `predspec23c_model.py`.
