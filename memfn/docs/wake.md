# memfn kit — wake-up brief

Rewritten 2026-11-15 13:25 by the kit session (pcrec-memfn), IN FLIGHT (context near compaction).

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = session `pcrec-main`. Frank rules, mostly via main.
Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. The UNIT in flight: lane/memfn-mfind (worktrees/mfind).

## Read in order
1. This file. 2. memfn/docs/journal.md entries 2026-11-15 (10:05 onward). 3. Reviews r5-memfn-mfindcomb (committed on
lane/memfn-mfind) and r6-memfn-mcfix (/var/tmp/pcrec-pcrec/scratch/crit-memfn-mcfix/review.md, RULED section).
4. D197 (main decisions.md): the fused mfind row is an UNPICKED measuring instrument; the timing is one-sided.

## CURRENT STATE (2026-11-15 13:25)
- Frank's 03:05 stop LIFTED for the kit (~11:00): finish mfind/slotx + the timing tonight; d3wire (R-44) after the landing.
- lane/memfn-mfind tip ac097a76e = mfind + mfindfix2 + slotx (+slotxfix/f8/f8b) + main 4ccd97ca7 + mcfixd + mcfixa + S3198 comment fix.
- FINAL GATE (box) on worktrees/mfind: 620 strict, 621 g2-full, 626 mech (+S3198) GREEN; 627 slot RUNNING; 622-624 ident and
  628 gate (7 keys) queued. Scripts: /var/tmp/pcrec-pcrec/scratch/memfn/mfind/gate/ (BASE 04fe41c92). Cloud test
  ac097a76e GREEN; cloud axes fe1b24e2a pending (verdicts via `scripts/monread kit`).
- Lane mcfixb (opus) on lane/memfn-mcfixb (worktrees/mcfixb, from ac097a76e): r6 FIX-NOW (D197 scorer: NOT-WIN order,
  confirm/second guards + code_commit equality, confirm cells only at CONFIRM levels (rulings R1), rule + cells pinned
  in the record, shipped-arm variant guard, TIMED-SHAPE callee allowlist, RULE-7, enum-sentinel asserts in window.c/
  finder.c, --sites<80 refusal, docs). S3206-S3215. Commits the r6 review.
- NEXT after mcfixb: a SIZED code round on its diff (Frank: never skipped) -> merge lane/memfn-mcfixb into
  lane/memfn-mfind (git -C worktrees/mfind merge, ALONE) only after the box gate ends -> re-run strict + slot (627) +
  cloud test (+ ident only if kit C bytes could move; mcfixb must prove 0 movers) -> write
  /var/tmp/pcrec-pcrec/scratch/memfn/mcfixa/jobs/window.vars (RUN_ID, FROZEN = the final tip) -> queue jobs 600-609
  (not-before 2026-11-16T01:00; the jobs check the 20:00-01:00 hold themselves); 610 = the confirming re-run, queue ONLY
  on a CONFIRM verdict. Frank's window: night 11-15 -> 11-16 after 01:00 (~2h20m + 25 min).
- Then deliver to main: done line in responses.md (branch tip, reports, reviews r5/r6, gate + cloud verdicts; the D197
  "what is timed" sentence from r5 Q1; flags: mcfixd edited comments in src/core/internal.h and cli/CLAUDE.md;
  FIDELITY-5's cells pin; SABROWS-2 is main's (fixposts2b)).
- Waiting list: worktrees/.mgr/waiting_on.kit. Heartbeat cron 17,47 (session-only; re-create after a restart).

## Lessons (today)
- Lane briefs must name tests/axes/run_axes.sh as forbidden (mfindfix2 ran it out of queue) and say "never idle on a
  background run; wait in the foreground with a bound".
- Run tests/memfn/run_arch_blind.sh after adding text under tests/ or memfn/ (S3198's comment went red twice).
- A gate job must exit with the OR of its stages (642's selftest failure hid behind the last stage's rc).
- Never merge into a worktree while its box gate runs (the gate builds from the live tree): merge after, or use a
  detached scratch worktree (worktrees/mfindcloud did that for the cloud runs; prune it after landing).
