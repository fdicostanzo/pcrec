# LANE BOILERPLATE — read this FIRST, follow all of it

**NEVER write outside your worktree + session scratchpad — `/tmp`,
`~/.claude`, `$HOME` and the main tree included. `mktemp` must be given the
scratchpad dir (e.g. `mktemp -p "$SCRATCH"`); compilers/scripts that default
to `/tmp` need `TMPDIR` pointed at the scratchpad.**

Standing rules for every pcrec subagent lane. Your brief names your task,
model tier, and deliverable; everything below applies without restatement.
(Ruled by Frank 2026-09-06 to cut brief size and lane startup cost.)

## Scope mandate
Touch ONLY the pcrec repo (its path on this box: root CLAUDE.md's MANDATE),
and inside it ONLY your own worktree under worktrees/ (read-only elsewhere
in the repo). NEVER write to the sibling pcrec-bench checkout (read-only
reference at most), no other
directories, no system config. Session-temporary files go in the session
scratchpad directory named in your environment, never committed. Subagents
you spawn inherit this mandate — restate it in their briefs.
Disclosure: you inherit the session-root CLAUDE.md and the manager's memory
index at spawn; treat them as context, not tasking.

## Worktree setup (writers)
1. `git -C "$(git rev-parse --show-toplevel)" worktree add worktrees/<lane> -b lane/<lane>` (run from the main tree)
2. cd there; FIRST command: `git rev-parse --show-toplevel` — no edit until
   it prints your worktree path.
3. Build: `make -j16` on the Linux dev box (plain `gcc` is GNU gcc 15.2;
   the Mac needs `CC=gcc-16`, see Box facts).
Read-only critics work in the main tree and never run make.

## Box facts (Linux dev box, `pcrec@192.168.1.17`, since 2026-10-07)
Numbers are the measured record in docs/testing.md "The boxes" (MEASURED
2026-10-07, main 23111928); re-measure before citing them elsewhere.
- Ryzen 7 7700X, 16 threads, ~29 GB; Ubuntu x86_64; gcc 15.2.0 as plain
  `gcc` (no `CC=` override, no `gcc-16`); GNU make 4.4.1; bash 5.3;
  python 3.14.4. No clang, no `pcre2test` binary.
- Build and suite: `make -j16` ~2 s; the full `make -k -j16 -Otarget test`
  ~11 min (678.6 s measured, 59 sections). Read its verdict from
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` (empty = green).
- libpcre2-8 10.46 headers are installed and it IS the reference oracle
  here, so PC-3/PC-4/uprops RUN rather than skip (a red is real, not
  U13-expected).
- Bare `timeout` is uutils (~105 ms/call): use `gnutimeout`
  (`/usr/bin/gnutimeout`); in test scripts `tests/lib/timeout_bin.sh` ->
  `"$TIMEOUT_BIN"`. sed/xargs/wc are GNU here, but keep new test-script
  `sed` portable anyway (the suite also runs on the Mac).
- K54 (gcc libasan hangs every sanitized process AT EXIT under
  `detect_leaks=1`) does NOT apply: it is specific to gcc-16's LSan on
  arm64-darwin, and the Makefile's `SAN_DETECT_LEAKS` derivation only
  disables the leak tier on Darwin. On Linux the leak tier runs
  (santriage3_report.md found LSan live on ubuntubudu; not re-checked here).
- D45 budgets and load-guard thresholds were calibrated on ubuntubudu (a
  slower Ryzen 5 1600); on this faster box they are ceilings, not floors.
  ONE heavy suite at a time on the box, with 16 threads shared.
- The other boxes, for pointers only: the Mac (`/Users/fdicostanzo/pcrec`)
  is the hardware-run box (arm64, Apple M1 Max; bare `timeout` is GNU,
  BSD sed silently no-ops GNU-only BRE `\b` `\|`, libpcre2 10.48 is NOT
  the reference so PC-3 reads expected reds, `make test` ~100 min,
  `make test-axes` is multi-hour: sweep only your own axes with
  `AXES="-fno-..."`; docs/testing.md carries the rest). ubuntubudu
  (`/home/duxevents/pcrec`) is the bench's box: never run suites there;
  light probes only, heavy runs by slot request through the manager.

## Process rules (each has cost a lane before)
- COMMIT INCREMENTALLY (WIP commits) — commit age is your liveness signal.
- Long validation (>~2 min) runs in a BACKGROUND task writing a log — never
  a blocking foreground call; never a Monitor on a progress log. NOR a
  Monitor/notification on a COMPLETION you then go idle waiting for: an
  idle wait longer than ~4 min is DO-THEN-FINISH's case — commit, report
  the run OWED with its log path, hand back, END (three lanes idled this
  way on 2026-09-28 alone: pf36, land84, findb6).
- ARM OWED RUNS DETACHED: a run you launch as a plain background task DIES
  WITH YOUR SHELL the moment the manager closes your session (b1triage's
  did, 2026-09-22) — a chain you are owing past your own end must be
  `nohup … > log 2>&1 & disown`, not a bare `&`. On the Mac, ALSO keep the
  box awake for the chain's life (`nohup caffeinate -s -w <chain PID> &`, or
  prefix the chain with `caffeinate -s`): a maintenance sleep counts toward
  GNU timeout's wall clock and fails a check as if the code did (pf35's
  test-recursion red, 2026-09-27, an 879 s sleep read as "does not build").
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
- NEVER IDLE-WAIT FOR A BOX SLOT OR A LONG RUN (Frank, 2026-10-07). A lane
  commits, ARMS the chain detached (`nohup setsid` waiter polling
  `worktrees/NAME/.lift`, then the chain script; `& disown`), hands back and
  ENDS. The manager lifts; a FRESH agent reads the verdicts.
  ONE WAITER PER WORKTREE. Before arming in a worktree that has been armed
  before, find any live waiter or chain (`ps -eo pid,args | grep
  worktrees/NAME/build/land`) and stop it with `scripts/safekill`. NEVER
  rewrite a chain.sh that a live waiter may run: bash reads scripts
  incrementally. On 2026-10-09 decattr's original waiter and decland's new
  one both fired on one `.lift` and ran interleaved chains over the same
  logs and scratch, which contaminated every verdict.
- MECH IDS ARE PASSED WITHOUT A SUFFIX (`S222`, never `S222_...`), and a row's
  verdict is read from its own `== mech run COMPLETE` trailer (C3's chain
  lost 23 rows to `S222_`).
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
- Mech/sabotage: take S-ids from the range YOUR BRIEF names. With no range,
  the highest S-id on main is NOT enough: `memfn/docs/requests.md` reserves
  ranges for the kit (`grep -n 'Sabotage ids' memfn/docs/requests.md`) and
  ids inside a reserved range are not free even when unused (k100/decattr
  took S674/S675 from the kit's S666-S675, 2026-10-09). Then check the
  highest existing S-id ON MAIN and in worktrees/*/tests/mech before numbering;
  anchors are copied from `git show HEAD:<path>`; a re-anchor needs its
  intent re-verified.

## Heavy-chain template: `make test` goes through `scripts/perfrun` ([TT-JTUNE])
A chain's (or slot's) full-suite line is NOT a raw `make -k -jN -Otarget test`:

    scripts/perfrun --label NAME -- "$L/test.log" [MAKEVAR=val ...]
    log "make test rc=$?"        # perfrun returns make's rc unchanged

It picks a rotated parallelism shape, writes make's output to the log
byte-identically (the verdict is still `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`),
samples CPU, and records a ledger row (docs/dev/ttune_measurement.md).
`--shape J,P` pins a shape when a run must be comparable to an earlier one.
The chain's log line may append `$(cat "$L/test.log.perfrun")`'s last lines.
TRIAGE RULE: a red section list is read WITH the perfrun note. `class=K44-ONLY`
(red only in test-corpus/counterk/resource/cli on the counterk.rxt:1807 or
resource CPU-cap cells) and `class=LOAD-SUSPECT` are the SHAPE's finding, not
the lane's failure: re-run the named sections solo (`make test-X`); green solo
= green-by-diagnosis (known_issues K44). `RED-REAL` is the lane's. Do not
re-run the whole suite at another shape to "check"; the rotation owns shapes.

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
A NEW OR CHANGED .rxt CORPUS FILE moves population pins well beyond
the rxtsource census: the start-set mover manifests (tests/startset/manifests/),
the axes allowances, size tripwires. Run `make test` (async), not only the
section you think counts (2026-10-10: rev2corp re-pinned rxtsource only;
main's post-merge make test went red on test-startset, lane sstri).
Never merge to main yourself.

## Other boxes
ubuntubudu (the bench's box, a second 10.46 oracle) is reachable by
`ssh duxevents@192.168.1.100` on the home LAN, or `duxevents@100.69.121.107`
over the tailnet. Light ops only; heavy runs there go through the manager
(never assume the box is free). Lanes on this Linux dev box rarely need
either: the 10.46 oracle is local.

## Design lanes
A design note answers the three STANDING QUESTIONS in docs/design/CLAUDE.md (measurement regime; independent control; what moves when data is regenerated). For each one, first state whether it is relevant to this design.
