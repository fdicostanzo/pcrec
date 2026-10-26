# [BOXQUEUE] — one box-wide job queue (plan row body)

Filed 2026-10-20 by Frank, session 120, from a discussion of `scripts/chainrun`.
Build go: "Build it tomorrow. You might learn some other requirements from this
run" (2026-10-20, about the ctxp2d validation chain then running).

## The problem

`chainrun` reads its stages file once (a snapshot, deliberately: editing a
running chain script was a recurring bug), so a running chain cannot be
reordered, extended or partly retried; a failed stage means a new chain by
hand. Separately, heavy work from main, the kit and the bench is coordinated
by promises in briefs and slot handshakes; on 2026-10-20 three main lanes
loaded the box during the kit's heavy slot and contaminated its make test.
`scripts/boxlock` serializes runs that take it, but holds no ORDER.

## The design agreed in discussion (Frank, 2026-10-20)

- A queue DIRECTORY: `pending/`, `running/`, `done/`, `failed/`. Each job is one
  executable SCRIPT; its name prefix sets the preferred order (`100-maketest`),
  and carries the owner (main / kit / bench / a lane). Reorder = rename; insert
  = a new file; retry = a copy put back into `pending/` where wanted; a long
  chain = several jobs, so a failed piece re-queues alone.
- ONE runner holds `scripts/boxlock` for each job. It walks `pending/` in order
  and RUNS each candidate; the job's EXIT CODE tells the runner what to do:

  | exit | meaning | runner |
  |---|---|---|
  | 0 | done, green | `done/` |
  | 75 | not ready yet (EX_TEMPFAIL, boxlock's code) | stays in `pending/`, asked next pass |
  | 76 | requeue me | to the end of `pending/` |
  | 77 | never (obsolete/cancelled) | `done/`, marked cancelled (queuewatch: `CANCELLED`, informational, never RED; same for `boxqueue cancel` of a pending or RUNNING job, 2026-10-26) |
  | other | failed | `failed/` with its log + verdict |

- Readiness (dependencies, time windows, quiet gates) lives at the TOP of each
  job script, before any side effect: "build job green", "past 01:00 and Frank
  cleared tonight", "CI green". No dependency language in the runner.
- Snapshot at start: the runner copies the script to `running/` and executes
  the copy; a 75 discards the copy and the pending original stays editable.
- Safety rules: a not-ready answer comes within seconds (a check that hangs is
  killed after a short bound and counts as not-ready, logged); a job that has
  side effects and then returns 75 is a bug the self-test plants; every pass
  logs every job's answer (so "why hasn't X run" has a one-line answer, which
  owner.md can show); a job not-ready past its stated patience is reported.
- Shared by main, the kit and the bench: a session reorders only its OWN jobs.
  `chainrun` stage files become batches of jobs (nothing is thrown away).

## Built (lane boxqueue, 2026-10-21)

`scripts/boxqueue` (contract in its header, summary in scripts/CLAUDE.md,
self-test scripts/tests/boxqueue.test planting each bug class below), the
lane template in docs/dev/lanes/BOILERPLATE.md "Queue template". Where the
build reads the design: the job is called in three MODES (`--dry-run`,
`--ready`, the work) because `boxqueue --dry-run` must run a job's readiness
check without its work; so 75 belongs to `--ready`, and a 75 from the work is
the planted "side effects, then 75" bug (failed, never re-run). Requirement
-> how met: docs/dev/lanes/boxqueue_report.md.

## Built (lane qscripts, 2026-10-26)

Three corrections to the queue and its watcher. (1) `boxqueue: size NAME=N` ([EXPECT-PREFLIGHT]): a dry run declares a population
it measures cheaply; a done run records `size=NAME=N` in its result; `add`/`plan`/START derive the effective cap = max(declared,
worst seconds-per-unit of the last 5 green runs of the KEY x N x 125%), written to running/NAME/cap. An `expect` that IS the
population is printed by the dry run from the same measurement (it is re-run at START). No size = the old behaviour.
(2) a deliberate stop is its own class: `boxqueue cancel KEY` on a RUNNING job writes running/NAME/cancelled then safekills the
job's group (and the battery.pid its logdir names); the end is `outcome=cancelled reason=CANCELLED-BY-OWNER`; queuewatch prints
`CANCELLED NAME ...` for every outcome=cancelled end, queuemon journals it INFO. (3) QUIET on a bench reservation samples the
bench's own files (params log=, last `chain pid/pgid N, output P` line), not the idle placeholder. Report: docs/dev/lanes/qscripts_report.md.

