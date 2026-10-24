# qwquiet2 report (sonnet lane, branch lane/qwquiet2, not merged)

Files: scripts/queuewatch, scripts/tests/queuewatch.test. No runner change.

1. QUIET read the wrong log. Growth now counts ANY file in the started job's dir (size+mtime; not the runner's idle/idle.seen).
   Chosen over the declared `expect ... log=` file because it needs no parsing of dry.log, covers job.log.make, perfrun side
   files and any future log shape. CPU did not count because perfrun jobs have no logdir/battery.pid, so only the
   battery.pid tree was ever sampled. Now the job's own `pid` file tree is sampled too, as a RATE (>= 5% of a core over the
   interval since the last look; 5 = boxqueue's IDLE_TREE_PCT, unmeasured here, env QUEUEWATCH_CPU_PCT): an exact-change test
   on that tree is defeated by the wrapper's own wait loop (fullsuite_job's grep+sleep forks), found when the simulated quiet
   scenario stopped going QUIET. battery.pid keeps its exact-change test (existing fork-loop case).
2. QUIET while pending: the runner makes running/NAME, tries the box lock and removes it again if held. QUIET now requires
   running/NAME/started. `started` content is in the signature so a new run is a new episode.
3. PENDING-STUCK age: counted from ready_since (queue.log: the `== pass N START <ts>` of the job's first non-not-ready
   answer after its add / last not-ready), only when the job's latest answer is not not-ready; the line then reads
   `pending for Ns, nothing running (queued Qs ago, ready for Ns)`. No ready record: the old queued-age fallback.

Tests: 10 new cases (3 QUIET-log incl. control and wrapper-poll, unstarted, 2 stuck, 3 plants). All new cases FAIL on main's
queuewatch (verified: 5 FAILs) and pass now. Whole file run 3 times (in parallel, separate TMPDIRs): 33 passed, 0 failed each.
Skill pcrec-monitor: unchanged (relays the line verbatim).
