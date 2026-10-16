# docs/dev/lanes/pcscope/ — lane pcscope's census instruments

Read-only scoping of D161 addendum 14's one window request, presence and handoff
side; the report is `../pcscope_report.md`.

- `census.py` — compiles every distinct corpus pattern (default, `--engine=vm`,
  `-e utf8`) and the rwquest questions with a `-DPCREC_CAND_TRACE` build of
  main, one row per artifact: the pre-check admission, site parts (gate, run
  tests, K65 set rest), handoff use and re-entry, and the route stamps.
- `kinds.py` — folds `census.py`'s rows into one presence/handoff kind per
  artifact; per-arm tallies, the give-up-exposed subset, rwquest kind x mode.

Outputs go to a gitignored `build/` directory; regenerate, never commit them.
