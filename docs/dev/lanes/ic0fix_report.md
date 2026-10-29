# ic0fix -- triage of the RED validation job 530-ic0-test (lane/ic0, [INLINE-C] stage 0)

Lane ic0fix (sonnet), branch lane/ic0. Job 530-ic0-test: outcome=failed, wall 2534s, populations all OK (strict 1/1, sweep 1/1, sections 79/79). Verdict RED came from exactly one section.

## What passed (read from artifacts)

- strict: `strict: whole tree compiles clean`.
- sweep (the mover proof): `emit_sweep: DONE rc=0` against the base patched ONLY by the two intended movers. No other mover.
- make test-codegen: `checks failed: 0`, `run_group: 19/19 scripts passed`.
- `make test`: exactly one `*** [Makefile:780: test-cpset-structure] Error 1`; no other `*** [...test-` line.

## Failure 1: test-cpset-structure, CHECK 3 (stamp census manifest drift)

- Cause: tests/codegen/manifests/m5_stage1_stamps.tsv records the `EMITTED_BYTES` of 12 sample artifacts. The one comment line "traps on" -> "propagates" is +2 bytes in every artifact's shared block, so all 12 rows moved by exactly +2 (all 12 deltas read from the job log diff; no other stamp moved, no row moved by any other amount). The abi digits keep their width (87 -> 88). A reader of the emitted size (not of the abi number or the comment text), so the lane's grep for "87" could not find it; same reader class as the many earlier re-records in run_cpset_structure.sh.
- Class: a pin expecting the old emitted size. Not a wrong answer, not flaky, not pre-existing.
- Fix: commit 08e1f08e7 re-records the 12 rows (+2 each) and adds the dated RE-RECORDED note in tests/codegen/run_cpset_structure.sh. Stage 0 still moves only the comment line and the abi digits.
- Evidence: `bash tests/codegen/run_cpset_structure.sh` on the fixed tree: checks passed 29, failed 0.

## Owed run

Re-queued job: key `530-ic0fix-test` (docs/dev/lanes/ic0fix_job: ic0_job with --ready answering not-ready after 22:30 and the perfrun label ic0fix; same expects). Logs: worktrees/.boxqueue/{pending,running,done,failed}/*530-ic0fix-test/job.log (+ .strict .codegen .sweep .make). Completion lines: `.strict` has `strict: whole tree compiles clean`; `.sweep` has `emit_sweep: DONE rc=0`; `.codegen` has `checks failed: 0`; `.make` ends `sections ran: 79/79` and `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` is empty; scripts/boxqueue state 530-ic0fix-test exits 0. Expected ~42 min; must finish by 23:30.

## STATE AT HANDOFF

Fix committed on lane/ic0 (08e1f08e7 plus the report/job commit). Rulings file ic0fix_rulings.md: re-read at start, "(none yet)", no entries applied. The re-validation job is queued as the last act; not yet run at handoff. FILEPIN re-pin to the merge commit is still the manager's (unchanged from ic0_report.md). docs/dev/artifact_size_log.tsv in the worktree was dirtied by the failed test run and restored with git checkout (not committed).
