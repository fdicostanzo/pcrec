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
  change.

## 3. Delegate — prefer subagents over doing it yourself

Writing code yourself burns your context; delegating preserves it so the
session doesn't need resetting. Default to a subagent for implementation,
corpus/test writing, doc maintenance, measurement sweeps, and fact-gathering.
Keep for yourself: architectural judgement, briefs, review-and-merge,
rulings to escalate to Frank, and design of key pieces (or design via
subagents and judge the results).

**EVERY LANE BRIEF STARTS: "Read docs/dev/lanes/BOILERPLATE.md FIRST and
follow it"** (Frank, 2026-09-06) — the standing rules (scope, worktree
ritual, box facts, process, lifecycle) live THERE; the brief carries only
the task, tier, charter pointers and deliverable. Do not restate boilerplate
content in briefs. LIFECYCLE (same ruling): lanes get NO self-keepalive
crons (subagent caches are 5-min TTL — ticks are pure cost); close agents
AGGRESSIVELY — an agent not needed within a few minutes summarizes (iff a
follow-up is expected) and ENDS; follow-ups go to FRESH agents resuming
from the committed report. And DELEGATE OPERATIONS HARD: the manager's
model is the most expensive in the ledger — mechanical runs, sweeps,
re-pins, triage, doc maintenance all go to lanes; the manager keeps
judgment, briefs, review, merges.

Rules of engagement (from CLAUDE.md conventions, D5/D6/D27):

- **Limit subagents doing significant work to 3 concurrent lanes** — more
  than that is unmanageable. Lanes must be disjoint (non-interdependent
  sections); create multiple workers only when the work genuinely partitions.
- **Use lower models** (e.g. `model: "sonnet"` or `"haiku"` on the Agent
  call) wherever the task fits one — mechanical sweeps, corpus transcription,
  doc fixes, measurement. Keep the strong model for design-heavy lanes.
- **Every brief restates the repository scope mandate** from CLAUDE.md
  (touch only /home/duxevents/pcrec; scratch files to the session
  scratchpad, never committed).
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
- **Before `git worktree remove` on a delivered lane, check for straggling processes** whose cwd is under the worktree (read `/proc/*/cwd` by PID; never pkill) — a harness worker outlived tt12b's delivery by a minute and wrote into the deleted path (2026-09-03).
- **Merges serialize through you, with the test battery between** (see
  wake.md §3 for the current battery shape and expected counts). Commit
  before battery runs that archive HEAD. A worker going idle uncommitted is
  recoverable — the landing bar travels with the brief, so you can finish
  the landing yourself.
- **Briefs tell workers to run long validation ASYNCHRONOUSLY** (Frank,
  2026-08-12 fourteenth session): `make test`, mech, and battery-length
  runs go in a background task with output to a log, polled via the
  artifact (log tail; mech's `== mech run COMPLETE` trailer) — never as a
  blocking foreground call. A lane blocked in a foreground run is
  unreachable and indistinguishable from dead (the manager has now made
  BOTH wrong calls: waited on a finished run believed alive, and started
  finishing a live lane's landing believed dead), and mid-wait is where
  every lane death to date has happened. Async keeps the lane responsive
  to messages while the run executes. Before finishing an "idle" lane's
  landing, check the worktree for fresh mtimes AND send a status message
  first; only take over on silence or an explicit handback.
- **A lane's background-run completion notice is NOT a reliable wake-up** (2026-09-02/03: opt5i, landing and r51fix each sat idle 10-20 min after their run had ended, "waiting for the notification"). Brief every lane: the run's LOG is the trigger — at each keepalive tick, check the log's tail for the completion line (`checks failed:`, `== mech run COMPLETE`, `run_group:`) and proceed the moment it is there; never arm a Monitor on a progress log (opt5i's per-minute flood). The manager's watchdog reads the same logs and pings on "run ended, lane silent".
- **STALL WATCHDOG (Frank, 2026-08-15, twenty-first session): whenever
  subagents or async background processes are in flight, set up a
  10-minute cron** (CronCreate) that checks for stalls — lanes or
  background scripts that are dead, stalled, or running longer than
  their work justifies. LIVENESS SIGNALS in order of trust: the lane's
  WIP-commit age (`git log -1 --format=%cr` in its worktree) +
  uncommitted-delta mtimes, background-log tails, process table.
  ListAgents does NOT show spawned lanes even when alive — never
  declare death from it. (`find -newermt` needs ISO timestamps on this
  box; relative strings silently fail.) Stale >20 min with no process →
  SendMessage ping; stale AND silent one tick later → dead, take over
  the landing (the twenty-first session lost a lane for eleven hours
  by "waiting" with no watchdog). Tear the cron down when no lanes or
  background work remain. Brief every lane to COMMIT INCREMENTALLY
  (WIP commits) — the watchdog's best signal, and a death then strands
  minutes, not hours.
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

## 5. Adversarial critic panels on designs and major code

New designs and major code pieces get a **multi-subagent adversarial critic
panel** (D6) before or at close: 2–4 independent read-only critics with
distinct lenses (e.g. checks/tests, engine semantics vs the oracle, docs
staleness), briefed to refute and to measure both sides of every claimed
cell. Compile findings into `docs/dev/reviews/YYYY-MM-DD-rN-<topic>.md` with
triage dispositions, then fix-with-measurement before disposition. Critics
are read-only and never run `make`.

## 6. Session end or pause — rewrite wake.md

Before ending the session or any significant pause:

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
