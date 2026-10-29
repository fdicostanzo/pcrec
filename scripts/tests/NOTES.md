# scripts/tests — notes (not auto-injected)

Per-test detail moved out of CLAUDE.md.

- **branchprune.test** — scripts/branchprune's self-test (59 checks) against a SACRIFICIAL repo plus a sacrificial bare origin under mktemp. One branch per gate (unmerged, fresh tip, worktree-attached, kit, protected main), each PAIRED with the same branch passing once its blocker is lifted; named vs bulk apply, `--archive` (dry run, merged/kit/clash refusals, tag round trip and restore), `--remote` dry run, named delete, moved-remote-tip refusal. A planted gate removal goes red.
