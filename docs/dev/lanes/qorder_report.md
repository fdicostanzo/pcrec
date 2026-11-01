# qorder report: queue ordering by run length, whole-tree cap kill, window `not_before`, missed-window notice

Lane qorder (sonnet), 2026-11-01, branch lane/qorder, from main 6ab3c1522. Owner GO 2026-11-01 ("order by unsharded run length";
"if there are waiting jobs and the box is free then let the next job run"). Rows [QORDER] and [QUEUE-CAPKILL] are STATE:started
(moved to Active). Scope kept: only this worktree and `$PCREC_TMPDIR/scratch/qorder/`; the live queue was never touched (no
`boxqueue add` into any queue, every test ran in a scratch queue with a sacrificial box lock); no suites.

## Per item

### 1. Order (scripts/boxqueue)
- **Changed.** Two new optional dry-run directives: `boxqueue: est SECONDS` (expected run) and `boxqueue: run-total SECONDS` (the
  UNSHARDED total of the run this job is a shard of). A job's length is run-total, else est, else its cap (cap none = last). The next
  job started among the READY ones is picked by a DECLARED first-match table `ORDER_ROWS` (not an if-chain), each row giving a tier and a
  sort key; ties fall back to C-locale name order:

  | row | holds when | sorts by |
  |---|---|---|
  | reservation | imported bench window (name `*-bench-*` with a `.bench` params file) | PRIO |
  | override | PRIO below 100 (`BOXQUEUE_OVERRIDE_BELOW`) | PRIO |
  | starved | ready and passed over >= 14400 s (`BOXQUEUE_STARVE_AFTER`) | longest wait first |
  | length | everything else | length, then name |

  **How a name prefix and the estimate compose (decided):** an ordinary PRIO (100 and up, every PRIO in use) no longer orders the
  queue; it is only the tie-break. The explicit override is the band below 100 (nobody uses it today). Bench windows are a
  reservation: they start as soon as ready, ahead of any shorter job (a promise of start time), ordered among themselves by prio.
  **Starvation bound:** 14400 s of being ready and passed over; an UNMEASURED default (about one long job; the soft limit per job is 1 h,
  the longest honest jobs run 4 h). Ready time = the runner's first ready answer (`.state/KEY.ready`, cleared by any not-ready answer).
  **Shard sets:** each shard declares the same `run-total`; summing pending members was rejected (no set identity; the remaining work
  shrinks as shards finish, so the last shards would jump the queue, the opposite of the ask). `est` past the cap and `run-total`
  below `est` are refused at add. Cross-session: one table for every owner. Other visible changes: queue.log has one `ORDER` line per
  pass, `status` says which job goes first and by which row for a ready job that waits, `plan` prints `start order among the ready`.
  The runner's pass sleep is cut to the nearest declared not-before (`gate_wait`), so a gate opens on time and a free box is not left idle
  for up to a pass pace (owner: "box is free then let the next job run").
- **Tests (scripts/tests/boxqueue.test section 29).** a) shortest first across owners (kit 60 s, lane est 120 s, main 3000 s against
  PRIO order 100,200,300); b) est beats cap, equal caps fall back to name order; c) two 100 s shards of a 5000 s run wait behind a
  1000 s job; d) override (PRIO 050); e) reservation (bench window ahead of a 10 s job); f) starved (ready 20000 s) and its negative
  (14000 s); g) a gated short job does not block a ready long one; h) validation at add (5 refusals, 1 accepted pair); i) plan line
  and status wording.
- **Proof it can fail.** Six plants against scratch copies, each makes its case go red: `byname` (length row sorts by PRIO: order comes
  out `lng shrt mid`), `noest`, `nototal`, `nooverride`, `noreserv`, `nostarve` (each prints the wrong order).

### 2. [QUEUE-CAPKILL] (scripts/boxqueue, scripts/boxlock)
- **Changed.** `timeout --kill-after=60` around the job is gone. The runner's own watcher (the POPULATION-OVER subshell) enforces the
  cap: it writes `running/NAME/capfired`, runs `scripts/safekill --grace 30` on the job pid (kills the process group AND the ppid tree:
  TERM, grace, KILL), then safekills every other process still holding the box-lock file open (new `boxlock holders`) that is not
  the runner's `_start` chain, then KILLs the job pid/group if anything survived. The watcher is not killed before it finishes (the
  main flow waits for it when the marker exists). The end reads `CAP-FIRED`; `capkill.log` stays in the run dir; queue.log gets a
  `CAP-KILL` line naming any holder that could not be removed. The old 124/137 -> CAP-FIRED mapping is gone (a job exiting 124 on
  its own is just `rc=124`).
