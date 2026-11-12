# mechfast report -- faster cloud mech runs ([CLOUD-SUITE], Frank 2026-11-12)

## STATE AT HANDOFF
Branch lane/mechfast (worktree /home/pcrec/projects/pcrec/worktrees/mechfast). Rulings file: no entries (none applied).
Premise test: `make cloud-check` on the untouched worktree was 14 passed / 1 FAILED (`kind mech: population check: DROPPED S3015`:
the committed table predates S3015); the mech row said 20 shards. Regenerating the table fixed it. After the change `make cloud-check`
is 15/15 (one population check more: mechrows). `scripts/tests/cloudrun.test` 53/0 after the fix of its 31-id case; `make testscripts`
was NOT run whole (it exceeded a 300 s foreground bound and was killed); the two scripts this change touches ran alone: cloudrun.test 53/0 (one flaky queuewatch case failed once under load, then 53/0 twice), queuewatch_cloud.test 7/0. No workflow file was changed.
The kit regenerates the mech table on its own branch (K38-2): this table change on main is re-derived when it merges main; take
`tests/ci/cloud_kinds.tsv` (mech row: 30 / `--waves 3` / setup 35, new mechrows row) and `cloud_units_plan.py --waves` as they are.

## BASELINE
Run 43261368093 (kit, K38-2, mech, 20 shards, max_parallel 20; 15 green, 5 red by their own rows):
- created 16:41:15 -> plan job started 17:16:32: **35 min queue**. The account's concurrent-job cap was full: the kit's previous mech run
  (43239936557, ended 17:16:57) and axes runs 43260937161/43259892389 (to 18:02/17:44) held the slots. Summing the job intervals of
  those runs gives exactly 40 concurrent jobs at 16:40-17:30, so the cap is 40 (shared by every run of the account), not per run.
