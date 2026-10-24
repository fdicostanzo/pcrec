---
name: pcrec-test
description: Run pcrec's test suites as a delegated, monitored box-queue job. `full` = the whole battery (scripts/battery.sh via scripts/fullsuite_job.sh, D177) on main at a frozen commit; `normal` = make test on a branch or main. The manager queues the job; the standing /pcrec-monitor session (Frank's separate haiku session, scripts/queuewatch) keeps the run going and alerts only on a problem or the verdict, with a per-run monitor agent as the fallback when no session is up; the manager never watches the log. Args: full|normal [branch], plus an optional note.
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
3. The monitor: ask whether the STANDING session is up (`/pcrec-monitor`, Frank starts it; it
   watches the whole queue by itself, nothing to hand it: the job's OWNER field in its key
   says whom it messages). If it is up, launch nothing. If not, launch the per-run FALLBACK
   (section 3): `subagent_type: pcrec-monitor` (.claude/agents/pcrec-monitor.md: haiku, 1-hour
   cache), background, name `mon-<mode>-<short>`, the brief below with the job key filled in.
   (The standing session starts with its own tools test, `scripts/monitor_preflight`, and a
   `MON up` message to the manager; it also watches CI on main, `CI-RED`/`CI-CANCELLED`
   lines, which the per-run fallback ignores.)
   Either way, rehearse a new queue/monitor change first with simulate mode
   (`scripts/fullsuite_job.sh --simulate red:axes --dry-run` is the safe check; the whole
   path is `scripts/tests/queuewatch.test`).
4. `full` only: set ONE one-shot alarm (CronCreate, not recurring) at the
   expected end + 2 h. When it fires and no monitor verdict has arrived,
   read `scripts/boxqueue state <KEY>` and `build/full_suite/*/trailer.log`
   yourself (one look; a problem goes to a triage lane, section 4).
5. Update docs/dev/owner.md (what is running, expected end).

## 3. The monitor

STANDING (the default): the session started with `/pcrec-monitor`
(.claude/skills/pcrec-monitor/SKILL.md). It loops `scripts/queuewatch` in the background (one
event per wake; the reported-events state is a file, so a relaunch never misses or repeats
one) and follows its own first-match table: triage on the first red stage, ledger line on the
verdict, `boxqueue start` once for a dead runner, a message to the job's owner session only
on a red, a problem or a verdict. The manager sends it nothing. Frank `/clear`s it between runs.

FALLBACK (no standing session up): one per-run agent, the same loop on the one run. Brief
(fill the <...>; keep it this short):

    MONITOR <mode> run <KEY> (haiku). Keep it going; act only by the table in
    /home/pcrec/projects/pcrec/.claude/skills/pcrec-monitor/SKILL.md (read it once, now),
    for events of the job <KEY> only. Scope: /home/pcrec/projects/pcrec only; never edit
    code, merge, cancel, kill or run make or any suite.
    LOOP until JOB-DONE for <KEY>, in the background:
      bash /home/pcrec/projects/pcrec/scripts/queuewatch --max-sec 3000
    Read only its one output line. Do not read stage logs; do not explain.

The fallback replaces the old watchrun/trailer-grep loop and `monitor_rules.md` (kept for
reference; its rows 1/5/6 assumed a watchrun that missed battery stage ENDs). A new fix joins
the monitor SKILL's table only when a run has shown its shape (section 5).

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
  line. FIXED 2026-10-24 in scripts/queuewatch (the sleep is cut to the time left).
- 2026-10-23, full run: the monitor MISSED a red stage (axes rc=2). Causes (2026-10-24,
  lane monwatch): (a) battery.sh writes `== stage axes rc=2 END`, chainrun `== stage N END rc=`,
  and watchrun matched only chainrun's shape (FIXED: both shapes, stage and rc extracted);
  (b) each watchrun relaunch baselined the ENDs already in the log, so an END landing between
  two capped calls was never reported; (c) the outer timeout killed watchrun silently;
  (d) a haiku monitor keeping its own "seen" list missed `== BATTERY DONE`. Lesson: what has
  been reported is STATE and belongs in a script. FIX: scripts/queuewatch (persistent state
  file, one event per launch, clamped bound) + the standing /pcrec-monitor session that only
  acts on its lines; proven against simulate-mode jobs (scripts/tests/queuewatch.test).
