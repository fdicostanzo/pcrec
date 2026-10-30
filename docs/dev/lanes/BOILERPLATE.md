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
- The interactive `grep` here may be a ugrep function that silently skips
  worktree contents; scripts and lanes use `command grep`.
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
- ARM OWED RUNS DETACHED: a run you launch as a plain background task DIES
  WITH YOUR SHELL the moment the manager closes your session (b1triage's
  did, 2026-09-22) — a chain you are owing past your own end must be
  `nohup … > log 2>&1 & disown`, not a bare `&` (`scripts/chainrun` detaches
  this way by default: setsid, stdin closed, output to its logdir). On the Mac, ALSO keep the
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
  background and END. The manager's watcher (`scripts/watchrun`) catches
  completion; a fresh agent (or the manager) reads the log and completes
  the delivery. If a
  long run's results feed your own later work, fill the wait with
  independent items — never idle-wait — or deliver in stages and let a
  fresh agent resume from your report.
- NEVER IDLE-WAIT FOR A BOX SLOT OR A LONG RUN (Frank, 2026-10-07). A lane
  commits, ARMS its chain with `scripts/chainrun --lift worktrees/NAME/.lift
  build/STAGES` (detached by default; the lift wait and every stage run in
  it), hands back and ENDS. The manager lifts; a FRESH agent reads the
  verdicts. DO NOT hand-write a waiter, a chain.sh or a watcher: chainrun,
  `scripts/watchrun` and `scripts/verdict` (scripts/CLAUDE.md) carry the
  fixes for every chain/watcher bug we have had, each planted back in their
  self-tests — rc read after a `$(...)`, DONE written when a stage died, two
  waiters on one `.lift` (decattr/decland, 2026-10-09, interleaved chains that
  contaminated every verdict), a chain.sh edited under a live waiter, a
  watcher that fired on its startup state or read quiet as done.
  ONE CHAIN OR WAITER PER TREE is enforced: a second chainrun in the tree is
  REFUSED naming the live one (`scripts/safekill PID` it first if it is
  yours and stale). The stages file is read once, so editing it later
  changes nothing. Stage verdicts and a chain's trailer (`== CHAIN DONE` only
  after the last stage passed, else `== CHAIN FAILED stage=...`) are in
  `build/chainrun/<ts>-<name>/chain.log`; read any log's verdict with
  `scripts/verdict LOG`. The manager watches with `scripts/watchrun TREE`
  (one line on an actionable state, then exits).
  OR ENQUEUE IT ([BOXQUEUE], 2026-10-21; template below): `scripts/boxqueue
  batch --owner NAME --prio P --lift worktrees/NAME/.lift build/STAGES` turns
  the same stages file into one queue job per stage, or `scripts/boxqueue
  add` queues a job script you wrote. Every job is dry-run AT ENQUEUE, so a
  bad invocation is refused in seconds instead of after hours waiting for a
  slot; a failed stage is retried ALONE (`scripts/boxqueue retry KEY`); a
  corrective or forgotten check is one more job, never a second chain or a
  hand-written waiter. `scripts/boxqueue status` answers "why has X not run".
  ONE STAGE PER JOB (Frank, 2026-10-30): a multi-stage validation (sections,
  make test, test-axes, asan, mech) is queued as one job PER STAGE (`batch`,
  or `add` jobs chained with `after`), never one script running them all, so
  a short job from another session slips in at each stage boundary instead
  of waiting hours behind a 4-hour chain (730-fsfix-check, one five-stage job, held the box for hours).
- MECH IDS ARE PASSED WITHOUT A SUFFIX (`S222`, never `S222_...`), and a row's
  verdict is read from its own `== mech run COMPLETE` trailer (C3's chain
  lost 23 rows to `S222_`).
- `timeout` (sized generously) on every command of uncertain length; a
  firing timeout is a FINDING.
- Kill only by `scripts/safekill PID`; wrap hang/allocation risks in
  `scripts/watchdog -s WALL -m RSS_KB -c CPU -S label -- cmd`.
