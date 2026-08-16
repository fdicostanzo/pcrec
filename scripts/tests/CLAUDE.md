# scripts/tests — self-tests for the scripts one directory up

Run ON CHANGE via `make testscripts` (top level) or `make -C scripts test`,
never as part of `make test` — docs/dev/decisions.md D48. The mechanism is
scripts/Makefile's single derived pattern rule: `<script-full-filename>.test`
here produces `<script-full-filename>.testreport` (gitignored) depending on
both the test file and the script, so an unchanged pair is a no-op and a
changed one re-tests mandatorily. Adding a script's self-test = drop one
`.test` file here; no Makefile edits anywhere. A failing run deletes its
report (`.DELETE_ON_ERROR`) — a red run must not leave a green artifact.

## Files

- **watchdog.test** — scripts/watchdog's 16-case self-test (moved from
  scripts/test_watchdog.sh at D48; history preserved via git mv). Bounds
  every case with coreutils `timeout`, NEVER with watchdog itself (a control
  must not share a mechanism with what it controls); includes the
  spinner/sleeper DISCRIMINATOR pair proving `-c` measures CPU work rather
  than wall time, and pins the stdin-passthrough (`<&0`) and fd-3 stderr
  behaviors that rollout bugs proved load-bearing.

Maintenance: update this file when .test files are added/removed or a
script's test coverage changes meaningfully.
