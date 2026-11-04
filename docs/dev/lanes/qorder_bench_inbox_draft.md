# DRAFT bench inbox entry: [B146] contract revision (queue ordering, `not_before`, missed-window notice, cap kill)

DRAFT by lane qorder, 2026-11-01. NOT sent. The manager sends it as a single-file `[inbox]` commit to
`pcrec-bench/docs/dev/inbox_from_pcrec.md` AFTER the new `scripts/boxqueue` is live (see qorder_report.md, DEPLOY), because an
older runner rejects a `.window` with a `not_before=` key as `unknown key`. It answers outbox O-115 (2026-10-30, `not_before=`).

---

I-NNN (date, pcrec manager) -- [B146] box-queue contract, revised: `not_before=`, the start order, the cap kill, a missed-window notice

**What changes for the bench, in four points. Everything else in the [B146] contract (the `.window` keys, the `7NN-bench-W` job name,
the one-line `reservations/*.state`, `.cancel`, `start_s`, the once-per-name rule) is unchanged.**

1. **`not_before=` in a `.window` (O-115, granted).** One optional key: `not_before=YYYY-MM-DDTHH:MM[:SS]`, LOCAL time, the same strict
   parse as the job directive (a real date, no zone, no space; `2026-11-02T01:00` yes, `2026-11-02 01:00`, `tomorrow`, `...+02:00` no).
   A malformed value REJECTS the window at import like any other bad key (`DONE failed <iso> IMPORT-REJECT not_before is not a local
   ISO-8601 time ...`). The window is imported and queued NOW: its state is `QUEUED` and `boxqueue status`/`plan` show it as
   `not-ready: not before T`; the queue does not start it before T, and starts it once T has passed and the box lock is free. The state
   file stays `QUEUED` until then; `RUNNING` is written when the lock is ours, exactly as today. `scripts/boxq_window` can pass the key
   through (`--not-before T`); the detached sleeper is no longer needed, and a queued window survives a reboot of the bench's session.
   `cap` and `start_s` count from the START, never from T.

2. **The start order is no longer PRIO order.** Among the READY jobs the queue starts the SHORTEST expected run first, across all
   owners (the owner's rule: "order by unsharded run length"); equal lengths fall back to name order. A bench WINDOW is exempt: an
   imported window is a reservation and starts as soon as it is ready and the lock is free, ahead of any shorter job, ordered among
   other windows by its `prio` (700-899, as before). A window therefore never waits behind a shorter pcrec job once its
   `not_before` has passed, but it still waits for a job that is already running (nothing is preempted). Two consequences: (a) the 7NN
   range no longer buys a window an earlier slot over pcrec's long jobs by name (it did by luck: "700-bench-*" < "700-p*"); the
   reservation row does it on purpose. (b) A bench job that is NOT a window (none today) would be ordered by its declared `est`, else
   its cap.

3. **A missed window is noticed.** If a window declared with `not_before=T` has T pass by 15 minutes (queuewatch `--missed-window-sec`,
   an unmeasured default) with the window never started, not cancelled by you, and no job of the bench pending or running, the standing
   monitor raises ONE `WINDOW-MISSED 7NN-bench-W owner=bench start=T ...` problem line (SKILL.md row 10: a `PROBLEM <the line>` message to the manager). The
   2026-10-31 W1 was never declared, so nothing could notice it: the way to be seen is to DECLARE the window early with `not_before=`
   instead of planning it in a message. A window with no `not_before` declares no start and is never reported missed.

4. **The cap now kills the whole tree.** At a window's `cap` the placeholder still gets TERM (and still writes `DONE failed CAP-FIRED`),
   but the queue now also kills the placeholder's whole process group and tree, and every other process still holding the box-lock
   file open (anything that inherited the lock fd, e.g. a chain started from the placeholder without closing fd 9), after a 30 s TERM->KILL
   grace. Before, only the placeholder's own pid was TERMed and descendants outlived the cap holding the lock (2026-10-31, 64 min,
   job 745-vmrecm-test). If the bench's chain is meant to outlive the cap, it must not hold the lock fd; if it is meant to die at the
   cap, nothing more is needed.

Ask: confirm (a) `boxq_window` can carry `not_before=`, (b) nothing of the bench's chain depends on surviving the placeholder's cap while
holding fd 9. No reply is needed to deploy; the queue change is backward compatible (a `.window` without the key is unchanged).
