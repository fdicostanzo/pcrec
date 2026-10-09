# mechpar STEP 1 -- why named-row mech runs look serial (measured)

Run: `env PROCS=4 bash tests/mech/run_sabotage_matrix.sh S159 S166 S169 S178
S193 S224 S253 S257 S261 S306 S40 S423` at f27ff639, pinned `taskset -c 0-7`
(so nproc=8, INNER_PROCS=2), under scripts/watchdog, process state sampled
every 3 s. Wall 1223 s (20.4 min).

## Finding: head-of-line blocking in the row throttle

The PROCS>1 dispatch (run_sabotage_matrix.sh, "run all requested
sabotages") launches rows in the background and, once `PROCS` are running,
`wait`s on `pids[0]` -- the OLDEST row -- before launching the next. It
never asks which row finished. So one slow row at the head of the list holds
every slot closed after the other three finish.

Row launch times (s from start) vs sampled load:

    t=4     S159 S166 S169 S178 launched (4 rows, load climbs to 25-34 on 8 cpus)
    ~300    S166 S169 S178 finished; load falls to ~1, R=1
    300-755 ONE process: S159's recursion suite (tests/recursion/
            run_recursion_diff.sh, a single-threaded per-case loop, ~12.5 min
            alone). `ps --forest` shows only that row alive; 8 rows unlaunched.
    755     S159 finishes; S193 S224 S253 S257 launched together
    1040    S261 S306 S40 S423 launched
    1223    done

Mean sampled load 9.7 on 8 cpus overall, but 755 of 1223 s (62 %) was spent
at load 1-2 with a single row alive. This is exactly B5's/B4's shape (S159
heads the list; 6 rows in ~10 min, load1 ~1). It is NOT: the reach probe
(runs once, ~4 s clean build), `git archive` + build (seconds), or PROCS
not reaching the dispatcher.

Secondary: while 4 rows overlap, load reaches 25-34 on 8 cpus (4 rows x
JOBS=2 builds x INNER_PROCS=2 sharded suites, and harness arms that spawn
more); oversubscribed but not wasteful. Out of scope here.

Control verdicts (PROCS=4, old throttle): verd_p4 = 11 DETECTED, S178
UNDETECTED (EXPECTED).
