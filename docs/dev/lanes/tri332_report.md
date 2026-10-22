# tri332 report: triage of the red make test, job 332-substb2

Job: 20261022T142635-332-substb2-b202610221355422645190.test, rc=2, 1407 s.
Verdict (`*** [Makefile:1670: test-spec-history] Error 1`): ONE failing section.

## test-spec-history: BASE-BRANCH issue, not fixed here

Re-run directly (`make test-spec-history` in worktrees/subst) reproduces:
`FAIL: [cites] measures: dangling citation(s): tests/compound/CLAUDE.md:125 §5¶8`.
main's docs/spec/measures.md has `[5¶8]` (A compound's parts); lane/subst's base
lacks it (its diff vs main in measures.md is -3/+1 lines). Nothing in the subst R4 build
touched it. The fix is the merge of main (gated on the manager's "I1+I2 landed"
line), so no commit was made. No other section failed; no real regression, no stale pin.

Re-queued: `scripts/boxqueue retry substb2-b202610221355422645190.test`.
Expect it to hit the same red until main is merged.
