# grow8 report: grow6-growth (run 44940630891) classification + measured-walls fold

Branch lane/grow8 (cut from lane/grow7 bd4319b36). Harness data and records only: no `src/`, `cli/`, `lib/` edit; no bound changed.
Rulings file `grow8_rulings.md` was empty; last R-n applied: none.
PREMISE TEST held: `tests/ci/measured_growth.tsv` exists; grow7's report has a Reweigh section naming `cloud_measure.py` + `cloud_units_plan.py`.

## Summary

- Run 44940630891 (tip 245110035, 61 shards): 15 shards red + `gather` red = 16 failed jobs. 13 are the K155 library-stage leak (one of them
  also carries a limit-cell TIMEOUT), 1 is a job killed at the 45-min limit (shard 31), 1 is spine/uni (K158), 0 new kinds.
- The slowest job (45.9 min) is shard 31: killed at the job limit, in the library ASan stage, after its CLI stage had already used about 1,460 s.
- Fold: both runs' measured walls are in `tests/ci/measured_growth.tsv`; the table regenerates to 96 shards (was 82), predicted slowest shard
  1,421 s (+70 s setup = 1,491 s predicted wall) against the 2,700 s limit; population check PASS (1,600 cells once each).
- That prediction is still too low for the `+`@15 first cells whose shards were red: `matrix/inline.plus.first.lit@15` and
  `matrix/named.plus.first.lit@15` carry the 79.2 s class default; their measured unit walls are 733 s and 721 s (below). The next table is
  still optimistic by about 650 s for each of those two shards until they are measured on a green shard.

## grow6-growth classification

