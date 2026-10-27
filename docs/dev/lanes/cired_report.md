# cired report

## Summary
CI run 40465053309 (main 7d3be7ec7) was red from a step TIMEOUT, not a test failure. Fix: re-balance tests/ci/shards.tsv from the run's measured section times.

## Failing job and step
Job `test (2/3)` (id 122058327641), step `make test-shard`: "The action 'make test-shard' has timed out after 55 minutes" (log line ##[error]). No `*** [... test-X] Error` lines exist. Shards 1/3 and 3/3 passed (41m47s, 31m9s job time).

## Cause
Stale shard weights, not a regression and not a CI-only tool difference. Shard 2 was the longest in the previous green runs (47.3, 51.8, 52.9 min) and crept up as sections grew (test-callouts measured 215 s vs 120 s estimated, test-findings 210 vs 154, test-startset 335 vs 171.5 lower bound, test-corpus 763 vs 575); this run it hit the 55-minute step cap while in test-compound, its last section. The stage 1b merge added test-callouts weight to shard 2.

## Fix
tests/ci/shards.tsv: weights replaced by runner seconds from the three `pcrec-ci-sections-*` artifacts of this run via tests/ci/shard_rebalance.py, re-assigned (shards now 2468/2467/2467 s, about 41 min each vs the 55-minute cap). test-compound (killed open, so only a 0.5 s lower bound) keeps 286.3 s from the earlier measurement. docs/testing.md CI paragraph gets a note. timeout-minutes untouched (not loosened).
No change to which patterns are accepted or what they match.

## Local evidence
`make -C worktree test-ci-shards`: checks passed 9, failed 0 (table held to TEST_SECTIONS, matrix lists 3 shards, planted self-test). The timeout itself is runner-only and not reproducible locally; the proof is the next CI run (watch shard times, expect each ~41 min).

## STATE AT HANDOFF
OWED: none. Committed on lane/cired. Rulings file read: none present/applied. test-endmark is still an ESTIMATE (60 s); callouts etc. are now measured. Residual risk: runner spread (shard 2's job time varied 47..58 min for similar content), so 41 min vs 55 gives ~1.35x headroom.
