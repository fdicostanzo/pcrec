# memfn kit — wake-up brief

Rewritten 2026-11-15 19:20 by the kit session (pcrec-memfn), IN FLIGHT: the mfcard timing is queued for 01:00.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = session `pcrec-main`. Frank rules, mostly via main.
Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Delivered unit: lane/memfn-mfind @ 363fec82e (worktrees/mfind).

## Read in order
1. This file. 2. memfn/docs/journal.md, 2026-11-15 entries. 3. responses.md's last `done:` (the unit, flags, validation).
4. D197 (main decisions.md): the fused mfind row is an UNPICKED measuring instrument; the timing is one-sided.

## CURRENT STATE (2026-11-15 19:20)
- DELIVERED to main: mfind+slotx combined unit, lane/memfn-mfind @ 363fec82e (reviews r5-r9 committed there). All gate
  stages green (the 628 summary red = a superseded slot stage; ruled green, main told).
- TIMING QUEUED: jobs 600-609 in /var/tmp/pcrec-pcrec/scratch/memfn/mcfixa/jobs/ (keys kit-mfcard-*), not-before
  2026-11-16T01:00, window.vars RUN_ID=mfcard-zen4-1 FROZEN=363fec82e, TREE worktrees/mfind (built). ~2h20m.
  609 prints the D197 verdict per ISA level (d197_rule.py, rule pinned in the record at window time).
  - On a CONFIRM verdict at some level: put CONFIRM_CELLS="<609's d197_confirm_cells>" in window.vars, queue 610 only.
  - On INCONCLUSIVE at a level: the ONE allowed re-run: set FIRST_RUNDIR/FIRST_RUNDIR_AVX2 (the first run's rundirs,
    see window.vars.example), a NEW RUN_ID, re-queue 600-609 (second INCONCLUSIVE = NOT-WIN), in a window main clears.
  - LOSS settles span_pick row 1 vs the finder at that level; WIN triggers the 2026-11-07 ruled split shape under its OWN
    go (ask main), then re-measure. Report the verdict to main (responses.md notice + SendMessage), with the scan ratios.
  Verdicts arrive via `scripts/monread kit` (a `--wait` is armed while jobs are queued).
- OWED after the window: ADQ-3-3 (a slot sabotage row m8 for the manifest pin site); rebase onto main's [COVER-CAP]
  stage 1 (abi 108) when main says it is on origin; lane d3wire (R-44: D3 floor script has no caller) after main merges.
- Worktrees to prune via scripts/wtprune once main merged: mfindcloud, mcfixa, mcfixd, mcfixb, slotx (+ mfind after).
- Ideas logged today (memfn/docs/ideas.md): long-span (1)-(4), COVER-CAP stage-2 owner direction (sub-span loops
  default; three cards; all-inline only as a dial option), covs1 EMITTED-2 near-miss x6.65 fact.

## Lessons (today)
- A harness-changing lane runs the FULL slot sabotage table before delivery (mcfixa/mcfixb broke anchors + a J4 crash
  that no review saw).
- Drill the entry point the window runs (the CLI, by subprocess), not only the imported function (r7 RULE-1).
- When a fix tolerates a missing field, plant that field deleted from a new-shape record (r8 ADQ-3).
- A rulings entry written while a lane is finishing is easily missed: check the deliverable applied it.
- Lanes idle on background watchers despite the brief: nudge them to wait in the foreground with a bound.
- The box queue orders ready jobs by row length, not by the name's priority number.
- A job's `expect stages=N` must be counted from the script's echo lines (I miscounted 7 for 6).