## Built (lane qscripts2, 2026-10-26)

A time gate is declared, not hand-coded: `boxqueue: not-before YYYY-MM-DDTHH:MM[:SS]` (local time, strict grammar, refused at `add`). boxqueue holds
the job until then without asking `--ready` (`not-ready: not before T`, shown by plan/status). queuewatch's PENDING-STUCK skips a job only while
now < its declared not-before and ages it from T afterwards; every other not-ready answer ages as before (the earlier any-not-ready exemption was
rejected). Old hand-written --ready gates keep working; new time gates use not-before. Report: docs/dev/lanes/qscripts2_report.md.

## Requirements observed from the 2026-10-20 ctxp2d chain (append as found)

- The armed stage list omitted one owed check (recursion identity); with a
  queue it is one more job dropped in, not a new chain.
- Four of ten stages failed on their INVOCATION, not their subject: `--extra -e`
  rejected by argparse (rc 2 in 0 s); `make mech S1171 ...` read the ids as make
  targets and ran the FULL matrix to two cap fires (100 min of box time lost); a
  witness script compared artifacts written to different `-o` basenames (8/8
  false DIFFER, the known trap). Requirement: a job declares a cheap `--dry`
  preflight the runner calls at ENQUEUE time (argument parsing, ids resolve,
  files exist), and a job whose first seconds look wrong (rc 2 instantly, or a
  population far larger than declared) is reported at once rather than at cap.
  A job also states its EXPECTED population (e.g. "6 mech rows") so the runner
  can compare it with what the job's own log reports.
- A heavy stage waiting on the lock held by another stage of the SAME chain is
  correct queueing, but it is invisible in the chain log until the stage ends;
  the runner's per-pass log should show "waiting on <holder>".
- chainrun allows one chain per tree, so the corrective stages could not be
  queued behind the still-running first chain; the lane hand-wrote a detached
  flock waiter (build/p2dval/s2/arm.sh) — the very pattern chainrun replaced.
  With a queue, corrective jobs are simply enqueued after the running one.
- (2026-10-20 night, lane p2dland) `scripts/emit_sweep.py` printed no
  completion line, so `scripts/verdict` read a FINISHED sweep's log as
  INCOMPLETE and the lane read arms.tsv by hand. Requirement: every heavy
  tool's log ends with a completion line the shared readers recognise —
  met by ONE convention, `TOOL: DONE rc=N` (perfrun's form, now read for any
  tool by verdict and watchrun; emit_sweep prints it on every ending), not by
  a per-job declared completion pattern (lane boxqueue, 2026-10-21).
- (found while building, lane boxqueue) the `make mech S1171 ...` invocation
  was the lane BOILERPLATE's own heavy-chain template (`mech heavy 5400 make
  mech S222 S223`): the make target takes no ids. A template that is never
  run is prose; the template now uses `run_sabotage_matrix.sh IDS`, and the
  queue template's dry run resolves the ids (`VALIDATE_ONLY=1`).

## Dry-run contract (Frank, 2026-10-20: "each script could support --dry-run for testing")

- Every job script accepts `--dry-run`: it does everything EXCEPT the work —
  parses its arguments, resolves its ids (mech rows, sweep arms, refs), checks
  that binaries and inputs exist, and prints the exact commands it would run
  plus its EXPECTED population (rows, cells, arms). No side effects, bounded to
  a few seconds; exit 0 = would run correctly, non-zero = would not (reason on
  stderr).
- Dry-run answers "would I run CORRECTLY", which is different from readiness
  (exit 75) answering "can I run NOW"; a job can pass one and fail the other.
- The runner calls `--dry-run` at ENQUEUE (a job that fails it is refused at
  once, so a bad invocation never waits hours for a slot) and again just before
  START (the tree or inputs may have changed meanwhile).
- `boxqueue --dry-run` runs every pending job's dry run and readiness check and
  prints the plan: order, ready/not-ready, expected populations, total cap — a
  whole queue can be checked before a night is committed to it.
- The runner's self-test plants a job whose dry run lies (passes, then the
  real run's population differs from the declared one) and shows the runner
  flags it from the job's own log.
- The corrected sweep stage failed AGAIN in 0 s: `--arms` and `--extra` are
  mutually exclusive in emit_sweep.py. A fix written without running the fixed
  command is the dry-run contract's own case: the fix lane's re-arm would have
  been refused at enqueue.
