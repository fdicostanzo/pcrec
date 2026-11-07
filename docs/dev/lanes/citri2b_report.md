# citri2b (2026-11-07) — CI run 42393813165 (f09ae836a) red on test (3/3)

Lane citri2 (sonnet). NOTE: `citri2_report.md` already exists (2026-10-13, strict/gcc13), so this report is `citri2b_report.md` and the deliver file was edited to match.

## Failures

Job "test (3/3)" (id 128466881034), step `make test-shard`. Shards 1 and 2 green. ONE make error line: `Makefile:1198: test-lookaround` (the `test-shard` line is its parent). Everything else in the shard passed.

1. `test-lookaround` §5 (`tests/lookaround/vlb_one.sh`): `FAIL utf8-invalid (?<*(.{1,3}))b — 2 of 36 cells differ`. Cause class: CI-oracle difference, SAME mechanism as U25 (vanilla libpcre2 10.46 interpreter steps a variable-length lookbehind across the invalid-UTF barrier), not a pcrec regression. Evidence: the log shows twice `vlb_one.sh: line 60: [: 18446744073709551614: integer expected` — in the tolerance's `-lt` test, the oracle's group-1 START is 2^64-2 (the backwards scan underflowed past subject start) in 2 cells; the 5-cell U25 tolerance only handled a numerically earlier start, and bash `-lt` cannot compare a 20-digit value, so those 2 cells stayed divergent. The other 3 tolerated cells passed; the printed "first" cell is a tolerated one (it prints raw mine/theirs). Which 2 cells wrapped cannot be seen in the log (probably the inferred `a9c3a962` ones); not reproducible here (patched 10.46).
   Fix (small, in worktree): `tests/lookaround/vlb_one.sh` accepts a 20-digit (wrapped) oracle group-1 start as "earlier"; all other conditions (pinned pattern, mode, pcrec answer, equal span and group end) unchanged; comment cites the run. U25 in `docs/dev/upstream_issues.md` gets an addendum. Verification is the next CI run (vanilla is unavailable here); if it stays red, the wrapped cells' other fields differ and the failing cell lines are needed.

No real answer regression found; no src/ edits.

## STATE AT HANDOFF

Rulings file citri2_rulings.md: empty. Commit on lane/citri2; not pushed. Only `bash -n` and a regex check were run (the tolerance is unreachable locally).
OWED: none