- ONE heavy suite at a time on this box; coordinate via the manager. THE BOX
  LOCK enforces it: `scripts/boxlock` (flock on `worktrees/.box.lock`) is
  taken by perfrun, battery.sh, the mech matrix (a single row too),
  emit_sweep.py corpus runs, `make test-axes` and `make test-ksweep`, and by
  every `heavy` chainrun stage; a second heavy run WAITS, naming the holder
  (`PCREC_BOXLOCK_WAIT=0` refuses instead, exit 75). `scripts/boxlock status`
  before starting anything heavy by hand. SWEEP CAP: a loop above 50
  compiles (a census, a sweep, a probe battery) is heavy — run it as
  `scripts/boxlock run --label NAME -- CMD` or as a `heavy` chainrun stage.
  `PCREC_BOXLOCK=0` opts out, only with the manager's say-so.
  LABEL EVERY `boxlock run --label <lane-name>-<what>` (2026-10-27): `boxlock status` lists the waiters by label, `lanewatch --follow` reads a lane waiting on the lock as WAITING (not QUIET) by that prefix, and `queuewatch` raises WAIT-LONG for it after 30 min.
  GENERATED LOAD IS HEAVY: a test that spins CPU on purpose (to shake out a
  race) runs under `scripts/boxlock run` like any suite (2026-10-24: a lane's
  32 busy loops pushed a queued make test past its cap).
  A lane's chain of `boxlock run` steps YIELDS to the box queue, and THE LOCK
  ENFORCES IT: a non-queue `boxlock run` waits (one `YIELDING to queue job`
  line) while any queue job is pending and ready (2026-10-24: a kit lane's
  back-to-back lock steps held two queued make tests for 30 min). Nothing to
  remember; `PCREC_BOXLOCK_JUMP=1` overrides, audited, manager's say-so only.
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
- Mech/sabotage: take S-ids from the range YOUR BRIEF names. With no range,
  the highest S-id on main is NOT enough: `memfn/docs/requests.md` reserves
  ranges for the kit (`grep -n 'Sabotage ids' memfn/docs/requests.md`) and
  ids inside a reserved range are not free even when unused (k100/decattr
  took S674/S675 from the kit's S666-S675, 2026-10-09). Then check the
  highest existing S-id ON MAIN and in worktrees/*/tests/mech before numbering;
  anchors are copied from `git show HEAD:<path>`; a re-anchor needs its
  intent re-verified.

## Heavy-chain template: `make test` goes through `scripts/perfrun` ([TT-JTUNE])
A chain's (or slot's) full-suite line is NOT a raw `make -k -jN -Otarget test`.
In a chainrun stages file (`NAME CLASS CAP COMMAND`, scripts/chainrun's header):

    build   light 300   make -j16
    strict  light 600   make strict
    test    light ttune scripts/perfrun --label NAME -- "$STAGE_LOG.make"
    mech    light 5400  bash tests/mech/run_sabotage_matrix.sh S222 S223

(NOT `make mech S222 S223`: the make target takes no ids, so make runs the
FULL matrix and then fails on `S222` as a target — 100 min of box time,
2026-10-20. perfrun and the matrix take the box lock themselves, so `light`
is enough for them; `heavy` is for a command that does not. `ttune` sizes the cap from the
ledger's longest clean run times 1.5.) perfrun returns make's rc unchanged.

It picks a rotated parallelism shape, writes make's output to the log
byte-identically (the verdict is still `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`),
samples CPU, and records a ledger row (docs/dev/ttune_measurement.md).
`--shape J,P` pins a shape when a run must be comparable to an earlier one.
`scripts/verdict LOG` reads that log plus its `LOG.perfrun` note in one go.
TRIAGE RULE: a red section list is read WITH the perfrun note. `class=K44-ONLY`
(red only in test-corpus/counterk/resource/cli on the counterk.rxt:1807 or
resource CPU-cap cells) and `class=LOAD-SUSPECT` are the SHAPE's finding, not
the lane's failure: re-run the named sections solo (`make test-X`); green solo
= green-by-diagnosis (known_issues K44). `RED-REAL` is the lane's. Do not
re-run the whole suite at another shape to "check"; the rotation owns shapes.

**TIMING WINDOWS ARE BOX-WIDE (2026-10-21).** Before ANY test or measurement command run outside the queue, single-process included (a compile batch, a sweep, a differential, a `PROCS>1` script), check `scripts/boxqueue status`. If a quiet-gated timing job is running (`idle-ok`, a `-slot`/`-window`/`-parity` name, or a label saying timing), do not run it: queue it as a job, or wait for the window to end. A lane's "light" work at PROCS=8 during the kit's E8 window contaminated its timing (2026-10-21). The quiet gate only checks quiet at the START of a window; keeping the box quiet afterwards is every lane's job. Single-process section runs during the kit's adatwin window (2026-10-21, lane i1tri2, allowed by its brief) still perturbed it: during a timing job, the only commands outside the queue are reads and edits.

## Queue template: a job script for `scripts/boxqueue` ([BOXQUEUE])
A job is one executable script named `PRIO-OWNER-REST`, called three ways
(scripts/boxqueue's header is the contract). `--dry-run` resolves everything
and prints the REQUIRED declarations; `--ready` answers "can I run now"
with no side effects; the plain call is the work, run under the box lock:

    #!/usr/bin/env bash
    # 200-NAME-mech: mech rows S222 S223 on worktrees/NAME
    set -u
    TREE=/home/pcrec/projects/pcrec/worktrees/NAME IDS="S222 S223"
    case "${1:-}" in
        --dry-run)    # ids resolve (VALIDATE_ONLY: seconds, no build, no lock)
            out=$(cd "$TREE" && VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh $IDS 2>&1) ||
                { printf '%s\n' "$out" | tail -3 >&2; exit 1; }
            n=$(printf '%s\n' "$out" | sed -n 's/^== mech FIELD VALIDATION COMPLETE: \([0-9]*\) def.*/\1/p')
            [ -n "$n" ] || { echo "no field-validation line" >&2; exit 1; }
            echo "would run in $TREE: bash tests/mech/run_sabotage_matrix.sh $IDS"
            echo "boxqueue: cap 5400"; echo "boxqueue: patience none"
            echo "boxqueue: size rows=$n"    # optional ([EXPECT-PREFLIGHT]): the cap scales past 5400 from earlier green runs' s/row
            echo "boxqueue: expect rows=$n last=^== mech run COMPLETE: "
            echo "boxqueue: witness rows=== mech run COMPLETE: $n rows (a sample of the line)"
            exit 0 ;;
        --ready)      # 0 now / 75 not yet (first line = the reason) / 77 never
            exec bash "$BOXQUEUE" after NAME-build ;;
    esac
    cd "$TREE" || exit 1
    exec bash tests/mech/run_sabotage_matrix.sh $IDS

