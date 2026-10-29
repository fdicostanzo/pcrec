# cired4 report: CI red on main 42d1a4037 (run 40835409808)

## Summary
No test failed. Shard 3/3 was killed by its 55-minute `make test-shard` step
timeout (`##[error]The action 'make test-shard' has timed out after 55
minutes.`) while in test-subst-d27; shards 1/3 and 2/3 were green. Class (a),
a CI-only environment difference (runner speed vs a tight cap). Fix: step
timeout 55 -> 65, job backstop 70 -> 80 (ci.yml, docs/testing.md "CI").

## Failing checks
- test (3/3): step `make test-shard` timed out at 55 min. No `*** [..test-` line
  anywhere in the job log (command grep -E, 5063 lines). The last log lines are
  green `diff ...: FAIL=0` summaries.

## Cause per failure
Per-section timings (artifacts `pcrec-ci-sections-*` of this run vs green run
40827253550, same shard, unchanged tests/ci/shards.tsv):
- Every section ran ~1.2-1.3x slower: test-codegen 323 -> 416 s, test-compound
  541 -> 648, test-anchored-match 293 -> 382, test-assertions 273 -> 341,
  test-rungselect 122 -> 145. Uniform slowdown = a slower hosted runner, not a
  code change. Shard total 2684 s (44.7 min) before; the cap is 1.23x of that.
- The landed work is not on shard 3: [INLINE-C] stage 2's suite is test-code on
  shard 2, which went 17 -> 29 s (+12 s) and passed. test-subst-d27 was merely
  the section running when the clock ran out (320 s the run before).
- The other shards also drifted: shard 2 finished at 50 min (3001 s vs 2757 s).
  Earlier green runs reached 54m52s (40626648149). Same class as cired
  (run 40465053309, shard 2 killed at 55 min).
Not (b), not (c): no code regression, and no capturediff drift.

## Fix
`.github/workflows/ci.yml`: shard step `timeout-minutes` 55 -> 65, job
`timeout-minutes` 70 -> 80, with a comment giving the basis. `docs/testing.md`
"CI" states the new value and why. No table re-balance: shard 3 was the
shortest shard on the previous run. No src/ change, no abi, no new ids.

## Local validation
`make test-ci-shards` in the worktree: 9 passed, 0 failed (it reads ci.yml's
matrix line). A CI-runner slowdown cannot be reproduced locally; the evidence is
the artifact timings above.

## STATE AT HANDOFF
Branch lane/cired4, committed. Rulings file read at start (empty); last entry
applied: none. Nothing OWED. Manager: merge; if shard 3 still nears 65 min on a
healthy runner, re-measure weights with tests/ci/shard_rebalance.py.
