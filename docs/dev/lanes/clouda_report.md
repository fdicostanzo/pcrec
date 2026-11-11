# clouda report — [CLOUD-SUITE] piece A (2026-11-10, sonnet)

Casual `make test` on any branch as sharded GitHub Actions jobs, one verdict, delivered through the
zero-token watcher. Branch lane/clouda.

## STATE AT HANDOFF

STATE: delivered; one validation OWED (the real cloud run, test a, below).

### Files

- `.github/workflows/cloud-test.yml` — trigger `push` on `cloud/**`; jobs `plan` (parses
  `cloud/OWNER/KIND/NAME`, asks `cloud_gather.sh shards KIND` for the shard list, refuses an undefined kind),
  `shard` (matrix from the plan, fail-fast false, ci.yml's steps, libpcre2 10.46 cache with ci.yml's key,
  records rc / CPU model / `/proc/cpuinfo` flags line / SKIP-line count, uploads `cloud-shard-N`), `gather`
  (`if: always()`, needs plan + shard, writes the ONE verdict artifact `cloud-verdict`, exits 1 on RED so the
  run's conclusion is the verdict). Own concurrency group per branch, cancel-in-progress false.
- `tests/ci/cloud_gather.sh` (+ `cloud_gather.test`) — `record`, `gather`, `shards KIND`. The workflow calls
  it; it runs locally on fabricated results.
- `scripts/cloudrun` (+ `scripts/tests/cloudrun.test`) — `--owner O --kind K [--name N] [--ref R] [--dry-run]`,
  `--prune`, `--list`, `--verdict BRANCH SHA`. Ledger `<queue dir>/.cloudrun/ledger.tsv` (`CLOUDRUN_LEDGER`).
  Header is the contract; INDEX.md and scripts/CLAUDE.md updated.
- `scripts/queuewatch` — new `cloud()` source, line `CLOUD-DONE OWNER-KIND-NAME owner=O kind=K verdict=GREEN|RED
  conclusion=C run=ID sha=S branch=B :: URL`, once per ledger row, same cadence/state as the CI source
  (`--ci-every`; `--no-ci` silences both). `scripts/queuemon` — one new row: CLOUD-DONE -> GREEN or RED line to
  `owner=` (a non-main/kit owner reaches main; RED/PROBLEM for kit also reaches main, as for queue jobs);
  `scripts/test_queuemon.sh` 47 checks (was 45).
- Docs: tests/ci/CLAUDE.md, scripts/tests/CLAUDE.md, the lanes history index
  (`docs/dev/history/claude_md/docs__dev__lanes.md`: `cloudres_facts.md` and this report added).

### Design notes

- GREEN means every EXPECTED shard (the plan job's list, from `# shards=N` in shards.tsv) has a result with
  rc 0. Missing result (cancelled, timed out, runner lost), rc != 0, rc `none` (the shard step wrote no rc: killed by
  its step timeout), a result naming another shard, and an empty expected list are each RED, by shard name.
  The shard step writes its rc to `build/cloud/rc` so "rc=2" and "killed" differ.
- CPU awareness (requirement 1) is RECORDED, not yet enforced: every result carries the cpuinfo flags line and
  the verdict prints per-shard `avx2=`/`avx512f=` and the count of log lines naming SKIP. The "SIMD rows declare
  the feature they need" half is a later piece; the loud-skip count is the hook for it.
- ci.yml is NOT changed. The shard job is a COPY of its steps, not a reusable workflow: putting ci.yml behind
  `workflow_call` renames its checks ("test / test (1/3)"), and ci.yml cannot be exercised without triggering it
  (barred). Drift cost: a change to ci.yml's shard steps must be repeated in cloud-test.yml (named in
  tests/ci/CLAUDE.md and the workflow header). OWED/optional: a check that the two stay equal.
- `cloudrun` refuses a branch that already exists on the remote (a push to it starts no new run), requires
  `--owner` and `--kind` (no presumed values), and never writes any ref but `cloud/...`.
- A cloud run's verdict is the run's conclusion: gather fails unless GREEN, so `gh run list` conclusion
  `success` = GREEN. A cancelled run is RED, never green.

### Facts: step-limit margin (facts §5)

CI's shards ran 38-73 min against the 75-min `make test-shard` step limit. Worst observed shard step in the
last three green main runs: 72.9 min (run 42889667159 shard 1/3), a margin of 2.1 min (2.8 %); other shards 71.9,
59.9, 59.4 min. Spread for the SAME shard across three consecutive green runs: shard 1 56.2-72.9, shard 2
38.5-59.4, shard 3 40.1-59.9. The table's weights say about 52 min each. The cloud workflow copies the 75-min
limit, so it inherits the same exposure: a slow runner turns a green tree RED as "shard N rc=none". Not fixed here.

### Tests (observed output)

(b)(c)(d) offline gather, `bash tests/ci/cloud_gather.test`:

    PASS: (d) all green -> GREEN rc=0
    PASS: (b) missing shard 2/3 -> RED by name
    PASS: (c) rc!=0 shard 2/3 -> RED by name only
    PASS: rc=none (killed before the rc was written) -> RED
    PASS: a result naming the wrong shard -> RED
    PASS: empty expected list -> RED (green by absence refused)
    PASS: record writes shard, rc, cpu_flags
    PASS: record counts SKIP lines (2)
    PASS: shards test = 1/N..N/N from shards.tsv
    PASS: shards mech -> exit 2 (undefined kind)
    cloud_gather.test: 10 passed, 0 failed

(e) `bash scripts/tests/cloudrun.test`: 35 passed, 0 failed (argument refusals, dry-run, push and ledger row,
existing branch refused, verdict mapping incl. gh failure -> NONE, queuewatch CLOUD-DONE once per run, silent
when pending / no ledger / `--no-ci`, `--prune` incl. keep-without-verdict, dry-run, idempotence).
`bash scripts/test_queuemon.sh`: 47 passed, 0 failed. `bash scripts/tests/queuewatch_ci.test`: 5 passed, 0 failed.
`scripts/tests/queuewatch.test`: see the owed line below. `scripts/check_claudemd_size.sh --all`: 363 files within
limits. `scripts/entry --lint-scripts`: 65 index lines, 0 failures. The workflow YAML parses (PyYAML); it has
NOT been seen by Actions until test (a).

(a) the real run: OWED, the lane's last act is `scripts/cloudrun --owner main --kind test --name clouda`, which
pushes `cloud/main/test/clouda`. The verdict arrives as `CLOUD-DONE main-test-clouda ...` through queuewatch /
monread, or read it: `gh run list --workflow cloud-test.yml --branch cloud/main/test/clouda`, the `cloud-verdict`
artifact (first line `VERDICT GREEN|RED`). If RED, the first-run risks are workflow-level (artifact path layout
for the gather's re-filing loop, matrix JSON) as much as tree-level; read the gather job and the shard logs.
After the verdict: `scripts/cloudrun --prune` deletes the branch.

### Owed

- Test (a)'s verdict (manager reads it). `queuewatch.test` full run result if not appended below.
- A check keeping cloud-test.yml's shard steps equal to ci.yml's.
- The "SIMD rows declare their feature" half of requirement 1 (flags are recorded; nothing enforces yet).
- mech / axes kinds: `cloud_gather.sh shards KIND` is the place; their timeouts and sizes need the facts in
  cloudres_facts.md.