- **Test (section 30).** The job spawns A (same group, ignores TERM, closed the lock fd: only the group/tree kill reaches it) and B (new
  session, double-forked, ignores TERM, holds the lock fd: only the lock-holder sweep reaches it); cap 2 s, grace 2 s. Asserts: failed
  `CAP-FIRED (2s)`; the job, A and B all dead; `boxlock holders` empty; 10 s wall; the next job runs green at once.
- **Proof.** Four plants: `nosweep` (B survives and holds the lock), `termonly` (the old shape, TERM to the job pid only: A survives),
  `nomarker` (the end reads `rc=143`, not CAP-FIRED), `watcherkilled` (the watcher is killed once the job pid is gone: B survives).
  `boxlock.test` gained a `holders` case and its plant. The first full run also caught a plant-harness gap: the scratch copies
  lacked `safekill`, so a cap never killed and the job outlived its test; the copies now include it and the cap kill falls back to
  KILL of the group when safekill is missing or fails.
- **Not done.** Sweeping lock holders after a NORMAL job end (no measured need; a job that leaves a detached lock holder is its own bug).

### 3. `.window` `not_before=`
- **Changed.** `win_parse` accepts `not_before=T` (strict local ISO-8601, ONE function `nb_epoch` shared with the job directive);
  `bench_one` carries it into the params file; `scripts/boxqueue_window` prints `boxqueue: not-before T` in its dry run, so the
  imported job is held by the queue's own time gate: queued at once, `QUEUED` state, `not-ready: not before T` in status/plan, no
  hand-made sleeper. A malformed value is rejected at import like any bad key (5 shapes tested).
- **Test (section 31).** A window with `not_before` +7 s: imported and QUEUED, params carry the key, status shows it, its `--ready` path
  is not asked; after T it runs RUNNING -> DONE green and its START is at or after T.
- **Proof.** Plants `nbnoparse` (strict parse dropped: the garbage value is not rejected by the window parser) and `nbnocarry` (key not
  copied to the job: the window starts a minute early, green before its time).

### 4. Missed-window notice (scripts/queuewatch, SKILL.md row 10)
- **Changed.** queuewatch raises ONE line `WINDOW-MISSED 7NN-bench-W owner=bench start=T passed Ns ago (grace 900s): the window never
  started and bench has no job pending or running` when a window DECLARED with `not_before=` (read from `.bench/KEY.params`) has its start
  pass by `--missed-window-sec` (900 s, UNMEASURED), the job never STARTED (no run dir with `started`), the owner did not cancel it
  (reservation `DONE cancelled`), and no job of its owner is pending or running. Once per window (episode id = window + start).
- **What the monitor does with it.** The standing monitor's table row 10 (`PENDING-STUCK`, `DISK-HIGH`) is "do nothing, send
  `PROBLEM <the line>`"; I added `WINDOW-MISSED` to that row (one word and a gloss), so it is relayed as a PROBLEM line. Until the
  standing haiku session re-reads SKILL.md (Frank `/clear`s it), an unlisted line has no row: it must be restarted to relay it.
- **Limit (honest).** The notice sees only DECLARED windows. 2026-10-31's W1 was never declared (a planned message), so nothing in the
  queue could have noticed it. What changes is that `not_before=` lets the bench declare a window days ahead; the notice then covers a
  declared window that is rejected late, failed before starting, or withdrawn without the owner's cancel while the box idles. A window
  that is pending but blocked behind a long running job is not "missed" (PENDING-STUCK only fires when nothing runs).
- **Test (queuewatch.test section 4).** Fires with the exact line; once only (relaunch silent); silent inside the grace; silent with a
  pending or running owner job; a foreign owner's job does not hide it; silent if the window ran, was cancelled, or has no `not_before`.
- **Proof.** Four plants (`nograce`, `noowner`, `nostarted`, `nocancel`): each guard removed, the silent case fires.

