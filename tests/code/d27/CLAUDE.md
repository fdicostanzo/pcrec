# tests/code/d27/ -- the D27 spec-first suite for embedded C

**[INLINE-C] stage 2, 2026-10-28 (lane ic2d27land).** Written from
`docs/spec/` (match_api.md §11.9-§11.10, cli.md §1.22, rxt_format.md §1.1,
pattern_language.md §7.12) by an author denied `src/` and `tests/` (D27);
every case cites its paragraph. The expectations are the author's as
written; only plumbing changed on landing. Arm 12 of `../run_code_tests.sh`
runs it (`make test-code`): floor 545 passes, 0 failures, and the control
(`PCREC=/bin/true`) must fail at least 100.

## Files

- `run.sh` -- the runner (`PCREC=... CC=... bash run.sh`; `D27_OUT` the work
  root, default `$TMPDIR/d27run`). It builds a scratch cell where `d27/rxt/`
  holds the fixtures renamed `.rxtin` -> `.rxt` (stored as `.rxt` they would
  join every `.rxt` corpus run), because the cases name file operands as
  `d27/rxt/NAME.rxt` and the `#line` expectations quote that spelling.
- `cli_cases.tsv` (CLI exit, diagnostic regex, written or not) and
  `match_cases.tsv` (compile, run, answer); `driver_*.c` -- the C drivers.
- `rxt/*.rxtin`, `hdr/` -- the file-operand and code-header fixtures.
- `REPORT.md` -- the author's record: coverage by paragraph, findings,
  spec gaps (the landing lane's disposition is
  `docs/dev/lanes/ic2d27land_report.md`).

Three rows pass because another rule refuses first (marked MASKED ROW).
