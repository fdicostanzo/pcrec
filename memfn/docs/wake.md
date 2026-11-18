# memfn kit — wake-up brief

Rewritten 2026-11-16 17:30 by the kit session (pcrec-memfn). Tonight: the mfcard timing window from 01:00.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = session `pcrec-main`. Frank rules, mostly via main.
Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Heartbeat cron `17,47` (OWNER=kit); waiting list
worktrees/.mgr/waiting_on.kit; sabotage ids worktrees/.mgr/sabotage_ids.txt (next free S3260).

## Read in order
1. This file. 2. memfn/docs/journal.md, 2026-11-16 entries. 3. responses.md's last two `done:` lines (R-44, R-45 plan B)
and the R-45 reply block (rev 6). 4. D197 (the mfind instrument; one-sided timing).

## UPDATE 2026-11-17 13:55 (read FIRST; supersedes everything below where they differ)
- TONIGHT (11-18 01:00): SET 1 = mfcard FRESH FIRST RUN QUEUED 600-609 (RUN_ID mfcard-zen4-3, FROZEN f6274c11b, no
  FIRST_RUNDIR; Frank cleared it). Main checks Steam/VS Code (loadshame --present) at 00:30 and 01:00; any quiet-gate refusal
  -> send main the line. Verdict rules: CONFIRM -> CONFIRM_CELLS + queue 610 only; INCONCLUSIVE -> the ONE re-run with
  FIRST_RUNDIR(_AVX2)=mfcard-zen4-3 + new RUN_ID (may share 11-19 night); LOSS settles span_pick row 1 at that level; WIN ->
  the ruled split shape under its own go. Any RED -> triage lane. Then unpin worktrees/mfind; r24 SR-1..4 owed.
- FORMS (R-45 plan A): lane/memfn-forms @ 1aec5d4d3 = frozen-tree candidate. Reviews r35-r38 all ruled + fixed (filed under
  docs/dev/reviews/2026-11-17-r35..r38). Code answer-clean, 0 movers at width 32, h=64 shipped UNMEASURED. Cards rule rev 10:
  per-pattern twin term, interleaved rounds, agreement gate, CONFIRM BY RE-RUN, class drill (84 rows, worst 0.020); fast-split
  limit retired. IN FLIGHT: round 5 crit-memfn-forms5 (scratch/crit-memfn-forms5) + cloud (test GREEN, axes pending).
- CARDS NIGHT 11-19 01:00 CLEARED by Frank (set 2, cap 3 h). The cards MUST time on lane/covs2b WITH the forms merged. MAIN
  TERMS: BY 14:00 11-18 send main the forms tip + responses.md done line + pcrec-side readers that move (abi, stamps, spec,
  pins, test expectations, found by grep) + expected conflicts vs covs2b @ 28af649c9 (known: docs, tests/ci/cloud_axes_shards.tsv,
  tests/ci/cloud_mech_shards.tsv: keep BOTH sides); if round 5 forces fixes that miss 14:00, tell main by 10:00 and the cards
  move a night. Main merges + freezes covs2b by 20:00 and sends the sha. Job set WRITTEN + dry-run: scratch/memfn/fcards/jobs
  700-704 (README has the queue lines; window.vars RUN_ID=fcards-zen4-1, FROZEN=main's sha; worktrees/fcards-night clean at
  FROZEN, pin it in .wtprune.keep). 704 identity runs only at h*=64; h*<64 -> kit commit + abi event after the night. Send main
  the keys when queued, and 'h* frozen' after 702.
- 14:25 ADD: round 5 (r39) on 1aec5d4d3 RULED: K1 LAYOUT TWIN (between-binary noise), K4 reading B, K6 one owed-confirm list,
  + small items. formsfixj DONE @ 2f3c964fc (K7/K10/K11; its mech shard table is REGENERATED wholesale: tell main to
  regenerate after merging, not line-merge). formsfixi (opus) running, due by 19:30. NEXT: landing lane merges formsfixi +
  formsfixj into lane/memfn-forms; round 6 (sized) + cloud on that tip; job-set update (700 runs G2 head passes on FROZEN ->
  G2 file; 701 calls `cards.py rule RUNDIR --g2 FILE` once before its loop; dry checks the file); by 14:00 11-18 deliver to
  main. Main accepted both critic-skill proposals (each pooled level; comparison kinds).
- 19:05 ADD (supersedes the 14:25 NEXT): round 6 (r41) ruled: L9 SETUP RANDOMIZATION replaced the layout twins (pools of 4
  layout variants per text, per-launch draws; R2 per-text layout term + variant-aware bimodal test; power is RECORD: a 5 %
  win is seen 170/300 at tau 1 %, 7 at 2 %; a missed win keeps 64). lane/memfn-forms FAST-FORWARDED to 27b18e75c = the
  frozen candidate (formsfixk report docs/dev/lanes/formsfixk_report.md); cloud test+axes on it in flight. fcards jobs
  UNCHANGED and updated earlier for G2 (700 runs G2 head passes -> g2_heads.txt; 701 one `rule --g2` first; total cap 9,672 s).
  MORNING ORDER: (1) set 1's verdict (rules above); (2) when the box is free of set 1, round 7 (sized, 2 critics, both
  simulate rules + perturbation lens) on 27b18e75c; judge K6's drill win re-centring 0.955->0.953; (3) BY 10:00 tell main
  whether 14:00 holds (else the cards move a night); (4) by 14:00 the delivery package (tip, done line, moving readers by
  grep, conflicts vs covs2b: docs + BOTH cloud shard tables, the mech table REGENERATED wholesale -> main regenerates after
  merging; h=64 UNMEASURED; known limits incl. power RECORD). Main accepted both lens changes (comparison kinds; by
  perturbation) and will check cover_cap §11.4's A/A floor with the kit before its width cells (pool is arm-generic).
- Sabotage ids: next free S3335. Main accepted the critic-skill change (simulate drills each pooled level + order step).
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