### 5. Contract and docs
- `boxqueue -h` (header: est, run-total, START ORDER table, THE CAP, window `not_before`), scripts/CLAUDE.md (one clause; at its 4 KB
  limit), scripts/NOTES.md, docs/design/plan_row_bodies/BOXQUEUE.md ("Built (lane qorder)" with the table and the rejected
  alternative), scripts/tests/CLAUDE.md (check count), docs/dev/lanes/BOILERPLATE.md (the "give the shorter run the earlier prio"
  advice replaced by est/run-total guidance and the queue template's `est` line), SKILL.md row 10.
- Bench inbox entry DRAFTED, not written: docs/dev/lanes/qorder_bench_inbox_draft.md (revises [B146]: `not_before=`, the order rule and
  the reservation exemption, WINDOW-MISSED, the cap kill including the lock-fd consequence).

## Validation (all in scratch queues, all on the branch)
- `scripts/tests/boxqueue.test`: 174 passed, 0 failed (full run, 6 min; 144 cases before, 30 new).
- `scripts/tests/queuewatch.test`: 67 passed, 0 failed (54 before, 13 new: 9 cases + 4 plants; the first run exposed a test
  artifact, the RUNNER-DEAD episode firing before the window event in a runner-less scratch queue, fixed by marking it seen).
- `scripts/tests/boxlock.test`: 37 passed, 0 failed; `scripts/tests/queuemon.test`: 45 passed, 0 failed.
- `scripts/plan_lint.sh`: 0 violations. Pre-commit staged checks passed (claude.md size, plan lint).
- Not run: `monitor_rehearsal` (a human-paced end-to-end rehearsal of the monitor session; no change to any line it compares) and
  `queuewatch_ci.test`, `chainrun.test` (untouched code).

## DEPLOY (the manager, in an idle gap)
The runner re-execs itself between jobs when its script changed (`reexec_if_changed`; one `== runner RE-EXEC` line), so the merge
IS the switch; the care is in the timing and the order of announcements.
1. **Choose the gap.** `scripts/boxqueue status`: no job running, no timing-sensitive job (`idle-ok`, `-slot`/`-window`/`-parity`, a
   bench window) running or ready next, and not Frank's box time. The re-exec itself is instant and never mid-job; the point is that the
   NEXT pick is made by the new table, so a queued timing job may start later than by name order.
2. **Merge alone** (`git merge lane/qorder`, read the result; `make strict` is unaffected: no C touched). git replaces files by rename,
   so a running bash keeps its old inode.
3. **Verify the switch.** Within one pass (<= 60 s; `queue.log` tail): `== runner RE-EXEC at pass N: ... sha A -> B`, then the next pass
   shows `pass N ORDER (k ready): ...` lines. If a job is running at the merge, the re-exec waits for its end; until then do NOT let
   anyone declare `est`/`run-total` or a window `not_before=` (the old runner logs `SKIPPED: cannot become runnable under this
   runner` for an unknown declaration, the [runnerfix] miss). BOILERPLATE.md is part of the merge, so announce the new directives to lanes
   only after RE-EXEC shows.
4. **Look at the first ORDER lines against the pending set.** Today's pending (779-781 kit, 790-797 rulepilot) are ordered by CAP once
   the new table is live. To keep the six pilot shards behind shorter work as one 3.6-4.2 h run, re-add them declaring
   `boxqueue: run-total SECONDS` (`boxqueue retry`/re-add while pending only changes the declaration; their not-before gates stay).
5. **The monitor.** queuewatch is relaunched by the standing monitor after every event, so it picks up WINDOW-MISSED by itself; SKILL.md
   row 10 needs Frank's `/clear` of the standing haiku session to be read.
6. **Send the bench inbox entry** (the draft) as a single-file `[inbox]` commit after step 3 shows RE-EXEC; a `.window` with `not_before=`
   sent earlier is rejected by the old runner as `unknown key`.
7. **ROLLBACK:** `git revert` the merge; the runner re-execs the old script at the next idle pass. No queue state migrates: the new
   `.state/KEY.ready` and `running/NAME/capfired` files are ignored by the old code.

## STATE AT HANDOFF
- STATE: delivered on lane/qorder, committed; NOT merged, NOT deployed. Last rulings entry applied: none (qorder_rulings.md said
  "(none yet)" at the last poll, before this report).
- OWED: none. Nothing is running or armed from this lane; scratch queues were all removed by the tests' own cleanup (scratch under
  `/var/tmp/pcrec-pcrec/scratch/qorder/`, the manager may delete it).
- Unmeasured defaults to tune from the first miss: OVERRIDE_BELOW 100, STARVE_AFTER 14400 s, CAP_GRACE 30 s, `--missed-window-sec` 900.
- Known limits, stated above: WINDOW-MISSED sees only declared windows; shards without a declared `run-total` sort individually by
  their own cap; the effective (size-scaled) cap is not used for ordering, only the declared one.
- The live queue (worktrees/.boxqueue/) was never written; its directory listings (job names only, to see which PRIO numbers are in
  use: 120-800, none under 100) were read once. Its runner and queue.log were not touched.
