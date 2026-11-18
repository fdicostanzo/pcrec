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

## CURRENT STATE (12:30 11-18)
- R-45 plan A DELIVERED 12:17: lane/memfn-forms @ 105bf8ef4, done line [responses] 7f655c9e3; cloud test + axes GREEN.
  Reviews r44 r45 (on the forms branch), r46 (no FIX-NOW, on lane/memfn-k1108 4e2649fd5). Main's landing lane merges it
  into a branch off lane/covs2b @ 28af649c9 and sends the FROZEN sha (by 20:00).
- MERGE RED (13:00): main's cloud test on the forms merged into the cover-cap line red in G2 presence (58 x more than
  MF_MAX_TERM terms). Lane g2pcap (lane/memfn-g2pcap off lane/covs2land 4d56a2537): G2P_MAXRUN = min(64, MF_WSPAN_POS,
  MF_MAX_TERM); re-pins; checks; dispatches cloud test as last act by 15:30. Main needs the tip GREEN by 18:00 (word by
  15:00 if slipping); then main freezes the combined line for set 2.
- SET 2 (form cards, 700-704; jobs /var/tmp/pcrec-pcrec/scratch/memfn/fcards/jobs/README.md): when main sends the frozen
  sha: `worktrees/fcards-night` at FROZEN, clean, pinned in .wtprune.keep; window.vars RUN_ID=fcards-zen4-1,
  FROZEN=<sha>; DRY-RUN the job set against it first (r44/r45 changed cards.py's run id + confirm rounds); queue 700-704
  (not before 2026-11-19T01:00); send main the keys; after 702 tell main "h* frozen". 704 identity only at h*=64.
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
- Owed later (after the night): r46 PLAN/DOC items (INTER_CLIP held-out, R0 counted apart, heavy-tail rows); r44 M
  [LAYOUT-DRAW] filed by main; prune worktrees (formsfixk..m, formsland*, gatebudget, crit trees) with scripts/wtprune;
  unpin worktrees/mfind after set 1; r24 SR-1..SR-4; ADQ-3-3; the mfind-long-run witness.

## Lessons (2026-11-18)
- A long selftest makes lanewatch fire QUIET every 25 min: re-arming it is noise; rely on the hand-back + heartbeat.
- A process started inside a boxqueue job inherits the box-lock fd unless fds > 2 are closed (CAL-1).
- A JMH-style job with many launches needs a per-launch quiet budget; the box idles at load ~1.9-2.2.
