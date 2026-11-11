# ciswitch report -- CI runs the cloud `test` machinery

## STATE AT HANDOFF

Done, committed on lane/ciswitch:
- `.github/workflows/cloud-test.yml` is reusable (`workflow_call`: `kind` required, `owner` default `ci`, `name`, `ref`);
  the `push: cloud/**` trigger and the branch-parse path are unchanged (the plan job parses the branch only when `inputs.kind`
  is empty). Concurrency group is per-run for a call (the caller's cancel-in-progress owns superseding), per-branch for a push.
- `.github/workflows/ci.yml`: job `build` (`make` + `make strict`, via the shared `shard-setup`) and job `test`
  (`uses: ./.github/workflows/cloud-test.yml`, `kind: test`). Concurrency cancel-in-progress on main/PR kept. Fork PRs: same
  workflows, no secrets used anywhere; the default read-only token uploads artifacts. NOTE: `make strict` now runs twice
  (the `build` job and shard 1/17 in cloud-test.yml); left as briefed -- dropping shard 1's copy needs a cloud-test.yml
  change that cloud lanes share.
- DELETED: `tests/ci/shards.tsv` (CI's old 3-shard table), check 5 of `check_shards.sh` (ci.yml `shard:` matrix line) and its
  plant, ci.yml's 3-shard matrix/timings/artifacts steps.
- NOT deleted, because still read (find by grep): `check_shards.sh` (Makefile `test-shard --list`; `test-ci-shards`;
  `cloud_kinds.tsv` population column; `cloud_check.sh`), `make test-ci-shards` + its TEST_SECTIONS entry (it now holds
  `cloud_test_shards.tsv` -- the table CI runs -- to TEST_SECTIONS; without it a new section could silently never run in CI),
  `shard_rebalance.py` (imported by `cloud_plan.py`: load/measured/lpt; its CLI default table now cloud_test_shards.tsv).
- Readers of the deleted shards.tsv, re-pointed: `check_shards.sh` (default TABLE), `cloud_plan.py` (section names now read from
  `--out`, the table being regenerated; output byte-identical on the committed measured file), `shard_rebalance.py` (default
  table), Makefile comments/usage text, tests/ci/CLAUDE.md, tests/CLAUDE.md, tests/doc_lint/CLAUDE.md, docs/testing.md (new
  "CI" paragraph, old one marked superseded), plan.md refs line. History files (journals, reviews, lanes reports, ttune ledgers,
  docs/design) still cite shards.tsv and are left as records.
- Touched shared files minimally: none of cloud_kinds.tsv, the gather or the extractor.
- Checked: `make test-ci-shards` (8 plants), `make cloud-check` (9 pass), cloud_kinds.test, cloud_gather.test, claudemd-size,
  doc-lint, plan-lint green; both workflows parse as YAML (no actionlint in the tree).

OWED: the real ci.yml run happens when main is pushed after landing. Watch: (1) the `build` job and `test / plan` start,
(2) the called jobs appear as `test / shard (K/17)` and `test / gather`, (3) `test / gather` prints the verdict, wall ~18 min,
(4) on a PR, a fork's run. If the call is rejected ("workflow file issue") suspect the `concurrency` expression using `inputs`
or the caller's `permissions`. Proof run via `scripts/cloudrun --owner main --kind test --name ciswitch` launched last: see
the reply to main.
