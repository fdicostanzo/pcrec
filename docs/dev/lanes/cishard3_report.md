# cishard3 report: triage of CI run 38358125348 (be9b255e5)

Lane cishard3 (sonnet), 2026-10-13. Evidence: `gh run download` artifacts
(`pcrec-ci-sections-*`, `pcrec-test-logs-*`) and `gh api .../jobs` step times.

## Verdict per shard

| shard | result | wall | red sections | cause |
|---|---|---|---|---|
| 1/3 | red | 26.2 min (`make test-shard`) | test-memfn-g2 only | the kit's `taskset -c 12-15` (see below) |
| 2/3 | green | 39 min | none | |
| 3/3 | red | 37 min | test-rxtsource only | stale rxtsource census pins (real, not runner-only) |

Neither red is a step timeout: shard 3's step ran 06:42:05 -> 07:19:02
(2217 s, `sections ran: 25/25`, trailer "every section was launched"), well
inside the 55-minute step timeout.

## Shard 3: test-rxtsource, REAL stale pins (fixed on this branch)

The log shows `FAIL: census MOVED: found 280/5647/56407, pinned
280/5645/56396` and the downstream C1 (legs A/B/C), case-row and C3 failures.
It is not runner-only and not shard-only: the same script run in this
worktree at be9b255e5 (python 3.14, gcc 15) fails identically
(`build/rxt_local.log`: `checks failed: 8`).

Cause: s157tri's `4ba75935f` added two oracle-written blocks to
`tests/recursion/quantified.rxt` (+2 blocks, +11 case lines, counted from the
commit's `+` lines) and did not re-pin the census (delivery-bar miss; the
lane's report claims only its mech row). The 11 cells have no python
expression, so on python 3.14 `C3_PASS` is unchanged and `C3_SKIP`,
`C3_SKIP_NOPYTHON`, `C3_VERIFIABLE` each move +11. CI's python 3.12 shows
the same +11 on the version-invariant `verifiable` pin (22004 against 21993),
so the re-pin is right for both.

Fix (`tests/rxtsource/run_rxtsource_tests.sh`, 7 pins, each annotated):
`CENSUS_BLOCKS` 5645 -> 5647, `CENSUS_LINES` 56396 -> 56407, `RUNSH_BLOCKS` /
`RUNSH_LINES` the same (quantified.rxt is not in known_fail), `C3_SKIP`
36466 -> 36477, `C3_SKIP_NOPYTHON` 2135 -> 2146, `C3_VERIFIABLE` 21993 ->
22004. Validation: `bash tests/rxtsource/run_rxtsource_tests.sh` on the
fixed file: rc 0, `checks passed: 298`, `checks failed: 0`
(`build/rxt_after.log`). The 19 other shard-3 sections were green in the CI log.

## Correction to the brief's fact

Main's local run (`worktrees/.mgr/mt111/test.log`) was NOT clean: it contains
`make[1]: *** [Makefile:537: test-rxtsource] Error 1` at line 6159 with
`checks failed: 8` immediately above it, the same failure. The "checks
failed: 0" read was another section's summary line. This is the learnings
§3 rule again: the verdict is make's `*** [test-X]` lines.

## Shard 1: confirmed the only red is the kit's taskset bug

`test-memfn-g2` fails on `SIMD family (run_g2_simd.py): checks failed: 29`.
All 20 `FAIL:` lines in that section's output are consequences of
`taskset: failed to set pid N's affinity: Invalid argument` (5 cells, from
the hard-coded `taskset -c ${G2V_CPUS:-12-15}`, `memfn/tests/run_g2_simd.py:353`,
on a 4-vCPU runner), then the floor lines (`paths ... below floor`, `edge ...
(0, 0) below floor`) and the 6 `plant ... NOT DETECTED` lines, which have
no answers to read. No other section in shard 1 is red (20/20 launched;
every other `*** [test-` grep is empty). lane/memfn-g2pin is the fix; I did
not touch memfn/. Until it merges, `G2V_CPUS=0-3` in the workflow would also
clear it (the env override exists), not applied here.

## Runner-vs-local notes

Nothing in shard 3 was gcc-13, tool or timeout related. Section wall times
for the shard are in `pcrec-ci-sections-2/sections.tsv` (largest: clskit
416 s, assertions 319 s, codegen 296 s, resource 258 s).
