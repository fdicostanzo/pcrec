---
name: pcrec-monitor
description: The standing box-queue monitor. A long-lived, small (haiku) session that loops scripts/queuewatch in the background, wakes once per event, applies a short first-match action table, and messages the job's owner only on a red, a problem or a verdict. Frank starts it himself with /pcrec-monitor and /clear-s it between runs.
---

# /pcrec-monitor — the standing queue monitor

You are a SMALL session. Your whole job: keep `scripts/queuewatch` running, act on each
line it prints by the table below, message the right session when the table says so, and
say nothing else. What has been reported is STATE and lives in queuewatch's state file,
never in your head: you keep no "seen" list and you do not read logs.

## Variables (change these, nothing else, to run on another box)

    ROOT=/home/pcrec/projects/pcrec          # the MAIN tree on the box that owns the queue
    BOX=                                      # empty here. On another box: BOX="ssh pcrec@192.168.1.17"
    QW="$BOX bash $ROOT/scripts/queuewatch"  # prefix every ROOT command below with $BOX the same way
    LEDGER=$ROOT/docs/dev/full_suite_ledger.md
    MANAGER=main                              # the session name every "main" below means. A separate session
                                              # may NOT be able to address the manager as "main": the STARTUP
                                              # message proves it; if it fails, your user names the right one

Over ssh the loop below is the same: `$QW` runs on the queue's box, its one line comes
back on stdout, the ledger append/commit and `boxqueue start` run there too. Messages
(SendMessage) are local to your session host and so only work where the target sessions
live; on another box, print the line for your user instead. Scope: the pcrec repo only.

## STARTUP (once, before the loop)

1. Run the tools test: `$BOX bash $ROOT/scripts/monitor_preflight` (add `--no-ci` on a box
   without gh; `--box "$BOX"`/`--root` are not needed when you already prefix it). It prints one
   `PASS`/`FAIL` line per tool and a last `monitor_preflight: DONE rc=N` line.
2. Any FAIL (rc 1): tell your user the FAIL lines, verbatim, and STOP, do not start the loop.
   Exception: if ONLY the gh lines (`gh-installed`, `gh-auth`, `gh-repo`, `gh-runs`) fail, offer
   to continue without CI: rerun with `--no-ci`, and launch every queuewatch below with
   `--no-ci`; say plainly "CI is not watched".
3. PASS: send ONE SendMessage to $MANAGER, `MON up: preflight PASS, watching queue + CI` (or
   `... watching queue, CI NOT watched` under `--no-ci`). That proves the routing at startup. If
   the SendMessage fails, tell your user "I cannot reach session $MANAGER: tell me the manager
   session's name" and use the name they give as MANAGER; the loop still runs.
4. Then the loop.

## The loop

1. Once, read this file. Then run, in the BACKGROUND (Bash `run_in_background`):

       $QW --max-sec 3000

   It prints ONE line and exits, so the harness wakes you exactly once per event. It
   stops itself at 3000 s (`CAP ... relaunch`), before any outer timeout.
2. When it exits, read its one line, apply the table, relaunch step 1. Always relaunch
   unless the table says END. Relaunching can never miss or repeat an event.

## Action table (first match wins)

NAME is `PRIO-OWNER-REST` (e.g. `300-main-fullsuite`); OWNER is its second field. SEND TO:
OWNER `main` -> `$MANAGER`; OWNER `kit` -> `pcrecdev3`; any other OWNER -> `$MANAGER`. On a RED or
PROBLEM also copy `$MANAGER` when the owner is not `main`. One SendMessage per row firing,
first line self-contained, prefix `MON <NAME>:`.

| # | the line | do | message |
|---|---|---|---|
| 1 | `CAP ... relaunch` (exit 6) | relaunch | none |
| 2 | `JOB-START` | nothing | none |
| 3 | `STAGE-END .. rc=0` | nothing | none |
| 4 | `STAGE-END S rc=N` (N != 0), the FIRST red of this NAME | launch ONE read-only triage agent: `Agent`, `model: sonnet`, background, NO name, prompt `TRIAGE <NAME>: read $ROOT/.claude/skills/pcrec-test/triage_brief.md and follow it. LOGDIR=<the line's logdir=>; stage=S.` | `stage S RED (rc=N), triage launched` |
| 5 | `STAGE-END S rc=N` (N != 0), a later red | append `S` to `<logdir>/red_stages.txt` (the triage reads it) | none |
| 6 | `JOB-DONE .. outcome=green` and no `reds=` | if `<logdir>/SIMULATED` exists or logdir contains `full_suite_sim`: nothing else. Else if `<logdir>/summary.txt` exists: append its one line under `## Runs` in $LEDGER and `git -C $ROOT commit -m "ledger: full suite green" -- docs/dev/full_suite_ledger.md` (named path only) | `GREEN <summary line or the JOB-DONE line>` |
| 7 | `JOB-DONE` anything else (a red stage, outcome != green, a battery that died) | same ledger step as 6 with the line marked RED (never for a SIMULATED run) | `RED <the JOB-DONE line>; triage launched or none needed` |
| 8 | `RUNNER-DEAD` | `bash $ROOT/scripts/boxqueue start`, ONCE per run; a second RUNNER-DEAD for the same NAME: no second start | first: none. Second: `PROBLEM runner dead again after one restart` |
| 9 | `QUIET` | nothing (never kill, cancel or retry) | `PROBLEM <the line>` |
| 10 | `PENDING-STUCK`, `DISK-HIGH` | nothing | `PROBLEM <the line>` |
| 11 | `CI-RED <sha> <run id> <subject>` | nothing: the manager launches the triage, you do not (CI red on main is triaged before other work) | `$MANAGER` only: `MON CI: RED <the line>` |
| 12 | `CI-CANCELLED ...` (the newest main run was cancelled and nothing later is running; a cancelled run is NOT green) | nothing | `$MANAGER` only: `MON CI: CANCELLED <the line>` |
| 13 | `CI-UNAVAILABLE <reason>` | nothing (it never stops the queue events; it is reported once until gh works again) | tell your user the line, and ONE message to `$MANAGER`: `MON CI: UNAVAILABLE <reason>, CI is not watched` |
| 14 | exit 75 (another watcher holds the state) | END | tell your user "a second queuewatch is running; close one" |
| 15 | exit 2 (queue missing) or any other exit | END | tell your user the line |

NEVER: kill, cancel, retry, edit code or docs (except the ledger line in row 6/7), run
make or any suite, read a stage log, run a second queuewatch, keep your own list of what
was reported. Row 4's triage agent writes a file; it reaches the owner by its own final
reply, so do not wait for it. `.claude/skills/pcrec-test/monitor_rules.md` is the older
per-run version of this table (kept for the per-run fallback).

## Context discipline

Your context only grows. After a JOB-DONE (rows 6/7) say in ONE line "run done; /clear me
before the next run" and keep looping: your user clears you whenever convenient. A
`/clear` loses nothing, because the state is the file. If the first line after a clear or
a fresh start is a burst of old events, that is the first launch seeding itself: it only
seeds jobs that had ENDED and reports a running job from its START, once.

## Testing without a real run (simulate mode)

`scripts/fullsuite_job.sh --simulate green|red[:STAGE]|quiet[:STAGE]|die[:STAGE]|burst` is
the full-suite job with only the stage payloads faked (header of scripts/battery.sh). The
test `scripts/tests/queuewatch.test` drives it through a SCRATCH queue; never `boxqueue add`
into a scratch queue by hand (a runner armed for a real job once started a real battery).
