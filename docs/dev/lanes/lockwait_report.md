# lockwait report

## Summary
Box-lock waiters are now visible three ways: `scripts/boxlock status` lists every waiter (label, pid, cwd, since, minutes waited; YIELDING vs WAITING), `scripts/queuewatch` raises `WAIT-LONG LABEL pid=N waited=Mm holder=H` once per waiter past `--wait-long-sec` (default 1800), and `scripts/lanewatch --follow NAME` prints `WAITING NAME label= waited= holder=` (rc 14) instead of QUIET when the lane has a live waiter. Self-tests are green with planted controls (boxlock.test 35/0, lanewatch.test 13/0, queuewatch.test 54/0). The live lock and queue were never touched.

## What was built
- Source choice: a waiter-written registry, `<lock dir>/.box.lock.waiters/PID`, rather than /proc. A waiter's flock(1) child shows neither label nor start time, so /proc cannot name the run or tell YIELDING from WAITING. The record carries pid + /proc starttime like the owner line, so a SIGKILLed waiter's record is dead on read and pruned (`status`/`waiters`); removal on acquire and via an EXIT trap otherwise. The flock acquire protocol is unchanged (the record is written beside it, never consulted by it; a failed write is ignored), so the STOP RULE did not fire.
- `boxlock`: `status` prints the holder line (exit codes unchanged) then `  WAITING|YIELDING label= pid= cwd= since= waited=Mm [on=JOB]`; new `boxlock waiters` machine form with `holder=`.
- `queuewatch`: `--wait-long-sec`, WAIT-LONG, once per waiter (episode = pid+starttime, a 3 h wait is one alert; repeats per multiple of the threshold were not built, one line to add). Lock found via PCREC_BOXLOCK_FILE else `<queue dir>/../.box.lock`, so scratch queues are isolated. Header and `.claude/skills/pcrec-monitor/SKILL.md` row 9a (WAIT-LONG goes to the waiter's owner as PROBLEM).
- `lanewatch --follow`: WAITING branch (label is NAME or `NAME-...`, or cwd under the lane worktree), rc 14, header documents it.
- Docs: script headers, scripts/CLAUDE.md (kept under 4 KB), scripts/NOTES.md entry, BOILERPLATE line to label runs `<lane-name>-<what>` (BRIEF_TEMPLATE had no boxlock text; BOILERPLATE carries the rule). Also fixed a latent lanewatch.test leak (`LWX=... out=$(...)` persisted the plant variable).

## Self-tests
All on scratch locks/queues under `build/scr`; run as `bash scripts/tests/NAME.test` with TMPDIR in the worktree.
- boxlock.test section 8: one holder + two waiters listed with durations; machine lines carry kind/pid/start/label/holder; a dead pid's record pruned; records removed on acquire; a waiter behind a ready queue job reads YIELDING on=JOB and its refusal cleans its record. PLANTs: no pruning (ghost listed), no registration (waiter unlisted).
- queuewatch.test (end): WAIT-LONG fires with label/pid/minutes/holder, is not repeated on relaunch, does not fire below the threshold. PLANTs: threshold ignored, state not written.
- lanewatch.test (end): `x-chain` waiter gives WAITING rc 14; another lane's waiters give QUIET; `xy` does not match `xylo-chain`. PLANT: WAITING branch dead gives QUIET.
- Results: boxlock.test 35 passed 0 failed; lanewatch.test pass=13 fail=0; queuewatch.test 54 passed 0 failed.

## STATE AT HANDOFF
Committed on lane/lockwait. Validation COMPLETE, nothing owed. Rulings file had no entries ("none yet") at each re-read. Not run: make test (out of scope). Known gap: no flock(1) (Mac) means no registration, those runs are unlocked anyway. Merge note: the monitor skill and BOILERPLATE edits are one line each.
