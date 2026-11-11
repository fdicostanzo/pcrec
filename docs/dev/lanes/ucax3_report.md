# ucax3 report

## STATE AT HANDOFF
- Merged main (clean, rc 0). Fixed tests/axes/utfcheck_arm.py `cell()`: all case kinds
  (m n ms ns mc mg gu, `under` prefix, `@file:` subjects, `pattern-esc` blocks), subject
  parsed by quote-aware `unquote` (no whitespace regex). Unplaceable line raises and is
  counted `unplaced` AND `fail`, printed `UNPLACEABLE file:line ...`.
- Control: island_illformed.rxt (1325 cells, both dumps) old arm fail=336 unplaced=391;
  new arm fail=0 agree=1325. Planted bad kind `zz` and unterminated `mg "a`: both fail loudly
  with file:line. Full corpus dump (76406 cells): unplaced=0.
- make strict green. Cloud axes run dispatched (see deliver commit); expected only the
  known `-fprefilter` 3 lost-other red. Verdict OWED via monread/queuewatch.
- Not done: cloud_gather.sh FAIL-grep anchoring (diag note 5) left untouched, out of brief.
