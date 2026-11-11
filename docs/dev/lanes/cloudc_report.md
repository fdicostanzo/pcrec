# cloudc report — [CLOUD-SUITE] C: cloud kinds `axes`, `ubsan`, `asan`

## STATE AT HANDOFF

Branch `lane/cloudc`, code commit 2e972fcd6 (from main 7fbb58485). The three real runs are started on that commit and
NOT read (verdicts arrive as CLOUD-DONE through queuewatch; the manager reads them).

**Run URLs** (the run ids were not yet listed when the lane ended; these are the per-branch run lists, one run each):
- axes: https://github.com/fdicostanzo/pcrec/actions/workflows/cloud-test.yml?query=branch%3Acloud%2Fmain%2Faxes%2FHEAD-2e972fc
- ubsan: https://github.com/fdicostanzo/pcrec/actions/workflows/cloud-test.yml?query=branch%3Acloud%2Fmain%2Fubsan%2FHEAD-2e972fc
- asan: https://github.com/fdicostanzo/pcrec/actions/workflows/cloud-test.yml?query=branch%3Acloud%2Fmain%2Fasan%2FHEAD-2e972fc
(`scripts/cloudrun --verdict cloud/main/<kind>/HEAD-2e972fc 2e972fcd6` gives GREEN/RED/PENDING + run id + URL.)

### Rows (tests/ci/cloud_kinds.tsv; a 9th column `population` is new)
| kind | command | selector | shards | max_parallel | limit_min | needs |
|---|---|---|---|---|---|---|
| axes | `cloud_axes_shard.sh {selector} {shard}` | cloud_axes_shards.tsv | 20 | 20 | 150 | pcre2 |
| ubsan | `cloud_san_shard.sh {selector} {shard} ubsan-locked` | cloud_san_shards.tsv | 12 | 20 | 90 | pcre2 |
| asan | `cloud_san_shard.sh {selector} {shard} asan-locked` | cloud_san_shards.tsv | 12 | 20 | 90 | pcre2 |

`population` column: a command `cloud_check.sh` runs that COUNTS the selector's population (test row: the existing
`check_shards.sh`; axes: `cloud_axes_check.sh`; sanitizers: `cloud_san_check.sh`). A kind without one fails cloud-check.

### Selectors
- **axes**: `run_axes.sh` already took `AXES=` words. Added: `AXES_PLAN=1` (prints `plan-job`/`plan-pass` lines for what
  an `AXES=` would run, skipping the baseline, then exits), an `axes_has` word test, and per-job selection for
  `--vm-entry-shape=N` and each `--part-*` spelling (before, the bare token selected all). A table row is a UNIT = the
  words that must travel together: `--engine -fno-start-set` (the product arm and the DFA-hat population sit across
  both), `-fno-start-width -fno-start-landing` (one product job), `--tune` (DIAL-S3 compares all positions), one `--memfn=`
  row (both layers + its reach cells), one `--analysis=` bundle, every bit flag alone. Shard 1 also runs giveup1, the
  PC-4 oracle and the form census; others set SKIP_ORACLE=1 and print that.
- **ubsan/asan**: `make <target>-locked SAN_SCRIPTS="..."` (command-line override of the manifest variable), one shared
  table over the 43 scripts of tests/lib/san_scripts.txt. The wrapper first builds and runs a sanitized `main` and
  FAILS LOUDLY if the runner's gcc lacks the runtimes. shard-setup needs NO change (libasan/libubsan/liblsan ship with
  Ubuntu's gcc); ci.yml untouched.

### Population proof (tests/ci/cloud_check.sh -> each row's `population`)
- axes: for every shard K, `AXES_PLAN=1 AXES_FULL=1 AXES=<K's words>` (SKIP_ORACLE=1 off shard 1) is listed; the sorted
  union must equal the unsplit list: **113 jobs + 26 passes (-futf-check arm, oracle, 24 memfn reach cells), each exactly
  once**; DROPPED / EXTRA / DUPLICATED lines name the unit. `--selftest` plants a dropped unit, a duplicated unit and a
  split group and requires each to be seen (all PASS). Needs the built compiler, so `cloud-check` now depends on `all`.
- san: table scripts == non-comment lines of san_scripts.txt, once each, every shard non-empty, files exist; selftest
  plants drop / duplicate / unknown script / empty shard (all PASS).
- Also: cloud_kinds.test 14 pass (every kind declares population + resolvable selector), cloud_gather.test 18 pass
  (new: record keeps `AXIS FAIL`/`DIAL-S3 FAIL`/`FATAL`/sanitizer lines, the verdict prints them under the red shard),
  `cloud_check.sh` 9 pass. Run here against the main tree's build/pcrec (no local build, per the box hold).

### Expected shard minutes (ESTIMATES, nothing measured on a runner yet)
- axes: job cost = local paired seconds x2 (runner 4 cores = 4x slower, run_axes pairs two jobs). Per shard 41-50 min
  of work + the per-shard baseline (193 s x4 = ~13 min) = **55-63 min, one wave of 20**. The ~10 min target is NOT
  reachable for axes: the baseline alone is 13 min per shard and 113 jobs x ~8 min = 15 h of work. More shards than 20
  only add baselines (40 shards x 22 min x 2 waves = 72 min wall, worse than 63); a per-run override to 40 slots with
  40 shards gives ~36 min. Real fix, not built (D77): compute the baseline dump once and pass it as an artifact.
- Units longer than the target: every unit is a job of ~8 min; the multi-job ones are `--tune` (4 jobs, 33 min),
  `--engine -fno-start-set` (4 jobs, 32 min), `-fno-start-width -fno-start-landing` (3 jobs, 25 min).
- ubsan/asan: per script, the CI-measured `make test` section seconds of the same script are a PROXY (labelled in the
  table; 7 scripts have none and carry 30 s). Uninstrumented proxy per shard 4-6 min, shard 1 = `tests/harness/run.sh`
  alone 10 min (the floor); instrumented is typically 3-5x, so expect **~15-20 min per shard, shard 1 ~40 min**, plus the
  instrumented build (a few min). 16 jobs of axes' 20 slots do not fit beside 12+12 — runs queue, fine.
- 16 axes jobs absent from the 20261108 log took the log's median (249 s), labelled in the table header.

### Local assumptions of nproc=16 in the axes/san runs (not changed)
`PROCS` defaults through `tests/lib/procs_default.sh` (capped by nproc), run_axes pairs jobs at PROCS/2, the battery's
`HARNESS_BATCH=64` is kept; `SAN_PROCS=4` / `SAN_GROUP_PROCS` default 4 jobs in the pool and `make -j$(nproc)`. The
13-minute baseline and the 4x scale are the only places the 16-core number leaks into the sizing.

### Notes / follow-ups
- cloud-test.yml's `make strict` on shard `1/` runs for every kind (harmless, ~20 s); not touched.
- The tables are generated: `python3 tests/ci/cloud_units_plan.py axes --plan P --log L --write` (P = the AXES_PLAN=1
  output), `... san --write`; replace the weights with the runner's measured shard minutes after these runs.
- No memfn/ edits, no ci.yml edits, no shard-setup edits.
