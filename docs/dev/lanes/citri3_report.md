# citri3 report: CI red on main, run 42530231132

## Summary

Run 42530231132 (main, head 0415c24e3) failed only in job "test (1/3)", step `make test-shard`, one section: `test-memfn-targets`. Cause is a CI-environment difference exposed by a new test, not a regression and not an answer change. Fixed in `tests/memfn/run_targets.sh`; the section re-validated green locally.

## Failures

The `gh run view --log-failed` output is empty for this run; the job log came from `gh api repos/fdicostanzo/pcrec/actions/jobs/128882581244/logs` (saved under the lane scratch, `scratch/citri3/job1.log`).

- Job log line 2843: `make[1]: *** [Makefile:1499: test-memfn-targets] Error 1`; line 2947 is the shard's `Error 1`. The other 3 sections of the shard and shards 2/3 were green.
- Cells `gcc-v4` and `clang-v4` (`-march=x86-64-v4`) printed `gnutimeout: the monitored command dumped core` then `FAIL: ... wrong answers:` with an empty result. The fixture compiled at x86-64-v4 may contain AVX-512 instructions; the GitHub runner CPU lacks AVX-512, so the process dies of SIGILL. The dev box (Zen 4) has AVX-512, so it ran green locally (P1 lane's job 470-main-p1tri-maketest). Hypothesis check: the cause is the host CPU, not sort locale or a missing tool.
- Introduced by: the K0 kit merge (commits 8ec9ef43d, ad3e25e47 added `tests/memfn/run_targets.sh` and its CI shard row; the cells are at `tests/memfn/run_targets.sh` `cell gcc-v4` / `cell clang-v4`). Last green CI run is 42525179207 (head c054e38e7), which predates the K0 merge; the failed run's push is the first to carry the section.

## Fixes

`tests/memfn/run_targets.sh`: `cell()` still compiles and links a `-march=x86-64-v4` cell everywhere but runs it only if `/proc/cpuinfo` lists `avx512f`; otherwise it prints a counted SKIP. The RAN floor drops by one (the gcc-v4 cell) on a host without avx512f. Header comment on the cell explains why.

Validation: `make test-memfn-targets` on this box: 9 cells ran, 0 skipped, 14 checks passed, 0 failed. The no-AVX-512 path was exercised by a scratch copy of the script with the feature name mangled (copy removed): 7 cells ran, 2 skipped (both v4), 12 checks passed, 0 failed. Both runs are the file `tests/memfn/run_targets.sh` (the section's own file). Section runtime under 1 minute, so no queue run owed.

## STATE AT HANDOFF

Complete. No runs owed. Rulings file `citri3_rulings.md` does not exist (no entries applied). A CI re-run of shard 1 is the only confirmation of the CI-side behaviour and happens after merge.
