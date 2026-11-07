# Monitoring: heartbeat, queue verdicts, lane liveness, idle

Loaded by the pcrec-manager trigger table (and by the kit skill's §1/§3) when
you are about to create or delete the heartbeat, go idle, queue a job, wait on
a run, a lane or a peer, or when a RED arrives. Everything here is a STEP, not
a condition to remember: where a rule depends on state, the state is read from
a file or a script, never recalled.

## 1. The heartbeat cron

Create it at every session start (crons are session-only; delete it at close).
ONE recurring CronCreate at two off-minute marks, `13,43 * * * *` for main
(the kit uses `17,47`). The manager session's prompt cache is 1-hour TTL, so a
tick is a cheap cache hit (measured at one line per tick over ~24 h,
2026-09-08/09). MAIN SESSIONS ONLY: lanes are 5-min TTL and never
self-keepalive.

The PROMPT (verbatim; every step runs every tick, none is conditional on
what you remember):

    HEARTBEAT (OWNER=main). Run these steps in order, then stop:
    0. Run `scripts/gestalt --owner main`; include its 'load' and 'sessions'
       lines in the one-line reply only when something is unusual (load >
       nproc, a session gone, CI red).
    1. `scripts/monread main`: act on each RED/PROBLEM line (a RED -> a
       triage lane, monitoring.md §2); GREEN/INFO lines -> refresh owner.md.
    2. Read docs/dev/owner.md "Waiting on": for every entry older than 60
       min, send that ONE session one line naming the thing and asking its
       status, ending "REPLY: one line, either way". No entry -> no message.
    3. Act on any delivered lane result or task notification.
    4. Otherwise reply ONE line. No new work, no re-reads.

The kit's prompt is the same with OWNER=kit, `scripts/gestalt --owner kit`, `scripts/monread kit`, and its
list in `worktrees/.mgr/waiting_on.kit`.

Why step 2 reads a file: the old wording ("ONLY if you are currently waiting
on a specific peer") asked the session to remember a wait across compactions;
the file survives them (the post-compact hook re-injects owner.md). Keep
"Waiting on" current at every state change, like the rest of owner.md: one
line per wait, `<since HH:MM> <session> <the thing>`. Never message a session
that is not listed there (a ping wakes an idle peer for a full turn; the
R-8 deadlock, 2026-10-08, is why the check exists at all).

KEEP OR DROP (Frank 2026-10-20/21): the heartbeat defeats idle compaction
(each tick resets the ~54-min idle clock). Keep it while anything is in
flight that is NOT watched by a very reliable monitor. Drop it only by the
`/idle` procedure (it writes the durable note first). The test is mechanical:

| state | heartbeat |
|---|---|
| a live lane (lanes go idle without reporting) | KEEP |
| a peer mid-handoff whose details live only in the conversation | KEEP |
| only queue jobs, queuemon alive (`scripts/queuemon status`), owner.md "Waiting on" empty | may drop via /idle (queuemon + monread is the reliable monitor) |
| nothing in flight, or a fixed-time wait (one-shot alarm) | drop via /idle |

## 2. Queue verdicts: ONE path for both managers

Every heavy run is a box-queue job named `PRIO-OWNER-REST` (OWNER `main` or
`kit`; a lane's jobs carry its manager's OWNER). `scripts/boxqueue add` starts
`scripts/queuemon` (idempotent), which applies the pcrec-monitor table and
journals ONE line per event to `worktrees/.mgr/monitor.log` with an OWNER
field. That journal is the only place a verdict reaches you from:

1. At wake and on every heartbeat tick: `scripts/monread OWNER` (prints the
   unread lines, advances the cursor). `scripts/monread` also prints a
   `PROBLEM ... monitor dead/stale` line when a job is queued and queuemon is
   not alive: then `scripts/queuemon start`.
2. While any job of yours is pending or running, keep ONE background
   `scripts/monread OWNER --wait` armed (Bash `run_in_background`). It exits on
   the first new line for OWNER: one notification. Then `scripts/monread
   OWNER`, act, re-arm.
3. A RED: launch a triage lane before reading the log yourself (§3 of the
   skill, delegaudit rule 2). A PROBLEM: decide; the monitor never kills,
   cancels or retries.
4. NEVER write a private watcher (a tail of queue.log, a done/-dir poll, a
   lock-label match) and NEVER run `scripts/queuewatch` by hand: queuemon owns
   it, and a by-hand launch consumes an event (main: 2026-10-29 twice, 11-04,
   11-05; the kit's private watchers failed four times in four days: a
   lock-label match that never fired and a false fire on cancelled jobs,
   11-04; silent on RED 416, 11-05; silent on REDs 485 and 482, 11-07, while
   monread held every line). If monread lacks
   a shape you need, file a row to grow it; do not fork it.
5. For `main` only, the UserPromptSubmit/SessionStart hook
   (`scripts/hooks/monitor_unread.sh`) also shows unread `main` lines. It is a
   backup, not the path: it fires only on a typed prompt.

Chains still run under `scripts/chainrun` are watched with `scripts/watchrun
TREE` (one line on CHAIN-END, QUIET, DIED, LOCK-ORPHAN, CAP, then exits;
relaunch on CAP); read any log's verdict with `scripts/verdict LOG`.

A full-suite run: the `/pcrec-test` skill (it queues the job and names the
monitor); it adds a one-shot alarm at the expected end + 2 h.

## 3. Lane liveness (what the manager watches; lanes never watch)

- A lane's long validation is its LAST act (DO-THEN-FINISH, Frank
  2026-09-08): anything over ~4 min is queued (or armed detached), recorded
  OWED in the report (keys, log path, completion line), and the lane commits,
  hands back and ENDS. It never waits for a notification. A lane that idles
  "waiting for the run" with owed jobs is a brief failure: the brief's OWED
  RUNS field must say END after queueing (BRIEF_TEMPLATE.md).
- A lane's background-run completion notice is NOT a reliable wake-up
  (2026-09-02/03: opt5i, landing and r51fix each sat idle 10-20 min after the
  run ended). The run's verdict is read from the queue (§2) or the log, by
  you or a fresh follow-up agent.
- STALL WATCHING IS A SCRIPT, NEVER A MODEL TURN (Frank, 2026-09-06; a
  10-minute CronCreate watchdog re-read the whole context per tick to say "no
  change"). Arm `scripts/lanewatch --follow NAME` (background) at every lane
  launch; relaunch on CAP. Never arm a Monitor on a progress log.
- Ladder: quiet > 20-25 min -> SendMessage ping; quiet AND silent after it ->
  dead: take over the landing, RE-RUNNING the lane's own full stated
  validation list (the K50 premature-merge lesson). ListAgents does NOT show
  spawned lanes; never declare death from it. Trust order: completion
  trailers, WIP-commit age (`git -C WT log -1 --format=%ct`),
  uncommitted-delta mtimes (`find -newermt`), never a process grep.
- Before finishing an "idle" lane's landing, check the worktree for fresh
  mtimes AND send a status message first; take over only on silence or an
  explicit handback.
- Before TaskStop of a lane: `scripts/boxlock status` for that lane's waiters
  (a stopped lane can leave a boxlock waiter that later takes the box,
  trailgc2-sections 2026-10-29), and confirm any detached run it owns
  survives or has ended (memory pcrec-taskstop-kills-detached-runs).

## 4. CI

After each push note its sha; on the next wake or heartbeat read `timeout 60
gh run list --commit <sha>`. A cancelled run is NOT green (a push cancels the
running job). Any `failure` on main -> a triage lane before other work.
