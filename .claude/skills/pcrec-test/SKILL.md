---
name: pcrec-test
description: Run pcrec's test suites as a delegated, monitored box-queue job. `full` = the whole battery (scripts/battery.sh via scripts/fullsuite_job.sh, D177) on main at a frozen commit; `normal` = make test on a branch or main. The manager queues the job and launches ONE small monitor agent that keeps the run going and alerts only on a problem or the verdict; the manager never watches the log. Args: full|normal [branch], plus an optional note.
---

# pcrec test run (delegated)

Frank, 2026-10-23: test runs are delegated. The manager queues, a monitor
keeps the run going, the manager hears only a verdict or a problem. The
monitor is SMALL: every wake re-reads its whole context, so it carries a
short brief, reads nothing else, and lets scripts do the waiting.

## 1. Modes

| mode | job | target | runtime | when |
|---|---|---|---|---|
| `full` | `scripts/fullsuite_job.sh` (battery: test strict axes san alloc lint mech recidentity) | main, frozen at queue start | many hours (stage sum ~46,000 s; cap 16 h) | D177's triggers (docs/dev/full_suite_ledger.md), in a box window cleared with Frank |
| `normal` | a make test job for the branch (until a shared job script exists, the lane's or landing's own job file) | a branch or main | ~25 min | before a landing, after a fix |

## 2. Launch (manager)

1. `scripts/boxlock status` and `scripts/boxqueue status`; for `full`,
   confirm the window (memory: the box is shared with Frank) and that no
   merge is due during the run (the frozen commit protects the battery, but
   the verdict is only about that commit).
2. Queue: `scripts/boxqueue add --name 300-main-fullsuite scripts/fullsuite_job.sh`
   (normal: the branch's job file). NEVER test a job with `boxqueue add`
   into a scratch queue: that arms a real runner (2026-10-23 incident);
   `JOB --dry-run` is the only safe check.
3. Launch the monitor (section 3): `model: haiku`, background, name
   `mon-<mode>-<short>`, the brief below with the job key and log path
   filled in. Nothing else in its prompt.
4. `full` only: set ONE one-shot alarm (CronCreate, not recurring) at the
   expected end + 2 h. When it fires and no monitor verdict has arrived,
   read `scripts/boxqueue state <KEY>` and `build/full_suite/*/trailer.log`
   yourself (one look; a problem goes to a triage lane, section 4).
5. Update docs/dev/owner.md (what is running, expected end).

## 3. The monitor brief (fill the <...>; keep it this short)

    MONITOR <mode> run <KEY> (haiku). Keep it going; alert only on a problem
    or the verdict. Scope: read-only in /home/pcrec/projects/pcrec; never
    edit, commit, merge, cancel or retry; never run make or any suite.
    LOOP until done:
      timeout 590 bash /home/pcrec/projects/pcrec/scripts/watchrun --log <TRAILER> --max-sec 570
      (exit with no line = cap, loop again; read only its one output line)
    On each line: CHAIN-END / BATTERY DONE -> read <SUMMARY> (one line) and
    `bash /home/pcrec/projects/pcrec/scripts/boxqueue state <KEY>`; send the
    manager ONE message: "MON <KEY>: <summary line>" then END.
    QUIET or DIED or LOCK-ORPHAN -> send "MON <KEY> PROBLEM: <the line>",
    then keep looping (the manager decides; you never act on the run).
    Do not read logs beyond the one summary line; do not explain.

For `full`: TRAILER = `build/full_suite/<date>_<sha>/trailer.log` (the
job's frozen.txt names it once the run starts; until it exists, loop on
`scripts/boxqueue state <KEY>` every 5 min with `sleep` inside a bounded
`timeout 590`), SUMMARY = `summary.txt` beside it.

## 4. On the verdict (manager)

- GREEN: copy summary.txt's line into docs/dev/full_suite_ledger.md
  "Runs", reset the counters (D177), commit named paths; prune the run's
  worktree with `scripts/wtprune`; tell Frank in one line.
- RED or a problem: a TRIAGE lane (sonnet, read-only first): per red
  stage, stale pin vs real regression, with evidence; one short report.
  The manager rules; fixes go to lanes. Never read the stage logs yourself.
- TaskStop the monitor once its message is in; delete the alarm.

## 5. Lessons

Append dated lessons here when a run teaches one (a missed wake, a wrong
trailer, a monitor that read too much).
