# tests/known_fail — regressions for confirmed-but-deferred bugs

These `.rxt` files assert the CORRECT (PCRE2) behavior for bugs documented in
docs/known_issues.md. They are **expected to fail** against the current build
and are deliberately NOT run by `make test`, so the main suite honestly
reflects what pcrec currently certifies.

Run them manually to check progress on a known bug:

    bash tests/harness/run.sh tests/known_fail/K1_dollar_in_repeat.rxt

When a bug is fixed, its file moves into tests/base/ (or the relevant module
dir) as a passing regression and the docs/known_issues.md entry is closed.
