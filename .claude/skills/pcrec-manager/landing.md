# Landing: merges, landing lanes, pruning

Loaded by the pcrec-manager trigger table when you are about to merge a lane
branch, launch a landing lane, or prune a worktree or branch. Routine merges
are the manager's (memory pcrec-merge-permission); the manager gives the
merge VERDICT and a sonnet landing lane does merge/strict/index/push/prune
(memory pcrec-delegate-docs-merges-searches).

- **Merges serialize through you, with the test battery between** (wake.md
  §3 for the current battery shape and expected counts). Commit before
  battery runs that archive HEAD. A worker going idle uncommitted is
  recoverable: the landing bar travels with the brief, so you can finish the
  landing yourself.
- **NEVER MERGE TO MAIN WHILE A BATTERY IS IN FLIGHT** (2026-09-10: mech
  re-archives HEAD per row, so oralink's mid-battery merge made the run's
  tail measure a half-converted tree, 1 unexpected + 6 anomalies, a full
  triage lane to disposition). Late-evening deliveries PARK on their lane
  branch until the trailer; the battery's pinned commit and main stay
  identical for its whole run.
- `git merge` ALONE in its own command; read its result (root CLAUDE.md
  situation row). For a conflicting TABLE ROW, merge the two rows' text,
  never pick a side (the 1g merge dropped review r5's critic clause,
  2026-11-04). For a conflicting COUNT, recount the names (altcatch,
  2026-11-07: both sides moved a manifest count 78 -> 80 with different rows;
  git merged "80" clean over 82 names).
- **Main-tree writers need the escape file** ([HOOK-GUARDS], 2026-10-25): a
  hook refuses any subagent Write/Edit to the main tree outside worktrees/.
  Before launching a landing lane (or any lane chartered to edit the main
  tree), `echo '*' > worktrees/.mgr/main_write_ok`; remove it when that lane
  ends (while it exists, NO subagent is guarded). While a lane works in the
  main tree, commit named paths only (memory
  pcrec-no-commit-a-during-landing).
- A landing that flips a DEFAULT runs EVERY mech row's reach probe (REACH_ONLY), not only the new rows' (2026-11-15: rule (1) moved S486's witness off its site; landing validation and a retroactive code round probed 9 rows of ~1,300; learnings §3.ad (f)).
- At each landing, add a line to docs/dev/full_suite_ledger.md
  (major/minor/none) and check D177's triggers; when one fires, offer the
  owner the full suite (skill "Offer the owner") and queue
  `scripts/fullsuite_job.sh` for the next window he clears.
- **Remove delivered worktrees with `scripts/wtprune`** (dry run, then
  `--apply NAME`; then their branches with `scripts/branchprune`, same
  shape), which enforces merged/clean/quiet/lock gates and the straggler
  check (processes whose cwd is under the worktree, read from
  `/proc/*/cwd` by PID; never pkill; a harness worker outlived tt12b's
  delivery by a minute and wrote into the deleted path, 2026-09-03). Never
  `rm -rf` (memory pcrec-wtprune-force-never-rmrf). Never remove a
  delivered lane's worktree while a message you sent it may be unread (it
  resurrects and re-creates the tree).
- Run the identity gate in the CLOUD (kind recidentity via `scripts/cloudrun` on the local merge) when the box queue is long or the evening hold is near; an idle landing lane does not self-wake: message it when the verdict lands (2026-11-15).
- Before launching a landing lane run `make test-plan-lint` on main yourself: land1115d stopped at step 1 on a violation an earlier landing's report had left on main (2026-11-15).
- The append-only lanes history index (docs/dev/history/claude_md/docs__dev__lanes.md) CONFLICTS whenever two lanes branched from the same main: delete the three marker lines, keep both lines, `git add`, commit the merge (ten times on 2026-11-17). A lane's HELPER agents hand back to the MANAGER, not to the lane: briefs say a helper writes its findings to a scratch file and returns the path (lane archhist lost three reports).
