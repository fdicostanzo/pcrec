# lockyield report

scripts/boxlock now makes a non-queue `run` yield to the box queue.

- Ready test: a pending job counts when its `.state/KEY.answer` (written by the runner each pass) starts `ready` or `waiting on`, and a runner is live (flock probe on `.runner.lock`). Not-ready, unasked, or no live runner: no block.
- Runner exemption: label starting `queue:` (what boxqueue already passes). No change to boxqueue, so the running runner is unaffected and there is no landing-order hazard.
- One `YIELDING to queue job NAME` line (reminder every 5 min); WAIT/--wait/--no-wait bound it (exit 75 `REFUSED ... yielding to`). A waiting step proceeds once no ready job is pending.
- `PCREC_BOXLOCK_JUMP=1`: acquires, one audit line to `<lock dir>/.box.lock.audit` (epoch, time, pid, label, cwd, jumped jobs).
- Limit: the answer is up to one runner pass (60 s) stale, so a job added a moment ago is not yet seen.
- Tests: scripts/tests/boxlock.test, 27 pass (10 new incl. a planted no-yield). `bash -n` clean. Docs: scripts/CLAUDE.md, BOILERPLATE.

## lockyield2

Reproduced the boxlock.test flake under a bounded busy-loop load (24-32 spinners, 16 threads): 1 in 20 at 24 spinners, 3 in 30 at 32. Two causes, neither in the yield/acquire path:

1. TEST RACE (the original 26/1 shape): `holder` waited for "held" by polling `status` at most 5 s; under load the background holder's bash start-up outran that, so section 2 saw a free lock (five cascading FAILs: holder never took the lock, status, --no-wait, --wait 1, default wait). Fix: the held command drops a marker file as its first act (`: > marker; sleep N`), the test waits on that marker (up to 30 s), and the hold time now starts when the command runs.
2. BOXLOCK SLOWNESS (diagnostic path only): `holders()` (used by `status` for HELD-ORPHAN) forked one `readlink` per /proc fd; with ~1450 fds on this box it took 12 s, over the test's 10 s timeout (rc=124, section 5). Replaced with a single `find /proc -lname`; 0.2 s. It is not on the acquire/yield path.

Real-lane safety: no race found in yield/acquire. A lane cannot slip past a ready job or deadlock because of either cause; the documented 60 s staleness of `.answer` remains the only window. Queue runner's lock acquisition untouched (stop rule not hit).

Verification: 30 plain + 30 under 32-spinner load, all 27/0 (60 of 60 clean).
