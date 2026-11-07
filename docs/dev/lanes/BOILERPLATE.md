# LANE BOILERPLATE — read this FIRST, follow all of it

**NEVER write outside your worktree + the pcrec temp root — `/tmp`,
`~/.claude`, `$HOME` and the main tree included. The temp root is
`$PCREC_TMPDIR` (default `/var/tmp/pcrec-$(id -un)`; `make` and the queue
scripts already export `TMPDIR` to it; in a plain shell run
`. scripts/tmpdir.sh`). Your lane scratch is `$PCREC_TMPDIR/scratch/<lane>/`
(`mktemp -p` it; `mkdir -p` it first). `/tmp` is not used (small RAM tmpfs).**

Standing rules for every pcrec subagent lane. Your brief names your task,
model tier, and deliverable; everything below applies without restatement.
(Ruled by Frank 2026-09-06 to cut brief size and lane startup cost.)

## Scope mandate
Touch ONLY the pcrec repo (its path on this box: root CLAUDE.md's MANDATE),
and inside it ONLY your own worktree under worktrees/ (read-only elsewhere
in the repo). NEVER write to the sibling pcrec-bench checkout (read-only
reference at most), no other
directories, no system config. Session-temporary files go in the session
scratch directory `$PCREC_TMPDIR/scratch/<lane>/`, never committed. Subagents
you spawn inherit this mandate — restate it in their briefs.
`/tmp` IS NOT USED (it is a small RAM tmpfs with a per-user quota; a full one
turned a `make test` red, 2026-10-28): no backups, plant copies, logs or `-o` outputs
there, not even briefly (2026-10-10: three lanes in one day). Use your
worktree's `build/` (gitignored) or your scratch dir under the temp root.
Disclosure: you inherit the session-root CLAUDE.md and the manager's memory
index at spawn; treat them as context, not tasking.

## Worktree setup (writers)
1. `git -C "$(git rev-parse --show-toplevel)" worktree add worktrees/<lane> -b lane/<lane>` (run from the main tree)
2. NO `cd` into the worktree (the PreToolUse hook scripts/hooks/no_cd_worktree.sh
   blocks it; it moves the session cwd): every command uses absolute paths or
   `git -C <worktree>`. FIRST command: `git -C <worktree> rev-parse
   --show-toplevel` — no edit until it prints your worktree path.
3. Build: `make -j16` on the Linux dev box (plain `gcc` is GNU gcc 15.2;
   the Mac needs `CC=gcc-16`, see RUNS.md "Box facts").
Read-only critics work in the main tree and never run make.

## Read by trigger (the rest of this file is always on)
| about to… | read first |
|---|---|
| build, run a suite or a sweep, queue a job, take a sabotage id, arm a chain, or work during a timing window | `docs/dev/lanes/RUNS.md` (box facts, the queue and chain templates, the box lock, timing windows, other boxes) |
| write or change C under `src/`, `cli/`, `lib/` | docs/dev/guide/README.md + coding.md |
| write or change a check | docs/dev/learnings.md §3 |
| write a design note | "Design lanes" below |

## Process rules (each has cost a lane before)
- STOP RULE: a lane asked to build (edit `src/`, `cli/`, `lib/` or
  `memfn/src/`) without the owner's build go QUOTED in its brief stops
  and asks the manager; it does design/measure only (BRIEF_TEMPLATE.md).
- RULINGS FILE: if your brief names `<name>_rulings.md` in your worktree,
  re-read it before each commit, before any run over ~2 min, and before
  your report; name the last entry applied in STATE AT HANDOFF. Later
  rulings come there, not by message.
- COMMIT INCREMENTALLY (WIP commits) — commit age is your liveness signal.
- NEVER `git stash` (push or pop): the stash is ONE list shared by every worktree of the repo, so a pop takes another session's entry (langfix2 popped the K113 landing's stash, 2026-10-22). Park work in a WIP commit on your branch instead.
- A HOOK refuses a subagent's Write/Edit to a main-tree path outside worktrees/ (scripts/hooks/lane_writes_in_worktree.sh, [HOOK-GUARDS]); another refuses `git commit -a`/`--all`. Blocked: write in your worktree, commit named paths. A lane the manager chartered to write the main tree (a landing lane) is admitted by `worktrees/.mgr/main_write_ok` (manager-written); never create that file yourself.
- Long validation (>~2 min) runs in a BACKGROUND task writing a log — never
  a blocking foreground call; never a Monitor on a progress log. NOR a
  Monitor/notification on a COMPLETION you then go idle waiting for: an
  idle wait longer than ~4 min is DO-THEN-FINISH's case — commit, report
  the run OWED with its log path, hand back, END (three lanes idled this
  way on 2026-09-28 alone: pf36, land84, findb6).
