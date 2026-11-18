# memfn kit — wake-up brief

Rewritten 2026-11-18 12:30 by the kit session (pcrec-memfn) IN FLIGHT (context near compaction). Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Heartbeat cron
`17,47` (OWNER=kit). Waiting list worktrees/.mgr/waiting_on.kit. Verdicts only via `scripts/monread kit`
(one `--wait` armed with run_in_background).

## Read in order
1. This file. 2. memfn/docs/journal.md, 2026-11-18 entries (from 23:25 11-17).

## Box rules (binding)
Evening hold 20:00-01:00 is Frank's; lane CPU ends 19:30. Timing only in windows main cleared. Never merge to main.

## CURRENT STATE (15:00 11-18)
- R-45 plan A DELIVERED 12:17: lane/memfn-forms @ 105bf8ef4, done line [responses] 7f655c9e3; cloud test + axes GREEN.
  Reviews r44 r45 (on the forms branch), r46 (no FIX-NOW, on lane/memfn-k1108 4e2649fd5). Main's landing lane merges it
  into a branch off lane/covs2b @ 28af649c9 and sends the FROZEN sha (by 20:00).
- MERGE RED fixed: g2pcap d5c41db37 cloud GREEN (44370476761); main merged it into lane/covs2land as 33fec79b3.
  (cloud/kit/test/HEAD-1a91106 was a stray push of main HEAD by the lane: ignore.)
- SET 2: main FROZE 33fec79b3efc4ce8b838cd8daa65908df5f4e847 (14:5x). worktrees/fcards-night at it, detached, pinned in
  .wtprune.keep. Lane fcardsq (sonnet, in flight) builds it, checks 700-704 vs rev 13.1 cards.py, writes window.vars
  (RUN_ID fcards-zen4-1), dry-runs, QUEUES 700-704; report /var/tmp/pcrec-pcrec/scratch/memfn/fcardsq/report.md; keys
  SENT to main (QUEUED 700-704). After 702: tell main "h* frozen". 704 CANCELLED for tonight (main): re-queue BY DAY 11-19 once main gives REBUILT_BUILD (+ MOVERS if h*<64); identity only at h*=64.
- SET 1 re-run QUEUED (600-609, RUN_ID mfcard-zen4-4, FROZEN e7f9a4365 = run.py per-launch quiet budget,
  worktrees/mfind; fresh first run, no FIRST_RUNDIR); waits while any kit-fcards-* is pending/running; NOT_BEFORE
  2026-11-19T01:00. LAST night for set 1 (main): if avx2libc refuses again at the 3 % byte floors on a gate-held night,
  record INCONCLUSIVE-AT-NOISE with both nights' figures (zen4-3 + zen4-4) and stop. 609 CONFIRM -> CONFIRM_CELLS, 610.
- CALIBRATION (Frank via main 11-18): set mfcal 800-809 re-times the green set 1 cards at load ~3 (RUN_ID
  mfcard-zen4-4L, MF_QUIET_LOAD=4.0 env only, tree worktrees/mfcal @ 77871a33e, jobs scratch/memfn/mfcal/jobs/),
  after sets 2+1, must end by 07:00, spinners hard end 07:15. CAL-1..8 FIXED (mfcalfix; CAL-1 proven by smoke 433/434),
  FROZEN = lane/memfn-mfcal HEAD (report/deliver commits only), 809 exempt from the 07:00 cut. QUEUED 800-809 12:4x, keys
  sent to main (ACKED).
  Morning: a lane writes the loaded-vs-quiet comparison (809's compare.txt) for main/Frank.
- R-46 ACKED 11-18 (dense-hit pre-check: a FORM reply only, no build go; request text on main 603154be1): design lane by day
  11-19 after the night verdicts + a critic round; responses.md entry target ~17:00 11-19.
- Owed later (after the night): r46 PLAN/DOC items (INTER_CLIP held-out, R0 counted apart, heavy-tail rows); r44 M
  [LAYOUT-DRAW] filed by main; prune worktrees (formsfixk..m, formsland*, gatebudget, crit trees) with scripts/wtprune;
  unpin worktrees/mfind after set 1; r24 SR-1..SR-4; ADQ-3-3; the mfind-long-run witness.

## Lessons (2026-11-18)
- A long selftest makes lanewatch fire QUIET every 25 min: re-arming it is noise; rely on the hand-back + heartbeat.
- A process started inside a boxqueue job inherits the box-lock fd unless fds > 2 are closed (CAL-1).
- A JMH-style job with many launches needs a per-launch quiet budget; the box idles at load ~1.9-2.2.
