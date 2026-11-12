# gestfix report

## STATE AT HANDOFF
- Gestalt `open` rule: fires only when a STATE:started row has had no sign of life (newer of status date / last commit touching its tag) for more than OPEN_STALE_D=7 days (default, unmeasured); names the count and the oldest OPEN_NAMED=3 by tag and age. The raw started/ready/blocked count now prints only when started+ready > OPEN_MAX=25 (was 6; default, unmeasured). Undated rows stay with the existing `stale` row.
- Output on today's plan: `open: 3 started row(s) idle > 7d (oldest: SUITE-RESUME 17d, QORDER 10d, QUEUE-CAPKILL 10d)` (was `open: started 16 / ready 3 / blocked 2 ...` every beat). Planted stale row (fake GESTALT_WORK_ENTRY, status 2026-10-01) printed `open: 1 started row(s) idle > 7d (oldest: PLANTED-OLD 42d)`; the fresh planted row did not.
- cloud-check check 6: tests/ci/workflow_perms_check.py (PyYAML), wired in tests/ci/cloud_check.sh with a sabotage (ci.yml minus `actions: read` in a scratch copy -> `cloud-test.yml (top-level) declares actions: read but ci.yml job test grants actions: none`, named). Current tree passes; `make cloud-check`: 15 passed, 0 failed.
- No gestalt selftest exists. make strict, test-doc-lint, test-plan-lint, test-claudemd-size pass; cloud run OWED (cloudrun --kind test --name gestfix).