- DO-THEN-FINISH (Frank 2026-09-08): your context cache lives 5 MINUTES; an
  idle wait longer than that busts it and every later turn re-pays your
  whole context at full price. So: a run ≤~4 min you may poll (log tail)
  and proceed. A run LONGER than that is the LAST thing you launch —
  sequence the work so all heavy-context phases (design, code, review)
  end at a commit + report FIRST; the report marks its validation numbers
  OWED and names the log path + exact completion line; launch the run in
  background and END. The manager's watcher (`scripts/watchrun`) catches
  completion; a fresh agent (or the manager) reads the log and completes
  the delivery. If a
  long run's results feed your own later work, fill the wait with
  independent items — never idle-wait — or deliver in stages and let a
  fresh agent resume from your report.
- NEVER IDLE-WAIT FOR A BOX SLOT, A LONG RUN OR A NOTIFICATION (Frank,
  2026-10-07; lanes still idled "waiting for a notification" with owed jobs on
  2026-11-07). Queue the run (RUNS.md), name its keys OWED in STATE AT HANDOFF,
  run lanecheck, SendMessage the manager, END. A fresh agent reads the verdicts.
  Never hand-write a waiter, a chain.sh or a watcher.
- `timeout` (sized generously) on every command of uncertain length; a
  firing timeout is a FINDING.
- Kill only by `scripts/safekill PID`; wrap hang/allocation risks in
  `scripts/watchdog -s WALL -m RSS_KB -c CPU -S label -- cmd`.
- If your task WRITES CODE (anything under `src/`, `cli/`, `lib/`): read
  docs/dev/guide/README.md and the files it names for your area (coding.md
  at least) before your first code edit — house disciplines, the
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
  changes; CLAUDE.md is orientation only (12 KB limit, 4 KB for docs/, docs/dev/, docs/dev/lanes/, scripts/; pre-commit and
  `make test-claudemd-size` enforce it), so history, lessons and session
  notes go in that directory's NOTES.md (create it on first need). Oracle-verify test expectations.
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

## Before ending: scripts/lanecheck ([LANECHECK])
If your brief has a DELIVER block (`docs/dev/lanes/<name>_deliver.txt`, written BY THE MANAGER
before you start: read it, never create, edit or overwrite it; if it is missing or looks
wrong, say so in the report), run
`scripts/lanecheck` from your worktree before the handback; it prints numbered
prose issues (a missing section, an uncited finding, an uncommitted report)
or `lanecheck: DONE rc=0`. Fix, commit, rerun; end only on DONE rc=0. If you
must stop early, put `STATE: stopped` in the report (a committed one) and run
lanecheck: rc=2 is the honest stop, not a pass.

## Delivery bar
Branch lane/<lane>, committed, report committed, targeted validation run
with numbers in the handback. RE-PIN EVERY MANIFEST/COUNT/PIN YOUR CHANGE
MOVES in the same delivery (readers found by grep) — post-merge manager
cleanup of your pins is a delivery failure. The full battery is the manager's at merge.
A NEW OR CHANGED .rxt CORPUS FILE moves population pins well beyond
the rxtsource census: the start-set mover manifests (tests/startset/manifests/),
the axes allowances, size tripwires. Run `make test` (async), not only the
section you think counts (2026-10-10: rev2corp re-pinned rxtsource only;
main's post-merge make test went red on test-startset, lane sstri).
A change that makes a strategy fire in new places (new row, widened admission, new rung) runs `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` before delivery and re-aims each moved witness in the same delivery.
Never merge to main yourself.

## Design lanes
A design note answers the three STANDING QUESTIONS in docs/design/CLAUDE.md (measurement regime; independent control; what moves when data is regenerated). For each one, first state whether it is relevant to this design.

Cite a docs/spec/ file by its section number (`match_api.md §6.3.4¶11`), never by line (the file name, a colon and a line number), in every file you write: notes, reports, review text. `make test-spec-history` scans the whole tree and goes red on a line cite (it turned CI red twice, 2026-10-17 and 10-18).
