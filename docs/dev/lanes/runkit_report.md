# Lane runkit — the run-control tool family (apply_here.md proposals 2 + 6)

Branch `lane/runkit` from main 441ce7e6f. Owner's build go 2026-10-20 ("2 and
6 should be related"). Scripts only, plus their docs; no product change, no
abi event, no `make test` section touched.

## What was built

One family, four scripts under `scripts/`, each with a self-test under
`scripts/tests/` (run by `make testscripts`, D48):

| tool | interface | role |
|---|---|---|
| `boxlock` | `run [--label L] [--wait S\|--no-wait] -- CMD`, `status`, `held`, `path` | the box's one heavy-run lock: flock on `<main>/worktrees/.box.lock`, owner line (pid, starttime, label, since, cwd, token), exec'd CMD holds it for its whole tree |
| `chainrun` | `[--fg] [--lift F] [--keep-going] [--logdir D] [--tree D] [--name N] STAGES`, `--check STAGES` | the chain runner: `NAME heavy\|light CAP CMD` per line; heavy stages take boxlock; one chain/waiter per tree (flock on `TREE/build/.chainrun.lock`); DONE only after the last stage |
| `watchrun` | `[--on chain\|stage] [--quiet-min N] [--every S] [--max-hours H] LOGDIR\|TREE`, `--log F [--pid P] [--done ERE]` | the watcher: exits once, one line, exit code per event (0 end, 3 QUIET, 4 DIED, 5 LOCK-ORPHAN, 6 CAP, 2 not armed) |
| `verdict` | `[--rc N] [--no-rc-lines] LOG...` | the one reader: make error lines (both forms), perfrun DONE (+ LOG.perfrun), mech COMPLETE/FATAL, battery, chainrun, run_group, `rc=` status lines; GREEN/RED/INCOMPLETE, exit 0/1/2 |

How "2 and 6 are related": chainrun takes the box lock for each `heavy`
stage (waiting, the holder named in the stage log; the wait is not counted in
the stage cap); chainrun reads each stage's pass/fail through `verdict`;
watchrun reads chainrun's `chain.log`/`chain.pid`/tree lock record, polls
`boxlock status` (LOCK-ORPHAN on a transition), and prints `verdict`'s line
with every end event. Nesting is by token: `boxlock run` exports
`PCREC_BOXLOCK_HELD`/`PCREC_BOXLOCK_FILE`, and `boxlock held` lets an entry
point inside the holder's tree proceed, so a battery's mech stage or a heavy
stage calling perfrun never deadlocks.

## Where the lock is integrated (all default ON, waiting)

- `scripts/perfrun` run mode (not `--next`/`--fold`): re-execs under the lock.
- `scripts/battery.sh`: the detached run holds it for the whole battery.
- `tests/mech/run_sabotage_matrix.sh`: any run, single rows included, except
  `VALIDATE_ONLY=1`.
