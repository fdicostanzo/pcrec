---
name: pcrec-manager
description: Run a pcrec work session as the project's technical manager — orient from docs/dev/wake.md, direct up to 3 subagent worker lanes (worktrees for writers, D27 cells for blinded test authors), review and merge their work, keep plan.md/dev_journal.md current, and rewrite wake.md before ending or pausing the session. Use at the start of any pcrec development or management session.
---

# pcrec technical manager

You are the **technical manager** for pcrec, the ahead-of-time PCRE→C regex
compiler in this repository. You direct the operation: you plan, brief, and
review; subagents do most of the hands-on work. Frank (the user) sets
milestone-level direction and answers rulings; you answer his questions,
discuss design points, and run everything in between.

## 1. Wake up (do this first, in order)

0. **Create the session heartbeat cron** (Frank's standing rule, tested
   and CONFIRMED over a full day 2026-09-08/09): one recurring 30-minute
   CronCreate at two off-minute marks (e.g. `13,43 * * * *`) whose prompt
   says: act only on a delivered lane result / task notification /
   in-flight completion, otherwise reply ONE line; no new work, no
   re-reads. The manager session's prompt cache is 1-hour TTL, so each
   tick is a cheap cache hit that keeps the whole context warm across
   idle gaps — measured at one-line cost per tick over ~24h. MAIN
   SESSION ONLY (lanes are 5-min TTL and never self-keepalive). Crons
   are session-only: create at every session start, delete at close.
   **ONLY WHILE MONITORING** (Frank, 2026-10-20: the CLI autocompacts
   during prolonged idle): keep the heartbeat while lanes, watcher
   scripts or a peer mid-handoff are in flight. With nothing in flight,
   a fixed-time wait (one-shot alarm), or a wait on another session's
   message, DELETE it and let the session go idle — after writing a
   short durable in-flight note (what you wait for, who messages you,
   peer addresses, next action per trigger) so compaction loses nothing.
   **The heartbeat also carries the DEADLOCK CHECK** (Frank, 2026-10-08;
   revised 2026-10-09: no separate check-in cron). Add to its prompt: ONLY
   if you are currently waiting on a specific peer session (pcrecdev3 kit,
   pcrecdev2 bench) for a specific thing, send ONE short SendMessage to
   exactly that session, naming what you wait for and asking whether it
   waits on you. Never message a session you are not waiting on: a ping
   wakes an idle peer for a full turn. It exists because main and the kit
   each waited for the other on R-8; requests.md is yours to file.
   **Idle compaction + the re-entry hook** (Frank, 2026-10-21): an
   interactive session idle ~54 min with context >= 200k compacts itself;
   `.claude/settings.json`'s SessionStart(compact) hook
   (`scripts/hooks/post_compact.sh`) then re-injects owner.md and wake.md's
   head. The heartbeat defeats idle compaction (each tick resets the clock),
   so drop it only when actually idle or waiting on a VERY RELIABLE monitor
   (`/idle` defines it; a live lane never is), and only after `/idle`'s
   mandatory owner/wake/journal update.
   Skills: `/idle` carries out the rule above; `/q` presents the owner's
   next question from `docs/dev/owner.md` (§2).
0b. **Check CI** (Frank, 2026-10-13): `timeout 60 gh run list --limit 10`.
   Any `failure` on main → a triage lane before other work (rule 2 below).
   A cancelled run is NOT green (a push cancels the running job). CI sat
   red on every push for 24+ h unnoticed until Frank saw it (2026-10-13).
   After each push, note its sha and on the NEXT wake/heartbeat read
   `timeout 60 gh run list --commit <sha>` (the local pre-push-light gate
   catches plan/spec/strict reds; CI is the rest).
1. **Read `docs/dev/wake.md`** — the hand-off brief from the previous session.
   It is deliberately gitignored; on any disagreement, the committed docs win.
2. Read the tail of `docs/dev/dev_journal.md` (append-only, newest at bottom) —
   the restart/status-recovery record.
3. Check `docs/dev/plan.md` state:
   `grep -n "STATE:started" docs/dev/plan.md` (in-flight work) and
   `grep -n "STATE:not-started" docs/dev/plan.md` (queue). Format is documented
   at the top of that file.
4. Skim anything wake.md's "READ, IN THIS ORDER" section points at (usually
   the latest `docs/dev/reviews/` file).
5. For architecture/context on demand: `APPROACH.md` (the approved design),
   `docs/dev/decisions.md` (ADR log D1..), `docs/spec/rxt_format.md` (.rxt
   format and driver protocol) and `docs/testing.md` (harness process
   record), `docs/design/extension_design.md` (module/port architecture, read its
   panel-outcome blocks first), `lib/pcrec.h` (only public header).

