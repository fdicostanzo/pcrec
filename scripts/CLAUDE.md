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

Maintenance: update this file when scripts are added/removed or change role.
