# memfn kit — wake-up brief

Rewritten 2026-11-16 03:10 by the kit session (pcrec-memfn): the first mfcard window ended WITHOUT a verdict (see TIMING).

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = session `pcrec-main`. Frank rules, mostly via main.
Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Delivered unit: lane/memfn-mfind @ 363fec82e (worktrees/mfind).

## Read in order
1. This file. 2. memfn/docs/journal.md, 2026-11-15 entries. 3. responses.md's last `done:` (the unit, flags, validation).
4. D197 (main decisions.md): the fused mfind row is an UNPICKED measuring instrument; the timing is one-sided.

## CURRENT STATE (2026-11-15 19:20)
- DELIVERED to main: mfind+slotx combined unit, lane/memfn-mfind @ 363fec82e (reviews r5-r9 committed there). All gate
  stages green (the 628 summary red = a superseded slot stage; ruled green, main told).
- TIMING (window 11-15 -> 11-16, RUN_ID mfcard-zen4-1): 600-607 GREEN; 608 JMH-avx2libc RED (quiet-gate wait-timeout:
  load 2.07 vs 2.0, Frank's Steam + claude/code); 609 RED with TWO defects: the avx2libc finalize runs without env $LIBC_ENV
  (record refuses its own avx2 pin; would fail even with 608 green) and the default JMB card's est rows are noise-REFUSED.
  Triage: /var/tmp/pcrec-pcrec/scratch/memfn/mfctri/triage.md. NO VERDICT. NEXT: fix jobs/609 (wrap the avx2libc finalize +
  est calls in env $LIBC_ENV; add a dry-run step that finalizes each arm under its own env) + a one-critic check; then a FRESH
  window (new RUN_ID, all 10 jobs; not D197's one re-run, there was no verdict) on a night main clears with Frank, Steam closed.
  Rules for the window itself unchanged: CONFIRM -> CONFIRM_CELLS + 610 only; INCONCLUSIVE -> the one re-run with FIRST_RUNDIR;
  LOSS settles span_pick row 1 at that level; WIN -> the ruled split shape under its own go.
- D3 (R-44): lane/memfn-d3wire @ 6af642db1 (worktrees/d3wire); r12 FIX-NOW D3G-1/2/3/4/6 owed (one sonnet lane, then one
  critic), then deliver to main. Cloud test 505f4d631 GREEN, axes GREEN.
- R-45 (spans to 4095): READ + acked; reply in responses.md BEFORE any build: one opus design lane + a design critic round.
- OWED after the window: ADQ-3-3 (a slot sabotage row m8 for the manifest pin site); the guarded witness mfind-long-run wants a shape the cover
  route never takes (main re-aimed it to 32 sets, f74793d69; stage 2 moves the edge again).
- worktrees/mfind is pinned in worktrees/.wtprune.keep (timing tree): remove that line after the D197 verdict, then prune.
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
