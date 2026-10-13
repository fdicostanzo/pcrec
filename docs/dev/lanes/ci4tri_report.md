# ci4tri report: triage of CI run 38387939363 (ddfac0b93), shard 1 red

Lane ci4tri (sonnet), 2026-10-13. Evidence: `gh run download` artifacts
(`pcrec-test-logs-0/ci/test.log`, `pcrec-ci-sections-*`) and `gh run view --json jobs`.

## Findings

1. Shard 1 (`test (1/3)`): the failing step is `make test-shard`; the only
   `*** [Makefile:1425: test-memfn-g2] Error 1` line is the sole red section.
   Failure line: `FAIL: x86-64-v4: answers None rc=-4` (checks passed
   71217786, failed 1: "SIMD family (run_g2_simd.py)"). The other four builds
   (x86-64, x86-64-v3, gpr-only, asan-v3) pass all 19250552 checks.
2. Class: RUNNER-ONLY, not a timeout, not B4, not a stale pin. rc=-4 is
   SIGILL: `memfn/tests/run_g2_simd.py` builds `-march=x86-64-v4` (AVX-512)
   and runs it unconditionally (BUILDS list, line ~162; the answers loop at
   ~795 has no CPU gate; only the paths/plant legs skip v4). This GitHub
   runner's CPU lacks AVX-512; the previous green run (43e741e25) landed on
   one that has it. A hardware lottery, so it will recur intermittently.
   Shard 1 `make test-shard` took 1712.7 s (28.5 min) against the 55-minute
   step limit; shards 2/3 were green (job times 34.5 / 38 min). No rebalance needed.
3. Nothing in B4 (abi 77, test-compound) or restri's re-pin is implicated.
   The 5ce6ea692 affinity-pin fix is in the run and worked (the taskset red
   of cishard3 is gone).

## Fix (kit's, NOT made here: memfn/ is not mine to edit)

Request to the kit lane: in `run_g2_simd.py`, gate the `x86-64-v4` run on
the host supporting it (`avx512f/bw/cd/dq/vl` in `/proc/cpuinfo`, or run a
tiny probe and treat SIGILL as "skip, loudly named"), and keep a loud
note when skipped so the census still records that v4 did not execute.
Interim: re-run the shard; it passes on AVX-512 runners.
