# scripts/tests — notes (not auto-injected)

Per-test detail moved out of CLAUDE.md.

- **branchprune.test** — scripts/branchprune's self-test (59 checks) against a SACRIFICIAL repo plus a sacrificial bare origin under mktemp. One branch per gate (unmerged, fresh tip, worktree-attached, kit, protected main), each PAIRED with the same branch passing once its blocker is lifted; named vs bulk apply, `--archive` (dry run, merged/kit/clash refusals, tag round trip and restore), `--remote` dry run, named delete, moved-remote-tip refusal. A planted gate removal goes red.

- statusline.test — scripts/statusline.sh: exit 0, one line, full-input session snapshot, usage-latest without rate_limits, prune, speed.

- **pred_doc_lint.py.test** — pred_doc_lint.py's own selftest (plants per clause of L1-L11, exact-rule detection, controls, constants) and the committed sample `pred_doc/root/` linted through the CLI, plus the CLI failure path (rc 1 and an `Ln file:line:` line; rc 2 on a missing root). `pred_doc/mut.py` is its mutation gate (r56): ~174 one-place mutants of the lint, each must turn this test red or be named equivalent with a reason; run it after any change to the lint.
- **entry_pieces.test** — scripts/entry's `predicates` profile (form `pieces`) over the sample: tag/slug keys, levels, exit codes 0/1/2, `-g`, `--state open`.
