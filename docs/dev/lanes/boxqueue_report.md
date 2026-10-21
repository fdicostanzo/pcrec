# Lane boxqueue — [BOXQUEUE], the box-wide job queue (2026-10-21)

Build go: Frank, 2026-10-20, "Build it tomorrow". Scripts and docs only;
nothing under src/, cli/, lib/ or memfn/src/. Design read from
docs/design/plan_row_bodies/BOXQUEUE.md.

## Premise test (before any edit, main 73c2bb655)

`TMPDIR=<worktree>/build/tmp bash scripts/tests/{boxlock,chainrun,verdict,watchrun}.test`:
boxlock 17/17 (10 s), chainrun 26/26 (23 s), verdict 28/28 (1 s), watchrun
16/16 (52 s), all rc 0. The tools exist and match the design. No STOP-rule
contradiction was found (one interpretation, under Deviations, is flagged).

## What was built

| file | what |
|---|---|
| `scripts/boxqueue` | the queue and its runner. The header is the contract. |
| `scripts/tests/boxqueue.test` | 53 checks and 10 plants, about 65 s, one trivial job at a time, a scratch queue and lock |
| `scripts/verdict` | the perfrun DONE recogniser generalised to any `TOOL: DONE rc=N` line (additive) |
| `scripts/watchrun` | the default `--done` ERE generalised the same way (additive) |
| `scripts/emit_sweep.py` | prints `emit_sweep: DONE rc=N` as its last line on every ending |
| `scripts/tests/{verdict,watchrun}.test` | trailer cases: verdict 28 -> 31, watchrun 16 -> 17 |
| `scripts/Makefile` | one dependency line (boxqueue.test drives boxlock, verdict, chainrun, safekill) |
| docs | scripts/CLAUDE.md, scripts/tests/CLAUDE.md, BOILERPLATE.md (queue guidance, Queue template, mech template fix), docs/testing.md, the root CLAUDE.md situation-index row, the plan row status, the body's observed list and a "Built" section |

## Requirements -> how met

