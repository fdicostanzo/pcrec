# Lane hooks report (sonnet, 2026-10-20)

Branch lane/hooks, from main a0c2ec9c4. No src/, cli/, lib/ change. Rulings file
`hooks_rulings.md` was empty at every re-read.

## Delivered
- A. `scripts/hooks/pre-push-light` (plan lint tree scan + spec scan + `make strict`,
  names each failure, ~25 s). `make hooks HOOKS=pre-push-light` installs it as
  `pre-push` (Makefile drops `-light`); the full gate stays `HOOKS=pre-push`.
  INSTALLED in /home/pcrec/projects/pcrec/.git/hooks (shared gitdir, all worktrees).
  Pcrec-manager skill step 0b: read `gh run list --commit <sha>` after each push.
- B. `scripts/hooks/no_cd_worktree.sh` (bash + one awk, ~2 ms, fails open) registered
  in `.claude/settings.json` (PreToolUse, Bash). Blocks `cd` into worktrees/ and
  chained `cd`; allows lone cd, git -C, quoted cd, subshell cd (documented).
  Self-test `scripts/tests/hooks.test` (37 checks, green). BOILERPLATE step 2 fixed.
  NOTE: the hook takes effect in a session only after the harness reloads project
  settings (new session / `/hooks`); this lane's own session did not load it.
- C1. san/ubsan/asan/lint/alloc and test-recursion-identity re-invoke as `<t>-locked`
  under `scripts/boxlock run` (verified: `make lint` held the lock, released, rc 0).
  CI needs nothing: ci.yml runs only make/strict/test, and none of these.
- C4. mech: requested ids validated before the lock (typo FATALs in ~1.7 s, rc 2).
- C5. emit_sweep.py.test variant plants: `boxlock run` wraps the 900 s timeout, so
  lock wait is not counted (chose this over --no-wait/skip: the plants still run).
- C3. Skill watcher paragraphs and learnings s6 now point at watchrun/chainrun/
  verdict/boxlock. scripts/CLAUDE.md, scripts/tests/CLAUDE.md, docs/testing.md rows.

## Not done / owed
- `make testscripts` full (~10 min) NOT run; ran only hooks.test (green) and
  `bash -n` on emit_sweep.py.test. A standalone emit_sweep.py.test run was still
  going at handoff (heavy); owed: `scripts/boxlock run --label hooks -- make testscripts`.
- Variant plants (EMIT_SWEEP_VARIANT_PLANTS=1) not exercised.
- `make strict`/plan lint on the final tree: owed as the first act of the merge.
- Known gap: a cd inside `bash -c "..."` is not caught (quotes are not parsed).

## STATE AT HANDOFF
Committed on lane/hooks; rulings applied: none (file empty).
