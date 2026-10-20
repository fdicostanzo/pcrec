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
  | 77 | never (obsolete/cancelled) | `done/`, marked cancelled |
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

## Requirements observed from the 2026-10-20 ctxp2d chain (append as found)

- The armed stage list omitted one owed check (recursion identity); with a
  queue it is one more job dropped in, not a new chain.
