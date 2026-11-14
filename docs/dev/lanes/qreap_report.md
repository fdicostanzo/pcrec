# qreap — boxqueue cleans up jobs whose prerequisite failed (2026-11-13, lane qreap, sonnet)

Go: Frank 2026-11-13 ("can we add a detection of these unrunnable items and a cleanup?").

## STATE AT HANDOFF

- Built and committed on lane/qreap; validation COMPLETE. `scripts/tests/boxqueue.test`: the full run (180 pass) had one FAIL, a
  test-script bug in my new retry case (stage a did not write a.out), fixed; the rerun of sections 1-18b (through all qreap cases)
  is 58 passed, 0 failed. The tail (cases 19+) is unchanged by this lane and was green in the first full run.
- The live queue (worktrees/.boxqueue) was never touched; every case runs in a scratch queue.

## CHANGES

- `scripts/boxqueue` `cmd_after`: a prerequisite that ENDED failed longer ago than `PREREQ_GRACE` (`BOXQUEUE_PREREQ_GRACE`, 1800 s,
  unmeasured, commented as the owner's `boxqueue retry` window) now answers 77 with `prerequisite-failed:KEY`; the runner's existing
  `--ready` 77 path ends the pending job as cancelled through `end_pending`, so it lands in done/ like any cancel and cascades (the
  next job sees a cancelled one, which already answered 77). Inside the window the answer is 75 as before, now naming the seconds left.
  Header contract updated. A cancelled prerequisite was already cleaned at once (77); unchanged.
- queuewatch/queuemon need no change: an ended-without-running cancel is already `CANCELLED NAME (never ran) :: why`, one line per job,
  INFO for the owner; PENDING-STUCK stops because the job leaves pending/.
- Self-test case 18b in `scripts/tests/boxqueue.test`: fresh failed head keeps the chain; past the window head + 2-job chain all
  cleaned with the reason; retry inside the window keeps the chain; cancelled prerequisite cleans dependent; green and pending
  prerequisites leave the dependent alone (a RUNNING one takes the same branch as pending; not separately exercised).
- Scope: applies to jobs whose `--ready` uses `boxqueue after` (all `batch` jobs and hand-written dependents), not to arbitrary custom `--ready` logic.
