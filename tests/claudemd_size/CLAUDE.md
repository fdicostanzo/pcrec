# tests/claudemd_size/ — CLAUDE.md files stay orientation guides

`make test-claudemd-size` (in `make test`). Runs `scripts/check_claudemd_size.sh --all`
over the real tree (12 KB per directory CLAUDE.md, 20 KB for the root; the table
is in the script), then a sabotage self-test in a temp tree: 13 KB directory and
21 KB root files must fail, a 1 KB one must pass, worktrees/ and the history
archive are skipped, `--staged` reads the index.

- `run_claudemd_size.sh` — the section runner (`ROOT_DIR` overridable).

History and notes go in the directory's NOTES.md, not CLAUDE.md.
