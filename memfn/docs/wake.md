# memfn kit — wake-up brief

Updated 2026-11-20 03:50 by the kit session IN FLIGHT (rewritten 18:25 11-19). Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. No heartbeat (Frank: none
needed; no lanes in flight). Waiting list worktrees/.mgr/waiting_on.kit. Verdicts only via `scripts/monread kit --wait`
(run_in_background); one is ARMED for 708/709.

## Read in order
1. This file. 2. memfn/docs/journal.md, the 2026-11-19 entries (from 08:00 on: formperf, simdhead, blockspan, COVER-CAP, R-46).

## Box rules (binding)
Evening hold 20:00-01:00 is Frank's; lane CPU ends 19:30. Timing only in windows main cleared. Never merge to main.

## CURRENT STATE (18:25 11-19)
- BLOCK FORMS DONE: 708 + 709 GREEN; verdict LOSS at both layers (frozen rule): blocks do NOT replace the inline form. Analysis
  scratch/memfn/blockanalysis/report.md; ideas.md 707 entry evaluated. dig/hi losses = walk confound; post-data SIMD table 0 LOSS (biased).
  OWED: Frank's answer on a confirming run (walk fixed, SIMD table declared before data). No build. fcards-night unpinned, prunable.
- R-46 (dense-hit pre-check FORM reply): SLIPPED from 17:00 11-19. New target 14:00 11-20 (main agreed). Design lane 08:00 after
  708/709, then a critic round. Scope (main, from Frank): dense = 2 or more hits per block, stop there; super-dense (hits within
  N) is not a target; read 709's N first.
- COVER-CAP LANDED on main 77edff7ae (span forms abi 109 + relabel 0df533a85). OWED: merge main into lane/memfn-k1108 (merge
  alone, make strict) at a quiet point (not during 708).
- fcards set 2 DONE: h*=64, C3 complete at 64 (705 GREEN), 704 identity GREEN. Findings in ideas.md (706 mispredicts; 707 blocks).
- OWED by day (from 11-19, still open): set 1 INCONCLUSIVE-AT-NOISE record (609 log:
  worktrees/.boxqueue/done/20261119T025228.524574978-609-kit-mfcard-time/job.log); calibration loaded-vs-quiet summary
  (scratch/memfn/mfcal/run/mfcard-zen4-4L/compare.txt); h*=64 ceiling note for main (grid stops at 64).
- Later: cards.py not-warm expect ignores 4 KiB chunking (fix); wtprune relabel64 (unpin first), formsfix*, formsland*,
  gatebudget, mfcal, g2pcap, crit trees, fcards-night (after 709); unpin mfind; r46 PLAN/DOC; r24 SR-1..4; ADQ-3-3;
  mfind-long-run witness.

## Lessons (2026-11-19)
- The runner RE-RUNS a job's --dry-run at START under a 30 s bound: a dry-run doing real work fails then.
- PENDING-STUCK can fire seconds after a predecessor ends; check its outcome and wait one poll.
- A job exiting 1 for "re-run owed" reads RED; triage tells it from a defect.
- A --ready chained on a job KEY breaks when that key fails and a re-run job replaces it (704 → re-pointed to c3rerun).
- Pins live in worktrees/.wtprune.keep (NOT the repo root); verify with a wtprune dry run showing "KEEP ... pinned". A root-file pin let fcards-night be pruned 11-19 13:45 and 708/709 fail at start 11-20 01:00.
- Owed-by-time items slip silently when owner-direct work fills the day: put each in waiting_on.kit WITH its due time (R-46).
