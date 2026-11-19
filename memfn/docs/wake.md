# memfn kit — wake-up brief

Rewritten 2026-11-19 04:10 by the kit session (pcrec-memfn) IN FLIGHT, after the night run. Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Heartbeat cron
`17,47` (OWNER=kit) is OFF tonight by Frank's word (no lanes in flight); recreate it when lanes run. Waiting list
worktrees/.mgr/waiting_on.kit. Verdicts only via `scripts/monread kit` (`--wait` with run_in_background); none armed, because
no kit job is queued.

## Read in order
1. This file. 2. memfn/docs/journal.md, the 2026-11-19 entries (01:02 onward).

## Box rules (binding)
Evening hold 20:00-01:00 is Frank's; lane CPU ends 19:30. Timing only in windows main cleared. Never merge to main.

## CURRENT STATE (04:10 11-19): the night is done, the box is free, no kit job is queued
- SET 2 (fcards-zen4-1, FROZEN 33fec79b3, worktrees/fcards-night, pinned): 700-702 GREEN, h* = 64 (the grid top; 64 cells void
  twice by method; R2(C3)/R5 not computed at 702). 703 RED = C3 RE-RUN OWED, not a defect (6 C3 cells void once; 703 exits 1
  until complete:64; triage scratch/memfn/triage703/report.md). 703 refuses a repeat run (results_c3_h64.tsv exists), so it needs
  a job: `cards.py rerun` then `rule`. Main asks Frank for a day window and sends it, or a no, BY 10:00. 704 (identity) after
  it, with REBUILT_BUILD only (no MOVERS at h*=64).
  Job fix 01:02: g2_dry's real G2 pass needs FCARDS_G2_DRY_REAL=1 (it broke the runner's 30 s start dry-run); backup
  fcards/jobs.bak-0102.
- SET 1 (mfcard-zen4-4): 600-609 GREEN as jobs. The verdict is INCONCLUSIVE-AT-NOISE per main's last-night rule (no 610). Every
  cell won beyond its floor (w16 16 win/2 tie, w32 18/18, both arms), but the arm records were REFUSED floor:byte.libc: the
  kit.find_byte.libc gate FAILED at noise 1193 on 38455 (3.1 %). OWED: the record with the zen4-3 and zen4-4 figures (609 log:
  worktrees/.boxqueue/done/20261119T025228.524574978-609-kit-mfcard-time/job.log). Then unpin worktrees/mfind.
- CALIBRATION (mfcard-zen4-4L): 800-809 GREEN, done 04:04. compare.txt = scratch/memfn/mfcal/run/mfcard-zen4-4L/compare.txt
  (loaded vs zen4-3 + zen4-4, same plan sha; every card loaded ok, mean load1 2.65-3.15). OWED: a morning lane writes the
  loaded-vs-quiet summary for main/Frank.
- OWED to main (by day): the h*=64 ceiling note (was any cell above 64 ever readable? rule_702.txt, results*.tsv).
- R-46 ACKED (dense-hit pre-check: a FORM reply only): design lane by day + a critic round; responses.md entry target ~17:00.
- R-45 plan A delivered (lane/memfn-forms @ 105bf8ef4); main lands it.
- Owed later: r46 PLAN/DOC items; prunes via wtprune (formsfix*, formsland*, gatebudget, mfcal, g2pcap, crit trees, fcards-night
  after 704); r24 SR-1..4; ADQ-3-3; the mfind-long-run witness.

## Lessons (2026-11-19)
- The runner RE-RUNS a job's --dry-run at START under the 30 s bound: a dry-run that does real work on a built tree fails then,
  even when the queue-time add passed.
- PENDING-STUCK can fire seconds after the job a chain waits on ends, before the runner re-asks; check the predecessor's outcome
  and wait one poll before acting.
- A job that exits 1 for "re-run owed" reads as RED; triage tells it from a defect.
