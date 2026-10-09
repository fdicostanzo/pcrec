# mechpar report ([TT-MECHPAR])

## Finding (measured; docs/dev/lanes/mechpar_profile.md)
The PROCS>1 row dispatch in `tests/mech/run_sabotage_matrix.sh` throttled by
`wait`ing on the OLDEST row's pid. A slow row at the head of a list
(S159, recursion suite, single-threaded, ~12.5 min) kept all slots closed
after its companions finished: one process alive, load ~1. Not the reach
probe, not git archive/build, not PROCS plumbing.

## Fix
Slot pool: `while [ "$(jobs -pr | wc -l)" -ge "$PROCS" ]; do sleep 0.2; done`
before each launch. bash 3.2-safe (no `wait -n`). Per-row scratch trees
(MECH-2), D45 budgets, JOBS/INNER_PROCS (= ncpu/PROCS) and merged
listing-order output are unchanged, so rows x INNER_PROCS <= nproc already
holds; no new constant. The default PROCS is untouched (1 for the script,
nproc for `make mech`); the 0.2 s poll is a latency bound, not a tuned value
(rows run seconds to minutes).

## Timing (12 rows S159 S166 S169 S178 S193 S224 S253 S257 S261 S306 S40
S423, `taskset -c 0-7`, PROCS=4, f27ff639 + docs commits)

| scheduler | wall | rows' verdicts |
|---|---|---|
| old FIFO | 1223 s (62 % at load 1-2, one row alive) | 11 DETECTED, S178 UNDETECTED (EXPECTED) |
| slot pool | 792 s (floor = S159 ~750 s) | identical (diffed) |

Row launches, old: 4 rows at t=4, next 4 at t=755, last 4 at t=1040. New: all
12 launched by ~t=300. Mean sampled load 9.7 (old) vs 27.8 (new) on 8 cpus:
the new run is oversubscribed at 4 rows x inner arms on the 8-cpu pin; on
the 16-cpu box INNER_PROCS is 4 at PROCS=4 so the shape is milder. If a
heavy run shows timeouts from that, the answer is a lower PROCS, not this
scheduler (not evidenced here).

## Owed: the full-size acceptance (HEAVY), ARMED on .lift
`docs/dev/lanes/mechpar_chain/chain.sh`: B5's 71 rows
(`rows.txt` = decfbB5_report.md's 34 re-run + 4 re-aims + 10 fbt + 23
state-write rows, 71 distinct, all exist) at PROCS=4 then PROCS=1, same HEAD,
verdicts diffed. Arming: `touch worktrees/mechpar/.lift` after the waiter is
up. Logs: `worktrees/mechpar-scratch/chain/chain.log`. Completion line:
`mechpar chain COMPLETE`, preceded by `VERDICTS IDENTICAL (71 rows)` or
`VERDICTS DIFFER`. Compare PROCS=4 wall to B5's 42 min (old, same list) and
B4's 36 min. Expect ~ (sum of row work)/4 bounded by the slowest row;
the serial arm may take hours. Commit nothing while it runs.
A diff between arms in a count-bearing column (e.g. S18's reject shards+1,
K30) is not a verdict difference; verdicts.sh compares the last column only.