A TIME GATE is a declaration, not a --ready wrapper: `echo "boxqueue: not-before 2026-10-27T00:05"` in the dry run (local ISO-8601, strict; boxqueue
holds the job until then without asking --ready and PENDING-STUCK stays quiet only until that time).

THE EXPECT DECLARATION has exactly these forms ([WATCH-IDLE]; `add` REFUSES
anything else and prints them): `expect none reason=WHY` (nothing counted; WHY
says what catches the tool crashing, e.g. "exec'd, so the tool's rc is the
job's rc"; a bare `none` is refused: a job that swallowed its tool's rc and
said `none` scored GREEN on a crash); `expect NAME=N [log=PATH] lines=ERE` (N =
lines of the log matching ERE); `expect NAME=N [log=PATH] last=ERE` (N = the
integer right after ERE's match on its last matching line, so it ALSO needs
`boxqueue: witness NAME=LINE`, a sample line the work prints, which the dry
run reads N back from with the same matcher: `last=^== X COMPLETE` with no
count after it read SHORT on a green 46-minute run). `log=PATH` names the file
the population is read from when the tool writes its OWN log (perfrun's
`-- LOG`; default job.log; relative = under the run dir, e.g. `log=job.log.make`
for `$STAGE_LOG.make`). A quiet but healthy stage (a single-threaded gate, a
quiet-gated timing slot) declares `boxqueue: idle-ok` (or `idle-ok SECONDS`)
so the IDLE-SUSPECT alarm (no CPU in the box or the job's tree, no log growth,
10 min) does not cry wolf; the alarm never kills.

`scripts/boxqueue add --name 200-NAME-mech FILE` dry-runs it (an unknown id
is REFUSED, exit 65) and queues a copy. Exit codes of the work: 0 done (green
only if `scripts/verdict` reads no red line AND the declared population was
met: 1 row of 2 is POPULATION-SHORT), 76 requeue me, 77 never, anything else
failed; a 75 from the WORK is a bug (readiness belongs in `--ready`). A
`lines=ERE` population that runs past its count (the full matrix instead of
6 rows) is killed within seconds. `scripts/boxqueue --dry-run` checks the
whole queue's plan before a night is committed to it.

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

## Other boxes
ubuntubudu (the bench's box, a second 10.46 oracle) is reachable by
`ssh duxevents@192.168.1.100` on the home LAN, or `duxevents@100.69.121.107`
over the tailnet. Light ops only; heavy runs there go through the manager
(never assume the box is free). Lanes on this Linux dev box rarely need
either: the 10.46 oracle is local.

## Design lanes
A design note answers the three STANDING QUESTIONS in docs/design/CLAUDE.md (measurement regime; independent control; what moves when data is regenerated). For each one, first state whether it is relevant to this design.

Cite a docs/spec/ file by its section number (`match_api.md §6.3.4¶11`), never by line (the file name, a colon and a line number), in every file you write: notes, reports, review text. `make test-spec-history` scans the whole tree and goes red on a line cite (it turned CI red twice, 2026-10-17 and 10-18).
