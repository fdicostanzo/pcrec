# benchres report: [BENCH-RESERVE], pcrec's side of the bench reservation contract

Lane benchres (sonnet), branch lane/benchres, 2026-10-25. Scripts only; no product change, no docs/spec hunk.

## STATE AT HANDOFF

Built, committed, NOT merged. Last rulings entry applied: R2 (R1 and R2 both; fcbaeae76 predated them).

- `scripts/boxqueue`: import step (`bench_inboxes`, `win_parse`, `bench_one`, `bench_reconcile`, `bench_sync`), a hidden
  `_pop MODE ERE LOG` subcommand (the placeholder reads the bench log with boxqueue's own `pop_count`), a `-h` block
  `BENCH WINDOWS`, `status` lists non-DONE windows.
- `scripts/boxqueue_window`: the FIXED placeholder job (a static file, copied byte for byte into pending/).
  Values come from QUEUE/.bench/KEY.params (validated key=value lines, read with a `case`, never sourced or eval'd).
- `scripts/boxqueue.inboxes`: the declared inbox list, one entry today:
  `/home/pcrec/projects/pcrec-bench/worktrees/.mgr/boxqueue /home/pcrec/projects/pcrec-bench` (inbox, log root).
- `scripts/tests/boxqueue.test` case 25 (25a-25p, 27 PASS rows when run alone, incl. 9 planted bugs S1610-S1618).
  Full file: see the closing line of the R2 section below (scratch TMPDIR under build/).
- Docs: `boxqueue -h`, scripts/CLAUDE.md, docs/testing.md (queue paragraph), plan row status.

How the contract maps onto boxqueue (reuse, nothing duplicated): cap = the job's `cap` (timeout's TERM is trapped by
the placeholder and written CAP-FIRED, job rc 124); patience, idle-ok = the job's declarations (`idle_ok=S` -> `idle-ok S`);
done_ere/expect/witness = a declared `expect window=N last=done_ere` + `witness window=LINE` read from the JOB's own
log (R2): the placeholder echoes the last done_ere line among the bytes the bench log gained since RUNNING, so the
enqueue gate still refuses a witness that cannot produce N and pop_check judges the finished window, while stale or
red lines already in the bench log never decide the verdict. Job lifecycle lines (`== job 750-bench-W START owner=bench`,
`END ...`) are queue.log lines like any job's.

queuemon: owner is the job name's second field (`bench`); an owner other than main/kit is addressed to main, and
RED/PROBLEM for any non-main owner are also written for main (queuemon header + `say`). So JOB-START/JOB-DONE of a
window are logged, green -> GREEN to owner bench, red/failed -> RED to bench AND main, cancelled -> INFO. Read from
the source, not run (a scratch queue keeps queuemon inert).

STOP RULE did not fire: a job that holds the lock until an external log line fits the model (the placeholder is
an ordinary job that polls).

PREMISE TEST: idle-ok fits. The idle alarm samples box CPU, the job tree's CPU and growth of job.log (the bench log is no
longer a declared `log=` since R2, so its growth no longer counts; a hot bench still keeps the box busy); a
quiet-gated timing window should send `idle_ok=SECONDS` (the alarm never kills).

## HOW TO ENABLE (the bench inbox)

