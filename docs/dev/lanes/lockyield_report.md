# lockyield report

scripts/boxlock now makes a non-queue `run` yield to the box queue.

- Ready test: a pending job counts when its `.state/KEY.answer` (written by the runner each pass) starts `ready` or `waiting on`, and a runner is live (flock probe on `.runner.lock`). Not-ready, unasked, or no live runner: no block.
- Runner exemption: label starting `queue:` (what boxqueue already passes). No change to boxqueue, so the running runner is unaffected and there is no landing-order hazard.
- One `YIELDING to queue job NAME` line (reminder every 5 min); WAIT/--wait/--no-wait bound it (exit 75 `REFUSED ... yielding to`). A waiting step proceeds once no ready job is pending.
- `PCREC_BOXLOCK_JUMP=1`: acquires, one audit line to `<lock dir>/.box.lock.audit` (epoch, time, pid, label, cwd, jumped jobs).
- Limit: the answer is up to one runner pass (60 s) stale, so a job added a moment ago is not yet seen.
- Tests: scripts/tests/boxlock.test, 27 pass (10 new incl. a planted no-yield). `bash -n` clean. Docs: scripts/CLAUDE.md, BOILERPLATE.
