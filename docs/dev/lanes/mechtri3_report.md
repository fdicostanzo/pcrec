# mechtri3 report (sonnet, 2026-11-11)

Triage of the first cloud mech run, GitHub Actions 43108213213 (sha ef67f23d6, kind mech, 20 shards, equal 45 s/row weights).

## STATE AT HANDOFF

Branch lane/cmland (worktree worktrees/cmland), 4 commits on top of the cloudmech merge. VALIDATION COMPLETE for the unit
tests (cloud_gather.test 30/30, cloud_failures.test 38/38, cloud_kinds.test 16/16, `make cloud-check` 13/13,
cloud_mech_check: 1232 ids exactly once). A second cloud mech run is OWED (dispatched as the last act, see below).

### The brief's premise was off: the run had two real reds, and four false ones
The verdict listed S126, S16, S17 (shard 7) and S38 (shard 9) as red. Their rows in the shard logs read **DETECTED**: the
shared extractor tests/ci/cloud_failures.sh flagged them because their prose/tally contains upper-case `FAIL`
(`compliance-FAIL`, "FAILS the path"). The two rows that really failed the run:

| row | shard | cause | class | fix |
|---|---|---|---|---|
| S-U6-next-pos-byte-advance | 9 | row declared SAB_EXPECT=UNDETECTED; the tests/utf8 find-all cells (vlbbuild U6) now kill it: `corpus:19fail/4975pass`, "NOW DETECTED". Local re-run on the same tree (49 s) reads the same. Stale expectation, not a cloud difference. | stale row | flipped to DETECTED (committed) |
| S1896-include-not-held | 7 | declared COMPILE-CATCH on 2026-11-11 (mechtri2) from gcc 15.2: the `consumer fortify` cell of tests/memfn/run_targets.sh fails to compile (always_inline memcpy inside the v3 region). The runner is ubuntu-latest, whose default `gcc` is older than 15 (the setup step prints it; the log is not kept) and compiles that cell. Cloud: `memfntargets:3fail/38pass`, no compile error; local gcc 15: `4fail/38pass` + the error, DETECTED-BUILD (13 s). The plant is still caught by the three F1 checks. | cloud-environment difference (compiler version) | new row field `SAB_CATCH_GCC_MIN=15`: below it a COMPILE-CATCH row that the checks detect reads DETECTED, not UNEXPECTED; S1896 carries it. Tested on a fake COMPILE-CATCH row (S1306 copy, MECH_SAB_DIR): min=99 -> DETECTED rc 0, no field -> UNEXPECTED rc 1. The gcc-13 path itself is not reproducible locally (only gcc-15 here): the next cloud run is its proof. |

S126-look-row-not-vmonly and S38-vm-empty-exit-fails were DETECTED in the cloud (not survivors); no test gap.
False-red fix: the extractor now ignores mech matrix rows (a line starting with an S-id then a tab or 2+ spaces); a failing
row is still named by the wrapper's own `FAIL: mech row ID: ...` line. Fixture-style cases added to cloud_failures.test.

### Shard 19 (rc=none, killed at the 150-minute step limit)
It was NOT a hang. 61 rows, and the driver prints nothing per row until the end (rows merge from files at the end), so the log
showed only the 61 `-- running` lines and `units.tsv` was empty (the wrapper copied the times only after the driver
returned). Which rows were slow is therefore unrecoverable for this shard. Evidence it was load, not a hang: the 17 finished
shards took 63-143 min of wall (shard 10, same EPYC 7763 class as shard 19, 143 min), the equal 45 s weights were 2-4x low (mean
measured row ~195 s of row-wall, heavy tailed: median 92 s, max 1579 s S220), so a 150-min limit sat only ~5% over the
slowest shard that finished. A planted infinite loop has no per-row wall cap in the driver (only the suites' own timeouts and
the SAB_REACH 120 s); the shard step limit is the only backstop, which is what fired. Not added: a per-row cap would be a new
mechanism without a measured need (a hung row would now be named by the TIMEOUT line, below).

### Honest verdict for a timed-out shard (item 4)
- cloud_mech_shard.sh now appends per-row seconds straight to the artifact's `units.tsv` as each row ends, so a killed shard
  keeps its finished rows.
- cloud_gather.sh reads `rc=none` as `RED: shard K/N TIMEOUT: no rc recorded ... Units not finished: <table rows minus units.tsv>`.
  Test added (fabricated mech shard 19/20). The old `rc=none (nonzero or never written)` text is gone.

### Reweigh (item 3)
`make cloud-reweight KIND=mech MEASURE=1`: measured_mech.tsv holds the 1047 rows of the 17 rc-0 shards (failed shards 7 and 9 and the
timed-out 19 are not counted: 185 rows unmeasured). Used for those: the MEAN of the measured rows (195 s row-wall = 97 shard-s),
not the median, which would have under-weighted them 3x. Weights are now row-wall / 2 (cloud_units_plan.py MECH_CONC: a
shard runs 2 rows at once; recorded sum(row)/shard wall was 1.76-1.95). Result: 20 shards x ~100 min predicted (was 48 min on
the equal weights); indivisible floor 860 s (largest row S220, 26 min of row-wall, ~13% of the limit, safe). Limit raised
150 -> 180 min (cloud_kinds.tsv), because runner CPU spread (EPYC 7763 vs 9V74) is ~1.4x and 100 x 1.4 = 140 was too close to 150.
If the second run shows a slowest shard past ~150 min, go to 28+ shards (a second wave on 20 slots, more total wall) rather than
a longer limit. Total mech cost is ~110 runner-hours-equivalent per run: this is a nightly/weekly kind, not a per-push one.

### OWED
Second cloud mech run from this branch: `scripts/cloudrun --owner main --kind mech --name mechtri3` (the last act). Expect GREEN;
it proves the gcc-13 SAB_CATCH_GCC_MIN path and S-U6's flip; then reweigh again from its full 20-shard measure.
Last RULINGS entry applied: none (no rulings file).
