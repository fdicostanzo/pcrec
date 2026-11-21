# alloclint report

## STATE AT HANDOFF
Job `300-main-alloclint` is queued (pending, runner live, queuemon up). Frozen commit: main db7aab3de9a3e45ad173821abbe45b7c5fc581f6 (resolved when the job starts, by `git rev-parse main`; a later merge on main before it starts moves the frozen commit, recorded in `<logdir>/frozen.txt`). Log directory: `build/alloclint/<date>_<sha9>/` in the main tree (trailer.log, alloc.log, lint.log, summary.txt, frozen.txt). Verdict: `scripts/monread main`; the job's last line is `alloclint: DONE rc=N battery_rc=M`, preceded by `alloclint: stages=K green of 2`. Nothing was run by this lane.

## THE JOB
Route: job file `docs/dev/lanes/alloclint_job` (committed), because scripts/fullsuite_job.sh has a fixed stage list and reads no BATTERY_STAGES from the environment or an option (a queued job takes no arguments). The file freezes main in a detached worktree `worktrees/alloclint-run-<date>_<sha>` (left for scripts/wtprune), runs `BATTERY_STAGES="alloc lint" scripts/battery.sh` there (battery.sh resolves the compiler via tests/lib/cc_resolve.sh for lint), and waits for `== BATTERY DONE`. `--dry-run` declares cap 1800, est 300, expect stages=2. `--ready` is box lock free and no queue job running (no load gate). It writes nothing to build/full_suite/ or docs/dev/full_suite_ledger.md; scripts/battery.sh and scripts/fullsuite_job.sh are unedited. Found on the first add: boxqueue refuses an expect count that comes from a DONE line's own rc, so the count rides a separate `stages=` line before the DONE line.

## OWED RUNS
The queued job itself (key 300-main-alloclint), unwaited. Afterwards: copy the summary.txt line into the ledger by hand if wanted, and `scripts/wtprune` the run worktree.
