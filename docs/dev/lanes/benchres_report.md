# benchres report: [BENCH-RESERVE], pcrec's side of the bench reservation contract

Lane benchres (sonnet), branch lane/benchres, 2026-10-25. Scripts only; no product change, no docs/spec hunk.

## STATE AT HANDOFF

Built, committed, NOT merged. Last rulings entry applied: none (benchres_rulings.md was empty).

- `scripts/boxqueue`: import step (`bench_inboxes`, `win_parse`, `bench_one`, `bench_reconcile`, `bench_sync`), a hidden
  `_pop MODE ERE LOG` subcommand (the placeholder reads the bench log with boxqueue's own `pop_count`), a `-h` block
  `BENCH WINDOWS`, `status` lists non-DONE windows.
- `scripts/boxqueue_window`: the FIXED placeholder job (a static file, copied byte for byte into pending/).
  Values come from QUEUE/.bench/KEY.params (validated key=value lines, read with a `case`, never sourced or eval'd).
- `scripts/boxqueue.inboxes`: the declared inbox list, one entry today:
  `/home/pcrec/projects/pcrec-bench/worktrees/.mgr/boxqueue /home/pcrec/projects/pcrec-bench` (inbox, log root).
- `scripts/tests/boxqueue.test` case 25 (25a-25p, 27 PASS rows when run alone, incl. 5 planted bugs S1610-S1614).
  Full file: `boxqueue.test: 113 passed, 0 failed` (scratch TMPDIR under build/scratch).
- Docs: `boxqueue -h`, scripts/CLAUDE.md, docs/testing.md (queue paragraph), plan row status.

How the contract maps onto boxqueue (reuse, nothing duplicated): cap = the job's `cap` (timeout's TERM is trapped by
the placeholder and written CAP-FIRED, job rc 124); patience, idle-ok = the job's declarations (`idle_ok=S` -> `idle-ok S`);
done_ere/expect/witness = a declared `expect window=N log=BENCHLOG last=done_ere` + `witness window=LINE`, so the
enqueue gate refuses a witness that cannot produce N and boxqueue's pop_check judges the finished window too; the
bench log's red lines count (boxqueue's `log=` rule). Job lifecycle lines (`== job 750-bench-W START owner=bench`,
`END ...`) are queue.log lines like any job's.

queuemon: owner is the job name's second field (`bench`); an owner other than main/kit is addressed to main, and
RED/PROBLEM for any non-main owner are also written for main (queuemon header + `say`). So JOB-START/JOB-DONE of a
window are logged, green -> GREEN to owner bench, red/failed -> RED to bench AND main, cancelled -> INFO. Read from
the source, not run (a scratch queue keeps queuemon inert).

STOP RULE did not fire: a job that holds the lock until an external log line fits the model (the placeholder is
an ordinary job that polls).

PREMISE TEST: idle-ok fits. The idle alarm samples box CPU, the job tree's CPU and growth of job.log AND every
`log=` file of an expect, so a window waiting on a hot bench is not idle (the bench log grows / box busy); a
quiet-gated timing window should send `idle_ok=SECONDS` (the alarm never kills).

## HOW TO ENABLE (the bench inbox)

