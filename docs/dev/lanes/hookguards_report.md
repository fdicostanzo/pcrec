# hookguards report ([HOOK-GUARDS], lane/hookguards)

## STATE AT HANDOFF

Built and fixture-tested (offline, `bash scripts/hooks/test_*.sh`, both "ok"):
- (a) `scripts/hooks/no_commit_all.sh` (PreToolUse Bash) + `test_no_commit_all.sh`
  (35 cases: -a/--all/-am/-avm/-qa, `git -C`/`-c`, &&, ;, |, newline, subshell,
  `$(...)`, if/then, heredoc message; allowed: flag text in -m, --amend,
  `git add -A`, named paths, `-ma`, `--`, quoted whole command). Exit 2 + stderr,
  same shape as no_cd_worktree.sh (premise check: both exit 2 on a sample JSON).
- (c) `scripts/hooks/lane_writes_in_worktree.sh` (Write|Edit|NotebookEdit) +
  `test_lane_writes_in_worktree.sh`. Both registered in `.claude/settings.json`.
- Docs: scripts/CLAUDE.md, docs/testing.md, plan.md [HOOK-GUARDS] (left
  STATE:started until merged; plan_lint forbids a done head in Backlog).

### (c) facts
URL: https://code.claude.com/docs/en/hooks ("Common input fields", fetched
2026-10-25). Quoted:
- `agent_id`: "Unique identifier for the subagent or in-process teammate the
  hook fires in."
- `agent_type`: "Agent name (for example, "Explore" or "security-reviewer").
  Present when the session uses `--agent` or the hook fires inside a subagent."
- "Hooks from settings files, managed policy settings, and plugins also run
  inside subagents ... the input carries the `agent_id` and `agent_type`
  common input fields that identify the subagent."
Caveats: the page does not say agent_id is absent in the main thread
(inferred; the hook fails open if absent either way); agent_type alone can
appear in the main session under `--agent`, so the hook keys on agent_id.
I read only the first 100k of 282k chars (PreToolUse section itself was
beyond the cut; the common fields apply to all events). Not tested live
(brief forbids experiments), so the first real subagent write is the test.

### Escape design (for your ruling)
`/home/pcrec/projects/pcrec/worktrees/.mgr/main_write_ok` (exists as a dir).
One entry per line: `*` (any subagent), an exact agent_id, or
`agent_type:NAME`. Absent file = no escape. Recommended use: when launching a
landing lane, write `*` (the lane's agent_id is only known after spawn, so an
id entry races its first write), remove it after. Alternative if you want it
tighter: `agent_type:` entries, or add the id right after spawn. Only
top-level JSON keys are read, so file content mentioning agent_id cannot
spoof it.

### Notes
- Hook limits: `bash -c "git commit -a"` (quoted whole command) is not caught
  (same deliberate gap as no_cd_worktree.sh); `git commit --al` abbreviations
  not caught; relative paths in Write fail open.
- The fixture tests call `mktemp -d` without TMPDIR (test_lane_writes created
  a short-lived /tmp dir, removed on exit) -- a boilerplate slip of mine.
  Same as the existing test_no_stale_claudemd.sh pattern.
- Not run: hooks.test / make testscripts (not heavy, but untouched; the
  Makefile deps list for hooks.testreport was not extended).
