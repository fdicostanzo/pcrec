# docs/dev/lanes/rxlib_evidence/ — lane rxlib's evidence (2026-11-17)

Evidence for `docs/dev/lanes/rxlib_report.md` and `docs/design/rx_module.md` (the owner's proposal: building patterns
without rx literals, an `rx` module and a sequence operator). DESIGN EVIDENCE ONLY; rules nothing. Historical after
merge; never edited after.

## Files

- `rxlib_check.py` — the construct definitions of the note's section 2 as code (one function per construct, each
  returning regex text; a condition is a callout where it is written), and the checks: PART A the libpcre2 harness's
  selfcheck (lane rxmodel's `../rxmodel_evidence/pcre2h.py`, imported, never edited); PART B the note's three
  before/after examples on libpcre2-8 in WHOLE / SEARCHED / FIND-ALL, each against an intent oracle on Python `re`;
  PART C the separator loop against a split oracle (two-copy and one-copy forms); PART D where a condition stands in a
  sequence; PART E what PCRE reads for a duplicate label name; PART F the quantifier operators (rulings R2); PART G every candidate of the note's section 7 examples. `RXLIB_SABOTAGE=1` breaks the loop and `optional`
  definitions (PART B must move).
- `rxlib_check.out` — the forward run's output (a few seconds).

Commands: the report's COMMANDS section.
