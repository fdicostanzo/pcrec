# int3 report — integration branch lane/int3

Lane int3 (sonnet, 2026-10-16). Base main 353249282. Merged, in order, each `git merge` alone:

| # | merged | result |
|---|---|---|
| a | lane/e0c 692c8d4bf | clean, no conflict |
| b | lane/ksrc 44a984b66 | one conflict: docs/dev/lanes/CLAUDE.md index appends; kept both entries |
| c | kit B0 delivery 10d9f43f4 (not memfn-fd's tip) | one conflict: docs/dev/lanes/CLAUDE.md index appends; kept all entries |

No conflict touched src/, scripts/ or tests/. docs/dev/plan.md auto-merged.
Tip: see `git log -1 lane/int3` (the merge of 10d9f43f4, then this report).

## Light checks (taskset -c 0-3, -j4; logs in worktrees/int3/build/v/)

| check | verdict |
|---|---|
| make | rc 0 |
| make strict | rc 0 |
| test-codegen | rc 0, run_group 16/16 scripts passed |
| test-registry | rc 0 |
| test-rxtsource | rc 0 (282 files / 5790 blocks / 70496 expectation lines) |
| scripts/m6read_check_sab_anchors.py | 754 sabotages, 779 anchor sites, all resolve |
| test-plan-lint | RED, 1 violation (below) |
| test-spec-history | RED, 1 failure (below) |

No count pin moved mechanically (registry, rxtsource and codegen are green unedited),
so there are no pin commits.

## Two red doc-citation checks, NOT fixed (need a ruling)

Both are documentation text from the merged branches, not conflicts. My attempt to edit
them with sed was refused by the auto-mode permission classifier, so I stopped rather than
work around it. The tree is unedited (`git status` clean apart from this report).

1. test-plan-lint PL14: `docs/dev/lanes/winreq_report.md:106` (arrives with the kit B0
   delivery, absent on main) cites a plan.md line number beside `[REGIME-LANDINGS]` (fixed by the manager, 6b5b47938 and the next commit).
   Mechanical fix: drop the parenthetical; the row is already cited by its ID
   `[REGIME-LANDINGS]`. `winreq_report.md` is a kit-authored file, so the kit may prefer
   to fix it on its own branch.
2. test-spec-history `[cites] findings`: three citations `findings §13`
   (`docs/dev/lanes/ksrc_report.md:109`, `:120`, and the ksrc index line,
   `docs/dev/lanes/CLAUDE.md:3965`) read as dangling references to docs/spec/findings.md
   (which ends at §9). They mean tests/findings section 13, the data-mover census
   (`tests/findings/run_findings_tests.sh`, "§13 THE DATA-MOVER CENSUS"). Mechanical fix:
   respell as `tests/findings sec. 13` (the form the lane reports already use for sec. 12).
   Introduced by lane/ksrc, red on its own branch tip too.

## Armed full make test

`worktrees/int3/build/v/run.sh` (waiter PID in `build/v/waiter.pid`): polls every 30 s for
`worktrees/int3/.lift`, then `scripts/perfrun --label int3 -- <worktree>/build/v/test.log`,
`rc=$?`, and writes `rc=$rc` to `build/v/DONE`. `.lift` was NOT created.
Verdict is read from `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-' build/v/test.log` with
the `test.log.perfrun` note. Expect test-plan-lint and test-spec-history red there until
the two citations above are fixed.
