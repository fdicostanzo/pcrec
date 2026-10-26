# qscripts2 report: PENDING-STUCK exempts only a DECLARED time gate (2026-10-26)

STATE AT HANDOFF: built and committed on lane/qscripts (continues fe7dad9e9). Rulings file read: no entries ("none yet") at the last check, so no ruling applied.

## Changes
- `scripts/boxqueue`: new dry-run declaration `boxqueue: not-before YYYY-MM-DDTHH:MM[:SS]` (local time; strict regex + `date -d` must accept it; anything else,
  including a space instead of T, an offset, an impossible date, is refused at `add` with exit 65 like other bad declarations). The pass does not ask `--ready`
  before that time: it answers `not-ready: not before T` (no side effects, the job's --ready is never run), and `plan` does the same, so `status`/`plan` show
  "not before ...". The pass loop needed no restructuring (one guard around the existing `callj ready`). `-h` documents it.
- `scripts/queuewatch`: qscripts' R1 rule (skip any `not-ready:` answer unless past patience) is REMOVED. PENDING-STUCK now reads `boxqueue: not-before T` from
  QUEUE/.state/KEY.decl and ages such a job from T (negative before T, so silent; T + `--stuck-sec` after it). Every other not-ready answer (a failed `after KEY`,
  a broken --ready, READY-HUNG) ages exactly as before qscripts. No separate "waits" flag: the age-from-T rule alone covers both halves.
- Back-compat: a hand-written `--ready` time-gate wrapper (e.g. 600-main-fullsuite-20261027, live) still works unchanged in boxqueue (tested). BUT with R1 removed it now
  ages like any not-ready job, so queuewatch WILL alarm PENDING-STUCK for it after --stuck-sec (1800 s) of waiting. That is the intended consequence of the ruling; future
  time gates should declare `not-before` instead (noted in BOILERPLATE.md queue template, scripts/NOTES.md, BOXQUEUE.md row body, pcrec-monitor skill row 10).
  The pcrec-test skill mentions no time gates (no change).
- Docs updated: scripts/NOTES.md (qscripts2 section), docs/design/plan_row_bodies/BOXQUEUE.md, .claude/skills/pcrec-monitor/SKILL.md row 10,
  docs/dev/lanes/BOILERPLATE.md. scripts/CLAUDE.md is at its 4 KB limit and names no time gates: unchanged.

## Self-tests (private scratch queues only)
Each run ALONE (sequential): boxqueue.test 144/144 (267 s; was 133, +11 for section 28), queuewatch.test 49/49 (340 s; was 46), test_queuemon.sh 45/45 (11 s),
fullsuite_job.sh.test 14/14 (14 s). CONCURRENT (all four started together, as make test would): boxqueue 144/144, queuewatch 49/49, queuemon 45/45 (rc 0), fullsuite_job 14/14 (rc 0).
New cases: boxqueue 28 (gate held, --ready not asked; status+plan show it; released after T; 5 malformed values refused; -h; hand-written gate back-compat) and
queuewatch (future gate silent; 100 s past gate under --stuck-sec silent; 1000 s past gate alarms aged from T; `after KEY` whose KEY failed ALARMS; broken --ready alarms; ready-but-held control).

## Sabotage (all caught, in the test files; no mech matrix rows)
- S1630 declared gate ignored (age from queueing) -> future-gated job reads stuck: caught.
- S1631 the REJECTED qscripts form (any not-ready exempt) -> failed-dependency job goes silent: caught.
- S1632 boxqueue does not enforce the gate (--ready asked before T): caught.
- The earlier unnamed `declaredwait` plant is retired (its rule no longer exists).

## The queuewatch.test / boxqueue.test flake
Not reproduced: alone and concurrent runs were all green. Looked for shared state and found none: every test makes its own `mktemp -d` and exports
PCREC_BOXQUEUE_DIR, PCREC_BOXLOCK_FILE (per scenario) and FULLSUITE_SIM_DIR; boxlock's yield check reads PCREC_BOXQUEUE_DIR (the scratch one); no fixed /tmp path, port or
shared lock exists in boxqueue/queuewatch/boxlock/fullsuite_job. The only defaults that would point at the LIVE queue/lock (<main>/worktrees/.boxqueue, .box.lock) are
overridden by the env in each test. Best explanation: the QUIET case is wall-clock/CPU-rate based (SIM_QUIET=9 s silence, 5%-of-a-core CPU threshold, 2 s watcher relaunches),
so a loaded box (boxqueue.test's fork-heavy loops plus other sessions) can shift it. Treat a repeat as load sensitivity unless it shows a shared path; if it recurs,
capture the failing case's `$T` before cleanup.

## LANDING NOTE
After merge the runner re-execs at an idle pass (reexec_if_changed); queuemon needs `scripts/queuemon stop` then `scripts/queuemon start`; restart any standing queuewatch.
Job 600-main-fullsuite-20261027 (hand-written gate) will draw a PENDING-STUCK alarm after 1800 s pending once the new queuewatch runs: expected, not a fault.
Sabotage ids used: S1630-S1632.
