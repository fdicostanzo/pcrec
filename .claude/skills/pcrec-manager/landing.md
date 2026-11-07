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
