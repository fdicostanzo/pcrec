# reweigh2 report

## STATE AT HANDOFF
- Step 1: `git merge --no-ff main` into lane/reweigh2, clean. test-rxtsource and test-startset green locally (nice make -j4).
- Step 2: generated cloud timing tables (tests/ci/cloud_*_shards.tsv, measured_*.tsv) are exempted by one pattern in each check:
  tests/compound/run_lever_fence.sh ALLOW, and tests/memfn/arch_blind_check.py (DATA_EXEMPT_RE / data_exempt(); the file-scope control
  now also plants a box name in tests/ci/measured_axes.tsv (must not hit) and tests/ci/not_a_table.sh (must hit)). test-compound and
  test-memfn-arch green locally.
- Step 3a: scripts/queuewatch PENDING-STUCK sleeps --confirm and re-reads running/ and the head of pending/ before reporting.
  scripts/tests/queuewatch.test: race case plus plant (noconfirmstuck). The test has 8 pre-existing FAILs ("ADD FAILED" etc.) that main's copy
  has too; none new.
- Step 3b: scripts/cloudrun refuses (64) --name with no --ref while the checkout is on branch main (the cloud/main/axes/ucax slip); `--ref main`
  or a lane worktree is fine. Documented in its header; scripts/tests/cloudrun.test 41/41.
- OWED: cloud run `scripts/cloudrun --owner main --kind test --name reweigh2` from this worktree (verdict arrives as CLOUD-DONE).
