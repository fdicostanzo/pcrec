# scripts — project process tooling

Shell tooling for the development process itself, not for building or testing
pcrec (the Makefile owns that).

## Files

- **mk_d27_cell.sh** — creates a D27 test writer's environment (Frank's
  ruling, 2026-08-11, amending the worktree convention): a git worktree as
  the DELIVERY target plus a parallel, non-git, allowlist-filtered CELL the
  author actually works in. The cell closes the two blindness leaks by
  construction — harness CLAUDE.md auto-injection (files that do not exist
  cannot be injected; five recorded instances) and git history (`git show`
  needs a .git the cell does not have). Allowlist, never denylist: a
  denylist miss leaks silently, an allowlist miss fails loudly. build/ is
  prebuilt inside the worktree so the author never runs make. The script
  self-verifies cell hygiene and prints the exact diff-back / review /
  teardown commands. Residual spawn-time leak (session-root CLAUDE.md and
  memory index, injected before any tool call) is unavoidable and stays
  covered by the briefs' disclosure requirement.

- **measure.sh** — builds and runs one `tests/probes/` probe and archives
  its full output as `docs/measurements/<probe>.txt` (D35, 2026-08-12):
  stable filename per probe so a re-measurement is a `git diff`; header
  stamps the report's full dependency set (probe source blob hash, ABI shim
  blob hash, oracle package version) plus date/repo/gcc context.
  `measure.sh --stale` checks every report's stamps against the current
  tree and oracle WITHOUT re-running — a report is a pure function of its
  dependencies (Frank's refinement). Reports are review evidence, never an
  oracle — no check reads them.

- **hooks/pre-push** — [TT-1] opt-in local push gate: runs `make test` (the
  full suite, not a tier) and blocks the push on failure. Installed ONLY by
  `make hooks`, which copies it to `git rev-parse --git-path hooks` (not a
  hardcoded `.git/hooks` — a worktree's `.git` is a file pointing at the
  shared gitdir, so the install must resolve the path rather than assume
  it). Never auto-installed, no CI (D2). See docs/testing.md "Tiered
  testing" for the opt-in rationale and `git push --no-verify` as the
  documented bypass.

Maintenance: update this file when scripts are added/removed or change role.
