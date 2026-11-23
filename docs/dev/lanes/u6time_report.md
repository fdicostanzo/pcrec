# u6time: the C6/C6c timing job (R-47 U6), prepared and rehearsed, NOT QUEUED

## STATE AT HANDOFF
Tree: this worktree at b291a2f7c (branch lane/u6time), built (`make -j16` under boxlock). Rulings file empty at every checkpoint
(last entry applied: none). Nothing timed, nothing queued, no clock read. Work ended before 18:15.
Not rehearsed: the evening refusal (20:00-01:00) and the `evening=ok` override, because it needs a different wall clock; the real
quiet wait and the time stage (timing, forbidden here). The window request's `--ready` floor of 18:15 is replaced by the brief's
20:00-01:00 rule with the clearance file as the authority (see CLEARANCE GATE).

## JOB
`docs/dev/lanes/u6time_evidence/jobs/kit-u6time.job` (one job, three phases; key kit-u6time). Declares cap 3600, est 1400, idle-ok,
patience none, not-before 2026-11-23T00:00, and the request's three expect lines (done=1, truncated=0, verdict=3).
- Freeze: TREE_SHA b291a2f7c is checked at --dry-run, --ready and start (HEAD equal, no tracked changes outside docs/dev/lanes/u6time*
  and artifact_size_log.tsv, build present, SMT sibling of CPU 15 read from sysfs = 7).
- PREPARE: `JOBS=12 cards.py time RUNDIR --prepare --cards C6,C6c`, then `--dry --dry-model tie` which must show `clock calls 0` and
  `DONE rc=0` (else the job stops).
- QUIET: the slot Waiter via the kit's earlier `waitquiet.py` (job 710's, in $PCREC_TMPDIR/scratch/memfn/fcards/jobs/); this lives
  OUTSIDE the tree and is checked by --dry-run.
- TIME: `CPU=15 nice -n 5 cards.py time RUNDIR --cap 3600 --job-start <job start> --stop-at <the clearance stop=>`.
- Then the c6decide read-back of the newest results_c6_*.tsv; the job exits with time's rc.
- TMPDIR=$PCREC_TMPDIR/scratch/u6time/tmp; RUNDIR=$PCREC_TMPDIR/scratch/u6time/run (refused if it exists).
- Prepare, quiet and time are phases of one job, not three boxqueue stages (boxqueue has no per-stage class inside a job); the one job
  is idle-ok as a whole.

## CLEARANCE GATE
File: /home/pcrec/projects/pcrec/worktrees/.mgr/u6time.cleared, one line `start=YYYY-MM-DDTHH:MM stop=YYYY-MM-DDTHH:MM [evening=ok]`.
`--ready` exits 75 (reason on stdout) unless the file exists and parses, start <= now, now + 1400 <= stop. Without `evening=ok` it also
refuses now or now + est in 20:00-01:00. The start re-checks the gate (and again after the quiet wait); --stop-at is the stop=.
The env override U6TIME_CLEARED is read only by --ready (for the drill). The lane never created the real file.
Drill (copies under $PCREC_TMPDIR/scratch/u6time/drill/):
| case | rc |
|---|---|
| no file | 75 |
| past window | 75 |
| valid window (stop = now + 25 min) | 0 |
| window ending at now + 10 min | 75 |
| window starting in the future | 75 |
| valid window, stop = now + 2.5 h | 0 |

## REHEARSAL
- `--dry-run`: exit 0, all declarations printed.
- prepare for real into a scratch rundir under boxlock: exit 0 (14 (pattern, layer) pairs reach-checked, 84 pools built and proved,
  336 exes, 70 disjoint pairs, 92 cells / 168 timed arm cells, harness 0c3674cd272dc615).
- `cards.py time RUNDIR --dry --dry-model tie`: `clock calls 0, timed execs refused 0`, `DONE rc=0`; synthetic C6 on and C6c off-clang read NO LOSS
  (marked NOT A TIMING). Log: $PCREC_TMPDIR/scratch/u6time/rehearse.log.
- Prepare was quick here (about 1 min, caches warm); the request's 3-5 min may be longer cold.
- The job's own body was NOT run end to end (it would time).

## QUEUE COMMAND
For the kit manager, after Frank clears a window and the manager writes the `.cleared` line:

    /home/pcrec/projects/pcrec/scripts/boxqueue add --name 710-kit-u6time /home/pcrec/projects/pcrec/worktrees/u6time/docs/dev/lanes/u6time_evidence/jobs/kit-u6time.job

Needs the u6time worktree to stay at b291a2f7c, built, until the run. Not run by this lane.