One `gh run view --json jobs` and one `--log-failed` (the latter returned EMPTY: the run's logs were not served by `--log-failed`); the
classification therefore reads the per-shard run artifacts (`test.log`, `result.txt`, `units.tsv`), downloaded once by `cloud_measure.py`
(cache `$PCREC_TMPDIR/scratch/cloud_measure/44940630891`). 63 jobs: `plan`, 61 shards, `gather`. 46 shards green.

| class | count | shards | evidence |
|---|---|---|---|
| K155 library-stage leak (32 KiB in 1 alloc; shard 54: 64 KiB in 2) | 13 | 13, 14, 18, 24, 34, 41, 48, 53, 54, 56, 59, 61, and 20 | `library process exit 1 ... on cell none (after the series)` + `LeakSanitizer` |
| K155 + a `+`@15 limit-cell TIMEOUT | 1 (counted above) | 20 | `matrix/named.plus.first.lit@15 (limit) uncapped [TIMEOUT]: wall/CPU limit (180s)`; that shard's unit wall 1,475 s |
| spine/uni (K158) | 1 | 60 | `library process exit 124 ... cell spine/uni@131069`, series line 115, bound 300 s, control.after missing |
| killed at the 45-min job limit | 1 | 31 | result.txt `rc=none wall_s=?`; step 'Run the shard' cut; see below |
| K157 star cell | 0 | | shard 13 carries `inline.star.first.bref@250` as KNOWN-RED (K157), not a failure |
| gather's verdict step | 1 | gather | `One verdict` step, 0.3 min; no cell of its own |
| anything else | 0 | | |

Counted by job: 15 red shards (the 13 leak shards incl. 20, shard 31, shard 60) + gather = 16. Shards 54 and 56 also print KNOWN-RED K148 cells, 60 K150;
declared kinds, not failures. Failing shard 31 also has two TIMEOUT FAILs (below).

Shard 31 (killed at the limit, 45.9 min). Its 28 cells ran the CLI stage (units sum 1,459 s: `matrix/inline.plus.first.lit@15` 733 s, `matrix/group.poss.last.lit@250`
544 s, the rest under 132 s each). The `inline.plus.first.lit@15` cell FAILed twice with `TIMEOUT: wall/CPU limit (180s)` (the uncapped run and the cap128M
run). The plain library stage then PASSED (140 compiles, slowest cell 187 s). The log ends at the header `library mode (ONE process), ASan+LSan build`: the job was
killed inside that stage. The artifact has no progress log, so the exact cell on which it was cut is NOT recorded (the job limit leaves no per-cell line).
The last cell the CLI stage finished is `spine/cat_ncgrp@131069` (24 s); the ASan stage re-compiles the shard's cells, so the likely sink is
`inline.plus.first.lit@15` again (ASan compile of the 41 MB case).

## Measured walls fold

`python3 -I tests/ci/cloud_measure.py growth --runs 44935813132 44940630891` (stdout, the artifacts of both runs: 37 + 46 rc-0 shards counted),
then the 50 units that sat only on red shards of both runs were kept from the previous file with their basis `apportioned` (header says so).
Previously 158 apportioned units: 108 are now measured. File: 1,422 measure rows + 50 apportioned. `@wall` median 2,036 s (1,592 and 2,480 s).

## Reweigh

`python3 -I tests/ci/cloud_units_plan.py growth --measured tests/ci/measured_growth.tsv --setup 70 --slots 25 --write` (needs `make` for build/pcrec).

| | grow7 table (run 44935813132) | now (both runs) |
|---|---|---|
| shards | 82 | 96 |
| predicted slowest shard | 1,421 s work (1,491 s with setup) | 1,421 s work, 1,491 s predicted wall |
| limit | 2,700 s | 2,700 s (1,209 s under) |
| indivisible floor | 1,491 s (`matrix/named.poss.last.lit@250`, 1,301 s) | same |
| cells with no measurement | 506 | 135 |

Population check: `python3 -I tests/growth/run_growth.py --shard-check --table tests/ci/cloud_growth_shards.tsv`:
`PASS: 96 shards of cloud_growth_shards.tsv run the unsplit sweep's 1600 cells exactly once`.

Risk the prediction does not see: the two `+`@15 first cells on red shards (`inline.plus.first.lit@15`, `named.plus.first.lit@15`) are on the 79.2 s class
default, but measured 733 s and 721 s; each lands in a shard with up to about 650 s unaccounted work. With the table's other weights both stay under the
limit (an estimate, not measured). Not changed: these cells carry no green-shard measurement, and the mechanism
counts rc-0 shards only; the next run measures them if their shard is green.

Measured wall of each `+`@15 `.lit` cell (unit seconds on the cloud runner, from 44940630891 `units.tsv`; a unit covers the uncapped run, ladder and caps;
a value on a red shard is complete for that cell but not folded; the two TIMEOUT cells include their 180 s bounds). For the owner's per-cell-bound question; no bound changed:
`ncgroup.first` 1,022 (shard 51, green); `inline.first` 733 (shard 31, TIMEOUT x2); `named.first` 721 (shard 20, TIMEOUT); `group.first` 686 (green);
`lookbehind.second` 289; `ncgroup.sole` 280 (shard 48, red by leak only); `inline.last` 269; `inline.sole` 391; `named.sole` 155; `named.second` 154; `group.second` 141;
`group.sole` 115; `atomic.sole` 115; `ncgroup.second` 67; `inline.second` 66; the other `.lit@15` cells (last, look, neglook) 3 to 22 s. The 4 `first` cells with `lit`
are the slow family (686 to 1,022 s); two of them (inline, named) are recorded crossing the 180 s per-run bound.

## STATE AT HANDOFF

Branch lane/grow8: `tests/ci/measured_growth.tsv`, `tests/ci/cloud_growth_shards.tsv`, this report, deliver file. Scratch: /var/tmp/pcrec-pcrec/scratch/grow8/{jobs.json,failed.log (empty),measure.out,shards.before}.
Last rulings applied: none (file empty). Owed runs: none; no cloud growth run dispatched. A `build/` in the worktree was made (gitignored).
Open for the owner: the per-cell bound for the `+`@15 first cells; unmeasured `inline`/`named` `plus.first.lit@15` weights; the cause of shard 31's ASan-stage overrun (no progress log in the artifact).
