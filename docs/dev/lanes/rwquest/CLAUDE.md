# rwquest/ — blinded user questions over the real-world corpus ([REGIME-CORPUS])

Lane `rwquest` (2026-10-14). 177 regex questions a user would ask of the seven
corpus classes in `worktrees/.corpus/` (logs, code, prose, structured, markup,
nonenglish, binary), written from the DATA and plausible intent, not from
engine internals. Report: `../rwquest_report.md`.

- `questions.src` — the hand-written input, one question per line, fields
  separated by ` ||| `: id, class, files (`;`), intent, flags (`-` or `,`-list of
  i m s utf ucp), mode (find-all / first / count / line), guessed frequency
  (rare / some / many / everywhere), PCRE2 pattern, optional python-`re`
  equivalent for patterns python cannot express (`\p{..}`, `\x{..}`).
- `check.py` — `python3 -I check.py` (reads only `questions.src` and the corpus
  files, never executes corpus content) compiles each pattern with python `re`
  and counts matches on a 4 MiB head sample and on the whole file (<= 64 MiB).
  Writes `questions.tsv`. Semantics per mode are in its docstring.
- `questions.tsv` — the generated table (pattern text contains raw `"`:
  parse with no CSV quoting). Columns: id, class, files, intent, pattern, flags,
  mode, guess_frequency, py_status, py_count_sample, py_count_full,
  sample_bytes, file_bytes, matches per MiB (sample / full),
  observed_frequency, first_match_offset_sample, py_equiv_pattern, seconds.

Counts are for the FIRST file listed only. python `re` is not PCRE2: the table
records python's answer, not an oracle's. Regenerate with `check.py` after any
edit to `questions.src`; never edit `questions.tsv` by hand.
