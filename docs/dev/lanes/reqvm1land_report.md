# reqvm1land report: landing lane/reqvm1m ([REQRUN-VM], abi 91) on main

## Summary

lane/reqvm1m (7ea91df96) merged on main (merge 02229045e), FILEPIN re-pinned to it (024f84b4b), ledger, plan and three filings committed (3199e85e7). Local build, strict and test-codegen green after the merge; queue job 660-reqvm1m-test (make test 81/81, mover census 0 unexpected) was the combination's validation. No src/ change beyond the merge. D177: see Ledger and plan.

## Merge

Premises held: main = 78627dbca, lane/reqvm1m = 7ea91df96, merge-base = 78627dbca. `git merge --no-ff lane/reqvm1m` ran alone and merged clean (no conflict) as 02229045e.

## Re-pins

`tests/codegen/run_recursion_identity.sh` FILEPIN: 88d3c5209 (lane self-pin) -> 02229045e (the landing merge commit), the same shape as main's 4b32adc72 for ic2fix, history chain extended in the trailing comment. Validation: `scripts/boxlock run` of `make -j16 && make strict && make test-codegen`, rc=0, `run_group: 19/19 scripts passed` (log: /var/tmp/pcrec-pcrec/scratch/reqvm1land/pin.log). The re-pin is commit 024f84b4b.

## Ledger and plan

- docs/dev/full_suite_ledger.md: a `major` line for 02229045e (abi 90 -> 91). Counter header left as the ic2fix landing left it.
- D177 triggers: row 4 (2-3 major changes since the last green run) and row 5 are already past (the ledger has had no green run since the baseline); row 3 (major refactor) is the manager's class call: this landing widens a shared mechanism (the required-run handoff) and is an abi event, so it is a candidate; row 2 not applicable. No suite queued (the manager does).
- docs/dev/plan.md: [REQRUN-VM] moved verbatim to plan_completed.md as STATE:completed (with its folded child [OPT-VMSEED]); no other plan row names [REQRUN-VM], [L1-VMHYB] or [OPT-VMSEED] as a trigger or gate (grep: only [REQRUN-VM]'s own child). plan_lint 232 rows, 0 violations.

## Filings

- [RUNG-HYB-GROW] (plan.md Backlog, not-started): the drop-handoff rung can grow a hybrid, e.g. `(\p{Xwd})x`: 1,040,199 B with the re-entry vs 1,041,150 B without, so the attempt is wasted; trigger is the mover census finding such a pattern (today 0 at the shipped caps). Source: reqvm1rung_report.md.
- K131 (known_issues.md): `make test-spec` link-fails, `pcre2_compile_8` undefined in check06_cursor, 10 checks red; pre-existing (same red on a clean copy of the merge base), not part of make test. Source: reqvm1_report.md "Local section runs".
- R-30 (memfn/docs/requests.md, `(2026-10-29, pcrec manager)`): facts only. Case 7 re-find asks `rx_reqrun` and `rx_reqrun_whole`; the window answer is unused when the whole run is the landmark; lane 1,304.9M vs main 3,295.1M instr:u (x2.53), twin 7a 922.7M; pcrec needs a single ask. No method presumed (D157). Source: reqvm1_report.md Deviations item 2.
- Also indexed: this report in docs/dev/history/claude_md/docs__dev__lanes.md.

## Push and CI

Pushed 0e358b446 (the report's first version was committed before the push); CI run 40827253550, in progress. Details in the PUSH line at the end.

## STATE AT HANDOFF

Rulings file read at each commit: no entries. Main tree: only docs/dev/artifact_size_log.tsv dirty (not mine, not committed). Owed: none.

PUSH: main 78627dbca..0e358b446 pushed (pre-push-light green: spec-scan, strict). CI run id 40827253550 (in_progress at handback; not waited on). This final report edit is committed locally and not pushed (a push would cancel the running CI job); it travels with the next push.
