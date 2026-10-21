# watchidle report — [WATCH-IDLE] (2026-10-21, lane watchidle, sonnet)

Scripts and docs only: `scripts/boxqueue`, `scripts/tests/boxqueue.test`,
`docs/dev/lanes/BOILERPLATE.md` (Queue template), `scripts/CLAUDE.md`,
`scripts/tests/CLAUDE.md`, plan row moved to `plan_completed.md`.

Premise test: `scripts/tests/boxqueue.test` at 15745b324 passed 53/53.
Final: 79 passed, 0 failed (run with `TMPDIR` inside the worktree; the test's
own mktemp otherwise lands in /tmp). `scripts/tests/watchrun.test` 17/17
(watchrun itself is unchanged). Every self-test runs in a scratch queue dir
under the worktree, never the live `worktrees/.boxqueue`.

STOP RULE: the new grammar gates `add`, `retry` and `batch` only. A job already
pending, or dropped into pending/ by hand, is read with the older lenient
grammar (bare `expect none` accepted, no witness needed), so no queued job
changes how it runs; `boxqueue --dry-run` marks such a job LEGACY. The idle
alarm is new runner behaviour but is advisory (it logs, it never kills), so it
changes no job's outcome; it does add ` idle=SUSPECT` to a flagged job's result.
Consequence to relay: other sessions' next `add`/`retry` of a bare `expect none`
or a `last=` without a witness is refused with the valid forms printed.
`boxqueue batch`'s generated jobs now declare `expect none reason=chainrun
stage: ...exec'd` (they are exec'd, so the stage rc is the job rc).

| shape | detector | plant (goes red) | result |
|---|---|---|---|
| 1 rc swallowed, `expect none` read GREEN | bare `none` refused at enqueue (65); `expect none reason=WHY` required; refusal prints the valid forms | `bare-none`: gate off, the rc-swallowing job scores GREEN | refused; accepted with a reason; plant caught |
| 2 tool's own log read as job.log | `expect NAME=N log=PATH lines=\|last=ERE`; default job.log; relative = run dir; a RED line in a named log fails the job; a SHORT now says why (log missing / matcher never matched / no integer) | `log-ignored`: every population read from job.log, the green 73/73 run reads SHORT | `log=job.log.make` reads 73 of 73 green; the control without it reads SHORT with the reason; plant caught |
| 3 count its own matcher cannot produce | a `last=` expect needs `boxqueue: witness NAME=LINE`; the dry run reads N back from the witness with the same matcher; an ERE ending in `$` or not compiling is refused | `no-witness-read`: read-back off, the manager's 120 shape accepted and reads SHORT | `last=^== postmerge COMPLETE` refused ("reads 'none' from the witness line"); no witness, `$`-ending and invalid ERE refused; a correct form accepted; plant caught |
| idle-box alarm | per job, beside the work: every `BOXQUEUE_IDLE_SAMPLE` s sample box CPU, the job's process tree (session + descendants by exact /proc walk) and its logs' size; idle for `BOXQUEUE_IDLE_WINDOW` s writes one IDLE-SUSPECT line to queue.log and `status`, marks the result, never kills; IDLE-CLEARED on resume; a foreign lock holder blocking a pending job is sampled once per pass (HOLDER-IDLE-SUSPECT) | `alarm-silent` (never raised), `no-tree-cpu` (a one-core busy loop falsely flagged), `no-log-growth` (a chatty job flagged) | quiet job flagged in `status` while running and in queue.log, ended green with idle=SUSPECT; negatives not flagged: `idle-ok`, `idle-ok 60`, one core at 100%, a busy child process, a chatty log, a busy foreign holder; all three plants caught |

Defaults (ALL UNMEASURED, env-tunable, labelled so in the alarm line): window
600 s, sample 15 s, box busy < 5%, tree < 5% of ONE core, no log growth.
Idle means ALL of them quiet, so a job with a busy tree is never flagged
however small its share of a 16-thread box (one core is about 6%), and a quiet
job on a box someone else is loading is not flagged either (the cost of
requiring the box to be quiet too, as the brief wrote it). iowait counts as idle
(the ghostty phantom). Tests push the window to 3 s and the box threshold past
100 so only the tree and logs decide.

Not built (outside the four asks; file when seen): a chain waiting on a `.lift`
nobody touched, a lock holder with no queue job waiting, a queue with pending
jobs and no runner, a lane's OWED chain never armed. The first two are watchrun's
(QUIET, LOCK-ORPHAN) territory.

## STATE AT HANDOFF
Committed on lane/watchidle (not merged). Rulings file
worktrees/watchidle/docs/dev/lanes/watchidle_rulings.md: "(none yet)" at the last
re-read. Validation complete: boxqueue.test 79/79, watchrun.test 17/17,
`scripts/plan_lint.sh` 0 violations. Nothing owed. The kit and bench jobs that
declare a bare `expect none` need `reason=` on their next add/retry.
