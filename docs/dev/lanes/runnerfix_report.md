# runnerfix — the box queue runner must not skip a job silently, and must notice its script changed

Lane runnerfix (sonnet, 2026-10-21), branch `lane/runnerfix` from main 83ff3efad.
Scripts and docs only; nothing under `src/`, no abi event.

## Premise test (done first)

Confirmed in `scripts/boxqueue`. `pass()` did `if ! ensure_decl ...; then rm -f "$s"; continue; fi`.
`ensure_decl` logs when a job fails on FIRST sight (it calls `end_pending`), but its last line,
`parse_decl "$st/$k.decl"` (the cached declarations a new script's `add` wrote), returned the
parse failure with nothing logged. A runner that predated the `idle-ok` grammar therefore
rejected the job's recorded `idle-ok` line on every pass and `continue`d silently. `status`
prints `.state/KEY.answer`, which that path never wrote, hence "not asked yet". The kit's
diagnosis holds: both causes (silent skip, runner running stale in-memory functions).

## What changed

- **No silent skip.** Every way `pass()` passes over a pending job logs one line naming the
  job and the reason and writes the same text to `.state/KEY.answer` (and the pass's status
  file), so `boxqueue status` shows it in place of "not asked yet". Two paths: the recorded
  declarations are unreadable by this runner (`SKIPPED: cannot become runnable under this
  runner (pid N): <the parse error>`; the job stays pending and says so every pass), and the
  pending file vanished before its snapshot. First-sight failures already ended the job in
  failed/ with a log line and are unchanged.
- **Self-change.** `reexec_if_changed` hashes `$self` at runner start (`SELF_SHA`). At the top of
  each pass, if the content differs and `running/` is empty (never mid-job), it `exec`s
  `bash $self run <same args>`: same process, so the same runner lock (fd 8 inherited; the new
  copy re-checks it with `flock -n 8` instead of reopening) and the same log. One line
  `== runner RE-EXEC at pass N: ... (sha a -> b)`, then `== runner RESUMED after RE-EXEC`. The pass
  counter continues. A new script that fails `bash -n` is refused once (logged) and the running
  copy carries on. Header comment updated.
- **STOP RULE checked:** re-exec cannot drop or duplicate pending state. All of it is on disk
  (`pending/`, `.state/` keyed by content sha), no job is running at the point of exec, and the
  self-test proves the second pending job is untouched and the lock survives.

## Validation

`scripts/tests/boxqueue.test`: 79 -> 86 checks. Full run 1 (`build/bqtest.log`, TMPDIR under the
worktree's `build/`): 86 passed, 0 failed. Case 24:

| check | planted failing direction |
|---|---|
| a stale-grammar runner skips a job: one log line naming job and reason, status shows it, job still pending | silent skip planted back: nothing logged, status reads "not asked yet" |
| script replaced on disk between passes: one RE-EXEC line, same pid, then the job only the new grammar accepts runs green | `reexec_if_changed` never called: the job is never recovered |
| runner lock survives the exec (a second runner is REFUSED 75), other pending job untouched | (same case) |
| negative: script replaced while a job is running in `running/`: no re-exec until it is gone, then one | running-job guard removed and the check hoisted above `recover`: it re-execs mid-job |

The stale-grammar runner is the real old parse_decl planted back into a scratch copy (the
`idle-ok` case label renamed), fed a job added by the real script. On review of run 1 the silent-skip plant check had a shell precedence slip
(`A || B && ok` passed whenever the log held SKIPPED); it is fixed to
`! has SKIPPED && status shows 'not asked yet'`. THE FIXED FILE'S FULL RE-RUN IS OWED: it was
started, ran clean (0 FAIL) up to the `--ready` hang case, and was stopped at the manager's
17:3x HOLD (rulings entry 1) before reaching case 24. Command, when 560-kit-e8-window is gone:
`TMPDIR=<worktree>/build/tmp gnutimeout 900 bash scripts/tests/boxqueue.test > build/bqtest3.log 2>&1`
(~3.5 min, light, one job at a time); expect `boxqueue.test: 86 passed, 0 failed`.

## STATE AT HANDOFF

Delivered; ONE run owed (above). The LIVE queue and its runner were not touched; the live runner is
still the old copy, so it picks this up only when it next restarts (the new code cannot re-exec
a runner that lacks it). Rulings file `runnerfix_rulings.md`: last entry applied: 1 (the HOLD; the
run in progress was stopped by safekill and nothing multi-core was started after).