1. Merge lane/benchres (manager). The shipped `scripts/boxqueue.inboxes` already names the bench inbox.
2. `scripts/boxqueue start` once (the MAIN tree's copy). A runner with a declared inbox does not IDLE-EXIT, so it
   stays up and scans every `BOXQUEUE_EVERY` (60 s) and, while a job runs, every `BOXQUEUE_BENCH_EVERY` (15 s). A runner already live picks the new script up by its own
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
  start_s=SECONDS (REQUIRED; the log must GROW, any appended byte, within this long after RUNNING; R1.7)
  done_ere=ERE (e.g. ^WINDOW_RUN_COMPLETE cells=)  expect=N (the integer right after done_ere's match; the bench will use done_ere `^BENCH_WINDOW_COMPLETE rc=` expect=0)  witness=a sample line
  fail_ere=ERE (the bench prints it on ANY abnormal exit; ends the window early)
STATUS (the bench polls by reading): /home/pcrec/projects/pcrec/worktrees/.boxqueue/reservations/<prio>-bench-<name>.state, ONE line, rewritten in place atomically (write tmp + mv):
  QUEUED <iso> | RUNNING <iso> <pid> | DONE <green|red|failed|cancelled> <iso> <reason>
  The bench starts its runner only on RUNNING. Lock held <=> state RUNNING (write RUNNING only after the lock is taken; write DONE before releasing it).
PLACEHOLDER ENDS: done_ere line with N == expect -> DONE green; N != expect -> DONE red POPULATION; fail_ere line -> DONE failed BENCH-FAIL; the log does not grow within start_s of RUNNING -> DONE failed NO-START (a log that exists at RUNNING is fine: its byte size is the offset and only appended bytes are scanned, R1.1/R1.2); cap -> DONE failed CAP-FIRED (lock released). The bench stops its window when the state leaves RUNNING.
CANCEL: <inbox>/<name>.cancel -> DONE cancelled (if RUNNING: lock released). Withdraw = the .window deleted before import. Import is once per name (a re-used name is refused/ignored with a log line; record imported names).

## Reasons written (the exact DONE reason text the bench will see)

- green: `WINDOW-COMPLETE n=N`; red: `POPULATION n=N expect=M`; failed: `BENCH-FAIL`, `NO-START (LOG did not grow within Ns of RUNNING)`,
  `CAP-FIRED (CAPs)`, `TERMINATED (after Ns, before the cap)` (an external kill), or boxqueue's own
  reason when the placeholder could not write DONE itself (runner died, killed hard; `bench_reconcile` writes it);
  `IMPORT-REJECT <reason>` for a refused window (exact line `DONE failed <iso> IMPORT-REJECT <reason>`; the log line says REJECTED); cancelled: `CANCELLED by the bench` (or boxqueue's reason if cancelled by hand).

## QUESTIONS FOR THE BENCH / MAIN (defaults chosen where the contract was silent; none is irreversible)

1. REJECTED windows: the contract has no word for a refused `.window`. Chosen: the importer logs it and, when name and
   prio are usable, writes `DONE failed <iso> IMPORT-REJECT <reason>` (R1.3/R2) so the bench does not wait forever. A rejected
   file may be fixed and rewritten under the SAME name (it was never imported; each distinct file content is judged once).
   Only an IMPORTED name is once-only. OK?
2. The `.window` file name must equal its `name=` key (the cancel file is `<name>.cancel`). Rejected otherwise.
3. Names containing `--` are rejected (a queue job name cannot hold `--`); the contract's regex alone allows it.
4. `log` is further limited to letters, digits, `_ . / -` (no spaces), no `..` component; the bench's own log path
   fits that today?
5. (R2: STALE-LOG is gone.) A pre-existing log is allowed; its size at RUNNING is the offset, only later bytes are scanned.
6. `patience` is DECLARED ONLY (R2): it is shown in `plan` and bounds nothing; there is no auto-withdraw of a queued window.
7. Atomic writes: the importer waits until a `.window` has been unmodified for `BOXQUEUE_WINDOW_SETTLE` s (2) as a guard
   against reading a half-written file; the bench should still write temp + `mv`.
8. (R2) Import and `.cancel` are acted on WHILE a job runs, see the R2 section.
9. `start_s` is measured from RUNNING (not from the bench's runner start): the bench's log must grow within
   start_s of seeing RUNNING.
10. Imported names are recorded in QUEUE/.bench/imported (queue-local); wiping the queue dir forgets them.
11. S1610-S1618 are used as in-test plant labels in boxqueue.test (not rows in the mech matrix).

## R2 (applied in this follow-up lane benchres2)

- STALE-LOG dropped. The placeholder records the log's byte size at RUNNING (0 if absent; reset to 0 if the log later
  shrinks) and scans only `tail -c +OFFSET+1` of it for fail_ere/done_ere. start_s = the log must grow past the offset.
- Verdict isolation: the declared expect no longer carries `log=BENCHLOG` (it would have made the runner's
  finalization read the whole bench log: a stale done line or a red line from an earlier run could turn a good window
  red). The placeholder echoes the last done_ere line of the appended bytes to its own log; pop_check reads that.
- Reject wording: `DONE failed <iso> IMPORT-REJECT <reason>`; patience/start_s missing = a reject (tested).
- Mid-job import and cancel, WITHOUT a structural change: the runner blocks in `cmd__start`'s `wait` on the job, but
  that function already runs a POPULATION-OVER watcher subshell that wakes every `BOXQUEUE_MONITOR` s (2). It now also
  calls `bench_sync` every `BOXQUEUE_BENCH_EVERY` s (15, must stay <= 60). `bench_sync` (import + `bench_cancel_queued`
  + reconcile) is serialised by a non-blocking flock on QUEUE/.bench/.sync.lock (a second caller skips), and is also
  called by `status` and `plan` (R1.3). `bench_cancel_queued` ends a pending bench job whose `.cancel` exists
  (`end_pending ... done`), then reconcile writes DONE cancelled. A cancel of a RUNNING window is the placeholder's own
  poll (BOXQUEUE_WINDOW_POLL, 2 s). Worst case for a new `.window`: settle (2 s) + 15 s + monitor tick.
- Tests (boxqueue.test 25f, 25k, 25q): stale done line does not end the window; no growth -> NO-START; a .window dropped
  mid-job is QUEUED while the job still runs; a mid-job .cancel of a queued window is honoured; patience/start_s missing
  rejected; IMPORT-REJECT wording. Plants S1615 (offset ignored), S1616 (growth not required), S1617 (no mid-job sync),
  S1618 (queued-cancel step dropped); S1612 now plants out both cancel paths.
- Full file: `boxqueue.test: 120 passed, 0 failed` (was 113; the watcher first used integer arithmetic on BOXQUEUE_MONITOR, which tests set fractionally, and broke the POPULATION-OVER case; it now uses $SECONDS).
- Known edge: the first appended line is concatenated to a pre-existing last line that lacked a trailing newline.

## Not done / caveats

- Nothing run on the live queue; every test is a scratch queue + scratch inbox + a fake bench runner.
- Process note: an accidental empty `/tmp/dummy` was created by a mistyped command and removed at once.