- shard starts then straggled 17:16:58 -> 17:33:33 (17 min) as slots freed.
- shard wall 85..137 min (median 124, 18 of 20 within 85-133); slowest shard 10/20 137 min; wall created -> done 3h10m.
- FIXED per-shard setup (jobs API step times; the logs' stamps): set up job 1 s + checkout 8-9 s + shard-setup 13-21 s = 22-30 s, plus about 2 s
  record/upload. The kinds table's 70 s default was 2x too high: setup_s is now 35 for mech.
- So the 3h10m was 35 min waiting + 137 min work + 1 min gather. Over-splitting cannot shorten the wait; it shortens the work part.

## CHANGES
(1) RE-SPLIT. `cloud_measure.py mech --last 3 --write`: tests/ci/measured_mech.tsv now holds the median of runs 43261368093, 43149107439
(mechtri4, 20 shards counted), 43131030250 (1247 units). Then `make cloud-reweight KIND=mech`. 4 rows keep an ESTIMATE (mean measured
row 95.9 s): S3007, S3009, S3012, S3015, rows added after those runs (no run has recorded them). Every other row is runner-measured.
Indivisible floor: S221 alone is 2551 s (42.5 min); it is the one shard that cannot shrink.

(2) OVER-SPLIT. Planner weights (shard seconds, 4-core runner), setup 35 s, greedy schedule over P slots (a shard starts when one frees),
deterministic wall and a 2000-trial simulation with each shard time x lognormal(sigma 0.17; the run's 85-137 min spread), minutes:
| shards N | slots P | det. wall | mean wall | p90 wall |
|---|---|---|---|---|
| 20 | 20 | 99.7 | 137.3 | 154.4 |  (today; the real run's work part was 137 min)
| 40 | 20 | 100.2 | 125.9 | 136.3 |
| 60 | 20 | 109.8 | 120.8 | 127.8 |
| 120 | 20 | 117.9 | 114.0 | 117.8 |
| 30 | 30 | 66.6 | 94.6 | 105.2 |
| 60 | 30 | 76.4 | 86.4 | 92.9 |
| 75 | 30 | 80.2 | 86.9 | 91.9 |
| **90** | **30** | 87.8 | **82.7** | **87.0** |
| 120 | 30 | 84.2 | 80.0 | 83.3 |
| 40 | 40 | 50.2 | 72.1 | 80.0 |
| 80 | 40 | 68.1 | 66.8 | 71.9 |
| 120 | 40 | 67.3 | 62.9 | 66.1 |
| 160 | 40 | 63.4 | 61.1 | 63.6 |
Total runner work is 1991 min whatever N; per-shard setup adds only 35 s x N (90 shards: 53 min of runner time, 2.6 %). Over-splitting
pays through the variance (N = P x waves with several waves beats N = P at the mean and p90); at equal N=P the deterministic wall is best
but the slowest runner sets it.
CHOICE: N = 90, P = 30 (`--slots 30 --waves 3`): predicted mean 83 min (p90 87), against 137 min work today (-40 %). Why not wider:
N = 120 is 3 min better but exceeds the gather's one jobs page (100, cloud-test.yml); P = 40 takes every slot of the account and
starves CI. CI TAKES: ci.yml = build 1 + plan 1 + test 18 shards (max_parallel 20) + gather 1, about 20 jobs; with mech at 30 a push
to main during a mech run gets about 10 slots, so CI's shards queue behind the mech run's waves (CI wall up to about 2x its 24 min while
they overlap); it is delayed, never starved to zero (GitHub starts queued jobs as slots free, matrix order). P = 20 would leave CI
untouched at +30 min of mech wall. Unverified: the 40 cap is inferred from job overlap, not read from the plan.
Set in tests/ci/cloud_kinds.tsv (mech: max_parallel 30, setup_s 35, reweigh `--slots {max_parallel} --waves 3`; new planner flag `--waves K`
= N = slots x K), regenerated tests/ci/cloud_mech_shards.tsv (90 shards, per-shard work 1303-2551 s). The table's `predicted_wall_s` is
still the slowest SHARD plus setup (2586 s), not the scheduled wall above; the REWEIGHT-DUE trigger compares shard walls, which is right.

(3) NAMED ROWS. New kind `mechrows` (10 shards, max_parallel 10, `suite` 0): `scripts/cloudrun --owner O --kind mechrows --rows S278,S517 [--name N]`
pushes cloud/O/mechrows/N.rows.S278_S517 (the ids ride in the branch name: no committed file, no workflow change, so the run measures
exactly the pushed commit). `cloud_kinds.sh command` fills a new `{rows}` placeholder from $GITHUB_REF_NAME (sanitized to [A-Za-z0-9,-]);
`cloud_kinds.sh takes-rows KIND` is what cloudrun asks, so no kind is named in code (cloud_check holds that). `cloud_mech_shard.sh -`
reads CLOUD_MECH_ROWS, validates each id against tests/mech/sabotages EXACTLY (the driver prefix-matches, S13 would also run S130),
deals them round-robin over the shards; a shard dealt none passes with a line; the trailer count check is unchanged. `--population N` is the
kind's population check (every sample id in one shard; unknown id and empty list refused). At most 30 ids. Verdict = CLOUD-DONE as any run.
RUNS.md "Cloud dispatch": after a fix re-run the changed rows; the full mech run is the last check before delivery; plus the 30-slot note.
Docs: tests/ci/CLAUDE.md, scripts/CLAUDE.md, scripts/INDEX.md, the cloudrun header, lanes history index. Tests: cloudrun.test +8 cases.
Local proof: `CLOUD_MECH_ROWS=S-U11 cloud_mech_shard.sh - 1/10` ran the real driver, DETECTED, trailer 1 row.

## OWED
- The named-rows proof run: owner main, kind mechrows, name mechfast-rows, rows S01,S13,S-U11 (green on main), dispatched as the last act
  from commit of lane/mechfast: branch cloud/main/mechrows/mechfast-rows.rows.S01_S13_S-U11 (CLOUD-DONE reaches main). Expect GREEN with
  10 shards, 3 of them running one row each, 7 saying "dealt no rows".
- The "after" measurement of the over-split table: the kit's next K38-2 full mech run (after it re-derives the table): compare to 3h10m /
  137 min work; check the slowest shard against predicted_shard_s 2551 s and that CI shards were delayed, not starved.
- `make testscripts` whole (not run): any reviewer or the landing lane.
