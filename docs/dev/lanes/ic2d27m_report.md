# ic2d27m report

## Summary
Merged main (d505ad0e0, abi 91) into the ic2d27 spec-first test branch (cca516654) with no conflicts, filed [ERR-MSG-TRUNC], ran build/strict/test-codegen locally (green), and queued the combination's `make test` as `665-ic2d27m-test`. Mech was not re-run. Source/cli/lib: nothing edited beyond what the merge brought.

## Merge and conflicts
`git merge main` alone: clean merge, zero conflicted files, no manual resolution. Premises held: branch tip cca516654, main d505ad0e0, merge-base f42dd4e4a. Main's S-range (S1700-S1714, reqvm1m) does not collide with the branch's S1740-S1741.

## Pins and counts
Checked each file the ic2d27 commits touched (`git diff f42dd4e4a cca516654 --name-only`) against main's reqvm1m landing: no file was edited by both sides, so there is no sum to fix. The branch's own pins are self-contained: arm 12 floor `D27_FLOOR=545` in tests/code/run_code_tests.sh, the matrix header row list (S1740-S1741) in tests/mech/run_sabotage_matrix.sh, tests/code/CLAUDE.md and tests/code/d27/CLAUDE.md file lists. The branch changed no .rxt corpus file (the d27 `.rxtin` fixtures live under tests/code/d27 and are not in the rxtsource census), so no census, startset or size pin moves; the full make test is the check. Two historical sentences say "abi 90" (tests/code/d27/REPORT.md, ic2d27land_report.md): records of what was measured, left as written. The abi digit is not an input of any ic2d27 check I found.

## ERR-MSG-TRUNC row
Filed at the top of Backlog in docs/dev/plan.md (STATE:not-started, filed 2026-10-29 manager, from ic2d27land Bug B), with the manager's direction (worst-case template-length check plus a visible truncation mark; struct size stays) and trigger (next overflowing diagnostic, or [IFACE-PUSH]). `scripts/plan_lint.sh`: 233 rows, 0 violations (the pre-commit hook agreed). Commit b8353d05c.

## Local validation
Under `scripts/boxlock run --label ic2d27m-local`: `make -j16` rc 0; `make strict` clean ("whole tree compiles clean with -Werror -Wshadow"); `make test-codegen` 0 `*** [..test-` lines, last lines "residual twins: 9 passed, 0 failed", "run_group: 19/19 scripts passed". Logs: /var/tmp/pcrec-pcrec/scratch/ic2d27m/{build,strict,codegen}.log.

## STATE AT HANDOFF
- Job: `665-ic2d27m-test` (docs/dev/lanes/ic2d27m_job, modelled on ic2d27_job: build, strict, perfrun make test), queued with cap 9000, expects strict=0 and sections=81 (`sections ran: 81/81`). Dry-run passed at enqueue.
- Log: the queue run dir's job.log, job.log.strict, job.log.make (`scripts/boxqueue status`); read with `scripts/verdict`.
- Completion lines: `strict: DONE rc=0` and `sections ran: 81/81`; green = no `\*\*\* \[(Makefile:[0-9]+: )?test-` lines.
- Commit tested: the HEAD of lane/ic2d27m when the job starts (b8353d05c plus this report/job commit; docs only after the merge).
- Rulings file ic2d27m_rulings.md: empty header only, nothing applied.
- Owed: ic2d27m-test verdict (manager reads). Mech not re-run, per brief.