| requirement (body / brief) | how met | checked by |
|---|---|---|
| ONE box-wide queue dir: pending/ running/ done/ failed/ under worktrees/, gitignored | `<main>/worktrees/.boxqueue/`, found from git's common dir (as boxlock's lock is). `worktrees/` is ignored. wtprune's `worktrees/*` glob skips dot entries. `PCREC_BOXQUEUE_DIR` overrides it. | every test case uses a scratch dir |
| jobs are SCRIPTS; the PRIO prefix orders; owner in the name; reorder = rename, insert = new file, retry = a copy back | the name is `PRIO-OWNER-REST` and KEY is `OWNER-REST`. Order is C-locale sort. `add` copies; a hand-dropped file is dry-run on first sight; `retry KEY` re-adds the latest ended run's script | case 1 (order), 10 (hand-dropped), 8a/18 (retry) |
| ONE runner holds boxlock per job | `boxlock run --label queue:NAME --wait 5 -- boxqueue _start`; one runner per queue (flock on `.runner.lock`, a second gets REFUSED 75) | 12, 13 |
| exit codes 0 / 75 / 76 / 77 / other | work: 0 green (verdict not RED and populations met), 76 requeue to the end (PRIO = max pending + 1), 77 cancelled, anything else failed. `--ready`: 0, 75, 76 (renamed to the end), 77, other = READY-ERRORED | 2, 16 |
| readiness at the TOP of the script, no dependency language in the runner | the `--ready` mode. `boxqueue after KEY` is a helper a job may call, not runner syntax | 3, 18 |
| snapshot at start; a 75 discards the copy; the original stays editable | every pass snapshots each pending job. Inside the lock, the snapshot is compared with the original: an edit made in between is CHANGED and is not run, and a new pass runs the edited job | 5 (CHANGED, plant no-cmp) |
| a not-ready answer within seconds; a hang is killed, counted not-ready and logged | `--ready` runs under GNU timeout (`BOXQUEUE_READY_BOUND`, 20 s, a policy margin). A hang is logged READY-HUNG and the job stays pending | 9 (plant no-bound) |
| a job with side effects that then returns 75 is a bug, planted | a 75 from the WORK goes to failed/ as NOT-READY-AFTER-START and is never re-run | 4 (plant side75) |
| every pass logs every job's answer; "why hasn't X run" in one line | `queue.log`: `pass N NAME ready / not-ready: <reason> (since T) / READY-HUNG / waiting on <holder>`, plus START/END. `status` (and the `status` file) shows one line per pending job | 1, 12 |
| not ready past its stated patience is reported | the `patience S\|none` declaration (required). Exceeding it writes one `REPORT` line | 8b |
| shared by main, the kit and the bench; a session reorders only its OWN jobs | OWNER is in every name. Ownership is a convention and is NOT enforced (see Deviations) | — |
| chainrun stage files become batches of jobs | `boxqueue batch --owner O --prio P [--lift F] [--tree D] STAGES`. It parses with `chainrun --check` (its caps and its ttune rule are reused). Each stage becomes one job whose `--ready` is `after <previous>`. Downstream stages WAIT on a failed stage, and `retry` re-runs that stage alone | 18 |
| `--dry-run` at ENQUEUE (refuse) and again before START | `add` refuses with exit 65 and shows the reason. START re-runs it, and a failure goes to failed/ as DRY-RUN-FAILED at START | 10 (plant no-dry-add), 11 |
| the first seconds look wrong (rc 2 at once) -> reported at once | the END line is written when the job exits, and a failure under `BOXQUEUE_FAST` (10 s) is marked FAILED-FAST | 2 |
| a population far larger than declared is reported at once | a `lines=` count is watched every `BOXQUEUE_MONITOR` s (2). Past its declaration the job is killed: POPULATION-OVER, killed early | 7 (plant no-watch) |
| declared EXPECTED populations checked against the job's log (fewer = not green) | `boxqueue: expect NAME=N lines=ERE\|last=ERE`, counted in THIS run's fresh log. Fewer = POPULATION-SHORT (failed) | 6 (plant no-short), 8a (plant append-log) |
| per-pass "waiting on <holder>" | the lock refusal's holder text is logged every pass and shown in `status` | 12 |
| corrective jobs enqueued behind the running one | there is no per-tree lock in the queue; an `add` goes into pending/ at any time | 2, 18 |
| `boxqueue --dry-run`: order, ready/not-ready, populations, total cap | `--dry-run` / `plan`. It exits 1 if any job would not run correctly, and moves nothing | 19 |
| plant: a dry run that lies | declared 2 and ran 20: killed early. With the watch planted away, it runs its full length | 7 |
| plant: a stale pending copy | the original kept after start makes the job run twice; no compare makes the stale v1 run over an edit | 5 |
| plant: a watcher counting pre-existing state | an appended per-name log counts an earlier run's rows (GREEN on a short run). Never-cleared state makes a re-added job inherit the old not-ready clock | 8a, 8b |
| ADDED: emit_sweep prints no completion line, so verdict reads INCOMPLETE | the general fix: ONE trailer convention, `TOOL: DONE rc=N` (below) | verdict.test, watchrun.test |
| build ON boxlock/chainrun; their self-tests green; contracts unchanged | boxlock and chainrun are unchanged; chainrun's `--check` is reused. verdict and watchrun gain an additive recogniser (perfrun's line now matches any tool). After the edits: chainrun 26/26, watchrun 17/17, verdict 31/31, emit_sweep.py.test 24/24 | see Validation |

## The completion-signal choice (the brief's ADD)

There were two candidates: give emit_sweep a completion line, or let a job
declare its own completion signal. I picked a general version of the first:
**one convention, `TOOL: DONE rc=N`**, recognised by verdict (and by
watchrun's default `--done`) for ANY tool. It was perfrun's existing form,
so perfrun is now one member rather than a special case. emit_sweep prints
the line on every ending: pass, red, argparse refusal and traceback (a
`completion_trailer()` wrapper around `main()`). A run re-exec'd under the
box lock prints it from the exec'd child.

Why I did not pick a per-job declared completion ERE:

- A declared ERE is a control written by the author of the thing it
  controls (learnings §3). A wrong ERE reads INCOMPLETE forever, or matches
  an echo and reads complete.
- It would only fix queue jobs. The observed failure was a HAND read
  (`scripts/verdict LOG`, then arms.tsv by eye), and a `watchrun --log` on a
  bare sweep log would stay blind.
- Inside the queue the runner already owns the job's rc (it passes `--rc`,
  as chainrun does), so completion is never in doubt there.

