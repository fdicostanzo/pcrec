# cmland report

## STATE AT HANDOFF

Merged lane/cloudmech onto main (which has lane/ciswitch), `git merge --no-ff`. Rule: ciswitch's structure wins, cloudmech's additions carried onto it.

Conflicts and resolutions:
- `tests/ci/shards.tsv` (modify/delete): stays DELETED; `tests/ci/cloud_test_shards.tsv` is the one test table. cloudmech's `test-alloc` row is in it (shard 17, weight 61, ESTIMATE; the first gather reweighs it); its `# extras=cloudgate-strict cloudgate-lint` header survived.
- `tests/ci/check_shards.sh`: ciswitch's removal of the ci.yml matrix check (old check 5) kept; cloudmech's EXTRAS check kept and renumbered 5.
- `tests/ci/cloud_plan.py`: cloudmech's EXTRAS docstring paragraph and extras handling kept on ciswitch's `--out` table loading; "shards.tsv's format" reworded to "the table's own format".
- `cloud-test.yml` merged cleanly; checked: reusable-workflow inputs (ciswitch) and cloudmech's steps both present, `cloud_check.sh` passes, both workflows YAML-parse (python3 -I).

Validation (all in this worktree): make cloud-check 13/0; cloud_gather.test 29/0; cloud_kinds.test 16/0; queuewatch.test pass; queuewatch_cloud.test 7/0; make test-ci-shards 8/0; make test-alloc 1/0; make strict clean; no conflict markers in code (only prose mentions in other reports).

OPEN NOTE: scripts/tests/cloudrun.test reported 41 passed, 4 failed on a first run overlapping other test runs on the box (another queuewatch.test and a famland suite were running); a solo rerun passed 45/0. Cause unexplained (suspected shared state, unconfirmed).

Cloud run dispatched as last act: `scripts/cloudrun --owner main --kind test --name cmland` (verdict via queuewatch/monread).
