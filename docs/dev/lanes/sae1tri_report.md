# sae1tri — triage of E1's red identity job 201-main-sae1-ident-2 (2026-11-09, sonnet)

STATE: done (re-queued, run OWED)

## Cause

The RED was a JOB defect, not an identity finding. The job's own log
(job.log) ends `== ident_check COMPLETE: 0 unexplained` (21 c-default, 21
c-vm and 122 facts-stream mover rows; 109 distinct census movers = 109
distinct facts-stream movers; no asymmetric row, no floor/witness line).
`scripts/verdict` flagged two lines the job itself printed: line 1,
`emit_sweep rc=1 (movers make it 1 by design ...)` (the hand-written-chain
`rc=N` status-line rule) and line 13, the sweep's own trailer
`emit_sweep: DONE rc=1` (the `TOOL: DONE rc=N` rule), echoed by the job's
grep. emit_sweep exits 1 whenever movers exist, which E1 expects. So
outcome=failed rc=0 reason=VERDICT-RED_rc=0_but_a_red_line.

No real unpredicted mover, no census/model gap, no answer change.

## Fix or disposition

The job script (scratch, not tracked: /var/tmp/pcrec-pcrec/scratch/sae1/jobs/
ident3.sh, from ident.sh) now prints `emit_sweep exit code N (...)` and
rewrites the sweep trailer to `sweep finished, exit code N`, so verdict sees
no `rc=` line for the by-design nonzero exit. The floor/witness RED check and
the ident_check call are unchanged. No change to lane/sae1 code or tooling.
Re-queued as 201-main-sae1-ident-3 (same hold-aware --ready via common.sh
`ready_after`; the 19:00-01:00 hold applies at start).

## Checks run

- verdict on the failed job.log: 2 red lines, both the echoes above.
- ident_check.py re-run by hand (nice) on the job's movers.tsv:
  `== ident_check COMPLETE: 0 unexplained`, same counts.
- `bash -n` and `--dry-run` on ident3.sh; boxqueue add accepted it.
- Not run: the emit_sweep itself (the queued job does it).

## STATE AT HANDOFF

Owed: queue key 201-main-sae1-ident-3 (log under worktrees/.boxqueue/;
expect `== ident_check COMPLETE: 0 unexplained` and verdict GREEN). Rulings
file sae1tri_rulings.md was empty. The sibling-lane `abcd(?:\b)+efgh`
codegen-bucket item is untouched here. The ident-2 verdict is a false red;
nothing was re-pinned.
