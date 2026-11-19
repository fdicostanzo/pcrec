# scripts/tests — notes (not auto-injected)

Per-test detail moved out of CLAUDE.md.

- **branchprune.test** — scripts/branchprune's self-test (59 checks) against a SACRIFICIAL repo plus a sacrificial bare origin under mktemp. One branch per gate (unmerged, fresh tip, worktree-attached, kit, protected main), each PAIRED with the same branch passing once its blocker is lifted; named vs bulk apply, `--archive` (dry run, merged/kit/clash refusals, tag round trip and restore), `--remote` dry run, named delete, moved-remote-tip refusal. A planted gate removal goes red.

- statusline.test — scripts/statusline.sh: exit 0, one line, full-input session snapshot, usage-latest without rate_limits, prune, speed.

- **pred_doc_lint.py.test** — pred_doc_lint.py's own selftest (a plant per rule L1-L11, exact-rule detection) and the committed sample `pred_doc/root/` linted through the CLI.