1. Merge lane/benchres (manager). The shipped `scripts/boxqueue.inboxes` already names the bench inbox.
2. `scripts/boxqueue start` once (the MAIN tree's copy). A runner with a declared inbox does not IDLE-EXIT, so it
   stays up and scans every `BOXQUEUE_EVERY` (60 s). A runner already live picks the new script up by its own
   RE-EXEC at the top of its next pass (never mid-job).
3. The bench creates the inbox dir `/home/pcrec/projects/pcrec-bench/worktrees/.mgr/boxqueue/` (absent today; pcrec
   never writes in that repo) and drops `<name>.window` (write a temp name, then `mv` into place).
4. The bench polls `/home/pcrec/projects/pcrec/worktrees/.boxqueue/reservations/<prio>-bench-<name>.state`.

Scratch/test use: `PCREC_BOXQUEUE_DIR` (queue), `BOXQUEUE_INBOXES=FILE` (config), `BOXQUEUE_WINDOW_SETTLE`,
`BOXQUEUE_WINDOW_POLL`. A scratch queue with no `BOXQUEUE_INBOXES` imports nothing.

## THE CONTRACT (copied verbatim from the 2026-10-25 brief; one copy for the bench and main)

.window FILE: <inbox>/<name>.window, key=value, one per line, no shell (PARSED, never sourced or eval'd; reject unknown keys, missing required keys, non-integer numbers, prio outside 700-899, name not [A-Za-z0-9._-]+, log not an absolute path under /home/pcrec/projects/pcrec-bench/). Keys, all required unless marked:
  prio=7NN (700-899)  name=<window> (job becomes <prio>-bench-<name>)
  cap=SECONDS (the window's work, lock wait excluded)  patience=SECONDS
  idle_ok=SECONDS (optional)
  log=ABS path of the bench's run log (under pcrec-bench)
  start_s=SECONDS (the log must exist within this long after RUNNING)
  done_ere=ERE (e.g. ^WINDOW_RUN_COMPLETE cells=)  expect=N (the integer right after done_ere's match; the bench will use done_ere `^BENCH_WINDOW_COMPLETE rc=` expect=0)  witness=a sample line
  fail_ere=ERE (the bench prints it on ANY abnormal exit; ends the window early)
STATUS (the bench polls by reading): /home/pcrec/projects/pcrec/worktrees/.boxqueue/reservations/<prio>-bench-<name>.state, ONE line, rewritten in place atomically (write tmp + mv):
  QUEUED <iso> | RUNNING <iso> <pid> | DONE <green|red|failed|cancelled> <iso> <reason>
  The bench starts its runner only on RUNNING. Lock held <=> state RUNNING (write RUNNING only after the lock is taken; write DONE before releasing it).
PLACEHOLDER ENDS: done_ere line with N == expect -> DONE green; N != expect -> DONE red POPULATION; fail_ere line -> DONE failed BENCH-FAIL; no log within start_s -> DONE failed NO-START; cap -> DONE failed CAP-FIRED (lock released). The bench stops its window when the state leaves RUNNING.
CANCEL: <inbox>/<name>.cancel -> DONE cancelled (if RUNNING: lock released). Withdraw = the .window deleted before import. Import is once per name (a re-used name is refused/ignored with a log line; record imported names).

## Reasons written (the exact DONE reason text the bench will see)

- green: `WINDOW-COMPLETE n=N`; red: `POPULATION n=N expect=M`; failed: `BENCH-FAIL`, `NO-START (no LOG within Ns of RUNNING)`,
  `CAP-FIRED (CAPs)`, `STALE-LOG ...`, `TERMINATED (after Ns, before the cap)` (an external kill), or boxqueue's own
  reason when the placeholder could not write DONE itself (runner died, killed hard; `bench_reconcile` writes it);
  `REJECTED: <reason>` for a refused window; cancelled: `CANCELLED by the bench` (or boxqueue's reason if cancelled by hand).

## QUESTIONS FOR THE BENCH / MAIN (defaults chosen where the contract was silent; none is irreversible)

1. REJECTED windows: the contract has no word for a refused `.window`. Chosen: the importer logs it and, when name and
   prio are usable, writes `DONE failed <iso> REJECTED: <reason>` so the bench does not wait forever. A rejected
   file may be fixed and rewritten under the SAME name (it was never imported; each distinct file content is judged once).
   Only an IMPORTED name is once-only. OK?
2. The `.window` file name must equal its `name=` key (the cancel file is `<name>.cancel`). Rejected otherwise.
3. Names containing `--` are rejected (a queue job name cannot hold `--`); the contract's regex alone allows it.
4. `log` is further limited to letters, digits, `_ . / -` (no spaces), no `..` component; the bench's own log path
   fits that today?
5. STALE-LOG: a log that already exists when the window begins (RUNNING) ends the window failed STALE-LOG, never read,
   because an earlier run's done line would read as a green. The bench must write a FRESH log path per window
   (and must not pre-create it before RUNNING). OK?
6. `patience` is declared (the job needs it) but has nothing to bound: the placeholder is always ready, and waiting for
   the box lock is not a not-ready answer, so it never fires. Do you want patience to mean "withdraw the window if still
   QUEUED after N s"? That would be a new rule; not built.
7. Atomic writes: the importer waits until a `.window` has been unmodified for `BOXQUEUE_WINDOW_SETTLE` s (2) as a guard
   against reading a half-written file; the bench should still write temp + `mv`.
8. While ANOTHER job runs (e.g. a 40-minute make test) the runner is inside that job, so a new `.window` is imported
   (state QUEUED) and a `.cancel` of a still-queued window is honoured only when that job ends (the ordering by prio is
   still right, since import happens before the next pick). A window already RUNNING reacts to `.cancel` within
   `BOXQUEUE_WINDOW_POLL` s (2). If the bench needs a prompt QUEUED, a side importer is possible; not built.
9. `start_s` is measured from RUNNING (not from the bench's runner start): the bench should create its log within
   start_s of seeing RUNNING.
10. Imported names are recorded in QUEUE/.bench/imported (queue-local); wiping the queue dir forgets them.
11. S1610-S1614 are used as in-test plant labels in boxqueue.test (not rows in the mech matrix).

## Not done / caveats

- Nothing run on the live queue; every test is a scratch queue + scratch inbox + a fake bench runner.
- Process note: an accidental empty `/tmp/dummy` was created by a mistyped command and removed at once.
