# monci report (2026-10-24): CI events in queuewatch + monitor preflight

Premise test: `gh run list --branch main --limit 5 --json databaseId,headSha,status,conclusion,createdAt,displayTitle` works here and shows recent runs (fields suffice to tell a superseded cancel from a newest one).

## Built
- scripts/queuewatch: CI source (`--ci-every S`/env CI_EVERY default 300, persisted across launches; `--no-ci`/env QUEUEWATCH_NO_CI). Events CI-RED (failure, timed_out, startup_failure), CI-CANCELLED (newest completed run cancelled AND no later run still running/queued; a deferred cancel is not reported, and a later green or red supersedes it), CI-UNAVAILABLE <reason> (once per episode, re-armed on recovery). Baseline = first SUCCESSFUL gh answer. Same state file; the last answer's events are cached in state.ci.out so two events from one answer both surface without re-asking gh.
- scripts/monitor_preflight (+ --root, --box, --no-ci), prints PASS/FAIL/SKIP lines and `monitor_preflight: DONE rc=N`; changes nothing (queuewatch checked against a scratch empty queue + scratch state).
- Skill: pcrec-monitor STARTUP section, MANAGER variable, rows 11-13 (CI-RED, CI-CANCELLED, CI-UNAVAILABLE); pcrec-test note; scripts/CLAUDE.md, scripts/tests/CLAUDE.md.

## Results (all run by me)
- scripts/tests/queuewatch_ci.test: 5 passed, 0 failed. Scenarios: baseline silent; red once; cancelled-then-green silent; cancelled with later in-progress deferred then only the later CI-RED; cancelled-newest CI-CANCELLED once; two events in order with gh asked once; unauthenticated CI-UNAVAILABLE once + DISK-HIGH still arrives, re-armed after recovery; gh missing (PATH without gh); --no-ci; baseline after a down first launch. Plants all red: state not written, baseline skipped, cancelled without the newest test, unavailable never re-armed.
- scripts/tests/queuewatch.test (now with the CI source off): 16 passed, 0 failed.
- scripts/tests/monitor_preflight.test: 7 passed, 0 failed (clean, gh missing, --no-ci, unauth, no repo run, no git identity, plant).

## Preflight on this box
```
PASS bash: GNU bash, version 5.3.9(1)-release (x86_64-pc-linux-gnu)
PASS git: git version 2.53.0
PASS flock: /usr/bin/flock
PASS timeout: /usr/bin/gnutimeout
PASS df: /dev/nvme0n1p4  1006435104 333412004 621825304      35% /
PASS queue-dir: /home/pcrec/projects/pcrec/worktrees/.boxqueue
PASS runner-state: runner: live pid=3716237 start=68811635 since=2026-10-24T09:35:43-04:00
PASS ledger-writable: /home/pcrec/projects/pcrec/worktrees/monci/docs/dev/full_suite_ledger.md
PASS committable: Frank DiCostanzo <frank@dicostanzo.com>, HEAD 404d56f84
PASS python3: python3 ok
PASS gh-installed: gh version 2.46.0 (2025-12-13 Ubuntu 2.46.0-4)
PASS gh-auth:   ✓ Logged in to github.com account fdicostanzo (/home/pcrec/.config/gh/hosts.yml)
PASS gh-repo: https://github.com/fdicostanzo/pcrec.git
PASS gh-runs: [{"conclusion":"","databaseId":40098484432,"status":"in_progress"}]
PASS queuewatch: exits 6 CAP, no event (scratch queue and state)
monitor_preflight: DONE rc=0
```

## Notes
- queuewatch needs python3 for CI parsing (preflight checks it).
- The test plants live briefly inside scripts/ (.queuewatch_plant_*, removed by trap) so siblings stay reachable.

## STATE AT HANDOFF
Branch lane/monci, all committed, not merged. Rulings file empty (no entries applied). Nothing owed. Live queuewatch state and queue untouched.