## Deviations / interpretations (each is a choice you might not expect)

1. **Three modes, not one call.** The body says the runner "RUNS each
   candidate" and "a 75 discards the copy". But it also asks `boxqueue
   --dry-run` to run every job's "dry run and readiness check" without
   running the work. That needs readiness to be callable on its own. So a
   job is called as `--dry-run`, `--ready`, and plainly for the work, and 75
   is `--ready`'s answer. A 75 from the work is exactly the "side effects,
   then 75" bug: it is failed (NOT-READY-AFTER-START), never left pending to
   repeat its side effects. The body's "Built" section records this.
2. **Ownership is not enforced.** OWNER is in every name and the docs say
   a session touches only its own jobs. A file queue cannot stop a `mv`.
3. **Every queue job runs under the box lock**, including a batch stage that
   chainrun called `light`. The queue is box-serial by construction. A
   lane's light steps that do not need ordering (a `make -j16`) can stay
   outside it.
4. **Batch jobs declare `expect none`**, and their generic dry run checks
   only that the tree exists and prints the command. A stage that has a
   population (mech rows, sweep arms) should be a written job script; the
   BOILERPLATE "Queue template" is the mech example.
5. **The runner is not a daemon.** It exits when pending/ is empty
   (IDLE-EXIT; there is a release-then-recheck so an `add` racing the exit
   is not stranded). `add` and `retry` arm a runner if none is live.
6. **Policy constants, unmeasured, labelled in the header:** ready bound
   20 s, dry bound 30 s, monitor 2 s, fail-fast 10 s, lock wait 5 s, pass
   pace 60 s. Each has an env override.
7. **Linux only.** It needs flock(1) and /proc and exits 69 otherwise. The
   Mac keeps `.mac-suite.lock`, as boxlock does.
8. **A finding outside the brief:** the BOILERPLATE heavy-chain template
   itself said `mech heavy 5400 make mech S222 S223`. That is the 2026-10-20
   invocation that ran the FULL matrix to two cap fires, because the make
   target takes no ids. It now says `bash tests/mech/run_sabotage_matrix.sh
   S222 S223` (light: the matrix takes the lock itself). The queue template
   resolves ids with `VALIDATE_ONLY=1`. I checked that template verbatim in a
   scratch queue: S222/S223 queued with `expect rows=2`, and S99999 was
   REFUSED 65 with the matrix's own FATAL line.
9. Bugs found and fixed while building, each now covered:
   - the mid-run watch's last `sleep` inherited the box-lock fd and left the
     lock HELD-ORPHAN for up to one poll after the job (the watch now closes
     inherited fds);
   - a detached runner armed by an `add` from inside a lock holder would
     have held that holder's lock fd forever (case 17, plant keep-fds);
   - `read` drops an ERE's trailing blank, so `last=^== mech run COMPLETE: `
     read "none" (blanks after the match are now skipped; case 6 mechlike).

## Opt-in: the kit

- A memfn slot script becomes the WORK of a job named `NNN-kit-<slot>`. The
  kit calls the MAIN tree's `scripts/boxqueue add` (the same user, the same
  box, so no relay is needed).
- The slot's own `scripts/boxlock run --label kit -- ...` stays valid: inside
  a queue job it nests by token and runs at once (case 12b). Nothing in the
  slot scripts has to change for that.
- What each slot adds is the two cheap modes:
  - `--dry-run`: the kit tree exists, the inputs and pins resolve, and the
    command is printed, plus the `cap` / `patience` / `expect` declarations.
    A judge slot with N cells declares `expect cells=N lines=<its per-cell
    line>`.
  - `--ready`: things like "main's B-step merged" or "Frank cleared the
    slot", via a file or `boxqueue after main-<key>`.
- Kit jobs are ordered with main's by PRIO alone. The manager and the kit
  agree on PRIO bands (a proposal: main 100-499, kit 500-699, bench
  700-899), so a session reorders inside its own band.

## Opt-in: the bench (draft inbox text below; nothing was written in pcrec-bench)

The bench's window scripts (`scripts/run_window.sh` and friends) stay its
own. A night window becomes one job per window (or per sub-bench):

- **Name:** `7NN-bench-<subbench>`.
- **`--dry-run`:** the bench's cheap preflight. Testee names resolve, the
  pcrec pin exists, the store is writable. It must take seconds and write
  nothing. The bench's existing `--dry-run` knob runs cells, so it is NOT
  this preflight.
- **`--ready`:** the window's own gates, such as the clock (past 01:00),
  Frank's clearance for tonight (a file), and the bench's quiet probe.
- **Work:** the window script itself.

The queue guarantees that no other queue job and no other boxlock taker runs
during the window. It does NOT make the box quiet: Frank's processes,
ghostty and untracked light work still run. The bench's quiet gate stays the
bench's, and its window handshake and calendar are unchanged.

### Draft bench inbox entry (for the manager to number and commit as `[inbox]`)

> **I-NNN (2026-10-2x, pcrec manager): a box-wide job queue is available
> (opt-in, nothing asked now).**
>
> pcrec has merged `scripts/boxqueue` ([BOXQUEUE]). It is ONE queue for
> heavy work on this box: `/home/pcrec/projects/pcrec/worktrees/.boxqueue/`.
> One runner takes the box lock for each job in turn and logs every pass,
> including "waiting on <holder>" while someone outside the queue holds the
> lock. A job is an executable script named `PRIO-OWNER-REST`. It is called
> three ways:
> - `--dry-run`: seconds, no side effects; it prints the commands and the
>   required `boxqueue: cap / patience / expect` lines. It is called when
>   the job is enqueued and again just before it starts.
> - `--ready`: 0 now, 75 not yet (the first line is the reason), 77 never.
> - with no argument: the work, under the box lock.
>
> The contract is in the script's header. Opting in would mean wrapping a
> night window as a job named `7NN-bench-<subbench>`: your window gates
> (clock, Frank's clearance, your quiet probe) go in `--ready`, and a cheap
> preflight goes in `--dry-run`. Then call
> `/home/pcrec/projects/pcrec/scripts/boxqueue add FILE`. While your job
> runs, no pcrec or kit queue job and no box-lock taker can run. The box is
> NOT made quiet, so your quiet gate stays yours. The calendar and the window
> handshake are unchanged; the queue only orders work once a window is
> cleared.
>
> We propose PRIO bands (main 100-499, kit 500-699, bench 700-899); each
> session reorders and cancels only its own jobs. Questions, or a different
> band, in your outbox whenever convenient.

## Proposed D text (if you want this recorded as a decision)

> D-next (BOXQUEUE): box-wide ORDER of heavy runs is `scripts/boxqueue`'s.
> (1) A job is a script with three modes: `--dry-run` (correctness;
> required `cap` / `patience` / `expect` declarations, no silent defaults),
> `--ready` (now: 0/75/76/77) and the work. A 75 from the work is a bug,
> failed and never repeated. (2) Green = rc 0, plus verdict not RED, plus
> every declared population met in the run's own log. (3) The completion
> convention for every tool's log is ONE `TOOL: DONE rc=N` line, read by
> verdict and watchrun. A per-job completion pattern was rejected (it is a
> control sharing its author with what it controls).

## Validation

- `scripts/tests/boxqueue.test`: **53 passed, 0 failed**, about 65 s. It was
  run directly with `TMPDIR=<worktree>/build/tmp`. The 10 plants all went
  red against their cases.
- After the edits, each run directly:
  - verdict.test 31/31;
  - watchrun.test 17/17;
  - chainrun.test 26/26 (unchanged script);
  - emit_sweep.py.test 24/24 (needs the worktree's `build/pcrec`, built
    with `make -j16`).
- `make -C scripts -k test` (the whole scripts self-test set, the D48 path):
  see STATE AT HANDOFF.
- Hooks and lint: `plan_lint` 0 violations; the pre-commit staged checks
  passed on every commit.
- No make test, no corpus sweep, no mech run (none is owed: scripts and
  docs only). The real box lock was never taken.

## STATE AT HANDOFF

- Branch `lane/boxqueue`, committed.
- Rulings file `docs/dev/lanes/boxqueue_rulings.md`: empty at every
  checkpoint, so no entry was applied.
- `make -C scripts -k test`: result recorded in the handback message
  (log `worktrees/boxqueue/build/tmp/testscripts.log`, completion line
  `make rc=N`).
- To resume: the merge is the manager's. After the merge, the first real use
  is main's next validation chain as `boxqueue batch` (or as job scripts).
  Then the kit's and the bench's opt-in, using the draft inbox text above.
