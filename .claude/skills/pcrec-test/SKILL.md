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
3. Launch the monitor (section 3): `subagent_type: pcrec-monitor` (.claude/agents/pcrec-monitor.md: haiku, 1-hour cache), background, name
   `mon-<mode>-<short>`, the brief below with the job key and log path
   filled in. Nothing else in its prompt.
4. `full` only: set ONE one-shot alarm (CronCreate, not recurring) at the
   expected end + 2 h. When it fires and no monitor verdict has arrived,
   read `scripts/boxqueue state <KEY>` and `build/full_suite/*/trailer.log`
   yourself (one look; a problem goes to a triage lane, section 4).
5. Update docs/dev/owner.md (what is running, expected end).

## 3. The monitor brief (fill the <...>; keep it this short)

    MONITOR <mode> run <KEY> (haiku). Keep it going; act only by the table
    in /home/pcrec/projects/pcrec/.claude/skills/pcrec-test/monitor_rules.md
    (read it once, now). Scope: /home/pcrec/projects/pcrec only; never edit
    code, merge, cancel, kill or run make or any suite.
    TRAILER=<path> SUMMARY=<path> LEDGER=docs/dev/full_suite_ledger.md
    LOOP until done:
      timeout 590 bash /home/pcrec/projects/pcrec/scripts/watchrun --on stage --log <TRAILER> --max-sec 480
    Read only its one output line (and, on a stage END, that stage's rc).
    Do not read stage logs; do not explain.

For `full`: TRAILER = `build/full_suite/<date>_<sha>/trailer.log` (the
job's frozen.txt names it once the run starts; until it exists, poll
`scripts/boxqueue state <KEY>` inside `timeout 590` with a 5-min sleep),
SUMMARY = `summary.txt` beside it.

The monitor's actions are the first-match table in `monitor_rules.md`
beside this file: mechanical fixes it may run itself (each ONCE, then it
alerts), the triage launch on a red stage, and the green bookkeeping. A
new fix joins that table only when a run has shown its shape (section 5).

## 4. On the verdict (manager)

- GREEN: the monitor has appended the ledger line and committed it; check
  the commit, reset nothing by hand (the ledger line IS the reset, D177);
  prune the run's worktree (`scripts/wtprune`); tell Frank in one line.
- RED: the monitor has already launched the triage lane (it starts at the
  FIRST red stage, while later stages still run). Read its report, rule,
  send fixes to lanes. Never read the stage logs yourself.
- A PROBLEM message: decide (the monitor never cancels or kills).
- TaskStop the monitor once its final message is in; delete the alarm.

## 5. Lessons

Append dated lessons here when a run teaches one (a missed wake, a wrong
trailer, a monitor that read too much).
- 2026-10-23, first run (iterland test + mech): worked end to end (red caught, triage
  launched, green reported). A teammate monitor cannot spawn NAMED agents (launch triage
  unnamed); the triage's final reply reached the manager, not the monitor, so the triage
  FILE is the delivery and the monitor must not wait for a reply.
- 2026-10-23, full run: watchrun checks `--max-sec` only at poll boundaries (`--every`,
  60 s), so 570 + 60 overran the monitor's `timeout 590` and every call ended 124 with no
  line. Keep max-sec + every under the outer timeout (480 now).