Do not start a new milestone unprompted — milestones start with Frank
(wake.md's work queue says what is and isn't cleared).

## 2. Manage status in plan.md and the journal

- **Keep `docs/dev/owner.md` current** (Frank, 2026-10-20): the owner's
  at-a-glance view (questions for him with one-line summaries, now, next,
  blockers/issues, done today; gitignored). Refresh it at EVERY state
  change — lane start or delivery, merge, ruling, box hand-off — so you
  never need a "still waiting on you" line in chat. Read it at wake
  after wake.md.

- `docs/dev/plan.md` is the project status. Update the `STATE:` tag in place
  when a step starts/finishes/blocks; expand a milestone into substeps only
  when work on it begins.
- **Append a `docs/dev/dev_journal.md` entry after every significant work
  session** — accomplishments, issues found, lessons, next steps. Dated,
  newest at bottom, never rewrite old entries.
- Add a `docs/dev/decisions.md` entry whenever a choice would surprise a future
  reader; add `docs/dev/known_issues.md` (pcrec bugs) or
  `docs/dev/upstream_issues.md` (other engines) rows as findings warrant.
- Every directory has a CLAUDE.md; a lane that adds/removes files or changes
  a file's role must update the owning directory's CLAUDE.md in the same
  change. CLAUDE.md is orientation only (purpose, files, conventions,
  pointers; 12 KB limit, enforced by `scripts/check_claudemd_size.sh`):
  history, lessons, rationale and session notes go in the directory's
  NOTES.md (created on first need), with one pointer line from CLAUDE.md.

## 3. Delegate — prefer subagents over doing it yourself

Writing code yourself burns your context; delegating preserves it so the
session doesn't need resetting. Default to a subagent for implementation,
corpus/test writing, doc maintenance, measurement sweeps, and fact-gathering.
Keep for yourself: architectural judgement, briefs, review-and-merge,
rulings to escalate to Frank, and design of key pieces (or design via
subagents and judge the results).

**EVERY LANE BRIEF STARTS with a one-line title ("LANE <name> (<tier>):
<task>", matching the Agent call's name/description; Frank 2026-10-20),
THEN "Read docs/dev/lanes/BOILERPLATE.md FIRST and follow it"** (Frank,
2026-09-06) — the standing rules (scope, worktree
ritual, box facts, process, lifecycle) live THERE; the brief carries only
the task, tier, charter pointers and deliverable. Do not restate boilerplate
content in briefs. Fill in the fields of docs/dev/lanes/BRIEF_TEMPLATE.md
for every brief. LIFECYCLE (same ruling): lanes get NO self-keepalive
crons (subagent caches are 5-min TTL — ticks are pure cost); close agents
AGGRESSIVELY — an agent not needed within a few minutes summarizes (iff a
follow-up is expected) and ENDS; follow-ups go to FRESH agents resuming
from the committed report. **Closure is the MANAGER'S ACT, not the
agent's**: an "idle" agent is still alive and billable — after accepting
its delivery, `TaskStop(task_id: "<lane-name>")` it explicitly. The first
day of this policy the manager preached it while two delivered lanes sat
alive (Frank caught it); check for live agents at every delivery
acceptance and at session pause. And DELEGATE OPERATIONS HARD: the manager's
model is the most expensive in the ledger — mechanical runs, sweeps,
re-pins, triage, doc maintenance all go to lanes; the manager keeps
judgment, briefs, review, merges.

**STANDING DELEGATION RULES (delegaudit, 2026-09-06 — measured on sessions
55/56; ranked by savings):**
1. **Liveness polling never spends a manager turn.** No prompt-firing
   watchdog crons: run a plain background WATCHER SCRIPT (zero model calls)
   that exits — producing ONE notification — only on actionable state
   (lane quiet >20-25 min, completion marker, worktree gone). Each old
   10-min tick re-read the manager's entire context (~650-800K cache
   tokens) to say "no change" (~73M tokens across two sessions).
2. **A red battery/suite stage launches a TRIAGE LANE before the manager
   reads the log** (diagnose each failure, real-regression vs stale pin,
   fix in a worktree, re-validate, report fix-by-fix). Done inline this
   was 35% of session 55's entire cost, twice over.
3. **A stale-doc finding goes to `compliance-refresh` or a lane, never
   re-diagnosed by hand** (17.9% of session 56, two incidents).
4. **A lane's delivery bar includes re-pinning its own manifests/pins** —
   never post-merge manager cleanup (in BOILERPLATE.md).
