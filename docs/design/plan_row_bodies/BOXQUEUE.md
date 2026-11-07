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
lane template in docs/dev/lanes/RUNS.md "Queue template". Where the
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

## Built (lane qorder, 2026-11-01)

Owner GO 2026-11-01: order by the "unsharded run length"; "if there are waiting jobs and the box is free then let the next job run".
Report: docs/dev/lanes/qorder_report.md. Four changes to the queue and its watcher.

(1) START ORDER. Among the READY jobs the next one started is the one with the shortest expected run. The expected run is a declared
number: `boxqueue: est SECONDS` (a new optional dry-run directive), else the job's cap (cap none = last). A shard of a longer run
declares `boxqueue: run-total SECONDS`, the UNSHARDED total, and that is its length, so shards of one 5000 s run do not each jump
ahead of a 1000 s job on their own small caps. (Rejected: summing the pending members of a shard set. It needs a set identity the
queue does not have, and the remaining work shrinks as shards finish, so the last shards would jump the queue, the opposite of the
ask. A declared total is the same number for every shard.) `est` past the cap and `run-total` below `est` are refused at add.
The rule is a DECLARED first-match table (`ORDER_ROWS` in scripts/boxqueue, printed by the header): each ready job falls under the
first row that holds and is sorted by (row, that row's key, name in C-locale):

| row | holds when | sorts by | why |
|---|---|---|---|
| reservation | an imported bench window (job `PRIO-bench-W` with a `.bench` params file) | PRIO | the bench's start time is a promise; the window must not wait behind a shorter job |
| override | PRIO below 100 (`BOXQUEUE_OVERRIDE_BELOW`) | PRIO | the explicit "go first" lane; nobody uses PRIO < 100 today |
| starved | ready and passed over for 14400 s (`BOXQUEUE_STARVE_AFTER`) | longest wait first | the starvation bound: shortest-first alone would starve a long job indefinitely |
| length | everything else | expected run, then name | the owner's rule; equal lengths and cap ties fall back to today's name order |

So a PRIO of 100 and up (every PRIO in use) no longer orders the queue; it is the tie-break. The old BOILERPLATE advice to give the
shorter overall run the earlier number is now automatic. "Ready" time is the runner's first ready answer (`.state/KEY.ready`,
cleared by any not-ready answer). A not-ready job never holds up a ready one. Cross-session: every owner's jobs go through the same
table. Every number is an UNMEASURED default: 100, 14400 s (about one long job's run), the 30 s cap-kill grace. `plan` prints the
order; `status` says, for a ready job that waits, which job goes first and by which row; queue.log has one `ORDER` line per pass.
The runner's pass sleep is also cut to the nearest declared not-before, so a gate opens when it says, not up to a pass pace later.

(2) [QUEUE-CAPKILL]. The cap used to be `timeout --kill-after=60` around the job, which TERMed the job's own pid: any descendant that
had changed process group or session survived with the box lock (its fd is inherited). 2026-10-31: job 745-vmrecm-test's make test
tree outlived its cap for 64 minutes. Now the runner's own watcher enforces the cap: marker `running/NAME/capfired`, safekill of the
job's group AND ppid tree (TERM, grace, KILL), then safekill of every process still holding the box-lock file open that is not the
runner's own `_start` chain (`boxlock holders`; a double-forked straggler belongs to no tree but it IS the lock). The end reads
`CAP-FIRED`; `capkill.log` in the run dir and one `CAP-KILL` line in queue.log say what was killed and whether anything still holds the lock.
Not done (no measured need): sweeping lock holders after a NORMAL end.

(3) `.window` gains `not_before=YYYY-MM-DDTHH:MM[:SS]`, the same strict local-time parse as the job directive (one function,
`nb_epoch`). The placeholder declares it, so the window queues at once, is held by the queue's own time gate and shows in
status/plan; the bench no longer needs a detached sleeper. Revised [B146] contract: docs/dev/lanes/qorder_bench_inbox_draft.md.

(4) WINDOW-MISSED (queuewatch). One event line when a window DECLARED with `not_before=` has its start pass by `--missed-window-sec`
(900, unmeasured) with the window never started, not cancelled by its owner, and no job of its owner pending or running. It is a
PROBLEM line the standing monitor relays (SKILL.md row 10, one word added). Limit: the notice sees only DECLARED windows; the
2026-10-31 W1 was never declared at all. The not_before key is what lets the bench declare a plan ahead of time.

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
