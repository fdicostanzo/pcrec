# cishard2 -- triage of the first sharded CI run (38354147463), rebalance (lane cishard2, 2026-10-13)

Lane cishard2 (sonnet), branch `lane/cishard2` from main f3aecbe71. Commit under test d67e07507.
Artifacts via `gh run download` (pcrec-ci-sections-0..2, pcrec-test-logs-0; the other shards were green so uploaded no logs).

## 1. Triage: shard 1 had TWO reds, only one is the kit's

Verdict lines in `ci/test.log`: `test-startset` (Makefile:1441) and `test-memfn-g2` (Makefile:1416).

1. **test-memfn-g2: the kit's taskset defect, and only that.** Every `FAIL:` in the SIMD family is
   `taskset: failed to set pid N's affinity: Invalid argument` (x86-64, x86-64-v3, x86-64-v4,
   gpr-only, asan-x86-64-v3), or a downstream effect of it (paths/edge floors at 0, planted
   mutations "NOT DETECTED" because nothing ran). The quick tier and the 14 other families were
   green (gcc-14 quick: 52.5M subjects, 0 failed). Kit-side; fix is lane g2pin, relayed, not touched
   (memfn/ is kit-owned). The SIMD family died at once, so its true cost on the runner is UNMEASURED.
2. **test-startset: OURS, a regression introduced by the sharding itself.** `FAIL: [dfa-diff] 0
   count-collapsed pairs, below the floor 2` (log line 2313). Cause: the new Makefile variable
   `SHARD=1/3` is exported by make to every recipe (command-line variables are), and
   `tests/startset/vmhat_diff.py` has its own `SHARD=i/n` env meaning "run every n-th (mover, config)
   from the i-th" (line 254). Under `make test-shard SHARD=1/3` it ran `jobs[1::3]`: the log shows
   per-config `nocaps: 78, auto: 2, collapse: 2` (index 1 mod 3 of the auto/nocaps/collapse cycle is
   nocaps), hence no count-collapsed pair. Not a runner-only or gcc-13 condition. Shards 2 and 3
   passed only because their `SHARD` values (2/3, 3/3) make `jobs[2::3]`/`jobs[3::3]` still reach
   a collapse pair; they too ran a THIRD of the diff jobs (silent loss of coverage on all three shards).
   Fix: the make variable is renamed `CISHARD` (Makefile, ci.yml, docs/testing.md, tests/ci/CLAUDE.md);
   `vmhat_diff.py` keeps its SHARD. Verified: `make -n test-shard CISHARD=1/3` resolves the list; the
   control passes. NOT re-run: `make test-startset` end to end (box held, LIGHT work only); the log
   shows the unsharded script would have reached its pairs.

   Lesson (not filed as a row): a new make variable with a generic name is an environment hazard
   for every script the recipes call. `grep -rn` for the name in tests/ and scripts/ before choosing it.

Other sections in shard 1 green. Classes: none of runner-only, gcc 13 or missing dependency.

## 2. Measured runner times (top 15, wall seconds; all three shards)

| section | s |
|---|---|
| test-memfn-g2 (quick tier only; SIMD family died) | 885 |
| test-corpus | 576 |
| test-clskit | 416 |
| test-assertions | 315 |
| test-anchored-match | 289 |
| test-codegen | 288 |
| test-compound | 286 (estimate had been 30 local) |
| test-resource | 256 |
| test-startset (a third of its diff jobs) | 172 |
| test-search-pinned | 157 |
| test-findings | 154 |
| test-recursion | 152 |
| test-start-landing | 141 (estimate 60 local) |
| test-memfn-guarded | 140 (estimate 30 local) |
| test-vm | 126 |

Shard step walls: shard 1 25.7 min (short: SIMD family dead), shard 2 37.6 min, shard 3 37.1 min.
Setup (checkout through strict) is about 25-45 s with the libpcre2 cache hit.

## 3. Rebalance

`shard_rebalance.py --measured` on the three sections.tsv, `--write`, then two rows relabeled by hand
and `--assign-only --write`:
- `test-memfn-g2` = 1535 s, ESTIMATED: measured 885 (quick tier) + 650 for the SIMD family
  (450 local-s x ci_scale 1.44; the 450 is itself citime's estimate). Weakest number in the table.
- `test-startset` = 171.5, LOWER BOUND (a third of the diff jobs ran).
All other 67 rows are runner-measured. `ci_scale` = 1.0 (rows are runner seconds). New split: 2224 / 2223 /
2224 s = 37.1 min each projected, 69 sections. `make test-ci-shards` green (9/9 plants red), ci.yml parses.

## 4. Timeouts

Shard step 60 -> **55 min**: 37.1 x spread factor 1.4 = 52, rounded up to 55. Basis for 1.4: the serial
suite's same-tree runner spread was 1.5x (56..85 min); one sharded run is too little to go lower, and
the g2 SIMD estimate could be off. Job ceiling 80 -> **70** (shard step + ~15 for setup, a libpcre2 cache
miss, upload). Re-lower once a second measured run exists (and g2's SIMD family is measured: if it comes in
over ~650 s, shard 1 is the long pole and `--measured` will rebalance it).

## Owed

A real CI run on this branch: the proof that startset is green under `CISHARD` and that g2pin (once
merged) clears shard 1. Branch not pushed.