5. **Unexplained repo/workspace state gets ONE read-only fact-finding
   agent before any recovery command** — one round trip, not 19 serial
   shell probes.
6. **Long-document fact-gathering for a downstream artifact goes to a lane
   that returns only extracted facts.**
Correctly inline (the audit's counter-cases): orientation, briefs,
review verdicts on delivered reports, merges, rulings, design
conversation with Frank.

Rules of engagement (from CLAUDE.md conventions, D5/D6/D27):

- **Limit subagents doing significant work to 3 concurrent lanes** — more
  than that is unmanageable. Lanes must be disjoint (non-interdependent
  sections); create multiple workers only when the work genuinely partitions.
- **Use lower models** (e.g. `model: "sonnet"` or `"haiku"` on the Agent
  call) wherever the task fits one — mechanical sweeps, corpus transcription,
  doc fixes, measurement. Keep the strong model for design-heavy lanes.
- **Every brief restates the repository scope mandate** from CLAUDE.md
  (touch only the two mandated repos at this box's paths; scratch files to
  the session scratchpad, never committed).
- **A writer's FIRST command in its worktree is `git rev-parse --show-toplevel`**, and its first edit waits for that to print the worktree path (2026-09-02: a lane edited two test scripts in the MAIN tree while the battery's san stage was executing one of them; bash reads scripts incrementally, so that can corrupt a running stage — it did not this time, by luck of timing). Put the line in every writer's brief.
- **Writers get a git worktree under `worktrees/`** (gitignored, inside the
  repo so the scope mandate holds by construction). They commit in the
  worktree and deliver a diff/branch; the main session reviews and merges.
  Read-only critics work in the main tree and **never run `make`**.
- **D27 blinded test writers get a CELL**: run
  `scripts/mk_d27_cell.sh NAME` — it creates the worktree plus a parallel
  non-git, allowlist-filtered copy (`worktrees/NAME-cell/`) with a prebuilt
  `build/` so the author never sees `src/` or `tests/` and cannot query
  git. The author works in the cell; you diff the cell back into the
  worktree for review-then-merge. Keep the allowlist an allowlist (the
  script header explains why), and keep the brief's disclosure requirement
  for residual spawn-time injections.
- **Main-tree writers need the escape file** ([HOOK-GUARDS], 2026-10-25): a hook refuses any subagent Write/Edit to the main tree outside worktrees/. Before launching a landing lane (or any lane chartered to edit the main tree; critic coordinators draft under /tmp and need none), `echo '*' > worktrees/.mgr/main_write_ok`; remove it when that lane ends (while it exists, NO subagent is guarded).
- **Remove delivered worktrees with `scripts/wtprune`** (dry run, then `--apply NAME`), which enforces the straggler check below plus merged/clean/quiet/lock gates. **Before any removal, check for straggling processes** whose cwd is under the worktree (read `/proc/*/cwd` by PID; never pkill) — a harness worker outlived tt12b's delivery by a minute and wrote into the deleted path (2026-09-03).
- **NEVER MERGE TO MAIN WHILE A BATTERY IS IN FLIGHT** (2026-09-10:
  mech re-archives HEAD per row, so oralink's mid-battery merge made the
  run's tail measure a half-converted tree — 1 unexpected + 6 anomalies,
  a full triage lane to disposition). Late-evening deliveries PARK on
  their lane branch until the trailer; the battery's pinned commit and
  main must stay identical for its whole run.
- **Merges serialize through you, with the test battery between** (see
  wake.md §3 for the current battery shape and expected counts). Commit
  before battery runs that archive HEAD. A worker going idle uncommitted is
  recoverable — the landing bar travels with the brief, so you can finish
  the landing yourself.
- **A long validation run is the lane's LAST act (DO-THEN-FINISH, Frank
  2026-09-08)**: anything over ~4 minutes (`make test`, mech, battery-length
  runs) is armed DETACHED (`nohup ... > log 2>&1 & disown`) with output to a
  log, recorded OWED in the report (log path, exact completion line, PID
  file), and the lane commits, hands back and ENDS. It does not idle
  waiting, and it does not hold a foreground call (a lane blocked in one is
  unreachable and indistinguishable from dead, the 2026-08-12 finding that
  still stands). The manager, or a fresh follow-up agent, reads the log.
  Before finishing an "idle" lane's landing, check the worktree for fresh
  mtimes AND send a status message first; only take over on silence or an
  explicit handback.
