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
    QWOPTS=                                   # empty outside TEST MODE (section "TEST MODE")
    LEDGER=$ROOT/docs/dev/full_suite_ledger.md
    MANAGER=pcrec-main                        # the manager session's name (Frank 2026-10-25; this session ran as pcrec_main once); every "main"
                                              # below means it. The STARTUP message proves it; if it fails, your
                                              # user names the right one

Over ssh the loop below is the same: `$QW` runs on the queue's box, its one line comes
back on stdout, the ledger append/commit and `boxqueue start` run there too. Messages
(SendMessage) are local to your session host and so only work where the target sessions
live; on another box, print the line for your user instead. Scope: the pcrec repo only.

**TRIAL NOTE (2026-10-25, [MON-SCRIPT]):** `scripts/queuemon` (the script) is now the default monitor; it applies this table, minus triage (the owner triages), and journals to worktrees/.mgr/monitor.log, read with `scripts/monread OWNER`. This session/subagent is the FALLBACK until the script has watched one real run.

## How you were started (session or subagent: read this once)

One skill, two ways to run it (Frank, 2026-10-24: "I want both methods supported").

| | (a) SESSION | (b) SUBAGENT |
|---|---|---|
| started by | Frank: `/pcrec-monitor` in a separate haiku session | the manager or a lane: `Agent`, `subagent_type: pcrec-monitor` (.claude/agents/pcrec-monitor.md, haiku, 1-hour cache) |
| MANAGER | `pcrec-main` (cross-session SendMessage by name) | `main`: SendMessage `to: "main"` reaches the session that launched you. Your parent's cross-session NAME would be a message to yourself |
| how the loop waits | step 1a: `$QW --max-sec 3000` in the BACKGROUND; the harness wakes you when it exits | step 1b: a FOREGROUND call (below). A subagent that ends its turn is finished and its background shell dies with it (measured 2026-10-24, lane montest: a `sleep 60` started with run_in_background was killed at the subagent's end, nothing woke it), so you must never end your turn while watching |
| between runs | Frank `/clear`s you | you end (reply "run done") when your brief's STOP condition is met; the launcher starts a fresh one for the next run |

If your prompt names MANAGER, TEST MODE or STOP_AT, it overrides the defaults here. Everything else
(STARTUP, the action table, NEVER) is identical.

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

1. Once, read this file. Then wait for the next event:

   (a) SESSION, in the BACKGROUND (Bash `run_in_background`): `$QW $QWOPTS --max-sec 3000`
   (b) SUBAGENT, in the FOREGROUND (Bash `timeout` 590000 ms): `timeout 580 $QW $QWOPTS --max-sec 540`
       (inner 540 + one poll (default --every 15) < outer 580 < the tool's 600 s); a CAP line comes back every
       540 s at most, which costs you one cheap wake: relaunch at once. Do not end your turn in between.

   It prints ONE line and exits, so you wake exactly once per event. It stops itself at its --max-sec
   (`CAP ... relaunch`, exit 6), before any outer timeout. QWOPTS is empty outside TEST MODE.
2. Read its one line, apply the table, relaunch step 1. Always relaunch unless the table says END
   (or, subagent only, your STOP condition from the prompt is met: then reply with one line and end).
   Relaunching can never miss or repeat an event.

## Action table (first match wins)

NAME is `PRIO-OWNER-REST` (e.g. `300-main-fullsuite`); OWNER is its second field. SEND TO:
OWNER `main` -> `$MANAGER`; OWNER `kit` -> `pcrecdev3`; any other OWNER -> `$MANAGER`. On a RED or
PROBLEM also copy `$MANAGER` when the owner is not `main`. One SendMessage per row firing,
first line self-contained, prefix `MON <NAME>:`.

EXPECT MISMATCH (manager, 2026-10-24, after 610-substland-test): a JOB-DONE with `verdict=GREEN` and `rc=0` but `reason=POPULATION-...` (or any expect/witness reason) is NOT a death: the work passed and the job's declared count is stale. Message the owner `EXPECT <the line>: work green, the job's expect is stale` and launch no triage; a job waiting on it (`boxqueue after`) stays blocked until the owner rules.

DIED vs RED (manager, 2026-10-24, after 611): only a full-suite job writes `reds=`; any other job's red JOB-DONE is plain `RED <the line>; owner triages`, never "run died".

TRIAGE SCOPE (manager, 2026-10-24, after 620-kit-s3-heavy): rows 4 and 7 launch a triage ONLY for a full-suite job (its logdir holds trailer.log, i.e. scripts/fullsuite_job.sh). Any other job (a lane's make test, a kit job, a chain) is triaged by its OWNER: send the message only, with the job dir, and say "owner triages". The kit triaged 620 itself while the monitor's triage (battery-shaped brief on a non-battery job) ended with no file.

| # | the line | do | message |
|---|---|---|---|
| 1 | `CAP ... relaunch` (exit 6) | relaunch | none |
| 2 | `JOB-START` | nothing | none |
| 3 | `STAGE-END .. rc=0` | nothing | none |
| 3a | `CANCELLED NAME ...` (a pending job cancelled, a RUNNING job stopped by `boxqueue cancel`, a work exit 77, a bench `.cancel`; queuewatch's own class since qscripts 2026-10-26) | nothing: a DELIBERATE stop is information, never a red and never a problem (before: `outcome=cancelled (never ran)` read as RED) | none (queuemon journals it INFO) |
| 4 | `STAGE-END S rc=N` (N != 0), the FIRST red of this NAME | launch ONE read-only triage agent: `Agent`, `model: sonnet`, background, NO name, prompt `TRIAGE <NAME>: read $ROOT/.claude/skills/pcrec-test/triage_brief.md and follow it. LOGDIR=<the line's logdir=>; stage=S.` The triage writes /tmp/claude-1001/triage-<NAME>/triage.md (that FILE is the delivery; its final reply may not reach you: never report "no report", give the path) | `stage S RED (rc=N), triage launched` |
| 5 | `STAGE-END S rc=N` (N != 0), a later red | append `S` to `<logdir>/red_stages.txt` (the triage reads it) | none |
| 6 | `JOB-DONE .. outcome=green` and no `reds=` | if `<logdir>/SIMULATED` exists or logdir contains `full_suite_sim`: nothing else. Else if `<logdir>/summary.txt` exists: append its one line under `## Runs` in $LEDGER and `git -C $ROOT commit -m "ledger: full suite green" -- docs/dev/full_suite_ledger.md` (named path only) | `GREEN <summary line or the JOB-DONE line>` |
| 7 | `JOB-DONE` anything else (a red stage, outcome != green, a battery that died) | same ledger step as 6 with the line marked RED (never for a SIMULATED run). If the job is a FULL-SUITE job (logdir holds trailer.log) and the line has NO `reds=` (the run died or failed outside a stage): launch the row-4 triage now with stage=`died` (TEST MODE: log "would launch triage"); a death is always a problem (manager ruling 2026-10-24) | with `reds=`: `RED <the JOB-DONE line>; triage already launched`. Without: `PROBLEM run died: <the JOB-DONE line>; triage launched` |
| 8 | `RUNNER-DEAD` | `bash $ROOT/scripts/boxqueue start`, ONCE per run; a second RUNNER-DEAD for the same NAME: no second start | first: none. Second: `PROBLEM runner dead again after one restart` |
| 9 | `QUIET` (for a bench reservation `NNN-bench-W`, queuewatch samples the bench's own chain group and log, not the placeholder) | nothing (never kill, cancel or retry) | `PROBLEM <the line>` |
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

## TEST MODE (rehearse the whole skill against a scratch queue)

Only when your prompt/user says `TEST_MODE=1`. The driver `scripts/monitor_rehearsal setup DIR` builds a
SCRATCH queue of four simulated jobs (green, red:axes, quiet:san, die:alloc) and prints these variables:

    TEST_MODE=1   MANAGER=<who gets the messages>   BOXQUEUE=DIR/q   STATE=DIR/state   ACTIONLOG=DIR/action.log
    QWOPTS="--queue DIR/q --state DIR/state --every 2 --confirm 2 --quiet-sec 15 --max-sec 300 --no-ci"
    STOP_AT=130-test-simdie       # end after the JOB-DONE of this job (for a restart check: 110-test-simred first)

(CI is off with `--no-ci`; to include it, drop `--no-ci`: the real `gh` is read-only and fine.) Rules, and only these differ:

1. QWOPTS is used on every queuewatch launch (and `monitor_preflight --no-ci`). A subagent keeps `--max-sec` below its
   foreground bound (the driver's 300 is under 540). Never use the live queue or the live state.
2. ACTION LOG: after you handle EACH line (rows 1-13, every row, including the do-nothing ones) append ONE line to
   $ACTIONLOG: `ROW=<n> | <the queuewatch line exactly> | <action taken> | <the message text, or none>`. Append, never
   rewrite. Your STARTUP `MON up` message is not logged. Row 1 (CAP) lines are logged and ignored by the compare.
3. SIMULATED logdir (`<logdir>/SIMULATED` exists, or the path has `full_suite_sim`; here always): row 4 does NOT launch
   the triage agent: action `would launch triage`; rows 6/7 never touch the ledger or commit: action `would append
   ledger`; row 5 appends nothing: `would append red_stages`; row 8 never starts a runner: `would start runner`.
4. Every message is real (SendMessage to $MANAGER) but its text begins `MON TEST ` (e.g. `MON TEST 110-test-simred: stage axes
   RED (rc=2), triage launched` becomes `MON TEST 110-test-simred: stage axes RED (rc=2), would launch triage`).
5. Stop: after the JOB-DONE of STOP_AT (or exit 75/2), reply in one line and END. State and action log stay for the next
   monitor: a fresh one with the same STATE and ACTIONLOG must neither repeat nor miss an event.

Known limit: QUIET/DISK-HIGH are live conditions, not replayed events; a monitor gap longer than the whole episode (restart check: use `setup --quiet 120`) can miss one, START/STAGE-END/JOB-DONE can not.

Compare: `scripts/monitor_rehearsal compare DIR` (expected vs actual rows/events, no real triage or ledger action, ledger
checksum unchanged), `status DIR` (queue + log tail), `teardown DIR` (kills the scratch runner, removes DIR).

### Rehearsing method (a), the standing session, yourself (Frank)

1. In any shell on the box (not the live queue; this touches only DIR): `scripts/monitor_rehearsal setup /tmp/monrehearsal`
   (use a scratch dir you may delete). It prints the variables and detaches a feeder that queues the four jobs once the
   monitor's first queuewatch launch appears (~4 min of simulated stages in all).
2. In the separate haiku session type: `/pcrec-monitor TEST_MODE=1 MANAGER=pcrec-main ` plus the three printed
   variable lines (BOXQUEUE/STATE/ACTIONLOG, QWOPTS, STOP_AT), copied as printed.
3. You should see: the preflight PASS lines, a `MON up` message, then `MON TEST ...` messages arriving at the manager
   (green once; red: `stage axes RED ... would launch triage` and `RED ...`; quiet: `PROBLEM QUIET ...` then `GREEN`; die:
   `PROBLEM run died ...`), and the monitor ending with a one-line reply after the `130-test-simdie` JOB-DONE.
4. `scripts/monitor_rehearsal compare /tmp/monrehearsal` must print PASS x3; then `... teardown /tmp/monrehearsal`.
   For the restart check use STOP_AT=110-test-simred, `/clear` the session, restart it with the same variables
   (STOP_AT=130-test-simdie) and compare: the log must show no repeat and no miss.

## Testing without a real run (simulate mode)

`scripts/fullsuite_job.sh --simulate green|red[:STAGE]|quiet[:STAGE]|die[:STAGE]|burst` is
the full-suite job with only the stage payloads faked (header of scripts/battery.sh). The
test `scripts/tests/queuewatch.test` drives it through a SCRATCH queue; never `boxqueue add`
into a scratch queue by hand (a runner armed for a real job once started a real battery):
`scripts/monitor_rehearsal` does it with pure simulate wrappers.
