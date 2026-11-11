# cloudmon report

## STATE AT HANDOFF
- (1) ONE extractor: `tests/ci/cloud_failures.sh [MAX] < LOG` (strips the GitHub timestamp; matches upper-case FAIL/FAILED/FAILURE not glued to a
  letter anywhere in the line, make `*** [...] Error`, FATAL:, `##[error]`, sanitizer lines; drops PASS/OK lines and `0 FAIL`/`FAIL: 0`
  tallies). `cloud_gather.sh record` (errors.txt, so the final verdict) calls it; so do the alert and `--status`. Surveyed the FAIL forms in
  tests/ scripts/ Makefile (84 `FAIL: `, `FAIL[name]:`, `FAILED`, `ADD FAILED`, `HARNESS FAILURE`, `GCC-FAILED`, `name|FAIL|..`, ...).
  Test `tests/ci/cloud_failures.test` (34 pass): REAL lines from run 43053543333 shard 8 and 43069897443 shard 7 (tests/ci/fixtures/, both the
  indented `  FAIL — utfcheck arm`, the `-futf-check arm ...: FAIL —` line, `AXIS FAIL`, `|FAIL|` row, `run_axes.sh: FAILED`, `##[error]`)
  all caught; real OK/tally lines (`checks failed: 0`, `fail=0`, ASSERT_ZERO, SKIPPED) not. `cloud_gather.test` 22 pass.
- (2) EARLY ALERT: `scripts/queuewatch` cloud(): for a ledger row whose run is PENDING it runs `cloudrun --reds RUN CACHE` and emits one
  `CLOUD-SHARD-RED OWNER KIND NAME shard K/N run=ID :: l1 || l2 || l3` per red shard (state id cloudred|RUN|K/N, so never twice; routed to the
  owner like CLOUD-DONE). A log is fetched once per shard (cache file state.cloudred.cache). API cost: per --ci-every tick (300 s) each in-progress
  run costs 3 gh calls (verdict list, run, jobs): 3 concurrent runs = 12 ticks/h x 9 calls = 108 calls/hour,
  plus one log
  call per newly red shard; GitHub allows 5000/h. Knob: the existing --ci-every / CI_EVERY. Test: `scripts/tests/queuewatch_cloud.test` (7 pass,
  shim gh, real shard-7 lines): silent with no red shard; one alert; four polls = one log fetch; second shard only; CLOUD-DONE after.
- (3) `scripts/cloudrun --status [RUN|BRANCH]` (default every un-pruned ledger run in progress) via `tests/ci/cloud_status.py`; documented in
  cloudrun's help, tests/ci/CLAUDE.md, scripts/INDEX.md. `--reds RUNID CACHE` is its machine form.
- (4) scripts/tests/queuewatch.test: the 8 failures were the test's own staleness: boxqueue add now REFUSES a script with no `--ready` text
  ([BOXQUEUE-READY-GUARD]); the test's wrapper (exec fullsuite_job.sh --simulate, which answers --ready itself) had no such text, so every
  scenario said ADD FAILED (all-green, red-at-axes, burst, die, quiet, provenance, runner-dead, wait). Fix: one comment line mentioning --ready in
  wrapper(). Now 69 passed, 0 failed (run with TMPDIR under the temp root; it defaults to /tmp otherwise). queuewatch_ci.test 5 pass, cloudrun.test 41 pass.
- Sample alert (real run 43069897443, via `cloudrun --reds`):
  `queuewatch: CLOUD-SHARD-RED main axes axfix shard 7/20 run=43069897443 :: AXIS FAIL: -fprefilter (PCREC_FORCE_PREFILTER, bit 9): 0 mismatch(es) (incl. 0 undocumented refusal(s), 0 unallowed one-sided give-up(s)), 3 lost-other, 0 gained || -fprefilter (PCREC_FORCE_PREFILTER, bit 9)|FAIL|keys_base=67678 keys_axis=67675 agree=21394 budget=0 g`
- Sample `cloudrun --status` (real, in-progress run):
```
run 43086187843  test reweigh2 (owner main)  in_progress  shards done 16/17 (0 red, 1 running)  elapsed 16m43s
  https://github.com/fdicostanzo/pcrec/actions/runs/43086187843
```
- Not run: make test (box rule). OWED: cloud run `scripts/cloudrun --owner main --kind test --name cloudmon` (verdict via CLOUD-DONE).
