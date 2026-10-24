# qwstart report: queuewatch reports JOB-START once per real run

Change (scripts/queuewatch `start_runs` + `lifecycle`): boxqueue logs `== job N START` BEFORE it knows whether the
lock is free (start_job creates running/N, logs START, then waits on the lock). Decision signal, argued:
- A START followed by that job's `  job N waiting on ...; stays pending` (or `CHANGED in pending/`) line, or by another
  START, is an abandoned attempt: never reported (REAL=0).
- running/N existing is NOT trustworthy (it exists during the failed lock wait). `running/N/started` is (written by
  `_start` once the lock is held), so the newest START with nothing after it is held until that file exists or an END
  follows.
- Run indexing: k-th reported START pairs with k-th job_dirs entry, END indexing unchanged; same REAL rule as qwseed.
No state-format change: IDs are the same `S|<line>`; old state files read unchanged (unreported abandoned STARTs are simply never emitted).

Tests (scripts/tests/queuewatch.test, scratch queue/lock only): new wait case (real runner, scratch lock held 7 s, 3 waits
logged): one JOB-START, 8 STAGE-ENDs, one JOB-DONE; PLANT old rule goes red. hist/quiet hand-built running dirs now carry
`started`; oldseed plant re-anchored. Results: queuewatch.test 23/0, queuewatch_ci 5/0, monitor_preflight 7/0, watchrun 21/0.

STATE AT HANDOFF: committed on lane/qwstart; validation COMPLETE; rulings file empty (no entries applied). Not run against the live queue.
