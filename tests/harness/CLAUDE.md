# tests/harness — test execution engine

Test runner and driver template. The runner (run.sh) orchestrates compilation and execution; the driver (driver.c) template is linked against generated code and exercises the matcher.

## Files

- **run.sh** — bash harness: parses .rxt, compiles patterns with pcrec, builds test executable, runs driver against each case, diffs output. Hardened per R1 review: perr requires clean exit 1 (crash != rejection), unparseable lines and zero-case files are hard failures, per-stage timeouts, -Wall -Wextra -Werror on generated code
- **driver.c** — test driver template: calls generated matcher (rx_search), decodes escape sequences in subjects, prints match/nomatch result
- **verify_rxt.py** — python-re oracle: cross-checks every corpus expectation (D4); `# pcre2-only` blocks are skipped (see docs/testing.md)

## Conventions

run.sh accepts file/directory arguments or scans tests/ recursively. Each .rxt pattern block is compiled to C, linked with driver.c (which includes the generated code), and executed for each m/n line. The driver decodes \" \\ \n \t \r \f \v \xHH escapes. Output is one line per case: "match START END" or "nomatch", compared against expected results.

Maintenance: update this file when files are added/removed or their roles change.
