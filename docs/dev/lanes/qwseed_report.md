# qwseed report: queuewatch first-launch seeding ([MONITOR-QUEUE])

Cause: a START line is logged every time a not-ready job is put back to pending (live: 342 STARTs, 151 ENDs; 33 for 200-reachonly-reach). The old code paired the k-th START with the k-th END, so only the first START(s) of an ended job read "closed" and the rest were seeded as news. The same pairing also mis-mapped START/END to run dirs.

Rule (scripts/queuewatch, `start_runs` + `lifecycle`): a START is REAL if followed by its END or last in the log for that job; a START followed by another START is an abandoned attempt. The first launch marks EVERY event seen (all STARTs, ENDs, "ended without running", old trailers) except the run in progress: the job's last START with nothing after it while `running/NAME` exists, plus that run's stage ENDs. So a job running at first launch still yields its START, later STAGE-ENDs, JOB-DONE. Run k = k-th real START and k-th END = k-th of job_dirs (fixes the dir mapping too). Other kinds: END and "ENDED WITHOUT RUNNING" are only ever historic at seed time (marked); stage ENDs are keyed logdir|stage|rc and belong to a real run. A pending job's trailing START is history. No state-format change (IDs unchanged).

Checks: live queue read-only, scratch state: first launch reports only `JOB-START 620-kit-s3-heavy` (the running job), nothing historic. queuewatch.test 18/18 (new hand-built restart-history case + plant old-seeding goes red), queuewatch_ci.test 5/5, monitor_preflight.test 7/7. Live state/queue untouched. Existing live state needs no change.

STATE AT HANDOFF: lane/qwseed committed; rulings file empty (no rulings applied). Not merged.