- `scripts/emit_sweep.py`: when it sweeps the corpus argv streams, or runs
  `--variant`/`--data`; not `--no-corpus`, `--limit <= 50`, or a
  composition/dumps-only run (`BOX_LOCK_CAP = 50`, BOILERPLATE's cap).
- `make test-axes` (both sweeps under one hold) and `make test-ksweep`.

Why default ON and waiting: every one of these is heavy by definition, and
the recorded breaks were all runs whose launcher did not think to check.
Waiting turns an overlap into a queue instead of a contaminated verdict, and
the first stderr line names the holder at once. A lane that would rather fail
fast sets `PCREC_BOXLOCK_WAIT=0` (exit 75, `boxlock: REFUSED ...`).
`PCREC_BOXLOCK=0` runs unlocked and says so. Runs that never call boxlock
still work. That covers the kit's and the bench's own scripts, CI, and
plain `make test`. A box with no `flock` (the Mac) and a non-git tree run
unlocked, each with a note.

BOILERPLATE now carries the numeric sweep cap: a loop above 50 compiles is
heavy and runs as `scripts/boxlock run --label NAME -- CMD` or as a `heavy`
chainrun stage.

## Self-test results (bug classes planted back, each caught)

`make testscripts` in this worktree (TMPDIR = worktree build/scratch):
boxlock.test 17/17, chainrun.test 26/26, watchrun.test 16/16,
verdict.test 28/28. Untouched tests re-ran because of their dependencies;
the results are in the STATE AT HANDOFF section below.

Each historical bug class was planted back into a scratch copy of the script,
and the matching case catches it:

- **rc lost through `$(...)`:** chainrun planted with `wait; stamp=$(date
  +%s); rc=$?`. The `exit 3` stage then reads rc=0, and the case fails.
- **DONE before the last stage:** two plants, a skipped failure check and an
  EXIT trap that writes DONE (the 2026-10-09 slot bug). Both write DONE on a
  failed chain, and both are caught. The real script stops at the failed
  stage, never runs the later ones, and writes `CHAIN FAILED`. A TERM'd
  chain writes `CHAIN FAILED ... killed=SIGTERM`.
- **Watcher firing on its startup state:** two plants. One drops the
  already-ended guard, and the watcher then fires at once. The other counts
  quiet from the tree's 2-hour-old commit, and the watcher then fires after
  3 s against a 5 s bound. Both are caught. A third plant, a one-miss stall
  test, is also caught.
- **A red make line read as green:** the pre-2026-10-06 `\*\*\* \[test-`
  reader misses `make: *** [Makefile:646: test-corpus] Error 1`, and the case
  catches the miss.
- **A stale lock from a dead PID:**
  - An owner record left by a dead pid reads `free (last holder ...
    exited)`, and the next taker proceeds at once. A planted record-file
    lock (the pidfile pattern) is blocked by that record, and the case
    catches it.
  - An orphaned holder gives `status` exit 3 and lists the live pid.
  - watchrun reports the change to orphaned as LOCK-ORPHAN. An orphan
    already present at startup only gets a warning.
- **Two waiters on one worktree:** a second chainrun in a tree with a live
  waiter is refused (75) and names the waiter's pid. The planted no-lock
  copy starts anyway, and the case catches it.

Integration was checked under a held sacrificial lock with
`PCREC_BOXLOCK_WAIT=0`: perfrun, mech `S1`, `make test-axes` and battery.sh
each refused with 75 or REFUSED and the holder named, and none of them ran
any work. `VALIDATE_ONLY` mech did not take the lock. The four "heavy"
emit_sweep shapes refused and the four light ones did not. All nine
sabotage anchors on `emit_sweep.py`/`run_axes.sh` still match once.
`make strict` green. Plan lint 2/2.

## For the manager to rule

1. **Not locked yet, though heavy:**
   - plain `make test` (lanes that call it without perfrun; CI must stay
     unlocked, so a wrapper would need opt-in);
   - `make san`/`ubsan`/`asan`/`lint`/`alloc`/`test-recursion-identity`
     run directly. The battery covers them as stages;
   - the python censuses: cls_identity.py, compile_time_census.py,
     alt_census.py.
   Each takes the same one-line wrapper. Recommendation: wrap the
   sanitizer targets and recursion-identity now. Leave plain `make test` to
   the BOILERPLATE rule that full suites go through perfrun.
2. **pcrec-bench and the kit:** both run their own scripts, unlocked. The
   kit's in-tree slots do take the lock when they call perfrun or mech. Bench
   nights could call `boxlock run` against the same file
   (`PCREC_BOXLOCK_FILE=/home/pcrec/projects/pcrec/worktrees/.box.lock`), but
   that is the bench's call through the inbox.
3. **Migration still owed** (outside this brief):
   - the pcrec-manager skill's watcher advice should say "use watchrun";
   - memory `pcrec-box-concurrency` rule 12 can point at BOILERPLATE's cap;
   - learnings.md §6 can point at watchrun.
4. Mech takes the lock before it validates ids, so a typo'd id waits for the
   lock and then FATALs. That is harmless, but it is a different order from
   before.
5. `emit_sweep.py.test`'s opt-in variant plants (`EMIT_SWEEP_VARIANT_PLANTS=1`)
   are a heavy sweep, so they now take the lock. Behind a long holder they
   could reach their 900 s timeout. That is the correct behaviour for a
   heavy sweep, and it is noted here so a red read that way is understood.
6. `cap=ttune` uses a growth factor of 1.5 (`CHAINRUN_GROWTH`). That is a
   policy margin, not a measurement. It applies only to rows on a box with
   the same nproc, clean and rc=0.

## STATE AT HANDOFF

Branch tip: see the handback message (the last commit adds this report).

Validation COMPLETE:
- the four self-tests, run directly: 17/26/16/28, all PASS;
- `make strict`: rc=0;
- `bash tests/plan_lint/run_plan_lint.sh`: 2 passed;
- the integration refusal checks above;
- `make testscripts`: see the handback message for its final line.

OWED: nothing heavy. No `make test` section changed. Mech's driver gained
only the lock re-exec ahead of its scratch setup, and no sabotage anchors
it.

A fresh agent resumes by rulings 1-3 above. Each is a one-line wrapper or a
doc pointer.
