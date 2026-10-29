# pcrec-test monitor rules (first match wins; each fix at most ONCE per run)

SUPERSEDED 2026-10-24 by .claude/skills/pcrec-monitor/SKILL.md (scripts/queuewatch). Rows 1/5/6 below assume a
watchrun that fires on battery stage ENDs and keeps no state across relaunches; kept as the older per-run table.

| # | you see | do | then |
|---|---|---|---|
| 1 | watchrun exits with no line (its cap) | loop again | — |
| 2 | the job is PENDING and `scripts/boxqueue status` shows no runner | `bash /home/pcrec/projects/pcrec/scripts/boxqueue start` | if still no runner after 5 min: PROBLEM |
| 3 | the job is PENDING, not ready, for over 60 min | read the not-ready reason from `boxqueue status` (one line) | PROBLEM with that line; keep looping |
| 4 | `df -h /home` above 95% at any check | nothing | PROBLEM; keep looping |
| 5 | a stage END with rc=0 | nothing | keep looping |
| 6 | the FIRST stage END with rc != 0 | launch ONE triage agent: `model: sonnet`, background, NO name (a teammate cannot spawn named agents), prompt = "TRIAGE <KEY>: read /home/pcrec/projects/pcrec/.claude/skills/pcrec-test/triage_brief.md and follow it. LOGDIR=<dir of TRAILER>; stage=<name>." | message the manager "MON <KEY>: stage <name> RED, triage launched; its table: /tmp/claude-1001/<triage dir>/triage.md"; keep looping |
| 7 | a later red stage | append its name to `<LOGDIR>/red_stages.txt` (the triage lane reads it) | keep looping |
| 8 | QUIET, DIED, LOCK-ORPHAN, FAILED-FAST, CAP-FIRED | nothing (never kill, cancel or retry) | PROBLEM with the line; QUIET: keep looping; the rest: END after the message |
| 9 | BATTERY DONE / the job's DONE line, all stages green | append SUMMARY's line under "## Runs" in LEDGER; `git -C /home/pcrec/projects/pcrec commit -m "ledger: full suite green <sha>" -- docs/dev/full_suite_ledger.md` (named path only) | message "MON <KEY>: GREEN <summary line>"; END |
| 10 | DONE with any red stage | append SUMMARY's line under "## Runs" in LEDGER (marked RED), commit as in 9 | message "MON <KEY>: RED <summary line>; triage tri-<KEY>"; END |

PROBLEM = one SendMessage to the manager: "MON <KEY> PROBLEM: <one line>".
Never more than one message per row firing. Never read stage logs.