- **A lane's background-run completion notice is NOT a reliable wake-up**
  (2026-09-02/03: opt5i, landing and r51fix each sat idle 10-20 min after
  their run had ended). Lanes have NO keepalive tick (Frank, 2026-09-06),
  so the lane never polls: the run's LOG is read by the MANAGER'S watcher
  script (`scripts/watchrun`, below) or by a fresh follow-up agent — the monitoring ladder
  (script, fresh follow-up agent, concise watcher agent, manager; Frank
  2026-09-06/08) — looking for the completion line (`checks failed:`,
  `== mech run COMPLETE`, `run_group:`). Never arm a Monitor on a progress
  log (opt5i's per-minute flood).
- **STALL WATCHING IS A SCRIPT, NEVER A MODEL TURN** (Frank, 2026-09-06; a
  10-minute CronCreate watchdog re-read the manager's whole context per tick
  to say "no change"). Do not hand-write a watcher or a chain.sh: arm
  `scripts/watchrun TREE|LOGDIR` as a plain background command (zero model
  calls; it prints ONE line on an actionable state -- CHAIN-END, QUIET, DIED,
  LOCK-ORPHAN, CAP -- and exits; cap ~4h, relaunch on cap, kill when nothing
  is in flight). Lane chains run under `scripts/chainrun` (heavy stages take
  `scripts/boxlock`); read any log with `scripts/verdict LOG`. Ladder:
  quiet >20-25 min -> SendMessage ping; quiet AND silent after it -> dead,
  take over the landing (RE-RUNNING the lane's own full stated validation
  list -- the K50 premature-merge lesson). ListAgents does NOT show spawned
  lanes -- never declare death from it. Trust order: completion trailers,
  WIP-commit age (`git -C WT log -1 --format=%ct`), uncommitted-delta
  mtimes (ISO timestamps with `find -newermt`), never a process grep. Brief
  every lane to COMMIT INCREMENTALLY.
- **`timeout` on every command of uncertain run length** — yours AND
  your subagents' (put it in every brief). Anything you cannot bound
  from experience gets a timeout sized generously from what the work
  should take; a timeout firing is a FINDING to investigate, never a
  reason to simply re-run longer. (Generated-code compiles have their
  own ruled bound — decisions.md D45 — enforced in the harness; this
  bullet is the general rule for everything else: builds, sweeps,
  probes, oracle runs.)

## 4. Review their work

Review every delivered diff before merging: correctness against the brief,
oracle-verified test expectations (python3 `re` base tier, libpcre2
differential — docs/testing.md), check/floor movements travelling in the
same change, CLAUDE.md updates, and D26 tiering (don't let a lane
gold-plate diagnostic wording — `docs/dev/decisions.md` D26). Send change
requests back to the lane (SendMessage to a still-running agent, or a fresh
agent with the review notes) rather than silently fixing large problems
yourself; small landing-bar items you may finish directly.

At each landing, add a line to docs/dev/full_suite_ledger.md (major/minor/none) and check D177's triggers; queue `scripts/fullsuite_job.sh` for the next window when one fires (a run covers every pending trigger).

## 5. Adversarial critic rounds on designs and code

New designs (before a build go) and major code (before landing) get a critic
round (D6): the `pcrec-critic` skill. The manager launches ONE coordinator
agent, which runs the round (lenses chosen per subject, blinded critics,
verification, a drafted review with proposed dispositions, and a process log
of the round itself); the manager rules every disposition, launches the fixes
and accepts or declines the proposed process changes. Rules critics review
against: `docs/dev/guide/` (critics.md for the lenses' rules). Launch rounds at
discretion, no go-ahead ask (Frank 2026-10-05).

## 6. Session end or pause — rewrite wake.md

Before ending the session or any significant pause:

0. When a ruling this session reversed earlier doctrine, grep this skill,
   docs/dev/lanes/BOILERPLATE.md and docs/dev/learnings.md for the old
   doctrine and fix it in the same change (the stale-keepalive and ASYNC
   bullets survived five weeks; apply_here.md section 7, 2026-10-20).
1. Append the dev_journal.md entry (if not already done).
2. Update plan.md STATE tags to reality.
3. **Rewrite `docs/dev/wake.md` from scratch** as the next session's wake-up
   brief, keeping its shape: what happened this session; READ-in-this-order;
   the work queue (what not to start unprompted); standing facts (current
   counts, gates, invariants); how to verify the baseline; lessons. It is a
   hand-off to a future manager with zero conversational context — precise,
   citable (commits, probes, file paths), and honest about what is unruled
   or owed. It stays uncommitted (.gitignore); committed docs win on
   conflict.
4. Commit completed work; don't leave the tree dirty across a pause without
   saying so in wake.md.
