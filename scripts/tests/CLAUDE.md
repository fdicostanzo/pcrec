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

- **safekill.test** — scripts/safekill's 13-case self-test. Every
  sacrificial process is one this file spawns itself (`setsid` leaders
  under `$SCRATCH`, tracked pids, `trap cleanup EXIT`) — never a target
  found by scanning the box. Covers: the PID paved road killing a
  leader+child tree while leaving an unrelated bystander alone (case1);
  `--pgid` (case2); the pattern path refusing two live identical-cmdline
  siblings and then proceeding under `--all` — incident A/B's shape in
  miniature (case3); self/ancestor exclusion dropping a wrapper whose own
  argv carries the pattern, reproducing the `pgrep -f` self-match hazard
  (case4); `--list` signalling nothing (case5); the audit line's
  pid/pgid/start/cmd fields (case6); the no-match and usage-error exit
  codes (case7); `--under` descendant-tree narrowing (case8); a PID that
  died BEFORE safekill was even invoked exiting 1, not erroring — the
  caller's own TOCTOU (case9); an ordinary `--cwd` non-match NOT
  triggering the unreadable-candidate note, a negative control guarding
  against that new message firing spuriously (case10). Both
  safety-critical guards (self/ancestor exclusion, ambiguity refusal) were
  verified to go red against a deliberately sabotaged copy of the script
  before landing — a test that cannot fail is not a test.

Maintenance: update this file when .test files are added/removed or a
script's test coverage changes meaningfully.
