# suiteresume report ([SUITE-RESUME], lane suiteresume, sonnet, 2026-10-25)

## STATE AT HANDOFF
Branch lane/suiteresume (worktree worktrees/suiteresume), scripts + docs only. Rulings file had no entries.
Offline: `scripts/tests/fullsuite_resume.test` 33/33, `fullsuite_job.sh.test` 14/14 still green, plan_lint 0,
claudemd sizes OK. Stage (2), the cheap REAL chain, is OWED (recipe below). No make test, no -j, never touched
the live queue (see INCIDENT).

PREMISE (read-only on build/full_suite/20261023_5596c3207): trailer/summary give test strict san alloc lint green,
axes mech recidentity RED(rc=2); `fullsuite_resume --dry-run` on it plans `[axes mech recidentity]`, carried
green `test strict san alloc lint`, cap 53100 s, tree = its frozen worktree (exists, HEAD verified). Its
red_stages.txt lists only mech/recidentity (queuemon writes later reds only), so green/red is read from the
TRAILER's `== stage S rc=N END` lines, never from red_stages.txt.

STOP RULE: not triggered. Every battery stage is one independent `make` invocation (battery.sh keeps no
cross-stage state; the shared state is the tree's build/ which make rebuilds), so a stage subset is re-runnable
(`BATTERY_STAGES`, already in battery.sh, was the hook).

## Design choice
- Shape: `scripts/fullsuite_job.sh [--simulate N] --resume RUNDIR [--dry-run|--ready]` (the work is the same
  script, so the setsid detach, trailer, DONE line, summary and wait loop are the real code) plus
  `scripts/fullsuite_resume [--dry-run] [--name N] RUNDIR`, because a queued job takes NO arguments (boxqueue
  enqueues a copy of one executable): the helper writes a one-line job (`exec bash <fullsuite_job.sh> --resume
  RUNDIR "$@"`) and `boxqueue add`s it (default name 301-main-fullsuite-resume). `boxqueue add` dry-runs the job
  first, so every refusal happens at add time. No boxqueue edit needed. Owner-commanded: queuemon, queuewatch,
  boxqueue, battery.sh, monread do not mention either entry point (asserted by the test).
- Runs in the parent's own frozen worktree (reused; recreated detached at the commit if wtprune'd). "Same
  commit" is checked as the worktree's HEAD == frozen.txt's commit, NOT main's HEAD (main has moved on; that
  reading would refuse every resume). CONSEQUENCE for the owner: a resume reproduces the same code, so it
  cures flakes/box faults only; a red caused by a code fault needs the fix on main and a FRESH full run.
- Green = a `== stage S rc=0 END` line (own trailer, or for a chain the carried origin's trailer, re-verified).
  Resume stage set = parent's own `== stages:` line (or its resume_of.txt `stageset`), so a reduced parent
  resumes within its set and the expect/DONE count follows (`stages=N`).
- Resume logdir `build/full_suite/<tag>_r<N>`: `== logdir`, trailer.log, summary.txt, `== battery_v5 DONE
  stages=N rc=`, frozen.txt (same format, chains), resume_of.txt (parent, commit, stageset, rerun, `carried S
  ORIGIN` lines). summary.txt: carried stages `green(@<origin tag>)`, ends `resume-of=<parent>`; the DONE line
  counts carried greens so stages=8 == combined all-green. queuewatch/queuemon read trailer.log + summary.txt +
  the logdir line, all as for a full run. NOTE queuemon's ledger() will append a GREEN/RED row for a resume
  like any run (and commit it): that is the combined verdict row, but a STAGED test run would also write one;
  revert it (it is not a real run).
- Refusals, all exit 65 and also in --dry-run: missing trailer.log/summary.txt/frozen.txt; run dir absent;
  battery.pid alive; SIMULATED/real mismatch; worktree HEAD != commit; dirty worktree; worktree gone AND commit
  unknown (simulate: gone); summary names a stage green with no green record; chained carry whose origin lost its
  record; unknown stage name in the stage line; nothing red/unrun.
- FINDING: a finished run's worktree is never porcelain-clean (make test rewrites docs/dev/artifact_size_log.tsv;
  the real 20261023 tree shows ` M` on it). The dirty check tolerates exactly that file (`RESUME_DIRTY_OK`
  overrides). Everything else dirty refuses.
- Guard added to fullsuite_job.sh: any argument other than ""/--dry-run/--ready exits 64 before any side effect.
  fullsuite_resume also greps for `SUITE-RESUME` in the job before calling it.

## INCIDENT (mine, disclosed)
My first `fullsuite_resume --dry-run` defaulted to MAIN's fullsuite_job.sh, which predates `--resume`, ignores it,
and so started a REAL full suite (worktree + battery waiting on the box lock behind job 624; no stage started).
My safekill was denied by the classifier; the manager cleaned it up (run dir/worktree 20261025_9ca6fce02 are
gone). Fixes: the helper uses the fullsuite_job.sh next to itself, checks for the marker, and the unknown-argument
guard above. LESSON for the manager: until this lane merges, main's fullsuite_job.sh treats ANY argument as a real run.

## Proposed D-entry text (number yours)
Full-suite resume is stage-level and owner-commanded: `fullsuite_job.sh --resume RUNDIR` re-runs the stages with no
green trailer record, in the parent's frozen worktree at the parent's commit, and reports a combined verdict naming
both runs; no queue/monitor/battery component starts one (auto-restart can mask a real fault). It cures flakes, not
code faults (same commit).

## Stage (2): staged real test on a cheap chain (OWED; manager queues; ~4 min real)
Needs this lane merged (the job must know `--resume`). Parent = a REAL reduced battery run killed mid-way:
1. `git worktree add --detach worktrees/fullsuite-run-staged_<sha> <main full sha>`; `mkdir build/full_suite/staged_<sha>`;
   write its frozen.txt as `== full suite staged_<sha> frozen at <FULL 40-hex sha> tree <abs worktree path>`.
2. As a boxqueue job (box lock; strict ~10 s, alloc ~40-100 s, lint ~60-90 s):
   `BATTERY_STAGES="strict alloc lint" bash <wt>/scripts/battery.sh build/full_suite/staged_<sha>`; poll trailer.log
   for `== stage strict rc=0 END`, then `scripts/safekill $(cat .../battery.pid)` so alloc and lint have START
   (or none) but no END. Write summary.txt by hand: `<date> <sha9> strict=green alloc=MISSING lint=MISSING log=build/full_suite/staged_<sha> duration=0s`.
3. `scripts/fullsuite_resume --dry-run build/full_suite/staged_<sha>` must say stages [alloc lint], carried strict.
4. `scripts/fullsuite_resume build/full_suite/staged_<sha>` (queues 301-main-fullsuite-resume).
EXPECT: job green; `build/full_suite/staged_<sha>_r1/` with trailer stages `alloc lint` only (no strict START),
summary `strict=green(@staged_<sha>) alloc=green lint=green ... resume-of=build/full_suite/staged_<sha>`,
`== battery_v5 DONE stages=3 rc=0`; queuewatch/queuemon print STAGE-END alloc/lint and JOB-DONE green (and
queuemon appends a ledger row: revert it). Then `scripts/wtprune` the staged worktree and remove both logdirs.
Optional refusal check on the real dirs: a second `fullsuite_resume --dry-run` of the _r1 dir exits 65 (nothing to resume).
