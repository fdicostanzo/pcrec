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
- DARWIN TIMEOUTS: the `.rxt` corpus section alone runs 20-30 min;
  `make test-axes` is MULTI-HOUR (one full corpus run PER AXIS) — sweep only
  your own axes with `AXES="-fno-…"` rather than the whole table; `make test`
  itself is ≈100 min. Size your `timeout`/watchdog accordingly — a 15-min
  wrapper on a corpus run is a self-inflicted kill, not a finding.

## Process rules (each has cost a lane before)
- COMMIT INCREMENTALLY (WIP commits) — commit age is your liveness signal.
- Long validation (>~2 min) runs in a BACKGROUND task writing a log — never
  a blocking foreground call; never a Monitor on a progress log.
- ARM OWED RUNS DETACHED: a run you launch as a plain background task DIES
  WITH YOUR SHELL the moment the manager closes your session (b1triage's
  did, 2026-09-22) — a chain you are owing past your own end must be
  `nohup … > log 2>&1 & disown`, not a bare `&`.
- DO-THEN-FINISH (Frank 2026-09-08): your context cache lives 5 MINUTES; an
  idle wait longer than that busts it and every later turn re-pays your
  whole context at full price. So: a run ≤~4 min you may poll (log tail)
  and proceed. A run LONGER than that is the LAST thing you launch —
  sequence the work so all heavy-context phases (design, code, review)
  end at a commit + report FIRST; the report marks its validation numbers
  OWED and names the log path + exact completion line; launch the run in
  background and END. The manager's watcher catches completion; a fresh
  agent (or the manager) reads the log and completes the delivery. If a
  long run's results feed your own later work, fill the wait with
  independent items — never idle-wait — or deliver in stages and let a
  fresh agent resume from your report.
- `timeout` (sized generously) on every command of uncertain length; a
  firing timeout is a FINDING.
- Kill only by `scripts/safekill PID`; wrap hang/allocation risks in
  `scripts/watchdog -s WALL -m RSS_KB -c CPU -S label -- cmd`.
- ONE heavy suite at a time on this box; coordinate via the manager.
- If your task WRITES CODE (anything under `src/`, `cli/`, `lib/`): read
  docs/dev/coding_guide.md before your first edit — house disciplines, the
  taught primitives in their current state, emitted-text and anchor-column
  rules, the altitude rubric, the do-nots.
- Before writing/altering any CHECK: docs/dev/learnings.md §3.
- "RE-RAN STANDALONE, CLEAN" MUST NAME THE FILE THE SUITE RUNS. A file you
  edited and re-ran directly can read green while the suite that CHAINS it
  is red — a different file's own coverage-count guard on your edited
  script's output can still be stale (regred_report.md, learnings.md §3.y).
  Name the exact file/command you validated, not just "the check."
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
  buy nothing and pay a full context rewrite each time. (The MAIN session's
  cache is 1-hour TTL — its 30-min heartbeat is legitimate and is not a
  precedent for lanes.)
- Work continuously to your deliverable. When blocked on a ruling, send the
  question and KEEP WORKING on whatever does not depend on it if anything;
  otherwise say you are stopping and why.
- WHEN DONE: commit everything, write your report (docs/dev/lanes/
  <lane>_report.md, committed), send the manager a handback message whose
  text is complete on its own (validation numbers inline, log paths), and
  END. Do not idle waiting for review. If a follow-up round is plausible,
  the summary in your report is what a fresh agent resumes from — write it
  so that works.
  **THE HANDBACK IS A SendMessage TOOL CALL (to "main"), MADE BEFORE YOUR
  FINAL TURN ENDS.** Your final plain-text output is NOT visible to the
  manager — a lane that "reports" in its closing prose and goes idle has
  DELIVERED NOTHING and costs a round-trip ping every time (five lanes in
  one night, 2026-09-12/13). The same applies mid-flight: if you are
  waiting on a background run, SendMessage the interim state rather than
  sitting silent — a quiet lane is indistinguishable from a dead one.
- A handback message names its validation COMPLETE or says what is owed —
  never leave the manager to infer which.

## Delivery bar
Branch lane/<lane>, committed, report committed, targeted validation run
with numbers in the handback. RE-PIN EVERY MANIFEST/COUNT/PIN YOUR CHANGE
MOVES in the same delivery (readers found by grep) — post-merge manager
cleanup of your pins is a delivery failure. The full battery is the manager's at merge.
Never merge to main yourself.

## Travel-month topology (2026-09-07 .. ~10-07)

The Linux box (ubuntubudu, the 10.46 reference oracle) is reachable
ONLY over the tailnet: `duxevents@100.69.121.107` (never 192.168.1.100
— that address only resolves from the home LAN). Light ops only, as
ever; heavy Linux runs go through the manager (pcrecdev2's executor
channel — never run one yourself over ssh, and never assume the box is
free). The Mac session is closed mornings; a lane needing a ruling
mid-morning parks and polls its rulings file.
