# montest report (2026-10-24, lane montest, sonnet)

Row [MONITOR-QUEUE]: /pcrec-monitor now runs as a session (a) or a subagent (b), one skill, and was rehearsed end to end.

## What wakes a subagent
Nothing but its own tool calls. Probe 2 (haiku pcrec-monitor subagent): started `sleep 60` with run_in_background, ended its
turn: the Agent call returned in 21 s and the background task never completed (killed with the subagent, no done file, no wake).
A subagent that ends its turn is finished. So the skill's loop 1b is a FOREGROUND `timeout 580 queuewatch --max-sec 540`
(inner 540 + poll 15 < outer 580 < Bash 600 s), relaunched on every CAP; the subagent never ends its turn while watching.
Note: in this lane's tool set the Agent call is synchronous (blocks the launcher until the monitor ends); the pcrec-test skill's
launch (background) is the manager's, unchanged. Each subagent finished with "ended without delivering a report through
SubagentHandback" (harness text; the final line is not shown), so the ACTION LOG is the evidence, not the reply.

## Rehearsal (driver scripts/monitor_rehearsal; scratch queue, four pure `fullsuite_job.sh --simulate` wrappers, feeder
queues them when the monitor's first queuewatch launch appears)
- Full run (haiku subagent, --quiet-sec 15, SIM_QUIET 40): action log == expected, 37 lines, every event once, in order, right
  row (JOB-START row 2, STAGE-END rc=0 row 3, axes rc=2 row 4 "would launch triage", greens row 6 "would append ledger",
  reds row 7, QUIET row 9, die job row 7). No triage launched, ledger checksum unchanged. 51 tool uses, 208 s.
- Restart check #1 (SIM_QUIET 40): monitor 1 stopped after the red job's JOB-DONE, monitor 2 started ~1 min later on the same
  state: every START/STAGE-END/JOB-DONE exactly once, BUT the QUIET of job 3 was missed (the whole 25 s quiet episode fell in the
  gap). Not a bug: QUIET is a live condition (an episode), not a replayed event. Documented as a known limit in the skill.
- Restart check #2 (setup --quiet 120): 37 lines == expected, no repeat, no miss. (Total 2 monitors, 125 s + 158 s.)
- Messages `MON TEST ...` went to MANAGER=main (the manager session, per the brief); not visible to the lane.

## Method (a)
Steps for Frank are in the skill, "Rehearsing method (a)": `scripts/monitor_rehearsal setup DIR`, type `/pcrec-monitor TEST_MODE=1 ...`
with the printed variables, then `compare DIR` and `teardown DIR`.

## Commits (lane/montest)
driver; skill + agent; pcrec-test launch step; this report + CLAUDE.md line + known-limit note.

STATE AT HANDOFF: all rehearsal dirs torn down (/tmp/claude-1001/montest/r0..r3 removed; no scratch runner left); live queue,
live queuewatch state and the ledger untouched. queuewatch.test premise run: see below. Rulings file empty; no entry applied.
