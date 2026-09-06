# LANE BOILERPLATE — read this FIRST, follow all of it

Standing rules for every pcrec subagent lane. Your brief names your task,
model tier, and deliverable; everything below applies without restatement.
(Ruled by Frank 2026-09-06 to cut brief size and lane startup cost.)

## Scope mandate
Touch ONLY /Users/fdicostanzo/pcrec, and inside it ONLY your own worktree
under worktrees/ (read-only elsewhere in the repo). NEVER write to
/Users/fdicostanzo/pcrec-bench (read-only reference at most), no other
directories, no system config. Session-temporary files go in the session
scratchpad directory named in your environment, never committed. Subagents
you spawn inherit this mandate — restate it in their briefs.
Disclosure: you inherit the session-root CLAUDE.md and the manager's memory
index at spawn; treat them as context, not tasking.

## Worktree setup (writers)
1. `git -C /Users/fdicostanzo/pcrec worktree add worktrees/<lane> -b lane/<lane>`
2. cd there; FIRST command: `git rev-parse --show-toplevel` — no edit until
   it prints your worktree path.
3. Build: `make -j4 CC=gcc-16`.
Read-only critics work in the main tree and never run make.

## Box facts (Mac M1, darwin)
bare `timeout` IS GNU; sed is BSD (GNU-only BRE constructs \b \| SILENTLY
NO-OP — spell portable or use -E); local libpcre2 is 10.48-Homebrew, NOT the
reference; the 10.46 reference oracle is `ssh duxevents@192.168.1.100` —
LIGHT probes only (small compiles, transcripts archived), never suite runs
(the bench owns that box); PC-3 red locally is U13-expected; known darwin
reds are listed in docs/dev/wake.md-era notes — A/B against a scratch build
of your branch point before claiming a red as yours or pre-existing.

## Process rules (each has cost a lane before)
- COMMIT INCREMENTALLY (WIP commits) — commit age is your liveness signal.
- Long validation (>~2 min) runs in a BACKGROUND task writing a log; poll
  the log TAIL and proceed the moment the completion line appears. Never a
  blocking foreground call; never a Monitor on a progress log.
- `timeout` (sized generously) on every command of uncertain length; a
  firing timeout is a FINDING.
- Kill only by `scripts/safekill PID`; wrap hang/allocation risks in
  `scripts/watchdog -s WALL -m RSS_KB -c CPU -S label -- cmd`.
- ONE heavy suite at a time on this box; coordinate via the manager.
- Before writing/altering any CHECK: docs/dev/learnings.md §3.
- D26: never gold-plate diagnostic wording. D80: caller-observable changes
  carry their docs/spec/ hunk in the same change. D76/D94: emitted-
  scaffolding changes ARE an abi bump + identity re-pin, readers found BY
  GREP. Update the owning directory's CLAUDE.md for file adds/removes/role
  changes. Oracle-verify test expectations.
- Mech/sabotage: check the highest existing S-id ON MAIN before numbering;
  anchors are copied from `git show HEAD:<path>`; a re-anchor needs its
  intent re-verified.

## Lifecycle (Frank's ruling 2026-09-06 — replaces all keepalive guidance)
- NO self-keepalive crons. Subagent caches are 5-minute TTL; periodic ticks
  buy nothing and pay a full context rewrite each time.
- Work continuously to your deliverable. When blocked on a ruling, send the
  question and KEEP WORKING on whatever does not depend on it if anything;
  otherwise say you are stopping and why.
- WHEN DONE: commit everything, write your report (docs/dev/lanes/
  <lane>_report.md, committed), send the manager a handback message whose
  text is complete on its own (validation numbers inline, log paths), and
  END. Do not idle waiting for review. If a follow-up round is plausible,
  the summary in your report is what a fresh agent resumes from — write it
  so that works.
- A handback message names its validation COMPLETE or says what is owed —
  never leave the manager to infer which.

## Delivery bar
Branch lane/<lane>, committed, report committed, targeted validation run
with numbers in the handback. The full battery is the manager's at merge.
Never merge to main yourself.
