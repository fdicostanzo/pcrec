# vlbland — landing of [VLOOKBEHIND] stage 1 (2026-11-07, lane vlbland, sonnet)

## STATE AT HANDOFF

LANDED on main. Premise test passed: lane/vlbbuild tip was 482f15d87, main was 65722f996, tree clean apart from the allowed untracked files.

- **Merge sha:** c44649a69 (`git merge --no-ff lane/vlbbuild`, run alone). Pin and filing commit: 109cd82ff.
- **Conflicts and resolutions** (three files, all append-style, both sides kept):
  - `docs/dev/decisions.md`: main's D188 and the branch's D189 both kept (D189 was free).
  - `docs/dev/known_issues.md`: K139, K138 (from main) and K137 FIXED (branch header; main's header said OPEN) all kept.
  - `docs/dev/history/claude_md/docs__dev__lanes.md`: both lanes' index lines kept.
  - decisions.md was not on the brief's list; its conflict was two independent trailing entries, resolved the same way as the listed ledger files. Flagged here for the manager.
  - `tests/registry/limits_check.sh` auto-merged with no conflict: count 78 -> 80 and the two lookbehind names. Main's S2a added no rows there, so no S2a pin was missing; `limits_check.sh` runs 41 passed, 0 failed.
- **Gates:**
  - `make -j4` clean; `make strict`: "whole tree compiles clean".
  - `make test-registry`, `make test-codegen`, `make test-plan-lint`: every "checks failed" line reads 0, no `*** [test-` line.
  - `make test-recursion-identity` with FILEPIN = ABASEPIN = c44649a69 (re-pinned from 97eadaca4, cause in the pin comment): checks passed 15, failed 0, rc=0. Log: `$PCREC_TMPDIR/scratch/vlbland/id.log`.
- **Filings:** [ENC-SIDE-EMIT] note (SEAM-6, VM_PROGRAM_BYTES); new row [ENC-ONE-RULE] (not-started, trigger: a third encoding); F18 on [DEC-RUNG]; F4a in [VLOOKBEHIND] with its status = stage 1 LANDED at c44649a69. `scripts/plan_lint.sh`: 311 rows, 0 violations. Notes sit in the row charters, because plan_lint PL10 refuses free lines before the attribute lines.
- **Identity triage:** `id1tri_report.md` and `id1tri_judge_v2.py` copied into docs/dev/lanes/ with a history-index line.
- **Ledger:** `full_suite_ledger.md` gains a major line for c44649a69 (major 1, minor 4). D177: row 5 already fires (4 minors); row 4 needs 2-3 majors (un-fired). No full suite queued.
- **Push and prune:** pushed (see handback). `wtprune` dry run lists vlbbuild as KEEP ("uncommitted changes": only `docs/dev/artifact_size_log.tsv` in that worktree); `branchprune` lists lane/vlbbuild as "checked out in a worktree". Not forced, so the worktree and branch remain.
- **Owed:** compliance refresh (`docs/pcre2_compliance.md`, per the vlbbuild report, the `compliance-refresh` skill); not run by this lane.
