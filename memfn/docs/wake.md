# memfn kit — wake-up brief

Updated 2026-11-21 08:57 by the kit session IN FLIGHT. Main (pcrec-main) is up.

## Who you are
The kit manager (`/pcrec-memfn-manager`). The ledger and journal branch is worktrees/memfn on lane/memfn-k1108.
- Heartbeat cron: 17,47.
- Waiting list: worktrees/.mgr/waiting_on.kit.
- Verdicts come only via `scripts/monread kit --wait` (run_in_background).
- Lanes are watched with `scripts/lanewatch --follow NAME`.

## Read in order
1. This file.
2. memfn/docs/journal.md, the 2026-11-20 evening and 2026-11-21 entries (710 CONFIRMED -> D201 build go -> block_span.md revs 1-4.1 -> r68/r69/r71/r72 -> U1 landed).
3. docs/design/memfn/block_span.md rev 4.1 (§14 units U1..U6).

## CURRENT STATE
- **R-47 / D201 (block span at the SIMD layer):**
  - Owner rulings:
    - block-build: "build with simd layer";
    - add. 1: build regardless of the census;
    - add. 2, scalar-wrap: option A;
    - add. 4, scalar-check-cut: yes. The census replaces the scalar timing; T-keep is dropped; [BSPAN-SCALAR-RISK] is filed.
  - Population: 3 bench sites (hex32, \b hex32 \b, \d{32}; all k31) and 0 in the corpus.
  - U1 LANDED on main c279e7e26 (0 movers).
  - **U2 + U2b in flight:** lane bsu2 (opus, worktrees/bsu2, S3505-S3519).
    - abi 111 (L3 holds 110; re-pin by grep if main says U2 lands first).
    - Its heavy steps wait on main's 300-grow2-lib job (box lock, until about 11:45). No jump granted.
    - Then its make test/mech jobs, a merge into k1108 (merge alone, make strict), a code round (ask main for the number), and delivery.
  - Then U3 (w32 helper), U4 (checks + the rest of C18), U5 (card C6, CANDIDATE), U6 (abi package, G1 dry run; C6 timing in main's window, every bench box incl. Zen 1).
  - Review numbers come from main; main takes the next free number for its own rounds.
- **Done 11-20 night:** 712 (the max ramp is the window rule; the method is OPEN), 711 (FRONT stays), 710 CONFIRMED.
- **Prunable later:** bsu1fix (the <120 min guard), spancensus, spancensus2, rampchunk, rampfix, bcq, cofix, bcfix (unmerged lane branches holding only reports: archive via scripts/branchprune). A /tmp/pcrec-mech-sabotage.* dir was left by bsu1fix; it was told to Frank and left alone.
- **OWED:**
  - the g2 win-family triage lane (shrink it or move it to g2-full; tell main first);
  - re-sync the rampfix branch copy of the 712 harness;
  - the cards.py not-warm chunking defect;
  - gatebudget, mfcal and mfind decisions;
  - r46 PLAN/DOC, r24 SR-1..4, ADQ-3-3, the mfind witness.

## Lessons (2026-11-21)
- **Lane briefs:**
  - TMPDIR=$PCREC_TMPDIR/scratch/LANE/tmp on every run.
  - Re-read the rulings file BY NAME at every checkpoint.
  - Lock-waiting runs never wake a lane: run them in the foreground or poll them.
  - Never pgrep/pkill.
- **Rulings and records:**
  - A reviewer's cut of a condition the owner was told is an owner question, never a manager ruling.
  - A census reads site KIND by the table's own predicate on the trace record, never by a text proxy.
  - Owner words given to the kit are journaled VERBATIM the same day.
  - Journal times come from `date`, never estimated.
- **Review mechanics:**
  - When the kit branch has already merged the subject, a code round's BASE is the parent of the lane's first commit.
  - In a heredoc journal entry, backticks run unless the heredoc is quoted ('EOF').
