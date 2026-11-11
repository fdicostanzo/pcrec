# cloudb report — [CLOUD-SUITE] piece A follow-up (2026-11-10, sonnet)

Branch lane/cloudb (from lane/clouda): the two run-1 bugs, then requirements 7-11.

## STATE AT HANDOFF

STATE: delivered; one validation OWED (the real cloud run, below).

### Bugs from run 42951967591, with their proof

1. GATHER FOUND NO SHARD. Cause: the upload named artifacts `cloud-shard-<job-index>` (0/1/2) while the gather read
   `cloud-shard-KofN`; and the upload of several paths nested results under `cloud/` where the gather looked in
   `build/cloud/`. Fix: `cloud_gather.sh slug K/N` is the ONE name; the upload is `cloud-shard-${{ steps.rec.outputs.slug }}`
   of the single path `build/cloudout`, so the download is `results/cloud-shard-<slug>/result.txt` exactly where the gather
   reads. The re-filing loop in the workflow is gone. Tests (tests/ci/cloud_gather.test, 16 pass): the workflow text uses
   `cloud_gather.sh slug` and no `job-index`; the gather reads 16 shards laid out as uploaded. `make cloud-check` holds the
   same rule.
2. SHARD 1/3 RED (test-memfn-arch, class 1 ISA names in tests/ci/cloud_gather.sh and .test). Fix: the code names no ISA; the
   record keeps the `/proc/cpuinfo` flags line verbatim and the verdict prints `cpu_flags=<line>` per shard; fixtures use
   `fpu vme de`. `python3 tests/memfn/arch_blind_check.py` on the tree: 17 passed, 0 failed (was 2 FAIL). Check and
   allowlist untouched.

### Requirement 7: the kinds table
`tests/ci/cloud_kinds.tsv` (kind, command, selector, shards, max_parallel, limit_min, needs, owners), read through
`tests/ci/cloud_kinds.sh` (kinds, get, shards, command, owner-ok, plan) by the workflow's plan job, `scripts/cloudrun`
(refuses an undeclared kind / disallowed owner, 64) and `cloud_gather.sh shards`. Today one row:
`test | CISHARD_TABLE={selector} make --debug=j test-shard CISHARD={shard} | tests/ci/cloud_test_shards.tsv | table | 20 | 35 | pcre2 | *`.
`needs` is checked to be within what shard-setup provides (pcre2) — informational, not a switch. Tests: cloud_kinds.test
(9; includes a planted new kind with its own numbers: a kind is a row), cloudrun.test (37, +2 for kind/owner refusal).
`make cloud-check` (opt-in, not a TEST_SECTIONS member since shards.tsv is CI's): cloud table = TEST_SECTIONS exactly,
NO kind named in code (sabotage-checked: a planted `test)` case in cloud_gather.sh goes red), one shard-setup copy, one
artifact-name source, no arithmetic in Actions expressions (run 42959538483 died "workflow file issue" on `fromJSON(..) + 15`;
the plan job now computes `job_limit_min`).

ONE COPY OF THE SETUP: `.github/actions/shard-setup/action.yml` (composite: python 3.14, pkg-config, libpcre2 10.46 cache/build/
point/verify, gcc --version, make) used by ci.yml and cloud-test.yml. ci.yml changed ONLY by replacing those 8 steps with
`- uses: ./.github/actions/shard-setup`. The shard step stays per-workflow (composite steps have no timeout-minutes; ci.yml's
and the cloud's result handling differ). How ci.yml's behaviour was proved identical: a script loaded the pre-change ci.yml
(`git show lane/clouda:.github/workflows/ci.yml`) and the new one, expanded the `uses` line into the action's steps (dropping
only `shell:`), and compared every step dict (name, uses, with, id, if, run) in order: 14 vs 14, IDENTICAL; job keys
(name, runs-on, strategy, timeout-minutes), `on`, concurrency, permissions all equal; the cache key and path are unchanged so
main's saved libpcre2 cache still hits; the job name `test (K/N)` is unchanged. Not exercised on Actions for ci.yml itself
(barred); the composite IS exercised by the cloud run below.

### Requirement 8
The verdict lists, under each red shard, its make `*** [...] Error` lines (`record` writes errors.txt next to result.txt;
at most 40; test: cloud_gather.test "(8)"). The watcher event already carries the run URL
(`CLOUD-DONE ... :: URL`; asserted in cloudrun.test). The verdict header now also has `url=`.

### Requirements 9-11: the derived `test` plan
`tests/ci/cloud_plan.py` (+ `--median` added to shard_rebalance.py) derived `tests/ci/cloud_test_shards.tsv` from the
`pcrec-ci-sections-*` artifacts of green main runs 42926942809, 42904468909, 42889667159 (median per section; shards.tsv
untouched). Setup measured from run-1's shard log: ~50-60 s checkout+python+cache+make, so passing a plan-built pcrec to the
shards as an artifact would save under a minute and risk make timestamps/paths: NOT done (setup assumed 70 s in the model).
Result: 16 shards, max_parallel 20 (all run at once; no waves needed — more shards would not shorten the run), per-shard
limit 35 min (worst section x1.45 spread = 29 min), job backstop limit+15.
Per-shard work: shard 1 = test-memfn-g2 alone 1212 s (20.2 min); shard 2 = test-corpus alone 609 s (10.1 min); shards 3-16
= 528-529 s (8.8 min) each. With ~70 s setup the 14 non-floor shards end at ~10 min; the RUN ends at about 21-22 min.
FLOOR (section alone + setup > the 600 s target): test-memfn-g2 1212 s (the run's wall, set by this one section) and
test-corpus 609 s. The ~10 min wall is unreachable until test-memfn-g2 is split or sped up; owner decision, not made here.
The sum of section time is 9225 s (~154 min serial), CI's 3 shards were 38-73 min.

### Run
The REAL run: first push 42959538483 died at once on the `+ 15` expression (fixed, above, with a cloud-check rule). Second:
`scripts/cloudrun --owner main --kind test --name cloudb2` -> branch cloud/main/test/cloudb2 at 8c6893f0a, run
https://github.com/fdicostanzo/pcrec/actions/runs/42959648886 (seen `in_progress` once, i.e. the workflow file parses; NOT
polled). The verdict arrives as CLOUD-DONE main-test-cloudb2 through queuewatch; the ledger also holds the dead
main-test-cloudb row, which will report one RED CLOUD-DONE (the workflow-file failure) — ignore it. Prune both branches
after the verdict: `scripts/cloudrun --prune`.

### Owed
- The verdict of run 42959648886 (manager reads it). First real sight of: the composite action on Actions, the 16-shard
  matrix with max-parallel 20, `timeout-minutes` expressions, the single-path artifact layout. If RED, read the plan/gather
  jobs first.
- ci.yml's next push to main is the first Actions run of ci.yml with the composite (identity proved structurally only).
- queuewatch.test's stale wrapper (noted in clouda_report) is still unfixed.
- "SIMD rows declare their feature" half of requirement 1 is still only recorded (flags line in the verdict).
