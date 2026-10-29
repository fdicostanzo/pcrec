# monwatch report ([MONITOR-QUEUE], lane monwatch, 2026-10-24)

Branch lane/monwatch. Premise test: confirmed. In build/full_suite/20261023_5596c3207/trailer.log no line matches
`^== stage [^ ]* END` (battery shape `== stage axes rc=2 END`); chainrun's `== stage N END rc=R` does.

## What was built (four commits, in order)

1. FORMAT FIX (scripts/watchrun): `END_ERE='^== stage [^ ]+ (rc=[0-9]+ )?END'`; STAGE-END now prints
   `stage=S rc=N :: <line>`. battery.sh's line is unchanged (verdict, chainrun's parser and others read it).
   watchrun.test +4 cases from the real trailer lines and a chainrun-shaped line; PLANT old-pattern -> CAP (red).
2. SIMULATE: `BATTERY_SIMULATE=NAME[:STAGE]` in battery.sh, `fullsuite_job.sh --simulate NAME[:STAGE]`.
   Only the stage payload is replaced (`sim_payload`); setsid detach, battery.pid, trailer, DONE, summary.txt, the job's wait loop
   and its `== battery_v5 DONE` line are the real code. fullsuite_job.sh now also prints `== logdir DIR` (the watcher finds the
   trailer from it). Test: scripts/tests/fullsuite_job.sh.test (14 checks).
3. scripts/queuewatch + scripts/tests/queuewatch.test (16 checks).
4. .claude/skills/pcrec-monitor/SKILL.md; pcrec-test SKILL.md section 2 step 3, section 3 and Lessons rewritten; monitor_rules.md
   marked superseded; scripts/CLAUDE.md and scripts/tests/CLAUDE.md updated.

## Decisions

- Worktree: simulate creates NONE (it runs the battery.sh next to the script), so nothing to prune. Checked: `git worktree list`
  count unchanged and no `worktrees/fullsuite-run-sim*`.
- Box lock: simulate takes none (it must never wait behind, or block, a real suite). `--ready` is always 0 under simulate.
- Guarantees, each with a check: no make/gcc/cc ever called (PATH shims record any call; battery's `gcc --version` probe is not a
  stage); every logdir under the simulate dir with a SIMULATED file and a `== SIMULATED` trailer line (never build/full_suite);
  full_suite_ledger.md checksum unchanged; a stray BATTERY_SIMULATE is unset in the real branch; PLANT (simulate branch
  disabled) -> the shim sees `make`.
- boxqueue: the REAL boxqueue + real runner are used, safely, in a SCRATCH queue (PCREC_BOXQUEUE_DIR) with a sacrificial
  PCREC_BOXLOCK_FILE, queueing only wrapper jobs that `exec fullsuite_job.sh --simulate SCEN`. The test asserts each wrapper
  before `add` and that the runner's queue.log names the scratch queue. The live queue was never added to.
- queuewatch is a NEW script, not a watchrun mode: it needs a persistent state file, multi-job/queue scope and a different
  exit contract (one event per launch); watchrun stays the one-log waiter.
- Event IDs are the artifact lines themselves (queue.log START/END lines, trailer END lines), written to the state file BEFORE
  printing (at-most-once; a SIGKILL in the microseconds between mark and print would drop one, accepted). Conditions are
  episodes (QUIET keyed by last-change epoch; RUNNER-DEAD, DISK-HIGH forgotten when cleared). First launch seeds only jobs that
  had already ended; a running job is reported from its START.
- The bound holds inside the sleep (sleep clamped to the time left): `--every 10 --max-sec 3` returns CAP in 3 s.

## What each scenario showed (queuewatch relaunched after every event and every 2 s)

- green: JOB-START, 8 STAGE-ENDs in order, JOB-DONE green, each once.
- red:axes: axes rc=2 reported, the other stages still reported, JOB-DONE outcome=failed rc=1 verdict=RED reds=axes(rc=2).
- burst (strict and axes ENDs in the same second): both reported, once each, in order.
- die:alloc (battery SIGKILLed, no DONE line): 4 stage ENDs then JOB-DONE failed; no invented alloc END.
- quiet:san (stage silent 9 s, --quiet-sec 4): exactly one QUIET between san's START and END.
- no runner + pending job: RUNNER-DEAD once, PENDING-STUCK once across 4 relaunches; DISK-HIGH once per episode and re-arms.
- fresh state on an already-finished queue: nothing replayed. Second watcher on one state: refused (75). SIGKILLed watcher:
  lock freed (the sleep child does not hold fd 9).
- Plants all go red: state not written, first launch swallowing live events, sleep not clamped.

## Incidents / notes

- Two early manual runs of queuewatch (flags `--state` in scratch) went against the LIVE queue because my shell lost its env
  between calls; queuewatch only reads the queue (opens .runner.lock for append, as boxqueue does), wrote nothing there.
- Row 6/7 of the monitor SKILL write the ledger line; simulated runs are excluded by rule (SIMULATED marker).
- Not done / not asked: `make test` (no product code); the old watchrun `--max-sec` poll-boundary overrun (c) is left in
  watchrun itself (queuewatch has the fix); the monitor SKILL is untested by a live haiku session (Frank starts it).

## STATE AT HANDOFF

Last ruling applied: none (monwatch_rulings.md empty). Worktree /home/pcrec/projects/pcrec/worktrees/monwatch, branch
lane/monwatch, all committed except this report if not yet committed. `make testscripts` result: see the reply to the manager.
Merge needs `make strict` is not applicable (no C); run `make testscripts` after merge. No processes left running (scratch
runners exit on IDLE-EXIT; test cleanup safekills the rest).
