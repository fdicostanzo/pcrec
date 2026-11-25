# process r94
freeze 15:15 SUBJECT=14e8c419b LANEBASE=b9f81ef80 main=e11c5f4ef rulings commit c0f8bd689 (plan/decisions)
FREEZE NOTE: main ruling recorded only in the launch message.
FREEZE NOTE: branch moved during setup (2dd4cf4af, 8bd727eab journal-only).
build 15:21 rc 0
critics launched 15:24: checkadequacy (opus), generalform (sonnet), parallelism (sonnet)
15:22-15:48 all three critics returned inside the launch turn (background calls ran to completion); each file complete with CRITIC COMPLETE, lanecheck DONE rc=0 x3. Final replies undeliverable (expected).
  checkadequacy opus ~26 min, 8 findings (2 design, 4 maintenance, 2 doc); ran 4 real --plant re-aims.
  generalform sonnet ~5 min, 4 findings; twin census matched the subject's own counts (16/23/S1540).
  parallelism sonnet ~10 min, 4 findings + 2 notes; PAR-1 duplicates COORD-1 (found at setup).
  Overlaps: PAR-1 = COORD-1. CA-1 alias part dies with CA-6.
verify: inline (quote/code-read claims + critic repros); no verifier agent.
draft 15:55. No leftover processes (ps check for sleep 1000).
## Process observations
- Light round with narrow briefs: all three finished in 5-26 min; the opus check-adequacy lens produced most findings, its mutation harness is reusable as the fix gate.
- The worktree hook (no_cd_worktree) blocked two coordinator commands that chained `cd`; use absolute paths from the start.
- A branch that carries unrelated arch commits makes `git merge-base main` meaningless as a review base; the lane's parent had to be used.
## Proposed changes
- Skill §3.1 code mode: "when the branch carries commits beyond the lane under review, BASE is the lane's first commit's parent; record both and diff that range" (this round).
- critics.md check adequacy: "for a check/apply pair, a mutant on the APPLY loop must be caught by the check; shared decode is not shared behaviour" (CA-6).
## Framework notes
- Coordinator plus 3 narrow critics, inline verify: ~40 min wall from launch to draft for a 13-file check change; a verifier agent was not needed when every finding carries a repro.
