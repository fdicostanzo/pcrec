# reachonly report ([MECH-REACHONLY], 2026-10-21, lane reachonly, sonnet)

Built `REACH_ONLY=1` for `tests/mech/run_sabotage_matrix.sh`. The reach block
already ran on the clean tree before any plant, so the mode is an early exit
after it (same code a full run executes), plus a no-probe early exit, a skip of
the encoding baseline and the asan probe, and a JOBS-wide clean build. Verdicts
per row: REACHED / UNREACHED / declared-UNREACHED / NOW-REACHED / NO-PROBE;
trailer `mech-reach-only: DONE rc=N ...`; rc 1 iff an undeclared row reads
unreached. Also: `MECH_SAB_DIR` (definitions dir override, for the self-test),
`tests/mech/reach_only_selftest.sh`, the BOILERPLATE delivery-bar line,
tests/mech/CLAUDE.md section (the "no cheap reach-only mode" sentence replaced).
STOP RULE did not fire: every probe runs on the clean tree; none needs a plant.

Premise: 455 of 848 files under sabotages/ mention SAB_REACH (grep -l), so many
rows carry probes.

## STATE AT HANDOFF
- Code, docs, self-test committed on lane/reachonly. `bash -n` clean.
- NOT YET RUN (box lock was held by x0oracle-v2 for 19+ min when I tried):
  boxqueue job `200-reachonly-reach` (queued 10:10, cap 3600) runs the
  self-test then the full sweep (PROCS=4 JOBS=4). Logs:
  /tmp/reachonly/selftest.log, /tmp/reachonly/full.log. Read with
  `scripts/verdict /tmp/reachonly/full.log`.
- OWED: wall time, today's unreached list (each row named), self-test result.
  Fill the three sections below from those logs; if the sweep exceeds ~10 min,
  say so and keep the queued form.

## Wall time
(owed)

## Rows reading unreached on f2dae53f9
(owed; no witness is to be fixed in this lane)

## Self-test
(owed)
