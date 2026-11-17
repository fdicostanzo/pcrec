# memfn kit — wake-up brief

Rewritten 2026-11-16 17:30 by the kit session (pcrec-memfn). Tonight: the mfcard timing window from 01:00.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = session `pcrec-main`. Frank rules, mostly via main.
Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Heartbeat cron `17,47` (OWNER=kit); waiting list
worktrees/.mgr/waiting_on.kit; sabotage ids worktrees/.mgr/sabotage_ids.txt (next free S3260).

## Read in order
1. This file. 2. memfn/docs/journal.md, 2026-11-16 entries. 3. responses.md's last two `done:` lines (R-44, R-45 plan B)
and the R-45 reply block (rev 6). 4. D197 (the mfind instrument; one-sided timing).

## UPDATE 2026-11-17 02:25 (read FIRST; supersedes the lines below where they differ)
- mfcard-zen4-2 ran: 600-603, 605-607 GREEN; 604 + 608 (JMH, both arms) RED on the quiet gate (load ~1.9 baseline vs 2.0:
  Frank's steam/ptyxis/code + idle Claude sessions + kworkers); 609 all levels INCONCLUSIVE only from never-ran JMH. MAIN RULED:
  NOT a measurement, NOT the one re-run; next window = a fresh FIRST run of all 10 jobs (new RUN_ID, no FIRST_RUNDIR). The
  quiet-gate question is Frank's (via main). Queue NO timing until main relays his answer + a cleared night. worktrees/mfind
  stays pinned. Triage: scratch/memfn/tri-mfc604, tri-mfc608.
- Main's combined branch lane/covs2b exists (covs2afix + main + lane/memfn-span4k + raise + READ-2/CHECK-1; pcrec abi 109 there).
  Main reserved sabotage S3260-S3275; the kit's forms lane holds S3276-S3299 (next free S3300).
- 03:36 FORMS DELIVERED: lane/memfn-forms @ 7506bca30 (report docs/dev/lanes/forms_report.md; width-32 movers 0; width 4095
  movers 1 [ab]{1000}; main's probe [0-9a-f]{3400}@4095 = 24,024 B, deny refused at 510,538). IN FLIGHT: code round
  crit-memfn-forms (opus coordinator, scratch/crit-memfn-forms/, ~2.5 h) and cloud test+axes on 7506bca30 (monread --wait
  armed). Lane asks to rule after the round: cards' home kit-grid@7 vs kit-synthetic; the force spelling's form-hash instance
  not built; K1/K2 text (report "Cards"); a known tuning.md conflict at landing; R28-2/3 recorded UNREACHED. Then: done line,
  tell main head length (64, UNMEASURED until the cards run) + the probe number.
- (history) LANE forms (opus) RAN from 02:17: worktrees/forms, lane/memfn-forms from lane/memfn-span4k 60c2958ae; R-45 plan A (forms
  I/L/H(h), span-loop PAIR row, test-only span-head=N lever, cards C1-C5 + dry run, interim h=64 labelled UNMEASURED, R28-2/3
  witnesses, K1/K2 text, main's r32 F1 probe number). lanewatch armed. CPU ends 19:30 11-17. NEXT on delivery: code round
  (coordinator), cloud test+axes, then deliver; tell main the head length + the probe number.

## CURRENT STATE (2026-11-16 17:30)
- TIMING TONIGHT: jobs 600-609 QUEUED (box queue, not-before 2026-11-17T01:00, RUN_ID mfcard-zen4-2, FROZEN f6274c11b =
  lane/memfn-scanrow, merged on main as c9ff8b53d; worktrees/mfind fast-forwarded and pinned in .wtprune.keep). Job set
  /var/tmp/pcrec-pcrec/scratch/memfn/mcfixa/jobs/ (JF-1 unset GLIBC_TUNABLES; 609 rc follows d197; a refused NON-DECIDING scan
  row prints "scan unpriced" and never vetoes). Main keeps the box clear from 00:30, load check 00:27; Frank asked to close Steam.
  If the quiet gate refuses on Frank's processes: REPORT, never retry around it. Verdicts via `scripts/monread kit` (one
  --wait armed). Rules: CONFIRM -> set CONFIRM_CELLS, queue 610 only; INCONCLUSIVE -> this was the FIRST run (zen4-1 ruled not
  a run): the ONE re-run with FIRST_RUNDIR(_AVX2)=zen4-2 and a new RUN_ID; a second INCONCLUSIVE = NOT-WIN; LOSS settles
  span_pick row 1 at that level; WIN -> the ruled split shape under its own go. Replay of zen4-1 under the fixed rule:
  slot/replay_zen4-1.txt (generic CONFIRM, x86-64/v3 INCONCLUSIVE only because avx2 JMH never ran).
- DELIVERED + MERGED today: R-44 D3 floor gate (c38f4362b), scanrow harness fix (c9ff8b53d).
- DELIVERED, awaiting main: R-45 PLAN B lane/memfn-span4k @ 60c2958ae (cloud test + axes GREEN; reviews r27, r28) and the
  HELD RAISE lane/memfn-span4k-raise @ 9d4907a16 (= 60c2958ae + 1; lands only on main's combined branch over covs2afix, with
  main's READ-2 asserts + CHECK-1 witness). Witness row (b) follows main's stage-2 B5 text.
- R-45 FORMS (plan A): GO EFFECTIVE (main, after r45chk) on design rev 6 @ 69acf5376 (lane/memfn-r45). NEXT: brief the forms
  build lane cut from lane/memfn-span4k 60c2958ae; its first doc edit folds main's K1 (Q1's answer into the reply + which
  "pcrec's side" items leave the combined branch) and K2 (a bench-run regime's lit-l16 A/A floor cells move to the bench);
  it also owes R28-2/R28-3 witness rows. Owner rulings: forms now (one joint landing), keep-short-spans NO, near-miss later.
  Night order: kit form cards first, h frozen by its rule, identity check, then main's width cells on the REBUILT binary.
  Main asked the bench dev how NOT-WARM/short-subject cells are timed via pcrec-harness --harness=span-head=N.
- OWED after tonight's verdict: r24 SR-1..SR-4 (scan-row harness notes; never on the frozen tree during the window);
  ADQ-3-3 (slot sabotage row m8); the mfind-long-run witness shape; remove worktrees/mfind from .wtprune.keep after the verdict.
- Worktrees to prune when their mtimes age (>120 min): scanrow, tri-span4kax, raisefix (wtprune --apply --force NAME).

## Lessons (today)
- A timing job set's queue-time check must EXECUTE the job's own calls (an arm_check that re-implements them shares a source
  with what it controls; r13 JF-2).
- A refused non-deciding row must never veto a verdict; read "deciding" from one declared source (r13 JF-4).
- A held commit that builds only on a future combined branch gets reviewed on a combined APPROXIMATION tree (r27: all three
  blockers were found there).
- After merging main into a branch that changed a seam signature, grep EVERY caller across the whole tree (lane probes too):
  r33_sim/probe.c broke cloud axes (AX-1).
- A new sizing helper's fallback on allocation failure is an absorbed OOM: test-resource's injector caught it (TRI-1).
- Design replies converge in several short single-critic rounds; drill the rule as WRITTEN each time (r23 dominance, r25 voids).
