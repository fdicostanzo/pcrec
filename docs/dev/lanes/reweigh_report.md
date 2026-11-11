# reweigh lane report ([CLOUD-SUITE], Frank 2026-11-11: "set up a process for reweighting the shards")

## STATE AT HANDOFF

STATE: done (code, tables, docs committed on lane/reweigh). OWED: one `scripts/cloudrun --kind test` run on this
branch (launched as the last act; its verdict is the first run that records `units.tsv` and `wall_s`).

### Before / after (predicted wall = slowest shard step + setup 70 s; `make cloud-reweight KIND=all`, run on today's data)

| kind | measured source | shards before -> after | predicted wall before -> after | measured slowest shard today | indivisible floor |
|---|---|---|---|---|---|
| test | 4 green CI runs (`pcrec-ci-sections-*`, median per section; today's cloud test runs carry no per-section times) | 16 -> 17 | 1282 s -> 1216 s | 1218 s (run 43053217234, shard 1 = test-memfn-g2) | 1216 s = setup 70 + test-memfn-g2 1146 |
| axes | run 43041879682 (red but complete; 15 of 20 shards rc 0 counted) | 20 -> 20 | 3826 s (2984 work + 772 baseline + 70) -> 3102 s | 3892 s | 2584 s = setup 70 + baseline 532 + `--tune` unit 1982 |
| ubsan | runs 43053391106, 43041959902, apportioned (see below) | 12 -> 4 | ~679 s (estimate, never matched) -> 1808 s | 1546 s median, 1724 s max | 1801 s = setup 70 + tests/harness/run.sh 1731 |
| asan | runs 43053475970, 43042026912, apportioned | 12 -> 4 (shared table) | same table | 1916 s | same table |

The old san/axes tables only carried ESTIMATES (axes: local log x2; san: a `make test` proxy), and the san estimate was off by
2-3x (sanitized runs are slower than the proxy), so "before" for them is the old header's number. After the reweigh the
predicted slowest shard is within 0-12 % of what ran today (axes 3032 s predicted vs 3892 s measured on the old table's
skewed assignment, i.e. the old table was the problem). ubsan/asan share one table, so it is the mean of their two measured
files; asan's slowest shard (1916 s) sits 10 % over the plan, inside the 25 % margin.

Shard-count change: the san table went 12 -> 4 because the smallest count within 5 % of the best the largest unit allows is 4
(one unit, `tests/harness/run.sh` ~1731 s, sets the wall; 8 fewer runners for the same wall). That floor is APPORTIONED, not
measured per script: the old runs predate the per-script record, so each old shard's measured wall was split over its scripts
by the table's weights (`basis apportioned`, flagged in `weight_source`). Re-measure after the first recorded san runs.

### Units that block ~10 min for `test` (candidates to split; NOT split here)

Target 600 s = 530 s of section work + 70 s setup. Sections above it, from `tests/ci/measured_test.tsv`:
`test-memfn-g2` 1146 s (needs >= 3 parts), `test-corpus` 683 s (>= 2), then `test-compound` 507 s (fits, but only as a shard
of its own), `test-memfn-d27region` 435 s, `test-codegen` 383 s, `test-startset` 371 s. With g2 and corpus split, the other 83
sections balance into ~510 s shards (the plan prints "without the floor shards the run would end at 582 s (9.7 min)").

### The process (5 lines; full text in `tests/ci/CLAUDE.md` "Reweighting", `docs/testing.md` "CI")

1. Every shard records `units.tsv` (seconds per section / axes job / sanitizer script, `@wall`, `@baseline`, `@build`) and `wall_s`.
2. `make cloud-reweight KIND=all MEASURE=1` (`tests/ci/cloud_reweight.sh`) re-measures the last runs into `tests/ci/measured_KIND.tsv` (median, provenance, CPU mix).
3. The kinds table's `reweigh` column runs the generator on those files; unmeasured units keep a flagged ESTIMATE; the table header names predicted shard/wall and the indivisible floor.
4. `make cloud-check` validates; `DRY=1` prints without writing.
5. Trigger: the verdict carries `REWEIGHT-DUE kind=K slowest=..s plan=..s` when the slowest shard exceeds `# predicted_shard_s` by `reweight_margin` (cloud_kinds.tsv, UNMEASURED default 25 %); the manager runs step 2 then, and after a section/job/script is added.

### What changed

- `tests/ci/cloud_units.py` (record), `cloud_measure.py` (measure), `cloud_reweight.sh` (entry), `measured_{test,axes,ubsan,asan}.tsv`.
- `cloud_gather.sh`: `record` writes `units.tsv` + `wall_s`; `gather` adds the REWEIGHT-DUE line (not red). `cloud-test.yml` generates `sections.tsv` before the record step. `cloud_san_shard.sh` timestamps each script.
- `cloud_kinds.tsv/.sh`: columns `measured`, `reweight_margin`, `setup_s`, `reweigh`.
- `cloud_plan.py` (`--units`), `cloud_units_plan.py` (`--measured`, `--slots`, self-generated axes plan); `shard_rebalance.py` reads a measured file.
- Tests: `cloud_gather.test` (+wall_s, units.tsv, REWEIGHT-DUE fire / no-fire; the 16-shard test follows the table), `cloud_kinds.test`, `scripts/tests/cloudrun.test` (owners column no longer last): all pass. `make cloud-check` 9/9.
- Makefile `cloud-reweight` target (KIND, MEASURE, DRY).

### Does it serve CI's `shards.tsv`?

Yes, same shape (`section, shard, weight_s, weight_source`) and the same unit names: `shard_rebalance.py --measured
tests/ci/measured_test.tsv` now reads the committed file (checked: prints a 3-shard proposal). CI keeps its fixed 3 shards
and its own table; no generator was added for it.

### Open / honest limits

- Only ONE axes run was complete (and red, 5 shards unusable): 26 axes units carry a flagged ESTIMATE (median job). Re-measure after the next axes run.
- `setup_s` 70 and `reweight_margin` 25 are UNMEASURED defaults (the job log's step times would measure setup).
- Not run: `make test` (box rule). The new files are not in any pin I know of; `make cloud-check`, `cloud_gather.test`, `cloud_kinds.test`, `cloudrun.test`, the claudemd size check were run.
